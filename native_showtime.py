"""Eight original packed-dot adaptations of Persona 5 Royal's partner attacks."""
from dataclasses import dataclass
from math import cos, pi, sin

from showtime_detail_cast import Stage, actor, face, prop
from showtime_detail_sets import (arena, blossom, bowl, burst, chapel, city_roof, desert,
                                  diner, meadow, petals, rain, road_city, screens, seed,
                                  spark_fan, van)

ROSE='ROSE & REVOLVER'
ROAD='HIGHWAY TO TROUBLE'
BEEF='MIDNIGHT TAKEOUT'
DUEL='THE DUEL AT DUSK'
DRIVE='TEA IN THE CROSSHAIRS'
RING='PALACE BODY SLAM'
MASK='TWO SIDES OF THE MASK'
DANCE='THE LAST WALTZ'


def mix(a,b,p):return a+(b-a)*p

def ease(p):return p*p*(3-2*p)

def swoop(s,x,y,r,q,ink='white',shadow='rose'):
    a=-2.75+q*3.8
    s.arc(x,y,r,r*.65,shadow,a,a+1.8)
    s.arc(x,y,r-2,r*.65-2,ink,a+.12,a+1.6)
    s.arc(x,y,r-5,r*.65-5,shadow,a+.33,a+1.46)

def lens(s,x,y,c='wine'):
    s.oval(x,y,24,3.7,c,grain=4)

def bouquet(s,x,y,k,t):
    s.face('white',(x-23*k,y-6*k),(x+24*k,y-8*k),(x+10*k,y+17*k),(x+3*k,y+27*k),
           (x-6*k,y+25*k),edge='rose')
    for j in range(17):
        q=seed(j*315+49);a=2*pi*seed(j*851+32)
        px=x+q*21*k*cos(a);py=y+q*13*k*sin(a)
        s.line((x+2*k,y+23*k),(px,py),'forest')
        blossom(s,px,py,(2.2+seed(j*761+18))*k,'red','wine',j+t)
    s.path('rose',(x-5*k,y+14*k),(x+7*k,y+16*k),(x+12*k,y+25*k))


def _rose(s,i,p,t):
    meadow(s,t,near=i in (1,2,3))
    if i==0:
        lens(s,59,112)
        actor(s,'mona',59,78,1.21,pose='ready')
        actor(s,'panther',153,69,.7,-1,'reach')
        bouquet(s,83,79,.78,t)
    elif i==1:
        face(s,'mona',48,66,2.1)
        face(s,'panther',160,71,1.72,-1)
        bouquet(s,mix(88,109,ease(p)),68,1.36,t)
    elif i==2:
        actor(s,'panther',128,83,1.58,-1,'aim',-5)
        if p<.38:bouquet(s,74,79,1.12,t)
        else:
            x0,y0=prop(s,'smg',73,78,1.14,pi)
            petals(s,t,26,(6,108,39,117))
            s.line((x0,y0),(x0-13,y0),'white')
    elif i==3:
        x=57-3*(sin(p*27)**2)
        grip=actor(s,'panther',x,72,1.43,1,'aim',-4)
        px,py=prop(s,'smg',*grip,1.22,-.06)
        spark_fan(s,px-4,py,p*4,28,'rose','amber',.39)
        if int(p*12)%3!=1:burst(s,px+3,py,(p*14)%1,'rose','amber',14)
        actor(s,'shadow',178,90,.62,-1,'trip',-38)
    elif i==4:
        actor(s,'panther',151,78,.86,-1,'aim',-3)
        actor(s,'mona',41,96,1.08,pose='lift')
        prop(s,'bomb',mix(57,145,ease(p)),90-56*sin(pi*p),.89+sin(pi*p)*.3)
        petals(s,t,28)
    elif i==5:
        actor(s,'mona',29,99,.71,pose='ready')
        actor(s,'panther',66,75,.74,1,'ready')
        burst(s,145,84,p,'rose','amber',39)
        petals(s,t*1.8,72)
        for j in range(8):
            a=j*pi/4+t
            blossom(s,146+44*p*cos(a),83+29*p*sin(a),1.1,'red','wine',a)
    else:
        actor(s,'panther',118,71,1.01,-1,'ready')
        actor(s,'mona',76,94,.73,pose='ready')
        petals(s,t,57)


