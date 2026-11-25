"""Nine selectable Persona 5 emblems drawn on the shared packed-dot canvas."""
from math import cos, pi, sin


def _ease(x):
    x=max(0.,min(1.,x))
    return x*x*(3.-2.*x)


class _Icon:
    """Keep the same silhouette at 26×11 and its compact 21×9 fallback."""
    def __init__(self,c,p):
        self.c=c;self.p=p
        self.a=(c.w-1)/51; self.b=(c.h-1)/43
    def pt(self,coord):
        x,y=coord;return x*self.a,y*self.b
    def line(self,ink,*p):
        self.c.path(tuple(map(self.pt,p)),ink)
    def shape(self,ink,*p,edge=None,grain=8):
        self.c.face(tuple(map(self.pt,p)),ink,grain,edge)
    def box(self,x,y,X,Y,ink,edge=None):
        self.shape(ink,(x,y),(X,y),(X,Y),(x,Y),edge=edge)
    def oval(self,x,y,rx,ry,ink,edge=None,grain=8):
        self.c.ellipse(*self.pt((x,y)),rx*self.a,ry*self.b,ink,grain,edge)
    def ring(self,x,y,rx,ry,ink,start=0,end=2*pi,steps=36):
        self.c.ring(*self.pt((x,y)),rx*self.a,ry*self.b,ink,start,end,steps)
    def speck(self,x,y,ink):
        xx,yy=self.pt((x,y));self.c.put(round(xx),round(yy),ink)


def _comet(s,x,y,l,ink='red'):
    s.shape(ink,(x,y),(x+l,y-4-l*.14),(x+l-4,y-1-l*.14),(x+2,y+1))


def _flecks(s,p,positions,ink='rose'):
    for i,(x,y) in enumerate(positions):
        drift=(1-p)*(3+i%5)*(-1 if i%2 else 1)
        s.shape(ink if i%4 else 'white',(x+drift,y),(x+drift+1.7,y-1.3),
                (x+drift+2.5,y+.3),(x+drift+.6,y+1.4))


def _mask(s,x,y,k=1.0,angle=0,p=1,ornate=False):
    """White eye mask with raised outer wings, faceted nose and two eye cuts."""
    co,si=cos(angle),sin(angle)
    def pt(a,b):return x+k*(a*co-b*si), y+k*(a*si+b*co)
    def poly(ink,*points,edge=None):s.shape(ink,*(pt(a,b) for a,b in points),edge=edge)
    def line(ink,*points):s.line(ink,*(pt(a,b) for a,b in points))
    wing=2.7*(1-_ease(p))
    poly('white',(-19,-7-wing),(-13,-4),(-8,-7),(-2,-1),(0,-3),(3,-2),
         (7,-7),(12,-4),(19,-8-wing),(17,1),(13,6),(8,8),(4,7),(0,11),
         (-4,7),(-9,8),(-14,6),(-18,1),edge='slate')
    for a in (-1,1):
        poly('ink',(a*15,-2),(a*11,-2.2),(a*4,0),(a*5,3),(a*9,5),
             (a*12,3),(a*15,-.5))
        line('red',(a*13,0),(a*10,1),(a*7,1))
        line('white',(a*16,-3),(a*10,-4),(a*5,-2))
        line('slate',(a*15,5),(a*11,7),(a*7,7),(a*4,5))
        if ornate:
            line('rose',(a*19,-6),(a*15,-6),(a*11,-8),(a*9,-7))
            line('red',(a*14,6),(a*10,9),(a*7,9))
    poly('slate',(-2,4),(0,1),(2,4),(0,9),edge=None)


def _crest(s,x,y,k=1.0):
    """Phantom thief topper and mask, suited to the calling card centerpiece."""
    def p(a,b):return x+a*k,y+b*k
    s.shape('ink',p(-16,-4),p(-11,-7),p(-9,-14),p(7,-15),p(11,-13),
            p(11,-7),p(17,-5),p(15,-2),p(-13,-2),edge='white')
    s.shape('slate',p(-8,-9),p(10,-9),p(11,-6),p(-11,-6))
    s.line('white',p(-15,-4),p(14,-4))
    _mask(s,x,y+4*k,k*.82,angle=-.04)


