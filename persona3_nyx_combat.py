"""January 31: Adamah approach, Strega rematches, and fourteen Arcana.

Recorded Reload gameplay: https://www.youtube.com/watch?v=AfNqizWPIr0
(Strega, Nyx Avatar, and post-Avatar finale), and
https://www.youtube.com/watch?v=DDBmG6Ye2ac (all fourteen Arcana).
Affinities follow Reload's distinct phase profiles rather than those from
FES or Portable. Damage and scripted response windows are tuned for the
terminal campaign.
"""
from dataclasses import dataclass

from persona3_summit import APPROACH


JIN = 'strega-jin'
TAKAYA = 'strega-takaya'
AVATAR = 'nyx-avatar'
PHYSICAL = ('Slash','Strike','Pierce')
MAGIC = ('Fire','Ice','Electric','Wind','Light','Dark')


FOES = {
    # Normal 257–261F variants, not the similarly named Monad variants.
    'adamah-magus': ('Grand Magus',98,'Ice',30,
                    {'Strike':'null','Fire':'weak','Ice':'repel','Light':'repel','Dark':'repel'},'magus'),
    'adamah-turret': ('Wicked Turret',117,'Fire',31,
                     {'Pierce':'repel','Fire':'resist','Electric':'weak'},'strike'),
    JIN: ('Jin',480,'Fire',36,{'Fire':'repel','Dark':'repel'},JIN),
    TAKAYA: ('Takaya',532,'Almighty',40,{'Light':'repel','Dark':'drain'},TAKAYA),
    AVATAR: ('Nyx Avatar',60,'Almighty',27,{},AVATAR),
}
ENCOUNTERS = {
    APPROACH: ('258F / Shadow Patrol',('adamah-magus','adamah-turret')),
    JIN: ('259F / Jin Rematch',(JIN,)),
    TAKAYA: ('263F / Takaya Rematch',(TAKAYA,)),
    AVATAR: ('264F / Nyx Avatar',(AVATAR,)),
}


@dataclass(frozen=True)
class Form:
    name:str
    health:int
    affinity:dict
    move:str=''
    element:str='Almighty'
    damage:int=0
    group:bool=True


FORMS = (
    Form('Fool',60,{}),
    Form('Magician',82,{'Fire':'null'},'Agidyne','Fire',29,False),
    Form('Priestess',82,{'Ice':'null'},'Ice Storm','Ice',24),
    Form('Empress',86,dict.fromkeys(MAGIC,'resist'),'Magarudyne','Wind',24),
    Form('Emperor',86,dict.fromkeys(PHYSICAL,'resist'),'Sweep','Slash',24),
    Form('Hierophant',88,{'Light':'repel','Dark':'null'},'Doomsday Doctrine','Almighty',23),
    Form('Lovers',88,{'Pierce':'resist','Fire':'null','Electric':'resist'},'Heartbreaker','Almighty',24),
    Form('Chariot',90,dict.fromkeys(PHYSICAL,'null'),'Deathbound','Slash',25),
    Form('Justice',90,dict.fromkeys(MAGIC,'null'),'Makougaon','Light',26),
    Form('Hermit',92,{'Pierce':'resist','Electric':'null','Wind':'null','Dark':'null'},
         'High-Volt Current','Electric',33,False),
    Form('Fortune',64,dict.fromkeys(('Fire','Ice','Wind','Light'),'drain'),'Inferno','Fire',32,False),
    Form('Strength',96,{'Slash':'resist','Strike':'repel','Pierce':'resist'},
         'God’s Hand','Strike',34,False),
    Form('Hanged Man',104,{'Strike':'resist','Fire':'null','Dark':'repel'},'Megidolaon','Almighty',30),
    Form('Death',720,{},'Megidolaon','Almighty',34),
)


def _living(b):
    return [a for a in b.allies if a.alive]


def _target(b, element, *, prefer_weak=True, excluded=()):
    pool = [a for a in _living(b) if a not in excluded] or _living(b)
    return min(pool,key=lambda a:(a.affinity.get(element)!='weak' if prefer_weak else False,
                                  a.guard,a.down,a.hp/a.max_hp))


