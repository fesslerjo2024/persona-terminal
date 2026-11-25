"""Native dot-illustration battle and Velvet Room reels. See persona3_animation_references.md."""
from math import cos, pi, sin, tau

from persona3_detail_tools import Stage, ease, unit

THEURGY_SECONDS = 1.65
VELVET_SECONDS = 1.12
FUSION_SECONDS = 1.30
FUSION_REVIEW_SECONDS = .62

# Local projection for purpose-built silhouettes, not a text/ASCII upscale.
class Cel:
    def __init__(self,s,x,y,w,h,flip=False):
        self.s=s;self.x=x;self.y=y;self.w=w*(-1 if flip else 1);self.h=h

    def pts(self,ps):return tuple((self.x+x*self.w*.01,self.y+y*self.h*.01) for x,y in ps)
    def shape(self,ps,ink,density=8,edge=None):self.s.shape(self.pts(ps),ink,density,edge)
    def path(self,ps,ink):self.s.path(self.pts(ps),ink)
    def disc(self,x,y,rx,ry,ink,density=8,edge=None):
        (px,py),=self.pts(((x,y),)); self.s.disc(px,py,abs(rx*self.w*.01),ry*self.h*.01,ink,density,edge)
    def ring(self,x,y,rx,ry,ink,a=0,b=tau):
        (px,py),=self.pts(((x,y),)); self.s.ring(px,py,abs(rx*self.w*.01),ry*self.h*.01,ink,a,b)