def _card(s,x,y,scale,angle,design,flip=1):
    ca,si=cos(angle),sin(angle)
    def q(a,b):return x+scale*(a*flip*ca-b*si), y+scale*(a*flip*si+b*ca)
    def poly(ink,*points,edge=None,grain=8):s.shape(ink,*(q(a,b) for a,b in points),edge=edge,grain=grain)
    def line(ink,*points):s.line(ink,*(q(a,b) for a,b in points))
    poly('umber',(-18,-12),(18,-12),(19,11),(-17,12),edge='wine')
    poly('red',(-20,-14),(18,-14),(18,9),(-20,9),edge='rose')
    poly('wine',(-18,-12),(16,-12),(16,7),(-18,7),edge='umber',grain=5)
    if abs(flip)>.45:
        for r in ((10.1,15.4) if design=='envelope' else (8.1,12.5,16.4)):
            line('red',*((r*cos(j*pi/20)-1,r*.56*sin(j*pi/20)-2) for j in range(41)))
        if design=='envelope':
            poly('umber',(-17,-11),(-1,3),(15,-11),edge='red')
            line('rose',(-17,-11),(-1,2),(15,-11))
            line('slate',(-16,7),(-6,-1))
            line('slate',(15,7),(5,-1))
            u,v=q(-1,0);s.oval(u,v,6.9*scale,5.8*scale,'red',edge='rose')
            u,v=q(-1,0);_mask(s,u,v,scale*.33,angle)
        else:
            u,v=q(-.5,-1)
            _crest(s,u,v,scale*(.63 if design=='open' else .53))
    for a in (-1,1):
        line('rose',(a*16,-10),(a*16,-12),(a*13,-12))
        line('rose',(a*16,5),(a*16,7),(a*13,7))


def _dagger(s,x,y,angle,k):
    """Blade tip anchors to the card; its beveled edge reads at narrow size."""
    def pt(a,b): return x+k*(a*cos(angle)-b*sin(angle)),y+k*(a*sin(angle)+b*cos(angle))
    def poly(ink,*pts,edge=None):s.shape(ink,*(pt(*u) for u in pts),edge=edge)
    def line(ink,*pts):s.line(ink,*(pt(*u) for u in pts))
    poly('white',(0,0),(-8,-2),(-20,-2.3),(-23,-.5),(-21,2),(-8,2.1),edge='slate')
    poly('slate',(-1,0),(-18,.7),(-21,2),(-8,2))
    line('rose',(-3,-.8),(-18,-1),(-21,-.4))
    poly('umber',(-23,-4),(-25,-5),(-25,4),(-23,5),edge='rose')
    poly('ink',(-25,-2),(-33,-2.2),(-35,-1),(-34,2),(-25,1.5),edge='slate')
    for i in range(4):line('red',(-26-i*1.7,-1.9),(-27-i*1.7,1.4))
    return pt(0,0)


def draw_pinned_calling_card(c,p):
    s=_Icon(c,p); f=_ease(p/.63); j=_ease((p-.36)/.48)
    _comet(s,1,35,23,'wine');_comet(s,35,40,14)
    _card(s,26-8*(1-f),26+4*(1-f),.98,-.20+.32*(1-f),'pin',max(.14,f))
    tip=_dagger(s,36+(1-j)*17,18-(1-j)*15,2.44+(.6*(1-j)),.92)
    if .65<p<.96:
        u,v=tip;r=3+10*(p-.65)
        for a in (-2,-1,.4,1.1):s.line('rose',(u+r*cos(a),v+r*sin(a)),(u+(r-3)*cos(a),v+(r-3)*sin(a)))
    _flecks(s,p,((5,10),(48,36),(4,31),(44,13)))


def _sealed(c,p):
    s=_Icon(c,p); f=_ease(p/.72)
    s.ring(26,22,22,17,'red',-2.4,4.63)
    s.ring(26,22,24,19,'wine',-1.15,2.5)
    coil=sin(p*pi)*4
    _card(s,26,25-coil,1.10,-.05+.13*(1-f),'envelope',max(.17,f))
    _flecks(s,p,((8,10),(43,7),(6,38),(47,36),(26,5)),'red')


def _heist(c,p):
    s=_Icon(c,p); f=_ease(p/.69)
    s.shape('umber',(0,14),(38,2),(50,6),(50,11),(15,38),(0,40))
    for j in range(4):_comet(s,2+j*8,38-j*9,14+j*4,'wine')
    for dx,dy,angle in ((4,5,-.46),(-5,3,.17)):
        _card(s,26+dx*f,24+dy*f,.80,angle,'blank',.86)
    z=.23+(1-.23)*f
    _card(s,27,24-6*sin(p*pi),1.16,-.32+.38*(1-f),'open',z)
    _flecks(s,p,((2,18),(48,18),(47,33),(5,35),(35,4)))