def tire(s,x,y,k,t):
    s.oval(x,y,28*k,31*k,'navy',edge='slate')
    s.arc(x,y,23*k,26*k,'cyan')
    s.arc(x,y,21*k,24*k,'red')
    s.oval(x,y,5*k,5*k,'slate',edge='ochre')
    for j in range(8):
        a=j*pi/4+t
        s.line((x+cos(a)*6*k,y+sin(a)*6*k),(x+cos(a)*19*k,y+sin(a)*23*k),'slate')


def _road(s,i,p,t):
    desert(s,t)
    if i==0:
        tire(s,27+11*ease(p),102,.63,t*2)
        actor(s,'skull',39+11*ease(p),61,.86,1,'run',-8)
        actor(s,'queen',158,72,.69,-1,'ready')
    elif i==1:
        face(s,'skull',56,59,2.1)
        prop(s,'can',128,63,1.38,p*.48-.22)
        for j in range(9):
            s.line((117+seed(j*704)*32,57+seed(j*706)*20),(152,52+seed(j*710)*31),'amber')
    elif i==2:
        actor(s,'skull',53,73,1.15,1,'reach')
        actor(s,'queen',151,72,1.20,-1,'reach')
        prop(s,'can',mix(88,115,ease(p)),54+7*sin(p*pi),.96,p*pi*.9)
    elif i==3:
        x=mix(62,116,ease(p))
        spark_fan(s,150,78,p*4,26,'ochre','amber',.77,-1)
        actor(s,'shadow',169,90,.75,-1,'trip',p*40)
        grip=actor(s,'queen',x,77,1.20,1,'punch' if p<.68 else 'kick',-7+sin(p*25)*8)
        swoop(s,*grip,25,(p*4)%1,'gold','red')
        if int(p*23)%5 in (2,3):burst(s,164,77,(p*17)%1,'red','amber',16)
    elif i==4:
        face(s,'queen',99,57,2.15)
        s.face('navy',(57,106),(59,86),(67,77),(83,75),(101,87),(115,108),
               (91,118),(67,115),edge='slate')
        prop(s,'can',88,92,.92-p*.46,.17)
        if p>.26:spark_fan(s,77,94,p,12,'rose','white',.42,-1)
    elif i==5:
        actor(s,'skull',41,79,.85,1,'ready')
        actor(s,'queen',76,80,.88,1,'punch',-8)
        for j in range(7):
            s.arc(144,84-3*j,17+j*6,6+j*3,'ochre' if j%2 else 'amber',.3,5.8)
        burst(s,147,80,p,'amber','gold',26)
    else:
        actor(s,'skull',69,70,1,1,'lift')
        actor(s,'queen',124,75,1,-1,'ready')
        prop(s,'can',97,47,.53,-.55)


def boards(s,t,p):
    for j in range(22):
        z=seed(j*491+11)
        a=seed(j*897+38)*2*pi; r=p*(30+z*75)
        x=104+cos(a)*r;y=62+sin(a)*r*.6
        dx=cos(a+t*.6)*(2+z*7);dy=sin(a+t*.6)*(2+z*7)
        s.face('ochre' if j%3 else 'amber',(x-dx,y-dy),(x+dx,y+dy),(x+dx+2,y+dy-2),
               (x-dx+2,y-dy-2),edge='red')


def dinner_close(s,x,y,k,d,who):
    def pt(a,b): return (x+a*k*d,y+b*k)
    coat='ink' if who=='skull' else 'indigo'
    s.face(coat,pt(-24,25),pt(-12,17),pt(12,16),pt(25,26),pt(34,47),
           pt(-35,47),edge='slate')
    s.face('ochre' if who=='skull' else 'slate',pt(-15,22),pt(-9,19),
           pt(0,26),pt(13,18),pt(18,24),pt(6,36),pt(1,32),pt(-5,35))
    s.path('red' if who=='skull' else 'teal',pt(-2,26),pt(4,33),pt(6,46))
    face(s,who,x,y,k,d)

