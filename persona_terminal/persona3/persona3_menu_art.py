"""Original 2×4 illustrations for the compact Persona 3 menu panels."""

from functools import lru_cache
from math import cos, sin, tau

from ..shared.detail_canvas import DotCanvas


class Plate:
    """Normalized drafting space for tiny viewports; draw at native microdots."""

    def __init__(self, canvas, sx=100, sy=60):
        self.c=canvas
        self.sx=(canvas.w-1)/sx
        self.sy=(canvas.h-1)/sy

    def p(self, a):
        x,y=a
        return x*self.sx,y*self.sy

    def path(self, ink, *pts):
        self.c.path(tuple(map(self.p,pts)),ink)

    def face(self, ink, density, edge, *pts):
        self.c.face(tuple(map(self.p,pts)),ink,density,edge)

    def disk(self, ink, density, edge, x, y, rx, ry):
        q,r=self.p((x,y))
        self.c.ellipse(q,r,rx*self.sx,ry*self.sy,ink,density,edge)

    def ring(self, ink, x, y, rx, ry, start=0, stop=tau):
        self.c.path(tuple(self.p((x+rx*cos(a),y+ry*sin(a))) for a in
                          (start+(stop-start)*i/40 for i in range(41))),ink)

    def rect(self, ink, density, edge, x, y, w, h):
        self.face(ink,density,edge,(x,y),(x+w,y),(x+w,y+h),(x,y+h))


def _tiles(p, y, left, right, columns, colors, bands):
    for r in range(bands):
        top=y+(60-y)*(r/bands)**1.5
        bot=y+(60-y)*((r+1)/bands)**1.5
        for j in range(columns):
            a=(j-columns/2)/columns
            b=a+1/columns
            def point(q,z):
                f=.27+.73*(z-y)/max(1,60-y)
                return ((left+right)/2+(right-left)*q*f,z)
            p.face(colors[(j+r)%2],5,None,point(a,top),point(b,top),
                   point(b,bot),point(a,bot))


def _thebel(p, hot, base, shine):
    # Gekkoukan's green windows and checkerboard stone become a deep hall.
    p.face(base,4,hot,(0,6),(22,14),(23,44),(0,57))
    p.face(base,4,hot,(100,5),(76,13),(76,45),(100,57))
    _tiles(p,37,0,100,10,(base,'dim'),6)
    for side in (-1,1):
        for i in range(3):
            x=50+side*(14+i*12)
            y=8+i*2
            height=20+i*4
            p.face('forest',6,base,(x-5,y+7),(x,y),(x+5,y+7),
                   (x+5,y+height),(x-5,y+height))
            p.path(hot,(x,y+3),(x,y+height-2))
            p.path(shine,(x-3,y+11),(x+3,y+11))
    p.face(base,7,hot,(25,53),(37,38),(37,29),(63,29),(63,38),(75,53))
    for i in range(5):
        y=31+i*4
        p.path(hot if i%2 else shine,(37-i*2.1,y),(63+i*2.1,y))
    p.path(shine,(35,28),(50,21),(66,28))


def _arqa(p, hot, base, shine, upper):
    # Glowing ribs and folded walls, with an oblique passage in upper Arqa.
    p.face(base,4,None,(0,0),(100,0),(66,29),(60,44),(100,60),(0,60),(41,36),(38,24))
    van=63 if upper else 43
    for lane in range(6,29,5):
        spread=lane*1.66
        y=(lane-6)*.51
        ridge=((van-spread-17,60),(van-spread,50-y),(van-spread*.83,20+y*.5),
               (van-spread*.29,y+4),(van+spread*.64,y+4),(van+spread*.87,17+y*.5),
               (van+spread*.78,48-y),(van+spread+10,60))
        p.path(base,*ridge)
        if lane%2:
            p.path(hot,*ridge[1:-1])
        for a,b in zip(ridge[1::2],ridge[2::2]):
            x=(a[0]+b[0])/2
            z=(a[1]+b[1])/2
            p.path(shine,(x-2,z),(x+1,z+2),(x+2,z-1))
    _tiles(p,38,0,100,8,(base,'dim'),5)
    for i in range(4):
        y=37+i*5
        p.path(hot,(van-i*6,y),(van+3+i*3,y+1),(van+12+i*4,y))


