"""Hand-drawn ASCII storyboard for Queen and Noir's wrestling Showtime.

A tiny character-cell stage layers scenery, articulated poses and impact
effects. Frame generation is pure so battle and rehearsal use the same reel.
"""
from bisect import bisect_right
from itertools import groupby

TITLE = 'PALACE BODY SLAM'
WIDTH, HEIGHT = 57, 15
# (end time, on-screen beat). The last second belongs to the held victory pose.
BEATS = (
    (1.24, '01 / ENTER THE RING'),
    (1.88, '02 / RING THE BELL'),
    (2.68, '03 / QUEEN: LARIAT'),
    (3.48, '04 / NOIR: DROPKICK'),
    (4.52, '05 / TO THE TOP ROPES'),
    (5.48, '06 / DOUBLE DIVE'),
    (5.87, '07 / IMPACT'),
    (7.67, '08 / THE COUNT'),
    (8.90, '09 / MATCH OVER'),
)
ENDS = tuple(end for end, _ in BEATS)
SECONDS = ENDS[-1]

# Asymmetric heads and gear survive a terminal's coarse resolution:
# Queen's visor, spiked shoulder pads and armor vs. Noir's brim, curls and bow.
HEADS = {
    'queen': (' .---. ', '/[===]\\', '\\_v_v_/'),
    'noir':  ('  _/\\ ', '==/__)==', ' (o.o) ', ' ~\\v/~ '),
    'foe':   (' /\\ /\\ ', '< * * >', ' \\_W_/ '),
}
BODIES = {
    'queen': ('_/[#]\\_', '  |#|  ', ' /   \\ ', '_|   |_'),
    'noir':  ('-/}> {\\-', '  /o\\  ', ' /   \\ ', '<_   _>'),
    'foe':   ('/\\|@|/\\', '  |@|  ', ' /   \\ ', '/_   _\\'),
}
ACTION = {
    'queen': {
        'run': ('  [#]==>', ' /|_|   ', ' <  \\_  '),
        'strike': ('_/=======>', '  [#]/    ', ' _/ \\___  '),
        'dive': ('\\_[#]_/', '  /#\\  ', ' _| |_ '),
        'victory': ('\\_/[#]\\_/', '    |#|  ', '   _| |_ '),
    },
    'noir': {
        'run': ('  }>{__', ' / /o\\ ', '_<   \\_'),
        'kick': ('<<___/}>-', '<<___/o\\ ', '       \\_'),
        'dive': ('\\_}>{_/', '  /o\\  ', ' _| |_ '),
        'victory': ('_/}>{_/o', '   /o\\  ', '  _| |_ '),
    },
}


# Splash close-ups use larger original sprites than the in-ring action.
PORTRAITS = {
    'queen': (
        r'    .------.',
        r'   / ////// \ ',
        r'  |========//|',
        r'  | \==[]==/ |',
        r'   \___v_v__/',
        r'  / ^[###]^ \ ',
        r' /_/|#####|\_\ ',
    ),
    'noir': (
        r'      _/\ ',
        r'    _/__ )_',
        r' ===\_____)===',
        r'   { (. .) }',
        r'  {~\  v /~~}',
        r'     >}< {',
        r'   _/  o  \_',
    ),
}


class Canvas:
    def __init__(self):
        self.cells = [[(' ', 'dim')] * WIDTH for _ in range(HEIGHT)]

    def put(self, x, y, rows, ink, opaque=False):
        if isinstance(rows, str):
            rows = (rows,)
        for j, row in enumerate(rows, y):
            if not 0 <= j < HEIGHT:
                continue
            for i, ch in enumerate(row, x):
                if 0 <= i < WIDTH and (ch != ' ' or opaque):
                    self.cells[j][i] = ch, ink

    def sprite(self, who, x, y, pose='ready'):
        head = HEADS[who]
        body = ACTION.get(who, {}).get(pose, BODIES[who])
        for i, line in enumerate(head + body):
            self.put(x, y + i, line, who if i >= len(head) else 'face', opaque=True)

    def finish(self):
        return tuple(tuple((''.join(ch for ch, _ in run), ink)
                           for ink, run in groupby(row, key=lambda cell: cell[1]))
                     for row in self.cells)


def _ring(c, t, impact=False):
    # Separate back ropes, canvas, apron and crowd. No random state is needed.
    c.put(0, 0, r' . .     \    .    /      .   .     \    .     /      .', 'dim')
    c.put(0, 1, r'  .  .    \       /       . .        \        /     . ', 'dim')
    for i in range(3):
        audience = ''.join('o' if (x*11 + i*7) % 17 in (0, 4)
                           else '.' if (x*5+i) % 13 < 3 else ' ' for x in range(WIDTH))
        c.put(0, 2+i, audience, 'dim')
    c.put(17, 0, ' +--- IRWF ARENA ---+ ', 'rail', opaque=True)
    for y in (5, 7, 9):
        c.put(4, y, 'O' + '='*47 + 'O', 'rope')
    for x in (4, 52):
        for y in range(4, 11):
            c.put(x, y, 'O' if y in (5, 7, 9) else '|', 'rail')
    c.put(3, 10, '/' + '.'*49 + '\\', 'dim')
    c.put(2, 11, '/' + '.'*51 + '\\', 'dim')
    c.put(1, 12, 'O' + '='*53 + 'O', 'rail')
    c.put(1, 13, '|         [ PHANTOM WRESTLING FEDERATION ]           |', 'rail')
    c.put(1, 14, '+' + '-'*53 + '+', 'rail')
    for x, y in ((8, 3), (49, 3), (54, 6), (2, 8)):
        if (int(t*10)+x) % 8 < (5 if impact else 2):
            c.put(x, y, '+', 'face')