# Each fighter shares a Tailored S.E.E.S. jacket base; head planes and
# recognisable silhouette accessories are drawn separately in the local cel.
def _figure(s,x,y,w,h,kind,ink,flip=False):
    a=Cel(s,x,y,w,h,flip)
    a.shape(((0,100),(5,69),(22,59),(35,55),(58,55),(78,63),(88,77),(100,100)),
            'navy',7,'slate')
    a.shape(((9,98),(19,70),(31,63),(33,91),(24,99)),'slate',5,'navy')
    a.shape(((67,60),(78,66),(89,79),(95,99),(67,95),(53,87)),ink,6,'slate')
    a.shape(((38,49),(55,48),(59,59),(51,69),(37,64),(33,56)),
            'slate',8,'teal')
    a.shape(((32,62),(48,68),(57,62),(53,98),(42,100)), 'white',7,'slate')
    a.shape(((44,73),(49,70),(54,76),(51,81),(55,100),(45,100),(47,82)),
            ink,7,'navy')
    a.path(((17,71),(29,62),(32,76),(27,86),(37,99)),'cyan')
    a.path(((73,67),(57,65),(60,81),(56,87),(63,100)),'cyan')
    a.shape(((73,70),(81,72),(85,79),(75,81),(70,77)),'red',8,'rose')
    a.shape(((27,17),(37,4),(60,5),(73,24),(72,39),(66,50),(50,57),(35,51),(26,38)),
            'white',8,'slate')
    a.shape(((26,25),(34,22),(34,36),(39,46),(49,53),(42,56),(32,51),(26,40)),
            'slate',7,'teal')
    a.shape(((43,31),(51,29),(58,31),(62,34),(54,37),(47,35)),
            'navy',8,'teal')
    a.shape(((49,33),(54,32),(57,34),(53,35)), 'white',8)
    a.path(((41,26),(55,27),(59,30)), 'slate')
    a.shape(((57,37),(63,38),(65,45),(58,46),(55,44)), 'slate',7,'teal')
    a.shape(((46,49),(53,48),(60,49),(57,51),(50,52)), 'navy',7)
    a.path(((58,32),(60,32)),'cyan')
    hair={
        'archer':((24,37),(23,17),(34,5),(53,2),(70,8),(75,20),(72,35),(66,24),
                  (61,19),(60,32),(55,25),(47,19),(40,34),(35,30),(30,43)),
        'swordsman':((22,29),(21,17),(31,10),(37,1),(57,1),(68,6),(78,17),(83,26),
                     (62,23),(46,25),(32,35),(29,43)),
        'ice':((19,23),(25,9),(45,0),(60,3),(74,13),(78,30),(79,46),(70,64),
               (65,62),(71,37),(65,21),(59,16),(43,28),(36,40),(31,52),(22,58),(15,53)),
        'boxer':((23,28),(22,16),(25,5),(32,8),(39,0),(49,3),(55,1),(66,5),(74,16),
                 (77,28),(67,19),(62,24),(58,15),(48,21),(42,16),(35,29),(28,37)),
        'spear':((20,39),(24,20),(30,5),(46,0),(63,5),(73,13),(78,31),(73,40),
                 (60,22),(53,27),(49,23),(39,38),(35,27),(27,42)),
        'heavy':((21,33),(20,17),(27,12),(29,6),(46,2),(60,0),(73,9),(76,21),
                 (73,33),(69,26),(43,24),(34,27),(32,39),(26,46)),
        'navigator':((20,29),(23,11),(33,3),(56,1),(68,8),(76,21),(70,35),(65,22),
                     (51,16),(44,31),(38,23),(32,41),(25,45)),
        'wild':((22,42),(19,22),(26,9),(35,4),(57,1),(72,9),(78,22),(76,33),
                (63,22),(66,38),(52,25),(49,42),(43,32),(36,47),(31,37),(26,50)),
    }[kind]
    hair_ink={'archer':'wine','swordsman':'navy','ice':'wine','boxer':'slate',
              'spear':'ochre','heavy':'slate','navigator':'teal','wild':'navy'}[kind]
    a.shape(hair,hair_ink,8,ink)
    a.path(((28,23),(34,13),(46,7),(60,9),(68,15)),ink)
    a.path(((33,16),(42,13),(54,12),(65,16)),ink)
    if kind=='swordsman':
        a.shape(((21,17),(29,6),(49,1),(66,2),(74,10),(75,23),(64,26),(34,25)), 
                'navy',8,'cyan')
        a.shape(((31,23),(51,20),(75,20),(86,26),(65,30),(44,29)), 'teal',7,'cyan')
    elif kind=='heavy':
        a.shape(((23,8),(40,1),(66,1),(72,11),(69,21),(23,24),(18,17)), 'navy',8,'rose')
        a.path(((21,17),(36,14),(57,12),(71,14)),'slate')
    elif kind=='navigator':
        a.disc(30,37,9,13,'navy',8,'cyan')
        a.disc(31,37,5,8,'teal',7,'white')
        a.path(((33,43),(42,51),(49,51)),'cyan')
    return a


def _set(s,t,ink):
    s.shape(((0,0),(49,0),(69,100),(0,100)),'navy',3)
    s.shape(((67,0),(100,0),(100,100),(92,100)),'navy',3)
    s.path(((43,0),(59,100)),'slate')
    s.path(((71,0),(86,100)),ink)
    s.ring(62,51,35,42,'slate',-.7,3.88)
    s.ring(62,51,33,40,ink,2+t,5.2+t)
    for i in range(10):
        y=9+i*8
        s.path((((i*3+t*12)%20,y),(40+(i*3)%9,y)),'navy')
    s.particles(t,ink,115,speed=5)


def _ring_swarm(s,f,ink='cyan',x=66,y=55):
    for i in range(6):
        r=4+i*3+10*f
        s.ring(x+i*.7,y,r,r*.67,ink if i%2 else 'teal',i*.55+f,i*.55+5.3+f)
    for i in range(22):
        a=i*tau/22
        x1,y1=x+cos(a)*(8+14*f),y+sin(a)*(5+11*f)
        s.path(((x1,y1),(x1+cos(a)*5,y1+sin(a)*5)), 'white' if i%4==0 else ink)


