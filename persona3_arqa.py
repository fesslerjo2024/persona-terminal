"""Original terminal adaptations for Lower Arqa and the June full moon."""
from datetime import date

from persona3_opening import Beat
from persona3_thebel import Floor

OPENS = date(2009, 5, 10)
AKIHIKO_JOINS = date(2009, 5, 23)
RESCUE_DAY = date(2009, 6, 8)
AFTER_RESCUE = date(2009, 6, 9)
BRIDGE = date(2009, 6, 13)
FLOOR_XP = (155, 195, 170, 185, 230)
RESCUE_XP = 260
BORDER = 43

FLOORS = (
    Floor(23, 'arqa-patrol', 'LOWER ARQA', 'Forneus',
          ((4,2,7,5),(10,5,13,8),(16,2,19,4)),
          ((15,5),(16,5),(17,5),(18,5),(18,6),(18,7),(17,7),(16,7)),
          (2,7),(20,2)),
    Floor(28, 'arqa-ravens', 'RAVEN GATE', 'Omoikane',
          ((5,2,7,8),(11,2,14,5),(17,5,19,8)),
          ((11,7),(12,7),(13,7),(14,7),(15,7),(15,6),(14,6),(13,6)),
          (2,3),(20,7),'Will O’ Wisp Raven'),
    Floor(35, 'arqa-magus', 'MAGUS GATE', 'Valkyrie',
          ((3,3,7,5),(10,6,12,8),(15,2,18,5)),
          ((12,2),(12,3),(12,4),(13,4),(13,5),(14,5),(14,6),(13,6)),
          (20,2),(3,8),'Heretic Magus'),
    Floor(36, 'arqa-dice', 'DICE GATE', 'Inugami',
          ((4,6,7,8),(8,2,12,5),(15,4,18,7)),
          ((13,2),(13,3),(13,4),(13,5),(13,6),(12,6),(11,6),(11,7),(12,7),(13,7), (14,6),(14,5),(14,4),(14,3),(14,2)),
          (2,2),(20,8),'Disturbing Dice'),
    Floor(42, 'arqa-relic', 'RELIC GATE', 'Forneus',
          ((4,2,7,6),(10,4,12,8),(15,4,18,6)),
          ((15,7),(16,7),(17,7),(18,7),(19,7),(19,6),(19,5),(19,4),(19,3),(18,3)),
          (20,8),(2,2),'Clairvoyant Relic'),
)

RESCUE = Beat('rescue','06/08','THE SEARCH FOR FUUKA',(
    'Fuuka, a student at Gekkoukan, is missing. She was last seen at school. At midnight, the team takes the search into Tartarus.',
    'Makoto, Junpei and Akihiko follow her signal. Yukari and Mitsuru hold the entrance.',
), 'tartarus')

FOUND = Beat('found','06/08','A VOICE IN TARTARUS',(
    'You find Fuuka in the tower. By the time you reach the entrance, two Shadows have cut off the others.',
    'Fuuka calls out from behind you. The Shadows are changing their defenses, and she can feel where they’re open.',
), 'thebel')

SIGNAL = Beat('signal','06/09','A NEW SIGNAL',(
    'Back at the dorm, Fuuka takes a seat by the radio. With her listening, the tower sounds a little less empty.',
), 'dorm')

BRIDGE_BEAT = Beat('bridge','06/13','SEES / THEURGY TRAINING',(
    'Fighters charge Theurgy by using their specialties. Healing fills Yukari’s gauge faster. At 100%, select Theurgy in battle.',
    'Makoto needs a Fusion Spell: register Orpheus and Apsaras for Cadenza.',
    'Yukari can demonstrate in a short drill. It spends no time and gives no rewards.',
), 'relay')

# A compressed, original route. The game stages the search through a
# separated Tartarus group; these clues are written for the terminal.
SEARCH = (
    ('A faint voice carries up through a grated stairwell.',
     ('Ground-floor corridor','Grated stairs','Locked service door'),1),
    ('Someone is tapping on the other side of the damaged relay.',
     ('Damaged relay','Open archway','Downward stairs'),0),
)