def _impact(b, boss, name, element, power, targets):
    more=False
    b._say(f'{boss.label} uses {name}.')
    for a in targets:
        more=b._hit(boss,a,element,power,False,ignore_affinity=element=='Almighty') or more
        if not b.allies[0].alive:
            break
    return more


class Strega:
    def __init__(self,b):
        self.b=b
        self.boss=b.enemies[0]
        self.beat=0
        self.signal=''
        self.aim=None
        self.stimulant=False
        self.grenade_hits=0

    @property
    def visible(self):
        return tuple(self.b.enemies)

    def threat(self):
        if self.signal=='grenade':
            name,element,_,target = self.aim
            advice='Guard or switch Persona.' if target is self.b.allies[0] else 'Guard.'
            return f'{name.upper()} / {target.label}: {advice}'
        if self.signal=='stim':
            return 'MEGIDOLAON NEXT / Guard or finish Jin.'
        if self.signal=='persona':
            return 'HYPNOS NEXT / Guard against Dark.'
        return ('WEAKNESS SCAN / Jin reads the squad.' if self.b.encounter==JIN and self.beat==0 else
                'TAKAYA / Be ready for Soul Drain.' if self.b.encounter==TAKAYA else '')

    def _jin_plan(self,b):
        options=(('Flame Grenade','Fire',37),('Shock Grenade','Electric',36),
                 ('Bufudyne','Ice',42))
        name,element,power=max(options,key=lambda x:sum(a.affinity.get(x[1])=='weak' for a in _living(b)))
        target=_target(b,element)
        self.aim=(name,element,power,target)
        self.signal='grenade'
        b._say(f'Jin scans, then aims {name} at {target.label}.')
        return False

    def turn(self,b,u,bonus):
        if u is not self.boss:
            return None
        live=_living(b)
        if not live:
            return False
        if bonus:
            _impact(b,u,'follow-up','Almighty',23,[_target(b,'Almighty')])
            return False
        self.beat+=1
        if self.signal:
            move,self.signal=self.signal,''
            if move=='grenade':
                name,element,power,target=self.aim
                self.aim=None
                return _impact(b,u,name,element,power,[target if target.alive else _target(b,element)])
            if move=='stim':
                _impact(b,u,'Megidolaon','Almighty',53,live)
                return False
            return _impact(b,u,'Hypnos','Dark',47,live)
        if b.encounter==JIN:
            if u.hp*100<=u.max_hp*38 and not self.stimulant:
                self.stimulant=True
                u.hp=min(u.max_hp,u.hp+round(u.max_hp*.16))
                self.signal='stim'
                b._say('Jin uses Potent Stim Injection. Guard for Megidolaon.')
                return False
            if self.beat%4 in (1,3):
                return self._jin_plan(b)
            if self.beat%4==0:
                return _impact(b,u,'EX Flash Grenade','Almighty',31,live)
        else:
            if self.beat%4==1 or self.beat%4==0 and u.hp*2<=u.max_hp:
                self.signal='persona'
                b._say('Takaya calls Hypnos. Brace before the persona attacks.')
                return False
            if self.beat%4==3:
                target=max(live,key=lambda a:(a.sp,not a.guard))
                cost=min(target.sp,8 if target.guard else 15)
                target.sp-=cost
                b._say(f'Takaya uses Soul Drain. {target.label} loses {cost} SP.')
                return False
            if u.hp*2<=u.max_hp:
                _impact(b,u,'Megidolaon','Almighty',39,live)
                return False
        return _impact(b,u,'Hamaon' if b.encounter==TAKAYA else 'Flame Grenade',
                       'Light' if b.encounter==TAKAYA else 'Fire',33,
                       [_target(b,'Light' if b.encounter==TAKAYA else 'Fire')])