def _cadenza(s,t,f):
    # The two Personas face one another and dissolve into a shared healing
    # wave; lyre strings are drawn individually instead of a generic pulse.
    for dx,flip,ink in ((19,False,'cyan'),(80,True,'teal')):
        g=Cel(s,dx-12*f if flip else dx,20-5*f,24,64,flip)
        g.shape(((0,98),(10,55),(29,42),(36,30),(30,13),(43,4),(57,10),(60,28),
                 (49,44),(69,52),(85,99),(45,86),(26,97)),ink,5,'white')
        g.shape(((28,27),(44,7),(58,24),(48,39),(33,46)),'white',7,'slate')
        g.path(((36,21),(45,16),(52,24)),'navy')
        if not flip:
            g.ring(75,55,19,16,'gold',-.7,4.8)
            for i in range(5):g.path(((62+i*5,43),(63+i*5,66)),'gold')
        else:
            for i in range(7):g.path(((40,16),(63+i*3,21+i*4)),'cyan')
    for i in range(7):
        x=50; y=78-i*6
        s.ring(x,y,8+29*f+i*2,5+4*f,'cyan' if i%3 else 'white')
    if t>.6:_ring_swarm(s,f,'cyan',50,51)


def _jacks(s,t,f):
    hop=sin(t*8)*5
    a=Cel(s,12,19-hop,36,66); b=Cel(s,56,17+hop,29,69)
    a.shape(((7,84),(17,61),(32,56),(51,62),(71,80),(86,91),(62,84),(54,98),
             (40,95),(35,82),(18,89)),'teal',7,'cyan')
    a.shape(((10,46),(14,24),(29,14),(16,8),(49,1),(62,7),(77,3),(94,26),
             (88,43),(69,55),(26,62)),'navy',7,'cyan')
    a.disc(48,40,32,20,'white',8,'slate')
    a.shape(((28,33),(39,31),(43,40),(33,43)),'navy',8)
    a.shape(((54,32),(65,34),(63,43),(53,39)),'navy',8)
    a.path(((35,49),(44,44),(49,50),(55,45),(62,47)),'navy')
    b.shape(((31,68),(49,63),(65,72),(78,95),(64,87),(48,99),(42,86),(27,97)), 
            'wine',7,'amber')
    b.disc(50,44,36,24,'amber',7,'gold')
    for i in (-2,-1,0,1,2):b.ring(50+i*7,44,13,23,'ochre',1.,4.9)
    b.shape(((23,42),(37,30),(41,45),(51,37),(60,48),(68,35),(80,42),(74,55),
             (65,52),(61,58),(50,52),(41,58),(31,53)),'wine',8)
    b.path(((46,22),(45,11),(65,6)),'green')
    if t>.62:_ring_swarm(s,f,'amber',51,51)


def _cyclone(s,t,f):
    h=_figure(s,10-6*f,21,40,80,'archer','rose')
    pull=ease(unit(t,.20,.66))
    x=57-f*1.3;y=49+pull*3
    s.ring(x-9,y,12,34,'gold',-1.3,1.3)
    s.ring(x-10,y,11,33,'white',-1.2,1.2)
    s.path(((x-5,y-32),(x-22-7*pull,y),(x-5,y+31)),'white')
    h.path(((62,69),(74,60),(100,61)),'rose')
    if t<.65:s.path(((x-21-7*pull,y),(x+14,y)),'teal')
    else:
        z=unit(t,.65,1.45)
        for i in range(7):
            pts=tuple((46+z*(45+i)-j*1.8,y+sin(j*.41+2*i+z*7)*i*2.7) for j in range(23))
            s.path(pts,'white' if i%3==0 else 'cyan')
        for i in range(5):s.ring(68+28*z,y,4+i*2,8+i*4,'teal',z*5+i,5+z*5+i)


