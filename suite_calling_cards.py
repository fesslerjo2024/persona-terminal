"""The launcher’s Tumbling Card, drawn in native terminal cells."""
from itertools import groupby
from math import cos, pi, sin

from battle_ui import RED, WHITE
from reel_palette import IDS

# Hat, mask and red rings echo the full-size calling-card intro.
TUMBLING_CARD = (
    '      ╭─────────╮',
    '    ╱  ╭▄▄▄─╮  ╱',
    '   ╱  (▀▀▀▀▀) ╱',
    '  ╱  ( ◥ ▴ ◤)╱',
    ' ╱    ╰───╯ ╱',
    '╭──────────╯',
    '',
)

_HAT_MASK = frozenset('▄█▀◥◤▴')
_RINGS = frozenset('( )◜')
_RAIL = frozenset('╭╯─│╰╮╱')


def render_calling_card(width,progress=None):
    """Render seven rows of compact art, including an unchanging resting pose."""
    c=[[' ',RED] for _ in range(width*7)]
    left=(width-17)//2

    def put(x,y,ch,ink=RED):
        x+=left
        if 0<=x<width and 0<=y<7:c[y*width+x]=[ch,ink]

    def face(stencil,dx=0,dy=0,scale=1.,printed=True,lighter=False):
        for y,row in enumerate(stencil):
            occupied=[x for x,ch in enumerate(row) if ch!=' ']
            for x,ch in enumerate(row):
                mark=round(8+(x-8)*scale)+dx
                if ch==' ':
                    if occupied and occupied[0]<x<occupied[-1] and scale>.60:
                        # Red halftone is confined to the inked page, shaped
                        # by contours around the central hat and mask.
                        r=round(((x-7.5)**2+((y-3.5)*1.95)**2)**.5)
                        if r in (3,5,7) and (x+y)%2:put(mark,y+dy,'·',IDS['wine'])
                    continue
                if not printed and ch not in _RAIL:
                    if (x+y*3)%4==1:put(mark,y+dy,'·',IDS['rose'])
                    continue
                color=WHITE if ch in _HAT_MASK else IDS['wine'] if ch in _RINGS else RED
                if lighter and ch in _RAIL:color=IDS['rose']
                put(mark,y+dy,ch,color)

    p=1. if progress is None else progress
    # Edge-on to front face, turning end over end on the diagonal.
    if p<.73:
        f=p/.73
        width_scale=max(.06,abs(cos((1-f)*pi*1.6)))
        dx=round((1-f)*-4)
        dy=-round(sin(f*pi)*2)
        face(TUMBLING_CARD,dx,dy,width_scale,printed=f>.51,lighter=True)
        for i in range(4):
            put(round(2+f*10)-i*2,5+i%2,'╱' if i<2 else '·',
                IDS['rose'] if i<2 else IDS['wine'])
    else:
        face(TUMBLING_CARD)
        if p<.95:
            put(round(11+(p-.73)*16),1,'✦',WHITE)
            put(3,5,'·',IDS['rose'])
    rows=[]
    for y in range(7):
        x=0; row=[]
        for ink,run in groupby(c[y*width:(y+1)*width],key=lambda cell:cell[1]):
            text=''.join(cell[0] for cell in run)
            if text.strip():row.append((x,text,ink))
            x+=len(text)
        rows.append(tuple(row))
    return tuple(rows)
