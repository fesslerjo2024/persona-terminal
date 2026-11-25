"""Small, keyboard-playable Royal story scenes, separate from battles and saves.

The campaign host owns timing, unlocks and the persistence of optional clues.
No scene awards a combat advantage, changes which route opens, or writes a save.
"""
import curses as C
from dataclasses import dataclass, field

from .battle_ui import CYAN, DIM, WHITE

PYRAMID_MOTIF = 'pyramid-motif'
CLUES = frozenset({PYRAMID_MOTIF})
PYRAMID_FRAGMENTS = (
    ('THE KITCHEN', 'A child holds a receiver. A tiny ink square marks her sleeve: '
                    'two strokes, and a gap where the line should close.'),
    ('THE STATEMENT', 'An adult hand lays a statement on the table. The very same '
                      'broken square is painted beside the first line.'),
)
CASINO_SIGNAL = 'EXIT lamp: two flashes, then darkness.'
CASINO_WINDOW = 'The stairwell runs into another patrol. You double back to the balcony. There’s a stained-glass window ahead and nowhere left to run.'
CASINO_ARREST = ('Glass scatters across the pavement. You land in a ring of police lights. '
                 'Officers close in and cuff you. One lets slip that someone tipped them off.')
_ENTER = frozenset(('\n', '\r', ' ', 10, 13, 343))
_ESCAPE = frozenset(('\x1b', 27))
COLD_OPEN = 'casino-cold-open'
ESCAPE_FIGHT = 'escape-fight'
MARUKI_QUESTIONS = (
    ('1', 'Hear him out', 'hear'),
    ('2', 'Ask about Sumire', 'sumire'),
    ('3', 'Refuse Maruki’s offer', 'reject'),
)


def button_clicked(button):
    if button is None:
        return False
    return clicked_story_button((button,)) is not None


def clicked_story_button(buttons):
    try:
        _, x, y, _, flags = C.getmouse()
    except C.error:
        return None
    if flags & C.BUTTON1_CLICKED:
        return next((key for row, col, label, key in buttons
                     if y == row and col <= x < col + len(label)), None)
    return None


@dataclass(frozen=True)
class Beat:
    heading: str
    body: str
    choices: tuple = ()
    enter: str | None = None
    enter_label: str = 'NEXT'


@dataclass(frozen=True)
class Scene:
    label: str
    beats: dict = field(default_factory=dict)
    before: bool = False
    optional: bool = False


