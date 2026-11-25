"""The Bullet of Rebellion: an original packed-dot staging of Sinful Shell."""
from math import cos, sin, pi

from detail_canvas import DotCanvas

TITLE = 'SINFUL SHELL'
SECONDS = 2.75
TAU = 2*pi


def _ease(f):
    f = max(0., min(1., f))
    return f*f*(3-2*f)


class Shot:
    """Aspect-neutral blocks measured on the microdot surface."""
    def __init__(self, canvas, x, y, scale=1):
        self.c = canvas
        self.x, self.y = x, y
        self.s = min(canvas.w/155,canvas.h/100)*scale

    def xy(self,x,y):
        return self.x+x*self.s,self.y+y*self.s

    def shape(self, coords, ink, edge=None, density=8):
        self.c.face(tuple(self.xy(x,y) for x,y in coords),ink,density,edge)

    def line(self,a,b,ink):
        self.c.line(self.xy(*a),self.xy(*b),ink)

    def arc(self,x,y,rx,ry,ink,start=0,stop=TAU):
        self.c.ring(*self.xy(x,y),rx*self.s,ry*self.s,ink,start=start,stop=stop)

    def point(self,x,y,ink):
        x,y=self.xy(x,y)
        self.c.put(round(x),round(y),ink)


def _sky(c, t):
    w,h=c.w,c.h
    # Qliphoth threads arc behind the distant city and disappear into its haze.
    for i in range(9):
        x=w*(.07+i*.111)
        y=h*(.06+(i*11%5)*.025)
        r=w*(.06+i%4*.024)
        c.path([(x-r+k*r/8,y+k*k*.38-(10 if i%2 else 0)) for k in range(17)],'wine')
    for layer in range(2):
        steps=15 if layer else 20
        step=w/steps
        for i in range(steps+1):
            x=i*step-layer*3; end=x+step*(.76+.06*(i%4))
            roof=h*(.79-layer*.075-((i*211+7*layer)%12)*.009)
            base=h*(.925+layer*.065)
            c.face(((x,base),(x,roof+3),(x+step*.17,roof),(end-step*.19,roof),
                    (end,roof+4),(end,base)), 'wine',5 if layer else 2, 'red' if layer and i%4==2 else 'wine')
            if i%5==2:
                c.line((x+step*.5,roof),(x+step*.5,roof-h*.10),'rose')
                c.put(round(x+step*.5),round(roof-h*.10),'gold')
            # Office windows wake up in clusters as the crowd responds.
            y=round(roof+6)
            while y<base-2:
                for k in range(1,4):
                    if (i*17+y*7+k*5)%19 < (4+int(min(1.5,t)*7)) and x+k*step*.20<end:
                        sx=round(x+k*step*.20)
                        c.line((sx,y),(sx+1,y),'gold' if layer and (k+i+y)%7==0 else 'rose')
                y+=4
    for i in range(90):
        x=round((i*29+i*i*17+t*4*(i%3))%max(1,w))
        y=round((i*13+i*i*7)%max(1,h*.74))
        c.put(x,y,'rose' if i%13==0 else 'wine')


def _satanael(c, t, spread):
    q=Shot(c,c.w*.345,c.h*.4,1.2); phase=t*3.1
    # Three pairs of scalloped wing blades taper inward, not a single fan.
    for side in (-1,1):
        for i in (2,1,0):
            root=(-4+i*4,10+i*8)
            stem=(25+i*5,1+i*13)
            outer=(47-i*4, -43+i*31+sin(phase+i)*2)
            v=1.0 if side<0 else .92
            p=lambda x,y:(side*x*spread*v,y)
            facets=(p(*root),p(*stem),p(*outer),p(outer[0]-5,outer[1]+18),
                    p(outer[0]-9,outer[1]+11),p(stem[0]+5,stem[1]+17),
                    p(stem[0]-4,stem[1]+9),p(root[0]+7,root[1]+25))
            q.shape(facets,'slate' if i==1 else 'wine','rose' if i==0 else 'slate',4+i)
            for j in range(4):
                a=(j+1)/5
                q.line(p(root[0]+4*j,root[1]+j*3),
                       p(outer[0]-3-3*j,outer[1]+20*a),'navy' if i==1 else 'slate')
            q.line(p(*root),p(stem[0]+4,stem[1]),'wine')
    # Layered black armor, split longcoat, bright mask, and the two tall horns.
    q.shape(((-13,6),(-20,22),(-16,36),(-21,61),(-9,57),(0,42),
             (7,57),(20,62),(13,38),(17,21),(13,5),(4,0),(-5,0)),'navy','slate',6)
    q.shape(((-11,19),(-3,12),(3,12),(11,19),(8,25),(0,33),(-8,27)),'wine','rose',4)
    for side in (-1,1):
        q.shape(((side*10,10),(side*14,7),(side*17,10),(side*17,15),
                 (side*15,14),(side*14,18),(side*11,16)), 'slate','ochre',6)
        q.point(side*13,11,'white');q.point(side*16,11,'white')
    q.shape(((-10,10),(-6,10),(11,37),(20,43),(19,47),(10,44),(5,36)),
             'red','rose',5)
    q.line((-11,37),(-15,54),'rose');q.line((9,38),(16,55),'wine')
    q.shape(((-8,-15),(-12,-23),(-16,-34),(-12,-32),(-7,-24),(-2,-13),(2,-13),
             (7,-24),(11,-32),(15,-34),(12,-23),(9,-15)), 'slate','ochre',6)
    q.shape(((-9,-14),(-5,-20),(4,-20),(10,-14),(7,-5),(2,1),(-3,1),(-8,-6)),
             'navy','white',7)
    q.shape(((-8,-13),(-1,-10),(0,-7),(2,-9),(8,-13),(5,-7),(2,-5),(-2,-6),(-6,-8)),
             'white','rose',6)
    q.line((-1,-6),(1,-1),'slate')
    # The long fantastical firearm reads as part of the character silhouette;
    # the shot is cinematic, not a mechanical illustration.
    q.shape(((11,14),(21,9),(23,13),(31,10),(40,11),(39,17),(28,20),
             (21,19),(16,28),(11,25)),'slate','wine',7)
    q.shape(((23,10),(30,7),(48,8),(53,7),(54,13),(32,15),(27,21),
             (20,19)), 'wine','ochre',7)
    q.line((30,9),(52,9),'white');q.line((31,13),(51,11),'rose')
    q.arc(31,12,4,3,'ochre')
    return q.xy(54,10)


