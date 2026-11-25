"""Optional durable resources between the last three summit fights."""
from dataclasses import dataclass, replace

from .persona3_summit import SUMMIT_LEVEL, SUMMIT_SUPPLIES


@dataclass(frozen=True)
class SummitCarry:
    roster: tuple[str,...]
    resources: tuple[tuple[str,int,int],...] | None
    supplies: tuple[tuple[str,int],...]
    charge: tuple[tuple[str,int],...]

    @classmethod
    def from_battle(cls,battle):
        return cls(tuple(u.name for u in battle.allies),
                   tuple((name,hp,sp) for name,(hp,sp) in battle.resources.items()),
                   tuple(battle.inventory.items()),tuple(battle.charge.items()))

    def restocked(self):
        pack=dict(self.supplies)
        for name,n in SUMMIT_SUPPLIES.items():
            pack[name]=max(pack.get(name,0),n)
        return replace(self,resources=None,supplies=tuple(pack.items()))

    @property
    def vitals(self):
        return {name:(hp,sp) for name,hp,sp in self.resources} if self.resources is not None else None


def decode(raw,state):
    from .persona3_combat import LEAD_ID, PARTY, party_caps
    invalid='Invalid summit checkpoint.'
    if (state.phase not in ('summit-takaya','summit-nyx') or not isinstance(raw,dict) or
            set(raw)!={'roster','resources','supplies','charge'}):
        raise ValueError(invalid)
    names=set(PARTY)-{'Shinjiro'}
    roster=raw['roster']
    if (not isinstance(roster,list) or not 1<=len(roster)<=4 or roster[0]!=LEAD_ID or
            any(not isinstance(name,str) or name not in names for name in roster) or
            len(set(roster))!=len(roster)):
        raise ValueError(invalid)

    def rows(key,size,allowed,cap,maximum):
        value=raw[key]
        if not isinstance(value,list) or len(value)>maximum:raise ValueError(invalid)
        found=set()
        for row in value:
            if (not isinstance(row,list) or len(row)!=size or not isinstance(row[0],str) or
                    row[0] not in allowed or row[0] in found or
                    any(type(n) is not int or not 0<=n<=limit for n,limit in zip(row[1:],cap(row[0])))):
                raise ValueError(invalid)
            found.add(row[0])
        return tuple(tuple(row) for row in value)

    resources=None
    if raw['resources'] is not None:
        caps=party_caps(max(SUMMIT_LEVEL,state.level),tuple(names))
        resources=rows('resources',3,names,caps.__getitem__,4)
        if not any(name==LEAD_ID and hp>0 for name,hp,_ in resources):raise ValueError(invalid)
    supplies=rows('supplies',2,SUMMIT_SUPPLIES,lambda name:(SUMMIT_SUPPLIES[name]+2,),len(SUMMIT_SUPPLIES))
    charge=rows('charge',2,names|{'Fuuka'},lambda name:(100,),5)
    return SummitCarry(tuple(roster),resources,supplies,charge)