def _slash(s,t,f,ice=False):
    _figure(s,7-11*f,16,41,86,'ice' if ice else 'swordsman','rose' if ice else 'red')
    a=-1.40+f*3.24
    x,y=42,74
    tip=(x+cos(a)*49,y+sin(a)*64)
    s.shape(((x-2,y+2),(tip[0]-3,tip[1]+2),tip,(tip[0]+5,tip[1]-1),(x+2,y-2)),
            'white',8,'cyan' if ice else 'amber')
    s.path(((tip[0]-3,tip[1]+2),(x,y), (x-5,y+8)),'teal' if ice else 'wine')
    if f>.05:
        for i in range(15):
            scale=i/15
            s.ring(43,71,34+scale*16,56+scale*10,'teal' if ice else ('wine' if i%3 else 'amber'),
                   max(-1.42,a-1.5-scale*.32),a-.15)
        for i in range(12):
            rx=57+(i*73%40);ry=29+(i*37%66)
            if ice:
                s.shape(((rx-2,ry+3),(rx,ry-11*f),(rx+3,ry-4*f),(rx+4,ry+4)),
                        'navy',6,'cyan')
                s.path(((rx,ry-11*f),(rx+1,ry+4)),'white')
            else:
                s.path(((rx,ry),(rx+f*6,ry-f*17),(rx+f*7,ry-f*12)),
                       'gold' if i%2 else 'red')


def _lightning(s,t,f):
    a=_figure(s,8-9*f,13,39,88,'boxer','gold')
    a.shape(((51,67),(57,57),(68,52),(79,52),(87,57),(93,66),(90,78),(79,84),
             (60,81),(51,77)),'white',8,'gold')
    a.path(((57,67),(66,59),(78,56),(85,60)),'navy')
    for i in range(9):
        x=46+i*6; y=34+(i*41)%36
        fork=tuple((x+sin(j*(2+i))*3.7, y+j*(4+2*f)) for j in range(10))
        if t>.26+i*.032:
            s.path(fork,'white' if i%3==0 else 'gold')
            b=fork[3]; c=fork[6]
            s.path((fork[0], b, (b[0]-8, b[1]+12), (b[0]-9,c[1]+11)),'violet')
    if t>.67:_ring_swarm(s,f,'gold',68,70)


def _divine(s,t,f):
    _figure(s,5-6*f,20,42,84,'spear','ochre')
    s.shape(((22,86),(70-6*f,32),(74-6*f,28),(81,18),(78,33),(75,36),(24,89)),
            'gold',8,'white')
    s.ring(70,46,18+f*8,26+f*10,'amber')
    s.ring(70,46,12+f*12,18+f*13,'gold')
    if t>.59:
        for i in range(8):
            x=60+i*3+sin(i*3)*3
            s.shape(((x-.3,5),(x+f*3,5),(x+f,79),(x-3*f,59)),'white' if i%3 else 'gold',4)
        for i in range(11):s.path(((70,85),(42+5*i,69-f*13)),'gold')


def _heavy(s,t,f):
    _figure(s,10-12*f,18,40,89,'heavy','wine')
    a=-2.5+f*4
    x=62+cos(a)*19;y=52+sin(a)*34
    s.path(((33,87),(x,y)),'slate')
    s.shape(((x-10,y-12),(x+3,y-15),(x+13,y-8),(x+9,y+11),(x-6,y+13),(x-7,y+4)),
            'wine',8,'rose')
    s.path(((x-9,y-10),(x+4,y-11),(x+9,y-6),(x+7,y+6)),'white')
    if t>.6:
        for i in range(14):
            a=i*tau/14
            s.path(((78,77),(78+cos(a)*18*f,77+sin(a)*23*f),
                    (78+cos(a)*30*f,77+sin(a)*34*f)),'rose' if i%4==0 else 'red')
        s.ring(78,77,20+f*11,4+f*5,'wine')


