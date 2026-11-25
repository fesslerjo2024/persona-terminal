"""A durable post-battle field checkpoint, including an unclaimed card."""
from dataclasses import dataclass, fields
from .persona3_thebel import FLOORS,H,W,Hall

@dataclass(frozen=True)
class FieldCheckpoint:
    block: str
    index: int
    replay: bool
    offset: int
    steps: int
    position: tuple[int,int]
    seen: tuple[tuple[int,int],...]
    resources: tuple[tuple[str,tuple[int,int]],...]
    items: tuple[tuple[str,int],...]
    charge: tuple[tuple[str,int],...]
    temperance: int
    lounge: bool
    guided: bool
    pending: bool

    @classmethod
    def capture(cls,hall,resources,items,charge,temperance,lounge,guided,pending):
        return cls(hall.block,hall.index,hall.replay,hall.patrol_offset,hall.steps,hall.pos,
                   tuple(sorted(hall.seen|{hall.pos})),tuple(resources.items()),tuple(items.items()),
                   tuple(charge.items()),temperance,lounge,guided,pending)

    def restore(self,floors):
        hall=Hall(self.index,replay=self.replay,patrol_offset=self.offset,floors=floors,block=self.block)
        hall.pos=self.position;hall.steps=self.steps;hall.seen=set(self.seen);hall.defeated=True
        return hall


def decode(raw,state):
    from .persona3_combat import ITEMS,LEAD_ID,PARTY,party_caps
    from . import persona3_arqa as arqa
    from . import persona3_upper as upper
    from . import persona3_yabbashah as yabba
    from . import persona3_yabbashah_upper as high
    from . import persona3_late_registry as registry
    date_floor={'thebel':(None,FLOORS),'arqa':(arqa.OPENS,arqa.FLOORS),'upper':(upper.OPENS,upper.FLOORS),
                'yabba':(yabba.OPENS,yabba.FLOORS),high.BLOCK:(high.OPENS,high.FLOORS),
                **{n:(d,registry.BLOCKS[n][0]) for n,d in registry.OPENS.items()}}
    if not isinstance(raw,dict) or set(raw)!={f.name for f in fields(FieldCheckpoint)}:
        raise ValueError('Incomplete field checkpoint.')
    block=raw['block']
    if not isinstance(block,str) or block not in date_floor or state.phase not in ('tartarus','calendar'):
        raise ValueError('Invalid field checkpoint.')
    date,floors=date_floor[block]
    depth=getattr(state,'depth' if block=='thebel' else block)
    index=raw['index']
    if (date is not None and state.day<date) or type(index) is not int or not 0<=index<min(depth,len(floors)):
        raise ValueError('Invalid checkpoint floor.')
    bounded=lambda n,limit: type(n) is int and 0<=n<=limit
    point=lambda p: isinstance(p,list) and len(p)==2 and bounded(p[0],W-1) and bounded(p[1],H-1)
    if (not all(type(raw[k]) is bool for k in ('replay','lounge','guided','pending'))
            or not bounded(raw['steps'],10**9) or not bounded(raw['offset'],len(floors[index].patrol)-1)
            or not bounded(raw['temperance'],2) or not point(raw['position'])
            or not isinstance(raw['seen'],list) or len(raw['seen'])>W*H
            or not all(point(p) for p in raw['seen']) or raw['position'] not in raw['seen']):
        raise ValueError('Invalid checkpoint map.')
    hall=Hall(index,floors=floors)
    if tuple(raw['position']) in hall.blocked:raise ValueError('Invalid checkpoint position.')
    for key in ('resources','items','charge'):
        rows=raw[key]
        if (not isinstance(rows,list) or len(rows)>32 or
                any(not isinstance(row,list) or len(row)!=2 or not isinstance(row[0],str) for row in rows)
                or len({row[0] for row in rows})!=len(rows)):
            raise ValueError('Invalid checkpoint supplies.')
    names=tuple(n for n,_ in raw['resources'])
    if not names or names[0]!=LEAD_ID or len(names)>4 or any(n not in PARTY for n in names):
        raise ValueError('Invalid checkpoint squad.')
    caps=party_caps(state.level,party=names)
    if any(not isinstance(pair,list) or len(pair)!=2 or not all(bounded(v,m) for v,m in zip(pair,caps[n]))
           for n,pair in raw['resources']):
        raise ValueError('Invalid checkpoint resources.')
    if any(n not in ITEMS or not bounded(v,99) for n,v in raw['items']):
        raise ValueError('Invalid checkpoint item.')
    if any(n not in (*names,'Fuuka') or not bounded(v,100) for n,v in raw['charge']):
        raise ValueError('Invalid checkpoint Theurgy.')
    return FieldCheckpoint(**{**raw,'position':tuple(raw['position']),'seen':tuple(map(tuple,raw['seen'])),
                              'resources':tuple((n,tuple(pair)) for n,pair in raw['resources']),
                              'items':tuple(map(tuple,raw['items'])),'charge':tuple(map(tuple,raw['charge']))})
