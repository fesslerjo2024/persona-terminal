"""Graduation, discoveries and post-credits illustrations on the native dot grid."""
from math import cos, isfinite, pi, sin, tau

from .persona3_detail_tools import Stage, ease, unit
from ..shared.wide_canvas import Canvas

DURATIONS = {'bad': 2.8, 'roof': 5.4, 'credits': 5.0, 'bridge': 3.2,
             'karaoke': 3.4, 'stars': 3.6, 'reunion': 3.6,
             'station-alley': 2.2, 'tartarus-roof': 2.6}


def _figure(s,x,y,height,accent='teal',human=True,lean=0):
    w=height*.34
    s.shape(((x-w*.49,y),(x-w*.35,y-height*.46),(x-w*.19,y-height*.57),
             (x+w*.16+lean,y-height*.59),(x+w*.41,y-height*.48),(x+w*.51,y)),
            'navy',8,accent)
    s.shape(((x-w*.09,y-height*.53),(x+w*.135,y-height*.60),(x+w*.16,y-height*.31),
             (x+w*.045,y-height*.20)), 'white',7,'slate')
    s.path(((x-w*.38,y-height*.41),(x-w*.14,y-height*.67),(x+w*.10,y-height*.21)), 'teal')
    s.path(((x+w*.35,y-height*.38),(x+w*.25,y-height*.62),(x+w*.12,y-height*.24)), 'slate')
    s.path(((x+w*.38,y-height*.37),(x+w*.16,y-height*.31)), 'rose' if human else accent)
    hx=x+lean
    s.disc(hx,y-height*.79,w*.24,height*.17,'white',8,'slate')
    if human:
        s.shape(((hx-w*.24,y-height*.81),(hx-w*.22,y-height*.93),(hx-w*.08,y-height*.99),
                 (hx+w*.16,y-height*.96),(hx+w*.30,y-height*.84),(hx+w*.16,y-height*.77),
                 (hx+w*.11,y-height*.89),(hx+w*.02,y-height*.79),(hx-w*.03,y-height*.89),
                 (hx-w*.14,y-height*.78),(hx-w*.25,y-height*.88)),
                'navy',8,accent)
    else:
        s.shape(((hx-w*.23,y-height*.78),(hx-w*.27,y-height*.90),
                 (hx-w*.09,y-height*.98),(hx+w*.10,y-height*.98),(hx+w*.27,y-height*.92),
                 (hx+w*.30,y-height*.86),(hx+w*.12,y-height*.88),(hx-w*.13,y-height*.88)),
                'gold',8,'amber')
        s.ring(hx-w*.23,y-height*.78,w*.11,height*.075,accent)
    s.path(((hx-w*.09,y-height*.82),(hx-w*.02,y-height*.83)), 'navy')
    s.path(((hx+w*.07,y-height*.82),(hx+w*.14,y-height*.82)), 'navy')


def _perspective(s,y,x,ink):
    for i in range(-8,9):
        s.path(((x+i*1.6,y),(x+i*12.8,100)),ink)
    for i in range(8):
        yy=y+((i+1)/8)**2*(100-y)
        s.path(((0,yy),(100,yy)),ink)


def _roof_set(s,u,hero=True):
    s.disc(76,29,17,17,'gold',5,'amber')
    s.shape(((0,75),(16,58),(30,54),(39,63),(55,62),(69,69),(87,53),(100,58),(100,100),(0,100)),
            'navy',7,'slate')
    for j in range(28):
        x=(j*47)%100;y=58+(j*61)%14
        s.rect(x,y,.45,1.6,'teal',6)
    for i in range(9):
        x=9+i*11
        s.path(((x,38),(x,91)), 'slate')
        s.path(((x+.45,38),(x+.45,89)), 'teal')
    for j in range(6):
        y=45+j*7
        s.path(((0,y),(100,y-5)), 'slate')
        s.path(((0,y-1),(100,y-6)), 'navy')
    s.path(((0,39),(100,35)),'cyan')
    if hero:
        s.shape(((23,100),(26,86),(44,82),(59,82),(73,86),(83,100)), 'teal',6,'navy')
        s.path(((26,88),(74,88)), 'cyan')
    s.particles(u*3,'rose',84,speed=3,region=(0,0,100,92))
    s.particles(u*2,'gold',31,speed=-7,region=(0,0,100,84))