def _orgia(s,t,f):
    a=Cel(s,7-6*f,11,53,88)
    a.shape(((7,100),(11,69),(25,56),(58,47),(80,52),(90,70),(99,100)),
            'slate',7,'cyan')
    a.shape(((29,51),(20,35),(20,22),(32,4),(56,0),(69,10),(79,25),(75,38),
             (62,48),(48,55)),'white',8,'gold')
    a.shape(((25,19),(37,8),(58,7),(71,14),(68,29),(59,39),(36,35),(23,30)),
            'gold',8,'amber')
    a.shape(((24,28),(38,23),(54,30),(72,25),(70,42),(57,48),(35,43)),
            'white',8,'slate')
    a.shape(((34,31),(43,29),(54,33),(56,38),(46,39),(39,35)), 'navy',8,'teal')
    a.shape(((44,33),(52,34),(51,37),(45,35)), 'cyan',8)
    a.path(((58,34),(64,41),(59,45)), 'slate')
    a.shape(((53,41),(57,45),(63,44),(59,47),(54,45)), 'slate',7)
    a.disc(23,40,10,12,'navy',8,'gold')
    a.disc(23,40,5,6,'teal',8,'white')
    a.shape(((40,65),(60,59),(78,62),(91,57),(99,62),(94,74),(74,85),(48,83)),
            'white',6,'gold')
    a.path(((51,73),(71,69),(86,69),(92,64)),'slate')
    for k in range(5):
        x=45+k*.8;y=62+k*1.3
        s.path(((x-4,y+6),(x,y),(x+3,y-1)),'cyan')
        if t>.45:
            z=(t*2.6+k*.13)%1
            u=x+z*50
            s.path(((u,y+(k-2)*z*6),(u+12,y+(k-2)*z*12)), 'gold' if k%2 else 'white')
            s.burst(u,y+(k-2)*z*6,2,5,'amber')
    if t>.64:
        s.ring(61,60,12+22*f,9+7*f,'gold',-.6,.6)


def _hound(s,t,f):
    for i in range(8):
        s.path(((0,78+i*2),(24+f*13,54+i*2),(89,52+i*4)),'wine')
    dog=Cel(s,12+9*f,16,73,69)
    dog.shape(((3,44),(19,30),(47,37),(53,29),(66,17),(78,31),(84,50),
               (80,61),(68,56),(66,82),(72,97),(58,95),(51,76),(43,90),(37,86),
               (30,65),(22,62),(8,74),(11,60),(4,66)), 'wine',8,'rose')
    dog.shape(((13,44),(28,34),(49,40),(56,49),(38,54),(31,53)), 'navy',6,'wine')
    for i in (-1,0,1):
        a=Cel(s,58+8*i+7*f,38+i*17,18,23)
        a.shape(((2,42),(12,24),(13,3),(27,13),(31,22),(63,20),(78,0),(84,21),
                 (85,33),(98,51),(84,69),(65,70),(61,91),(33,83),(20,62)),
                'wine',8,'rose' if i else 'white')
        a.shape(((68,45),(85,42),(96,50),(84,59),(67,55)),'navy',7,'rose')
        a.shape(((38,37),(54,28),(66,34),(62,44),(50,48),(42,44)), 'gold',8,'amber')
        a.path(((50,35),(54,46)), 'navy')
        a.path(((59,65),(72,67),(83,63)),'white')
    if t>.75:
        for i in range(12):
            y=22+i*6    
            s.path(((8,y+9),(40*f,y),(65*f,y-7)),'rose' if i%4==0 else 'wine')


def _oracle(s,t,f):
    _figure(s,31,14+3*sin(t*4),38,81,'navigator','teal')
    s.disc(54,48,37,45,'navy',3)
    for i in range(6):
        s.ring(54,48,13+4*i,15+5*i,'teal' if i%2 else 'cyan',t*2+i,t*2+i+4.8)
    for q in range(24):
        a=q*tau/24
        s.path(((54+36*cos(a),48+44*sin(a)),(54+34*cos(a),48+41*sin(a))),
               'white' if (q+int(t*9))%5==0 else 'cyan')
    # Reference is Fuuka's non-combat support; the atlas sweeps instead of striking.
    for i in range(3):
        x=54+sin(3*t+i*.63)*(18+7*i);y=48+cos(3*t+i*.63)*(23+8*i)
        s.burst(x,y,.8,2,'gold')
        s.path(((54,48),(x,y)),'teal')
    if t>.66:
        _ring_swarm(s,f,'cyan',54,48)


