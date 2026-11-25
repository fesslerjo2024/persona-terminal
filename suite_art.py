"""Small terminal-cell art and title-specific highlight effects."""
from itertools import groupby
from math import cos, sin

from battle_ui import WHITE
from reel_palette import IDS
from suite_calling_cards import render_calling_card

PULSE_SECONDS = .72
OPEN_SECONDS = .40
TUMBLE_SECONDS = 1.25

DARK_HOUR_CLOCK = (
    '    ╭──12───╮    ',
    '  ╭─╯   │   ╰─╮  ',
    ' ╭╯ •   │   • ╰╮ ',
    ' 9      ●      3 ',
    ' ╰╮ •       • ╭╯ ',
    '  ╰─╮       ╭─╯  ',
    '    ╰───6───╯    ',
)

TUBE_TV = (
    '     ╲  ╱',
    '      ╲╱',
    '╭─────────────╮',
    '│ ╭───────╮ ◉ │',
    '│ │▒░▒░▒░▒│ • │',
    '│ ╰───────╯ ═ │',
    '╰─┬─────────┬─╯',
)


def emblem_runs(number,width,ink,elapsed=None):
    """Return seven rows of the selected icon in terminal-cell coordinates."""
    if number==5:
        p=elapsed/TUMBLE_SECONDS if elapsed is not None and 0<=elapsed<TUMBLE_SECONDS else None
        return render_calling_card(width,p)
    art=DARK_HOUR_CLOCK if number==3 else TUBE_TV
    height=7
    cells=[[(' ',ink) for _ in range(width)] for _ in range(height)]
    left=(width-max(map(len,art)))//2
    for y,line in enumerate(art):
        for x,ch in enumerate(line,left):
            if 0<=x<width and y<height:cells[y][x]=(ch,ink)

    def paint(x,y,ch,color,*,empty=False):
        if 0<=x<width and 0<=y<height and (not empty or cells[y][x][0]==' '):
            cells[y][x]=(ch,color)

    def glow(x,y,color):
        if 0<=x<width and 0<=y<height:
            ch,_=cells[y][x]
            if ch!=' ':paint(x,y,ch,color)

    def wind_clock(p):
        """Draw short and long hands from one pivot, ending vertically at 12."""
        cx,cy=left+8,3
        paint(cx,1,' ',ink)
        paint(cx,2,' ',ink)
        amount=min(1.,p/.78)
        eased=amount*amount*(3-2*amount)
        for angle,rx,ry,color in ((-.43*(1-eased),2.,1.3,IDS['teal']),
                                  (-1.66*(1-eased),5.,2.15,WHITE)):
            x1=cx+round(sin(angle)*rx)
            y1=cy-round(cos(angle)*ry)
            dx,dy=x1-cx,y1-cy
            steps=max(abs(dx),abs(dy))
            glyph='─' if dy==0 else '│' if dx==0 else '╲' if dx*dy>0 else '╱'
            for i in range(1,steps+1):
                paint(cx+round(i*dx/steps),cy+round(i*dy/steps),glyph,color)
        paint(cx,cy,'●',WHITE)
        for x,y in ((cx-1,0),(cx,0),(left+1,3),(left+15,3),(cx,6)):
            if p>.79:glow(x,y,WHITE)
        if .84<p<.97:
            paint(cx-5,1,'✦',WHITE,empty=True)
            paint(cx+5,1,'◦',IDS['teal'],empty=True)

    if elapsed is not None and 0<=elapsed<PULSE_SECONDS:
        if number==3:
            wind_clock(elapsed/PULSE_SECONDS)
        else:
            # The TV crackles and the rolling scan line settles.
            tick=int(elapsed*29)
            for y in (3,4,5):
                for x in range(left+3,left+10):
                    n=(x*7+y*13+tick*11)%11
                    fill='─' if y==3+tick%3 else ' ░▒▓'[n%4]
                    paint(x,y,fill,WHITE if n==5 else ink)

    result=[]
    for row in cells:
        out=[]
        x=0
        for color,run in groupby(row,key=lambda cell:cell[1]):
            text=''.join(ch for ch,_ in run)
            if text.strip():out.append((x,text,color))
            x+=len(text)
        result.append(tuple(out))
    return tuple(result)
