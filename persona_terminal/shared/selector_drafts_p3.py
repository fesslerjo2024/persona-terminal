"""Nine original microdot selector icon sketches for Persona 3."""
from math import cos, pi, sin, tau


class _Icon:
    """Draw in a viewbox suited to both the small tile and the draft viewer."""
    def __init__(self, canvas):
        self.c = canvas
        self.x = (canvas.w - 1) / 100
        self.y = (canvas.h - 1) / 100

    def xy(self, x, y):
        return x * self.x, y * self.y

    def line(self, *points, ink='cyan'):
        self.c.path(tuple(self.xy(*point) for point in points), ink)

    def face(self, *points, ink='navy', density=8, edge=None):
        self.c.face(tuple(self.xy(*point) for point in points), ink, density, edge)

    def box(self, x, y, w, h, ink='navy', density=8, edge=None):
        self.face((x, y), (x+w, y), (x+w, y+h), (x, y+h),
                  ink=ink, density=density, edge=edge)

    def disc(self, x, y, rx, ry, ink='navy', density=8):
        self.c.ellipse(*self.xy(x,y), *self.xy(rx,ry), ink, density)

    def arc(self, x, y, rx, ry, ink='cyan', a=0, b=tau):
        self.c.ring(*self.xy(x, y), *self.xy(rx, ry), ink, a, b)

    def dot(self, x, y, ink='cyan'):
        x, y = self.xy(x, y)
        self.c.put(round(x), round(y), ink)

    def star(self, x, y, r=3, ink='white'):
        self.line((x-r,y), (x+r,y), ink=ink)
        self.line((x,y-r*1.4), (x,y+r*1.4), ink=ink)


def _float(p):
    return sin(pi*p)


def draw_dark_hour_clock(c, p):
    s = _Icon(c)
    s.disc(52, 53, 27, 39, 'navy', 3)
    s.arc(50, 53, 28, 41, 'navy')
    s.arc(50, 53, 25, 37, 'cyan')
    s.arc(50, 53, 21, 31, 'slate')
    s.box(44, 2, 12, 5, 'navy', edge='cyan')
    s.line((47,7), (47,11), (53,11), (53,7), ink='white')
    for i in range(12):
        t = i*tau/12-pi/2
        short = 18 if i%3 else 15
        s.line((50+short*cos(t), 53+short*1.5*sin(t)),
               (50+20.5*cos(t), 53+30*sin(t)), ink='white' if i%3==0 else 'cyan')
    minute = (1-p)*tau*1.6-pi/2
    hour = -pi/2-.24-(1-p)*1.2
    for t,r,ink in ((minute,15,'white'),(hour,11,'cyan')):
        s.line((50-2*cos(t),53-3*sin(t)),
               (50+r*cos(t),53+r*1.5*sin(t)), ink=ink)
    s.disc(50,53,1.8,3, 'white')
    s.arc(50,53,30,44,'cyan',p*tau+.25,p*tau+1.4)
    s.star(79,24,2,'cyan')
    s.dot(18,71,'navy')


def _moon(c,p):
    s = _Icon(c)
    shift = 4 * _float(p)
    s.disc(50,49+shift,25,40,'navy',5)
    s.arc(50,49+shift,24,40,'cyan',.7,4.55)
    s.disc(60,41+shift,24,37,None)
    s.arc(60,41+shift,24,37,'white',1.18,4.15)
    s.arc(49,49+shift,19,32,'navy',1.3,3.98)
    for x,y in ((31,32),(33,55),(43,71),(48,77),(25,44)):
        s.dot(x,y+shift,'white')
    for x,y,r in ((62,23,2),(71,49,3),(75,76,2),(27,17,1)):
        s.star(x,y,r,'cyan' if r!=3 else 'white')
    gleam=2.3+2.1*p
    s.star(50+26*cos(gleam),49+40*sin(gleam)+shift,1.5,'white')