SCENES = {
    COLD_OPEN: Scene('NOVEMBER / CASINO', {
        'start': Beat('LOSE THE GUARDS',
                      'You’re Joker, one of the Phantom Thieves. Your crew just pulled off a heist, '
                      'and guards are flooding the casino. A teammate cuts in over the radio: '
                      '“We’re taking the main exit. Joker, take the service stairs.” ' + CASINO_SIGNAL,
                      (('1', 'Take the service stairs', 'balcony'),)),
        'balcony': Beat('THE LAST WAY OUT',
                        CASINO_WINDOW,
                        enter='arrest', enter_label='JUMP THROUGH THE WINDOW'),
        'arrest': Beat('SURROUNDED',
                       CASINO_ARREST,
                       enter='interrogation', enter_label='CONTINUE TO INTERROGATION'),
        'interrogation': Beat('THE INTERROGATION ROOM',
                              'Prosecutor Sae Niijima sits across from you. She wants to know how a '
                              'student on probation became a Phantom Thief. To answer, you have to '
                              'start in April, when you first arrived in Tokyo.',
                              enter='done', enter_label='TELL SAE HOW IT STARTED'),
    }, before=True, optional=True),
    'castle-return': Scene('APRIL / SHUJIN', {
        'start': Beat('THE FIRST ESCAPE',
                      'You and Ryuji are locked in a cell. A cat calling himself Morgana slips '
                      'through the bars and gets the door open. Across the passage, a boy in a Shujin '
                      'volleyball jacket grips the bars of another cell. The king tells a guard to '
                      'lock the rest of the team up with him.',
                      enter=ESCAPE_FIGHT, enter_label='FOLLOW MORGANA'),
        'return': Beat('WHY GO BACK?',
                       'With the guard out of the way, Morgana gets you back to the real school. '
                       'Ann finds you outside the gym. Shiho, her friend on the volleyball team, isn’t '
                       'answering. You tell Ann about the boy in the cell. “I’m coming,” she says. '
                       '“I need to see what he’s doing to them.”',
                       enter='warden', enter_label='FOLLOW THE SOUND OF A BELL'),
        'warden': Beat('THE FIRST VISIT',
                       'That night you wake behind bars again, in a room lit blue. The man at the desk '
                       'introduces himself as Igor. “Your rehabilitation is our responsibility.” He calls '
                       'to Justine and Caroline. One twin unlocks your cell; the other shows you the book '
                       'where they’ll register Personas. The door will open again when you need it.',
                       enter='gate', enter_label='RETURN TO THE CASTLE'),
        'gate': Beat('AT THE GATE',
                     'Ann follows you through and the guards separate her from the group. Morgana, '
                     'now Mona on the radio, leads you back to the gate. Ryuji answers to Skull. You’re Joker.',
                     enter='done', enter_label='HELP ANN'),
    }, before=True),
    'castle-card': Scene('CASTLE / CALLING CARD', {
        'start': Beat('GIVE THE CROWN A SHAPE',
                      'Mona explains: a Palace grows from what its ruler wants most. You’ve found '
                      'Kamoshida’s Treasure, but it has no solid form. Warn the real Kamoshida that you’ll steal '
                      'it, and the fear of losing it makes it something you can take.',
                      enter='ready', enter_label='SEND THE CALLING CARD'),
        'ready': Beat('IT WORKED',
                      'The card is up at Shujin. Inside the castle, a crown now waits in the throne room. '
                      'If taking it changes Kamoshida’s heart, he’ll have to face what he did outside these walls.',
                      enter='done', enter_label='TAKE THE CROWN'),
    }, before=True),
    'castle-confession': Scene('SHUJIN / ASSEMBLY', {
        'start': Beat('HE SAYS IT HIMSELF',
                      'The real Kamoshida takes the microphone. No one has to speak for him this time. '
                      'He admits what he did to the students and says he’ll answer for it. Ann watches '
                      'the room fall silent. Stealing the crown changed something outside the castle.',
                      enter='aftermath', enter_label='LEAVE THE ASSEMBLY'),
        'aftermath': Beat('BACK IN THE HALLS',
                          'Shujin brings in a counselor, Dr. Maruki, to talk with students after the confession. '
                          'Outside, a first-year gymnast introduces herself as Kasumi Yoshizawa. You add her to '
                          'your contacts before heading back to Leblanc.',
                          enter='done', enter_label='BACK TO THE TEAM'),
    }),
    'museum-purpose': Scene('MAY / MADARAME’S EXHIBIT', {
        'start': Beat('WHO PAINTED IT?',
                      'Yusuke, an art student, defends his mentor Madarame. But a former pupil says '
                      'the famous painter passed off students’ work as his own. The Sayuri is the painting '
                      'at the center of his reputation. Its story may be the oldest lie in the exhibit.',
                      enter='done', enter_label='INVESTIGATE THE MUSEUM'),
    }, before=True),
    'bank-purpose': Scene('JUNE / SHIBUYA', {
        'start': Beat('THE PRICE OF KEEPING QUIET',
                      'Students are being pressured into jobs and then blackmailed. Makoto, Shujin’s '
                      'student council president, traces it to Kaneshiro. When he threatens the group, '
                      'she sees that waiting for the adults to act won’t get anyone out of his grip.',
                      enter='done', enter_label='ENTER KANESHIRO’S BANK'),
    }, before=True),
    'panther-joins': Scene('CASTLE / BY THE GATE', {
        'start': Beat('ANN TAKES HER NAME BACK',
                      'The king calls after Ann as if he can tell her where to stand. She refuses. '
                      'The chains fall away and Carmen, the Persona she awakens, stands between Ann and the king.',
                      (('1', 'Hold the gate for her', 'gate'),)),
        'gate': Beat('PANTHER',
                     'Ann takes one step toward the road home, then turns around. '
                     '“I came back for Shiho. I’m staying for the people he thinks can’t fight him.” '
                     'She waits at the gate for the others to catch up.', enter='done', enter_label='BACK TO DEBRIEF'),
    }),
    'fox-awakens': Scene('MUSEUM / THE LOCKED DOOR', {
        'start': Beat('THE NAME ON THE FRAME',
                      'Yusuke watches Madarame adjust a signature on a canvas by another pupil. '
                      'The motion is too practiced to be a mistake.',
                      (('1', 'Let Yusuke speak', 'answer'),)),
        'answer': Beat('GOEMON ANSWERS',
                       'Yusuke sets his sketchbook down. “You taught me to look closely. '
                       'I wish I had looked sooner.” When the guards come, Goemon meets them at his back.',
                       enter='done', enter_label='RETURN'),
    }),
    'queen-joins': Scene('BANK / SERVICE DOOR', {
        'start': Beat('MAKOTO TAKES THE LEAD',
                      'Kaneshiro tells Makoto to fetch someone who can negotiate. '
                      'Instead she walks up to the locked service door and lays a hand on it. '
                      'Johanna’s engine starts on the other side.',
                      (('1', 'Follow her through', 'follow'),)),
        'follow': Beat('QUEEN',
                       'Makoto rides through on Johanna, her newly awakened Persona. She waits until everybody is '
                       'through before she lets the door swing shut. '
                       '“Next time, we make the plan together.”', enter='done', enter_label='RETURN'),
    }),
    'bank-warning': Scene('BANK / THE EMPTY VAULT', {
        'start': Beat('SOMEONE WAS HERE BEFORE YOU',
                      'Kaneshiro slides away from the Treasure. “There’s someone else who can get in here. '
                      'A black mask. Even the Shadows give that one room.” You ask who it is. '
                      'Kaneshiro won’t even look at the door.',
                      enter='done', enter_label='TAKE THE TREASURE'),
    }),
    'pyramid-request': Scene('JULY / LEBLANC', {
        'start': Beat('A MESSAGE FOR THE THIEVES',
                      'An unsigned message on the Phan-Site names your team and gives a deadline.',
                      (('1', 'Open Medjed’s message', 'threat'),)),
        'threat': Beat('MEDJED’S DEADLINE',
                       '“Disband by August 21. If you refuse, we’ll make your names public and bring the '
                       'country’s servers down.” A second message arrives before you can reply: '
                       'someone says she can stop them.',
                       enter='request', enter_label='OPEN THE REPLY'),
        'request': Beat('A REQUEST FROM FUTABA',
                      'A hacker named Futaba asks the Thieves to steal her heart. She says she can stop Medjed, '
                      'the group threatening you, but that isn’t the only reason to help. She hasn’t been able to '
                      'leave her room since her mother, Wakaba, died. Futaba was made to believe it was her fault.',
                      enter='desert', enter_label='ANSWER FUTABA'),
        'desert': Beat('THE TOMB SHE IMAGINES',
                       'Futaba’s room becomes a pyramid in the Metaverse. Her Shadow offers a way inside: a bandit '
                       'in the desert town stole the map. Bring it back and she’ll show you the way to the stairs.',
                       enter='done', enter_label='FIND THE PAPYRUS'),
    }, before=True),
    'pyramid-inspect': Scene('PYRAMID / MURAL CHAMBER', {
        'start': Beat('TWO PIECES FELL OUT',
                      'The gallery mirrors throw a beam across the floor. '
                      'Two pieces of the mural are loose. The guard route is open whether you stop or not.',
                      (('1', 'Examine the kitchen fragment', 'fragment1'),
                       ('2', 'Examine the statement fragment', 'fragment2')),
                      enter='done', enter_label='CONTINUE TO COMBAT'),
        'fragment1': Beat(*PYRAMID_FRAGMENTS[0],
                          (('2', 'Examine the statement fragment', 'fragment2'),),
                          enter='done', enter_label='CONTINUE TO COMBAT'),
        'fragment2': Beat(*PYRAMID_FRAGMENTS[1],
                          (('1', 'Examine the kitchen fragment', 'fragment1'),),
                          enter='done', enter_label='CONTINUE TO COMBAT'),
    }, before=True, optional=True),
    'pyramid-recall': Scene('PYRAMID / REMEMBER THE MURAL', {
        'start': Beat(*PYRAMID_FRAGMENTS[0],
                      (('2', 'Look at the statement fragment', 'fragment2'),),
                      enter='fragment2', enter_label='NEXT'),
        'fragment2': Beat(*PYRAMID_FRAGMENTS[1],
                          (('1', 'Look at the kitchen fragment', 'start'),),
                          enter='done', enter_label='RETURN'),
    }, optional=True),
    'pyramid-recognition': Scene('PYRAMID / AT THE FOOT OF THE STAIRS', {
        'start': Beat('FUTABA STOPS ON THE STAIR',
                      'Futaba puts her hand over a mark on the stone. “That broken square. '
                      'I drew it on everything I was afraid to look at.” She looks up at the Sphinx. '
                      '“The Palace used my mark to make it feel true. That doesn’t make it Mom’s voice.”',
                      (('1', 'Give Futaba room', 'ready'),)),
        'unseen': Beat('FUTABA STOPS ON THE STAIR',
                       'A voice wearing Wakaba’s face calls down. Futaba asks it to use the little '
                       'nickname her mother used when work kept her away. It only repeats the accusation. '
                       'Futaba steps past the last stair on her own.',
                       (('1', 'Give Futaba room', 'ready'),)),
        'ready': Beat('AN OPENING OF HER OWN',
                      'Futaba studies the counterweight above the arena. “I think I know what this place '
                      'can do.” She asks the team to hold out while she takes the other side.',
                      enter='done', enter_label='DEPLOY'),
    }, before=True),
    'oracle-handoff': Scene('LEBLANC / AFTER THE PYRAMID', {
        'start': Beat('A NEW VOICE ON THE RADIO',
                      'Futaba’s Persona helped you bring the Sphinx down. Back home, she takes Medjed offline. '
                      'She asks to handle your maps and comms on the next job. On the radio, call her Oracle.',
                      (('1', 'Straighten the receipt', 'quiet'),), enter='done', enter_label='RETURN'),
        'quiet': Beat('A SMALL THANK YOU',
                      'Sojiro has left two cups behind the counter. Under one, you find a crooked receipt. '
                      'Futaba drew a tiny face on the back, where no one walking past would notice it.',
                      enter='done', enter_label='RETURN'),
    }),
    'spaceport-purpose': Scene('SEPTEMBER / OKUMURA FOODS', {
        'start': Beat('THE ARGUMENT AT THE HIDEOUT',
                      'Ryuji says the team can manage without Mona now that Futaba can navigate. Mona '
                      'puts his paws on the edge of the table. “Then I’ll find Okumura’s Palace myself.” '
                      'He jumps down before anyone can stop him.',
                      enter='catchup', enter_label='GO AFTER MONA'),
        'catchup': Beat('MONA WENT IN WITHOUT YOU',
                      'When you catch up to Mona inside Okumura’s Palace, a masked girl in a plumed hat '
                      'is covering his retreat. She introduces herself as the Beauty Thief. Mona '
                      'calls her Haru.',
                      enter='gate', enter_label='HEAR HARU OUT'),
        'gate': Beat('HER FATHER’S NAME OPENS DOORS',
                     'Haru is Okumura’s daughter. He’s using her engagement as part of a business arrangement '
                     'she never agreed to. Haru wants to take him on, and her family clearance is the only way '
                     'through the biometric gate. Mona asks to do this one together.',
                     enter='done', enter_label='OPEN THE INNER GATE'),
    }, before=True),
    'noir-joins': Scene('SPACEPORT / THE INNER GATE', {
        'start': Beat('HARU TAKES THE KEY',
                      'Haru takes the gate key from the defunct copy of her fiancé. She turns it once, '
                      'then leaves it in her own pocket. “The next door is mine to open.”',
                      (('1', 'Ask what to call her on comms', 'name'),)),
        'name': Beat('NOIR',
                     '“Noir,” she says. Behind her, the barrel of Milady’s cannon folds away into the '
                     'hem of her dress. Mona holds the door for her this time.',
                     enter='done', enter_label='BACK TO DEBRIEF'),
    }),
    'okumura-broadcast': Scene('SEPTEMBER / AFTER THE EXECUTIVE FLOOR', {
        'start': Beat('AFTER YOU LEAVE',
                      'As the last of the team leaves with the Treasure, the executive office falls silent. '
                      'A figure in a dark mask steps past the ruined robots and raises a hand toward the '
                      'Shadow still on the floor. The light under the office door goes out.',
                      enter='broadcast', enter_label='WATCH THE PRESS CONFERENCE'),
        'broadcast': Beat('THE BROADCAST GOES QUIET',
                          'The real Okumura starts to speak into the microphones. Haru edges closer to '
                          'the television. He grips the lectern and collapses before he can finish. '
                          'The feed holds on the empty lectern for one long second, then cuts.',
                          (('1', 'Check the Phan-Site', 'public'),)),
        'public': Beat('THE TIDE TURNS',
                       'The messages of support are already being buried. “Did the Thieves do this?” '
                       'The police are treating it as a death, not a change of heart. If you don’t find '
                       'out who else was there, you’ll take the blame for it.',
                       enter='done', enter_label='BACK TO DEBRIEF'),
    }),
    'crow-joins': Scene('CASINO / STAFF ELEVATOR', {
        'start': Beat('ONE MORE PERSON ON COMMS',
                      'The members card lights the elevator panel. Akechi waits until the doors close '
                      'before he gives Oracle the radio frequency to use.',
                      (('1', 'Ask for his codename', 'name'),)),
        'name': Beat('CROW',
                     '“Crow,” he says. “If the house cheats, tell me before you pull the alarm.” '
                     'He moves aside to give Joker a clear view of the next floor.',
                     enter='done', enter_label='BACK TO DEBRIEF'),
    }),
    'casino-purpose': Scene('NOVEMBER / COURTHOUSE', {
        'start': Beat('BEFORE THE CASE CLOSES',
                      'After Okumura collapses on television, the investigation turns on the Thieves. '
                      'Sae Niijima is the prosecutor closing in. Crow proposes entering her Palace before you '
                      'can be pinned for a death your crew didn’t cause. To her, the courthouse has become a '
                      'casino where the house decides who wins.',
                      enter='done', enter_label='ENTER THE CASINO'),
    }, before=True),
    'casino-phone-setup': Scene('CASINO / BEFORE THE HEIST', {
        'start': Beat('KEEP YOUR PHONE WITH YOU',
                      'Before you head in, Futaba checks your phone one more time. If you get separated and '
                      'Sae comes to see you, ask her to show the phone to whoever comes for you next. Futaba '
                      'won’t say more over an open channel.',
                      enter='done', enter_label='HEAD TO SAE’S WHEEL'),
    }, before=True),
    'casino-payoff': Scene('CASINO / THE ESCAPE', {
        'start': Beat('BACK AT THE BALCONY',
                      'Leviathan falls. Footsteps flood the ballroom as the team splits up. '
                      'The service door is in the same place. ' + CASINO_SIGNAL,
                      (('1', 'Take the service stairs', 'window'),)),
        'window': Beat('THE LAST WAY OUT', CASINO_WINDOW,
                       enter='capture', enter_label='JUMP THROUGH THE WINDOW'),
        'capture': Beat('THE CAPTURE',
                        CASINO_ARREST + ' The others get away. Your phone is taken into the station with you.',
                        enter='table', enter_label='BACK TO SAE'),
        'table': Beat('THE INTERROGATION ROOM',
                      'You’re back where you started, across the table from Sae. She closes her notebook '
                      'on the story you’ve just told. Someone is coming down the hall. It’s time to ask for '
                      'the favor Futaba prepared you for.',
                      (('1', 'Ask Sae to show Akechi the phone', 'change'),)),
        'change': Beat('A ROOM THAT LOOKS THE SAME',
                       'Outside, Sae passes Akechi and shows him the phone. Futaba uses that moment to '
                       'trigger the Metaverse app. He walks into what looks like the same interrogation room '
                       'and shoots the Palace’s copy of you. The real you is still in the police station.',
                       enter='signal'),
        'signal': Beat('THE OTHER END OF THE PLAN',
                       'Your door opens again. This time it’s Sae. The phone buzzes once in her coat: '
                       'Futaba has the signal she was waiting for. You leave by the stairs together.',
                       enter='done', enter_label='RETURN'),
    }),
    'cruiser-purpose': Scene('NOVEMBER / SHIDO’S CRUISER', {
        'start': Beat('THE MAN AT THE HELM',
                      'Shido is campaigning to lead Japan. You recognize him: he’s the man who got you '
                      'put on probation in April. After the casino trap, the Thieves follow the conspiracy '
                      'to him. In his Palace, he’s steering a ship that only his supporters are allowed to board.',
                      enter='letters', enter_label='CHECK THE PASSENGER LIST'),
        'letters': Beat('FIVE RECOMMENDATIONS',
                        'Entry to the central hall takes five letters from Shido’s VIPs. Start with Ooe and '
                        'the former noble. Get their signatures before the crew can reach the man on the bridge.',
                        enter='done', enter_label='FIND THE FIRST TWO VIPS'),
    }, before=True),
    'akechi-glove': Scene('CRUISER / OUTSIDE THE ENGINE ROOM', {
        'start': Beat('EARLIER / AFTER THE DUEL',
                      'Akechi pulls off a glove and tosses it at your feet. “Keep it. We’re settling this '
                      'properly next time.” He leaves before you can answer. You pick it up.',
                      enter='present', enter_label='BACK TO THE ENGINE ROOM'),
        'present': Beat('HIS FOOTSTEPS STOP',
                      'The glove is still in your coat. Akechi waits at the end of the passage. This time '
                      'Crow isn’t here to fight beside you.',
                      enter='done', enter_label='FACE AKECHI'),
    }, before=True),
    'akechi-farewell': Scene('CRUISER / ENGINE ROOM', {
        'start': Beat('THE BULKHEAD',
                      'The other Akechi appears at the far end of the engine room with a gun drawn. '
                      'Akechi keeps a hand on the bulkhead switch and looks at Joker instead.',
                      (('1', 'Show him the glove', 'answer'), ('2', 'Stay at the door', 'wait'))),
        'answer': Beat('THE DUEL ISN’T OVER',
                       'You hold up the glove he gave you. He recognizes it, just before the heavy door '
                       'comes down. On your side, the whole room goes still. Then you hear him move away '
                       'from the door toward his double.',
                       enter='quiet'),
        'wait': Beat('ONE MORE MOVE',
                     'You take one step toward the switch. Akechi shakes his head, just once, '
                     'and lowers the bulkhead. The footsteps behind it move away from you.',
                     enter='quiet'),
        'quiet': Beat('AFTER THE DOOR CLOSES',
                      'No one reaches for the controls again. You give the silence a few seconds, '
                      'put the glove away, and follow the others toward Shido.',
                      enter='done', enter_label='RETURN'),
    }),
    'shido-confession': Scene('DECEMBER / AFTER THE ELECTION', {
        'start': Beat('SHIDO SPEAKS',
                      'Shido stands before the cameras and confesses. The room is silent. '
                      'You wait for someone to ask what should happen next.',
                      (('1', 'Listen to the crowd outside', 'street'),)),
        'street': Beat('THE CITY STILL WAITS',
                       'On the crossing, someone puts away their phone. “All right. Who’s going to fix '
                       'it for us now?” The crowd keeps moving. Mona asks you to come back to Mementos '
                       'with him. One change of heart hasn’t reached whatever keeps Tokyo waiting.',
                       enter='done', enter_label='BACK TO DEBRIEF'),
    }),
    'depths-purpose': Scene('DECEMBER / MEMENTOS', {
        'start': Beat('WHY SHIDO WASN’T ENOUGH',
                      'Shido confessed, but people still want someone else to make their choices. One person’s '
                      'distortion can form a Palace. Mementos is a Palace shared by the public. The team follows '
                      'its tracks down to see what is keeping everyone so willing to give up control.',
                      enter='done', enter_label='GO BELOW TOKYO'),
    }, before=True),
    'grail-reckoning': Scene('VELVET ROOM / THE LOCKED CELL', {
        'start': Beat('ERASED FROM SHIBUYA',
                      'You survive the Grail’s attack. It draws strength from people who would rather let it '
                      'choose for them. Mementos spills into Tokyo. People look straight past the Thieves '
                      'until you disappear from the crossing altogether.',
                      enter='recall', enter_label='WAKE IN THE VELVET ROOM'),
        'recall': Beat('THE SAME WORDS',
                       'The lock clicks. The man at the desk says, “Your rehabilitation is our '
                       'responsibility.” This time he orders the twins to execute you. Justine keeps '
                       'one hand on the cell door. Caroline lowers her weapon.',
                       enter='wardens', enter_label='WATCH THE TWINS'),
        'wardens': Beat('THE REAL WARDEN',
                        'Justine and Caroline refuse the order to execute you. The twins become Lavenza again. '
                        'The master who’s been sitting in Igor’s place is the Grail in another form: the god '
                        'who’s been rigging the contest all along.',
                        enter='bargain', enter_label='HEAR THE OFFER'),
        'bargain': Beat('BE ALLOWED TO WIN',
                        'The false master offers to leave your fame intact if you let him keep control of the world. '
                        'Your friends are still locked in cells nearby. The offer gives them nothing.',
                        enter='reunite', enter_label='REFUSE THE BARGAIN'),
        'reunite': Beat('NOT ALONE',
                        'You go from cell to cell. You ask each friend to remember what they chose for themselves. '
                        'One by one they stand up. You return together to the city that Mementos has swallowed.',
                        enter='done', enter_label='RETURN TO SHIBUYA'),
    }),
    'january-contradiction': Scene('JANUARY / LEBLANC', {
        'start': Beat('A PLACE SET FOR WAKABA',
                      'Sojiro sets out another cup. Futaba is talking to the woman who just sat down. '
                      'It’s Wakaba, alive. Nobody in the room thinks this is strange, except you.',
                      enter='counselor', enter_label='ASK WHAT CHANGED'),
        'counselor': Beat('THE COUNSELOR’S ANSWER',
                          'Maruki, the counselor who worked at Shujin, explains that he can reshape what people '
                          'experience as real. He’s granting wishes so nobody has to live with their worst loss. '
                          'The cost is that they don’t get to choose whether he changes their lives.',
                          enter='sumire', enter_label='HEAR WHAT HE CHANGED'),
        'sumire': Beat('KASUMI AND SUMIRE',
                       'Maruki calls the gymnast Sumire. “Kasumi was my sister,” she says, barely above a '
                       'whisper. “After the accident I asked him to let me be her.” Maruki tells her he can '
                       'keep that wish in place. Sumire turns away and runs deeper into the laboratory.',
                       enter='done', enter_label='ENTER THE LABORATORY'),
    }, before=True),
    'daat-purpose': Scene('LABORATORY / SEALED ROUTE', {
        'start': Beat('WHERE THE SIGNAL GOES',
                      'The path into the deeper laboratory is sealed. Oracle traces the lock’s connection '
                      'into Mementos: Maruki is using the shared Palace to reach far beyond this building. '
                      'Follow the new Da’at route, reach the control room, and open the way from there.',
                      enter='done', enter_label='TAKE THE DA’AT ROUTE'),
    }, before=True),
    'violet-joins': Scene('LABORATORY / AFTER THE FIRST VISIT', {
        'start': Beat('THE NAME SHE CHOOSES',
                      'Sumire takes a breath. She says the last routine she practiced was hers, not her sister’s. '
                      'She won’t ask Maruki to take that away from her. In the Palace she still wants the name '
                      'Violet, but outside she asks you to call her Sumire.',
                      enter='done', enter_label='REGROUP WITH VIOLET'),
    }),
    'maruki-offer': Scene('LABORATORY / THE LAST OFFER', {
        'start': Beat('A TOMORROW WITHOUT LOSS',
                      'Maruki sets a second cup on the table. He can return the people the team lost. '
                      'He talks about them by name.',
                      MARUKI_QUESTIONS),
        'hear': Beat('THE LIFE HE WOULD CHOOSE',
                     '“I can stop this from ever hurting you again.” He looks down at his own cup. '
                     'For an instant you wonder which loss he’s talking about.',
                     MARUKI_QUESTIONS[1:]),
        'sumire': Beat('HER OWN NAME',
                       'Maruki offers to give her back a life without the accident. '
                       'Sumire answers before you can. “You’re not asking whether I want it. '
                       'You’re asking whether I want to stop being me.”',
                       (MARUKI_QUESTIONS[0], MARUKI_QUESTIONS[2])),
        'reject': Beat('ON YOUR OWN TERMS',
                       'You slide the calling card onto the table. No one promises that getting their '
                       'old life back will make it easier. The future is theirs to meet anyway.',
                       enter='done', enter_label='FACE MARUKI'),
    }, before=True),
    'maruki-coda': Scene('LABORATORY / AFTER THE LAST SHOT', {
        'start': Beat('NO PERSONAS LEFT',
                      'The floor gives way. Maruki grabs your sleeve, then swings at you with his '
                      'free hand. It’s a tired punch. He’s still holding on to the ledge.',
                      (('1', 'Take his hand', 'hold'),)),
        'hold': Beat('THE EDGE',
                     'You catch his wrist and don’t let go. Maruki looks down for a long second. '
                     'Then he puts his other hand up where you can reach it.',
                     enter='outside'),
        'outside': Beat('EARLY LIGHT',
                        'Outside, Sumire changes the contact in your phone from Kasumi to her own name. '
                        'You wait while she decides what photo to use.',
                        enter='done', enter_label='FINISH THE STORY'),
    }),
}