def _roof(s,u,reunion=False):
    _roof_set(s,u)
    if reunion:
        for i,(ink,x) in enumerate((('rose',25),('ochre',41),('teal',59),('slate',75))):
            dx=(x-50)*.38*(1-ease(u))
            _figure(s,x+dx,91+sin(u*10+i)*1.6,53+i%2*5,ink,lean=sin(i)*2.5)
    else:
        _figure(s,59,97,77,'teal',human=False,lean=-2)
        s.shape(((26,94),(28,74),(36,65),(49,67),(57,82),(65,94)), 'navy',7,'teal')
        s.shape(((33,80),(38,69),(51,72),(59,80),(54,87),(44,88)), 'white',8,'slate')
        s.shape(((35,75),(36,69),(42,66),(48,66),(54,68),(57,74),(53,77),(47,74),
                 (43,79),(41,74),(37,80)), 'navy',8,'cyan')
        s.path(((45,81),(53,80)), 'navy')
        s.path(((62,86),(59,87),(52,79),(50,81)), 'teal')


def _graduation(s,u):
    s.shape(((0,100),(0,11),(28,0),(72,0),(100,11),(100,100)), 'navy',7,'slate')
    _perspective(s,55,50,'teal')
    s.shape(((22,49),(22,4),(78,4),(78,49),(68,56),(31,56)), 'wine',7,'rose')
    for side in (-1,1):
        for i in range(8):
            x=50+side*(5+i*2.95)
            s.path(((x,6),(x+side*4,50)), 'wine' if i%2 else 'rose')
    s.rect(42,41,15,32,'slate',7,'teal')
    s.rect(42,39,15,4,'navy',6,'gold')
    s.path(((42,56),(57,56)), 'teal')
    _figure(s,49.5,40,25,'rose',lean=sin(u*4))
    for row in range(2):
        for j in range(10-row):
            x=4+j*(10+row)
            y=98-row*8
            ht=9+row*5+sin(j*4+u*5)
            s.disc(x,y-ht,2+row*.25,ht*.31,'slate',8,'navy')
            s.shape(((x-3,y+4),(x-2,y-ht*.8),(x+2,y-ht*.8),(x+3,y+4)), 'navy',8,'teal')


def _classroom(s,u):
    s.shape(((0,0),(100,0),(100,70),(0,70)), 'navy',7,'slate')
    s.rect(15,8,44,28,'forest',7,'teal')
    for i in range(10):s.path(((18+i,31),(34+i*2,31)), 'slate')
    for j in range(3):
        x=66+j*10
        s.rect(x,6,7,42,'teal',5,'slate')
        s.path(((x+3,6),(x+3,48)), 'navy')
        s.path(((x,19),(x+7,19)), 'navy')
    _perspective(s,48,49,'slate')
    for j in range(3):
        ys=49+j*17
        for i in range(4):
            x=16+i*21+(i-1.5)*j
            s.shape(((x-6,ys),(x+6,ys),(x+8,ys+11),(x-8,ys+11)),
                    'navy',8,'slate')
            s.path(((x-7,ys+10),(x-6,ys+21)), 'teal')
    s.particles(u*3,'teal',80,speed=2,region=(60,7,29,87))


def _karaoke(s,u):
    s.shape(((0,0),(100,0),(100,100),(0,100)), 'wine',3)
    s.shape(((20,65),(18,22),(80,22),(84,65)), 'navy',8,'violet')
    s.rect(30,31,40,24,'navy',8,'rose')
    s.path(((34,46),(41,42),(47,45),(55,34),(66,40)),'cyan')
    for i,(x,c) in enumerate(((26,'rose'),(49,'slate'),(73,'ochre'))):
        _figure(s,x,94+sin(u*13+i*2)*2,58,c)
        y=53+sin(u*8+i)*5
        s.path(((x+8,72),(x+4,y)), 'white')
        s.disc(x+4,y,1.5,3.7,'gold',8,'rose')
    for i in range(15):
        x=5+(i*47)%90
        y=(i*19-u*99)%71
        s.burst(x,y,1.1,2.8,'rose' if i%2 else 'violet')