def _beef(s,i,p,t):
    diner(s,t,counter=i in (0,1,2,6),open_door=i in (3,4,5,6))
    if i==0:
        dinner_close(s,47,60,1.68,1,'skull')
        dinner_close(s,151,56,1.49,-1,'fox')
        bowl(s,104,94,1.0,t)
    elif i==1:
        actor(s,'fox',119,82,1.29,-1,'reach',-7)
        bowl(s,80,86,1.1,t)
    elif i==2:
        dinner_close(s,63,51,1.58,1,'skull')
        bowl(s,108,96,1.45,t)
        s.path('gold',(32,79),(54,64),(94,71))
        s.path('amber',(32,81),(55,67),(95,74))
        for j in range(9):s.path('red',(99+j,74),(99+j*1.1,84),(96+j,88))
    elif i==3:
        if p<.25:
            s.path('rose',(89,41),(100,51),(95,61),(107,78))
            s.path('amber',(126,43),(115,55),(119,67),(109,80))
        else:
            actor(s,'shadow',105,81,.9,1,'run')
            boards(s,t,(p-.23)*1.6)
            burst(s,104,62,p,'rose','amber',27)
    elif i==4:
        actor(s,'fox',60,80,.95,1,'slash',-11)
        x,y=actor(s,'skull',119,75,1.04,1,'aim',-6)
        xx,yy=prop(s,'gun',x,y,1.0,-.07)
        spark_fan(s,xx,yy,p*3,15,'gold','rose',.32)
        bowl(s,92,103,.7,t)
    elif i==5:
        x,y=actor(s,'fox',72+27*ease(p),81,1.18,1,'slash',-14)
        prop(s,'katana',x,y,.94,-.57+p*.65)
        swoop(s,143,75,35,p,'cyan','rose')
        actor(s,'shadow',174,86,.65,-1,'trip',-24-p*50)
        boards(s,t,p*.6)
    else:
        dinner_close(s,47,60,1.64,1,'skull')
        dinner_close(s,154,58,1.43,-1,'fox')
        bowl(s,102,95,1.10,t)
        s.path('gold',(25,82),(53,70),(81,80));s.path('amber',(25,85),(53,73),(81,83))


def umbrella_sweep(s,x,y,p):
    prop(s,'parasol',x,y,1.07,-.4+p*.7)
    swoop(s,x+12,y+3,29,p,'white','rose')


def _duel(s,i,p,t):
    screens(s,t,pan=18*ease(p) if i in (2,4) else 0)
    if i==0:
        actor(s,'fox',68,78,.99,1,'ready')
        actor(s,'shadow',153,76,.9,-1,'ready')
        face(s,'fox',29,43,.49)
    elif i==1:
        face(s,'fox',70,68,2.18)
        prop(s,'katana',127,96,1.48,-.98+p*.21)
        s.path('cyan',(134,79),(149,58),(154,47))
    elif i==2:
        x,y=actor(s,'fox',53+31*ease(p),76,1.07,1,'slash',-10)
        prop(s,'katana',x,y,1,-.95+p*1.1)
        actor(s,'shadow',143,81,.77,-1,'trip',p*21)
        petals(s,t,22)
    elif i==3:
        x=134-14*ease(p);y=35+34*ease(p)
        actor(s,'fox',55,83,.73,1,'kneel')
        actor(s,'panther',x,y,.94,-1,'float',-13+p*15)
        prop(s,'parasol',x-20,y-19,1.1,-.30+p*.44)
        petals(s,t,59)
    elif i==4:
        actor(s,'panther',84,74,1.11,1,'slash',-14)
        umbrella_sweep(s,113,56,p)
        x,y=actor(s,'fox',121,90,.90,1,'slash',-7)
        prop(s,'katana',x,y,.87,-1.03+p*1.04)
        actor(s,'shadow',167,87,.64,-1,'trip',-18)
    elif i==5:
        x,y=actor(s,'fox',99,82,1.03,1,'slash',-4)
        prop(s,'katana',x,y,1.05,-.47-p*.3)
        actor(s,'panther',47,76,.96,1,'reach')
        burst(s,162,74,p,'violet','white',30)
        petals(s,t,55)
    else:
        actor(s,'fox',122,78,1.03,1,'ready')
        actor(s,'panther',74,77,.98,-1,'ready')
        prop(s,'parasol',56,41,1.1,.16)
        petals(s,t,52)


