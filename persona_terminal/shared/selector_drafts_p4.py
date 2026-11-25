"""Persona 4 selector studies. The fog stays spoiler-free."""
from math import cos, sin, tau


class Art:
    def __init__(self,c,p):
        self.c,self.p=c,p

    def xy(self,x,y):
        return x*(self.c.w-1)/100,y*(self.c.h-1)/100

    def shape(self,pts,ink,d=8,edge=None):
        self.c.face(tuple(self.xy(*q) for q in pts),ink,d,edge)

    def line(self,pts,ink):
        self.c.path(tuple(self.xy(*q) for q in pts),ink)

    def dot(self,x,y,ink):
        self.c.put(*map(round,self.xy(x,y)),ink)

    def oval(self,x,y,r,d,ink,density=8,edge=None):
        self.c.ellipse(*self.xy(x,y),*self.xy(r,d),ink,density,edge)

    def ring(self,x,y,r,d,ink,a=0,b=tau):
        self.c.ring(*self.xy(x,y),*self.xy(r,d),ink,a,b)

    def glint(self,x,y,s):
        self.shape(((x,y-s),(x+s*.24,y-s*.18),(x+s*.7,y),(x+s*.24,y+s*.18),
                    (x,y+s),(x-s*.24,y+s*.18),(x-s*.7,y),(x-s*.24,y-s*.18)),'white')

    def fog(self,x,y,span,n,ink='ochre'):
        for i in range(n):
            a=x+((i*53+i*i*7)%100)/100*span
            b=y+(i*37)%17
            f=0 if self.p==1 else 6*sin(self.p*tau+i*.7)
            self.line(((a+f,b),(a+f+2+(i*7)%9,b)),ink)


def draw_golden_tube_tv(c,p):
    a=Art(c,p)
    swing=12*(1-p)
    a.line(((42,27),(24+swing,8),(19+swing,8)),'amber')
    a.line(((44,27),(66+swing,5),(72+swing,5)),'gold')
    a.shape(((11,35),(19,25),(80,25),(89,33),(89,77),(79,84),(23,84),(11,76)),'ochre',8,'gold')
    a.shape(((18,37),(25,31),(66,31),(72,40),(70,69),(64,76),(25,75),(19,67)),'ink',8,'amber')
    a.shape(((75,33),(84,36),(84,74),(75,77)),'umber',6)
    a.oval(79.5,44,3.1,4.7,'gold',6,'amber')
    a.oval(79.5,57,2.1,3.2,'amber')
    a.line(((79.5,41),(79.5,44)),'white')
    for i in range(4):a.line(((77,64+i*2),(82,64+i*2)),'ochre')
    for x in (23,72):a.shape(((x,80),(x+8,80),(x+5,91),(x,91)),'umber',8,'amber')
    for i in range(92):
        x=26+(i*53)%40;y=36+(i*13)%34
        if (x+y+int(p*28))%9<4:a.dot(x,y,'ochre' if y%2 else 'amber')
    y=44 if p==1 else 36+30*p
    a.line(((24,y),(66,y)),'gold')
    a.line(((25,36),(32,33),(61,34)),'white')


def glasses(c,p):
    a=Art(c,p)
    a.line(((16,41),(6,27),(18,23),(34,36)),'ochre')
    a.line(((84,41),(94,25),(86,22),(69,36)),'ochre')
    for pts in (
        ((9,44),(17,35),(42,36),(48,44),(44,62),(37,70),(20,70),(13,65)),
        ((52,45),(58,36),(83,35),(91,44),(88,62),(81,70),(65,70),(57,64)),
    ):
        a.shape(pts,'gold')
        mx=sum(x for x,y in pts)/len(pts);my=sum(y for x,y in pts)/len(pts)
        a.shape(tuple((mx+(x-mx)*.80,my+(y-my)*.72) for x,y in pts),'ink',8,'amber')
        dx=(p-1)*11
        a.line(((mx-11+dx,57),(mx-2+dx,45),(mx+5+dx,43)),'amber')
        a.line(((mx-7+dx,57),(mx+3+dx,47)),'white')
    a.line(((46,46),(49,43),(52,43),(55,46)),'white')
    a.glint(79,35,6 if p==1 else 1+6*sin(p*tau)**2)


def rain(c,p):
    a=Art(c,p)
    a.shape(((18,9),(81,9),(88,19),(88,85),(12,85),(12,19)),'ochre',7,'gold')
    a.shape(((20,18),(80,18),(80,77),(20,77)),'ink',8,'amber')
    a.oval(61,32,10,11,'amber',6,'gold')
    for x,y,w in ((20,54,14),(33,59,9),(42,48,12),(59,57,13),(71,52,9)):
        a.shape(((x,78),(x,y),(x+w*.5,y-5),(x+w,y),(x+w,78)),'umber',8,'ochre')
    for j in range(40):
        x=21+(j*19)%58;y=20+((j*43+p*72)%54)
        a.line(((x,y),(x-2,min(76,y+4+(j%4)))),'amber' if j%6==0 else 'ochre')
    a.line(((49,18),(49,77)),'gold')
    a.line(((20,49),(80,49)),'gold')
    a.shape(((9,83),(90,83),(94,91),(7,91)),'gold',7,'amber')