def _stars(s,u):
    s.particles(u*4,'teal',230,speed=-2)
    for i in range(21):
        x=(i*39+u*3)%100;y=(i*71-u*3)%96
        s.burst(x,y,.55 if i%5 else 1.2,1.1 if i%5 else 3,
                'white' if i%5==0 else 'slate')
    for i in range(5):
        q=u+.17*i
        s.path(((13+18*i,38+6*sin(q*3)),(65+2*sin(i),16+7*i)),
               'navy')
    s.disc(70,28,16,22,'navy',5,'slate')
    s.ring(70,28,14.5,21,'teal',2.5,5.6)


def _credits(s,u):
    s.shape(((0,60),(100,72),(100,100),(0,100)), 'navy',5,'teal')
    s.disc(71,40,11+u*4,14+u*3,'gold',5,'amber')
    for j in range(11):
        y=56+j**1.5*.95
        s.path(tuple((i*3.6,y+sin(i*.79+j*.37-u*13)*2.4) for i in range(29)),
               'teal' if j%3 else 'cyan')
    for j in range(6):
        for i in range(18):
            x=66+(i*23%175)/12-j*.81+2*sin(u*11+i)
            y=59+j*4.5
            s.path(((x,y),(x+.6+j*.24,y)), 'gold' if i%4 else 'white')
    s.particles(u*2,'slate',86,speed=2,region=(0,0,100,55))


def _station(s,u):
    _perspective(s,54,53,'slate')
    for k,side in enumerate((-1,1)):
        a=50+side*49;b=50+side*20
        s.shape(((a,0),(b,35),(b,55),(a,100)),'navy',7,'slate')
        for i in range(10):
            z=i/10
            x=a+(b-a)*z
            s.path(((x,z*34),(x,100-z*43)), 'slate' if i%2 else 'teal')
        s.ring(a-side*17,27,7,15,'slate',pi,tau)
        s.disc(a-side*17,38,2+(u*.6 if not k else 0),4,'gold',7,'amber')
    _figure(s,43+(1-u)*2,75,35,'rose',lean=-1.1)
    _figure(s,63-(1-u)*2,76,30,'slate',lean=.7)
    s.particles(u*4,'teal',104,speed=-3,region=(0,20,100,74))


def _tartarus_roof(s,u):
    _stars(s,u)
    s.shape(((1,100),(14,78),(33,63),(61,63),(83,75),(98,100)), 'navy',7,'slate')
    for i in range(6):
        y=65+i*5.7
        span=16+i*5
        s.path(((50-span,y),(50+span,y)), 'teal')
    s.ring(71,28,15,21,'rose',pi*.62,pi*2.03)
    for j in (-1,1):
        p=50+j*23
        s.path(((p,53),(p,31),(p+j*12,22)), 'teal')
        s.path(((p,32),(p+j*11,28)), 'rose')
    _figure(s,49,88,54,'teal',human=False,lean=sin(u*2)*2)
    s.ring(50,56,19+u*12,24+u*15,'teal',u*4,u*4+5.03)


_RENDERERS={'bad':_graduation,'roof':_roof,'credits':_credits,'bridge':_classroom,
            'karaoke':_karaoke,'stars':_stars,'reunion':lambda s,u:_roof(s,u,True),
            'station-alley':_station,'tartarus-roof':_tartarus_roof}


def render(scene,t,w,h):
    """Return h rows of single-column art, preserving compact scene bands."""
    if w<0 or h<0:raise ValueError('Ending frame dimensions must be nonnegative')
    if scene not in _RENDERERS:raise ValueError(f'Unknown ending scene: {scene}')
    if w<22 or h<5:return Canvas(w,h).finish()
    u=unit(t,0.,DURATIONS[scene]) if isfinite(t) else 0.
    fading=scene in ('credits','karaoke','stars')
    if fading and u>=1:return Canvas(w,h).finish()
    s=Stage(w,h)
    _RENDERERS[scene](s,u)
    if fading and u>.78:
        f=ease(unit(u,.78,1.))
        for y,row in enumerate(s.c.rows):
            for x,ink in enumerate(row):
                if ink is not None and (x*17+y*23+3*x*y)%101<101*f:row[x]=None
    return s.c.finish()