_BEFORE = {
    'campaign-start': COLD_OPEN, '__prologue__': COLD_OPEN,
    'april-infiltration': 'castle-return', 'throne-room': 'castle-card',
    'museum-entry': 'museum-purpose', 'bank-entry': 'bank-purpose',
    'pyramid-desert': 'pyramid-request',
    'pyramid-murals': 'pyramid-inspect', 'pyramid-boss': 'pyramid-recognition',
    'spaceport-entry': 'spaceport-purpose', 'casino-service': 'casino-purpose',
    'casino-heist': 'casino-phone-setup',
    'cruiser-guests': 'cruiser-purpose', 'cruiser-akechi': 'akechi-glove',
    'depths-prison': 'depths-purpose',
    'laboratory-reality': 'january-contradiction', 'laboratory-daat': 'daat-purpose',
    'laboratory-choice': 'maruki-offer',
}
_AFTER = {
    'castle-gate': 'panther-joins', 'throne-room': 'castle-confession', 'museum-security': 'fox-awakens',
    'bank-entry': 'queen-joins', 'bank-boss': 'bank-warning', 'pyramid-boss': 'oracle-handoff',
    'spaceport-entry': 'noir-joins', 'spaceport-boss': 'okumura-broadcast',
    'casino-service': 'crow-joins', 'casino-heist': 'casino-payoff',
    'cruiser-akechi': 'akechi-farewell', 'cruiser-duel': 'shido-confession',
    'depths-grail': 'grail-reckoning',
    'laboratory-reality': 'violet-joins', 'laboratory-choice': 'maruki-coda',
}
REQUIRED_AFTER = frozenset(_AFTER)
RECRUIT_HANDOFFS = {
    'castle-gate': 'Panther', 'museum-security': 'Fox', 'bank-entry': 'Queen',
    'spaceport-entry': 'Noir', 'casino-service': 'Crow', 'laboratory-reality': 'Violet',
}


