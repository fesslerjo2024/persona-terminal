"""Early standalone Persona 3 terminal combat, with no Persona 5 dependencies."""
from dataclasses import dataclass, field
import curses as C
import random
from time import monotonic
from persona3_battle_cues import BattleCue, BattleCues
from persona3_meters import MeterTrails, meter_cells
from reel_palette import IDS as SCENE_INKS
from combat_palette import P3_MARKS as ELEMENT_MARKS
import persona3_arqa_combat as arqa
import persona3_late_registry as late
import persona3_sees as sees
import persona3_upper_combat as upper
import persona3_yabbashah_combat as yabba
import persona3_august_combat as august
import persona3_hermit_combat as hermit
import persona3_yabbashah_upper_combat as high

RED,GOLD,CYAN,WHITE,DIM,GREEN=range(1,7)
ENTER=(C.KEY_ENTER,'\n','\r')
ESC='\x1b'
LEAD_ID='Protagonist'  # Stable roster/resource key.
LEAD_NAME='Makoto'
STAT_TURNS=3
STAT_NAMES=(('attack','ATK'),('defense','DEF'),('agility','AGI'),('crit_boost','CRIT'))


def display_name(unit_id):
    return LEAD_NAME if unit_id==LEAD_ID else unit_id


def stat_text(unit):
    return ' '.join(f'{label}{"↑" if getattr(unit,stat)>0 else "↓"}{unit.stat_turns[stat][0]}'
                    for stat,label in STAT_NAMES if stat in unit.stat_turns)


ELEMENTS=('Slash','Strike','Pierce','Fire','Ice','Electric','Wind','Light','Dark')
# Compact symbol, expanded HUD mark, target badge, and ink. "Vuln" never
# implies a weakness knockdown: Priestess merely takes extra Fire damage.
AFFINITY_MARKS={
    'unknown':('?', '?', '', DIM),
    'normal':('·','NORM','NORMAL',WHITE),
    'weak':('W','WEAK','WEAK',GOLD),
    'resist':('R','RES','RESIST',CYAN),
    'null':('N','NULL','NULL',SCENE_INKS['navy']),
    'repel':('P','RPL','REPEL',RED),
    'drain':('D','DRN','DRAIN',GREEN),
    'vulnerable':('V','VULN','VULN',SCENE_INKS['rose']),
}
SKILL_AFFINITY_ORDER=('weak','vulnerable','drain','repel','null','resist')

PARTY={
    LEAD_ID:(130,54,'Slash',('Agi','Bash','Tarunda'),{'Electric':'weak','Dark':'weak'}),
    'Yukari':(116,54,'Pierce',('Garu','Dia','Patra'),{'Electric':'weak','Wind':'resist'}),
    'Junpei':(148,44,'Slash',('Agi','Cleave','Rakukaja'),{'Wind':'weak','Fire':'resist'}),
    'Akihiko':(151,51,'Strike',('Zio','Sonic Punch','Tarukaja','Rakukaja'),{'Ice':'weak','Electric':'resist'}),
    'Mitsuru':(140,58,'Slash',('Bufu','Mabufu','Rakunda','Marin Karin'),{'Fire':'weak','Ice':'resist'}),
}
PARTY['Aigis']=august.AIGIS
PARTY['Koromaru']=high.KOROMARU
PARTY.update(sees.KITS)
DEFAULT_PARTY=(LEAD_ID,'Yukari','Junpei')
RESCUE_PARTY=(LEAD_ID,'Junpei','Akihiko')
START_RESOURCES={name:PARTY[name][:2] for name in DEFAULT_PARTY}
PERSONAS={
    'Orpheus':(('Agi','Bash','Tarunda'),{'Electric':'weak','Dark':'weak'}),
    'Pixie':(('Zio','Dia','Rakunda'),{'Ice':'weak','Electric':'resist'}),
    'Angel':(('Garu','Dia','Sukukaja'),{'Dark':'weak','Wind':'resist','Light':'resist'}),
    'Nekomata':(('Agi','Cleave','Tarunda'),{'Ice':'weak','Fire':'resist'}),
    "Jack O'Lantern":(('Agi','Maragi','Rakunda'),{'Ice':'weak','Fire':'drain'}),
    'Apsaras':(('Bufu','Dia','Sukukaja'),{'Fire':'weak','Ice':'resist'}),
}
PERSONAS={k:{'skills':spec[0],'affinity':spec[1]} for k,spec in {**PERSONAS,**arqa.PERSONAS,**upper.PERSONAS,**late.PERSONAS,**yabba.PERSONAS}.items()}
PERSONA_ALIASES={"Jack-o'-Lantern":"Jack O'Lantern","Jack-o’-Lantern":"Jack O'Lantern",
                  'Jack-o-Lantern':"Jack O'Lantern"}
BAG={'Medicine':3,'Soul Drop':1,'Revival Bead':1}
ITEMS={'Medicine':('heal',50),'Soul Drop':('sp',12),'Revival Bead':('revive',40),**upper.ITEMS}
# kind, element/stat, base power, SP, target, percent max HP
SKILLS={
    'Agi':('hit','Fire',33,4,'one',0),
    'Bufu':('hit','Ice',32,4,'one',0),
    'Zio':('hit','Electric',32,4,'one',0),
    'Garu':('hit','Wind',32,4,'one',0),
    'Maragi':('hit','Fire',25,8,'foes',0),
    'Bash':('hit','Strike',33,0,'one',8),
    'Cleave':('hit','Slash',36,0,'one',8),
    'Skewer':('hit','Pierce',34,0,'one',8),
    'Dia':('heal','',54,4,'ally',0),
    'Patra':('cure','',0,3,'ally',0),
    'Tarunda':('debuff','attack',0,4,'one',0),
    'Rakunda':('debuff','defense',0,4,'one',0),
    'Rakukaja':('buff','defense',0,4,'ally',0),
    'Sukukaja':('buff','agility',0,4,'ally',0),
}
SKILLS.update(arqa.SKILLS)
SKILLS.update(upper.SKILLS)
SKILLS.update(yabba.SKILLS)
SKILLS.update(august.SKILLS)
SKILLS.update(high.SKILLS)
SKILLS.update(sees.SKILLS)
SKILLS.update(late.combined(late.TACTICS_MODULES,'SKILLS'))
THEURGIES={**arqa.THEURGIES,**sees.THEURGIES,'orgia':august.THEURGY,'hound':high.THEURGY}
PARTY_THEURGY={**arqa.PARTY_THEURGY,**sees.THEURGY_BY_ALLY,'Aigis':'orgia','Koromaru':'hound'}

# The compressed early progression uses party level as a single shared
# milestone, rather than simulating a separate experience curve per mask.
PERSONA_LEARNS={
    'Pixie': ((3,'Sukukaja'),),
    'Angel': ((4,'Patra'),),
    'Nekomata': ((4,'Maragi'),),
    "Jack O'Lantern": ((5,'Tarunda'),),
    'Apsaras': ((5,'Patra'),),
}


PERSONA_LEARNS.update(arqa.PERSONA_LEARNS)
PERSONA_LEARNS.update(upper.PERSONA_LEARNS)
PERSONA_LEARNS.update(late.combined(late.TACTICS_MODULES,'PERSONA_LEARNS'))


def party_caps(level=1,party=None):
    extra=max(0,int(level)-1)
    return {name:(PARTY[name][0]+extra*4,PARTY[name][1]+extra*2)
            for name in (DEFAULT_PARTY if party is None else party)}


def persona_skills(name,level=1,extra=()):
    name=PERSONA_ALIASES.get(name,name)
    base=PERSONAS[name]['skills']
    learned=tuple(move for at,move in PERSONA_LEARNS.get(name,()) if level>=at)
    extras=(extra,) if isinstance(extra,str) else tuple(extra)
    return tuple(dict.fromkeys(k for k in (*base,*learned,*extras) if k in SKILLS))


def party_skills(name,day):
    """One dated learned-skill list for combat and recovery."""
    return tuple(dict.fromkeys((*PARTY[name][3],*sees.evolved(name,day)[1])))


# Name, max HP, attack type, power, weaknesses/resists, role.
FOES={
    'maya':('Cowardly Maya',28,'Strike',13,{'Slash':'weak','Fire':'weak'},''),
    'tiara':('Muttering Tiara',43,'Fire',15,{'Wind':'weak'},''),
    'hand':('Magic Hand',49,'Strike',18,{'Fire':'weak','Electric':'resist'},''),
    'ruthless':('Ruthless Ice Raven',102,'Ice',24,{'Fire':'weak','Ice':'resist','Wind':'resist'},''),
    'beast':('Barbaric Beast Wheel',141,'Strike',29,{'Wind':'weak','Fire':'resist'},'wheel'),
    'axle':('Swift Axle',158,'Wind',31,{'Electric':'weak','Slash':'resist','Strike':'resist','Wind':'resist'},'axle'),
    'cupid':('Obsessed Cupid',54,'Wind',18,{'Ice':'weak','Electric':'resist'},''),
    'priestess':('Priestess',382,'Ice',28,{'Ice':'null','Fire':'vulnerable'},'priestess'),
    'despairing':('Despairing Tiara',55,'Ice',17,{'Slash':'weak','Fire':'weak'},'tiara-healer'),
    'loathsome':('Loathsome Tiara',58,'Wind',20,{'Pierce':'weak','Wind':'weak'},'loathsome'),
}
ENCOUNTERS={
    'awakening':('Dorm Rooftop',('maya','maya')),
    'thebel-patrol':('Thebel Patrol',('maya','tiara')),
    'venus-eagles':('Ruthless Ice Raven • 5F',('ruthless','ruthless')),
    'dancing-hand':('Barbaric Beast Wheel • 11F',('beast','hand','hand')),
    'rampage-drive':('Swift Axle • 17F',('axle',)),
    'thebel-ascent':('Thebel Upper Patrol',('cupid','hand')),
    'priestess':('Monorail • Priestess',('priestess',)),
}
FOES.update(arqa.FOES)
ENCOUNTERS.update(arqa.ENCOUNTERS)
FOES.update(upper.FOES)
ENCOUNTERS.update(upper.ENCOUNTERS)
FOES.update(yabba.FOES)
ENCOUNTERS.update(yabba.ENCOUNTERS)
FOES.update(august.FOES)
ENCOUNTERS.update(august.ENCOUNTERS)
FOES.update(hermit.FOES)
ENCOUNTERS.update(hermit.ENCOUNTERS)
FOES.update(high.FOES)
FOES.update(late.combined((*late.TACTICS_MODULES,*late.CYCLE_MODULES),'FOES'))
ENCOUNTERS.update(high.ENCOUNTERS)
ENCOUNTERS.update(late.combined((*late.TACTICS_MODULES,*late.CYCLE_MODULES),'ENCOUNTERS'))
ALIASES={'ruthless-ice-raven':'venus-eagles','barbaric-beast-wheel':'dancing-hand',
         'swift-axle':'rampage-drive','first-moon':'priestess'}

