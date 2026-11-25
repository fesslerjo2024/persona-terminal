"""October/November Full Moon battles and the hospital confrontation.

References are the original fights in play:
10/4 https://www.youtube.com/watch?v=jsfQDkR0Cto&t=433s
11/3 https://www.youtube.com/watch?v=tAfniKvSOQg&t=251s
11/22 https://www.youtube.com/watch?v=e0LG8QJINEA
Fixed and ordinary damage are scaled to the terminal party's HP.
"""

from persona3_upper_combat import hold_status


FORTUNE='fortune-strength'
STREGA='takaya-jin'
BRIDGE='hanged-man'
CHIDORI='chidori'


def statue_affinities(*weak):
    return {element:'weak' if element in weak else 'resist'
            for element in ('Slash','Strike','Pierce','Fire','Ice','Electric','Wind','Light','Dark')}


FIRST_SEALS=('seal-left','seal-center','seal-right')
SECOND_SEALS=('seal-gale','seal-claw','seal-ember')
FOES={
    'shadow-strength':('Strength',390,'Strike',36,{'Light':'null','Dark':'null'},'shadow-strength'),
    'shadow-fortune':('Fortune',254,'Wind',34,
        {'Strike':'weak','Electric':'weak','Fire':'drain','Ice':'drain','Wind':'drain','Light':'drain'},'shadow-fortune'),
    'moon-takaya':('Takaya',365,'Light',31,{'Light':'repel','Dark':'null'},'moon-takaya'),
    'moon-jin':('Jin',302,'Fire',31,{'Fire':'repel','Dark':'repel'},'moon-jin'),
    'arcana-hanged':('Hanged Man',665,'Dark',36,{'Strike':'resist','Fire':'null','Dark':'repel'},'arcana-hanged'),
    'seal-left':('Left Statue',69,'Ice',20,statue_affinities('Strike','Ice'),'moon-seal'),
    'seal-center':('Center Statue',69,'Electric',20,statue_affinities('Slash','Electric'),'moon-seal'),
    'seal-right':('Right Statue',69,'Light',20,statue_affinities('Pierce','Light'),'moon-seal'),
    'seal-gale':('Left Statue',70,'Wind',22,statue_affinities('Wind','Slash'),'moon-seal'),
    'seal-claw':('Center Statue',70,'Strike',22,statue_affinities('Strike','Electric'),'moon-seal'),
    'seal-ember':('Right Statue',70,'Fire',22,statue_affinities('Fire','Pierce'),'moon-seal'),
    'seal-great':('Great Statue',138,'Strike',29,statue_affinities(),'moon-seal'),
    'armed-maya':('Devious Maya',70,'Fire',21,{'Ice':'weak','Dark':'null'},'armed-maya'),
    'moon-chidori':('Chidori',320,'Fire',33,{'Fire':'drain'},'moon-chidori'),
}
ENCOUNTERS={
    FORTUNE:('Iwatodai Station • Fortune & Strength',('shadow-strength','shadow-fortune')),
    STREGA:('Moonlight Bridge • Takaya & Jin',('moon-takaya','moon-jin')),
    BRIDGE:('Moonlight Bridge • Hanged Man',('arcana-hanged',*FIRST_SEALS)),
    CHIDORI:('Chidori Confrontation',('moon-chidori',)),
}


def hit_team(b,attacker,element,power):
    extra=False
    for target in b.allies:
        if target.alive:extra=b._hit(attacker,target,element,power,False) or extra
        if not b.allies[0].alive:break
    return extra


def living_ally(b):
    return min((u for u in b.allies if u.alive),key=lambda u:(u.guard,u.hp/u.max_hp))


class Cycle:
    def __init__(self,b):
        self.b=b

    @property
    def visible(self):
        return self.b.enemies

    def targetable(self,u):
        return u.alive

    def settle(self,b):
        pass