def _drive(s,i,p,t):
    road_city(s,t if i in (0,6) else t*1.43)
    if i==0:
        actor(s,'mona',67,91,.94,pose='ready')
        actor(s,'noir',139,73,.99,-1,'ready')
    elif i==1:
        if p<.4:
            actor(s,'mona',98,83,1.30,pose='ready')
            s.arc(100,68,32+p*22,29+p*12,'amber',p,5.9+p)
        else:
            van(s,99,83,.53+ease(p)*.69,True)
            spark_fan(s,65,77,p,22,'rose','gold',.48,-1)
    elif i==2:
        x=79+p*25; y=94+4*sin(p*pi)
        van(s,x,y,1.16,False)
        actor(s,'noir',x-7,53-29*sin(p*pi),.70,1,'arc',-23+p*25)
    elif i==3:
        van(s,101,89,.76+ease(p)*.45,True)
        grip=actor(s,'noir',105,53,.72,1,'kneel',-6)
        prop(s,'launcher',*grip,.81,-.17)
        spark_fan(s,106,108,p,23,'violet','rose',.52)
    elif i==4:
        van(s,71,103,1.42,False)
        x,y=actor(s,'noir',70,68,1.10,1,'aim',-4)
        a,b=prop(s,'launcher',x,y,1.10,-.23)
        spark_fan(s,a,b,p*3,26,'violet','amber',.49)
        if int(p*8)%3:burst(s,a+7,b,(p*7)%1,'gold','amber',13)
    elif i==5:
        van(s,80,95,.98,False)
        burst(s,146,80,p,'rose','amber',36)
        spark_fan(s,144,80,3*p,25,'violet','rose',.65)
    else:
        van(s,102,91,.9-.64*ease(p),False)
        for j in range(7):
            x=128+seed(j*809)*56*ease(p);y=95-seed(j*943)*48*ease(p)
            s.arc(x,y,5+j*1.4,4+j*.5,'violet',.14+j,3+j)


def _ring(s,i,p,t):
    arena(s,t,close=i in (1,2,3,5,6),front=i in (0,4))
    if i==0:
        actor(s,'queen',54+7*p,76-4*sin(pi*p),.65,1,'ready')
        actor(s,'noir',131-7*p,75-3*sin(pi*p),.63,-1,'ready')
        actor(s,'shadow',109+3*p,88,.53,-1,'ready')
    elif i==1:
        x,y=actor(s,'queen',60,79,1.16,1,'aim',-8)
        actor(s,'noir',142,72,1.06,-1,'reach')
        s.path('rose',(x+1,y+3),(111,69),(120,63))
    elif i==2:
        x=117-16*ease(p); y=99-45*sin(p*pi*.65)
        actor(s,'noir',x,y,.92,-1,'arc',-20-p*23)
        actor(s,'queen',132,90,.91,1,'lift',4)
        for j in range(6):
            s.arc(x+10-j*2,y+12,36+j*3,23+j*2,'gold' if j%2 else 'red',1.25,2.67)
    elif i==3:
        actor(s,'shadow',125,82,1.02,-1,'trip',-10-p*36)
        actor(s,'queen',55+41*ease(p),77,1.12,1,'kick',-22-p*24)
        if p>.30:swoop(s,123,78,45,p,'white','amber')
    elif i==4:
        actor(s,'noir',102+8*p,32+45*ease(p),.96,1,'arc' if p<.65 else 'float',-79+55*p)
        actor(s,'shadow',116,85,.72,-1,'dip',-48)
        spark_fan(s,108,69,p*3,28,'gold','amber',.53,-1)
    elif i==5:
        actor(s,'queen',47,82,.94,1,'kneel')
        actor(s,'noir',111,72,.92,-1,'kneel',-38)
        burst(s,116,95,p,'amber','white',32)
        s.arc(118,106,22+p*52,5+p*7,'amber')
    else:
        actor(s,'queen',63,75,1.06,1,'ready')
        actor(s,'noir',137,75,1.06,-1,'lift')
        s.arc(141,63,39,28,'gold',3.8,5.8)


