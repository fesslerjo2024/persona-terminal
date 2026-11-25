"""Lower Yabbashah, Yakushima and the first Monad route."""
from datetime import date
from .persona3_thebel import Floor

OPENS=date(2009,7,18)
YAKUSHIMA=date(2009,7,20)
BEACH=date(2009,7,21)
AIGIS=date(2009,7,24)
AUGUST_MOON=date(2009,8,6)
AFTER_AUGUST=date(2009,8,7)
BORDER=92
FLOOR_XP=(195,280,205,305,330,360)
AUGUST_XP=400
DOOR='door'
PASSAGE='passage'
MONAD_STAGES={
    DOOR:('monad-door',),
    PASSAGE:('monad-passage-maya','monad-passage-guard'),
}
MONAD_FLOOR={80:DOOR,91:PASSAGE}
MONAD_REWARD={DOOR:(250,3,140),PASSAGE:(420,5,260)}
CLOCK_COST=7

FLOORS=(
    Floor(70,'yabba-patrol','LOWER YABBASHAH','Rakshasa',
          ((3,2,7,3),(8,5,10,8),(13,3,16,6),(18,6,20,7)),
          ((14,7),(15,7),(16,7),(17,7),(17,8),(16,8),(15,8),(14,8)),(2,6),(21,3)),
    Floor(77,'yabba-77','SAND GATE','Yamata-no-Orochi',
          ((4,3,6,8),(10,2,12,6),(14,5,17,8)),
          ((15,2),(16,2),(17,2),(18,2),(18,3),(17,3),(16,3),(15,3)),(19,8),(3,2),'Ochlocratic Sands'),
    Floor(80,'yabba-patrol','MONAD LANDING','Pale Rider',
          ((4,5,7,8),(10,2,13,5),(16,4,19,6)),
          ((14,3),(15,3),(16,3),(17,3),(18,3),(19,3),(20,3),(20,4)),(2,7),(20,2)),
    Floor(82,'yabba-82','ARCANIST GATE','Pale Rider',
          ((3,2,7,4),(8,6,12,8),(15,3,17,5)),
          ((17,6),(17,7),(18,7),(19,7),(20,7),(20,6),(19,6),(18,6)),(20,2),(2,7),'Arcanist Decapitator'),
    Floor(90,'yabba-90','CONVICT GATE','Rakshasa',
          ((4,4,8,7),(11,2,13,5),(15,5,18,8)),
          ((10,7),(11,7),(12,7),(13,7),(14,7),(14,6),(13,6),(12,6)),(20,8),(2,3),'Deviant Convict'),
    Floor(91,'yabba-91','PARTNERS’ GATE','Yamata-no-Orochi',
          ((5,3,7,8),(10,4,13,7),(17,2,19,5)),
          ((16,6),(16,7),(17,7),(18,7),(19,7),(20,7),(21,7),(21,6)),(2,2),(20,8),'Controlling and Dependent Partners'),
)

# Original, compressed dialogue. Order and dates follow Reload.
TRIP=(
    ('THE KIRIJO VILLA','Yakushima',('Yukari and the others came to ask about the Kirijo Group. The answer takes them back to an accident, ten years ago.',)),
    ('AIGIS','Yakushima beach',('At the shore, a stranger stops when she sees Makoto. Her name is Aigis. She asks if she can stay by his side.',)),
    ('RETURN TO IWATODAI','Yakushima',('Mitsuru explains that the Kirijo Group built Aigis to fight Shadows. Aigis comes back with S.E.E.S. and can deploy on July 24.',)),
)

from .persona3_opening import Beat

AFTER_BEAT=Beat('august-after','08/07','AFTER THE UNDERGROUND PASSAGE',(
    'The team makes it back to the dorm. The fighting has stopped for tonight.',
    'Tartarus practice remains available.',
), 'dorm')


def shore(part,w,h):
    """The villa, dock meeting, and departure keep the same live art band."""
    from .persona3_scenic_detail import shoreline
    return shoreline(part,w,h)
