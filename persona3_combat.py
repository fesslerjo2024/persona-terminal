"""Early standalone Persona 3 terminal combat, with no Persona 5 dependencies."""
from dataclasses import dataclass
import curses as C
import random
from time import monotonic
from persona3_meters import MeterTrails, meter_cells
from reel_palette import IDS as SCENE_INKS

RED,GOLD,CYAN,WHITE,DIM,GREEN=range(1,7)
ENTER=(C.KEY_ENTER,'\n','\r')
ESC='\x1b'
LEAD_ID='Protagonist'  # Stable roster/resource key.
LEAD_NAME='Makoto'


def display_name(unit_id):
    return LEAD_NAME if unit_id==LEAD_ID else unit_id


ELEMENTS=('Slash','Strike','Pierce','Fire','Ice','Electric','Wind','Light','Dark')
PARTY={
    LEAD_ID:(130,54,'Slash',('Agi','Bash','Tarunda'),{'Electric':'weak','Dark':'weak'}),
    'Yukari':(116,54,'Pierce',('Garu','Dia','Patra'),{'Electric':'weak','Wind':'resist'}),
    'Junpei':(148,44,'Slash',('Agi','Cleave','Rakukaja'),{'Wind':'weak','Fire':'resist'}),
}
START_RESOURCES={name:record[:2] for name,record in PARTY.items()}
PERSONAS={
    'Orpheus':(('Agi','Bash','Tarunda'),{'Electric':'weak','Dark':'weak'}),
    'Pixie':(('Zio','Dia','Rakunda'),{'Ice':'weak','Electric':'resist'}),
    'Angel':(('Garu','Dia','Sukukaja'),{'Dark':'weak','Wind':'resist','Light':'resist'}),
    'Nekomata':(('Agi','Cleave','Tarunda'),{'Ice':'weak','Fire':'resist'}),
    "Jack O'Lantern":(('Agi','Maragi','Rakunda'),{'Ice':'weak','Fire':'drain'}),
    'Apsaras':(('Bufu','Dia','Sukukaja'),{'Fire':'weak','Ice':'resist'}),
}
PERSONAS={k:{'skills':spec[0],'affinity':spec[1]} for k,spec in PERSONAS.items()}
PERSONA_ALIASES={"Jack-o'-Lantern":"Jack O'Lantern","Jack-o’-Lantern":"Jack O'Lantern",
                  'Jack-o-Lantern':"Jack O'Lantern"}