_STAGES={
    'cadenza':('cyan',_cadenza),'jackbrothers':('amber',_jacks),
    'cyclonearrow':('rose',_cyclone),'hacknblast':('red',_slash),
    'lightningspike':('gold',_lightning),'blizzardedge':('cyan',lambda s,t,f:_slash(s,t,f,True)),
    'divineretribution':('gold',_divine),'bleedingfury':('wine',_heavy),
    'orgiamode':('gold',_orgia),'houndofhades':('rose',_hound),'oracle':('teal',_oracle),
}
_ALIAS={'makoto':'cadenza','yukari':'cyclonearrow','junpei':'hacknblast','akihiko':'lightningspike',
        'mitsuru':'blizzardedge','ken':'divineretribution','shinjiro':'bleedingfury','aigis':'orgiamode',
        'koromaru':'houndofhades','fuuka':'oracle','revelation':'oracle',
        'tranquility':'cyclonearrow','blazeoflife':'hacknblast','bladeofexecution':'blizzardedge'}


def render_theurgy(name,t,w,h,*,low_motion=False):
    t=.94 if low_motion else min(THEURGY_SECONDS,max(0.,t))
    s=Stage(w,h)
    key=''.join(c for c in str(name).casefold() if c.isalnum())
    ink,stage=_STAGES.get(_ALIAS.get(key,key),_STAGES['cadenza'])
    _set(s,t,ink)
    f=ease(unit(t,.36,1.36))
    stage(s,t,f)
    if t<.18:
        k=t/.18
        s.path(((9+70*k,0),(35+70*k,100)),'cyan')
    return s.c.finish()


def _elevator_room(s,t,p):
    # Angled cage roof, widely spaced brass bars, patterned runner, attendants.
    for side in (-1,1):
        a=50+side*45
        s.shape(((a,100),(a,9),(50+side*12,25),(50+side*12,71)), 'navy',7,'teal')
        for i in range(1,8):
            x=50+side*(12+i*4);top=25-i*2
            s.path(((x,top),(x,73+i*3)),'teal' if i%2 else 'slate')
            s.path(((x+side,top),(x+side,74+i*3)),'navy')
        for i in range(5):
            s.path(((a,10+i*20),(50+side*12,25+i*11)),'teal')
        s.shape(((a,89),(50+side*12,70),(50+side*6,70),(50+side*24,100)), 'teal',4)
    s.shape(((5,100),(40,72),(60,72),(95,100)), 'navy',7,'cyan')
    for i in range(6):
        y=72+i*i*1.2
        spread=10+i*4.4
        s.path(((50-spread,y),(50+spread,y)),'teal')
    for x,ink in ((40,'gold'),(62,'slate')):
        s.disc(x,45,4,8,'slate',7,ink)
        s.shape(((x-7,67),(x-4,55),(x+5,56),(x+8,67),(x+10,72),(x-9,72)), 
                'teal',6,ink)
        s.path(((x-4,44),(x-1,42),(x+1,44)),'cyan')
    s.shape(((37,64),(62,64),(69,72),(32,72)), 'slate',7,'cyan')
    s.shape(((32,72),(69,72),(66,89),(34,89)), 'navy',8,'teal')
    s.shape(((46,67),(49,65),(54,66),(56,70),(51,69),(48,71)), 'teal',8,'cyan')
    s.ring(50,25,20,13,'cyan',pi,tau)
    for i in range(3):s.ring(50,26,18+i*4,10+i*3,'navy',pi+.09,tau-.09)
    if p<1:
        for side in (-1,1):
            inner=50+side*37*p; outer=50+side*49
            s.rect(min(inner,outer),3,abs(inner-outer),94,'navy',7,'teal')
            for i in range(1,5):
                x=inner+side*(i*.17)*abs(inner-outer)
                s.path(((x,4),(x,94)),'teal' if i%2 else 'slate')
            s.path(((inner,3),(inner,97)),'cyan')


