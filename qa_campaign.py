"""Deterministic campaign combat QA without opening an existing save.

Examples:
  python3 -B qa_campaign.py
  python3 -B qa_campaign.py --story --seeds 0,1,2
  python3 -B qa_campaign.py --testing adapted --chapter casino --trace
  python3 -B qa_campaign.py --testing none --story --json

The default informed heuristic can inspect combat data (including affinities);
--knowledge observed scores unlearned affinities as neutral. A policy loss
is a signal for playtesting, not proof of a broken encounter.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from hashlib import sha256
from itertools import combinations
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory

from battle_data import SKILLS
from battle_engine import AFF, STATS, TECH
from campaign_combat import build_stage, stage_grade
from campaign_data import CHAPTERS
from campaign_state import Campaign, TestingCampaign

ROOT = Path(__file__).resolve().parent
SUPPORT = {'heal', 'restore', 'revive', 'cure', 'buff', 'debuff', 'dekaja', 'dekunda', 'ailment'}
GUARD_HINTS = ('guard before', 'incoming. guard', 'incoming / guard', 'stop it or guard',
               'charge; guard', 'brace for', 'guard every standing', 'suppress arms or guard',
               'incoming. heal or guard', 'incoming. guard or heal')
ADAPTIVE_TEAMS = {
    'pyramid': ('Mona','Skull','Queen','Panther','Fox'),
    'spaceport': ('Noir','Queen','Mona','Skull','Panther'),
    'casino': ('Queen','Panther','Skull','Mona'),
    'cruiser': ('Queen','Crow','Panther','Skull'),
    'depths': ('Queen','Skull','Fox','Panther'),
    'laboratory': ('Queen','Crow','Violet','Skull'),
}


def hp(unit):
    return unit.hp / unit.max_hp


def configure_adapted(campaign, chapter, node, *, observed=False):
    """Legal pre-battle loadout selection; no stat/resource injection."""
    data = campaign.data
    available = [n for n in data['teammates'] if n not in node.get('forbidden_team', ())]
    preferred = ADAPTIVE_TEAMS.get(chapter, ('Mona','Skull','Panther','Fox','Queen'))
    ranked = [n for n in preferred if n in available] + [n for n in available if n not in preferred]
    squad = ranked[:data['squad_slots']]
    if squad != data['squad']:
        campaign.equip_squad(squad)

    specs = {name: campaign.persona_spec(name) for name in data['personas']}
    weak = set()
    if not observed:
        from campaign_data import ENEMY_DATA
        weak = {e for wave in node['waves'] for n in wave
                for e, f in ENEMY_DATA[n].get("affinity",{}).items() if f == 'weak'}
    primary = next((n for n in ('Shiki-Ouji', 'Arsène') if n in specs), next(iter(specs)))
    picks = [primary]
    kinds = Counter()
    elems = {}
    def catalogue(name, counts, powers):
        for skill in specs[name]['skills']:
            spec = SKILLS[skill]
            counts[spec['kind']] += 1
            if spec['kind'] == 'damage':
                e = spec.get('element', 'Physical')
                v = spec['power'] + (14 if spec['target'] == 'enemies' else 0)
                powers[e] = max(v, powers.get(e, 0))
    catalogue(primary, kinds, elems)
    while len(picks) < min(len(specs), data['slots']):
        def value(name):
            counts, powers = Counter(), {}
            catalogue(name, counts, powers)
            return (sum(max(0, v-elems.get(e, 0))*(1.85 if e in weak else 1)
                        for e, v in powers.items()) +
                    sum(weight for kind, weight in [('heal', 55), ('debuff', 27), ('revive', 28),
                                                    ('dekaja', 21), ('dekunda', 21), ('cure', 17)]
                        if counts[kind] and not kinds[kind]))
        name = max((n for n in specs if n not in picks), key=value)
        picks.append(name)
        catalogue(name, kinds, elems)
    if picks != data['loadout'] or primary != data['primary']:
        campaign.equip_personas(picks, primary)


def actionable(intent, specials):
    """Use visible text or an available special, not boss HP or internal flags."""
    norm = intent.casefold()
    if specials or any(key in norm for key in GUARD_HINTS):
        return True
    return ('9:' in norm or 'press 9' in norm or '9 take the shot' in norm or
            'topple or sever' in norm or 'hit the core' in norm or 'use skills or gun' in norm or
            'heal before the follow-up' in norm or 'replacements after' in norm or
            'reinforcements after' in norm or 'guard and watch' in norm or
            'protect weaknesses' in norm or 'disable the bodyguard' in norm or
            'keep joker standing' in norm or 'keep joker conscious' in norm)


def charged(intent):
    norm = intent.casefold()
    return (any(key in norm for key in GUARD_HINTS) or norm.startswith('march of the piggy:')
            or ('incoming for ' in norm and 'guard or heal' in norm))


class Tactician:
    def __init__(self, battle, knowledge):
        self.b = battle
        self.knowledge = knowledge

    def affinity(self, t, e):
        if e == 'Almighty':
            return 1
        seen = t.affinity if self.knowledge == 'informed' else self.b.seen.get(t.name, {})
        if t.status == 'freeze' and e in ('Physical','Gun') and seen.get(e) in ('resist','repel','drain','null'):
            return 1
        return -1 if seen.get(e) in ('repel','drain') else AFF.get(seen.get(e, 'normal'), 1)

    def damage(self, a, t, spec, chain, intent):
        e = spec.get('element', 'Physical')
        if (intent.startswith('WAKABA AIRBORNE') or intent.startswith('SPHINX DIVE')) and e == 'Physical':
            return 0, 0, 0
        if t.behavior=='lab-azathoth' and intent.startswith('SHIELD TENDRIL'):
            return 0, 0, 0
        if t.behavior == 'casino-sae' and intent.startswith(f'ROULETTE: {e.upper()}'):
            return 0, 0, 0
        if t.behavior == 'bank-kaneshiro':
            bodyguard = next((u for u in self.b.enemies if u.alive and u.behavior=='bank-bodyguard'
                              and not u.down and u.status not in ('sleep','freeze')),None)
            if bodyguard:
                if spec['target'] == 'enemies':
                    return 0, 0, 0
                t = bodyguard
        aff = self.affinity(t, e)
        if aff < 0:
            return -105, 0, 0
        marked = e in TECH.get(t.status, ())
        crit = spec.get('crit',14)/100 if e in ('Physical','Gun') and aff >= 1 else 0
        chance = max(0, min(1, (spec.get('accuracy',96)+8*a.buffs.get('agility',(0,0))[0]
                               -8*t.buffs.get('agility',(0,0))[0]-18*(a.status=='dizzy'))/100))
        raw = (spec['power'] * aff * (1.42 if marked else 1) * (1+.45*crit) *
               (1+.2*chain) * (1+.25*a.buffs.get('attack',(0,0))[0]) *
               (1-.25*t.buffs.get('defense',(0,0))[0]) * (.48 if t.guard else 1))
        ko = max(0, min(1, (raw*1.10-t.hp)/(raw*.2))) if raw else 0
        extra = (1 if marked or aff == 1.5 else crit) if not t.down and not t.guard else 0
        if t.no_knockdown:
            extra = ko if aff == 1.5 and not t.down else 0
        return (min(t.hp,raw)*.94 + (26 if len(self.foes)>1 else 16)*ko)*chance, extra*chance, ko*chance

    def score(self, a, command, spec, t, chain, intent):
        mode, kind = spec['target'], spec['kind']
        ts = ([t] if t is not None else [a] if mode=='self' else
              self.foes if mode=='enemies' else self.live)
        cost = 0 if chain >= 3 else (spec.get('sp',0)*(.47 if a.sp>20 else .78) +
               a.max_hp*spec.get('hp',0)/100*(.35 + .7*(hp(a)<.70) + 1.3*(hp(a)<.40)))
        if command.startswith('item:'):
            cost += 8
        joker = self.b.allies[0]
        if kind=='damage':
            hits = [self.damage(a,u,spec,chain,intent) for u in ts]
            extra = max(x[1] for x in hits)
            kills = len(ts)==len(self.foes) and min(x[2] for x in hits)
            score = sum(x[0] for x in hits) + (1-kills)*extra*32
            if command == 'gun' and a.ammo<=2:
                cost += 3
            if command == 'showtime':
                cost += 3
            if charged(intent):
                if kills > .75:
                    return score+150
                score *= .66
            return score-cost
        if kind=='heal':
            result = 0
            for u in ts:
                if not u.alive:
                    continue
                missing = u.max_hp-u.hp
                amount = min(missing, spec['power']*(1+.2*chain))
                ratio = hp(u)
                urgency = .28 if ratio>.70 else .64 if ratio>.43 else .96
                result += amount*urgency*(1.32 if u is joker else 1)
                if amount>=12 and ratio<.43:
                    result += (38 if u is joker else 18)*(.43-ratio)/.43
                if u is joker and amount>=14 and u.hp<max(60, u.max_hp*.32):
                    result += (60-u.hp)*.42 + 23
            return result-cost
        if kind=='revive':
            return 62 + spec.get('power',50)*.3 + (10 if len(self.live)<3 else 0) - cost
        if kind=='restore':
            return sum((min(u.max_sp-u.sp,spec['power'])*.98+(24 if u is joker else 16)) if
                       u.sp<=8 and u.max_sp>10 else 0 for u in ts)-cost
        if kind=='cure':
            bad={'sleep':40,'freeze':43,'forget':41,'fear':31,'shock':26,'burn':22}
            return sum(bad.get(u.status, 0)*(1.28 if u is joker else 1) for u in ts)-cost
        if kind=='ailment':
            return sum((21 if spec.get('status') in ('sleep','freeze') else 14) +
                       min(15,u.hp/10) for u in ts
                       if not u.status and not u.no_knockdown and u.hp>40 and not u.guard)-cost
        if kind in ('buff','debuff','dekaja','dekunda'):
            sign = 1 if kind in ('buff','dekaja') else -1
            stat = spec.get('stat','all')
            stats = STATS if stat=='all' else (stat,)
            total = 0
            for u in ts:
                lifespan = min(2.75,u.hp/(28+10*len(self.live))) if u.enemy else 2.5
                for stat in stats:
                    present, left = u.buffs.get(stat,(0,0))
                    if kind in ('dekaja','dekunda'):
                        uptime = min(lifespan,left) if present==sign else 0
                    elif present==sign:
                        uptime = .35 if left==1 else 0
                    else:
                        uptime = lifespan*(.68 if present==-sign else 1)
                    weight = {'attack':8.8,'defense':8.0,'agility':3.1}[stat]
                    if u.enemy and stat=='defense':
                        weight *= len(self.live)*.8
                    if u is joker and stat=='defense':
                        weight *= 1.28
                    total += uptime*weight
            return total-cost
        return -100

    def legal_moves(self, a, *, hypothetic=False):
        """Enumerate UI actions; let engine validate every candidate actually sent."""
        b=self.b
        if not hypothetic:
            for cat in ('attack','gun','showtime','items'):
                for aid, _, _ in b.actions(cat):
                    yield aid, None
            pool = b.personas if a.name=='Joker' and not b.shifted else (None,)
            for p in pool:
                for aid, _, _ in b.actions('skills',p):
                    yield aid, p
        else:  # One-step lookahead for the legal Baton receivers.
            yield 'attack', None
            if a.ammo:
                yield 'gun', None
            for item,count in b.items.items():
                if count:
                    yield 'item:'+item, None
            if a.name=='Joker':
                for p, data in b.personas.items():
                    for skill in data['skills']:
                        yield 'skill:'+skill, p
            else:
                for skill in a.skills:
                    yield 'skill:'+skill, None

    def best(self, a, intent, chain, *, hypothetic=False):
        b = self.b
        desperate = a is b.allies[0] and hp(a)<.32
        best = (56 + (25 if a.hp<61 else 0) if charged(intent) else 5 if desperate else -2,
                'guard', None, None)
        if intent.startswith(('ROULETTE OPENING','RIGGED ROULETTE')):
            best = (35, 'guard', None, None)
        for aid, persona in self.legal_moves(a, hypothetic=hypothetic):
            spec = b._spec(aid)
            if spec is None:
                continue
            if hypothetic:
                costsp = spec.get('sp',0)
                costhp = (a.max_hp*spec.get('hp',0)+99)//100
                if a.status=='forget' and (costsp or costhp):
                    continue
                if chain<3 and (costsp>a.sp or costhp>=a.hp):
                    continue
            for target in b.targets(aid) if spec['target'] in ('enemy','ally') else (None,):
                if not hypothetic and aid!='showtime' and b.action_block(aid,target,persona):
                    continue
                if intent.startswith(('ROULETTE OPENING','RIGGED ROULETTE')) and spec['kind']=='damage':
                    continue
                score = self.score(a,aid,spec,target,chain,intent)
                if persona and persona!=b.persona:
                    affinity=b.personas[persona]['affinity']
                    score += .8*sum(1 for f in affinity.values() if f in ('repel','drain','null'))
                    score -= .7*sum(1 for f in affinity.values() if f=='weak')+.7
                if score>best[0]:
                    best=score,aid,target,persona
        return best

    def choose(self, intent, specials):
        b = self.b
        self.foes = [u for u in b.enemies if u.alive]
        self.live = [u for u in b.allies if u.alive]
        if specials:
            return specials[0][0], None, None
        if intent.startswith(('FULL FORCE /', 'ADAM KADMON / Wait for', 'OPENING / Joker')):
            return 'guard', None, None
        best=self.best(b.actor,intent,b.chain)
        if b.hold_up:
            damage=b.allout_damage
            expected=sum(min(damage,u.hp) for u in self.foes)
            if all(u.hp<=damage for u in self.foes) or expected+14>best[0]:
                return 'allout', None, None
        for aid, _, _ in b.actions('baton'):
            ally=next(u for u in self.live if u.name==aid[5:])
            value, command, _, _=self.best(ally,intent,b.chain+1,hypothetic=True)
            if command!='guard' and value+3>best[0]+8:
                best=value+3,aid,None,None
        return best[1:]


@dataclass
class Result:
    mode: str
    chapter: str
    node: str
    seed: int
    base_seed: int
    attempt: int
    squad: list[str] = field(default_factory=list)
    personas: list[str] = field(default_factory=list)
    outcome: str = 'timeout'
    actions: int = 0
    wave: int = 0
    waves: int = 0
    rounds: int = 0
    medal: str = ''
    joker_hp: int = 0
    joker_min_hp: int = 0
    enemy_hp_remaining: int = 0
    action_types: Counter = field(default_factory=Counter)
    support: Counter = field(default_factory=Counter)
    actionable: Counter = field(default_factory=Counter)
    responses: Counter = field(default_factory=Counter)
    trace: list[str] = field(default_factory=list)
    final_log: list[str] = field(default_factory=list)
    error: str = ''


def fight(campaign, node, chapter, mode, seed, attempt, args):
    row=Result(mode,chapter,node['id'],seed,seed-attempt+1,attempt)
    b=build_stage(campaign,node['id'],seed)
    row.squad = [u.name for u in b.allies]
    row.personas = list(b.personas)
    row.joker_min_hp = b.allies[0].hp
    row.waves = b.wave_count
    bot=Tactician(b,args.knowledge)
    previous=None
    # Observe all log events, including when the engine's 160-line buffer wraps.
    written=list(b.log)
    engine_say=b._say

    def capture(msg):
        written.append(msg)
        engine_say(msg)
    b._say=capture

    for _ in range(args.max_actions):
        if b.phase!='turn':
            break
        intent=b.story_intent
        specials=b.actions('story-special')
        command,target,persona=bot.choose(intent,specials)
        wave,rnd=b.wave,b.round
        hint = re.sub(r' \(\d+/\d+\)\.$', '.', intent)
        episode=(wave,hint)
        act=actionable(intent,specials)
        if act and episode!=previous:
            row.actionable[hint or specials[0][1]]+=1
        previous=episode if act else None
        actor=b.actor
        if args.trace:
            row.trace.append(f'{wave}.{rnd} {actor.name}: {command}'
                             f'{(" -> "+target.name) if target else ""}'
                             f'{(" via "+persona) if persona else ""}'
                             f'{(" | "+intent) if intent else ""}')
        error=b.act(command,target,persona=persona)
        if error:
            row.error=f'{wave}.{rnd} {actor.name} -> {command}: {error}'
            row.outcome='invalid-action'
            break
        row.actions+=1
        spec=b._spec(command)
        kind=(spec['kind'] if spec else 'baton' if command.startswith('pass:') else command)
        row.action_types[kind]+=1
        if kind in SUPPORT:
            row.support[command.split(':',1)[-1]]+=1
        if specials and command==specials[0][0]:
            row.responses[specials[0][1]]+=1
        elif charged(intent) and command=='guard':
            row.responses['Guard on charge']+=1
        if args.trace:
            # Preserve exact event order without keeping a separate unbounded UI buffer.
            row.trace.extend(written)
        for entry in written:
            if entry.startswith(('ORACLE / MORAL SUPPORT:', 'ORACLE / FINAL GUARD:',
                                 'ORACLE / EMERGENCY SHIFT:', 'ORACLE / UFO:')):
                row.support[entry.split(':',1)[0]]+=1
        written.clear()
        if b.wave!=wave:
            row.rounds+=rnd
        row.joker_min_hp=min(row.joker_min_hp,b.allies[0].hp,
                             *(after for u,before,after in b.damage_events if u is b.allies[0]))
    if b.phase!='turn':
        row.outcome=b.phase
    row.wave=b.wave
    row.rounds+=b.round
    row.joker_hp=b.allies[0].hp
    row.enemy_hp_remaining=sum(u.hp for u in b.enemies)
    if row.outcome=='win':
        row.medal=stage_grade(b)
    if row.outcome!='win':
        row.final_log=b.log[-12:]
    return row


def rows_for_campaign(campaign, mode, seed, args):
    """Stop on a blocked Story op; all selected Testing ops run independently."""
    story = mode=='story'
    for chapter in CHAPTERS:
        if args.chapter and chapter['id']!=args.chapter:
            continue
        for node in chapter['nodes']:
            if args.node and node['id']!=args.node:
                continue
            if mode in ('story','adapted'):
                configure_adapted(campaign,chapter['id'],node,observed=args.knowledge=='observed')
            for attempt in range(1,args.retries+2):
                result=fight(campaign,node,chapter['id'],mode,seed+attempt-1,attempt,args)
                yield result
                if result.outcome=='win':
                    campaign.clear(node['id'],result.medal)
                    break
                if result.outcome=='invalid-action':
                    break
            if story and result.outcome!='win':
                return


def summarize(rows):
    buckets={}
    for row in rows:
        key=(row.mode,row.chapter)
        if key not in buckets:
            buckets[key]={'mode':row.mode,'chapter':row.chapter,'starts':0,'wins':0,'losses':0,
                          'timeouts':0,'invalid_actions':0,'retries':0,'actions':0,
                          'actionable_episodes':0,'responses':Counter(),'support':Counter()}
        b=buckets[key]
        b['starts']+=row.attempt==1
        b['wins']+=row.outcome=='win'
        b['losses']+=row.outcome=='loss'
        b['timeouts']+=row.outcome=='timeout'
        b['invalid_actions']+=row.outcome=='invalid-action'
        b['retries']+=row.attempt>1
        b['actions']+=row.actions
        b['actionable_episodes']+=sum(row.actionable.values())
        b['responses'].update(row.responses)
        b['support'].update(row.support)
    return list(buckets.values())


def parse(argv=None):
    p=argparse.ArgumentParser(description=__doc__,
                              formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--testing',choices=('stock','adapted','both','none'),default='both')
    p.add_argument('--story',action='store_true',help='also exercise an ordered, disposable Story save')
    p.add_argument('--chapter',choices=tuple(c['id'] for c in CHAPTERS),help='only run a Testing chapter')
    p.add_argument('--node',choices=tuple(n['id'] for c in CHAPTERS for n in c['nodes']),
                   help='only run one Testing operation')
    p.add_argument('--seeds',default='0,1,2',help='comma-separated distinct base seeds (1–32 seeds)')
    p.add_argument('--knowledge',choices=('informed','observed'),default='informed')
    p.add_argument('--max-actions',type=int,default=320)
    p.add_argument('--retries',type=int,default=0,help='extra attempts after a loss or timeout at seed+attempt-1')
    p.add_argument('--trace',action='store_true',help='emit all actions and combat lines')
    p.add_argument('--json',action='store_true',help='write summary and attempt details to stdout')
    p.add_argument('--strict',action='store_true',help='exit 1 if any start lacks a win after its allotted retries')
    args=p.parse_args(argv)
    try:
        args.seeds=[int(s) for s in args.seeds.split(',')]
    except ValueError:
        p.error('--seeds needs comma-separated integers')
    if not 1<=len(args.seeds)<=32 or len(set(args.seeds))!=len(args.seeds):
        p.error('--seeds needs 1–32 distinct integers')
    if not 1<=args.max_actions<=2000 or not 0<=args.retries<=9:
        p.error('--max-actions must be 1–2000 and --retries must be 0–9')
    if args.testing=='none' and not args.story:
        p.error('enable at least one of Testing or Story')
    if args.story and (args.chapter or args.node):
        p.error('Story must begin from the first operation; omit --chapter and --node')
    if args.chapter and args.node and not any(c['id']==args.chapter and
            any(n['id']==args.node for n in c['nodes']) for c in CHAPTERS):
        p.error('--node is not in the selected --chapter')
    return args


def main(argv=None):
    args=parse(argv)
    # Print versions to make results useful even for evolving chapter modules.
    files=('qa_campaign.py','campaign_combat.py','campaign_data.py','campaign_state.py','battle_data.py',
           'battle_engine.py','weekend_bosses.py','early_data.py','pyramid_data.py','spaceport_data.py','late_data.py',
           'shido_boss.py','depths_boss.py','lab_boss.py')
    fingerprints={f:sha256((ROOT/f).read_bytes()).hexdigest() for f in files if (ROOT/f).is_file()}
    rows=[]
    modes=('stock','adapted') if args.testing=='both' else () if args.testing=='none' else (args.testing,)
    for mode in modes:
        for seed in args.seeds:
            rows.extend(rows_for_campaign(TestingCampaign(),mode,seed,args))
    if args.story:
        with TemporaryDirectory(prefix='phantom-qa-campaign-') as temp:
            for i,seed in enumerate(args.seeds):
                save=Path(temp)/f'qa-{i}.json'
                campaign=Campaign(save)
                campaign.new_game()
                rows.extend(rows_for_campaign(campaign,'story',seed,args))
                if Campaign(save).data['cleared']!=campaign.data['cleared']:
                    raise RuntimeError('Disposable Story load did not reproduce cleared operations.')
    summary=summarize(rows)
    if args.json:
        # Counter fields serialize as normal JSON objects.
        def result_dict(row):
            return {k:dict(v) if isinstance(v,Counter) else v for k,v in vars(row).items()}
        print(json.dumps({'settings':vars(args),'sha256':fingerprints,'summary':summary,
                          'attempts':[result_dict(row) for row in rows]},indent=2,ensure_ascii=False))
    else:
        print(f"Seeds {args.seeds} | {args.knowledge} affinity knowledge | "
              f"{args.max_actions} actions/attempt | {args.retries} retry limit")
        print("mode     chapter        won/started retries actions hints   replies  support")
        for b in summary:
            print(f"{b['mode']:8} {b['chapter']:14} {b['wins']:2}/{b['starts']:<9} {b['retries']:>2} "
                  f"{b['actions']:>8} {b['actionable_episodes']:>5} "
                  f"{sum(b['responses'].values()):>9} {sum(b['support'].values()):>8}")
        for row in rows:
            if row.outcome!='win':
                print(f'{row.mode}/{row.node} seed={row.seed} attempt={row.attempt}: '
                      f'{row.outcome} in {row.actions} actions at wave {row.wave}/{row.waves}; '
                      f'{row.enemy_hp_remaining} enemy HP left. {row.error}')
            if args.trace:
                print(f"== {row.mode}/{row.node} seed {row.seed} attempt {row.attempt} ==")
                print('\n'.join(row.trace))
        print(f"Snapshots: {', '.join(k + '=' + v[:10] for k,v in fingerprints.items())}")
    if any(row.outcome=='invalid-action' for row in rows):
        return 2
    return int(args.strict and sum(b['wins'] for b in summary)<sum(b['starts'] for b in summary))


if __name__=='__main__':
    raise SystemExit(main())