BAG={'Medicine':3,'Soul Drop':1,'Revival Bead':1}
ITEMS={'Medicine':('heal',50),'Soul Drop':('sp',12),'Revival Bead':('revive',40)}
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
# Name, max HP, attack type, power, weaknesses/resists, role.
FOES={
    'maya':('Cowardly Maya',28,'Strike',13,{'Slash':'weak','Fire':'weak'},''),
    'tiara':('Muttering Tiara',43,'Fire',15,{'Wind':'weak'},''),
    'hand':('Magic Hand',49,'Strike',18,{'Fire':'weak','Electric':'resist'},''),
    'ruthless':('Ruthless Ice Raven',102,'Ice',24,{'Fire':'weak','Ice':'resist','Wind':'resist'},''),
    'beast':('Barbaric Beast Wheel',141,'Strike',29,{'Wind':'weak','Fire':'resist'},''),
    'axle':('Swift Axle',158,'Wind',28,{'Electric':'weak','Slash':'resist','Strike':'resist','Wind':'resist'},'axle'),
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

    def __init__(self,encounter,*,resources=None,persona='Orpheus',seed=None,inventory=None):
        encounter=ALIASES.get(encounter,encounter)
        if encounter not in ENCOUNTERS:raise ValueError(f'Unknown encounter: {encounter}')
        persona=PERSONA_ALIASES.get(persona,persona.strip() if isinstance(persona,str) else persona)
        if persona not in PERSONAS:raise ValueError(f'Unknown Persona: {persona}')
        self.encounter=encounter;self.title,foes=ENCOUNTERS[encounter]
        self.rng=random.Random(seed)
        self._carry=dict(START_RESOURCES)
        self._carry.update(resources or {})
        self.allies=[];self.enemies=[];self.persona=persona
        for i,(name,(hp,sp,element,skills,affinity)) in enumerate(PARTY.items()):
            if i and encounter=='awakening':break
            current=self._carry[name]
            if isinstance(current,dict):current=(current.get('hp',hp),current.get('sp',sp))
            if i==0:skills,affinity=PERSONAS[persona]['skills'],PERSONAS[persona]['affinity']
            self.allies.append(Unit(name,hp,sp,max(0,min(hp,int(current[0]))),
                max(0,min(sp,int(current[1]))),element,23 if i==0 else 20+i,skills,dict(affinity)))
        self.inventory={name:max(0,int((BAG if inventory is None else inventory).get(name,0))) for name in BAG}
        self.log=[];self.seen={};self.outcome=None;self.one_more=False;self.shifted=False
        self.round=1;self.clock=30 if encounter=='priestess' else None
        self._rail_stage=0;self._slot=0;self._shadow_turns=0;self._charge=False
        self.screen='command';self.pick=0;self.back=[];self.overlay=None;self.action=None
        self.notice='';self.log_scroll=0;self.inspected=None
        self.meters=MeterTrails()
        for name in foes:self._spawn(name,foes.count(name)>1)
        self.order=[*self.allies,*self.enemies]
        self.actor=self.allies[0]
        if self.clock is not None:self._say('Mitsuru: Reach Priestess before the train hits the station.')
        if not self.actor.alive:self._finish('loss')

    @property
    def resources(self):
        return dict(self._carry,**{u.name:(u.hp,u.sp) for u in self.allies})

    @property
    def remaining(self):
        return self.clock

    @property
    def all_out(self):
        living=[e for e in self.enemies if e.alive]
        return (self.one_more and self.allies[0].alive and not self.allies[0].down
                and sum(u.alive and not u.down for u in self.allies)>=2
                and bool(living) and all(e.down for e in living))

    @property
    def shift_targets(self):
        if not self.one_more or self.shifted:return []
        return [u for u in self.allies if u is not self.actor and u.alive and not u.down and not u.status]

    @property
    def threat(self):
        if self.clock is not None:
            if self.clock<=6:return 'Last stretch. Defeat Priestess before impact.'
            if self._rail_stage>=1:return 'Invitation to Chaos shortened the countdown.'
            return 'Each committed action advances the train.'
        if self._charge:return 'Swift Axle is charging. Guard or knock it down.'
        return ''

    def _spawn(self,key,tagged=False):
        name,hp,element,power,affinity,role=FOES[key]
        if tagged:name+=' '+chr(65+sum(u.name.startswith(name+' ') for u in self.enemies))
        unit=Unit(name,hp,0,hp,0,element,power,(),dict(affinity),True,role)
        self.enemies.append(unit)
        if hasattr(self,'order'):self.order.append(unit)
        return unit

    def _say(self,msg):
        self.log.append(msg)
        if len(self.log)>80:del self.log[0]

    def _finish(self,result):
        self.outcome=result
        self.one_more=False;self.shifted=False
        self._say({'win':'Shadows defeated.','loss':f'{LEAD_NAME} falls.','timeout':'The train reaches the station before you can stop it.'}[result])

    def _ended(self):
        if not self.allies[0].alive:self._finish('loss')
        elif self.clock is not None and not self.enemies[0].alive:self._finish('win')
        elif all(not u.alive for u in self.enemies):self._finish('win')
        return self.outcome is not None

    def _hit(self,a,t,element,power,can_crit=True):
        effect=t.affinity.get(element,'normal')
        accuracy=100+14*(a.agility-t.agility)
        if accuracy<100 and self.rng.randrange(100)>=accuracy:
            self._say(f'{t.label} dodges.')
            return False
        if not a.enemy and t.enemy:self.seen.setdefault(t.name,{})[element]=effect
        varied=round(power*self.rng.uniform(.93,1.07))
        damage=max(1,round(varied*(1+.20*a.attack)*(1-.23*t.defense)))
        if effect in ('null','repel','drain'):
            if effect=='drain':t.hp=min(t.max_hp,t.hp+damage)
            if effect=='repel':a.hp=max(0,a.hp-damage)
            self._say(f'{t.label}: {effect.upper()} {element}.')
            return False
        crit=can_crit and not t.guard and effect!='resist' and element in ELEMENTS[:3] and self.rng.random()<(.22 if t.status=='distress' else .12)
        if effect=='weak':damage=round(damage*1.55)
        if effect=='vulnerable':damage=round(damage*1.25)
        if effect=='resist':damage=round(damage*.52)
        if crit:damage=round(damage*1.4)
        if t.guard:damage=max(1,round(damage*.45))
        fresh=(effect=='weak' or crit) and not t.down and not t.guard
        t.hp=max(0,t.hp-damage)
        if fresh and t.alive:t.down=True
        if not t.alive:t.down=False
        flags=[flag for yes,flag in ((effect=='weak','WEAK'),(effect=='resist','RESIST'),(crit,'CRIT'),(t.guard,'GUARD')) if yes]
        self._say(f'{t.label} takes {damage}'+(' ['+' '.join(flags)+']' if flags else '')+'.')
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

    def _enemy_turn(self,u):
        live=[x for x in self.allies if x.alive]
        if not live:return False
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
                    bonus=self._hit(u,t,'Strike',30,False) or bonus
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
            self._slot=(self._slot+1)%len(self.order)
            if self._slot==0:self.round+=1
            u=self.order[self._slot]
            if not u.alive:continue
            self.actor=u;u.guard=False
            if u.down:
                u.down=False
                if u.role=='axle' and self._charge:
                    self._charge=False;self._say('The knockdown interrupts Swift Axle’s charge.')
            if not u.enemy:return
            more=self._enemy_turn(u)
            if self._ended():return
            if more:
                self._say(f'{u.label} earns One More!')
                # Cap enemy follow-up at one; the opening slice remains recoverable.
                self._enemy_turn(u)
                if self._ended():return

    def _committed(self,extra=False):
        if self.clock is not None:self.clock=max(0,self.clock-1)
        if self._ended():return
        self._rail_events()
        if self.outcome:return
        if extra:
            self.one_more=True;self.shifted=False
            self._say('All Shadows down.' if self.all_out else f'{self.actor.label} earns One More!')
        else:self._advance()

    def _targets(self,action):
        if action=='shift':return self.shift_targets
        if action=='analyze' or action=='attack':return [u for u in self.enemies if u.alive]
        if action.startswith('item:'):
            kind,_=ITEMS[action[5:]]
            return [u for u in self.allies if u.alive!=(kind=='revive')]
        if action.startswith('skill:'):
            spec=SKILLS[action[6:]]
            if spec[4]=='ally':return [u for u in self.allies if u.alive]
            if spec[4]=='one':return [u for u in self.enemies if u.alive]
        return []

    def _block(self,action,target=None):
        a=self.actor
        if action=='allout' and not self.all_out:return f'Down every Shadow. Keep {LEAD_NAME} and one ally standing.'
        if action=='shift' and not self.shift_targets:return 'Shift is available once per One More.'
        if action.startswith('item:'):
            name=action[5:]
            if name not in ITEMS or not self.inventory.get(name):return 'That item is no longer in the bag.'
            if not self._targets(action):return 'No knocked-out ally to revive.'
            kind,_=ITEMS[name]
        elif action.startswith('skill:'):
            name=action[6:]
            if name not in a.skills:return 'That Persona does not know this skill.'
            kind,_,_,sp,_,hp=SKILLS[name]
            need=(a.max_hp*hp+99)//100
            if sp>a.sp:return f'{name} needs {sp} SP. {a.sp} left.'
            if need>=a.hp:return f'{name} costs {need} HP. You must survive the cost.'
        else:kind=''
        if target is not None:
            if kind in ('heal','sp') and getattr(target,'hp' if kind=='heal' else 'sp')==getattr(target,'max_hp' if kind=='heal' else 'max_sp'):
                return f'{target.label} already has full {"HP" if kind=="heal" else "SP"}.'
            if kind=='cure' and not target.status:return f'{target.label} has no ailment.'
        if kind=='cure' and not any(u.status for u in self.allies if u.alive):return 'No ally has an ailment.'
        return ''

    def act(self,action,target=None):
        """Resolve an action before recording any change for the renderer."""
        before={u:(u.hp,u.sp) for u in (*self.allies,*self.enemies)}
        result=self._act(action,target)
        if result is None:
            now=monotonic()
            for u,(hp,sp) in before.items():
                self.meters.record((u,'hp'),hp,u.hp,now)
                if not u.enemy:self.meters.record((u,'sp'),sp,u.sp,now)
        return result

    def _act(self,action,target=None):
        """Resolve a single explicit action. Return a reason on refusal, else None."""
        if self.outcome:return 'This battle is over.'
        if isinstance(target,str):
            target=next((u for u in (*self.allies,*self.enemies) if target in (u.name,u.label)),None)
        possible={'attack','guard','allout','shift','analyze'}
        if not (action in possible or action.startswith(('item:','skill:'))):return 'Unknown action.'
        reason=self._block(action,target)
        if reason:return reason
        targets=self._targets(action)
        if targets and target not in targets:return 'Choose a valid target.'
        if action in ('shift','attack','analyze') and target is None:return 'Choose a target.'
        if action=='analyze':self.inspected=target;return None
        if action=='shift':
            self._say(f'Shift: {self.actor.label} → {target.label}.')
            self.actor=target;self.shifted=True;return None
        if action=='allout':
            self._say('SEES: All-Out Attack!')
            damage=34*sum(u.alive and not u.down for u in self.allies)
            for u in self.enemies:
                if u.alive:
                    u.hp=max(0,u.hp-damage)
                    if not u.alive:u.down=False
            self._committed();return None
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
        a.sp-=sp;a.hp-=(a.max_hp*hp+99)//100
        self._say(f'{a.label} uses {name}.')
        if kind=='hit':
            extra=False
            for u in ([target] if mode=='one' else [u for u in self.enemies if u.alive]):
                extra=self._hit(a,u,element,power) or extra
                if not a.alive:break
            self._committed(extra)
        else:
            if kind in ('buff','debuff'):
                setattr(target,element,1 if kind=='buff' else -1)
                self._say(f'{target.label}: {element} {"up" if kind=="buff" else "down"}.')
            elif kind=='cure':
                target.status='';self._say(f'{target.label} recovers.')
            else:self._recover(target,kind,power)
            self._committed()
        return None

    def _recover(self,u,kind,power):
        if kind in ('heal','revive'):
            previous=u.hp
            u.hp=min(u.max_hp,u.hp+power);u.down=False
            self._say(f'{u.label} recovers {u.hp-previous} HP.')
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
            elif kind=='heal':info=f'Restore up to {power} HP'
            elif kind=='cure':info='Clear an ally’s ailment'
            else:info=element.upper()+(' ↑' if kind=='buff' else ' ↓')
            if hp:info+=f' • {((a.max_hp*hp)+99)//100} HP'
            if sp:info+=f' • {sp} SP'
            return info
        if action.startswith('item:'):
            kind,power=ITEMS[action[5:]]
            return {'heal':f'Restore up to {power} HP','sp':f'Restore up to {power} SP',
                    'revive':f'Revive with {power} HP'}[kind]
        return {'attack':f'{a.element} • No cost','guard':'Reduce damage and avoid knockdown.',
                'shift':'Hand off this extra action. No damage boost or recovery.',
                'allout':'Strike every downed Shadow without spending SP.',
                'analyze':'Check learned affinities without spending a turn.'}.get(action,'')

    def _affinity_tags(self,action):
        element=None
        if action=='attack':element=self.actor.element
        if action.startswith('skill:') and SKILLS[action[6:]][0]=='hit':
            element=SKILLS[action[6:]][1]
        if not element:return {}
        return {u:self.seen.get(u.name,{}).get(element,'unknown') for u in self.enemies if u.alive}

    def _menu(self):
        empty=''
        if self.screen=='command':
            ids=('skills','attack','guard','items','shift','allout','analyze')
            return [(name,key,None,self._block(key) if key not in ('skills','items') else empty,
                     self._details(key)) for name,key in zip(self.COMMANDS,ids)]
        if self.screen=='skills':
            rows=[]
            for name in self.actor.skills:
                aid='skill:'+name
                learned=self._affinity_tags(aid).values()
                danger=[t.upper() for t in ('drain','repel','null','weak') if t in learned]
                label=name+(' ['+' / '.join(danger)+']' if danger else '')
                rows.append((label,aid,None,self._block(aid),self._details(aid)))
            return rows
        if self.screen=='items':
            return [(f'{name} ×{n}','item:'+name,None,self._block('item:'+name),self._details('item:'+name))
                    for name,n in self.inventory.items() if n]
        known=self._affinity_tags(self.action)
        return [(u.label+(' ['+known[u].upper()+']' if known.get(u) in ('weak','null','repel','drain') else ''),
                 self.action,u,self._block(self.action,u),self._details(self.action,u))
                for u in self._targets(self.action)]

    def _open(self,screen):
        self.back.append((self.screen,self.pick));self.screen=screen;self.pick=0

    def key(self,k):
        """Handle a battle key. False exits a resolved result; never forfeits on Escape."""
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
        if aid in ('skills','items'):
            self._open(aid)
        elif self.screen!='target' and self._targets(aid):
            self.action=aid;self._open('target')
        else:
            reason=self.act(aid,target)
            if reason:self.notice=reason;return True
            self.screen='command';self.pick=0;self.back=[]
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

    def _frame(self,app,heading,footer):
        self._line(app,1,2,'◆ DARK HOUR',CYAN)
        self._line(app,1,max(18,app.w-len(heading)-3),heading,GREEN)
        self._line(app,2,2,'─'*(app.w-4),CYAN)
        self._line(app,app.h-3,2,'─'*(app.w-4),CYAN)
        self._line(app,app.h-2,max(2,(app.w-len(footer))//2),footer,DIM)

    def _draw_overlay(self,app):
        h,w=app.h,app.w
        nav='↑↓ SCROLL  ESC BACK' if self.overlay=='log' else 'ESC BACK'
        header={'log':'BATTLE LOG','status':'SQUAD STATUS','help':'COMBAT GUIDE','intel':'AFFINITY SCAN'}[self.overlay]
        self._frame(app,header,nav)
        if self.overlay=='log':
            count=h-8
            start=min(max(0,len(self.log)-count-self.log_scroll),max(0,len(self.log)-count))
            for i,line in enumerate(self.log[start:start+count]):self._line(app,4+i,3,line)
        elif self.overlay=='intel':
            target=self.inspected
            self._line(app,4,3,target.label,GREEN)
            known=self.seen.get(target.name,{})
            for i,element in enumerate(ELEMENTS):
                row,col=divmod(i,3)
                value=known.get(element,'unknown').upper()
                self._line(app,7+2*row,3+col*((w-6)//3),f'{element}  {value}',GOLD if value=='WEAK' else DIM)
        elif self.overlay=='status':
            for i,u in enumerate(self.allies):
                y=4+i*4
                title=u.label+(' / '+self.persona if i==0 else '')
                self._line(app,y,3,title,GREEN)
                status=f'   {u.status.upper()}' if u.status else ''
                self._line(app,y+1,3,f'HP {u.hp}/{u.max_hp}   SP {u.sp}/{u.max_sp}'+status)
                affinity=' • '.join(f'{k} {v}' for k,v in u.affinity.items())
                self._line(app,y+2,3,affinity or 'No special affinities',DIM)
        else:
            topics=(('ONE MORE','A fresh weakness hit or critical earns another action.'),
                    ('SHIFT','Hand the extra action to a standing ally.'),
                    ('ALL-OUT',f'Down all enemies and keep {LEAD_NAME} standing.'),
                    ('GUARD','Reduce incoming damage and prevent knockdowns.'),
                    ('MONORAIL','Only committed actions tick; Shift and Analyze are free.'))
            for i,(title,about) in enumerate(topics):
                y=4+i*3
                self._line(app,y,3,title,GREEN)
                self._line(app,y+1,3,about)

    def draw(self,app):
        """Draw with the host terminal's minimum put/w/h interface."""
        if self.overlay:return self._draw_overlay(app)
        h,w=app.h,app.w
        now=monotonic()
        outcome_title={'win':'VICTORY','loss':'SQUAD DEFEATED','timeout':'TIME EXPIRED'}.get(self.outcome)
        outcome_ink=GREEN if self.outcome=='win' else RED
        if self.outcome:
            self._frame(app,self.title.upper(),'↵ CONTINUE  L LOG')
            if not self.meters.active(now,settle=.10):
                self._line(app,7,max(3,(w-len(outcome_title))//2),outcome_title,outcome_ink)
                self._line(app,10,3,self.log[-1])
                return
        else:
            self._frame(app,self.title.upper(),'↑↓ SELECT  ↵ CONFIRM  ESC BACK' if self.screen!='command' else
                        '↑↓ SELECT  ↵ CONFIRM  I STATUS  L LOG  ? GUIDE')
        if self.clock is not None:
            self._line(app,4,3,f'IMPACT IN {self.clock:02} ACTIONS',RED if self.clock<=6 else GREEN)
            self._line(app,5,3,self.threat,GOLD)
        elif self.threat:self._line(app,4,3,self.threat,GOLD)
        split=w//2
        spacing=4 if h>=34 else 3 if h>=28 else 2
        ally_number=17
        detailed=split>=44
        ally_bar=ally_number+(12 if detailed else 8)
        shadow_number=split+2
        shadow_bar=shadow_number+12
        self._line(app,7,3,'SEES',CYAN)
        self._line(app,7,split,'SHADOWS',CYAN)
        selected=None
        if not self.outcome and self.screen=='target':
            candidates=self._targets(self.action)
            if candidates:selected=candidates[min(self.pick,len(candidates)-1)]
        for i,u in enumerate(self.allies):
            y=8+spacing*i
            marker='▶' if u is self.actor else '›' if u is selected else ' '
            self._line(app,y,3,f'{marker} {u.label}',GREEN if u is self.actor else WHITE if u.alive else DIM)
            state='KO' if not u.alive else 'DOWN' if u.down else 'GUARD' if u.guard else u.status.upper()
            if state:self._line(app,y+1,5,state,GOLD if u.alive else DIM)
            for j,(label,value,maximum) in enumerate((('HP',u.hp,u.max_hp),('SP',u.sp,u.max_sp))):
                number=f'{label} {value}'+(f'/{maximum}' if detailed else '')
                self._line(app,y+j,ally_number,number,WHITE if u.alive else DIM)
                self._meter(app,y+j,ally_bar,u,split-1-ally_bar,now,sp=j==1)
        for i,u in enumerate(self.enemies):
            y=8+spacing*i
            state=' KO' if not u.alive else ' ↓' if u.down else ''
            marker='▶' if u is selected else ' '
            self._line(app,y,split,f'{marker} {u.label}{state}',WHITE if u.alive else DIM)
            self._line(app,y+1,shadow_number,f'HP {u.hp}/{u.max_hp}',WHITE if u.alive else DIM)
            self._meter(app,y+1,shadow_bar,u,w-2-shadow_bar,now)
        top=11+spacing*(max(len(self.allies),len(self.enemies))-1)
        if self.outcome:
            self._line(app,top,3,outcome_title,outcome_ink)
            self._line(app,h-5,3,self.log[-1])
            return
        title={'command':('ALL-OUT READY' if self.all_out else 'ONE MORE' if self.one_more else 'COMMANDS'),
               'skills':(self.persona if self.actor is self.allies[0] else self.actor.label)+' / SKILLS',
               'items':'SUPPLIES','target':'TARGET'}[self.screen]
        self._line(app,top,3,title,GREEN)
        rows=self._menu()
        if not rows:self._line(app,top+1,3,'No supplies left.',DIM)
        capacity=max(1,h-6-top)
        # Two short columns keep every main command visible at 65×25 even
        # with three status pairs on each side. Navigation order is unchanged.
        columns=2 if self.screen=='command' and len(rows)>capacity else 1
        limit=capacity*columns
        start=min(max(0,self.pick-limit+1),max(0,len(rows)-limit))
        if len(rows)>limit:
            position=f'{self.pick+1}/{len(rows)}'
            self._line(app,top,w-3-len(position),position,DIM)
        for i,(label,aid,target,reason,_) in enumerate(rows[start:start+limit],start):
            selected=i==self.pick
            col,row=divmod(i-start,capacity)
            prefix=f'{i+1} ' if i<9 else ''
            self._line(app,top+1+row,3+col*split,('▶ ' if selected else '  ')+prefix+label,
                       GREEN if selected else DIM if reason else WHITE,active=selected,
                       limit=split-4 if columns==2 else None)
        if self.log:self._line(app,h-5,3,self.log[-1],WHITE)
        if rows:
            selected=rows[min(self.pick,len(rows)-1)]
            detail=self.notice or selected[3] or selected[4]
            if detail:self._line(app,h-4,3,detail,GOLD if self.notice or selected[3] else DIM)