def _wanted_mask(c,p):
    s=_Icon(c,p); f=_ease(p/.70)
    s.oval(25,22,18,13,'umber',grain=4)
    s.ring(25,22,21,16,'red',0,2*pi)
    s.ring(25,22,24,19,'wine',-2.9,.82)
    s.ring(25,22,24,19,'rose',.81,1.62)
    for j in range(4):
        a=pi*.50*j
        s.line('red',(25+21*cos(a),22+17*sin(a)),(25+24*cos(a),22+20*sin(a)))
    _mask(s,25,22,max(.41,f)*1.10,-.14+.44*(1-f),f,True)
    _flecks(s,p,((3,12),(45,11),(46,32),(8,34)))


def _wildcard(c,p):
    """A staged unmasking: silhouette, separate glove, and knocked-off mask."""
    s=_Icon(c,p); f=_ease(p/.84)
    s.shape('red',(0,32),(49,2),(51,9),(49,14),(8,41),(0,40))
    s.shape('wine',(2,38),(46,10),(47,12),(20,39),(10,41),grain=4)
    s.shape('ink',(6,36),(8,22),(13,10),(22,5),(30,6),(36,9),(39,16),(35,18),
            (33,26),(26,29),(27,37),(32,42),(1,42),edge='slate')
    s.shape('slate',(13,23),(18,12),(23,8),(30,8),(35,12),(29,13),(23,12),
            (20,18),(16,22))
    s.shape('wine',(15,42),(18,32),(26,30),(30,34),(33,42),edge='red')
    s.shape('wine',(21,23),(28,19),(32,18),(30,24),(28,27),(23,29),(20,26))
    s.line('white',(21,23),(26,21),(29,22))
    s.line('rose',(29,22),(30,25),(27,25),(26,27))
    dy=(1-f)*11;dx=(1-f)*13
    s.shape('red',(33-dx,42),(32-dx,34),(36-dx,29+dy),(35-dx,24+dy),(36-dx,22+dy),
            (39-dx,23+dy),(42-dx,30+dy),(48-dx,31+dy),(48-dx,37),(41-dx,42),edge='rose')
    _mask(s,37-dx,16+dy,.64,-.43+.58*(1-f),f)
    _flecks(s,p,((43,6),(48,14),(4,24),(46,27)))


def _navigator(c,p):
    s=_Icon(c,p); f=_ease(p/.77)
    for i in range(4):
        s.line('wine',(2,37-i*9),(46,2+8*i))
    s.ring(27,23,18,15,'wine',.5,5.7)
    s.ring(27,23,21,18,'red',-.2,1.4)
    dx=(1-f)*13;dy=(1-f)*17
    def pt(x,y):return (x-dx+.17*(y-20),y+dy)
    def poly(ink,*pts,edge=None):s.shape(ink,*(pt(*a) for a in pts),edge=edge)
    poly('ink',(15,6),(31,4),(36,7),(37,33),(34,38),(19,40),(15,37),edge='slate')
    poly('red',(17,8),(32,6),(35,8),(35,33),(33,35),(19,37),(17,34),edge='rose')
    poly('umber',(19,10),(32,8),(33,29),(19,31))
    s.line('rose',pt(19,29),pt(32,27),pt(33,28))
    s.line('ink',pt(22,7),pt(27,6.5))
    x,y=pt(26,20)
    for r in (4.5,6.5):s.ring(x,y,r,r,'red' if r>5 else 'rose')
    s.shape('white',(x-6,y),(x-2,y-3),(x+2,y-3),(x+6,y),(x+2,y+3),(x-2,y+3),edge='rose')
    s.oval(x,y,2.4,2.6,'umber',edge='red');s.oval(x+.4,y,.8,1.2,'ink')
    s.line('white',pt(24,34),pt(28,33.5))
    _flecks(s,p,((11,12),(41,10),(40,23),(43,32),(11,30)))


