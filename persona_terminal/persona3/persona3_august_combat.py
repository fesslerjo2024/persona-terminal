"""August full-moon boss forms and Aigis' combat kit.

Reference: https://www.youtube.com/watch?v=Yib906pJ3HY&t=1083s
Terminal tuning compresses the HP scale and uses round-based reform windows.
"""

ENCOUNTER='chariot-justice'
TANK,CHARIOT,JUSTICE='tank','chariot','justice'
FORMS=(TANK,CHARIOT,JUSTICE)
PHYSICAL=('Slash','Strike','Pierce')
FOES={
    'august-tank':('Tank-Form Shadow',400,'Pierce',30,
                   dict.fromkeys((*PHYSICAL,'Fire','Ice','Electric','Wind','Light','Dark'),'resist'),TANK),
    'august-chariot':('Chariot',207,'Strike',30,dict.fromkeys(PHYSICAL,'resist'),CHARIOT),
    'august-justice':('Justice',176,'Pierce',29,
                      dict.fromkeys(('Fire','Ice','Electric','Wind','Light','Dark'),'resist'),JUSTICE),
}
ENCOUNTERS={ENCOUNTER:('Underground Bunker',tuple(FOES))}
AIGIS=(157,47,'Pierce',('Swift Strike','Marakukaja','Matarukaja'),{'Electric':'weak','Pierce':'resist'})
SKILLS={
    'Swift Strike':('hit','Strike',38,0,'foes',11),
    'Marakukaja':('buff','defense',0,9,'team',0),
    'Matarukaja':('buff','attack',0,9,'team',0),
}
THEURGY=('Orgia Mode','orgia','Pierce',72,'group','Three turns of automatic fire, then one cooldown turn.')


class TankCycle:
    def __init__(self,battle):
        self.tank,self.chariot,self.justice=battle.enemies
        self.chariot.hp=self.justice.hp=0
        self.stage=TANK
        self.exposed=0
        self.count=0
        self.reform=False
        self.hp=(self.chariot.max_hp,self.justice.max_hp)

    @property
    def visible(self):
        return (self.tank,) if self.stage==TANK else (self.chariot,self.justice)

    def threat(self):
        if self.stage==TANK:
            if self.cracking:
                if self.count%3==1:return 'CANNON AIMED / Shell cracking. Guard or break through.'
                return 'SHELL CRACKING / Keep pressure on.'
            return ('CANNON AIMED / Guard or force the shell open.' if self.count%3==1 else
                    'ARMORED SHELL / Damage or Almighty can split it.')
        if self.chariot.alive!=self.justice.alive:
            survivor=self.chariot if self.chariot.alive else self.justice
            return f'REVIVAL INCOMING / Defeat {survivor.label} before it acts.'
        if self.reform:
            return 'RECOMBINE INCOMING / Finish both halves before they reform.'
        return 'SEPARATED / Bring both halves down before either revives.'

    @property
    def split_hp(self):
        return self.tank.max_hp*2//3

    @property
    def cracking(self):
        return self.split_hp<self.tank.hp<=self.split_hp+self.tank.max_hp//12

    def settle(self,b,*,force=False):
        if self.stage!=TANK:return
        if not force and self.tank.hp>self.split_hp:return
        self.tank.hp=0
        self.chariot.hp,self.justice.hp=self.hp
        self.exposed=0
        self.reform=False
        self.stage='split'
        b._say('The shell splits. Two separate Shadows emerge.')

    def _merge(self,b):
        self.hp=(self.chariot.hp,self.justice.hp)
        self.chariot.hp=self.justice.hp=0
        self.tank.hp=self.tank.max_hp*5//6
        b.clear_stats(self.tank)
        self.count=0
        self.stage=TANK
        b._say('Both halves recombine. Their wounds carry into the next split.')

    def turn(self,b,u,bonus):
        live=[x for x in b.allies if x.alive]
        if u is self.tank:
            self.count+=1
            if self.count%3==1:
                b._say('The tank sights in its main cannon.')
                return False
            if self.count%3==2:
                b._say('The tank fires its High-Explosive Shell.')
                more=False
                for target in live:
                    more=b._hit(u,target,'Pierce',43,False) or more
                    if not b.allies[0].alive:break
                return more
        else:
            partner=self.justice if u is self.chariot else self.chariot
            if not partner.alive:
                partner.hp=max(1,partner.max_hp//3)
                partner.down=partner.guard=False
                b._say(f'{u.label} revives {partner.label} at {partner.hp} HP.')
                return False
            if u is self.justice and not bonus and self.exposed%2==0:
                target=min(live,key=lambda v:(v.hp/v.max_hp,v.label))
                b._say(f'Justice fires at {target.label}.')
                return b._hit(u,target,'Pierce',41,False)
            if u is self.chariot and not bonus:
                if self.reform:
                    self._merge(b)
                    return False
                self.exposed+=1
                if self.exposed==3:
                    self.reform=True
                    b._say('Chariot signals Justice to recombine next round.')
        target=max(live,key=lambda x:(not x.guard,b.rng.random()))
        b._say(f'{u.label} attacks.')
        return b._hit(u,target,u.element,u.power,False)


def orgia_burst(b,u):
    b._say('Aigis opens fire in Orgia Mode.')
    for target in [e for e in b.enemies if e.alive]:
        b._hit(u,target,'Pierce',THEURGY[3],False,ignore_affinity=True)
    b.orgia-=1
    if not b.orgia:
        b.orgia_cooldown=True
        b._say('Aigis overheats and must cool down next turn.')