def _yabba(p, hot, base, shine, upper):
    p.face(base,4,hot,(0,2),(100,2),(90,12),(14,15))
    p.face(base,4,hot,(0,48),(100,48),(100,59),(0,59))
    p.rect('dim',8,base,36,8,29,32)
    for x in (6,24,74,92):
        p.rect(base,6,hot,x,12,5,36)
        for y in range(17,44,8):
            p.path(shine,(x,y),(x+5,y-2))
        p.path(base,(x+5,12),(x+11,25),(x+5,34))
    ys=(23,34,44) if upper else (19,31,44)
    for i,y in enumerate(ys):
        a,b=(0,100) if not upper else (0,48) if i%2 else (50,100)
        p.face(base,7,hot,(a,y),(b,y),(b-4,y+4),(a+3,y+4))
        for x in range(a+3,b-4,7):
            p.path(shine,(x,y+1),(x+4,y+1))
    for i in range(7):
        p.path(shine,(46-i,31+3.6*i),(58+i,31+3.6*i))
    for x in (14,87):
        p.path(base,(x,2),(x+7,7),(x+5,15))


def _tziah(p, hot, base, shine, upper):
    # The gilded galleries' raised central dais and circular floor inlay.
    p.ring(base,50,50,49,14)
    p.ring(shine,50,50,41,10)
    p.ring(base,50,50,34,6)
    for x in (12,24,76,88):
        y=5 if upper else 8
        p.face(base,6,hot,(x-5,y),(x+5,y),(x+4,y+6),
               (x+2,36),(x+5,37),(x+5,40),(x-5,40),(x-5,37),
               (x-2,36),(x-4,y+6))
        p.path(shine,(x-1,y+7),(x-1,34))
    p.face(base,5,hot,(20,10),(33,4),(67,4),(80,10),(73,14),(27,14))
    p.face(base,6,hot,(27,49),(38,34),(42,28),(58,28),(62,34),(73,49))
    if upper:
        p.ring(hot,50,24,12,11,2.70,6.70)
        p.face(shine,6,hot,(50,15),(55,23),(50,29),(45,23))
        p.path(shine,(0,23),(29,25),(38,19))
        p.path(shine,(62,19),(71,25),(100,23))
    else:
        for x in (8,92):
            p.face(base,7,hot,(x-4,41),(x-5,36),(x-4,32),
                   (x+4,32),(x+5,36),(x+4,41))
            p.path(shine,(x-4,34),(x+4,34))
    for i in range(4):
        p.path(shine,(39-i*2,34+i*4),(61+i*2,34+i*4))


def _harabah(p, hot, base, shine, upper):
    # Broken checkerboard and intersecting bands, not a literal kiln.
    _tiles(p,32,0,100,12,(base,'dim'),8)
    for side in (-1,1):
        tip=50+side*(13 if upper else 30)
        profile=((50+side*50,0),(50+side*30,5),(tip,20),
                 (50+side*20,31),(50+side*48,38),(50+side*50,42))
        p.face(base,5,hot,*profile)
        for i in range(4):
            p.path(shine if i%2==0 else hot,(50+side*46,i*9),
                   (50+side*(30+i*2),6+i*7),(tip+side*i*4,12+i*5))
    if upper:
        p.face(base,7,hot,(28,22),(43,14),(66,14),(76,22),(65,25),(39,25))
        p.face(base,6,shine,(28,42),(43,31),(70,31),(76,36),(61,42))
        p.path(hot,(35,54),(52,40),(56,37),(56,30),(62,25))
    else:
        p.ring(hot,50,28,15,18,-1.2,4.9)
        p.ring(shine,50,28,11,15,-1.2,3.0)
        p.path(hot,(35,31),(42,24),(43,31),(53,23),(58,25),(65,18))


def _adamah(p, hot, base, shine):
    # Near-monochrome pillars, spherical centerpiece and optical floor rings.
    for x in (5,17,28,72,83,95):
        p.face(base,6,'slate',(x-3,0),(x+3,0),(x+3,38),(x+6,46),(x-6,46),(x-3,38))
        p.path('white',(x-2,0),(x-2,40))
    for i in range(6):
        p.ring('white' if i%2==0 else 'slate',50,55,11+i*13,3+i*2.3)
    p.disk(base,7,'white',50,24,15,19)
    p.ring(hot,50,24,11,19)
    p.ring('white',50,24,5,19)
    p.ring('slate',50,24,15,7)
    p.ring('white',50,24,15,12)
    p.path(shine,(50,41),(50,48))