def render_velvet(t,w,h,*,low_motion=False):
    t=VELVET_SECONDS if low_motion else min(VELVET_SECONDS,max(0.,t))
    s=Stage(w,h)
    p=ease(unit(t,.44,1.04))
    if t>.36:
        _elevator_room(s,t,p)
    else:
        s.shape(((0,55),(100,44),(100,100),(0,100)), 'navy',5)
        for i in range(9):
            f=ease(unit(t,0,.37))
            x=50+sin(i)*3*f
            y=65-i*3-f*27
            s.ring(x,y,4+f*29+i*2,4+f*10,'cyan' if i<2 else 'teal',pi*i*.13,1.85*pi+i*.27)
        s.particles(t,'slate',180,speed=11,region=(0,40,100,60))
    return s.c.finish()


def _card(s,x,y,w,h,ink,mark,slant=0):
    a=Cel(s,x,y,w,h)
    a.shape(((slant,0),(100+slant,0),(100,100),(0,100)),'navy',8,ink)
    a.shape(((7+slant,6),(93+slant,6),(93,94),(7,94)), 'slate',4,'teal')
    for i in range(4):
        a.path(((10+slant+i*3,8+i*3),(35+slant,8+i*3)),ink)
        a.path(((90-i*3,92-i*3),(67,92-i*3)),ink)
    a.ring(50+slant/2,48,35,33,'teal')
    a.ring(50+slant/2,48,31,29,ink)
    x=50+slant/2
    if mark==0:
        a.path(((x-26,58),(x,25),(x+26,58),(x,69),(x-26,58)), ink)
        a.path(((x,25),(x,73)),ink)
    elif mark==1:
        a.ring(x,50,22,22,ink,1.10,5.15)
        a.ring(x+9,47,20,17,ink,1.53,4.65)
    else:
        a.path(((x+15,30),(x+4,47),(x+24,44),(x-14,71),(x-6,54),(x-24,57),(x+15,30)),ink)


def render_fusion_review(t,w,h=5,*,low_motion=False):
    t=FUSION_REVIEW_SECONDS if low_motion else max(0.,min(t,FUSION_REVIEW_SECONDS))
    p=ease(unit(t,0,FUSION_REVIEW_SECONDS))
    s=Stage(w,h)
    # The same parent cards remain side by side in the live confirm panel.
    for a,k in ((-1,0),(1,1)):
        x=50+a*(29-13*p)-8
        _card(s,x,0 if h<7 else 15,16,100 if h<7 else 69,'cyan' if not k else 'rose',k)
        for i in range(4):
            y=25+i*15
            s.path(((x+a*10,y),(x+a*(12+7*(1-p)),y)), 'teal')
    return s.c.finish()


def render_fusion(t,w,h,*,low_motion=False):
    t=FUSION_SECONDS if low_motion else min(FUSION_SECONDS,max(0.,t))
    s=Stage(w,h);f=ease(unit(t,.08,.75))
    s.particles(t,'navy',200,speed=10)
    for i in range(5):
        s.ring(50,49,8+i*9,13+i*7,'navy' if i%2 else 'teal',t*3+i,t*3+i+5.6)
    if t<.78:
        for k,d in enumerate((-1,1)):
            x=50+d*(30-24*f)-11
            y=23+d*9*(1-f)
            _card(s,x,y,22,55,'cyan' if k==0 else 'rose',k,24*f*d)
    else:
        # A pair of enclosing orbits opens, leaving a third sigil, not either parent.
        z=ease(unit(t,.77,1.20))
        for i in range(6):
            s.ring(50,50,5+i*3+22*z,9+i*4+24*z,'white' if i<2 else 'cyan',i*.7,i*.7+5.8)
        _card(s,39,20-4*z,22,58,'white',2,5*(1-z))
        for i in range(26):
            a=i*tau/26
            x,y=50+cos(a)*(9+35*z),50+sin(a)*(12+37*z)
            s.burst(x,y,.22,.45,'gold' if i%4==0 else 'teal')
    return s.c.finish()