class FortuneCycle(Cycle):
    WHEEL_DAMAGE=62
    all_out_against_exposed=True

    def __init__(self,b):
        super().__init__(b)
        self.strength,self.fortune=b.enemies
        self.spin=0
        self.strength_turn=0
        self.fortune_turn=0
        b._say('Strength’s illusion shields Fortune.')

    def targetable(self,u):
        return u.alive and (u is not self.fortune or not self.strength.alive)

    def threat(self):
        if self.fortune.alive and self.spin==1:
            return f'ROULETTE NEXT / Heal above {self.WHEEL_DAMAGE} HP. Fixed damage.'
        if self.fortune.alive and self.strength.alive:
            return 'ILLUSION / Defeat Strength to expose Fortune.'
        if self.fortune.alive and self.fortune_turn:
            return 'WIND NEXT / Guard if weak to Wind.'
        return ''

    def turn(self,b,u,bonus):
        if bonus:return None
        if u is self.strength:
            self.strength_turn+=1
            if self.strength_turn%3==0:
                target=living_ally(b)
                b._say(f'Strength casts Marin Karin on {target.label}.')
                hold_status(b,target,'charm')
                return False
            if self.strength_turn%3==2:
                b._say('Strength sweeps the field with Swift Strike.')
                return hit_team(b,u,'Strike',26)
            return None
        if self.spin==0:
            self.spin=1
            for unit in (*b.allies,*b.enemies):
                if unit.alive:b.modify_stat(unit,'attack',1)
            b._say('Wheel of Fortune raises the attack of both sides.')
            return False
        if self.spin==1:
            self.spin=2
            b._say(f'Wheel of Fortune takes {self.WHEEL_DAMAGE} HP from every ally.')
            for unit in b.allies:
                if unit.alive:unit.hp=max(0,unit.hp-self.WHEEL_DAMAGE)
            if not b.allies[0].alive:b.defeat_cause=f'Wheel of Fortune took {self.WHEEL_DAMAGE} HP from every ally.'
            return False
        if self.strength.alive:
            b._say('Fortune watches from behind the illusion.')
            return False
        self.fortune_turn+=1
        if self.fortune_turn==1:
            b._say('Fortune steadies its wheel and gathers Wind.')
            return False
        if self.fortune_turn%2==0:
            b._say('Fortune casts Magarudyne.')
            return hit_team(b,u,'Wind',31)
        b._say('Fortune casts Garudyne.')
        return b._hit(u,living_ally(b),'Wind',44,False)


class StregaCycle(Cycle):
    def __init__(self,b):
        super().__init__(b)
        self.takaya,self.jin=b.enemies
        self.jin_turn=0
        self.takaya_turn=0
        self.grenade_target=None

    def threat(self):
        if self.takaya.alive and any(u.alive and u.status=='fear' for u in self.b.allies):
            return 'GHASTLY WAIL / Cure Fear or Guard before Takaya acts.'
        if self.jin.alive and self.grenade_target and self.grenade_target.alive:
            return f'FRAG GRENADE / {self.grenade_target.label} should Guard.'
        return ''

    def turn(self,b,u,bonus):
        if bonus:return None
        if u is self.jin:
            mode=self.jin_turn%3
            self.jin_turn+=1
            if mode==0:
                self.grenade_target=living_ally(b)
                b._say(f'Jin readies a frag grenade for {self.grenade_target.label}.')
                return False
            if mode==1:
                target,self.grenade_target=self.grenade_target,None
                if not target or not target.alive:return False
                b._say(f'Jin throws Frag Grenade at {target.label}.')
                hp=target.hp
                b._hit(u,target,'Almighty',36,False)
                if target.alive and target.hp<hp and not target.down and not target.guard:
                    target.down=True
                    return True
                return False
            if self.takaya.alive:
                for stat in ('attack','defense'):b.modify_stat(self.takaya,stat,1)
                b._say('Jin bolsters Takaya with Heat Riser.')
                return False
            b._say('Jin throws Flame Grenade.')
            return b._hit(u,living_ally(b),'Fire',43,False)
        mode=self.takaya_turn%4
        self.takaya_turn+=1
        if mode==0:
            target=living_ally(b)
            b._say(f'Takaya uses Evil Smile on {target.label}.')
            hold_status(b,target,'fear')
            return False
        if mode==1:
            scared=[a for a in b.allies if a.alive and a.status=='fear']
            if scared:
                b._say('Takaya uses Ghastly Wail.')
                extra=False
                for target in scared:
                    extra=b._hit(u,target,'Dark',57,False) or extra
                    if not b.allies[0].alive:break
                return extra
        if mode==3 and u.hp*2<=u.max_hp:
            b._say('Takaya casts Megidola.')
            return hit_team(b,u,'Almighty',25)
        return None


