"""Upper Yabbashah checkpoints and September's story handoff.

Reload footage: https://www.youtube.com/watch?v=oLtsLnSPmTo
https://www.youtube.com/watch?v=ojDhTHCVtQI&t=1288s
https://www.youtube.com/watch?v=OuHrq1CuHJc&t=770s
"""
from datetime import date
from .persona3_thebel import Floor

OPENS=date(2009,8,8)
HERMIT_DAY=date(2009,9,5)
AFTER_HERMIT=date(2009,9,6)
BORDER=118
FLOOR_XP=(250,370,255,395,425,280)
PASSAGE='passage-upper'
PASSAGE_STAGES=('upper-monad-bronze','upper-monad-iron','upper-monad-platinum')
PASSAGE_REWARD=(540,5,320)
BLOCK='yabba_upper'

FLOORS=(
    Floor(93,'upper-yabba-patrol','UPPER YABBASHAH','Rakshasa',
          ((5,3,7,8),(11,2,13,6),(16,5,19,7)),
          ((16,2),(17,2),(18,2),(19,2),(19,3),(18,3)),(3,7),(20,2)),
    Floor(99,'upper-yabba-magus','VENOMOUS MAGUS GATE','Pale Rider',
          ((4,6,7,8),(10,2,13,4),(15,5,18,8)),
          ((14,2),(15,2),(16,2),(17,2),(17,3),(16,3)),(2,8),(20,2),'Venomous Magus'),
    Floor(103,'upper-yabba-gallery','CENTRAL GALLERY','Yamata-no-Orochi',
          ((4,2,7,5),(9,5,12,8),(16,2,18,5)),
          ((15,7),(16,7),(17,7),(18,7),(19,7),(19,8)),(3,2),(20,8)),
    Floor(105,'upper-yabba-maria','BLOODY MARIA GATE','Rakshasa',
          ((5,2,8,5),(11,4,13,8),(16,2,19,4)),
          ((17,6),(18,6),(19,6),(20,6),(20,7),(19,7)),(2,2),(20,8),'Bloody Maria'),
    Floor(112,'upper-yabba-tower','IMPOSING SKYSCRAPER GATE','Yamata-no-Orochi',
          ((5,4,8,8),(10,2,13,4),(16,5,19,8)),
          ((4,2),(5,2),(6,2),(7,2),(8,2),(8,3)),(20,8),(2,2),'Imposing Skyscraper'),
    Floor(117,'upper-yabba-gallery','MONAD LANDING','Pale Rider',
          ((5,3,8,6),(11,5,14,8),(17,2,19,5)),
          ((17,7),(18,7),(19,7),(20,7),(20,8),(19,8)),(3,8),(20,1)),
)

KOROMARU_INTRO=(
    'The shrine dog is staying in the dorm. He pads into the command room with a new Evoker fitted into his collar.',
    'Koromaru can deploy with S.E.E.S. tonight.',
)
HERMIT_BRIEF=(
    'Fuuka traced the Shadow to Club Escapade. Junpei hasn’t returned, so the rest of the team heads for the club.',
)
HERMIT_AFTER=(
    'The squad finds Junpei with Chidori. She fights for Strega and can summon a Persona, too.',
    'S.E.E.S. takes Chidori into custody at the hospital. Junpei asks if he can visit her.',
)
