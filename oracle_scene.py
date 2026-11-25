"""Oracle's All-Out Attack: original ASCII art, inspired by the Royal footage.

Reference: https://p-ch.jp/news/3885/ and
https://www.youtube.com/watch?v=W3J4rSjfgeE
"""
from wrestling_scene import Canvas, WIDTH, HEIGHT

TITLE = 'ORACLE // UFO PAYLOAD'
SECONDS = 4.65

UFO = (
    '             .-----------.',
    '          .-"  _/\\_/\\_   "-.',
    '    ____ /   .-----------.   \\ ____',
    ' _=/____/___/_____<O>_____\\___\\____\\=_',
    '<__o___o___o__[=======]___o___o___o__>',
    '   "\\___________|===|___________/"',
    '               "\\___/"',
)
BOMB = (
    '   ,*',
    '  /',
    ' _||_',
    '/    \\',
    '| () |',
    '\\____/',
)
ORACLE_FACE = (
    '      .-------.__',
    '   .-" /////     "-.',
    '  / //  /// ///     \\',
    ' |// /-----------.\\  |',
    ' || /  _____ _____\\| |',
    ' || | /_[#] V [#]_\\| |',
    '  | \\    .'+"'"+' v   /  |',
    ' /|  "-.  \\___/ ." |\\',
    '/ | /  _.>[===]<._ | \\',
    '   /__/[=]  |  [=]\\__\\',
)
EXPLOSION = (
    r'        \      |      /',
    r'     .---\---- | ----/---.',
    r' __--   .-*--====--*-.   --__',
    r'<====  <   B O O M !  >  ====>',
    ' ""--   \x60-*--====--*-\x60   --""',
    r'     \---/---- | ----\---/',
    r'        /      |      \ ',
)


def render(elapsed):
    c = Canvas()
    t = max(0, elapsed)
    if t < 2.02:
        for y in range(1,13):
            for x in range(2,55):
                if (x*13+y*17+int(t*8)) % 67 == 0:
                    c.put(x,y,'.','dim')
        x = 11-int(max(0,.8-t)*9)
        c.put(x,1,UFO,'green',opaque=True)
        c.put(1,0,'[ NECRONOMICON // AIR SUPPORT ]','green')
        c.put(1,14,' -------------------------------------- TARGET LOCK [*]','dim')
        for j in range(4):
            offset=8+j*2
            c.put(28-offset,7+j, '/', 'cyan')
            c.put(28+offset,7+j, '\\','cyan')
        if t < .86:
            c.put(24,11,'[ + + ]','red')
            return '01 / ORACLE TAKES OVER',c.finish()
        b_y = 5+int(((t-.86)/1.16)**1.8*4)
        c.put(26,b_y,BOMB,'gold',opaque=True)
        return '02 / PAYLOAD AWAY',c.finish()
    if t < 2.54:
        c.put(13,4,EXPLOSION,'flash',opaque=True)
        for x,y in ((8,8),(47,8),(11,3),(44,3),(7,11),(50,11)):
            c.put(x+int(t*10)%3,y,'*','red')
        return '03 / DIRECT HIT',c.finish()
    # Reference-inspired arcade victory poster with original layout and art.
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if x in (0,WIDTH-1) or y in (0,HEIGHT-1):
                c.put(x,y,'+' if x in (0,WIDTH-1) and y in (0,HEIGHT-1) else
                      '-' if y in (0,HEIGHT-1) else '|','green')
            elif (x-y*3) % 23 == 0:
                c.put(x,y,'/','dim')
    c.put(4,2,'[ ORACLE // ALL-IN ]','green')
    c.put(29,2,ORACLE_FACE,'green',opaque=True)
    # Put the mask accent at the same coordinate as the rest of the sprite.
    c.put(29,7,ORACLE_FACE[5],'white',opaque=True)
    c.put(5,5,('  ___ ___ _____', ' / __|_ _|_   _|',
                   '| (_ || |  | |', r' \___|___| |_|'),'gold',opaque=True)
    c.put(7,9,('  ___ _   _ ___', ' / __| | | |   \\',
                   '| (_ | |_| | |) |',r' \___|\___/|___/'),'gold',opaque=True)
    c.put(31,12,'>> PAYLOAD DELIVERED','cyan',opaque=True)
    if int(t*3)%2:
        c.put(49,2,'[+]','white')
    return '04 / ORACLE FINISHER',c.finish()


SCENES = {TITLE: (SECONDS,render)}