def cable(s,x,y,anchor,tail):
    s.path('slate',anchor,(x*.6+anchor[0]*.4,y*.6+anchor[1]*.4),(x,y))
    s.path('white',(anchor[0]+1,anchor[1]),(x+1,y))
    s.path('red',(x,y),tail)


def _mask(s,i,p,t):
    city_roof(s,t)
    if i==0:
        face(s,'crow',117,65,2.16)
        actor(s,'joker',38,74,.74,1,'ready')
    elif i==1:
        face(s,'crow',100,59,2.36)
        # A warm glint from the visor is the reference shot's focal point.
        s.oval(120,56,7,4.2,'wine')
        s.oval(120,56,4.3,2.7,'red',edge='rose')
        s.oval(120,56,2.1,1.4,'white')
        s.line((104-14*p,56),(133+16*p,56),'red')
        s.line((115,56),(125,56),'white')
        for j in range(11):
            a=j*pi*2/11
            s.path('red' if j%3==0 else 'wine',(102+cos(a)*31,60+sin(a)*24),
                   (101+cos(a-.12)*(53+p*13),60+sin(a-.12)*38),
                   (101+cos(a)*81,60+sin(a)*57))
    elif i==2:
        x=mix(53,119,ease(p))
        u,v=actor(s,'crow',x,82,1.16,1,'run',-8)
        prop(s,'blade',u,v,.92,-.95)
        ux,vy=actor(s,'joker',102+24*ease(p),29+9*sin(pi*p),.83,1,'arc',-28+p*13)
        cable(s,ux,vy,(32,-4),(ux+5,vy+9))
        rain(s,t,25,'slate')
    elif i==3:
        u,v=actor(s,'joker',85+36*ease(p),52+27*ease(p),1.1,1,'slash',-32+p*30)
        prop(s,'blade',u,v,1.03,-.64+p*.8)
        actor(s,'shadow',158,86,.72,-1,'trip',p*48)
        swoop(s,143,65,41,p,'white','teal')
    elif i==4:
        phase=(p*5)%1
        x=86+29*ease(p)+sin(p*14)*11
        u,v=actor(s,'crow',x,80,1.16,1,'slash',-11+17*sin(p*14))
        prop(s,'blade',u,v,1.23,-.68+phase*.56)
        actor(s,'shadow',162,89,.75,-1,'trip',-38)
        for j in range(3):
            swoop(s,149+j*5,67+j*7,33+j*2,(phase+.2*j)%1,'white' if j==0 else 'rose','violet')
    elif i==5:
        u,v=actor(s,'joker',62,79,1.47,1,'aim',-3)
        x,y=prop(s,'gun',u,v,1.15,-.06)
        actor(s,'crow',146,82,.81,-1,'dip',-22)
        if p>.25:
            spark_fan(s,x,y,p,21,'red','amber',.35)
            burst(s,x+5,y,(p-.25)*1.3,'rose','amber',17)
    else:
        actor(s,'joker',66,79,1.05,-1,'ready')
        u,v=actor(s,'crow',134,78,1.04,1,'ready')
        prop(s,'blade',u,v,.71,.92)
        rain(s,t,28,'slate')


def shadow_cross(s,x,y,p):
    for a in (-1,1):
        for j in range(3):
            u=x+a*(28+j*8)+p*15
            s.path('rose' if j%2==0 else 'white',(u,y+12+j*4),(x+4,y),(x-a*49,y-25+j*3))