class HangedCycle(Cycle):
    all_out_against_exposed=True

    def __init__(self,b):
        super().__init__(b)
        self.boss=b.enemies[0]
        self.seals=self.b.enemies[1:]
        self.stage=1
        self.maya=None
        self.armed=False
        self.ground_turn=0
        self.airborne=True
        self.transcend=False
        b._say('Three statues suspend Hanged Man. Break the seals.')

    @property
    def visible(self):
        return (self.boss,*[u for u in self.b.enemies[1:] if u.alive])

    def targetable(self,u):
        return u.alive and (u is not self.boss or not self.airborne)

    def exposed(self,u):
        return u is self.boss and u.alive and not self.airborne

    def can_act(self,u):
        return u is not self.boss or not self.airborne

    def threat(self):
        if not self.boss.alive:return ''
        if self.airborne:
            if self.stage==3:return 'GREAT STATUE / Defeat it to expose Hanged Man.'
            return 'AIRBORNE / Break the statues to expose Hanged Man.'
        if self.maya and self.maya.alive and self.armed:
            return 'ARMED AND READY / Destroy Devious Maya or Guard.'
        if self.transcend:
            return 'GRIM TRANSCENDENCE / Guard against a double attack.'
        return 'GROUNDED / Strike while the seals are broken.'

    def settle(self,b):
        if self.airborne and all(not u.alive for u in self.seals):
            self.airborne=False
            self.ground_turn=0
            b._say('All seals break. Hanged Man drops into reach.')
        elif not self.airborne and self.stage<3:
            floor=self.boss.max_hp*(67 if self.stage==1 else 34)//100
            if self.boss.hp<=floor:
                self.boss.hp=floor
                self._raise(b,self.stage+1)

    def _raise(self,b,stage):
        self.stage=stage
        self.airborne=True
        self.transcend=False
        self.boss.down=False
        if self.maya:self.maya.hp=0
        self.maya=None
        self.seals=[b._spawn(k) for k in (SECOND_SEALS if stage==2 else ('seal-great',))]
        for u in self.seals:b.seen.pop(u.name,None)
        b._say('Hanged Man rises behind new statues.' if stage==2 else
               'Hanged Man raises the Great Statue.')

    def turn(self,b,u,bonus):
        if u is self.maya:
            if bonus:return False
            if not self.armed:
                self.armed=True
                b._say('Devious Maya is Armed and Ready.')
                return False
            b._say('Devious Maya self-destructs.')
            more=hit_team(b,u,'Almighty',34)
            u.hp=0;u.down=False
            return more
        if u is not self.boss:return None
        if self.airborne:return False
        if bonus:return None
        self.ground_turn+=1
        if self.ground_turn%4==1 and (not self.maya or not self.maya.alive):
            self.maya=b._spawn('armed-maya')
            self.armed=False
            b._say('Hanged Man summons Devious Maya.')
            return False
        if self.transcend:
            self.transcend=False
            b._say('Hanged Man casts Maeigaon and follows with God’s Hand.')
            extra=hit_team(b,u,'Dark',30)
            if b.allies[0].alive:extra=b._hit(u,living_ally(b),'Strike',43,False) or extra
            return extra
        if self.stage>=2 and self.ground_turn%4==2:
            self.transcend=True
            b._say('Hanged Man prepares Grim Transcendence.')
            return False
        return None


class ChidoriCycle(Cycle):
    def __init__(self,b):
        super().__init__(b)
        self.chidori=b.enemies[0]
        self.recovered=False
        self.turn_no=0

    def threat(self):
        if self.b.outcome:return ''
        if self.turn_no%3==0:
            return ('MARAGIDYNE NEXT / Guard if weak. Spring of Life spent.' if self.recovered else
                    'MARAGIDYNE NEXT / Guard if weak to Fire.')
        return 'SPRING OF LIFE SPENT' if self.recovered else ''

    def settle(self,b):
        u=self.chidori
        if not self.recovered and u.hp*5<=u.max_hp:
            self.recovered=True
            u.hp=u.max_hp;u.down=False
            b._say('Chidori uses Spring of Life and fully recovers.')
        elif self.recovered and (u.hp*5<=u.max_hp*3 or self.turn_no>=6) and b.allies[0].alive:
            u.hp=max(1,u.hp);u.down=False
            b._finish('win')
            b.log[-1]='Chidori puts away her weapon. The confrontation ends.'

    def turn(self,b,u,bonus):
        if bonus:return None
        mode=self.turn_no%3
        self.turn_no+=1
        if mode==0:
            b._say('Chidori casts Maragidyne.')
            return hit_team(b,u,'Fire',38)
        if mode==1:
            b._say('Chidori uses Neuro Slash.')
            return hit_team(b,u,'Slash',29)
        return None


def make_cycle(b):
    controller={FORTUNE:FortuneCycle,STREGA:StregaCycle,BRIDGE:HangedCycle,CHIDORI:ChidoriCycle}
    kind=controller.get(b.encounter)
    return kind(b) if kind else None