@dataclass(eq=False)
class Unit:
    name:str
    max_hp:int
    max_sp:int
    hp:int
    sp:int
    element:str
    power:int
    skills:tuple
    affinity:dict
    enemy:bool=False
    role:str=''
    down:bool=False
    guard:bool=False
    status:str=''
    attack:int=0
    defense:int=0
    agility:int=0
    status_until:int=0
    crit_boost:int=0
    stat_turns:dict=field(default_factory=dict)

    @property
    def label(self):
        return display_name(self.name)

    @property
    def alive(self):
        return self.hp>0


def hp_meter(hp,max_hp,width):
    """Remaining HP in terminal cells, preserving a full/zero distinction."""
    cells=meter_cells(hp,max_hp,width)
    return '█'*cells,'░'*(max(0,width)-cells)


class P3Battle:
    """Action-based battle. Only committed attacks, skills, items or Guard tick the clock."""
    COMMANDS=('Skills','Attack','Guard','Items','Shift','All-Out','Analyze')

    def __init__(self,encounter,*,resources=None,persona='Orpheus',seed=None,inventory=None,
                 stock=None,level=1,party=None,fuuka=False,theurgy=False,charge=None,registered=None,
                 low_motion=False,day=None,affinity_memory=None):
        encounter=ALIASES.get(encounter,encounter)
        if encounter not in ENCOUNTERS:raise ValueError(f'Unknown encounter: {encounter}')
        persona=PERSONA_ALIASES.get(persona,persona.strip() if isinstance(persona,str) else persona)
        if persona not in PERSONAS:raise ValueError(f'Unknown Persona: {persona}')
        self.encounter=encounter;self.title,foes=ENCOUNTERS[encounter]
        self.rng=random.Random(seed)
        self.level=max(1,int(level))
        self.day=day
        default_roster=hermit.DEFAULT_ROSTER if encounter==hermit.ENCOUNTER else DEFAULT_PARTY
        roster=RESCUE_PARTY if encounter=='emperor-empress' else tuple(party) if party is not None else default_roster
        if not roster or len(roster)>4 or roster[0]!=LEAD_ID or len(set(roster))!=len(roster):
            raise ValueError('Makoto must lead a squad of distinct teammates.')
        if encounter in upper.HOTEL and 'Yukari' not in roster:
            raise ValueError('Yukari must join the hotel operation.')
        if encounter==hermit.ENCOUNTER and 'Junpei' in roster:
            raise ValueError('Junpei is unavailable for the Club Escapade operation.')
        self.caps=party_caps(self.level,roster)
        self._carry=dict(self.caps)
        self._carry.update(resources or {})
        masks={PERSONA_ALIASES.get(n,n):extra for n,extra in (stock or {}).items()}
        masks.setdefault(persona,())
        self.stock={n:persona_skills(n,self.level,extra or ()) for n,extra in masks.items() if n in PERSONAS}
        self.registered=frozenset(PERSONA_ALIASES.get(n,n) for n in (registered if registered is not None else self.stock))
        self.allies=[];self.enemies=[];self.persona=persona
        for i,name in enumerate(roster):
            _,_,element,skills,affinity=PARTY[name]
            hp,sp=self.caps[name]
            if i and encounter=='awakening':break
            current=self._carry[name]
            if isinstance(current,dict):current=(current.get('hp',hp),current.get('sp',sp))
            if i==0:skills,affinity=self.stock[persona],PERSONAS[persona]['affinity']
            else:skills=party_skills(name,day)
            self.allies.append(Unit(name,hp,sp,max(0,min(hp,int(current[0]))),
                max(0,min(sp,int(current[1]))),element,(23 if i==0 else 20+i)+(self.level-1)//2,skills,dict(affinity)))
        supplies=dict(BAG if inventory is None else inventory)
        if inventory is None and encounter=='hotel-hierophant':supplies['Dis-Charm']=2
        self.inventory={name:max(0,int(supplies.get(name,0))) for name in ITEMS if name in BAG or name in supplies}
        self.log=[];self.seen={};self.outcome=None;self.one_more=False;self.shifted=False
        self._affinity_memory=affinity_memory or {};self.affinity_updates={};self._affinity_species={}
        self.defeat_cause="";self.adjust_lead=False;self._enemy_bonus=False
        self.round=1;self.clock=30 if encounter=='priestess' else None
        self._rail_stage=0;self._slot=0;self._shadow_turns=0;self._charge=False
        self.screen='command';self.pick=0;self.back=[];self.overlay=None;self.action=None
        self.notice='';self.log_scroll=0;self.inspected=None
        self.persona_used=False;self.mask_preview=None
        self.meters=MeterTrails()
        self.cues=BattleCues()
        self._action_cues={};self._reel_cues={}
        self.fuuka=bool(fuuka or encounter in ('emperor-empress','theurgy-drill'))
        self.scan_left=(3 if encounter=='emperor-empress' else 2) if self.fuuka else 0
        self.scan_pending=False;self._scan_signature=None
        self.theurgy=bool(theurgy or encounter=='theurgy-drill') and encounter!='emperor-empress'
        self.charge={u.name:max(0,min(100,int((charge or {}).get(u.name,0)))) for u in self.allies} if self.theurgy else {}
        if self.fuuka and self.theurgy:
            self.charge['Fuuka']=max(0,min(100,int((charge or {}).get('Fuuka',0))))
        self.reel=None;self._reel_change=[];self.low_motion=low_motion
        self._all_out_reel=None
        self._charge_hits={};self._arcana_dirty=set();self._arcana_beat={};self._arcana_phase={}
        self._relic_pos=0;self._upper_beat={}
        for name in foes:self._spawn(name,foes.count(name)>1)
        self.tank_cycle=august.TankCycle(self) if encounter==august.ENCOUNTER else None
        self.hermit_cycle=hermit.HermitCycle(self) if encounter==hermit.ENCOUNTER else None
        self.orgia=0;self.orgia_cooldown=False
        if self.encounter=='venus-eagles':
            self.enemies[-1].guard=True
            self._say(f'{self.enemies[-1].label} braces as its partner attacks.')
        elif self.encounter=='rampage-drive':
            self._charge=True;self._shadow_turns=1
            self._say('Swift Axle is lining up a collision.')
        if self.encounter=='emperor-empress':
            for foe in self.enemies:
                self._arcana_beat[foe.name]=0;self._arcana_phase[foe.name]=0
                self._arcana_pattern(foe)
            self._say('Fuuka has stepped in. Queue Full Analysis to find the openings.')
        self.order=[*self.allies,*self.enemies]
        self.actor=self.allies[0]
        self.late_cycle=late.cycle(self)
        if encounter=='theurgy-drill':
            self.actor=next((u for u in self.allies if u.name=='Yukari'),None)
            if self.actor is None:raise ValueError('Yukari must deploy for the field test.')
            self._slot=self.order.index(self.actor)
            self.charge['Yukari']=100
            self._say('Fuuka: Your new gear is ready.')
        if self.clock is not None:self._say('Mitsuru: Reach Priestess before the train hits the station.')
        self._stat_slot=self.actor
        self._stat_start=dict(self.actor.stat_turns)
        if not self.actor.alive:
            self.defeat_cause=f'{LEAD_NAME} entered battle at 0 HP.'
            self._finish('loss')

    def modify_stat(self,u,stat,amount):
        """Apply or refresh a temporary stat for the recipient's next turns."""
        current=u.stat_turns.get(stat)
        baseline=current[1] if current else getattr(u,stat)
        setattr(u,stat,amount)
        u.stat_turns[stat]=(STAT_TURNS,baseline)

    def clear_stats(self,u,*,sign=0,stat=None):
        """Clear modifiers on a transformation, or remove one direction only."""
        for key,_ in STAT_NAMES:
            if stat is not None and stat!=key:continue
            amount=getattr(u,key)
            if sign and amount*sign<=0:continue
            prior=u.stat_turns.pop(key,None)
            setattr(u,key,prior[1] if sign and prior is not None else 0)

    def _close_stat_slot(self):
        u=self._stat_slot
        if u is None:return
        for stat,label in STAT_NAMES:
            original=self._stat_start.get(stat)
            if original is None or u.stat_turns.get(stat) is not original:continue
            remaining,baseline=original
            if remaining>1:u.stat_turns[stat]=(remaining-1,baseline)
            else:
                del u.stat_turns[stat]
                setattr(u,stat,baseline)
                self._say(f'{u.label}: {label} modifier expires.')
        self._stat_slot=None

    @property
    def resources(self):
        return dict(self._carry,**{u.name:(u.hp,u.sp) for u in self.allies})

    @property
    def remaining(self):
        return self.clock

    @property
    def all_out(self):
        living=self.targetable_enemies
        if len(living)!=sum(u.alive for u in self.enemies) and not getattr(self.late_cycle,'all_out_against_exposed',False):return False
        return (self.one_more and self.allies[0].alive and not self.allies[0].down
                and sum(u.alive and not u.down for u in self.allies)>=2
                and bool(living) and all(e.down for e in living))

    @property
    def targetable_enemies(self):
        can_hit=getattr(self.late_cycle,'targetable',None)
        return [e for e in self.enemies if e.alive and (can_hit is None or can_hit(e))]

    @property
    def next_actor(self):
        """The next scheduled slot, not a prediction of new knockdowns or summons."""
        if self.outcome:return None
        can_act=getattr(self.late_cycle,'can_act',lambda _:True)
        next_slot=self._slot+1
        return next((u for u in (*self.order[next_slot:],*self.order[:next_slot])
                     if u.alive and can_act(u)),None)

    def is_exposed(self,u):
        exposed=getattr(self.late_cycle,'exposed',None)
        return bool(exposed is not None and exposed(u))

    @property
    def shift_targets(self):
        if not self.one_more or self.shifted:return []
        return [u for u in self.allies if u is not self.actor and u.alive and not u.down and not u.status
                and not (u.name=='Aigis' and (self.orgia or self.orgia_cooldown))]

    @property
    def threat(self):
        if self.clock is not None:
            if self.clock<=6:return 'Last stretch. Defeat Priestess before impact.'
            if self._rail_stage>=1:return 'Invitation to Chaos shortened the countdown.'
            return 'Each committed action advances the train.'
        if self._charge:return 'Swift Axle is charging. Guard or knock it down.'
        if self.scan_pending:return 'Fuuka is analyzing. Act once to receive the scan.'
        if self.tank_cycle:return self.tank_cycle.threat()
        if self.hermit_cycle:return self.hermit_cycle.threat()
        if self.late_cycle:
            intent=self.late_cycle.threat()
            if intent:return intent
        for module in late.TACTICS_MODULES:
            intent=module.threat(self)
            if intent:return intent
        high_intent=high.threat(self)
        if high_intent:return high_intent
        upper_intent=upper.threat(self)
        if upper_intent:return upper_intent
        if self.encounter=='emperor-empress':
            if self._arcana_dirty:return 'PARADIGM SHIFT / Affinities changed. Scan again.'
            if not self._scan_signature:return 'Fuuka can expose both Shadows with Full Analysis.'
        if self.encounter=='theurgy-drill' and self.actor.name=='Yukari' and self.charge['Yukari']==100:
            return 'Yukari’s gauge is full. Cyclone Arrow bypasses resistance.'
        if self.encounter=='arqa-relic':
            return f'CLAIRVOYANT RELIC / {arqa.RELIC_SEQUENCE[self._relic_pos]} incoming.'
        if self.encounter=='venus-eagles' and any(u.alive and u.guard for u in self.enemies):
            return 'A Raven is guarding. The other can be knocked down.'
        if self._wheel_braced():return 'Magic Hands brace the Wheel. Eliminate both first.'
        return ''

    def _arcana_pattern(self,foe):
        options=arqa.ARCANA[foe.role]
        weakness=options[self._arcana_phase.get(foe.name,0)%len(options)]
        foe.affinity={element:'null' for element in ELEMENTS}
        foe.affinity[weakness]='weak'
        if foe.role=='emperor':foe.affinity['Slash']='repel'

    def _scan_key(self):
        return tuple((u.name,self._arcana_phase.get(u.name,0)) for u in self.targetable_enemies)

    def _scan_block(self):
        if not self.fuuka:return 'Fuuka is not on navigation.'
        if self.scan_pending:return 'Full Analysis is already in progress.'
        if not self.scan_left:return 'Fuuka has no scans remaining this fight.'
        if self._scan_signature==self._scan_key():return 'Fuuka already scanned the current formation.'
        return ''

    def _resolve_scan(self):
        self.scan_pending=False
        self._scan_signature=self._scan_key()
        for u in self.targetable_enemies:
            self.seen[u.name]={e:u.affinity.get(e,'normal') for e in ELEMENTS}
        self._arcana_dirty.clear()
        self._nav_charge(42)
        self._say('Fuuka completes Full Analysis. Current affinities are on the board.')

    def _nav_charge(self,n):
        if 'Fuuka' in self.charge:self.charge['Fuuka']=min(100,self.charge['Fuuka']+n)

    def _oracle_block(self):
        if 'Fuuka' not in self.charge:return 'Fuuka’s Theurgy equipment is not unlocked.'
        n=self.charge['Fuuka']
        return '' if n==100 else f'Oracle requires full charge ({n}%).'

    def _oracle(self):
        reason=self._oracle_block()
        if reason:return reason
        self.charge['Fuuka']=0
        live=[u for u in self.allies if u.alive]
        if any(2*u.hp<u.max_hp for u in live):
            for u in live:self._recover(u,'heal',(u.max_hp+2)//3)
            event='restores squad HP'
        elif any(3*u.sp<u.max_sp for u in live):
            for u in live:self._recover(u,'sp',14)
            event='restores squad SP'
        else:
            for u in live:self.modify_stat(u,'defense',max(1,u.defense))
            event='raises squad defense'
        self._say(f'Fuuka’s Oracle {event}.')
        return None

    def _theurgy_ids(self):
        name=self.actor.name
        if name==LEAD_ID:
            return [k for k,v in arqa.FUSION_SPELLS.items() if v<=self.registered]
        return [PARTY_THEURGY[name]] if name in PARTY_THEURGY else []

    def _theurgy_block(self,ident=None):
        if not self.theurgy:return 'Theurgy equipment is not unlocked.'
        if self.actor.status:return 'An ailment prevents Theurgy. Clear it first.'
        acts=self._theurgy_ids()
        if not acts:return 'Register Orpheus and Apsaras for Cadenza.'
        if ident and ident not in acts:return 'This Theurgy is not available.'
        n=self.charge[self.actor.name]
        if n<100:return f'Theurgy requires full charge ({n}%).'
        return ''

    def _gain_charge(self,u,n):
        if self.theurgy and u.name in self.charge:self.charge[u.name]=min(100,self.charge[u.name]+n)

    def _charge_for(self,actor,action,target):
        if not self.theurgy:return
        hit=self._charge_hits.get(actor,set())
        moves=SKILLS.get(action[6:]) if action.startswith('skill:') else None
        damaged=action=='attack' or moves and moves[0]=='hit'
        bonus=10 if damaged else 5
        if 'down' in hit:bonus+=12
        if actor.name==LEAD_ID and moves:bonus+=18
        if actor.name=='Yukari' and ((moves and moves[0]=='heal') or action=='item:Medicine'):bonus+=30
        if actor.name=='Junpei' and 'crit' in hit:bonus+=32
        if actor.name=='Aigis' and moves and moves[0]=='hit' and moves[-1]:bonus+=28
        if actor.name=='Ken' and actor.sp*2<actor.max_sp:bonus+=28
        if actor.name=='Shinjiro' and actor.hp*2<actor.max_hp:bonus+=28
        if actor.name=='Koromaru' and moves and moves[1]=='Dark':bonus+=25
        self._gain_charge(actor,bonus)

    def _use_theurgy(self,ident,target):
        reason=self._theurgy_block(ident)
        if reason:return reason
        name,kind,element,power,mode,_=THEURGIES[ident]
        area=self.targetable_enemies
        if mode=='single' and target not in area:return 'Choose a living enemy.'
        actor=self.actor
        self.charge[actor.name]=0
        self._say(f'{actor.label} uses {name}.')
        extra=False
        if kind=='orgia':
            self.orgia=3
            august.orgia_burst(self,actor)
        elif kind=='heal':
            for u in self.allies:
                if u.alive:
                    self._recover(u,'heal',(u.max_hp+1)//2)
                    self.modify_stat(u,'agility',1)
        else:
            for u in (area if mode=='group' else [target]):
                self._hit(actor,u,element,power,False,ignore_affinity=True)
                if ident=='jacks' and u.alive and self._can_down(u) and not u.down and not u.guard and self.rng.random()<.60:
                    u.down=True;extra=True
                    self._cue(u,'hp',0,'DOWN')
        if self.tank_cycle and element=='Almighty':self.tank_cycle.settle(self,force=True)
        self._committed(extra)
        self._start_reel(name)
        return None

    def _start_reel(self,name):
        try:
            from persona3_cinematics import THEURGY_SECONDS
        except ImportError:return
        now=monotonic()
        self._all_out_reel=None
        self.reel=(name,now,now+THEURGY_SECONDS)

    def _start_all_out(self,actor,finishing,cast,targets):
        from persona3_allout import FINISH_SECONDS, IMPACT_SECONDS
        now=monotonic()
        duration=FINISH_SECONDS if finishing else IMPACT_SECONDS
        self._all_out_reel=finishing
        self._all_out_cast=cast;self._all_out_targets=targets
        self.reel=(actor.label,now,now+(min(.55,duration) if self.low_motion else duration))

    def _finish_reel(self,now=None):
        now=monotonic() if now is None else now
        for key,before,after in self._reel_change:self.meters.record(key,before,after,now)
        if self._reel_cues:self.cues.publish(self._reel_cues,now)
        self._reel_cues={}
        self.reel=None;self._reel_change=[];self._all_out_reel=None

    def _wheel_braced(self):
        return self.encounter=='dancing-hand' and self.enemies[0].alive and any(u.alive for u in self.enemies[1:])

    def _persona_block(self,name):
        if name not in self.stock:return 'That Persona is not in your active stock.'
        if self.actor is not self.allies[0]:return 'Only Makoto can change Personas.'
        if self.persona_used:return 'Can switch again on Makoto’s next normal turn.'
        if name==self.persona:return 'That Persona is already equipped.'
        return ''

    def _equip(self,name):
        self.persona=name;self.persona_used=True
        self.allies[0].skills=self.stock[name]
        self.allies[0].affinity=dict(PERSONAS[name]['affinity'])
        self._say(f'{LEAD_NAME} equips {name}.')

    @property
    def persona_preview(self):
        return self.screen=='skills' and self.actor is self.allies[0] and not self.persona_used and len(self.stock)>1

    def _spawn(self,key,tagged=False):
        name,hp,element,power,affinity,role=FOES[key]
        if tagged:name+=' '+chr(65+sum(u.name.startswith(name+' ') for u in self.enemies))
        unit=Unit(name,hp,0,hp,0,element,power,(),dict(affinity),True,role)
        self.enemies.append(unit)
        if not role:
            self._affinity_species[unit]=key
            known={**self._affinity_memory.get(key,{}),**self.affinity_updates.get(key,{})}
            known={element:effect for element,effect in known.items() if unit.affinity.get(element,'normal')==effect}
            if known:self.seen[unit.name]=known
        if hasattr(self,'order'):self.order.append(unit)
        return unit

    def _say(self,msg):
        self.log.append(msg)
        if len(self.log)>80:del self.log[0]

    def _cue(self,u,resource,delta,*tags):
        if delta or tags:
            key=(u,resource)
            self._action_cues[key]=self._action_cues.get(key,BattleCue(0)).combine(delta,tags)

    def _finish(self,result):
        self.outcome=result
        self.one_more=False;self.shifted=False
        self._say({'win':'Shadows defeated.','loss':f'{LEAD_NAME} falls.','timeout':'The train reaches the station before you can stop it.'}[result])

    def _ended(self):
        if self.outcome is not None:return True
        settle=getattr(self.late_cycle,'settle',None)
        if settle is not None:settle(self)
        if self.outcome is not None:return True
        if not self.allies[0].alive:self._finish('loss')
        elif self.clock is not None and not self.enemies[0].alive:self._finish('win')
        elif all(not u.alive for u in self.enemies):self._finish('win')
        return self.outcome is not None

    def _can_down(self,u):
        check=getattr(self.late_cycle,'can_down',None)
        return check is None or check(u)

    def _hit(self,a,t,element,power,can_crit=True,*,ignore_affinity=False):
        if not a.enemy and t.enemy:
            if t not in self.targetable_enemies:
                self._say(f'{t.label} is protected.')
                return False
            block=getattr(self.late_cycle,'block_hit',None)
            if block is not None and block(self,a,t,element,ignore_affinity=ignore_affinity):return False
        effect='normal' if ignore_affinity else t.affinity.get(element,'normal')
        accuracy=100+14*(a.agility-t.agility)
        if accuracy<100 and self.rng.randrange(100)>=accuracy:
            self._cue(t,'hp',0,'MISS')
            self._say(f'{t.label} dodges.')
            return False
        if not ignore_affinity and not a.enemy and t.enemy:
            self.seen.setdefault(t.name,{})[element]=effect
            if (species:=self._affinity_species.get(t)) is not None and t.affinity==FOES[species][4]:
                self.affinity_updates.setdefault(species,{})[element]=effect
        varied=round(power*self.rng.uniform(.93,1.07))
        attack=a.attack+(a.name=='Aigis' and self.orgia>0)
        defense=t.defense+(t.name=='Aigis' and self.orgia>0)
        damage=max(1,round(varied*(1+.20*attack)*(1-.23*defense)))
        if effect in ('null','repel','drain'):
            old_hp=t.hp
            if effect=='drain':t.hp=min(t.max_hp,t.hp+damage)
            if effect=='repel':
                old_actor_hp=a.hp
                a.hp=max(0,a.hp-damage)
                self._cue(a,'hp',a.hp-old_actor_hp,'REPEL')
                if a is self.allies[0] and not a.alive:
                    self.defeat_cause=f'{t.label} reflected {element} for {damage} damage.'
            self._cue(t,'hp',t.hp-old_hp,effect.upper())
            self._say(f'{t.label}: {effect.upper()} {element}.')
            return False
        crit=can_crit and not t.guard and effect!='resist' and element in ELEMENTS[:3] and self.rng.random()<(.12+.10*(t.status=='distress')+.21*a.crit_boost)
        if effect=='weak':damage=round(damage*1.55)
        if effect=='vulnerable':damage=round(damage*1.25)
        if effect=='resist':damage=round(damage*.52)
        if crit:damage=round(damage*1.4)
        if t.guard:damage=max(1,round(damage*.45))
        fresh=(effect=='weak' or crit) and self._can_down(t) and not t.down and not t.guard
        if fresh and t.role=='wheel' and self._wheel_braced() and damage<t.hp:
            fresh=False
            self._say('The Magic Hands keep the Wheel upright.')

        old_hp=t.hp
        t.hp=max(0,t.hp-damage)
        if t is self.allies[0] and not t.alive:
            strike=f'{a.label} • {element} • {damage} damage'
            cue=f'{element} hit a weakness.' if effect=='weak' else 'Critical hit.' if crit else ''
            follow='One More follow-up.' if self._enemy_bonus else ''
            self.defeat_cause='\n'.join(part for part in (strike,cue,follow) if part)
        if fresh and t.alive:
            t.down=True
            if t.role=='axle' and self._charge:
                self._charge=False;self._say('The knockdown interrupts Swift Axle’s charge.')
        if not t.alive:t.down=False
        if self.theurgy and not a.enemy:
            cues=self._charge_hits.setdefault(a,set())
            if fresh:cues.add('down')
            if crit:cues.add('crit')
        flags=[flag for yes,flag in ((effect=='weak','WEAK'),(effect=='resist','RESIST'),(crit,'CRIT'),(t.guard,'GUARD')) if yes]
        self._cue(t,'hp',t.hp-old_hp,*flags,*(['DOWN'] if fresh and t.down else ()))
        self._say(f'{t.label} takes {damage}'+(' ['+' '.join(flags)+']' if flags else '')+'.')
        if self.hermit_cycle:self.hermit_cycle.on_damage(self,a,t,damage)
        on_damage=getattr(self.late_cycle,'on_damage',None)
        if on_damage is not None:on_damage(self,a,t,damage)
        return fresh

    def _rail_events(self):
        if self.clock is None or self.outcome:return
        boss=self.enemies[0]
        stage=int(boss.hp*10<=boss.max_hp*7)+int(boss.hp*10<=boss.max_hp*3)
        while self._rail_stage<stage:
            self._rail_stage+=1
            penalty=3 if self._rail_stage==1 else 4
            self.clock=max(0,self.clock-penalty)
            summon=self._spawn('despairing' if self._rail_stage==1 else 'loathsome')
            self._say(f'Invitation to Chaos: −{penalty} actions. {summon.label} joins.')
        if self.clock<=0:self._finish('timeout')

    def _enemy_turn(self,u,bonus_action=False):
        live=[x for x in self.allies if x.alive]
        if not live:return False
        if self.tank_cycle:return self.tank_cycle.turn(self,u,bonus_action)
        if self.hermit_cycle:return self.hermit_cycle.turn(self,bonus_action)
        if self.late_cycle:
            directive=self.late_cycle.turn(self,u,bonus_action)
            if directive is not None:return directive
        for module in late.TACTICS_MODULES:
            directive=module.enemy_turn(self,u,bonus_action)
            if directive is not None:return directive
        scripted=high.enemy_turn(self,u,bonus_action)
        if scripted is not None:return scripted
        scripted=upper.enemy_turn(self,u,bonus_action)
        if scripted is not None:return scripted
        if u.role in arqa.ARCANA and not bonus_action:
            beat=self._arcana_beat[u.name]=self._arcana_beat[u.name]+1
            phase=self._arcana_phase[u.name]
            if not phase and (beat>=2 or u.hp*3<=u.max_hp*2):
                self._arcana_phase[u.name]+=1
                self._arcana_pattern(u)
                self.seen.pop(u.name,None);self._arcana_dirty.add(u.name)
                self._say(f'{u.label} uses Paradigm Shift. Fuuka’s old reading is invalid.')
                return False
        if u.role=='relic':
            index=self._relic_pos if not bonus_action else (self._relic_pos-1)%len(arqa.RELIC_SEQUENCE)
            element=arqa.RELIC_SEQUENCE[index]
            target=max(live,key=lambda t:(t.affinity.get(element)=='weak',not t.guard,self.rng.random()))
            if not bonus_action:self._relic_pos=(self._relic_pos+1)%len(arqa.RELIC_SEQUENCE)
            self._say(f'Clairvoyant Relic casts {element}.')
            return self._hit(u,target,element,u.power,False)
        if u.role=='magus' and not bonus_action and len(live)>1 and self.round%2==0:
            extra=False;self._say('Heretic Magus sweeps the party with Wind.')
            for target in live:
                extra=self._hit(u,target,'Wind',18,False) or extra
                if not self.allies[0].alive:break
            return extra
        if u.role=='priestess':
            self._shadow_turns+=1
            if self._shadow_turns%3==0:
                self._say('Priestess sweeps the car with Ice.')
                bonus=False
                for t in live:
                    bonus=self._hit(u,t,'Ice',22,False) or bonus
                    if not self.allies[0].alive:break
                return bonus
        if u.role=='tiara-healer' and self.enemies[0].alive and self.enemies[0].hp<self.enemies[0].max_hp-26 and self.rng.random()<.55:
            boss=self.enemies[0];boss.hp=min(boss.max_hp,boss.hp+25)
            self._say(f'{u.label} restores 25 HP to Priestess.')
            return False
        target=max(live,key=lambda t:self.rng.random()+(.53 if t.affinity.get(u.element)=='weak' else 0)-.28*t.guard-.25*t.down+(1-t.hp/t.max_hp)*.22)
        if u.role=='axle':
            self._shadow_turns+=1
            if self._charge:
                self._charge=False
                bonus=False;self._say('Swift Axle unleashes a heavy collision.')
                for t in live:
                    bonus=self._hit(u,t,'Strike',39,False) or bonus
                    if not self.allies[0].alive:break
                return bonus
            if self._shadow_turns%3==1:
                self._charge=True;self._say('Swift Axle leans into a charge.')
                return False
        self._say(f'{u.label} attacks.')
        bonus=self._hit(u,target,u.element,u.power)
        if u.role=='loathsome' and target.alive and not target.guard and not target.status and self.rng.random()<.24:
            target.status='distress';self._say(f'{target.label} is distressed.')
        return bonus

    def _advance(self):
        self.one_more=False;self.shifted=False
        while not self.outcome:
            self._close_stat_slot()
            self._slot=(self._slot+1)%len(self.order)
            if self._slot==0:self.round+=1
            u=self.order[self._slot]
            if not u.alive:continue
            self._stat_slot=u
            self._stat_start=dict(u.stat_turns)
            self.actor=u;u.guard=False
            if u.status=='poison' and (not u.status_until or self.round<=u.status_until):
                poison=max(1,u.max_hp//20)
                u.hp=max(0,u.hp-poison)
                self._say(f'{u.label} takes {poison} poison damage.')
                if u is self.allies[0] and not u.alive:self.defeat_cause=f'Poison dealt {poison} damage.'
                if self._ended():return
                if not u.alive:continue
            if u.down:
                u.down=False
                if u.role=='axle' and self._charge:
                    self._charge=False;self._say('The knockdown interrupts Swift Axle’s charge.')
            if upper.step_afflicted(self,u):
                if self._ended():return
                continue
            if not u.enemy:
                if u.name=='Aigis' and (self.orgia or self.orgia_cooldown):
                    if self.orgia:august.orgia_burst(self,u)
                    else:
                        self.orgia_cooldown=False
                        self._say('Aigis cools down.')
                    if self.tank_cycle:self.tank_cycle.settle(self)
                    if self._ended():return
                    continue
                if u is self.allies[0]:self.persona_used=False
                if u.name=='Akihiko' and max(u.attack,u.defense,u.agility)>0:self._gain_charge(u,16)
                if u.name=='Mitsuru' and any(e.alive and (e.status or min(e.attack,e.defense,e.agility)<0) for e in self.enemies):
                    self._gain_charge(u,16)
                return
            more=self._enemy_turn(u)
            if self._ended():return
            if more:
                self._say(f'{u.label} earns One More!')
                # Cap enemy follow-up at one; the opening slice remains recoverable.
                self._enemy_bonus=True
                try:self._enemy_turn(u,True)
                finally:self._enemy_bonus=False
                if self._ended():return

    def _committed(self,extra=False):
        if self.clock is not None:self.clock=max(0,self.clock-1)
        if self.tank_cycle:self.tank_cycle.settle(self)
        if self._ended():return
        self._rail_events()
        if self.outcome:return
        if extra:
            self.one_more=True;self.shifted=False
            self._say('All Shadows down.' if self.all_out else f'{self.actor.label} earns One More!')
        else:self._advance()

    def _targets(self,action):
        if action=='shift':return self.shift_targets
        if action.startswith('theurgy:'):
            mode=THEURGIES[action[8:]][4]
            return self.targetable_enemies if mode=='single' else []
        if action=='analyze' or action=='attack':return self.targetable_enemies
        if action.startswith('item:'):
            kind,_=ITEMS[action[5:]]
            return [u for u in self.allies if u.alive!=(kind=='revive')]
        if action.startswith('skill:'):
            spec=SKILLS[action[6:]]
            if spec[4]=='ally':return [u for u in self.allies if u.alive]
            if spec[4]=='one':return self.targetable_enemies
        return []

    def _block(self,action,target=None,*,persona=None):
        a=self.actor
        if a.status in upper.CONTROLLED:
            damaging=(action.startswith('skill:') and SKILLS.get(action[6:],(None,))[0]=='hit')
            if action in ('attack','allout','shift') or damaging:
                return f'{a.label} has {a.status.title()}. Guard or clear the ailment.'
        if action=='allout' and not self.all_out:
            if any(self.is_exposed(u) and not u.down for u in self.targetable_enemies):
                return 'Exposed is not Down. Knock the boss down to use All-Out.'
            return f'Down every Shadow. Keep {LEAD_NAME} and one ally standing.'
        if action=='shift':
            if not self.one_more:return 'Earn a One More before shifting.'
            if self.shifted:return 'Already shifted this One More.'
            if not self.shift_targets:return 'No teammate can receive this Shift.'
        if action.startswith('item:'):
            name=action[5:]
            if name not in ITEMS or not self.inventory.get(name):return 'Out of '+name+'.'
            if not self._targets(action):return 'No knocked-out ally to revive.'
            kind,_=ITEMS[name]
            if kind=='clear-charm' and not any(u.alive and u.status=='charm' for u in self.allies):
                return 'No ally is charmed.'
        elif action.startswith('skill:'):
            name=action[6:]
            if persona and persona!=self.persona:
                reason=self._persona_block(persona)
                if reason:return reason
                moves=self.stock[persona]
            else:moves=a.skills
            if name not in moves:return 'That Persona does not know this skill.'
            kind,_,_,sp,mode,hp=SKILLS[name]
            if kind=='heal' and mode=='team' and all(not u.alive or u.hp==u.max_hp for u in self.allies):
                return 'All living allies already have full HP.'
            need=(a.max_hp*hp+99)//100
            if sp>a.sp:return f'{name} needs {sp} SP. {a.sp} left.'
            if need>=a.hp:return f'{name} costs {need} HP. You must survive the cost.'
        else:kind=''
        if target is not None:
            if kind in ('heal','sp') and getattr(target,'hp' if kind=='heal' else 'sp')==getattr(target,'max_hp' if kind=='heal' else 'max_sp'):
                return f'{target.label} already has full {"HP" if kind=="heal" else "SP"}.'
            if kind=='cure' and not target.status:return f'{target.label} has no ailment.'
            if kind=='clear-charm' and target.status!='charm':return f'{target.label} is not charmed.'
        if kind=='cure' and not any(u.status for u in self.allies if u.alive):return 'No ally has an ailment.'
        return ''

    def act(self,action,target=None,*,persona=None):
        """Resolve an action before recording any change for the renderer."""
        before={u:(u.hp,u.sp) for u in (*self.allies,*self.enemies)}
        actor=self.actor;pending=self.scan_pending
        self._charge_hits={};self._action_cues={}
        result=self._act(action,target,persona=persona)
        if result is None:
            now=monotonic()
            committed=action in ('guard','attack','allout') or action.startswith(('skill:','item:','theurgy:'))
            if committed:
                if pending and not self.outcome:self._resolve_scan()
                if not action.startswith('theurgy:'):self._charge_for(actor,action,target)
                self._nav_charge(4)
            for u,(hp,sp) in before.items():
                for key,x,y in (('hp',hp,u.hp),('sp',sp,u.sp)):
                    if x==y or key=='sp' and u.enemy:continue
                    if (u,key) not in self._action_cues:self._cue(u,key,y-x)
                    if self.reel is not None:self._reel_change.append(((u,key),x,y))
                    else:self.meters.record((u,key),x,y,now)
            if committed or self._action_cues:
                if self.reel is not None:self._reel_cues=self._action_cues.copy()
                else:self.cues.publish(self._action_cues,now)
        return result

    def _act(self,action,target=None,*,persona=None):
        """Resolve a single explicit action. Return a reason on refusal, else None."""
        if self.outcome:return 'This battle is over.'
        if isinstance(target,str):
            target=next((u for u in (*self.allies,*self.enemies) if target in (u.name,u.label)),None)
        if action=='great-seal':
            if not getattr(self.late_cycle,'seal_ready',False):return 'The Great Seal is not ready.'
            return self.late_cycle.special(self,action)
        if action=='oracle':return self._oracle()
        if action=='full-analysis':
            reason=self._scan_block()
            if reason:return reason
            self.scan_left-=1;self.scan_pending=True
            self._say('Fuuka begins Full Analysis.')
            return None
        if action.startswith('theurgy:'):return self._use_theurgy(action[8:],target)
        if action.startswith('persona:'):
            name=PERSONA_ALIASES.get(action[8:],action[8:])
            reason=self._persona_block(name)
            if reason:return reason
            self._equip(name)
            return None
        possible={'attack','guard','allout','shift','analyze'}
        if not (action in possible or action.startswith(('item:','skill:'))):return 'Unknown action.'
        persona=PERSONA_ALIASES.get(persona,persona) if action.startswith('skill:') else None
        reason=self._block(action,target,persona=persona)
        if reason:return reason
        targets=self._targets(action)
        if target is not None and target not in targets:return 'Choose a valid target.'
        if targets and target is None:return 'Choose a valid target.'
        if action.startswith('skill:') and SKILLS[action[6:]][4]=='one' and not targets:
            return 'No exposed Shadow can be targeted.'
        if action in ('shift','attack','analyze') and target is None:return 'Choose a target.'
        if action=='analyze':self.inspected=target;return None
        if action=='shift':
            self._say(f'Shift: {self.actor.label} → {target.label}.')
            self.actor=target;self.shifted=True;return None
        if action=='allout':
            actor=self.actor
            cast=tuple(u.label for u in self.allies if u.alive and not u.down)
            targets=tuple(self.targetable_enemies)
            self._say('SEES: All-Out Attack!')
            damage=34*len(cast)
            for u in targets:
                before=u.hp;u.hp=max(0,u.hp-damage)
                self._cue(u,'hp',u.hp-before)
                if not u.alive:u.down=False
                on_damage=getattr(self.late_cycle,'on_damage',None)
                if on_damage is not None:on_damage(self,self.actor,u,before-u.hp)
            cleared=not any(u.alive for u in self.enemies)
            self._committed()
            self._start_all_out(actor,cleared and self.outcome=='win',cast,len(targets))
            return None
        a=self.actor
        if action=='guard':
            a.guard=True;self._say(f'{a.label} guards.')
            self._committed();return None
        if action=='attack':
            self._committed(self._hit(a,target,a.element,a.power))
            return None
        if action.startswith('item:'):
            name=action[5:];kind,power=ITEMS[name]
            self.inventory[name]-=1
            self._recover(target,kind,power)
            self._committed();return None
        name=action[6:];kind,element,power,sp,mode,hp=SKILLS[name]
        if persona and persona!=self.persona:self._equip(persona)
        health_cost=(a.max_hp*hp+99)//100
        a.sp-=sp;a.hp-=health_cost
        self._cue(a,'sp',-sp);self._cue(a,'hp',-health_cost)
        self._say(f'{a.label} uses {name}.')
        if kind=='hit':
            extra=False
            for u in ([target] if mode=='one' else self.targetable_enemies):
                extra=self._hit(a,u,element,power) or extra
                if name=='Sonic Punch' and u.alive and not u.guard and not u.status and self.rng.random()<.48:
                    u.status='distress';self._say(f'{u.label} is distressed.')
                if not a.alive:break
            self._committed(extra)
        else:
            if kind in ('buff','debuff'):
                group={'team':[u for u in self.allies if u.alive], 'everyone':[u for u in self.order if u.alive],
                       'foes':self.targetable_enemies,'self':[a]}.get(mode,[target])
                for u in group:
                    for stat in ('attack','defense','agility') if element=='all_stats' else (element,):
                        self.modify_stat(u,stat,1 if kind=='buff' else -1)
                self._say(f'{"Everyone" if mode=="everyone" else "Squad" if mode=="team" else "Shadows" if mode=="foes" else a.label if mode=="self" else target.label}: {"critical chance" if element=="crit_boost" else element} {"up" if kind=="buff" else "down"}.')
            elif kind=='cure':
                target.status='';target.status_until=0;self._say(f'{target.label} recovers.')
            elif kind=='ailment':
                if self.rng.random()>=.76 or not upper.hold_status(self,target,element):
                    self._say(f'{target.label} resisted {name}.')
            elif kind=='heal' and mode=='team':
                for u in self.allies:
                    if u.alive:self._recover(u,kind,power)
            else:self._recover(target,kind,power)
            self._committed()
        return None

    def _recover(self,u,kind,power):
        if kind in ('heal','revive'):
            previous=u.hp
            u.hp=min(u.max_hp,u.hp+power);u.down=False
            self._say(f'{u.label} recovers {u.hp-previous} HP.')
        elif kind=='clear-charm':
            u.status='';u.status_until=0
            self._say(f'{u.label} clears Charm.')
        elif kind=='sp':
            previous=u.sp
            u.sp=min(u.max_sp,u.sp+power)
            self._say(f'{u.label} recovers {u.sp-previous} SP.')

    @staticmethod
    def _navigate(k,i,n):
        if not n:return 0
        if k in (C.KEY_UP,'k','K'):return (i-1)%n
        if k in (C.KEY_DOWN,'j','J'):return (i+1)%n
        if k==C.KEY_HOME:return 0
        if k==C.KEY_END:return n-1
        return min(i,n-1)

    @staticmethod
    def _choice(k,i,n):
        if k in ENTER and n:return min(i,n-1)
        if isinstance(k,str) and k in '123456789' and int(k)<=n:return int(k)-1
        return None

    def _details(self,action,target=None):
        a=self.actor
        if action.startswith('skill:'):
            name=action[6:]
            kind,element,power,sp,mode,hp=SKILLS[name]
            if kind=='hit':
                info=f'{element} • '+('all foes' if mode=='foes' else 'one foe')
            elif kind=='heal':info=f'Restore up to {power} HP'+(' to each living ally' if mode=='team' else '')
            elif kind=='ailment':info=f'Try to inflict {element.title()}'
            elif kind=='cure':info='Clear an ally’s ailment'
            elif mode=='everyone':info=f'CRIT ↑ for allies and foes • {STAT_TURNS} own turns'
            else:
                label='ATK/DEF/AGI' if element=='all_stats' else dict(STAT_NAMES).get(element,element.upper())
                scope={'team':' • allies','foes':' • foes','self':' • self'}.get(mode,'')
                info=label+(' ↑' if kind=='buff' else ' ↓')+scope+f' • {STAT_TURNS} own turns'
            if hp:info+=f' • {((a.max_hp*hp)+99)//100} HP'
            if sp:info+=f' • {sp} SP'
            return info
        if action.startswith('item:'):
            kind,power=ITEMS[action[5:]]
            return {'heal':f'Restore up to {power} HP','sp':f'Restore up to {power} SP',
                    'revive':f'Revive with {power} HP','clear-charm':'Clear Charm from one ally'}[kind]
        return {'attack':f'{a.element} • No cost','guard':'Reduce damage and avoid knockdown.',
                'shift':'Hand off this extra action. No damage boost or recovery.',
                'allout':'Strike every downed Shadow without spending SP.',
                'analyze':'Check learned affinities without spending a turn.',
                'full-analysis':f'Queued scan resolves after one action. {self.scan_left} left.',
                'theurgies':{
                    LEAD_ID:'Charge fastest by casting Persona skills.',
                    'Yukari':'Charge fastest by healing an ally.',
                    'Junpei':'Charge fastest by landing critical hits.',
                    'Akihiko':'Charge fastest by starting turns with a buff.',
                    'Mitsuru':'Charge fastest when a foe starts debuffed.',
                    'Aigis':'Charge fastest with physical skills that spend HP.',
                    'Koromaru':'Charge fastest with Dark skills.'
                }.get(a.name,'Requires a full gauge.')}.get(action,'')

    def _attack_element(self,action):
        if action=='attack':return self.actor.element
        if action=='allout':return 'Almighty'
        if action and action.startswith('skill:'):
            spec=SKILLS.get(action[6:])
            if spec and spec[0]=='hit':return spec[1]
        if action and action.startswith('theurgy:'):
            spec=THEURGIES.get(action[8:])
            if spec and spec[1] in ('damage','orgia'):return spec[2]
        return None

    def _affinity_tags(self,action):
        # Affinity-bypassing actions have a flavor color, not a target forecast.
        element=self._attack_element(action) if action=='attack' or action.startswith('skill:') else None
        if not element:return {}
        return {u:self.seen.get(u.name,{}).get(element,'unknown') for u in self.targetable_enemies}

    def _menu(self):
        empty=''
        if self.screen=='command':
            if getattr(self.late_cycle,'seal_ready',False):
                return [('Great Seal','great-seal',None,'','Use the power entrusted to Makoto.')]
            ids=('skills','attack','guard','items','shift','allout','analyze')
            rows=[(name,key,None,self._block(key) if key not in ('skills','items') else empty,
                   self._details(key)) for name,key in zip(self.COMMANDS,ids)]
            if self.fuuka or self.theurgy:
                label=f"Fuuka {self.charge['Fuuka']}%" if 'Fuuka' in self.charge else 'Fuuka'
                rows.append((label,'navigation',None,'','Open navigation support.'))
            if self.theurgy:
                locked=not self._theurgy_ids()
                rows.append(('Theurgy [LOCKED]' if locked else 'Theurgy','theurgies',None,
                             'Register Orpheus and Apsaras for Cadenza.' if locked and self.actor.name==LEAD_ID else
                             'No Theurgy is available.' if locked else '',
                             self._details('theurgies')))
            return rows
        if self.screen=='navigation':
            rows=[('Full Analysis','full-analysis',None,self._scan_block(),self._details('full-analysis'))]
            if 'Fuuka' in self.charge:
                rows.append(('Oracle','oracle',None,self._oracle_block(),
                             'Responds to the squad’s condition. Does not spend a turn.'))
            return rows
        if self.screen=='theurgies':
            return [(THEURGIES[k][0],'theurgy:'+k,None,self._theurgy_block(k),THEURGIES[k][-1])
                    for k in self._theurgy_ids()]
        if self.screen=='skills':
            rows=[]
            preview=self.mask_preview
            for name in self.stock[preview] if preview else self.actor.skills:
                aid='skill:'+name
                learned=self._affinity_tags(aid).values()
                tags=[AFFINITY_MARKS[t][2] for t in SKILL_AFFINITY_ORDER if t in learned]
                label=name+(' ['+' / '.join(tags)+']' if tags else '')
                rows.append((label,aid,None,self._block(aid,persona=preview),self._details(aid)))
            return rows
        if self.screen=='items':
            return [(f'{name} ×{n}','item:'+name,None,self._block('item:'+name),self._details('item:'+name))
                    for name,n in self.inventory.items()]
        known=self._affinity_tags(self.action)
        rows=[]
        for u in self._targets(self.action):
            badge=AFFINITY_MARKS[known.get(u,'unknown')][2]
            label=u.label+(f' [{badge}]' if badge else '')
            reason=self._theurgy_block(self.action[8:]) if self.action.startswith('theurgy:') else self._block(self.action,u,persona=self.mask_preview)
            detail=THEURGIES[self.action[8:]][-1] if self.action.startswith('theurgy:') else self._details(self.action,u)
            rows.append((label,self.action,u,reason,detail))
        return rows

    def _open(self,screen):
        self.back.append((self.screen,self.pick));self.screen=screen;self.pick=0

    def key(self,k):
        """Handle a battle key. False exits a resolved result; never forfeits on Escape."""
        if self.reel is not None:
            now=monotonic()
            if now>=self.reel[2] or k in (*ENTER,ESC,' '):self._finish_reel(now)
            return True
        low=k.lower() if isinstance(k,str) else k
        if self.overlay:
            if k==ESC or low in ('i','l','?') or self.overlay=='intel' and k in ENTER:
                self.overlay=None;return True
            if self.overlay=='log':
                if k in (C.KEY_UP,'k','K'):self.log_scroll=min(len(self.log),self.log_scroll+1)
                if k in (C.KEY_DOWN,'j','J'):self.log_scroll=max(0,self.log_scroll-1)
            return True
        if self.outcome:
            if low=='l':
                self.overlay='log';self.log_scroll=0;return True
            return k not in (*ENTER,ESC)
        if low in ('i','l','?'):
            self.overlay={'i':'status','l':'log','?':'help'}[low]
            self.log_scroll=0;return True
        if k==ESC:
            self.notice=''
            if self.back:self.screen,self.pick=self.back.pop()
            if self.screen=='command':self.mask_preview=None
            return True
        if self.persona_preview and k in (C.KEY_LEFT,C.KEY_RIGHT):
            masks=tuple(self.stock)
            self.mask_preview=masks[(masks.index(self.mask_preview or self.persona)+(1 if k==C.KEY_RIGHT else -1))%len(masks)]
            self.pick=0;self.notice=''
            return True
        if self.persona_preview and low=='p' and self.mask_preview and self.mask_preview!=self.persona:
            self.notice=self.act('persona:'+self.mask_preview) or ''
            self.mask_preview=None
            return True
        rows=self._menu()
        old=self.pick
        self.pick=self._navigate(k,self.pick,len(rows))
        if old!=self.pick:self.notice=''
        chosen=self._choice(k,self.pick,len(rows))
        if chosen is None:return True
        self.pick=chosen
        _,aid,target,reason,_=rows[chosen]
        if reason:
            self.notice=reason;return True
        self.notice=''
        if aid in ('skills','items','navigation','theurgies'):
            self._open(aid)
        elif self.screen!='target' and self._targets(aid):
            self.action=aid;self._open('target')
        else:
            reason=self.act(aid,target,persona=self.mask_preview)
            if reason:self.notice=reason;return True
            self.screen='command';self.pick=0;self.back=[];self.mask_preview=None
            if aid=='analyze':
                self.overlay='intel'
        return True

    @staticmethod
    def _line(app,y,x,text,color=WHITE,*,limit=None,active=False):
        n=max(0,min(app.w-1-x,limit if limit is not None else app.w))
        if n and 0<=y<app.h:
            app.put(y,x,text[:n],color,active,active)

    def _meter(self,app,y,x,u,width,now,*,sp=False):
        attr='sp' if sp else 'hp'
        value,maximum=getattr(u,attr),getattr(u,'max_'+attr)
        fill,tail,empty=self.meters.segments((u,attr),value,maximum,width,now)
        ink=CYAN if sp else GREEN if 10*value>3*maximum else GOLD
        # Keep thin fills even within the short compact status pairs.
        self._line(app,y,x,'▄'*fill,ink)
        self._line(app,y,x+fill,'▄'*tail,SCENE_INKS['navy'] if sp else RED)
        self._line(app,y,x+fill+tail,'▂'*empty,DIM)

    def _paint_cue(self,app,y,x,cue,text,*,sp=False):
        ink=(CYAN if sp else RED) if cue.delta<0 else GREEN if cue.delta>0 else GOLD
        self._line(app,y,x,text,ink)

    def _resource(self,app,y,x,bar,right,u,now,*,sp=False,detailed=True,inline_cue=True):
        attr='sp' if sp else 'hp'
        value,maximum=getattr(u,attr),getattr(u,'max_'+attr)
        abbr=attr.upper()
        short=f'{abbr} {value}'
        number=f'{short}/{maximum}' if detailed else short
        cue=self.cues.get((u,attr),now) if inline_cue else None
        if cue is not None:
            names=tuple(dict.fromkeys((number,short)))
            shapes=[(n,label) for label in cue.labels(abbr) for n in names if label]
            choice=next(((n,label) for n,label in shapes if len(n)+len(label)+4<=right-x),None)
            if choice is None:
                choice=next(((n,label) for n,label in shapes if len(n)+len(label)+1<=right-x),None)
            if choice is not None:
                number,label=choice
                start=right-len(label)
                bar=max(x+len(number)+1,min(bar,start-3))
                self._paint_cue(app,y,start,cue,label,sp=sp)
                right=start-1
        self._line(app,y,x,number,WHITE if u.alive else DIM)
        self._meter(app,y,bar,u,max(0,right-bar),now,sp=sp)

    def _ally_cues(self,app,y,left,right,u,now):
        """Use the spare line on tall panels so both meters stay anchored."""
        hp=self.cues.get((u,'hp'),now)
        sp=self.cues.get((u,'sp'),now)
        if sp:
            text=sp.labels('SP')[0]
            start=right-len(text)
            self._paint_cue(app,y,start,sp,text,sp=True)
            right=start-2
        if hp:
            text=next((t for t in hp.labels('HP') if len(t)<=right-left),'')
            if text:self._paint_cue(app,y,left,hp,text)

    def _affinity_row(self,app,y,x,unit=None):
        """Header or discovered-only strip, with aligned element columns."""
        start=x+2
        stride=max(2,min(6,(app.w-2-start)//len(ELEMENTS)))
        wide=stride>=5
        known=self.seen.get(unit.name,{}) if unit is not None else {}
        for i,element in enumerate(ELEMENTS):
            if unit is None:
                value=element[:3 if wide else 2].upper()
                color=ELEMENT_MARKS[element][1]
            else:
                compact,expanded,_,color=AFFINITY_MARKS[known.get(element,'unknown')]
                value=expanded if wide else compact
            self._line(app,y,start+i*stride,value,color,limit=stride)

    def _attack_choice(self,app,y,x,prefix,label,element,*,selected,blocked,limit):
        if not element:
            self._line(app,y,x,prefix+label,GREEN if selected else DIM if blocked else WHITE,
                       active=selected,limit=limit)
            return
        marker,ink=ELEMENT_MARKS[element]
        width=min(app.w-1-x,limit if limit is not None else app.w)
        width=max(0,width-len(prefix)-2)
        title,sep,badge=label.partition(' [')
        shown=title[:width]
        suffix=(sep+badge)[:width-len(shown)]
        self._line(app,y,x,prefix,GREEN if selected else DIM if blocked else WHITE,active=selected)
        x+=len(prefix)
        self._line(app,y,x,shown,ink)
        self._line(app,y,x+len(shown),suffix,DIM if blocked else WHITE)
        self._line(app,y,x+len(shown)+len(suffix)+1,marker,ink)

    def _frame(self,app,heading,footer):
        self._line(app,1,2,'◆ DARK HOUR',CYAN)
        self._line(app,1,max(18,app.w-len(heading)-3),heading,GREEN)
        self._line(app,2,2,'─'*(app.w-4),CYAN)
        self._line(app,app.h-3,2,'─'*(app.w-4),CYAN)
        self._line(app,app.h-2,max(2,(app.w-len(footer))//2),footer,DIM)

    def _draw_overlay(self,app):
        h,w=app.h,app.w
        nav='↑↓ SCROLL  ESC BACK' if self.overlay=='log' else 'ESC BACK'
        header={'log':'BATTLE LOG','status':'FIELD STATUS','help':'COMBAT GUIDE','intel':'AFFINITY SCAN'}[self.overlay]
        self._frame(app,header,nav)
        if self.overlay=='log':
            count=h-8
            start=min(max(0,len(self.log)-count-self.log_scroll),max(0,len(self.log)-count))
            for i,line in enumerate(self.log[start:start+count]):self._line(app,4+i,3,line)
        elif self.overlay=='intel':
            target=self.inspected
            self._line(app,4,3,target.label,GREEN)
            stats=stat_text(target)
            if stats:self._line(app,5,3,stats+'  •  own turns left',GOLD)
            known=self.seen.get(target.name,{})
            for i,element in enumerate(ELEMENTS):
                row,col=divmod(i,3)
                effect=known.get(element,'unknown')
                self._line(app,7+2*row,3+col*((w-6)//3),f'{element}  {effect.upper()}',AFFINITY_MARKS[effect][3])
            if 'vulnerable' in known.values():
                self._line(app,14,3,'Vulnerable: extra damage, but does not knock down.',DIM)
        elif self.overlay=='status':
            foes=[e for e in self.enemies if e.alive and e.stat_turns]
            split=w//2
            width=split-5 if foes else w-6
            for i,u in enumerate(self.allies):
                y=4+i*4
                title=u.label+(' / '+self.persona if i==0 else ' / '+sees.evolved(u.name,self.day)[0] if sees.evolved(u.name,self.day)[0] else '')
                self._line(app,y,3,title,GREEN,limit=width)
                status=f'   {u.status.upper()}' if u.status else ''
                self._line(app,y+1,3,f'HP {u.hp}/{u.max_hp}   SP {u.sp}/{u.max_sp}'+status,limit=width)
                affinity=' • '.join(f'{k} {v}' for k,v in u.affinity.items())
                self._line(app,y+2,3,affinity or 'No special affinities',DIM)
                stats=stat_text(u)
                if stats:self._line(app,y+3,3,stats,GOLD)
            if foes:
                for i,u in enumerate(foes[:4]):
                    y=4+i*4
                    self._line(app,y,split,u.label,GREEN)
                    self._line(app,y+1,split,stat_text(u),GOLD)
            if foes or any(u.stat_turns for u in self.allies):
                self._line(app,h-4,3,'↑ Buff  ↓ Debuff  •  Own turns left',DIM)
        else:
            topics=(('ONE MORE','A fresh weakness hit or critical earns another action.'),
                    ('SHIFT','Hand the extra action to a standing ally.'),
                    ('ALL-OUT',f'Down all enemies and keep {LEAD_NAME} standing.'),
                    ('GUARD','Reduce incoming damage and prevent knockdowns.'),
                    ('MONORAIL','Only committed actions tick; Shift and Analyze are free.'))
            for i,(title,about) in enumerate(topics):
                y=3+i*2
                self._line(app,y,3,title,GREEN)
                self._line(app,y+1,3,about)
            self._line(app,14,3,'ELEMENT COLORS',GREEN)
            column=(w-6)//5
            for idx,(element,(mark,ink)) in enumerate(ELEMENT_MARKS.items()):
                y,x=divmod(idx,5)
                self._line(app,15+y,3+x*column,f'{mark} {element}',ink,limit=column)
            self._line(app,19,3,'AFFINITY KEY',GREEN)
            self._line(app,20,3,'? Unknown   · Normal   W Weak   R Resist   N Null')
            self._line(app,21,3,'P Repel   D Drain   V Vulnerable (extra damage, no down)')

    def draw(self,app):
        """Draw with the host terminal's minimum put/w/h interface."""
        if self.reel is not None:
            name,began,over=self.reel
            now=monotonic()
            if now<over:
                inks={'red':RED,'gold':GOLD,'cyan':CYAN,'white':WHITE,'dim':DIM,'green':GREEN,**SCENE_INKS}
                if self._all_out_reel is None:
                    from persona3_cinematics import render_theurgy
                    frames=render_theurgy(name,now-began,app.w-1,app.h,low_motion=self.low_motion)
                else:
                    from persona3_allout import FINISH_SECONDS, IMPACT_SECONDS, render_all_out
                    span=FINISH_SECONDS if self._all_out_reel else IMPACT_SECONDS
                    elapsed=span*.8 if self.low_motion else now-began
                    frames=render_all_out(name,elapsed,app.w-1,app.h,finishing=self._all_out_reel,
                                          cast=self._all_out_cast,targets=self._all_out_targets)
                for y,runs in enumerate(frames):
                    x=0
                    for text,ink in runs:
                        if text.strip():self._line(app,y,x,text,inks.get(ink,WHITE))
                        x+=len(text)
                return
            self._finish_reel(now)
        if self.overlay:return self._draw_overlay(app)
        h,w=app.h,app.w
        now=monotonic()
        outcome_title={'win':'VICTORY','loss':'SQUAD DEFEATED','timeout':'TIME EXPIRED'}.get(self.outcome)
        outcome_ink=GREEN if self.outcome=='win' else RED
        if self.outcome:
            self._frame(app,self.title.upper(),'↵ CONTINUE  '+('A ADJUST LEAD  ' if self.adjust_lead and self.outcome!='win' else '')+'L LOG')
            if not self.meters.active(now,settle=.10):
                self._line(app,7,max(3,(w-len(outcome_title))//2),outcome_title,outcome_ink)
                self._line(app,10,3,self.log[-1])
                if self.outcome=='loss':
                    for n,line in enumerate(self.defeat_cause.splitlines()):
                        self._line(app,12+n,3,line,GOLD)
                return
        else:
            nav='↑↓ SELECT  ↵ CONFIRM  ESC BACK'
            if self.persona_preview:
                nav='←→ PREVIEW  '+('P EQUIP  ' if self.mask_preview and self.mask_preview!=self.persona else '')+nav
            self._frame(app,self.title.upper(),nav if self.screen!='command' else
                        '↑↓ SELECT  ↵ CONFIRM  I STATUS  L LOG  ? GUIDE')
        if self.clock is not None:
            self._line(app,4,3,f'IMPACT IN {self.clock:02} ACTIONS',RED if self.clock<=6 else GREEN)
            self._line(app,5,3,self.threat,GOLD)
        elif self.threat:self._line(app,4,3,self.threat,GOLD)
        split=w//2
        # At the compact minimum a third foe uses one otherwise blank
        # header row. Four foes share one selected affinity strip so
        # the combat choices stay above the log instead of under it.
        foes=self.late_cycle.visible if self.late_cycle else self.tank_cycle.visible if self.tank_cycle else self.enemies
        compact_group=h<28 and len(foes)>=4
        first=7 if h<28 and len(foes)>=3 else 8
        spacing=2 if compact_group else 4 if h>=34 else 3
        ally_spacing=2 if h<28 else spacing
        has_ally_cue_row=ally_spacing>=4
        ally_number=17
        detailed=split>=44
        ally_bar=ally_number+(12 if detailed else 8)
        shadow_number=split+2
        shadow_bar=shadow_number+12
        self._line(app,first-1,3,'SEES',CYAN)
        if (next_unit:=self.next_actor) is not None:
            self._line(app,first-1,10,f'NEXT {next_unit.label}',GOLD,limit=split-11)
        self._affinity_row(app,first-1,split)
        selected=None
        if not self.outcome and self.screen=='target':
            candidates=self._targets(self.action)
            if candidates:selected=candidates[min(self.pick,len(candidates)-1)]
        for i,u in enumerate(self.allies):
            y=first+ally_spacing*i
            marker='▶' if u is self.actor else '›' if u is selected else ' '
            self._line(app,y,3,f'{marker} {u.label}',GREEN if u is self.actor else WHITE if u.alive else DIM)
            state='KO' if not u.alive else u.status.upper() if u.status in upper.CONTROLLED else 'DOWN' if u.down else 'GUARD' if u.guard else u.status.upper()
            if u.name=='Aigis' and u.alive and (self.orgia or self.orgia_cooldown):
                state='ORGIA' if self.orgia else 'COOL'
            if self.theurgy:
                grade=self.charge[u.name]
                self._line(app,y+1,3,f'TG {grade:>3}%',GOLD if grade==100 else CYAN)
                if state:self._line(app,y+1,11,state if len(state)<=5 else '!',GOLD if u.alive else DIM)
            elif state:self._line(app,y+1,5,state,GOLD if u.alive else DIM)
            for j in range(2):
                self._resource(app,y+j,ally_number,ally_bar,split-1,u,now,sp=j==1,
                               detailed=detailed,inline_cue=not has_ally_cue_row)
            if has_ally_cue_row:self._ally_cues(app,y+2,5,split-1,u,now)
        for i,u in enumerate(foes):
            y=first+spacing*i
            state=(' KO' if not u.alive else ' ↓' if u.down else ' GUARD' if u.guard else
                   ' EXPOSED' if self.is_exposed(u) else '')
            marker='▶' if u is selected else ' '
            title_row=f'{marker} {u.label}{state}'
            self._line(app,y,split,title_row,WHITE if u.alive else DIM)
            cue=self.cues.get((u,'hp'),now)
            in_name=False
            if cue:
                result=cue.labels('HP')[0]
                start=w-2-len(result)
                if result and start>split+len(title_row):
                    self._paint_cue(app,y,start,cue,result)
                    in_name=True
            self._resource(app,y+1,shadow_number,shadow_bar,w-2,u,now,inline_cue=not in_name)
            if u.alive and not compact_group:self._affinity_row(app,y+2,split,u)
        if compact_group:
            inspect=selected if selected in foes and selected.alive else next(iter(self.targetable_enemies),None)
            if inspect:
                y=first+spacing*len(foes)
                self._line(app,y,3,'AFFINITY / '+inspect.label,DIM,limit=split-5)
                self._affinity_row(app,y,split,inspect)
        roster_end=max(first+ally_spacing*(len(self.allies)-1)+(2 if has_ally_cue_row else 1),
                       first+spacing*(len(foes)-1)+2)
        top=roster_end+1
        if self.outcome:
            self._line(app,top,3,outcome_title,outcome_ink)
            self._line(app,h-5,3,self.log[-1])
            return
        if self.screen=='navigation' and 'Fuuka' in self.charge:
            value=self.charge['Fuuka']
            self._line(app,3,3,f'ORACLE {value:>3}%',GOLD if value==100 else WHITE)
            n=meter_cells(value,100,16)
            self._line(app,3,20,'▄'*n,GOLD if value==100 else CYAN)
            self._line(app,3,20+n,'▂'*(16-n),DIM)
        if self.screen=='skills' and self.actor is self.allies[0]:
            name=self.mask_preview or self.persona
            defenses=', '.join(f'{k} {v}' for k,v in PERSONAS[name]['affinity'].items())
            self._line(app,3,3,f'Defense: {defenses or "Normal"}',DIM)
        title={'command':('ALL-OUT READY' if self.all_out else 'ONE MORE' if self.one_more else 'COMMANDS'),
               'skills':((self.mask_preview or self.persona) if self.actor is self.allies[0] else self.actor.label)
                        +(' / PREVIEW' if self.mask_preview and self.mask_preview!=self.persona else ' / SKILLS'),
               'items':'SUPPLIES','target':'TARGET','navigation':'FUUKA / NAVIGATION',
               'theurgies':f'{self.actor.label.upper()} / THEURGY'}[self.screen]
        aimed=self._attack_element(self.action) if self.screen=='target' else None
        if aimed:
            marker,ink=ELEMENT_MARKS[aimed]
            self._line(app,top,3,f'{title}  {marker} {aimed.upper()}',ink)
        else:self._line(app,top,3,title,GREEN)
        rows=self._menu()
        if not rows:self._line(app,top+1,3,self._theurgy_block() if self.screen=='theurgies' else 'No supplies left.',DIM)
        capacity=max(1,h-6-top)
        # Compact three-foe battles may need three short command columns.
        # Grouping preserves the numeric and arrow traversal order.
        columns=(len(rows)+capacity-1)//capacity if self.screen=='command' else 1
        columns=max(1,columns)
        column_width=(w-6)//columns
        limit=capacity*columns
        start=min(max(0,self.pick-limit+1),max(0,len(rows)-limit))
        if len(rows)>limit:
            position=f'{self.pick+1}/{len(rows)}'
            self._line(app,top,w-3-len(position),position,DIM)
        for i,(label,aid,target,reason,_) in enumerate(rows[start:start+limit],start):
            selected=i==self.pick
            col,row=divmod(i-start,capacity)
            prefix=f'{i+1} ' if i<9 else ''
            element=self._attack_element(aid) if self.screen!='target' else None
            self._attack_choice(app,top+1+row,3+col*column_width,('▶ ' if selected else '  ')+prefix,
                                label,element,selected=selected,blocked=bool(reason),
                                limit=column_width-2 if columns>1 else None)
        if self.log:self._line(app,h-5,3,self.log[-1],WHITE)
        if rows:
            selected=rows[min(self.pick,len(rows)-1)]
            detail=self.notice or selected[3] or selected[4]
            if detail:self._line(app,h-4,3,detail,GOLD if self.notice or selected[3] else DIM)
