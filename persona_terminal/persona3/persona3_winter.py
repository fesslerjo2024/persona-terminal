"""December–January Tartarus checkpoints; the January 31 summit is separate.

Reload player-recorded route references:
https://www.youtube.com/watch?v=l0nvWyi6hGQ
https://www.youtube.com/watch?v=HxeWdq8FbP0&t=1111s
https://www.youtube.com/watch?v=zEfiTJj0wAs&t=376s
"""
from datetime import date

from .persona3_thebel import Floor

NAMES={'harabah_upper':'Upper Harabah','adamah':'Adamah'}
OPENS={'harabah_upper':date(2009,12,10),'adamah':date(2010,1,1)}
BORDERS={'harabah_upper':226,'adamah':256}
REPLAY_ENCOUNTERS={'harabah_upper':'winter-harabah-patrol','adamah':'winter-adamah-patrol'}
HARABAH_PASSAGE='passage-harabah-upper'
# Same key/stages/reward shape as the shorter Yabbashah passage.
PASSAGES={HARABAH_PASSAGE:('harabah_upper',225,('winter-monad-book','winter-monad-hands'),(780,5,520))}

_HALLS=(
    (((5,3,7,7),(11,2,13,5),(16,5,18,8)),
     ((15,2),(16,2),(17,2),(18,2),(19,2),(19,3),(18,3)),(2,8),(20,2)),
    (((4,4,7,7),(10,2,12,5),(15,5,18,8)),
     ((4,2),(5,2),(6,2),(7,2),(8,2),(8,3),(7,3)),(20,8),(2,2)),
    (((4,2,7,5),(10,5,13,8),(16,2,18,5)),
     ((15,7),(16,7),(17,7),(18,7),(19,7),(19,8),(18,8)),(2,2),(20,8)),
    (((5,4,8,7),(11,2,13,5),(16,4,19,6)),
     ((16,7),(17,7),(18,7),(19,7),(20,7),(20,8),(19,8)),(2,8),(20,8)),
)


def _floor(number, encounter, label, mask, geometry=0, guardian=''):
    pillars, patrol, start, stairs=_HALLS[geometry]
    return Floor(number, encounter, label, mask, pillars, patrol, start, stairs, guardian)


HARABAH_FLOORS=(
    _floor(199,'winter-harabah-patrol','EMBER LANDING','Kikuri-Hime'),
    _floor(203,'winter-icebreaker','ICEBREAKER LION GATE','Kikuri-Hime',1,'Icebreaker Lion'),
    _floor(209,'winter-harabah-mid','FRACTURED GALLERY','Seiryu',2),
    _floor(212,'winter-siblings','THREE SIBLINGS GATE','Seiryu',3,'Deadly Eldest Sibling'),
    _floor(218,'winter-scornful','SCORNFUL DICE GATE','Pazuzu',1,'Scornful Dice'),
    _floor(221,'winter-harabah-high','UPPER EMBER GALLERY','Pazuzu',2),
    _floor(225,'winter-nulla','MINOTAUR NULLA GATE','Kikuri-Hime',0,'Minotaur Nulla'),
)
HARABAH_XP=(390,610,400,650,670,420,700)

ADAMAH_FLOORS=(
    _floor(227,'winter-adamah-patrol','ADAMAH LANDING','Koumokuten',3),
    _floor(230,'winter-obsessive','OBSESSIVE SAND GATE','Koumokuten',2,'Obsessive Sand'),
    _floor(233,'winter-adamah-mid','PRISM GALLERY','Raphael',1),
    _floor(236,'winter-comeback','COMEBACK CASTLE GATE','Raphael',0,'Comeback Castle'),
    _floor(241,'winter-overseers','OVERSEER GATE','Seiryu',2,'Overseer of Creation'),
    _floor(246,'winter-appropriating','APPROPRIATING NOBLE GATE','Suzaku',1,'Appropriating Noble'),
    _floor(247,'winter-high-judge','HIGH JUDGE GATE','Suzaku',3,'High Judge of Hell'),
    _floor(250,'winter-adamah-high','UPPER PRISM GALLERY','Koumokuten',0),
    _floor(253,'winter-cultist','CULTIST OF DEATH GATE','Pazuzu',1,'Cultist of Death'),
    _floor(254,'winter-hedonistic','HEDONISTIC SINNER GATE','Raphael',2,'Hedonistic Sinner'),
    _floor(255,'winter-genocidal','GENOCIDAL MERCENARY GATE','Suzaku',3,'Genocidal Mercenary'),
)
ADAMAH_XP=(480,740,490,770,790,800,820,510,850,880,930)

BLOCKS={'harabah_upper':(HARABAH_FLOORS, BORDERS['harabah_upper'], HARABAH_XP),
        'adamah':(ADAMAH_FLOORS, BORDERS['adamah'], ADAMAH_XP)}
