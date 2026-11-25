"""September 5 Full Moon: Arcana Hermit's electrical attack cycle.

Gameplay reference: Persona 3 Reload, Sept. 5 battle at Club Escapade
(https://www.youtube.com/watch?v=8BZ0mmGkH0U&t=712s). Charge windows
and damage below are scaled to this terminal's party/blocking model.
"""

ENCOUNTER='hermit'
FOE='arcana-hermit'
DEFAULT_ROSTER=('Protagonist','Yukari','Mitsuru')
FOES={FOE:('Hermit',665,'Electric',25,
           {'Electric':'null','Wind':'null','Dark':'null'},FOE)}
ENCOUNTERS={ENCOUNTER:('Club Escapade • Hermit',(FOE,))}

# The strongest crossed threshold takes precedence on a large hit.
WINDOWS=((22,'Tera Spark',2,71),(55,'Giga Spark',3,60),(90,'Mega Spark',3,49))


class HermitCycle:
    def __init__(self,battle):
        self.boss=battle.enemies[0]
        self.window=None
        self.beats=0
        self.stagger=0
        self.used=set()
        self.ordinary=0

    def threat(self):
        if not self.boss.alive:return ''
        if not self.window:
            return 'HERMIT / Watch for its electrical charge.'
        _,name,_,_=self.window
        if self.beats==1:
            return (f'{name.upper()} NEXT / Guard or deal {self.stagger} to interrupt.'
                    if self.stagger else f'{name.upper()} NEXT / Guard or finish Hermit.')
        if not self.stagger:
            return f'{name.upper()} CHARGING / Hermit’s defense is down.'
        return f'{name.upper()} CHARGING / {self.stagger} damage to interrupt.'

    def on_damage(self,b,actor,target,damage):
        if target is not self.boss or actor.enemy or not target.alive or not damage:
            return
        urgent=(22 not in self.used and target.hp*100<=target.max_hp*22)
        if self.window:
            if self.stagger:
                self.stagger=max(0,self.stagger-damage)
                if not self.stagger:
                    name=self.window[1]
                    self.window=None
                    self.beats=0
                    b._say(f'{name} interrupted. Hermit loses its charge.')
            if self.window and not urgent:return
        pending=next((window for window in WINDOWS
                      if window[0] not in self.used and target.hp*100<=target.max_hp*window[0]),None)
        if pending is None:return
        limit,name,self.beats,_=pending
        self.used.update(w[0] for w in WINDOWS if w[0]>=limit)
        self.window=pending
        if limit==22:
            self.stagger=0
            # Permanent phase vulnerability, not the Rakunda status.
            b.clear_stats(target,stat='defense')
            target.defense=-1
            b._say('Accelerated Charging: Hermit drops its defense.')
        else:
            party=sum(u.alive for u in b.allies)
            self.stagger=65+32*party+(limit==55)*25
            b._say(f'Hermit uses Initiate Charging for {name}.')

    def _team_hit(self,b,live,element,power):
        extra=False
        for target in live:
            extra=b._hit(self.boss,target,element,power,False) or extra
            if not b.allies[0].alive:break
        return extra

    def turn(self,b,bonus):
        live=[a for a in b.allies if a.alive]
        if not live:return False
        physical=min(live,key=lambda t:(t.guard,t.hp/t.max_hp))
        if bonus:
            b._say(f'Hermit follows up with Gigantic Fist on {physical.label}.')
            return b._hit(self.boss,physical,'Strike',25,False)
        if self.window:
            _,name,_,power=self.window
            self.beats-=1
            if self.beats==0:
                self.window=None
                self.stagger=0
                b._say(f'Hermit releases {name}!')
                return self._team_hit(b,live,'Electric',power)
            if self.beats==1:
                b._say(f'Charging Complete. {name} is next.')
            else:
                b._say('Hermit draws power from the club.')
            return False
        step=self.ordinary%4
        self.ordinary+=1
        if step==1 and self.boss.hp*2<=self.boss.max_hp:
            b._say('Hermit uses Swift Strike.')
            return self._team_hit(b,live,'Strike',28)
        if step in (1,3):
            b._say('Hermit casts Mazio.')
            return self._team_hit(b,live,'Electric',21)
        if step==2 and any(max(a.attack,a.defense,a.agility)>0 for a in live):
            for a in live:b.clear_stats(a,sign=1)
            b._say('Hermit uses Dekaja to remove the squad’s buffs.')
            return False
        target=max(live,key=lambda t:(not t.guard,not t.down,
                                      t.affinity.get('Electric','')=='weak',
                                      -t.hp/t.max_hp))
        b._say(f'Hermit casts Zio on {target.label}.')
        return b._hit(self.boss,target,'Electric',27,False)
