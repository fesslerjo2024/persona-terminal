"""Dated Upper Arqa floors, rescue records and original July operation scenes."""
from dataclasses import dataclass
from datetime import date

from .persona3_opening import Beat
from .persona3_thebel import Floor

OPENS=date(2009,6,13)
HOTEL_DAY=date(2009,7,7)
AFTER_HOTEL=date(2009,7,8)
RESCUE_DEADLINE=date(2009,7,6)
BORDER=69
FLOOR_XP=(170,230,175,240,175,265,180)
HOTEL_XP=330

FLOORS=(
    Floor(44,'upper-patrol','UPPER ARQA','Take-Minakata',
          ((5,2,7,5),(11,5,13,8),(16,2,18,4)),
          ((16,6),(17,6),(18,6),(19,6),(19,7),(18,7),(17,7),(16,7)),(2,8),(20,2)),
    Floor(47,'upper-servant','SERVANT TOWER GATE','Naga',
          ((5,4,7,8),(10,2,13,5),(16,4,18,7)),
          ((15,2),(16,2),(17,2),(18,2),(19,2),(19,3),(18,3),(17,3),(16,3)),(20,8),(2,2),'Servant Tower'),
    Floor(50,'upper-patrol-50','RELAY GALLERY','Sati',
          ((6,3,8,8),(12,2,14,4),(16,5,19,7)),
          ((16,2),(17,2),(18,2),(19,2),(20,2),(20,3),(19,3),(18,3),(17,3)),(2,8),(20,1)),
    Floor(54,'upper-lady','LADY’S GATE','Principality',
          ((4,4,7,7),(10,2,12,6),(16,4,18,7)),
          ((14,3),(15,3),(16,3),(17,3),(18,3),(19,3),(19,4),(19,5),(19,6)),(20,2),(2,8),'Lascivious Lady'),
    Floor(56,'upper-patrol-56','SOUTH LANDING','Take-Minakata',
          ((5,2,7,6),(11,5,14,8),(16,2,18,5)),
          ((16,6),(17,6),(18,6),(19,6),(19,7),(18,7),(17,7),(16,7)),(20,8),(2,1)),
    Floor(60,'upper-cavalry','CAVALRY GATE','Naga',
          ((4,4,7,8),(10,2,12,5),(15,4,19,6)),
          ((14,6),(14,7),(15,7),(16,7),(17,7),(18,7),(19,7),(20,7)),(3,2),(20,8),'Fleetfooted Cavalry'),
    Floor(64,'upper-patrol-56','QUIET LANDING','Principality',
          ((5,2,7,6),(10,5,14,8),(16,2,18,5)),
          ((16,7),(17,7),(18,7),(19,7),(20,7),(20,6),(19,6),(18,6),(17,6)),(2,8),(20,2)),
)

@dataclass(frozen=True)
class Rescue:
    id: str
    name: str
    day: date
    floor: int
    pos: tuple[int,int]
    yen: int
    kits: int


RESCUES=(
    Rescue('ayako','Ayako Yoshimoto',date(2009,6,18),50,(4,5),120,1),
    Rescue('kenjiro','Kenjiro Tsutsumi',date(2009,6,26),56,(15,8),170,0),
    Rescue('yoshimi','Yoshimi Miyama',date(2009,6,26),64,(4,4),150,1),
)
BY_RESCUE={entry.id:entry for entry in RESCUES}
BY_FLOOR={entry.floor:entry for entry in RESCUES}
REPORT_DAYS=frozenset(entry.day for entry in RESCUES)

HOTEL=Beat('hotel','07/07','CHAMPS DE FLEUR',(
    'Fuuka senses two Shadows inside the hotel. Yukari is assigned to keep you healed. Choose up to two more allies before you go in.',
), 'arrival')
AFTER=Beat('hotel-after','07/08','AFTER THE HOTEL',(
    'Both readings are gone. Outside, the street is quiet enough to hear Yukari let out the breath she was holding.',
    'The July operation is complete. Tartarus practice remains open.',
), 'exit')

@dataclass(frozen=True)
class Mirror:
    room: str
    mirrors: tuple[tuple[str,bool],...]


MIRRORS=(
    Mirror('205',(('Mirror above the sink',True),('Mirror by the curtains',False),('Mirror by the door',True))),
    Mirror('304',(('Mirror near the doorway',False),('Mirror beside the bed',True),('Mirror near the wardrobe',True))),
)
