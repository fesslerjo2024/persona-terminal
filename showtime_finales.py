"""Two original character-cell reels for the third-semester duos.

Choreography references (actual Royal gameplay footage, no assets reused):
https://www.youtube.com/watch?v=F6BYdZ34KOM (Crow/Joker at 6:43)
https://www.youtube.com/watch?v=3XaOOKnntOw (Violet/Joker)
https://www.lp.zone/t/colors-flying-high-lets-play-persona-5-royal/3971?page=23
Titles are those of this terminal adaptation.
"""
from bisect import bisect_right
from math import cos, pi, sin

from wrestling_scene import Canvas, WIDTH

MASK = 'TWO SIDES OF THE MASK'
WALTZ = 'THE LAST WALTZ'
MASK_BEATS = (
    (.98, '01 / THUNDER OVER TOKYO'),
    (1.83, '02 / CROW: BERSERK'),
    (2.95, '03 / TWO LEVELS OF ATTACK'),
    (3.80, '04 / JOKER: THE KNIFE DROPS'),
    (5.35, '05 / CROW: BLADE FRENZY'),
    (6.27, '06 / ONE SHOT IN THE RAIN'),
    (7.80, '07 / TWO SIDES OF THE MASK'),
)
WALTZ_BEATS = (
    (.95, '01 / THE CHAPEL DOORS'),
    (2.55, '02 / ONE LINE, TWO THIEVES'),
    (3.40, '03 / VIOLET IN FLIGHT'),
    (4.29, '04 / KASUMI REACHES BACK'),
    (5.83, '05 / PAS DE DEUX'),
    (6.49, '06 / THE CROSSING BLADES'),
    (8.35, '07 / THE LAST WALTZ'),
)

# Rows are drawn in separate inks, so identities are readable in both color and
# monochrome: Joker's white mask and tails, Crow's pointed mask and armor,
# Violet's ribbon and rapier, and Kasumi's sleeveless leotard and long line.
HEAD = {
    'joker': (' .~~-~. ', '/_////_\\', '|<v==v>|', ' \\_--_/ '),
    'crow': (' .^--^. ', '/#\\  /#\\', '|[#\\/]> ', ' \\###_/ '),
    'violet': ('  <>_~.  ', ' /(-v-)\\ ', ' \\_   _)>', '   \\_/   '),
    'echo': (' .~_<>  ', '/ ~. )\\ ', '\\  o_o) ', '  \\_/   '),
    'shadow': (' ^.   .^ ', '/[o] [o]\\', '\\_  W  _/', '  \\===/  '),
}
INK = {'joker': 'red', 'crow': 'foe', 'violet': 'cyan', 'echo': 'face', 'shadow': 'rail'}
BODIES = {
    'joker': {
        'stand': ('_/\\::/\\_', ' \u007c\\::/| ', ' / || \\ ', '/_ || _\\', ' o/  \\o '),
        'swing': (' /\\::/======', '/_ \\::\\ ', '  /__\\ \\_', ' /_   \\_'),
        'fall': ('\\_/::\\_/', '  /::\\  ', ' / || \\ ', '   ||   ', '   \\/   '),
        'slash': (' _/::\\__', ' \\ |::|  \\ ', '  \\|::|   >', '  /_  \\_', ' o/    \\o'),
        'aim': ('_/\\::/========', ' \\ |::|      ', ' / || \\ ', '/_ || _\\', ' o/  \\o '),
        'bow': ('__/\\::/\\', '    \\::/\\___', '   /___\\ ', '   |  \\_ ', '  _/    \u003e'),
    },
    'crow': {
        'stand': ('<^/##\\^>', ' \\|##|/ ', ' / ## \\ ', '/_/  \\_\\', ' o/  \\o '),
        'rage': ('\\^/##\\^/', ' \\|##|/ ', ' <_##_> ', ' /_/\\_\\ ', ' o/  \\o '),
        'rush': (' _/###\\===>>', '  \\|#|/  ', '  / /\\_   ', ' <_/  \\_  '),
        'high': ('/\\/##\\===========', '  |##|/  ', '  /# \\  ', '_/_  \\_  '),
        'low': (' _/##\\___', '  \\|##|  \\____', '  /_/#\\______>>', ' <_   _/  '),
        'exit': ('<^\\##/^> ', ' /|##|\\ ', '   ## \\ ', '  /_/>  ', ' _/     '),
    },
    'violet': {
        'stand': (' _/\\Y/\\_', '  / |\\   ', '  \\ V/   ', '  / \\   ', ' _/ \\_  '),
        'swing': ('\\_/Y\\____', '   /|/>  ', '  // \\_ ', ' _/    >'),
        'reach': ('____/Y\\__/', '    |/\\  ', '   / \\_  ', '  _>  >  '),
        'spin': ('---_/Y\\__/', '    /|/> ', ' __/ V\\ ', '<____/  ', '    \\_  '),
        'blade': (' _/Y\\=========>>', '  / |/   ', '__\\ V\\   ', '\\___/\\_  ', '      \\_  '),
    },
    'echo': {
        'reach': ('____/|\\__/', '    \\|/    ', '     |\\    ', '    _/ >   '),
        'spin': ('---_/|\\__/', '    /|\\  ', '   /_/\\__', '  <______', '    \\_   '),
        'blade': (' _/|\\=========>>', '  /|\\    ', '  \\_/  __', ' </_____/', '   \\_    '),
    },
    'shadow': {
        'stand': ('_/\\[##]/\\_', ' \\|[##]|/ ', '  <####>  ', ' /_/  \\_\\ ', ' _/    \\_ '),
        'reel': ('<<\\[##]/|', '   [##] / ', '   <##>   ', '  /_/\\_', ' _/    >'),
    },
}
PORTRAITS = {
    'crow': (
        r'     .^--------^.',
        r'   _/##/  //##_',
        r'  /##_/##/##_/## ',
        r'  |####[ >  < ]####|',
        r'   ######/######/>',
        r'    #####==#####/',
        r' ^__/ ########/ __^',
        r'/####___==__/_/#### ',
    ),
    'joker': (
        r'     .-~~-~.',
        r'  ._//////~\ ',
        r' / /////////_  ',
        r'|  <___/___/>|',
        r'    v   v    /',
        r'  ____--____/',
        r'__/\:::///__',
        r' /  _:::_/   ',
    ),
    'violet': (
        r'    __ <> __',
        r'  .~  ~/~  ~.',
        r' /  ~~    ~~   ',
        r'|  (__/__/)  |',
        r' _   v  v   _/)',
        r'   __ ~~ __/ ~~',
        r'   __/>==<__',
        r'  / /   /   ',
    ),
}