def _tower(c,p):
    s = _Icon(c)
    rise = (1-p)*9
    for x,y,rx,ry in ((51,20,15,15),(51,20,20,21)):
        s.arc(x,y,rx,ry,'navy',3.04,6.44)
    s.face((8,86),(18,79),(23,80),(24,61),(32,66),(37,78),(40,69),(38,60),
           (44,49),(42,44),(48,35),(45,31),(50,11+rise),(53,4+rise),
           (58,21+rise),(58,28),(62,40),(58,43),(66,55),(63,59),(73,70),
           (73,79),(81,77),(87,83),(93,86), ink='navy',density=6,edge='cyan')
    for y,left,right in ((32,47,57),(42,45,59),(53,44,62),(63,42,67),(75,37,73)):
        s.line((left,y),(54,y-2),(right,y),ink='navy' if y==32 else 'cyan')
        s.dot(54,y+1,'white')
    s.line((52,19+rise),(51,33),(54,47),(51,81),ink='white')
    s.line((17,90),(83,90),ink='navy')
    s.line((28,95),(72,95),ink='navy')
    s.star(73,27,2,'cyan')


def _coffin(c,p):
    s = _Icon(c)
    lift = 7 * _float(p)
    s.face((50,12),(72,28),(61,80),(48,91),(34,80),(28,32),ink='navy',density=5,edge='navy')
    s.face((43-lift,5),(56-lift,6),(69-lift,29),(58-lift,87),(43-lift,88),
           (32-lift,30),ink='navy',density=5,edge='white')
    s.line((44-lift,11),(55-lift,12),(63-lift,32),(54-lift,80),
           (45-lift,82),(37-lift,32),(44-lift,11),ink='cyan')
    s.line((50-lift,29),(50-lift,61),ink='cyan')
    s.line((43-lift,39),(57-lift,39),ink='cyan')
    for x,y in ((38,30),(58,30),(46,77),(53,77)):
        s.dot(x-lift,y,'white')
    s.arc(52,85,30,10,'navy',0,pi)
    s.arc(52,85,30,10,'cyan',p*2.3,p*2.3+.65)
    s.star(75,45,2,'cyan')


def _velvet(c,p):
    s = _Icon(c)
    s.face((24,17),(38,5),(62,5),(76,17),(76,92),(24,92),
           ink='navy',density=3,edge='cyan')
    s.face((28,23),(39,14),(61,14),(72,23),(72,87),(28,87),
           ink='navy',density=6,edge='white')
    s.box(31,31,38,53,None,edge='cyan')
    gap=2.2+((1-p)**2)*14
    s.box(32,32,max(0,18-gap),50,'navy',4,edge='cyan')
    s.box(50+gap,32,max(0,18-gap),50,'navy',4,edge='cyan')
    for y in (38,48,58,68,78):
        s.line((33,y),(49-gap,y),ink='slate')
        s.line((51+gap,y),(67,y),ink='slate')
    s.arc(50,25,7,4,'cyan',pi,2*pi)
    t=pi*(1.85-.72*p)
    s.line((50,25),(50+6*cos(t),25+4*sin(t)),ink='white')
    s.line((20,94),(80,94),ink='navy')
    s.dot(78,52,'white')


def _headphones(c,p):
    s = _Icon(c)
    s.arc(46,51,24,39,'navy',pi-.2,tau+.2)
    s.arc(46,51,22,36,'cyan',pi-.15,tau+.15)
    s.arc(46,51,17,30,'white',pi-.1,tau+.1)
    for x in (22,69):
        s.face((x-4,43),(x+5,42),(x+8,52),(x+6,70),(x+2,76),
               (x-5,73),(x-7,59),ink='navy',density=7,edge='cyan')
        s.line((x-3,48),(x-2,69),ink='white')
    s.line((65,76),(66,82),(72,89),(79,89),(82,85),(82,74),
           (88,69),(91,76),(89,88),(84,95),(77,95),ink='white')
    s.line((84,74),(87,73),(88,77),ink='cyan')
    for i in range(7):
        height=(5,10,16,22,14,9,4)[i]*(.6+.4*p)+3*sin(p*tau+i)
        x=34+i*4
        s.line((x,55-height/2),(x,55+height/2),ink='navy' if i%2 else 'cyan')