def _dance(s,i,p,t):
    chapel(s,t,dream=i in (3,4,5))
    if i==0:
        actor(s,'violet',68+7*ease(p),73-2*sin(pi*p),.99,1,'ready')
        actor(s,'joker',142-7*ease(p),69,.91,-1,'reach')
        petals(s,t,12,(2,198,25,96))
    elif i==1:
        x=mix(57,123,ease(p))
        a,b=actor(s,'joker',x,61-22*sin(pi*p),1.01,1,'arc',-31+p*32)
        cable(s,a,b,(79,-6),(a-7,b+8))
        actor(s,'violet',59+15*p,85,.82,1,'run',-7)
    elif i==2:
        x=81+37*ease(p);y=71-24*sin(p*pi)
        a,b=actor(s,'violet',x,y,1.20,1,'float',-29+p*33)
        prop(s,'blade',a,b,1.09,-.42)
        swoop(s,x+21,y+1,38,p,'white','violet')
        petals(s,t,36)
    elif i==3:
        # The fantasy dance uses Violet's unmasked echo, not a text cutaway.
        face(s,'violet',82,70,1.83)
        s.oval(141,63,32,33,'rose',grain=3,edge='white')
        actor(s,'echo',143,89,1.01,-1,'reach',-7+12*ease(p))
        petals(s,t,31)
    elif i==4:
        x=86+22*sin(pi*p)
        a,b=actor(s,'violet',x,75,1.03,1,'slash',-25+37*p)
        prop(s,'blade',a,b,1.04,-.92+p*.5)
        actor(s,'echo',153-12*ease(p),78,.84,-1,'arc',18)
        swoop(s,110,75,46,p,'white','violet')
        petals(s,t,47)
    elif i==5:
        actor(s,'violet',83+22*p,75,1.0,1,'slash',-23)
        actor(s,'shadow',145,86,.73,-1,'trip',-14-p*35)
        shadow_cross(s,145,68,p)
        if p>.34:burst(s,147,73,p,'violet','rose',26)
    else:
        # Joker supports the final low dip back in the stained-glass room.
        actor(s,'joker',110,75,1.08,-1,'reach',7)
        actor(s,'violet',87,77+14*ease(p),1.05,1,'dip',37+28*ease(p))
        petals(s,t,31)


@dataclass(frozen=True)
class Reel:
    stages: tuple
    draw: object


REELS={
    ROSE:Reel(((1.08,'Meadow'),(2.12,'Bouquet'),(3.08,'Unwrap'),(4.45,'Gunfire'),
               (5.63,'Bomb'),(6.12,'Flower burst'),(7.78,'Petals')),_rose),
    ROAD:Reel(((1.06,'Wasteland'),(2.,'Soda'),(2.93,'Handoff'),(4.65,'Fist flurry'),
               (5.79,'Crushed can'),(6.23,'Dust impact'),(7.91,'Dust settles')),_road),
    BEEF:Reel(((1.13,'Late night'),(2.15,'Beef bowl'),(3.26,'Chopsticks'),(4.52,'Door breaks'),
               (5.59,'Gunfire'),(6.29,'Counterstrike'),(7.92,'Back to dinner')),_beef),
    DUEL:Reel(((1.,'Kabuki set'),(2.1,'Draw'),(3.35,'First strike'),(4.57,'Parasol'),
               (5.67,'Crossing blades'),(6.31,'Impact'),(8.4,'Flowers')),_duel),
    DRIVE:Reel(((1.,'Meeting'),(2.12,'Transformation'),(3.43,'Boarding'),(4.67,'Chase'),
                (5.8,'Launcher'),(6.62,'Detonation'),(8.45,'Drive past')),_drive),
    RING:Reel(((1.16,'Arena'),(2.28,'Tag'),(3.52,'Vault'),(4.72,'Dropkick'),
               (6.24,'Body slam'),(7.08,'Impact'),(8.9,'Celebration')),_ring),
    MASK:Reel(((.86,'Storm'),(1.83,'Berserk'),(2.95,'Grapple'),(3.80,'Knife'),
               (5.35,'Blade flurry'),(6.27,'Gunshot'),(7.30,'Aftermath')),_mask),
    DANCE:Reel(((.95,'Chapel'),(2.55,'Grapple'),(3.40,'Vault'),(4.29,'Echo'),
                (5.83,'Dance'),(6.49,'Crossing blades'),(7.98,'Final dip')),_dance),
}
DURATIONS={title:reel.stages[-1][0] for title,reel in REELS.items()}


def render(title,t,w,h):
    reel=REELS[title]
    t=max(0.,min(t,DURATIONS[title]))
    s=Stage(w,h)
    start=0.
    for i,(end,beat) in enumerate(reel.stages):
        if t<end or i==len(reel.stages)-1:
            reel.draw(s,i,(t-start)/(end-start),t)
            return beat,s.finish()
        start=end
    raise AssertionError('A reel must define at least one stage')
