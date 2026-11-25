"""Makoto's cut-in: eight addressable dots per terminal cell, no font changes."""

from math import cos, pi, sin
from ..shared.wide_canvas import Canvas
from ..shared.detail_canvas import DotCanvas

# Local coordinates trace the glove-adjustment pose: torso, face planes,
# asymmetrical fringe, Epaulet/armband, cuffs and independently drawn fingers.
_PLANES=(
    ('navy',6,'teal',((0,110),(10,86),(35,74),(60,74),(78,79),(91,98),(100,113))),
    ('slate',4,'navy',((0,110),(11,90),(26,84),(39,90),(29,110))),
    ('teal',5,'navy',((62,77),(78,79),(91,98),(96,112),(72,110),(67,89))),
    ('white',7,'teal',((36,72),(51,77),(62,73),(63,91),(56,111),(36,111),(34,91))),
    ('teal',6,'navy',((46,84),(49,80),(53,85),(49,91),(53,112),(44,112))),
    ('navy',6,'cyan',((19,81),(33,75),(40,94),(35,111),(31,98),(24,96))),
    ('navy',6,'cyan',((63,75),(74,83),(69,100),(61,107),(63,94),(56,91))),
    ('red',7,'rose',((77,85),(85,87),(91,98),(82,100),(76,96))),
    ('slate',7,'navy',((38,61),(57,62),(58,72),(65,76),(53,83),(40,80),(33,74))),
    ('white',7,'teal',((23,26),(37,7),(59,7),(75,23),(75,43),(70,56),(58,68),(48,72),(33,63),(24,48))),
    ('slate',5,None,((23,26),(36,20),(38,39),(34,54),(48,72),(33,63),(24,48))),
    ('teal',5,None,((63,33),(74,30),(74,44),(66,51),(61,47))),
    ('white',8,'slate',((69,39),(77,36),(80,42),(77,50),(72,52))),
    ('navy',8,'cyan',((19,35),(20,19),(25,12),(34,7),(32,4),(54,1),(70,5),(82,17),(83,32),
                      (76,40),(73,31),(69,29),(71,42),(62,30),(59,41),(50,29),(42,48),
                      (41,37),(34,50),(27,42),(24,50),(21,42))),
    ('teal',7,None,((24,22),(28,14),(42,7),(57,6),(67,9),(47,12),(37,16),(29,27))),
    ('slate',5,None,((47,7),(59,5),(75,13),(80,23),(75,27),(68,17),(60,12))),
)
_GLOVE=(
    ('navy',7,'cyan',((23,101),(41,101),(50,92),(47,84),(40,83),(30,87),(17,95))),
    ('teal',7,'white',((40,93),(47,86),(57,81),(63,84),(69,91),(64,96),(58,95),(50,99))),
    ('slate',8,'white',((52,84),(56,79),(62,76),(65,78),(63,81),(60,84),(72,82),(75,85),
                      (74,89),(66,92),(57,91))),
    ('teal',7,'cyan',((61,100),(68,89),(74,86),(80,88),(84,94),(79,100),(71,101),(66,109))),
    ('white',7,'teal',((75,87),(81,90),(84,94),(82,98),(78,96),(73,91))),
    ('navy',7,'cyan',((82,92),(94,97),(99,111),(76,111),(73,102))),
)
_LINES=(
    ('navy',((52,43),(59,40),(63,41))),
    ('cyan',((55,45),(60,45))),
    ('navy',((62,43),(61,50),(64,53),(60,54))),
    ('slate',((49,59),(55,60),(62,58))),
    ('teal',((42,63),(47,65),(53,65))),
    ('teal',((40,13),(33,18),(29,28),(27,38))),
    ('slate',((57,10),(65,14),(72,21),(75,30))),
    ('navy',((76,39),(74,43),(76,45))),
    ('cyan',((76,49),(77,53),(76,57))),
    ('white',((78,87),(84,88),(86,92))),
    ('slate',((27,95),(37,92),(44,92))),
    ('navy',((59,84),(64,85),(69,84))),
    ('cyan',((66,95),(70,92),(75,91))),
    ('teal',((11,92),(16,86),(27,82))),
)


def detail_card(t,w,h):
    """New motion and portrait planes sampled on the subcell grid."""
    c=DotCanvas(w,h)
    W,H=c.w,c.h
    t=max(0,t)
    slide=max(0,1-t/.31)**3
    cx,cy=W*.68,H*.49
    radius=min(W*.43,H*.69)
    # Cropped circle and halftone field form Reload's screen-print composition.
    for y in range(H):
        for x in range(W):
            z=((x-cx)/radius)**2+((y-cy)/(H*.51))**2
            if .90<z<.94 and (x+y)%5<3:c.put(x,y,'cyan')
            elif z<.90 and (x*3+y*7)%23==0:c.put(x,y,'teal')
            elif (x-y*2)%83<2:c.put(x,y,'navy')
    for i in range(12):
        x=round(W*(.08+i*.073)); y=round(H*(.10+(i*17%49)/62))
        if (i+int(t*4))%4==0:
            c.line((x-3,y),(x+3,y),'teal');c.line((x,y-2),(x,y+2),'cyan')
    # Keep the physical proportions stable even when cells are wide or tall.
    sx=min(W*.57/101,H*.96/100) if w>=85 else W*.57/101
    sy=H*.91/112
    x0=W*.41 + W*.32*slide
    y0=H*.095 + H*.09*slide
    def project(points,dx=0,dy=0):
        return tuple((round(x0+x*sx+dx),round(y0+y*sy+dy)) for x,y in points)
    for ink,density,edge,points in _PLANES:
        c.face(project(points),ink,density,edge)
    glove_t=max(0,1-t/.59)
    dx=W*.055*glove_t;dy=H*.07*glove_t
    for ink,density,edge,points in _GLOVE:
        c.face(project(points,dx,dy),ink,density,edge)
    for i,(ink,points) in enumerate(_LINES):
        placement=project(points,dx,dy) if i in (10,11,12) else project(points)
        for a,b in zip(placement,placement[1:]):c.line(a,b,ink)
    if .27<t<.54:
        f=(t-.27)/.27
        x,y=project(((63,83),),dx,dy)[0]
        for i in range(6):
            angle=i*pi/3
            a=round(4+8*f);b=round(7+14*f)
            c.line((x+round(a*cos(angle)),y+round(a*sin(angle))),
                   (x+round(b*cos(angle)),y+round(b*sin(angle))),'cyan' if i%2 else 'white')
    if t<.26:
        cut=round(W*(.16+2.9*t))
        for j in range(3):c.line((cut+j*6,0),(cut-W//7+j*6,H-1),'cyan')
    return c.pack()
