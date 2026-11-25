"""Recovery choices for a Tartarus expedition; all costs use combat definitions."""
from dataclasses import dataclass

from . import persona3_combat as combat


KIT_HP = 42


@dataclass(frozen=True)
class Aid:
    name: str
    kind: str
    power: int
    count: int = 0
    caster: str = ''
    cost: int = 0
    team: bool = False

    @property
    def label(self):
        return f'{combat.display_name(self.caster)} • {self.name}' if self.caster else self.name

    @property
    def detail(self):
        power={'kit':f'+{self.power} HP to standing allies',
               'heal':f'+{self.power} HP'+(' to standing allies' if self.team else ''),
               'sp':f'+{self.power} SP',
               'revive':f'Revive with up to {self.power} HP'}[self.kind]
        return (f'{self.cost} SP  ·  ' if self.caster else f'×{self.count}  ·  ')+power

    def blocked(self,resources,caps):
        if self.caster:
            hp,sp=resources[self.caster]
            if not hp:return 'Caster is knocked out.'
            if sp<self.cost:return f'Needs {self.cost} SP.'
        elif not self.count:return 'None left.'
        if not any(self.eligible(name,resources,caps) for name in resources):
            return {'kit':'No injured standing ally.',
                    'heal':'No injured standing ally.',
                    'sp':'No standing ally needs SP.',
                    'revive':'No ally is knocked out.'}[self.kind]
        return ''

    def eligible(self,name,resources,caps):
        hp,sp=resources[name]
        max_hp,max_sp=caps[name]
        return {'kit':0<hp<max_hp,'heal':0<hp<max_hp,
                'sp':bool(hp and sp<max_sp),'revive':not hp}[self.kind]

    def apply(self,resources,caps,target=None):
        if self.blocked(resources,caps):
            raise ValueError('Recovery option is no longer available.')
        updated=dict(resources)
        team=self.kind=='kit' or self.team
        names=tuple(resources) if team else (target,)
        if not team and (target not in resources or not self.eligible(target,resources,caps)):
            raise ValueError('Recovery target is no longer valid.')
        if self.caster:
            hp,sp=updated[self.caster]
            updated[self.caster]=(hp,sp-self.cost)
        for n in names:
            if not self.eligible(n,resources,caps):continue
            hp,sp=updated[n]
            max_hp,max_sp=caps[n]
            updated[n]=(hp,min(max_sp,sp+self.power)) if self.kind=='sp' else (min(max_hp,hp+self.power),sp)
        return updated


def options(resources,inventory,kits,state):
    """Expose exactly the known healing skills and the expedition bag."""
    aids=[Aid('Field Kit','kit',KIT_HP,kits)]
    aids.extend(Aid(name,kind,power,inventory.get(name,0)) for name,(kind,power) in combat.ITEMS.items()
                if kind in ('heal','sp','revive'))
    for caster in resources:
        known=(combat.persona_skills(state.equipped,state.level,state.stock[state.equipped])
               if caster==combat.LEAD_ID else combat.party_skills(caster,state.day))
        for move in known:
            kind,_,power,cost,scope,_=combat.SKILLS[move]
            if kind=='heal':aids.append(Aid(move,kind,power,caster=caster,cost=cost,team=scope=='team'))
    return tuple(aids)