def _mementos(c,p):
    s=_Icon(c,p); f=_ease(p/.65)
    s.shape('umber',(0,31),(0,16),(8,3),(18,0),(35,0),(45,5),(51,16),
            (51,31),(35,28),(17,28),edge='wine')
    for i in range(4):
        s.ring(25.5,22,10+i*3.9,9+i*3.3,'red' if i%2 else 'wine',-.98*pi,-.03*pi,20)
    s.shape('indigo',(0,43),(18,29),(35,29),(51,43),edge='wine')
    for a in (-1,1):
        s.line('red',(25+a*5,30),(25+a*24,43))
        s.line('rose',(25+a*6,30),(25+a*26,43))
    for j in range(4):s.line('wine',(15-j*5,34+j*3),(36+j*5,34+j*3))
    k=.22+f*.78;x=25.7;y=26-5*(1-f)
    def pt(a,b):return x+a*k,y+b*k
    def poly(ink,*pts,edge=None):s.shape(ink,*(pt(*a) for a in pts),edge=edge)
    poly('ink',(-15,8),(-14,-6),(-11,-13),(-5,-14),(8,-14),(13,-10),
         (15,7),(12,12),(-12,12),edge='rose')
    poly('teal',(-10,-10),(9,-10),(11,-3),(-11,-3),edge='slate')
    poly('gold',(-2,-13),(2,-13),(2,8),(-2,8),edge='ochre')
    for a in (-1,1):
        u,v=pt(a*8.7,3)
        if f>.45:s.shape('amber',(u-1,v+1),(u+1,v+1),(u+a*7,v+10),(u+a*12,v+12),grain=2)
        s.oval(u,v,2.7*k,2.2*k,'white',edge='amber')
        u,v=pt(a*10,11);s.oval(u,v,2.6*k,3.7*k,'ink',edge='slate')
    s.line('white',pt(-6,8),pt(7,8))


def _arsene(c,p):
    s=_Icon(c,p); f=_ease(p/.79)
    s.ring(25.5,21,20,18,'red',-2.6,3.43)
    s.ring(25.5,21,22,20,'wine',-2.0,2.63)
    for a in (-1,1):
        def q(x,y):return (25.5+a*(x*(.4+.6*f)),y+(1-f)*6)
        for i in range(4):
            j=i*2.1
            s.shape('ink',q(3,24+j),q(18+j*.95,5+j*1.64),q(24.8,4+j*2.4),
                    q(22-j*.45,12+j*2.2),q(21-j*.7,18+j*.8),q(14-j*.24,19+j*1.1),
                    q(5,31+j*.9),edge='wine')
            s.line('red' if i%2 else 'rose',q(7,26+j),q(16+j*.5,13+j*1.14),q(20+j*.09,8+j*1.25))
    s.shape('ink',(20,28),(24,21),(29,21),(32,28),(34,38),(30,42),(26,37),
            (22,42),(18,39),edge='red')
    s.shape('red',(21,19),(25,15),(29,16),(31,22),(28,27),(25,29),(22,24),edge='rose')
    s.shape('ink',(17,17),(20,16),(22,7),(32,6),(31,14),(34,15),(33,18),(18,19),edge='rose')
    s.line('white',(23,21),(25,22));s.line('white',(28,21),(30,20))
    s.line('wine',(21,31),(25,34),(28,32),(31,28))
    _flecks(s,p,((4,33),(43,36),(5,13),(44,8)))


def _casino(c,p):
    s=_Icon(c,p); f=_ease(p/.69)
    for j in range(4):_comet(s,5+j*6,37-j*7,14+j*3,'wine' if j%2 else 'red')
    for i in range(3):
        ang=.44*(i-1)*f+.23; dx=(i-1)*11*f
        def q(a,b):return 24+dx+a*cos(ang)-b*sin(ang),19+a*sin(ang)+b*cos(ang)
        s.shape(('ink','umber','ink')[i],q(-9,-11),q(9,-11),q(9,11),q(-9,11),edge='rose' if i!=1 else 'white')
        s.shape('red',q(0,-5),q(4,0),q(0,5),q(-4,0),edge='wine')
        s.line('slate',q(-7,-10),q(7,-10),q(8,-3))
        for a in (-1,1):
            s.line('rose',q(-a*7,a*7),q(-a*6,a*9),q(-a*4,a*7))
    for j in range(3):
        y=35+j*2.45
        s.oval(33,y,12,4.6,'umber',edge='red')
        s.ring(33,y,10,3.5,'rose',0,pi,22)
    y=33-7*sin(pi*p)*f
    s.oval(34,y,12,5,'red',edge='rose')
    s.ring(34,y,8,3.5,'white')
    for i in range(8):
        a=i*pi/4
        s.line('white',(34+cos(a)*9.7,y+sin(a)*4.0),(34+cos(a)*11.9,y+sin(a)*5))
    s.shape('umber',(34,y-2.4),(38,y),(34,y+2.1),(31,y),edge='rose')
    _flecks(s,p,((6,34),(45,12),(9,10),(48,22)))


DRAFTS=(
    ('Pinned Calling Card',draw_pinned_calling_card),
    ('Wax-Sealed Threat',_sealed),
    ('Calling Card Cascade',_heist),
    ('Mask in the Crosshairs',_wanted_mask),
    ('The Wild Card',_wildcard),
    ('Metaverse Navigator',_navigator),
    ('Last Train to Mementos',_mementos),
    ('Arsène Takes Flight',_arsene),
    ('Casino of Envy',_casino),
)
