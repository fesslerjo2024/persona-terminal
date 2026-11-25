"""Turn-based exploration of five representative Thebel floors."""
from dataclasses import dataclass

W,H=23,10
DIRECTIONS={'up':(0,-1),'down':(0,1),'left':(-1,0),'right':(1,0)}
POS_START=(2,8)
POS_STAIRS=(20,1)


@dataclass(frozen=True)
class Floor:
    number: int
    encounter: str
    label: str
    mask: str
    pillars: tuple[tuple[int,int,int,int],...]
    patrol: tuple[tuple[int,int],...]
    start: tuple[int,int] = POS_START
    stairs: tuple[int,int] = POS_STAIRS
    guardian: str = ''


FLOORS=(
    Floor(2,'thebel-patrol','ENTRY HALL','Pixie',
          ((5,2,7,6),(11,4,12,8),(15,2,17,5)),
          ((15,7),(16,7),(17,7),(18,7),(19,7),(19,6),(19,5),(18,5),(18,6))),
    Floor(5,'venus-eagles','ICE RAVEN GATE','Angel',
          ((4,2,6,5),(8,4,10,8),(13,3,16,6)),
          ((16,7),(17,7),(18,7),(18,6),(18,5),(18,4),(17,4),(17,5),(17,6)),(2,2),(20,8),'Ruthless Ice Ravens'),
    Floor(8,'thebel-ascent','TWISTED GALLERY','Nekomata',
          ((5,5,8,8),(10,2,13,4),(16,5,17,8)),
          ((12,7),(13,7),(14,7),(15,7),(15,6),(15,5),(14,5),(13,5),(12,5),(12,6)),(19,2),(3,8)),
    Floor(11,'dancing-hand','WHEEL GATE',"Jack O'Lantern",
          ((4,3,7,7),(10,2,12,5),(15,4,17,7)),
          ((16,3),(17,3),(18,3),(19,3),(19,4),(18,4),(18,5),(18,6),(18,7)),(11,8),(20,4),'Barbaric Beast Wheel'),
    Floor(17,'rampage-drive','SWIFT AXLE GATE','Apsaras',
          ((4,6,7,8),(9,2,11,5),(14,5,16,8)),
          ((16,3),(17,3),(18,3),(19,3),(20,3),(20,4),(19,4),(18,4),(17,4),(17,3)),(2,2),(19,5),'Swift Axle'),
)


def _blocks(floor):
    cells={(i,j) for i in range(W) for j in range(H) if i in (0,W-1) or j in (0,H-1)}
    for xa,ya,xb,yb in floor.pillars:
        cells.update((x,y) for x in range(xa,xb+1) for y in range(ya,yb+1))
    return frozenset(cells)


class Hall:
    def __init__(self,index,*,replay=False,patrol_offset=0,floors=FLOORS,block="thebel"):
        self.index=index;self.floor=floors[index];self.replay=replay;self.block=block
        self.patrol_offset=patrol_offset
        self.blocked=_blocks(self.floor)
        self.pos=self.floor.start;self.steps=0;self.alert=False;self.defeated=False
        self.seen=set()
        self._reveal()

    @property
    def encounter(self):
        if not self.replay:return self.floor.encounter
        from persona3_late_registry import REPLAY
        if self.block in REPLAY:return REPLAY[self.block] if self.floor.guardian else self.floor.encounter
        if self.block=='arqa':return 'arqa-patrol'
        if self.block=='upper':return 'upper-patrol' if self.floor.guardian else self.floor.encounter
        if self.block=='yabba_upper':return 'upper-yabba-patrol' if self.floor.guardian else self.floor.encounter
        if self.block=='yabba':return 'yabba-patrol' if self.floor.guardian else self.floor.encounter
        return 'thebel-ascent' if self.floor.number>=8 else 'thebel-patrol'

    @property
    def stairs_open(self):
        return self.replay or self.defeated

    @property
    def shadow(self):
        return self.floor.patrol[(self.steps//2+self.patrol_offset)%len(self.floor.patrol)]

    def _reveal(self):
        x,y=self.pos
        self.seen.update((i,j) for i in range(W) for j in range(H)
                         if abs(i-x)+abs(j-y)<=5)

    def step(self,direction):
        """Return None, 'battle', 'stairs'; walls do not spend a turn."""
        dx,dy=DIRECTIONS[direction];dest=self.pos[0]+dx,self.pos[1]+dy
        if dest in self.blocked:return None
        old_shadow=self.shadow
        self.pos=dest;self.steps+=1;self._reveal()
        if dest==self.floor.stairs and self.stairs_open:return 'stairs'
        if not self.defeated:
            sx,sy=self.shadow
            self.alert=abs(sx-dest[0])+abs(sy-dest[1])<=2
            if dest in (old_shadow,self.shadow,self.floor.stairs):return 'battle'
        return None

    def glyph(self,x,y):
        p=(x,y)
        if p==self.pos:return '@'
        if p not in self.seen:return ' '
        if p==self.floor.stairs:return '⇧' if self.stairs_open else '⊗'
        if not self.defeated and p==self.shadow:return '◆'
        if p in self.blocked:return '▒'
        return '·'