def _center(c, y, s, ink='face', opaque=False):
    c.put((WIDTH-len(s))//2, y, s, ink, opaque)


def _flip(row):
    return row[::-1].translate(str.maketrans('/\\<>()[]{}', '\\/><)(][}{'))


def _sprite(c, who, x, y, pose='stand', face=-1):
    head, body = HEAD[who], BODIES[who][pose]
    for i, row in enumerate(head + body):
        row = row if face == 1 else _flip(row)
        # Center asymmetrical weapons around the torso rather than sliding
        # the actor as attack frames get wider.
        offset = 8-len(row) if face == -1 and len(row)>8 else 0
        # Mask only the silhouette's interior: keep the stage around the
        # edges, but don't let windows or candles show through a face.
        left = len(row) - len(row.lstrip())
        c.put(x+offset+left, y+i, row.strip(),
              ('face' if who == 'joker' and i == 2
               else 'red' if who == 'violet' and i == 0 else INK[who]), True)


def _path(c, x0, y0, x1, y1, ink, char=None, stride=1):
    steps = max(abs(x1-x0), abs(y1-y0))
    for k in range(0, steps+1, stride):
        f = k/max(1, steps)
        mark = char or ('|' if abs(x1-x0)<abs(y1-y0)/2 else
                        '-' if y0 == y1 else '\\' if (x1-x0)*(y1-y0)>0 else '/')
        c.put(round(x0+(x1-x0)*f), round(y0+(y1-y0)*f), mark, ink)


def _shards(c, x, y, tick, ink='gold', size=8):
    for i, (dx, dy) in enumerate(((-3,-2),(-2,1),(-2,2),(-3,0),
                                  (3,-2),(2,1),(2,2),(3,0),(0,2),(0,-2))):
        length = .55 + .1*((tick+i*2)%4)
        _path(c, x+dx, y+dy, x+round(dx*size*length/3),
              y+round(dy*min(3,size/3)*length), ink, stride=2)
    c.put(x-2, y, ('-*+*-', '+*#*+')[tick%2], 'flash')


def _roof(c, t, flash=False):
    # Moving parallax story: rain, silhouettes and the foreground rooftop.
    tick = int(16*t)
    for x, y, w in ((0,3,7),(8,1,6),(15,5,8),(25,3,5),
                    (32,4,4),(38,2,7),(46,5,4),(51,1,6)):
        c.put(x, y, '+'+'-'*(w-2)+'+', 'dim')
        for r in range(y+1, 9):
            windows = ''.join('.' if (i*5+r*3+x)%7 in (1,3) else ' '
                              for i in range(w-2))
            c.put(x, r, '|'+windows+'|', 'dim')
    for i in range(26):
        y = (i*7+tick)%11
        x = (i*19+tick*2-y)%WIDTH
        c.put(x, y, '/', 'rail' if (i%5==0 and flash) else 'dim')
    if flash:
        _path(c, 48, 0, 44, 3, 'gold', '/')
        _path(c, 44, 3, 49, 3, 'gold', '-')
        _path(c, 49, 3, 41, 7, 'white', '/')
    c.put(0, 10, '.'*WIDTH, 'dim')
    for x in (2,17,40,49):
        c.put(x, 9, (' .----. ', '/_::::_\\', '|_____|'), 'rope')
    c.put(0, 12, '+'+'='*(WIDTH-2)+'+', 'rail')
    c.put(0, 13, ' |//      R O O F T O P   /   S T O R M      \\\\| '.center(WIDTH), 'rope')
    c.put(0, 14, '+'+'-'*(WIDTH-2)+'+', 'dim')


def _chapel(c, t):
    # Tall leaded-glass lancets, high rib vaults and a tiled vanishing point.
    for x in (2, 44):
        c.put(x, 0, ('    /\\', '   /  \\', '  / /\\ \\', ' /_/__\\_\\',
                     ' | :||: |', ' | .||. |', ' |_:||:_|', '   |  |'), 'rope')
    window = (
        '       _/\\_',
        '     _/ /\\ \\_',
        '    / _/{}\\_ \\',
        '   / /<>||<>\\ \\',
        '   ||+==++==+||',
        '   || <>||<> ||',
        '   || / || \\ ||',
        '   +===/  \\===+',
    )
    c.put(21, 0, window, 'cyan')
    for x in (1, 12, 43, 54):
        c.put(x, 7, (" . ", " ) ", " | ", "_|_"), 'gold')
    c.put(0, 11, '+'+'-'*(WIDTH-2)+'+', 'rope')
    for x in (0,12,24,31,43,56):
        _path(c, 28+(x-28)//4, 11, x, 14, 'dim', stride=3)
    c.put(0, 13, '.'*WIDTH, 'dim')
    for i in range(12):
        f = (t*.35+i*.16)%1
        x = (i*17+int(f*9))%WIDTH
        c.put(x, 2+int(f*10), ('.','*',',')[i%3], 'face' if i%4 else 'red')


def _pick(t, beats):
    t = min(max(t,0), beats[-1][0])
    i = min(bisect_right([end for end,_ in beats], t), len(beats)-1)
    start = beats[i-1][0] if i else 0
    return t, i, (t-start)/(beats[i][0]-start)


def _mask(t):
    t, shot, f = _pick(t, MASK_BEATS)
    c = Canvas()
    tick = int(t*16)
    _roof(c, t, flash=(shot == 0 and .3<f<.68) or (shot == 1 and .39<f<.62))
    if shot == 0:
        c.put(4, 2, PORTRAITS['crow'], 'foe', opaque=True)
        c.put(35, 2, PORTRAITS['joker'], 'face', opaque=True)
        c.put(23, 5, ('  //  ', ' //   ', '//    '), 'red')
        c.put(8, 10, ' [ CROW ] ', 'red', True)
        c.put(38, 10, ' [ JOKER ] ', 'face', True)
    elif shot == 1:
        _sprite(c, 'joker', 9, 3, 'stand', 1)
        _sprite(c, 'shadow', 42, 3, 'stand', -1)
        cx = 22+round(3*f)
        for i in range(6):
            a = 2*pi*(i/6+f*.42)
            c.put(cx+4+round(cos(a)*(6+2*f)), 6+round(sin(a)*(3+f)), '+', 'red')
        _sprite(c, 'crow', cx, 3-(tick%2), 'rage', 1)
        c.put(0, 13, '[ B E R S E R K ]'.center(WIDTH), 'flash', True)
    elif shot == 2:
        jx, jy = 9+round(18*f), 2-round(2*sin(pi*f))
        cx = 12+round(20*f)
        _path(c, 31, 0, jx+6, jy+4, 'cyan', stride=2)
        c.put(jx-10, jy+7, '.--->>', 'dim')
        c.put(cx-9, 10, '--->> ', 'rail')
        _sprite(c, 'crow', cx, 5, 'rush', 1)
        _sprite(c, 'joker', jx, jy, 'swing', 1)
        _sprite(c, 'shadow', 43, 3, 'stand', -1)
    elif shot == 3:
        x = 28+round(f*10)
        y = round(f*f*4)
        _sprite(c, 'crow', 19+round(6*f), 5, 'rush', 1)
        _sprite(c, 'shadow', 45+round(2*f), 4, 'reel', -1)
        _path(c, 41, 0, x+5, y+7, 'face', '|', stride=2)
        _sprite(c, 'joker', x, y, 'slash' if f>.56 else 'fall', 1)
        if f>.52:
            _path(c, x+10, y, x+10, 11, 'gold', '|')
            _shards(c, x+11, 7, tick, 'gold', 6)
    elif shot == 4:
        _sprite(c, 'joker', 13-round(f*6), 3, 'stand', -1)
        x = 29+round(4*sin(4*pi*f))
        high = int(f*8)%2 == 0
        _sprite(c, 'shadow', 42+round(2*sin(8*pi*f)), 3, 'reel', -1)
        _sprite(c, 'crow', x, 1 if high else 5, 'high' if high else 'low', 1)
        _path(c, x+4, 2 if high else 10, 53, 10 if high else 2, 'red')
        _shards(c, 46, 5+int(f*8)%3, tick, 'red', 9)
    elif shot == 5:
        _sprite(c, 'joker', 12+round(4*f), 3, 'aim', 1)
        _sprite(c, 'crow', 8-round(8*f), 5, 'exit', -1)
        _sprite(c, 'shadow', 42, 3, 'reel', -1)
        if .36<f<.65:
            c.put(26, 7, '>>> --------------- >*', 'gold')
            _shards(c, 45, 7, tick, 'flash', 12)
        elif f>=.65:
            for i in range(9):
                c.put(36+i*2, 8+(i%4), '*..'[i%3], 'rope')
    else:
        _sprite(c, 'crow', 4+max(0, 5-round(f*6)), 3, 'exit', -1)
        _sprite(c, 'joker', 43, 3, 'stand', -1)
        _center(c, 3, '/=------------------------=\\', 'rail', True)
        _center(c, 5, 'TWO SIDES', 'face', True)
        _center(c, 6, 'OF THE MASK', 'gold', True)
        _center(c, 8, '\\=------------------------=/', 'rail', True)
        c.put(0, 13, '[ CROW x JOKER ]'.center(WIDTH), 'face', True)
    return MASK_BEATS[shot][1], c.finish()


def _dip(c, x, y):
    c.put(x, y, HEAD['joker'], 'red')
    c.put(x+1, y+2, '<v==v>', 'face')
    c.put(x-2, y+4, (' _/\\::/==========.', '   |::|           \\',
                      '  / || \\           \\',
                      ' /_ || _\\           \\__',
                      ' o/    \\o'), 'red')
    c.put(x+18, y+5, (' <~_  ', '(=v-)~>', ' \\__/ '), 'cyan')
    c.put(x+7, y+6, ('    .-/Y\\---', ' __/ /V\\    ', '<___/  \\___>'), 'cyan')
    c.put(x+22, y+5, '<>', 'red')


def _waltz(t):
    t, shot, f = _pick(t, WALTZ_BEATS)
    c = Canvas()
    tick = int(t*14)
    _chapel(c, t)
    if shot == 0:
        c.put(9+round(8*f), 6, ('   _     ', ' _| |__  ',
                                '|______| ', '_________'), 'rope')
        _sprite(c, 'joker', 5+round(8*f), 4, 'stand', 1)
        _sprite(c, 'violet', 16+round(7*f), 3, 'reach', 1)
        _sprite(c, 'shadow', 45, 3, 'stand', -1)
    elif shot == 1:
        x = 8+round(30*f)
        y = 3+round(2.5*sin(pi*f))-round(4*f)
        _path(c, 28, 0, x+4, y+4, 'face', stride=2)
        _path(c, x-6, y+7, x, y+8, 'cyan', '.')
        _sprite(c, 'shadow', 45, 4, 'reel' if f>.50 else 'stand', -1)
        _sprite(c, 'joker', x, y, 'swing', 1)
        _sprite(c, 'violet', x-6, y+3, 'swing', 1)
        if .38<f<.83 and tick%3:
            _path(c, x+11, y+5, 48, 8, 'gold', '.', stride=2)
            _shards(c, 48, 9, tick, 'flash', 5)
    elif shot == 2:
        x = 37-round(13*f)
        y = round(3*f*f)
        _path(c, 28, 0, 42+round(12*f), 3, 'rope', stride=2)
        _sprite(c, 'joker', 42+round(12*f), 0, 'swing', 1)
        _sprite(c, 'violet', x, y, 'spin', -1)
        for j in range(5):
            c.put(x+5+j*2, y+4-j%3, '.,*'[j%3], 'cyan')
    elif shot == 3:
        c.put(6, 2, PORTRAITS['violet'], 'cyan', True)
        c.put(13, 2, '<>', 'red')
        c.put(35-round(3*f), 1, ('  .-~^~~.', ' /- ~  ~\\',
                                 '(      < )', ' \\    o_o)',
                                 '  \\___-_/ ', '   _/|\\__ ',
                                 '  / /|\\ \\ '), 'face', True)
        _path(c, 20, 9, 28, 8, 'cyan')
        _path(c, 37, 8, 30, 8, 'face')
        c.put(27, 8, '-*-' if f>.45 else ' . ', 'flash')
        _center(c, 12, ' [ VIOLET  /  KASUMI ] ', 'face', True)
    elif shot == 4:
        # The two silhouettes orbit, swapping foreground and background.
        a = 2*pi*f
        dx, dy = round(11*cos(a)), round(1.7*sin(a))
        sx, sy = 27+dx, 2+dy
        ex, ey = 27-dx, 2-dy
        for i in range(13):
            angle = a-.16*i
            c.put(31+round(17*cos(angle)), 8+round(3*sin(angle)),
                  ('o' if i%3==0 else '.'), 'cyan' if i%2 else 'white')
        pose = 'spin' if f<.78 else 'blade'
        _sprite(c, 'shadow', 43, 4, 'stand', -1)
        for who,x,y in sorted((('violet',sx,sy), ('echo',ex,ey)), key=lambda pair:pair[2]):
            _sprite(c, who, x, y, pose, 1 if x<=27 or pose=='blade' else -1)
    elif shot == 5:
        _sprite(c, 'shadow', 41, 4, 'reel', -1)
        _sprite(c, 'violet', 21+round(12*f), 3, 'blade', 1)
        _sprite(c, 'echo', 27+round(12*f), 0, 'blade', 1)
        if f>.24:
            _path(c, 29, 11, 54, 2, 'face')
            _path(c, 32, 1, 55, 10, 'cyan')
            _shards(c, 46, 6, tick, 'gold', 12)
    else:
        _dip(c, 14, 3-round(1-f))
        c.put(5, 3, '+', 'face')
        c.put(48, 3, '+', 'face')
        _center(c, 11, '.-=-----------------------=-.', 'cyan', True)
        c.put(0, 12, 'T H E  L A S T  W A L T Z'.center(WIDTH), 'face', True)
        c.put(0, 14, 'JOKER x VIOLET'.center(WIDTH), 'gold', True)
    return WALTZ_BEATS[shot][1], c.finish()


SCENES = {
    MASK: (MASK_BEATS[-1][0], _mask),
    WALTZ: (WALTZ_BEATS[-1][0], _waltz),
}