def _butterfly(c,p):
    s = _Icon(c)
    spread=.65+.35*p + .17*sin(p*2*tau)*_float(p)
    def pt(x,y,side):
        return 50+x*spread*side,y
    for side in (-1,1):
        for points,ink,density in (
            (((2,49),(9,25),(24,14),(36,17),(35,30),(26,45),(13,55),(4,59)), 'navy', 5),
            (((2,53),(16,51),(27,58),(29,75),(20,84),(9,77),(4,67)), 'navy', 6),
            (((6,48),(13,29),(24,20),(30,22),(23,37),(13,46)), 'cyan', 5),
            (((8,58),(18,56),(23,62),(23,72),(18,75),(12,69)), 'teal', 5),
        ):
            s.face(*(pt(x,y,side) for x,y in points),ink=ink,density=density,edge='cyan')
        for line in (((5,49),(15,40),(22,28)),((7,53),(19,49),(31,32)),
                     ((7,60),(17,66),(19,74)),((1,47),(4,37),(9,30))):
            s.line(*(pt(x,y,side) for x,y in line),ink='white')
        for x,y in ((21,22),(26,27),(25,33),(19,61),(21,66)):
            s.dot(*pt(x,y,side),'white')
    s.line((50,45),(50,66),(51,71),ink='white')
    s.dot(50,44,'white')
    s.star(15,67,2,'cyan')
    s.star(86,37,2,'cyan')
    s.dot(77,89,'navy')


def _armband(c,p):
    s = _Icon(c)
    s.arc(50,62,37,21,'navy',2.9,6.55)
    turn=7*_float(p)
    s.face((18,36+turn),(65,16),(81,24),(82,65-turn),(33,86),(16,74),
           ink='navy',density=6,edge='cyan')
    s.face((18,38+turn),(65,19),(79,26),(80,62-turn),(32,82),(18,72),
           ink='wine',density=8,edge='rose')
    s.line((18,42+turn),(65,22),(79,29),ink='white')
    s.line((18,69),(32,78),(80,60-turn),ink='white')
    # A tiny hand-drawn SEES stencil follows the fabric instead of a caption.
    stencil = ('011 111 111 011',
               '100 100 100 100',
               '010 110 110 010',
               '001 100 100 001',
               '110 111 111 110')
    for y,row in enumerate(stencil):
        for x,ch in enumerate(row):
            if ch=='1':
                left=25+x*3.2
                top=46+y*4.2-x*.99
                s.line((left,top),(left+1.4,top),ink='white')
    s.face((16,63),(11,62),(10,39),(17,32),(18,35),ink='navy',density=5,edge='cyan')
    s.star(86,67-25*_float(p),2,'cyan')
    s.arc(50,51,38,31,'cyan',0.75+2*p,1.25+2*p)


def _lyre(c,p):
    s = _Icon(c)
    s.arc(50,54,32,37,'navy',.25,2.94)
    s.arc(50,54,34,40,'navy',3.28,5.9)
    s.face((47,88),(38,77),(28,61),(25,45),(28,28),(34,19),
           (40,24),(38,31),(33,32),(33,51),(40,65),(50,77),(60,65),
           (67,51),(67,32),(62,31),(60,24),(66,19),(72,28),(75,45),
           (72,61),(62,77),(53,88),ink='navy',density=6,edge='cyan')
    s.box(33,34,34,4,'navy',edge='white')
    for i,x in enumerate((40,45,50,55,60)):
        y=63+(3-abs(2-i))*3
        wiggle=sin((p*5+i)*tau)*_float(p)*3
        s.line((x,38),(x+wiggle,51),(x,y),ink='white' if i%2==0 else 'cyan')
    s.face((43,65),(57,65),(54,77),(50,81),(46,77),ink='navy',density=7,edge='white')
    s.star(50,16,3,'white')
    s.arc(50,54,32,37,'white',.38+2*p,.68+2*p)
    s.star(75,19,2,'cyan')
    s.dot(19,72,'cyan')


DRAFTS = (
    ('Dark Hour Clock', draw_dark_hour_clock),
    ('Crescent Moon', _moon),
    ('Tartarus', _tower),
    ('Silent Coffin', _coffin),
    ('Velvet Elevator', _velvet),
    ('Makoto’s Headphones', _headphones),
    ('Blue Butterfly', _butterfly),
    ('S.E.E.S. Armband', _armband),
    ('Orpheus’s Lyre', _lyre),
)
