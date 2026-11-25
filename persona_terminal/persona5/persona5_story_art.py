"""Read-only, scene-specific microdot illustrations for Persona 5 interludes."""
from math import pi, tau

from ..shared.detail_canvas import DotCanvas
from ..shared.reel_palette import IDS

_INK={'red':1,'gold':2,'cyan':3,'white':4,'dim':5,'green':6,**IDS}


class View:
    """Draw local 100×100 planes at the actual panel dimensions."""
    def __init__(self,w,h):
        self.c=DotCanvas(w,h);self.w=w;self.h=h
        self.sx=(self.c.w-1)*.01;self.sy=(self.c.h-1)*.01

    def p(self,xy):return round(xy[0]*self.sx),round(xy[1]*self.sy)

    def plane(self,ink,points,d=8,edge=None):
        self.c.face(tuple(self.p(q) for q in points),ink,d,edge)

    def line(self,ink,*points):
        self.c.path(tuple(self.p(q) for q in points),ink)

    def disk(self,ink,x,y,rx,ry,d=8,edge=None):
        self.c.ellipse(*self.p((x,y)),rx*self.sx,ry*self.sy,ink,d,edge)

    def arc(self,ink,x,y,rx,ry,a=0.,b=tau):
        self.c.ring(*self.p((x,y)),rx*self.sx,ry*self.sy,ink,a,b,44)

    def point(self,ink,x,y):
        self.c.put(*self.p((x,y)),ink)


def draw(app,painter,x,y,w,h,**kwargs):
    # A plate never draws into framing, a footer, or across its requested
    # crop. The calling surface draws text and buttons separately.
    w=min(w,app.w-x-2);h=min(h,app.h-y-3)
    if w<10 or h<4:return
    v=View(w,h);painter(v,**kwargs)
    for row,runs in enumerate(v.c.finish(),y):
        left=x
        for mark,ink in runs:
            if mark.strip():app.put(row,left,mark,_INK[ink])
            left+=len(mark)


def press(v,opening,failed):
    # Press-cycle staging is legible without color: the piston travels up,
    # leaving a physically open passage over a perspective catwalk.
    hue='green' if opening else 'amber' if failed else 'red'
    v.plane('navy',((0,14),(47,4),(100,11),(99,100),(0,100)),5,'teal')
    for x in (6,22,78,94):
        v.plane('teal',((x,11),(x+3,8),(x+3,89),(x,91)),7,'navy')
        for yy in (24,44,64):v.line('navy',(x,yy),(x+3,yy+5))
    v.plane('slate',((19,12),(25,2),(74,2),(82,12),(78,22),(23,22)),6,'cyan')
    y=31 if opening else 66
    v.plane('navy',((45,18),(55,18),(56,y-4),(43,y-4)),8,'cyan')
    for yy in range(25,y-3,6):v.line('teal',(44,yy),(55,yy+2))
    v.plane('slate',((31,y-6),(38,y-13),(64,y-13),(71,y-7),(70,y+7),(30,y+7)),7,hue)
    v.line(hue,(31,y+5),(70,y+5))
    v.plane('navy',((0,78),(30,76),(43,68),(61,68),(77,76),(100,80),(100,99),(0,99)),7,hue)
    v.line('cyan',(1,90),(30,87),(44,74),(59,74),(76,86),(98,90))
    if opening:
        for i in range(6):v.line('green',(39+i*5,79),(36+i*6,89))
    else:
        for i in range(7):v.line(hue,(28+i*8,82),(32+i*8,91))
    for x in (11,87):
        v.disk('navy',x,33,6,15,8,'slate')
        v.disk(hue,x,31,2.5,6,7,'white')


def slot(v,hub=False,bypassed=(),jackpot=False):
    """Heavy cabinet, separate reel collars, two physically distinct lamps."""
    v.plane('wine',((9,99),(10,18),(16,6),(83,6),(90,19),(91,98)),7,'gold')
    v.plane('navy',((18,35),(83,35),(82,78),(17,78)),8,'ochre')
    v.arc('amber',50,18,30,12,pi,tau)
    glow='gold' if jackpot else 'slate'
    for i in range(3):
        x=32+i*18
        v.plane('slate',((x-8,38),(x+8,38),(x+9,72),(x-9,72)),6,'ochre')
        v.disk('navy',x,55,8,15,8,glow)
        v.arc(glow,x,55,5,10,0,tau)
    for i in range(9):v.disk('amber',13+i*9,87,1.5,3,6)
    for i,ink in enumerate(('red','green')):
        x=44+12*i
        v.disk('navy',x,19,4,6,8,'ochre')
        v.disk(ink if hub and ink not in bypassed else 'slate',x,19,2,3,7)
    v.line('rose',(92,53),(97,53),(98,30))
    v.disk('gold',98,29,2.0,5,7,'white')


def lab_bridge(v,blue):
    # Both doors are visible, but just one uninterrupted traffic span is.
    for i in range(4):
        y=22+i*14
        v.line('navy',(2,y+11),(39,y-9),(68,y+6),(98,y+5))
        v.line('slate',(8,y+14),(30,y+7))
    for x,ink in ((14,'wine'),(85,'navy')):
        v.plane(ink,((x-10,69),(x-10,27),(x-6,14),(x+4,13),(x+10,23),(x+10,68)),
                7,'red' if x<50 else 'teal')
        v.plane('navy',((x-6,66),(x-5,27),(x-1,20),(x+5,26),(x+5,65)),8,
                'wine' if x<50 or not blue else 'cyan')
        if x<50 or not blue:
            for n in range(3):v.line('red' if x<50 else 'slate',(x-5,34+n*12),(x+5,34+n*12))
    v.plane('slate',((37,91),(40,72),(48,60),(58,63),(65,74),(65,91)),6,'cyan')
    v.line('teal',(37,92),(65,92))
    if blue:
        v.plane('teal',((57,69),(75,57),(83,51),(87,57),(77,67),(63,83)),6,'cyan')
        for x,y in ((60,71),(67,65),(73,60),(79,56)):
            v.line('white',(x,y),(x+3,y+8))
        v.line('cyan',(60,79),(63,83),(63,88))
        v.line('wine',(19,58),(27,64));v.line('wine',(34,70),(41,74))
    else:
        v.plane('wine',((17,51),(25,55),(44,67),(43,77),(36,79),(27,70),(15,63)),7,'red')
        for x,y in ((18,57),(24,59),(30,63),(36,67)):
            v.line('red',(x,y),(x-1,y+8))
        v.line('slate',(60,77),(66,71));v.line('slate',(76,62),(82,57))
    # The entry switch is on the near platform; this is a drawing, not a hitbox.
    v.plane('navy',((46,79),(47,70),(52,69),(55,76),(52,81)),8,'teal')
    v.disk('cyan' if blue else 'red',50,74,2,4,8,'white')
