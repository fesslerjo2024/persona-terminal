"""Interactive May monorail and July hotel connective scenes.

Recorded Reload reference: May train cars / Junpei:
https://www.youtube.com/watch?v=GFGGWFMXmRQ
May Priestess / brake, 21:53 and 28:25:
https://www.youtube.com/watch?v=WHXuCHsByK4
July post-Hierophant search, reunion and Lovers:
https://www.youtube.com/watch?v=PKBHa3rKK9I&t=987s

Maps compress the original routes. State is transient; the usual bosses alone
commit operation progress, and July keeps the party and resources provided by
the controller. No clock runs during walking or while observing mirrors.
"""
from dataclasses import dataclass
import curses as C
from time import monotonic

from persona_terminal.shared.terminal_constants import ENTER, ESC, CYAN, DIM, GOLD, WHITE
from ..shared.reel_palette import IDS
from .persona3_mirror_art import render as mirror_art, observation
from .persona3_operation_art import train, hotel
from .persona3_upper import MIRRORS, Mirror

OPERATION_ROUTE_PAGES=frozenset(('train-cars','train-brake','hotel-hall','hotel-mirror'))
_MOVES={C.KEY_LEFT:(-1,0),C.KEY_RIGHT:(1,0),C.KEY_UP:(0,-1),C.KEY_DOWN:(0,1),
        'a':(-1,0),'d':(1,0),'w':(0,-1),'s':(0,1)}
_HEADERS=('REAR CAR','MIDDLE CAR','LEAD CAR')
# Seat/obstruction positions, relative to the player's grid (9 by 3).
_BLOCKS=(
    frozenset(((1,0),(2,0),(4,1),(6,2),(7,2))),
    frozenset(((1,2),(2,2),(3,1),(5,0),(6,0))),
    frozenset(((1,0),(4,2),(5,2),(6,0))),
)
_START=(0,1)
_HATCH=(8,1)
_JUNPEI=(3,1)
_TEAL=IDS['teal']
_GOAL_ROOMS=frozenset(room.room for room in MIRRORS)
_ROOMS={room.room:room for room in (*MIRRORS,
        Mirror('202',(('Mirror above the washbasin',True),)),
        Mirror('204',(('Mirror by the curtains',True),)),
        Mirror('302',(('Mirror behind the door',True),)),
        Mirror('306',(('Mirror near the wardrobe',True),)))}
_DECOY_ART={'202':('205',0),'204':('205',1),'302':('304',0),'306':('304',2)}
_FLOORS=((('202','Room 202'),('204','Room 204'),('205','Room 205'),('up','Stairs to 3F')),
         (('302','Room 302'),('304','Room 304'),('306','Room 306'),('suite','Return to the suite'),('down','Stairs to 2F')))


@dataclass
class TrainRoute:
    car: int = 0
    position: tuple[int,int] = _START
    reunited: bool = False

    def move(self,k):
        dx,dy=_MOVES[k]
        x,y=self.position
        target=x+dx,y+dy
        if (not 0<=target[0]<=8 or not 0<=target[1]<3 or target in _BLOCKS[self.car]
                or self.car==2 and not self.reunited and target==_JUNPEI):
            return False
        self.position=target
        return True

    @property
    def beside_junpei(self):
        x,y=self.position
        return (self.car==2 and not self.reunited and
                abs(x-_JUNPEI[0])+abs(y-_JUNPEI[1])==1)