def story_offer(node_id, phase, *, seen_clues=()):
    if phase == 'before':
        return _BEFORE.get(node_id)
    if phase == 'after':
        return _AFTER.get(node_id)
    if phase == 'review' and node_id in ('pyramid-murals', 'pyramid-door', 'pyramid-boss'):
        if PYRAMID_MOTIF in seen_clues:
            return 'pyramid-recall'
    return None


class StoryScene:
    def __init__(self, scene_id, *, seen_clues=(), suspendable=False):
        self.scene_id = scene_id
        self.scene = SCENES[scene_id]
        self.beat = 'unseen' if scene_id == 'pyramid-recognition' and PYRAMID_MOTIF not in seen_clues else 'start'
        self.inspected = set()
        self.clues = set()
        self.cancelled = False
        self.suspendable = suspendable
        self.suspended = False
        self.choice_pick = self.default_pick()
        self.requested_transition = None

    def primary_button(self):
        beat = self.scene.beats[self.beat]
        if beat.enter and not beat.choices:
            return 16, 3, f' ▶  {beat.enter_label}  ', '\n'
        if not beat.enter and len(beat.choices) == 1:
            key, label, _ = beat.choices[0]
            return 16, 3, f' ▶  {key}  {label}  ', key
        return None

    def choice_buttons(self):
        beat = self.scene.beats[self.beat]
        if not beat.choices or (not beat.enter and len(beat.choices) < 2):
            return ()
        options = [(key, f'{key}  {label}') for key, label, _ in beat.choices]
        if beat.enter:
            options.append(('\n', beat.enter_label))
        return tuple((16 + i, 3, f' {"▶" if i == self.choice_pick else " "}  {label}  ', key)
                     for i, (key, label) in enumerate(options))

    def default_pick(self):
        beat = self.scene.beats[self.beat]
        return len(beat.choices) if beat.enter else 0

    def mouse_enabled(self):
        return bool(self.primary_button() or self.choice_buttons())

    def draw(self, app):
        beat = self.scene.beats[self.beat]
        button = self.primary_button()
        choices = self.choice_buttons()
        actions = []
        if button:
            actions.append('ENTER SELECT')
        elif choices:
            actions.append('↑↓ CHOOSE  ENTER SELECT')
        elif beat.enter:
            actions.append('ENTER ' + beat.enter_label)
        if self.suspendable:
            actions.append('ESC TITLE')
        elif self.scene_id == 'pyramid-inspect':
            actions.append('ESC BRIEF')
        elif self.scene.before and not self.scene.optional:
            actions.append('ESC BRIEF')
        else:
            actions.append('ESC ' + ('SKIP' if self.scene_id == COLD_OPEN else 'BACK'))
        app.panel(self.scene.label, beat.heading, '  '.join(actions))
        app.lines(8, 3, beat.body, width=min(app.w - 6, 76), limit=6, color=WHITE)
        if self.scene_id == 'pyramid-inspect' and PYRAMID_MOTIF in self.clues:
            app.put(14, 3, 'BOTH FRAGMENTS NOTED', DIM)
        if button:
            row, col, label, _ = button
            app.put(row, col, label, CYAN, True, True)
        elif choices:
            for i, (row, col, label, _) in enumerate(choices):
                selected = i == self.choice_pick
                app.put(row, col, label, CYAN if selected else WHITE, selected, selected)
        else:
            for row, (key, label, _) in enumerate(beat.choices, 16):
                app.put(row, 3, f'{key}  {label}', CYAN)

    def key(self, k):
        if k in _ESCAPE:
            self.suspended = self.suspendable
            self.cancelled = self.scene.before and (not self.scene.optional or self.scene_id == 'pyramid-inspect')
            return True
        beat = self.scene.beats[self.beat]
        button = self.primary_button()
        choices = self.choice_buttons()
        if k == C.KEY_MOUSE:
            buttons = (button,) if button else choices
            if not buttons or (k := clicked_story_button(buttons)) is None:
                return False
        elif choices and k in (C.KEY_UP, C.KEY_DOWN):
            self.choice_pick = (self.choice_pick + (-1 if k == C.KEY_UP else 1)) % len(choices)
            return False
        elif choices and k in _ENTER:
            k = choices[self.choice_pick][3]
        elif k in _ENTER and button and not beat.enter:
            k = button[3]
        step = beat.enter if k in _ENTER else next((to for key, _, to in beat.choices if key == k), None)
        if step is None:
            return False
        if step == 'done':
            return True
        if step == ESCAPE_FIGHT:
            self.requested_transition = step
            return True
        self.beat = step
        self.choice_pick = self.default_pick()
        if self.scene_id == 'pyramid-inspect' and step in ('fragment1', 'fragment2'):
            self.inspected.add(step)
            if len(self.inspected) == 2:
                self.clues.add(PYRAMID_MOTIF)
        return False
