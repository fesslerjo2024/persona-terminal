"""Three independently staged Oracle scenes drawn on the 2×4 dot canvas."""
from math import cos, sin, pi, tau

from detail_canvas import DotCanvas
from oracle_scene import GUARD, SUPPORT, TITLE, SCENES as LEGACY_SCENES
from wide_allout import Rig, THEME, _runner, _shadow, _burst, _cross, ease


def _bound(t,a,b):return max(0.,min(1.,(t-a)/(b-a)))

def _ship(c,x,y,sx,sy,t):
    r=Rig(c,x,y,sx,sy)
    flare=ease(t/.28)
    # The lip and open vent are drawn below the canopy for clear depth cues.
    r.disk('navy',0,10,49,20,8,'green')
    r.disk('teal',0,7,47,12,6,'green')
    r.plane('navy',((-47,7),(-41,-1),(-25,-5),(-19,-16),(-11,-22),(13,-22),(24,-13),(26,-5),(43,-1),(48,7),(40,16),(25,20),(-24,20),(-39,16)),8,'green')
    r.plane('forest',((-42,4),(-29,0),(-20,-3),(21,-3),(32,0),(42,5),(18,8),(-23,8)),7,'teal')
    r.plane('navy',((-22,-3),(-17,-15),(-11,-20),(9,-21),(19,-13),(22,-4),(16,1),(-16,1)),8,'teal')
    r.plane('teal',((-19,-4),(-16,-13),(-9,-18),(10,-18),(16,-11),(19,-4),(12,-6),(-11,-7)),6,'cyan')
    r.plane('forest',((-40,11),(-27,10),(22,10),(41,12),(30,16),(-22,17)),6,'green')
    r.plane('navy',((-14,17),(-14,24),(-7,28),(8,28),(14,24),(14,17)),8,'teal')
    r.disk('green',0,24,8,3,6,'white')
    for j in range(11):
        x0=(j-5)*7.3
        y0=11+3*cos(j*.58)
        r.disk('white' if j%5==int(12*t)%5 else 'green',x0,y0,2.1,1.8,6,'teal')
        if j%2==0:r.line('teal',(x0-2,y0+3),(x0+2,y0+3))
    r.line('white',(-14,-14),(-9,-17),(1,-17))
    r.line('cyan',(10,-17),(16,-12),(17,-8))
    for j in range(5):
        x0=-9+j*4.5
        r.line(('white','teal','cyan')[j%3],(x0,24),(x0*.7,27+4*flare))
    return r.p(0,26)