class OperationRoute:
    def draw_operation_route(self):
        {'train-cars':self._draw_train_cars,'train-brake':self._draw_train_brake,
         'hotel-hall':self._draw_hotel_hallway,'hotel-mirror':self._draw_hotel_pane}[self.page]()

    def operation_route_key(self,k):
        {'train-cars':self._train_cars_key,'train-brake':self._train_brake_key,
         'hotel-hall':self._hotel_hallway_key,'hotel-mirror':self._hotel_pane_key}[self.page](k)

    def start_train_route(self):
        self.train_route=TrainRoute()
        self.train_started=monotonic()
        self.go('train-cars')

    def _draw_train_cars(self):
        r=self.train_route
        if r.beside_junpei:interact='  ENTER REGROUP'
        elif r.position==_HATCH:interact='  ENTER HATCH'
        else:interact=''
        self.frame(f'MONORAIL / {_HEADERS[r.car]}','ARROWS MOVE'+interact+'  ESC BRIEF')
        self.draw_scene_rows(train(self.w-5,7,r.car,monotonic()-self.train_started),top=5,left=2)
        width=29
        left=max(3,(self.w-width)//2)
        self.put(13,left,'┌'+'─'*(width-2)+'┐',DIM)
        for y in range(3):
            self.put(14+y,left,'│',DIM)
            self.put(14+y,left+width-1,'│',DIM)
            for x in range(9):
                cell=x,y
                if cell==r.position:glyph,ink='@',CYAN
                elif cell in _BLOCKS[r.car]:glyph,ink='█',DIM
                elif cell==_HATCH:glyph,ink='>',_TEAL
                elif r.car==2 and not r.reunited and cell==_JUNPEI:glyph,ink='J',GOLD
                else:glyph,ink='·',DIM
                self.put(14+y,left+2+3*x,glyph,ink,True)
        self.put(17,left,'└'+'─'*(width-2)+'┘',DIM)
        if r.car==0:body='Junpei breaks into a run. Follow him through the hatch.'
        elif r.car==1:body='Yukari: He’s still ahead of us. Try the open aisle.'
        elif not r.reunited:body='Junpei is by the seats. Step beside him and regroup.'
        else:body='The train lurches. The last hatch leads to the cab.'
        self.lines(19,4,body,count=2,color=_TEAL)

    def _train_cars_key(self,k):
        r=self.train_route
        if k==ESC:self.go('operation');return
        if k in _MOVES:
            self.notice=''
            r.move(k)
            return
        if k not in ENTER:return
        if r.beside_junpei:
            r.reunited=True
            return
        if r.position!=_HATCH:return
        if r.car<2:
            r.car+=1
            r.position=_START
        elif not r.reunited:
            self.notice='Regroup with Junpei before entering the cab.'
        else:
            self.open_battle('priestess')

    def start_train_brake(self,*,stopped=False):
        self.train_stopped=monotonic() if stopped else None
        self.train_started=monotonic()
        self.go('train-brake')

    def _draw_train_brake(self):
        stopped=self.train_stopped is not None
        t=0. if stopped else monotonic()-self.train_started
        self.frame('MONORAIL / DRIVER’S CAB','ENTER CONTINUE' if stopped else 'ENTER PULL BRAKE',
                   status='05/09  SAT')
        self.draw_scene_rows(train(self.w-5,12,3,t,braking=True,stopped=stopped),top=5,left=2)
        self.lines(18,4,
                   'The brakes catch. For a moment, nobody moves.' if stopped else
                   'The Shadow is gone, but the train is still moving. Reach for the brake.',
                   count=2,color=_TEAL)

    def _train_brake_key(self,k):
        if k==ESC:self.exit=True;return
        if k not in ENTER:return
        if self.record.aftermath in ('monorail-brake','monorail-stopped') and not self.write(self.store.advance_boss_aftermath):return
        if self.train_stopped is None:self.train_stopped=monotonic()
        else:self.beat('finale')

    def start_hotel_route(self):
        self.hotel_floor=0
        self.hotel_hall_index=0
        self.hotel_room=None
        self.hotel_cleared=set()
        self.mirror_index=0
        self.mirror_observation=False
        self.go('hotel-hall')

    @property
    def _hotel_route_choices(self):
        return _FLOORS[self.hotel_floor]

    def _draw_hotel_hallway(self):
        rows=self._hotel_route_choices
        self.frame(f'CHAMPS DE FLEUR / {self.hotel_floor+2}F HALL',
                   '↑↓ DOORS  ENTER OPEN  H HEAL  ESC LEAVE')
        self.draw_scene_rows(hotel(self.w-5,8,self.hotel_floor,3,self.i),top=5,left=2)
        self.choices(tuple(label+(' / CLEARED' if key in self.hotel_cleared else '')
                           for key,label in rows),13,4,step=1)
        if self.hotel_cleared==_GOAL_ROOMS:
            text='The far suite is open. The second Shadow is waiting.'
        elif not self.hotel_cleared:
            text='Yukari: Look for glass that shows the room but leaves us out.'
        else:
            text='One broken mirror. There’s another on the other floor.'
        self.lines(18,4,text,count=2,color=_TEAL)

    def _hotel_hallway_key(self,k):
        if k==ESC:self.overlay='hotel-retreat';return
        rows=self._hotel_route_choices
        previous=self.i
        pick=self.choose(k,len(rows))
        if previous!=self.i:self.notice=''
        if pick is None:return
        key,_=rows[pick]
        if key in ('up','down'):
            self.hotel_floor=1 if key=='up' else 0
            self.go('hotel-hall')
        elif key=='suite':
            if self.hotel_cleared==_GOAL_ROOMS:self.open_battle('hotel-lovers')
            else:self.notice='The suite still won’t open. Check both floors.'
        elif key in self.hotel_cleared:self.notice='Only broken glass remains.'
        else:
            self.hotel_hall_index=self.i
            self.hotel_room=key
            self.go('hotel-mirror')

    def _restore_hotel_hall(self):
        self.go('hotel-hall')
        self.i=self.hotel_hall_index

    def _draw_hotel_pane(self):
        room=_ROOMS[self.hotel_room]
        self.frame(f'CHAMPS DE FLEUR / ROOM {room.room}',
                   '↑↓ MIRRORS  ENTER BREAK  I DESCRIBE  ESC HALL' if len(room.mirrors)>1 else
                   'ENTER BREAK  I DESCRIBE  ESC HALL')
        reflection=room.mirrors[self.i][1]
        art_room,art_option=_DECOY_ART.get(room.room,(room.room,self.i))
        self.draw_scene_rows(mirror_art(reflection,self.w-5,8,option=art_option,room=art_room,
                                        members=len(self.hotel_party)),top=5,left=2)
        self.choices(tuple(label for label,_ in room.mirrors),14,4,54,1)
        if self.mirror_observation:
            self.lines(18,4,observation(reflection),count=2,color=_TEAL)

    def _hotel_pane_key(self,k):
        if k==ESC:self._restore_hotel_hall();return
        if k in ('i','I','\t'):
            self.mirror_observation=not self.mirror_observation
            return
        room=_ROOMS[self.hotel_room]
        previous=self.i
        pick=self.choose(k,len(room.mirrors))
        if previous!=self.i:self.notice=''
        if pick is None:return
        if room.mirrors[pick][1]:
            self.notice='Your reflection looks back. The glass stays intact.'
            return
        self.hotel_cleared.add(room.room)
        self.mirror_index=len(self.hotel_cleared)
        self._restore_hotel_hall()
        self.notice='The glass breaks. A lock clicks somewhere in the hall.'