def _impact(c, x, y, big=False):
    burst = (
        r'      \    |    /',
        r'  --   \   |   /   --',
        r'     .-*=======*-.',
        r'>>>  <  K R A K  >  <<<',
        r'     `-*=======*-`',
        r'  --   /   |   \   --',
        '      /    |    \\',
    ) if big else (r'   \ | /', '--< * >--', '   / | \\')
    c.put(x, y, burst, 'flash', opaque=True)


def _titles(c, first, second):
    for y in (1, 13):
        c.put(9, y, '/' * 39, 'rope')
    c.put(16, 2, ' [ SHOWTIME / TAG TEAM ] ', 'rail', opaque=True)
    c.put(10, 11, '  '+first+'  ', 'queen', opaque=True)
    c.put(35, 11, '  '+second+'  ', 'noir', opaque=True)


def render(elapsed):
    """Return (beat label, lines of (ASCII run, ink)) for an elapsed second."""
    t = min(max(elapsed, 0.0), SECONDS)
    shot = min(bisect_right(ENDS,t), len(BEATS)-1)
    dt = t - (ENDS[shot-1] if shot else 0)
    f = dt / (ENDS[shot] - (ENDS[shot-1] if shot else 0))
    c = Canvas()
    _ring(c, t, shot in (6, 8))
    if shot == 0 and f < .52:
        _titles(c, 'Q U E E N', 'N O I R')
        c.put(9, 3, PORTRAITS['queen'], 'queen', opaque=True)
        c.put(34, 3, PORTRAITS['noir'], 'noir', opaque=True)
        c.put(26, 6, '  &  ', 'rail', opaque=True)
    elif shot <= 1:
        c.sprite('foe', 25, 4)
        c.sprite('queen', 8 + int(f*4), 4)
        c.sprite('noir', 41 - int(f*3), 3)
        if shot == 1:
            c.put(18, 1, ('  (( DING! DING! ))  ' if int(dt*11)%2
                         else '     DING! DING!     '), 'flash', opaque=True)
    elif shot == 2:
        c.sprite('foe', 26 + (2 if f>.64 else 0), 4)
        c.sprite('noir', 42, 3)
        x = 12+int(min(1,f*1.55)*10)
        c.put(x-5, 9, '-->>', 'queen')
        c.sprite('queen', x, 4, 'strike' if f>.46 else 'run')
        if f>.58:
            _impact(c, 28, 6)
    elif shot == 3:
        c.sprite('queen', 9, 4)
        c.sprite('foe', 27-(4 if f>.57 else 0), 4)
        x = 40 - int(min(1,f*1.72)*10)
        y = 3 - int(2*(1-abs(2*f-1)))
        c.put(x+10, y+5, '<<---', 'noir')
        c.sprite('noir', x, y, 'kick')
        if f>.51:
            _impact(c, 24, 6)
    elif shot == 4:
        c.put(22, 10, r'--<*_[(@)]_*>--', 'foe', opaque=True)
        y = 4-int(min(1,f*1.3)*3)
        c.sprite('queen', 10-int(f*5), y)
        c.sprite('noir', 41+int(f*4), max(1,y-1))
    elif shot == 5:
        c.put(22, 10, r'--<*_[(@)]_*>--', 'foe', opaque=True)
        x, y = int(f*13), max(0,int(f*f*6))
        c.put(5+x, max(0,y-1), r'\ \ ', 'queen')
        c.put(46-x, max(0,y-1), '/ /', 'noir')
        c.sprite('queen', 7+x, y, 'dive')
        c.sprite('noir', 43-x, y, 'dive')
        c.put(2, 13, '[ DOUBLE DEATH BLOW ]'.center(53), 'flash', opaque=True)
    elif shot == 6:
        # Brief impact panel, not a rapidly alternating full-screen flash.
        c.sprite('queen', 12, 5, 'strike')
        c.sprite('noir', 37, 4, 'kick')
        _impact(c, 17, 2, big=True)
        c.put(16, 12, '[ D O U B L E   D I V E ]', 'flash', opaque=True)
    elif shot == 7:
        c.sprite('queen', 10, 4)
        c.put(22, 10, r'--<*_[(@)]_*>--', 'foe', opaque=True)
        c.put(23, 8, (' __/}>{\\', '/_==/o\\_>'), 'noir', opaque=True)
        count = min(3, 1+int(dt/.60))
        for i in range(count):
            c.put(18+i*8, 2, f'[ {i+1} ]', 'flash' if i==count-1 else 'rail', opaque=True)
        c.put(2, 13, '[ PINFALL ]'.center(53), 'rail', opaque=True)
        c.put(37, 8, ('  (o)', ' __|__', '/_/ \\_'), 'face', opaque=True)
        if int(dt*10)%6<3:
            c.put(37, 11, '* SLAP *', 'flash', opaque=True)
    else:
        _titles(c, 'Q U E E N', 'N O I R')
        c.sprite('queen', 13, 3, 'victory')
        c.sprite('noir', 36, 3, 'victory')
        c.put(24, 6, '  WIN!  ', 'flash', opaque=True)
        c.put(2, 13, '[ P I N F A L L ]'.center(53), 'flash', opaque=True)
    return BEATS[shot][1], c.finish()