class NyxCycle:
    def __init__(self,b):
        self.b=b
        self.boss=b.enemies[0]
        self.index=0
        self.beat=0
        self.death_beats=0
        self.apocalypse=False
        self.apocalypse_used=False
        self.night_queen=False
        self.night_queen_used=False
        self._shift(b,0,announce=False)

    @property
    def visible(self):
        return tuple(self.b.enemies)

    @property
    def form(self):
        return FORMS[self.index]

    def can_down(self,foe):
        return foe is not self.boss

    def _shift(self,b,i,announce=True):
        self.index=i; self.beat=0
        u=self.boss; f=self.form
        u.hp=u.max_hp=f.health
        u.element=f.element;u.power=f.damage
        u.affinity=dict(f.affinity)
        u.down=u.guard=False
        u.status='';u.status_until=0
        b.clear_stats(u)
        if hasattr(b,'_arcana_phase'):
            b._arcana_phase[u.name]=i
        b.seen.pop(u.name,None)
        if announce:
            b._say(f'Arcana Shift: {f.name}. Previous affinity readings cleared.')

    def threat(self):
        if self.apocalypse:return 'APOCALYPSE NEXT / Guard, then recover.'
        if self.night_queen:return 'NIGHT QUEEN NEXT / Guard against the curse.'
        return f'ARCANA {self.index+1}/14 / {self.form.name.upper()}'

    def on_damage(self,b,a,t,damage):
        if t is self.boss:
            t.down=False
            t.status='';t.status_until=0

    def settle(self,b):
        u=self.boss
        u.down=False
        u.status='';u.status_until=0
        if u.alive or not b.allies[0].alive:
            return
        if self.index+1<len(FORMS):
            self._shift(b,self.index+1)
        else:
            b._say('The Avatar falls. Above Tartarus, the moon is still moving.')

    def turn(self,b,u,bonus):
        if u is not self.boss:return None
        live=_living(b)
        if not live or bonus:return False
        self.beat+=1
        f=self.form
        if self.index==0:
            self._shift(b,1)
            return False
        if f.name!='Death':
            if f.name=='Strength' and self.beat%3==1:
                b.modify_stat(u,'attack',1)
                b._say('Nyx Avatar raises its attack with Tarukaja.')
                return False
            if f.name=='Hanged Man' and self.beat%3==1:
                b._say('The Hanged Man gathers its magic.')
                return False
            if f.name=='Lovers' and self.beat%3==1:
                for a in live:
                    if not a.guard and not a.status and b.rng.random()<.25:
                        a.status='charm';a.status_until=b.round+2
                        b._say(f'{a.label} is charmed.')
            targets=live if f.group else [_target(b,f.element)]
            _impact(b,u,f.move,f.element,f.damage,targets)
            return False
        self.death_beats+=1
        if self.night_queen:
            self.night_queen=False
            _impact(b,u,'Night Queen','Almighty',46,live)
            for a in (v for v in live if v.alive and not v.guard and not v.status):
                if b.rng.random()<.35:
                    a.status='fear';a.status_until=b.round+2
                    b._say(f'{a.label} is afraid.')
            return False
        if self.apocalypse:
            self.apocalypse=False
            b._say('Nyx Avatar uses Apocalypse.')
            for a in live:
                a.hp=max(1,round(a.hp*(.58 if a.guard else .16)))
            return False
        if not self.night_queen_used and (u.hp*3<=u.max_hp*2 or self.death_beats>=3):
            self.night_queen=self.night_queen_used=True
            b._say('Nyx Avatar gathers a dark aura. Guard for Night Queen.')
            return False
        if not self.apocalypse_used and u.hp*3<=u.max_hp:
            self.apocalypse=self.apocalypse_used=True
            b._say('Nyx Avatar prepares Apocalypse. Guard and save a heal.')
            return False
        if self.death_beats%4==0:
            _impact(b,u,'Megidolaon','Almighty',31,live)
            return False
        if self.death_beats%4==2:
            b._say('Grim Transcendence: Nyx Avatar strikes twice.')
            for k in range(2):
                _impact(b,u,'Sweep','Slash',29,[_target(b,'Slash')])
                if not b.allies[0].alive:break
            return False
        _impact(b,u,'Sweep','Slash',36,[_target(b,'Slash')])
        return False


def make_cycle(b):
    if b.encounter==AVATAR:return NyxCycle(b)
    if b.encounter in (JIN,TAKAYA):return Strega(b)
    return None