@lru_cache(maxsize=32)
def block_plate(block,w,h,colors):
    c=DotCanvas(w,h)
    p=Plate(c)
    hot,base,shine=colors
    if block=='thebel':_thebel(p,hot,base,shine)
    elif block in ('arqa','upper'):_arqa(p,hot,base,shine,block=='upper')
    elif block.startswith('yabba'):_yabba(p,hot,base,shine,block.endswith('_upper'))
    elif block.startswith('tziah'):_tziah(p,hot,base,shine,block.endswith('_upper'))
    elif block.startswith('harabah'):_harabah(p,hot,base,shine,block.endswith('_upper'))
    else:_adamah(p,hot,base,shine)
    return c.finish()


@lru_cache(maxsize=24)
def shuffle_plate(kind,w,h,enabled,selected):
    c=DotCanvas(w,h)
    p=Plate(c)
    low='navy' if enabled else 'dim'
    metal='gold' if selected and enabled else 'slate'
    light='white' if selected and enabled else 'cyan' if enabled else 'slate'
    shine='teal' if enabled else 'dim'
    p.ring(low,50,30,30,23)
    for r in (0,1):
        a,y=(20,13) if not r else (14,42)
        p.path(shine,(a,y),(a+4,y-3),(a+8,y))
        p.path(shine,(100-a-8,y),(100-a-4,y+3),(100-a,y))
    if kind=='persona':
        # A terminal-specific anonymous reflection, not an invented Persona.
        p.face(low,8,metal,(34,7),(50,4),(66,7),(73,15),(75,25),(72,36),
               (64,42),(61,49),(50,55),(39,49),(36,42),(28,36),(25,25),(27,15))
        p.face(shine,7,light,(29,16),(41,13),(51,18),(63,13),(71,16),(69,29),
               (64,33),(59,31),(50,41),(41,31),(36,33),(31,29))
        for x in (41,59):
            p.face(low,8,metal,(x-6,21),(x+5,23),(x+4,26),(x-4,27))
        p.path(light,(44,44),(50,47),(56,44))
        p.path(shine,(47,30),(50,26),(53,30))
    elif kind=='coin':
        # Faceted coin / jewel, with the silver tracery of Reload's arcana frame.
        p.disk(low,7,metal,50,30,23,24)
        p.ring(light,50,30,19,19)
        p.face(shine,7,light,(50,13),(63,26),(59,41),(50,47),(41,41),(37,26))
        p.face(metal,7,light,(50,16),(55,29),(50,40),(45,29))
        p.path(low,(38,26),(50,30),(62,26))
        p.path(light,(42,42),(50,36),(58,42))
    else:
        # Four-part silhouette: curved handles, cup bowl, neck and foot.
        for side in (-1,1):
            p.path(metal,(50+side*18,13),(50+side*28,13),(50+side*28,21),
                   (50+side*23,29),(50+side*15,30))
        p.face(shine,7,light,(30,10),(70,10),(67,26),(62,34),(56,39),
               (53,41),(53,49),(61,50),(65,54),(35,54),(39,50),(47,49),(47,41),
               (42,39),(37,35),(33,25))
        p.path(light,(36,17),(64,17))
        p.path(metal,(36,27),(44,29),(50,27),(56,29),(64,27))
        p.path(metal,(40,51),(60,51))
    return c.finish()


@lru_cache(maxsize=2)
def moon_medallion():
    c=DotCanvas(8,5)
    p=Plate(c)
    p.disk('teal',7,'cyan',50,30,37,27)
    p.face('navy',5,None,(29,17),(40,7),(49,6),(39,17),(33,31),(42,48),(53,56),
           (40,55),(24,43),(19,31))
    for x,y,r in ((45,16,8),(60,27,11),(42,35,5),(61,44,6),(75,23,4)):
        p.disk('slate',7,'navy',x,y,r,r*.75)
    p.ring('white',50,30,37,27,-1.7,.1)
    return c.finish()