def _nebula(c,t,ink):
    W,H=c.w,c.h
    # Off-center orbital arcs and circuit horizon are layered but not boxed.
    for k in range(3):
        c.ring(W*.26,H*.57,W*(.46+k*.028),H*(.44+k*.043),'teal' if k==1 else 'navy',3.12,6.20,92)
        c.ring(W*.76,H*.65,W*(.38+k*.035),H*(.22+k*.025),ink if k==0 else 'navy',.1,2.9,71)
    for i in range(68):
        x=(i*53+round(t*8)*(i%3+1)+i//4)%W
        y=(i*31+9*(i//9))%H
        if (i+int(t*8))%13==0:_cross(c,x,y,2,3,'cyan')
        else:c.put(x,y,ink if i%7==0 else 'navy')
    for i in range(11):
        x=W*i/10
        y=H*(.89+i%3*.03)
        c.path(((W*.51+(x-W*.51)*.20,H*.69),(W*.51+(x-W*.51)*.34,H*.76),(x,H*.94)),'navy')
        c.line((x,y),(x+W*.06,y),'forest' if i%2 else 'teal')

def _cockpit(c,t):
    W,H=c.w,c.h
    p=ease(t/.22)
    # Green perspective glass inset, instrument roll, Futaba's head and hands.
    c.face(((W*.01,H*.88),(W*.18,H*.12),(W*.68,0),(W*.92,H*.24),(W*.99,H*.85),(W*.88,H),(W*.10,H)),
           'navy',8,'teal')
    c.face(((W*.12,H*.79),(W*.27,H*.18),(W*.65,H*.08),(W*.85,H*.31),(W*.89,H*.76),(W*.63,H*.88),(W*.39,H*.92)),
           'forest',4,'green')
    c.path(((W*.07,H*.84),(W*.19,H*.24),(W*.29,H*.11),(W*.65,H*.02),(W*.86,H*.20),(W*.97,H*.63)),'cyan')
    for i in range(14):
        xx=W*(.18+i*.047)
        yy=H*(.73+.08*sin(i*1.7))
        c.path(((xx,H*.88),(xx+4,yy),(xx-4,yy),(xx-3,yy-8)),'teal')
        c.ellipse(xx-3,yy-8,2,3,('green','cyan','amber')[i%3],5)
    f=Rig(c,W*(.49+.08*(1-p)),H*.53,W/254,H/184)
    f.plane('navy',((-55,53),(-40,26),(-25,13),(-13,12),(20,13),(40,20),(58,46),(47,64),(-47,64)),8,'green')
    f.plane('forest',((-54,53),(-47,35),(-28,28),(-13,30),(-21,47),(-32,60)),7,'teal')
    f.plane('teal',((13,21),(36,22),(48,34),(34,42),(19,31)),7,'cyan')
    f.plane('wine',((-32,17),(-37,-26),(-27,-48),(-8,-53),(16,-48),(39,-27),(35,5),(44,27),(38,36),(25,29),(17,15),(-19,15),(-26,34),(-37,36)),8,'amber')
    f.plane('white',((-27,-24),(-9,-37),(14,-35),(30,-19),(28,3),(17,13),(-8,17),(-23,7)),8,'teal')
    f.plane('ochre',((-31,-24),(-18,-39),(-2,-46),(14,-43),(25,-37),(32,-25),(30,-13),(15,-24),(10,-15),(2,-25),(-8,-18),(-15,-26),(-25,-12)),8,'amber')
    f.plane('navy',((-31,-17),(-12,-23),(1,-17),(13,-21),(34,-17),(32,0),(22,9),(7,4),(1,-3),(-7,3),(-22,8),(-30,3)),8,'green')
    for k in (-1,1):
        f.ring('cyan',k*15,-7,10,7);f.disk('green',k*16,-7,4,4);f.disk('white',k*16-1,-8,1.3,2.1)
    for i in range(4):
        q=4*sin(t*18+i)
        f.plane('navy',((-19+i*9,41+q),(-11+i*9,36+q),(-8+i*9,44+q),(-14+i*9,50+q)),8,'green')
    f.plane('teal',((-49,61),(-39,50),(42,49),(49,59),(53,82),(-54,82)),8,'cyan')
    for j in range(9):
        f.disk('white' if j==int(t*40)%9 else 'green',-32+j*8,58+sin(j*3)*2,2.5,2.8)
    return 'cockpit'

def _orb(c,x,y,w,h,t):
    c.ellipse(x,y,w,h,'forest',7,'green')
    c.ring(x,y,w*.78,h*.78,'cyan',t*7,t*7+4.6)
    c.ring(x,y,w*.58,h*.56,'green',t*4+2,t*4+6)
    c.ellipse(x,y,w*.36,h*.38,'teal',7,'green')
    _cross(c,x,y,w*.61,h*.37,'white' if t>.78 else 'cyan')

def _field_art(c,t,ink,x,y,p):
    W,H=c.w,c.h
    for j in range(4):
        c.ring(x,y,W*(.08+j*.042+.18*p),H*(.035+j*.028+.11*p),
               ink if j%2 else 'teal',3.0-p,tau+p)
    _burst(c,x,y,W*.57,H*.48,ink,'teal',p,29)
    for i in range(29):
        k=(i*39%29-14)/14
        x1=x+W*.26*k*p;y1=y-H*(.11+(i*11%13)*.019)*p
        c.line((x1,y1),(x1+k*3,y1+3),'green' if i%5 else 'white')

def _futaba_out(c,x,y,scale,t):
    r=Rig(c,x,y,scale*.62,scale,-1)
    bob=5*sin(t*3*pi)
    r.plane('navy',((-20,15),(-23,-8),(-13,-20),(7,-20),(23,-8),(20,16),(12,27),(-9,28)),8,'green')
    r.plane('teal',((-17,2),(-10,-5),(3,-5),(13,2),(12,18),(-6,21)),7,'cyan')
    r.plane('green',((-17,4),(-30,11+bob),(-31,18+bob),(-20,18+bob),(-9,12)),8,'teal')
    r.plane('green',((14,2),(24,6-bob),(32,6-bob),(29,14-bob),(19,18-bob),(10,12)),8,'teal')
    r.plane('wine',((-16,-15),(-21,-32),(-10,-47),(10,-49),(27,-41),(28,-25),(20,-19),(17,-11),(8,-17),(-8,-15),(-21,-7)),8,'amber')
    r.plane('white',((-13,-36),(5,-42),(23,-35),(21,-19),(10,-16),(-4,-18)),7,'teal')
    r.plane('navy',((-14,-34),(0,-37),(21,-34),(22,-27),(12,-22),(2,-24),(-8,-24)),8,'green')
    r.disk('cyan',1,-31,4,4);r.disk('green',14,-30,4,4)
    r.line('rose',(22,-38),(24,-30),(27,-22),(29,-14))
    r.line('green',(-10,27),(-17,38+bob),(-23,40+bob))
    r.line('green',(9,25),(22,32-bob),(24,40-bob))

def _payload(c,t,targets):
    W,H=c.w,c.h
    ink='green'
    if t<.63:return _cockpit(c,t)
    _nebula(c,t,ink)
    release=_bound(t,.78,1.72)
    splash=_bound(t,1.72,2.39)
    end=ease((t-2.40)/.75)
    x0=W*(.51+.26*end);y0=H*(.27-.22*end)
    field_x,field_y=W*.56,H*.76
    times=max(1,min(5,targets or 3))
    if t<1.72:
        for i in range(times):
            _shadow(c,field_x+W*.105*(i-(times-1)/2),field_y+(i%2)*H*.041,W/660,H/548,'teal')
    if t>=1.72:
        _field_art(c,t,'green' if t<2.12 else 'gold',field_x,field_y,splash)
    rim=_ship(c,x0,y0,W*(.0088-.0013*end),H*(.0072-.0021*end),t)
    if t<1.72:
        x,y=(rim[0]+(field_x-rim[0])*release,rim[1]+(field_y-rim[1])*release**1.48)
        _orb(c,x,y,W*(.021+.013*release),H*(.034+.023*release),release)
        c.path((rim,(rim[0]-W*.017,y-H*.084),(x,y-H*.035)),ink)
    if 1.43<t<2.09:
        u=(t-1.43)/.66
        x=W*(.80-.048*u);y=H*(.49+.25*u-.11*sin(u*pi))
        _futaba_out(c,x,y,min(W,H)*.0098,u)
        for i in range(5):
            c.line((x+W*.037+i*2,y-i*4),(x+W*.083+i*3,y-i*5),'green')
    if t>=2.39:
        # Finisher close-up echoes the game's green computer-pattern artwork.
        f=Rig(c,W*(.78+.11*(1-end)),H*.60,W/244,H/132,-1)
        f.plane('navy',((-38,50),(-28,14),(-8,7),(18,14),(45,47),(39,68),(-44,69)),8,'green')
        f.plane('wine',((-31,43),(-40,2),(-38,-30),(-18,-47),(10,-50),(33,-38),(43,-17),(35,4),(47,33),(35,45),(24,26),(9,9),(-16,8),(-26,43)),8,'amber')
        f.plane('white',((-23,-25),(8,-33),(30,-19),(25,4),(11,19),(-10,16),(-23,3)),7,'teal')
        f.plane('ochre',((-34,-28),(-22,-37),(-13,-42),(10,-46),(29,-35),(36,-23),(28,-14),(18,-23),(4,-17),(-2,-25),(-13,-18),(-17,-25),(-28,-12)),8,'amber')
        f.plane('navy',((-28,-16),(-15,-22),(-3,-15),(9,-17),(30,-16),(31,-3),(23,5),(13,2),(2,-5),(-7,0),(-24,5)),8,'green')
        for z in (-1,1):
            f.ring('green',z*15,-8,10,8)
            f.disk('cyan',z*14,-8,3,4)
        f.line('teal',(-7,10),(4,12),(9,10))
        f.plane('green',((21,30),(27,18),(32,19),(30,27),(41,19),(45,23),(39,32),(45,39),(34,47),(29,55),(15,58),(14,50)),7,'cyan')
    return ('drop' if t<1.72 else 'blast' if t<2.39 else 'finisher')

def _ally(c,who,x,y,scale,t,guard=False):
    ink,sh,lit,*_=THEME.get(who,THEME['Joker'])
    if who=='Mona':
        _runner(c,who,x,y,scale*.81,1,t)
        return
    r=Rig(c,x,y,scale*.67,scale)
    tilt=10*(1-ease(t))
    r.plane('navy',((-24,29),(-18,-6+tilt),(-9,-18+tilt),(7,-19+tilt),(19,-11+tilt),(24,7),(24,26),(12,30),(-6,26)),8,ink)
    r.plane(sh,((-15,7),(-8,-10+tilt),(7,-7+tilt),(13,5),(9,20),(-14,19)),7,lit)
    if guard:
        r.plane('navy',((-22,5),(-30,-17),(5,-19),(19,0),(13,18),(-14,18)),8,'cyan')
        r.line('white',(-18,-12),(7,-13),(13,-1),(-12,10))
    else:
        r.plane(ink,((-23,-2+tilt),(-32,14),(-27,18),(-14,8),(-14,-2+tilt)),8,lit)
        r.plane(ink,((16,-9+tilt),(28,8),(25,16),(17,12),(9,3+tilt)),8,lit)
    r.plane('slate',((-12,-23+tilt),(-10,-38+tilt),(1,-43+tilt),(14,-36+tilt),(18,-26+tilt),(10,-18+tilt),(-1,-17+tilt)),8,ink)
    r.plane('white',((-10,-31+tilt),(-4,-34+tilt),(5,-31+tilt),(15,-33+tilt),(15,-27+tilt),(7,-24+tilt),(-5,-24+tilt)),7,ink)
    r.line('navy',(-9,-29+tilt),(1,-31+tilt),(12,-28+tilt))
    r.line('slate',(-9,20),(-7,28),(-14,32)); r.line('teal',(10,19),(10,29),(16,33))

def _support(c,t,cast):
    W,H=c.w,c.h
    _nebula(c,t,'cyan')
    hover=sin(t*3.1)*.020
    outlet=_ship(c,W*.49,H*(.25+.08*(1-ease(t/.36))+hover),W*.0081,H*.0070,t)
    people=tuple(cast)[:4] or ('Joker','Mona','Skull','Panther')
    for i,name in enumerate(people):
        x=W*(.5+(i-(len(people)-1)/2)*.184)
        y=H*(.70+.038*(i%2))
        beat=_bound(t,.46+i*.11,1.44+i*.12)
        c.ellipse(x,y+H*.167,W*.065,H*.013,'navy',6,'teal')
        if .05<beat:
            c.face((outlet,(x-W*.039*beat,y+H*.11),(x+W*.039*beat,y+H*.105)),
                   'forest' if beat<.8 else 'teal',2)
            for j in range(5):
                q=(beat+.175*j)%1
                r0=y+H*.13-H*.30*q
                r1=(1-q)*W*.035
                c.ring(x,r0,r1+1,H*.018+q*3,'green' if j%3 else 'cyan',-.02,4.9)
                _cross(c,x+W*.045*sin(i+q*6),r0,2+j%2,3+j%3,'green')
        _ally(c,name,x,y+H*.03,min(min(W,H)*(.008+.002*beat),W*.184/43),beat)
    return 'relay' if t<.70 else 'recover' if t<1.89 else 'rally'

def _hex(cx,cy,rx,ry,d=0):
    return tuple((cx+rx*cos(i*tau/6+d),cy+ry*sin(i*tau/6+d)) for i in range(6))

def _guard(c,t,cast):
    W,H=c.w,c.h
    _nebula(c,t,'teal')
    ready=ease((t-.38)/.62)
    pulse=_bound(t,1.17,1.97)
    disperse=_bound(t,1.82,2.8)
    cxx,cyy=W*.40,H*.73
    pxy=_ship(c,W*.31,H*(.18+.017*sin(t*4)),W*.0068,H*.0060,t)
    if ready:
        c.face((pxy,(cxx-W*.22*ready,cyy+H*.13),(cxx+W*.19*ready,cyy+H*.13)),
               'forest',2)
    people=tuple(cast)[:4] or ('Joker','Mona','Skull','Panther')
    for i,name in enumerate(people):
        x=W*(.40+(i-(len(people)-1)/2)*.124);y=H*(.74+(i%2)*.02)
        _ally(c,name,x,y,min(min(W,H)*.008,W*.124/38),_bound(t,.28,.66),.56<t<1.95)
    if ready:
        for j in range(4):
            px,py=W*(.44+.015*j),H*.61
            c.ring(px,py,W*(.168+j*.013)*ready,H*(.26+j*.016)*ready,
                   'white' if .06<pulse<.30 and j==0 else ('cyan' if j%2 else 'teal'),
                   3.22+disperse*.8,6.05+disperse*.72,82)
        for j in range(7):
            a=(j+1)*.41+3.14
            q=.90+.10*sin(j+t)
            x=W*.45+W*.200*q*ready*cos(a)
            y=H*.62+H*.30*q*ready*sin(a)
            mesh=_hex(x,y,W*.012,H*.031)
            c.path((*mesh,mesh[0]),'cyan' if j%2 else 'teal')
    threat=_bound(t,.18,1.18)
    if t<1.18:
        x=W*(1.06-.43*threat);y=H*(.22+.37*threat)
        c.face(((x,y),(x+W*.125,y-H*.07),(x+W*.19,y-H*.062),(x+W*.09,y+H*.030)),
               'red',7,'white')
        c.line((x,y),(x+W*.14,y-H*.006),'amber')
        for i in range(6):
            c.line((x+W*.06+i*4,y-3-i),(x+W*.28+i*4,y-H*.07-i*2),'wine')
    if pulse:
        x=W*.632;y=H*.588
        for j in range(5):
            c.ring(x,y,W*(.017+j*.013+pulse*.16),H*(.047+j*.017+pulse*.18),
                   'white' if j==2 and pulse<.45 else 'teal',3.9+pulse*.34,7.2+pulse*.43)
        _burst(c,x,y,W*.27,H*.43,'cyan','teal',pulse,18)
    return 'incoming' if t<.46 else 'shield' if t<1.18 else 'deflect' if t<2.02 else 'safe'

_SCENES={TITLE:(LEGACY_SCENES[TITLE][0],_payload,'green'),
         SUPPORT:(LEGACY_SCENES[SUPPORT][0],_support,'cyan'),
         GUARD:(LEGACY_SCENES[GUARD][0],_guard,'cyan')}

def render(title,elapsed,width,height,*,cast=(),targets=0,finishing=True):
    """Preserve each original battle cue, cast and native runtime."""
    t=max(0.,min(_SCENES[title][0],elapsed))
    c=DotCanvas(max(1,width),max(1,height))
    if title==TITLE:beat=_payload(c,t,targets)
    elif title==SUPPORT:beat=_support(c,t,cast)
    else:beat=_guard(c,t,cast)
    return beat,c.finish()