def _yaldabaoth(c, t, hit=0.):
    # Radial halo, nested ribs and the pale face inside the gold mask.
    q=Shot(c,c.w*.82,c.h*.45,.79+.25*hit)
    q.arc(0,-14,21,25,'ochre')
    q.arc(0,-14,19,23,'gold')
    for i in range(12):
        a=i*TAU/12
        q.line((20*cos(a),-14+24*sin(a)),(23*cos(a),-14+28*sin(a)),'ochre')
    for side in (-1,1):
        q.shape(((side*5,-10),(side*14,-6),(side*23,12),(side*13,7),(side*17,25),
                 (side*6,19),(side*4,34),(0,29)), 'ochre','gold',5)
        q.line((side*11,1),(side*16,13),'white')
        q.line((side*7,9),(side*11,23),'ochre')
    q.shape(((-8,-15),(-5,-23),(0,-27),(5,-23),(8,-15),(4,-6),(0,-2),(-4,-6)),
             'amber','white',6)
    q.shape(((-4,-18),(4,-18),(3,-12),(0,-8),(-3,-12)),
             'wine','gold',6)
    q.line((-4,-15),(-1,-15),'rose');q.line((1,-15),(4,-15),'rose')
    return q.xy(0,-14)


def render(_title,t,width,height):
    c=DotCanvas(width,height)
    if not width or not height:return 'city',c.finish()
    t=max(0.,min(SECONDS,t))
    _sky(c,t)
    if t<.45:
        return 'city',c.finish()
    spread=.22+.78*_ease((t-.43)/.68)
    muzzle=_satanael(c,t,spread)
    focus=_yaldabaoth(c,t)
    if t<1.60:
        return 'manifest',c.finish()
    if t<1.91:
        grow=_ease((t-1.60)/.31)
        c.ring(*muzzle,1+grow*8,2+grow*8,'gold')
        c.ellipse(*muzzle,1+grow*4,1+grow*5,'white',6)
        for j in range(15):
            a=TAU*j/15
            x,y=muzzle
            s=3+grow*(6+j%4)
            c.line((x+s*cos(a),y+s*sin(a)),(x+(s+4)*cos(a),y+(s+5)*sin(a)),'rose')
        return 'charge',c.finish()
    flight=_ease((t-1.91)/.23)
    mx,my=muzzle; hx,hy=focus
    x=mx+(hx-mx)*flight;y=my+(hy-my)*flight
    for i in range(-3,4):
        c.line((mx,my+i),(x,y+i*.3),'white' if abs(i)<2 else 'rose')
    c.ellipse(x,y,3,4,'white',8)
    if t>=2.12:
        p=_ease((t-2.12)/.57)
        r=5+c.w*.21*p
        c.ring(hx,hy,r,r*.85,'gold')
        c.ring(hx,hy,r*.73,r*.64,'rose')
        for i in range(27):
            a=TAU*i/27;d=r*(.4+(i*7%9)*.085)
            bx,by=hx+d*cos(a),hy+d*.82*sin(a)
            c.line((bx,by),(bx+(.10*r+i%5)*cos(a),by+(.08*r+i%5)*sin(a)),
                   'white' if i%5==0 else 'rose' if i%3 else 'ochre')
        c.ellipse(hx,hy,max(2,11-8*p),max(3,14-9*p),'white',7)
    return 'shell',c.finish()
