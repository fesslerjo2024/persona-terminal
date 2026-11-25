"""Measure player-response gaps in seeded campaign battles, without reading any save.

python3 -B qa_pacing.py
python3 -B qa_pacing.py --node bank-vault --seeds 0,1,2 --json

Stock and expanded Testing loadouts each run against the same seeds
and both qa_campaign tactical policies. Adapted loadouts are selected without
consulting unrevealed affinities and held identical across policies; the
informed policy sees affinity tables only when making combat choices.

Large burst: Joker loses at least 45% of max HP between two player inputs.
Before first Joker action is not necessarily before any teammate input.
Direct defense is a legal Guard (Joker), or a useful heal/cure/defense buff
at that prompt; offense and indirect protection can still be viable.
This measures policy outcomes, not a proof that a prior action could
never avoid a lethal position. No rules are altered unless --party-first
is explicitly selected as an in-memory counterfactual.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from pathlib import Path
import re

from qa_campaign import Tactician, configure_adapted
from campaign_combat import build_stage
from campaign_data import CHAPTERS, ENEMY_DATA
from campaign_state import TestingCampaign

ROOT = Path(__file__).resolve().parent
EARLY = {'castle', 'museum', 'bank'}
LATE = {'casino', 'cruiser', 'depths', 'laboratory'}
# Include every early operation. In late chapters keep regular-shadow waves
# only, even when they're followed by a named fight in the same operation.
REGULAR_FOE = {'', 'normal', 'support', 'ailment', 'aggressive', 'brute', 'caster'}
SKIP = re.compile(r'^(?P<actor>.+) loses the turn to (?P<ailment>.+)\.$')
DEFENSIVE = {'heal', 'cure', 'buff', 'dekunda'}
PRESSURE_RATIO = .45


@dataclass
class Hit:
    enemy: str
    element: str
    hp_lost: int
    damage: int
    weak: bool
    technical: bool


@dataclass
class Wave:
    wave: int
    formation: list[str]
    behaviors: list[str]
    joker_entry_hp: int
    joker_max_hp: int
    joker_entry_mask: str
    joker_entry_status: str
    inputs: int = 0
    usable: int = 0
    joker_usable: int = 0
    defense_options: int = 0
    joker_skips: list[str] = field(default_factory=list)
    enemies_before_first: int = 0
    first_actor: str = ''
    entry_damage: int = 0
    max_enemy_chain: int = 0
    max_chain_damage: int = 0
    joker_outgoing: list[str] = field(default_factory=list)
    incoming: list[Hit] = field(default_factory=list)
    pressure: list[dict] = field(default_factory=list)
    death: dict | None = None


class Probe:
    """Attach pass-through observers to one Battle, without draws or rule edits."""

    def __init__(self, b, party_first=False):
        self.b = b
        self.party_first = party_first
        self.waves = []
        self.wave = None
        self.joker = b.allies[0]
        self.gap = None
        self.after_spawn()
        if b.phase != 'turn' or b.actor is None or b.actor.enemy or b.damage_events:
            raise RuntimeError('Initial Story player-first invariant changed; capture battle construction too.')
        self.attach()

    def after_spawn(self):
        b = self.b
        self.wave = Wave(b.wave, list(b.waves[b.wave-1]), [u.behavior for u in b.enemies],
                         self.joker.hp, self.joker.max_hp, b.persona, self.joker.status)
        self.waves.append(self.wave)
        self.reset_gap('wave spawned')

    def reset_gap(self, before):
        self.gap = {'after': before, 'hp_at_input': self.joker.hp, 'damage': 0, 'enemies': [],
                    'enemy_one_mores': [], 'hits': [], 'mask': self.b.persona, 'status': self.joker.status,
                    'round': self.b.round, 'input_budget': self.wave.inputs,
                    'usable_budget': self.wave.usable, 'joker_budget': self.wave.joker_usable,
                    'defense_budget': self.wave.defense_options}

    def on_prompt(self, command, target, persona):
        b, w = self.b, self.wave
        # Baton passes are real inputs but not damage/recovery/Guard decisions.
        if not w.first_actor:
            w.first_actor=b.actor.name
        w.inputs += 1
        if not command.startswith(('pass:', 'persona:')) and command!='analyze':
            w.usable += 1
            w.joker_usable += b.actor is self.joker
            w.defense_options += self.defense_available()
        s=b._spec(command)
        if s and b.actor is self.joker and s['kind']=='damage':
            w.joker_outgoing.append(s.get('element','Physical'))
        self.reset_gap(f'{b.actor.name}: {command}'+(f' -> {target.name}' if target else '')+
                       (f' via {persona}' if persona and persona!=b.persona else ''))

    def defense_available(self):
        b, a, j = self.b, self.b.actor, self.joker
        if a is j:
            return True  # Guard is always a legal choice at Joker's own prompt.
        for category in ('skills','items'):
            for aid, _, _ in b.actions(category):
                s=b._spec(aid)
                mode=s['target']
                if mode not in ('ally','allies') or s['kind'] not in DEFENSIVE:
                    continue
                if s['kind']=='heal' and j.hp>=j.max_hp:
                    continue
                if s['kind']=='cure' and not j.status:
                    continue
                if s['kind']=='buff' and s.get('stat','attack') not in ('defense','all'):
                    continue
                if s['kind']=='dekunda' and j.buffs.get('defense',(0,0))[0]>=0:
                    continue
                if not b.action_block(aid,j if mode=='ally' else None):
                    return True
        return False

    def attach(self):
        b=self.b
        spawn, step, strike, say, hurt=b._spawn,b._enemy_step,b._strike,b._say,b._hurt
        hit_ctx=[]

        def observed_spawn():
            self.finish_gap()
            spawn()
            if self.party_first and b.wave>1:
                opener=next(u for u in b.order if not u.enemy and u.alive)
                b.order.remove(opener)
                b.order.insert(0,opener)
                b.next_order=b.order[:]
            self.after_spawn()

        def observed_step(actor):
            gap,w=self.gap,self.wave
            enemy=actor.name
            gap['enemies'].append(enemy)
            w.enemies_before_first += not bool(w.first_actor)
            w.max_enemy_chain=max(w.max_enemy_chain,len(gap['enemies']))
            return step(actor)

        def observed_strike(a,t,s):
            element=s.get('element','Physical')
            ctx=(a.name,element,a.enemy and t.affinity.get(element)=='weak' and element!='Almighty',
                 a.enemy and element in self.technical.get(t.status, ()))
            hit_ctx.append(ctx)
            try:
                return strike(a,t,s)
            finally:
                hit_ctx.pop()

        def observed_hurt(u, amount):
            before=u.hp
            value=hurt(u,amount)
            if u is not self.joker or u.hp>=before:
                return value
            w,g=self.wave,self.gap
            loss=before-u.hp
            source,element,weak,tech=hit_ctx[-1] if hit_ctx else (
                g['enemies'][-1] if g['enemies'] else (b.actor.name if b.actor else 'unknown'),
                'Status/script',False,False)
            if not g['hits']:
                g.update(hp_before_first_hit=before,mask=b.persona,status=u.status)
            hit=Hit(source,element,loss,amount,weak,tech)
            w.incoming.append(hit)
            g['hits'].append(hit)
            g['damage']+=loss
            if not w.first_actor:
                w.entry_damage+=loss
            w.max_chain_damage=max(w.max_chain_damage,g['damage'])
            if not u.alive and w.death is None:
                w.death=self.gap_record(g)
            return value

        def observed_say(msg):
            if msg.endswith(' gets One More!') and b.actor and b.actor.enemy:
                self.gap['enemy_one_mores'].append(b.actor.name)
            if msg.startswith('Joker loses the turn to '):
                match=SKIP.match(msg)
                if match:
                    self.wave.joker_skips.append(match['ailment'])
            say(msg)

        from battle_engine import TECH
        self.technical=TECH
        b._spawn,b._enemy_step,b._strike,b._say,b._hurt=(
            observed_spawn,observed_step,observed_strike,observed_say,observed_hurt)

    def gap_record(self,gap):
        return {**gap,'enemies':list(gap['enemies']),'enemy_one_mores':list(gap['enemy_one_mores']),
                'hits':[asdict(h) for h in gap['hits']]}

    def finish_gap(self):
        if self.gap['damage'] >= self.joker.max_hp*PRESSURE_RATIO:
            self.wave.pressure.append(self.gap_record(self.gap))


def selection(args):
    for chapter in CHAPTERS:
        for node in chapter['nodes']:
            if args.node:
                if node['id']==args.node:
                    yield chapter['id'],node
            elif chapter['id'] in EARLY or chapter['id'] in LATE and any(
                standard_wave(ENEMY_DATA[n].get('behavior','') for n in wave) for wave in node['waves']
            ):
                yield chapter['id'],node


def fight(chapter,n,seed,mode,policy,args):
    c=TestingCampaign()
    if mode=='adapted':
        configure_adapted(c,chapter,n,observed=True)
    b=build_stage(c,n['id'],seed)
    p=Probe(b,party_first=args.party_first)
    t=Tactician(b,policy)
    actions=0
    while b.phase=='turn' and actions<args.max_actions:
        aid,target,persona=t.choose(b.story_intent,b.actions('story-special'))
        p.finish_gap()
        p.on_prompt(aid,target,persona)
        error=b.act(aid,target,persona=persona)
        if error:
            raise RuntimeError((n['id'],seed,mode,policy,aid,error))
        actions+=1
    p.finish_gap()
    return {
        'chapter':chapter,'node':n['id'],'seed':seed,'loadout':mode,'policy':policy,
        'squad':[u.name for u in b.allies],'personas':list(b.personas),
        'outcome':b.phase if b.phase!='turn' else 'timeout','actions':actions,
        'waves':[asdict(w) for w in p.waves],
        'last_log':b.log[-20:] if b.phase!='win' else [],
    }


def standard_wave(behaviors):
    return all(behavior in REGULAR_FOE for behavior in behaviors)


def include_wave(r,w,opts):
    # Single-node drilldowns deliberately include scripted waves.
    return bool(opts.node or r['chapter'] in EARLY or
                standard_wave(w['behaviors']))


def ranked_counts(counter):
    return dict(sorted(counter.items(), key=lambda p:(-p[1],p[0])))


def summarize(rows,args):
    table=defaultdict(list)
    for r in rows:
        for w in r['waves']:
            if include_wave(r,w,args):
                table[(r['node'],w['wave'])].append((r,w))
    clustered=[]
    for (node,wave), cases in table.items():
        fatal=[(r,w) for r,w in cases if w['death']]
        critical=[(r,w) for r,w in cases if w['pressure']]
        groups={}
        for mode in ('stock','adapted'):
            for policy in ('observed','informed'):
                own=[w for r,w in cases if r['loadout']==mode and r['policy']==policy]
                groups[mode+'/'+policy]={
                    'arrivals':len(own),'losses':sum(bool(w['death']) for w in own),
                    'large_bursts':sum(bool(w['pressure']) for w in own),
                    'pre_joker_deaths':sum(bool(w['death']) and not w['joker_usable'] for w in own),
                    'entry_damage':sum(bool(w['entry_damage']) for w in own),
                }
        losses_by_seed=Counter(r['seed'] for r,w in fatal)
        clustered.append({
            'node':node,'wave':wave,'formation':cases[0][1]['formation'],'arrivals':len(cases),
            'losses':len(fatal),'distinct_loss_seeds':len(losses_by_seed),
            'confirmed_policy_overlap_seeds':sorted({r['seed'] for r,w in fatal if
                any(r2['seed']==r['seed'] and r2['loadout']==r['loadout'] and r2['policy']!=r['policy']
                    for r2,w2 in fatal)}),
            'before_first_team_action':sum(w['usable']==0 for r,w in fatal),
            'before_first_joker_action':sum(w['joker_usable']==0 for r,w in fatal),
            'before_direct_defensive_prompt':sum(w['defense_options']==0 for r,w in fatal),
            'entry_pressure_cases':sum(w['entry_damage']>=w['joker_max_hp']*PRESSURE_RATIO for r,w in cases),
            'large_burst_cases':len(critical),'entry_damage_cases':sum(bool(w['entry_damage']) for r,w in cases),
            'max_gap_damage':max(w['max_chain_damage'] for r,w in cases),
            'loss_enemy_elements':ranked_counts(Counter(h['element'] for r,w in fatal for h in w['death']['hits'])),
            'loss_masks':ranked_counts(Counter(w['death']['mask'] for r,w in fatal)),
            'outgoing_elements':{policy:ranked_counts(Counter(e for r,w in cases
                if r['policy']==policy for e in w['joker_outgoing'])) for policy in ('observed','informed')},
            'groups':groups,
        })
    clustered.sort(key=lambda s:(-s['before_first_team_action'],-s['before_first_joker_action'],
                                 -s['distinct_loss_seeds'],-s['losses'],-s['entry_pressure_cases'],
                                 -s['large_burst_cases'],s['node'],s['wave']))
    return clustered


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--seeds',default=','.join(map(str,range(10))),help='comma-separated seeds')
    p.add_argument('--node',choices=tuple(n['id'] for c in CHAPTERS for n in c['nodes']))
    p.add_argument('--max-actions',type=int,default=320)
    p.add_argument('--top',type=int,default=12)
    p.add_argument('--party-first',action='store_true',
                   help='counterfactual only: move a living ally to first initiative in later waves')
    p.add_argument('--json',action='store_true',help='emit details to stdout')
    args=p.parse_args(argv)
    try:
        seeds=[int(x) for x in args.seeds.split(',')]
    except ValueError:
        p.error('provide comma-separated integer seeds')
    if not 1<=len(seeds)<=32 or len(set(seeds))!=len(seeds):
        p.error('provide 1–32 distinct seeds')
    if not 1<=args.max_actions<=1500 or not 1<=args.top<=100:
        p.error('--max-actions must be 1–1500 and --top 1–100')
    stages=list(selection(args))
    rows=[fight(chapter,n,seed,mode,policy,args) for chapter,n in stages
          for seed in seeds for mode in ('stock','adapted') for policy in ('observed','informed')]
    groups={f'{mode}/{policy}':Counter(r['outcome'] for r in rows
             if r['loadout']==mode and r['policy']==policy)
             for mode in ('stock','adapted') for policy in ('observed','informed')}
    summaries=summarize(rows,args)
    hashes={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.glob('*.py'))
            if not p.name.startswith('test_') and (p.name.endswith(('_boss.py','_data.py')) or
            p.name in ('battle_engine.py','weekend_bosses.py','campaign_combat.py',
                       'campaign_state.py','qa_campaign.py','qa_pacing.py'))}
    if args.json:
        print(json.dumps({'seeds':seeds,'party_first_counterfactual':args.party_first,
                          'outcomes':groups,'sha256':hashes,
                          'wave_summary':summaries,'attempts':rows},ensure_ascii=False,indent=2))
    else:
        print(f'Seeds {seeds}; {len(stages)} operations; {len(rows)} battles; {len(summaries)} wave buckets.')
        if args.party_first:
            print('Counterfactual: living ally first after every wave transition.')
        for key,results in groups.items():
            print(key,dict(results))
        print('Wave                      death/arrive  preTeam/preJoker/noDefense  large gaps (entry)')
        for s in summaries[:args.top]:
            print(f"{s['node']+':'+str(s['wave']):26} {s['losses']:2}/{s['arrivals']:<5} "
                  f"         {s['before_first_team_action']}/{s['before_first_joker_action']}/"
                  f"{s['before_direct_defensive_prompt']}              "
                  f"{s['large_burst_cases']:2} ({s['entry_pressure_cases']})")
        if args.node:
            for r in rows:
                for w in r['waves']:
                    d=w['death']
                    if d:
                        hits=', '.join(f"{h['enemy']} {h['element']} {h['damage']}" for h in d['hits'])
                        print(f"{r['loadout']}/{r['policy']} seed={r['seed']} wave={w['wave']} "
                              f"actions={d['usable_budget']} Joker={d['joker_budget']} "
                              f"mask={d['mask']} hp={d['hp_before_first_hit']} → {hits}")
        print('Core snapshots:', ', '.join(n+'='+hashes[n][:10] for n in
              ('battle_engine.py','qa_campaign.py','qa_pacing.py')))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