def fog_town(c,p):
    a=Art(c,p)
    a.oval(69,34,13,16,'amber',5,'gold')
    a.shape(((4,61),(22,38),(36,43),(50,59),(61,50),(88,48),(97,63),(96,72),(5,74)),
            'umber',7,'ochre')
    for x,b,k in ((11,69,2),(25,70,6),(42,71,3),(58,69,9),(75,68,2),(85,71,4)):
        a.shape(((x-1,b),(x-1,b-15-k),(x+5,b-23-k),(x+11,b-15-k),(x+11,b)),'ochre',7,'amber')
        a.dot(x+4,b-11,'white')
    a.line(((4,73),(85,73),(98,67)),'gold')
    a.line(((10,81),(33,75),(61,74),(95,74)),'umber')
    a.fog(3,61,83,21)
    a.fog(11,79,75,12,'gold')


def broadcast(c,p):
    a=Art(c,p)
    for i in range(3):
        r=12+i*10+(0 if p==1 else 4*sin(p*tau+.7*i))
        for side in (-1,1):
            start=-.49 if side==1 else 2.65
            a.ring(50,28,r,r*1.05,'gold' if i==0 else 'ochre',start,start+.98)
    a.shape(((49,25),(51,25),(67,89),(61,89),(50,41),(39,89),(33,89)),'ochre',7,'gold')
    for i,y in enumerate((48,61,74,87)):
        r=6+i*3
        a.line(((50-r,y),(50+r,y)),'amber')
        if i<3:a.line(((50-r,y),(50+r+1,y+12)),'ochre')
    a.oval(50,28,4,5,'gold',7,'white')
    a.glint(50,14,5)
    a.fog(12,77,68,14,'umber')


def portal(c,p):
    a=Art(c,p)
    a.shape(((10,27),(18,17),(75,17),(88,29),(88,77),(78,85),(17,85),(10,75)),'ochre',7,'gold')
    a.shape(((17,32),(22,25),(72,25),(80,33),(80,70),(72,78),(23,78),(17,69)),'ink',8,'amber')
    for j in range(4):
        r=27-j*5+(1-p)*3
        a.ring(49,51,r,r*.8,('gold','amber','ochre','umber')[j],p*tau+j*.4,p*tau+j*.4+5.55)
    a.oval(49,43,4.2,6,'white')
    a.shape(((44,47),(54,47),(57,60),(52,61),(53,71),(48,72),(46,61),(42,64),(39,60)), 'gold')
    for i in range(8):
        x=24+(i*41)%48;y=31+(i*17)%38
        a.dot(x,y,'white')
    a.line(((13,87),(2,94),(25,94)),'ochre')
    a.line(((83,86),(97,94),(69,94)),'ochre')


def arcana(c,p):
    a=Art(c,p)
    t=(1-p)*10
    a.shape(((16,24),(45,15),(62,63),(34,77)), 'umber',8,'ochre')
    a.shape(((55,20),(79,29),(82,76),(52,79)), 'ochre',7,'amber')
    a.shape(((36-t,13),(69-t,13),(69+t*.5,86),(36+t*.5,86)),'ink',8,'gold')
    a.line(((39-t,17),(66-t,17),(66+t*.5,82),(39+t*.5,82),(39-t,17)),'ochre')
    for i in range(12):
        b=i*tau/12+p*tau
        a.line(((52+cos(b)*11,48+sin(b)*15),(52+cos(b)*15,48+sin(b)*22)),'gold')
    a.oval(52,48,8,11,'amber',7,'gold')
    a.glint(52,48,8)
    a.dot(52,75,'white')


def shopping(c,p):
    a=Art(c,p)
    lift=(1-p)*7
    a.ring(49,38-lift,13,20,'gold')
    a.ring(51,38-lift,10,17,'amber')
    a.shape(((25,36-lift),(73,36-lift),(79,85-lift),(20,85-lift)),'ochre',8,'gold')
    a.shape(((73,36-lift),(83,43-lift),(88,79-lift),(79,85-lift)),'umber',8,'amber')
    a.shape(((27,42-lift),(68,42-lift),(73,79-lift),(25,79-lift)),'ink',8,'amber')
    a.oval(49,61-lift,12,13,'gold',5,'amber')
    for i in range(8):
        b=i*tau/8
        a.line(((49+15*cos(b),61-lift+15*sin(b)),
                (49+19*cos(b),61-lift+19*sin(b))),'amber')
    a.glint(49,61-lift,9)


def train(c,p):
    a=Art(c,p)
    shift=(1-p)*18
    a.shape(((10,39),(35,36),(65,20),(81,20),(89,29),(89,75),(79,85),(64,84),(10,62)),
            'umber',8,'amber')
    a.shape(((58-shift,30),(68-shift,20),(84-shift,22),(91-shift,32),(91-shift,73),
             (85-shift,83),(66-shift,83),(58-shift,73)), 'ochre',8,'gold')
    a.shape(((63-shift,32),(85-shift,32),(85-shift,49),(63-shift,49)),'ink',8,'amber')
    a.line(((74-shift,33),(74-shift,48)),'amber')
    for i in range(5):
        x=15+i*8
        a.line(((x,43-i*2),(x+4,43-i*2)),'gold')
    for x in (64-shift,85-shift):a.oval(x,64,3.5,4.5,'gold',8,'white')
    a.line(((68-shift,75),(82-shift,75)),'white')
    a.line(((7,71),(54,86),(68,98)),'ochre')
    a.line(((11,63),(73,84),(91,97)),'gold')


DRAFTS=(
    ('Golden Tube TV',draw_golden_tube_tv),('Investigation Glasses',glasses),('Rainy Window',rain),
    ('Fog over Inaba',fog_town),('Midnight Broadcast',broadcast),('Into the TV',portal),
    ('Shuffle Time',arcana),('Junes Shopping Bag',shopping),('Train to Inaba',train),
)
