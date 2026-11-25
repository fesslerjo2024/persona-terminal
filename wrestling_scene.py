"""Hand-drawn ASCII storyboard for Queen and Noir's wrestling Showtime.

A tiny character-cell stage layers scenery, articulated poses and impact
effects. Frame generation is pure so battle and rehearsal use the same reel.
"""
from bisect import bisect_right
from itertools import groupby

TITLE = 'PALACE BODY SLAM'
WIDTH, HEIGHT = 57, 15
# Editorial timecodes, never displayed during playback.
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
    
    for y in (5, 7, 9):
        c.put(4, y, 'O' + '='*47 + 'O', 'rope')
    for x in (4, 52):
        for y in range(4, 11):
            c.put(x, y, 'O' if y in (5, 7, 9) else '|', 'rail')
    c.put(3, 10, '/' + '.'*49 + '\\', 'dim')
    c.put(2, 11, '/' + '.'*51 + '\\', 'dim')
    c.put(1, 12, 'O' + '='*53 + 'O', 'rail')
    c.put(1, 13, '|'+' /'*26+' |', 'rail')
    c.put(1, 14, '+' + '-'*53 + '+', 'rail')
    for x, y in ((8, 3), (49, 3), (54, 6), (2, 8)):
        if (int(t*10)+x) % 8 < (5 if impact else 2):
            c.put(x, y, '+', 'face')


def _impact(c, x, y, big=False):
    burst = (
        r'      \    |    /',
        r'  --   \   |   /   --',
        r'     .-*=======*-.',
        r'>>>  <    #!#    >  <<<',
        r'     `-*=======*-`',
        r'  --   /   |   \   --',
        '      /    |    \\',
    ) if big else (r'   \ | /', '--< * >--', '   / | \\')
    c.put(x, y, burst, 'flash', opaque=True)


def render(elapsed):
    """Return (beat label, lines of (ASCII run, ink)) for an elapsed second."""
    t = min(max(elapsed, 0.0), SECONDS)
    shot = min(bisect_right(ENDS,t), len(BEATS)-1)
    dt = t - (ENDS[shot-1] if shot else 0)
    f = dt / (ENDS[shot] - (ENDS[shot-1] if shot else 0))
    c = Canvas()
    _ring(c, t, shot in (6, 8))
    if shot <= 1:
        c.sprite('foe', 25, 4)
        step = f * .65 if shot == 0 else .65 + f * .35
        c.sprite('queen', 6 + int(step*6), 4, 'run' if int(t*10)%2 else 'ready')
        c.sprite('noir', 46 - int(step*8), 3, 'run' if int(t*10)%2 else 'ready')
        c.put(25, 0, ('  _o_  ', ' /___\\ ', '   *   '), 'gold', opaque=True)
        if shot == 1:
            for j in range(1,4):
                radius = j*4+int(f*4)
                c.put(28-radius,1,'((', 'face')
                c.put(27+radius,1,'))', 'face')
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
    elif shot == 6:
        # Brief impact panel, not a rapidly alternating full-screen flash.
        c.sprite('queen', 12, 5, 'strike')
        c.sprite('noir', 37, 4, 'kick')
        _impact(c, 17, 2, big=True)
    elif shot == 7:
        c.sprite('queen', 10, 4)
        c.put(22, 10, r'--<*_[(@)]_*>--', 'foe', opaque=True)
        c.put(23, 8, (' __/}>{\\', '/_==/o\\_>'), 'noir', opaque=True)
        count = min(3, int(dt/.60)+1)
        for i in range(count):
            c.put(20+i*7, 2, '*', 'flash' if i==count-1 else 'rail')
        if dt%.60 < .22:
            c.put(37, 8, ('  (o)', ' __/___', '/_/ \\_'), 'face', opaque=True)
            c.put(43, 11, '*', 'flash')
        else:
            c.put(37, 8, ('  (o)', ' __|_/', '/_/ \\_'), 'face', opaque=True)
    else:
        # Let the referee rise and raise a hand. The camera stays ringside.
        c.put(22, 10, r'--<*_[(@)]_*>--', 'foe', opaque=True)
        c.sprite('queen', 10+int(f*6), 4, 'victory' if f>.38 else 'ready')
        c.sprite('noir', 29+int(f*4), 4-int(f*2), 'victory' if f>.50 else 'ready')
        c.put(43, 8-int(f*4), ('  (o)/', ' __|/', '  / \\ '), 'face', opaque=True)
        for j in range(3):
            c.put(23+j*6, 2, '+' if int(t*8)%3==j else '*', 'flash')
    return BEATS[shot][1], c.finish()
