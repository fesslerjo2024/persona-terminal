"""Original vector silhouettes and props for the Persona 5 Showtime reel."""
from math import atan2, cos, pi, sin

from ..shared.detail_canvas import DotCanvas


class Stage:
    """Shot coordinates use a common 200×128 illustration space, not a cel."""
    def __init__(self,w,h):
        self.d=DotCanvas(w,h); self.sx=(self.d.w-1)/200; self.sy=(self.d.h-1)/128
    def point(self,p):
        return p[0]*self.sx,p[1]*self.sy
    def dot(self,x,y,c):
        x,y=self.point((x,y)); self.d.put(round(x),round(y),c)
    def line(self,a,b,c):
        self.d.line(self.point(a),self.point(b),c)
    def path(self,c,*pts):
        self.d.path(tuple(map(self.point,pts)),c)
    def face(self,c,*pts,grain=8,edge=None):
        self.d.face(tuple(map(self.point,pts)),c,grain,edge)
    def oval(self,x,y,rx,ry,c,grain=8,edge=None):
        self.d.ellipse(x*self.sx,y*self.sy,rx*self.sx,ry*self.sy,c,grain,edge)
    def arc(self,x,y,rx,ry,c,start=0,end=2*pi):
        self.d.ring(x*self.sx,y*self.sy,rx*self.sx,ry*self.sy,c,start,end)
    def box(self,x,y,X,Y,c,grain=8,edge=None):
        self.face(c,(x,y),(X,y),(X,Y),(x,Y),grain=grain,edge=edge)
    def finish(self):
        return self.d.finish()


# hair, cloth, contour highlight, accessories, mask, skin
_SKINS={
    'panther':('gold','wine','red','rose','red','amber'),
    'skull':('gold','ink','navy','gold','white','amber'),
    'queen':('ochre','ink','slate','cyan','slate','amber'),
    'fox':('ink','indigo','navy','teal','white','amber'),
    'noir':('amber','plum','rose','violet','ink','amber'),
    'joker':('ink','ink','slate','red','white','amber'),
    'crow':('ink','ink','navy','red','ink','slate'),
    'violet':('red','indigo','violet','rose','ink','white'),
    'echo':('wine','white','rose','rose','navy','white'),
    'shadow':('plum','plum','violet','rose','violet','slate'),
}


def limb(s,a,b,width,base,highlight):
    angle=atan2(b[1]-a[1],b[0]-a[0])+pi/2
    cx,cy=cos(angle)*width,sin(angle)*width
    s.face(base,(a[0]+cx,a[1]+cy),(b[0]+cx*.8,b[1]+cy*.8),
           (b[0]-cx*.8,b[1]-cy*.8),(a[0]-cx,a[1]-cy),edge=highlight)
    s.line((a[0]-cx*.3,a[1]-cy*.3),(b[0]-cx*.3,b[1]-cy*.3),highlight)


def face(s,who,x,y,k=1,d=1):
    def pts(coords):
        return tuple((x+d*k*a,y+k*b) for a,b in coords)
    def poly(c,*coords,edge=None):
        s.face(c,*pts(coords),edge=edge)
    def line(c,*coords):
        s.path(c,*pts(coords))
    def oval(a,b,w,h,c,edge=None):
        s.oval(x+a*k*d,y+b*k,w*k,h*k,c,edge=edge)
    if who=='mona':
        poly('ink',(-18,6),(-20,-19),(-9,-13),(7,-14),(18,-21),(22,7),
             (15,18),(-6,20),(-19,15),edge='slate')
        poly('slate',(-17,-14),(-16,-4),(-10,-10))
        poly('teal',(18,-15),(19,-4),(12,-9))
        poly('white',(-18,7),(-8,1),(3,6),(14,1),(21,7),(16,16),(2,20),(-12,17))
        for a in (-10,12):
            oval(a,3,6,8,'cyan','navy');oval(a+1,4,2.6,6,'navy');oval(a+2,-1,1.6,1.8,'white')
        poly('navy',(-1,8),(7,8),(3,12))
        line('navy',(-6,13),(-2,15),(3,13),(6,15),(11,12))
        for a in (-1,1):
            for i in range(3):line('white',(a*12,10+i*2),(a*25,7+i*3))
        return
    hair,coat,light,accent,mask,skin=_SKINS[who]
    if who=='panther':
        for a in (-1,1):
            poly('ochre',(a*6,-13),(a*16,-16),(a*22,-2),(a*23,13),(a*27,25),
                 (a*21,34),(a*16,26),(a*13,14),(a*10,4),edge='gold')
            for j in range(4):
                line('gold',(a*(11+j*2),-11+j),(a*(16+j*1.4),8),(a*(18+j*2),22))
    elif who in ('violet','echo'):
        poly('wine',(-6,-14),(-17,-14),(-24,-9),(-28,6),(-27,29),(-22,40),
             (-16,30),(-21,8),(-14,-2),(-5,3),edge='red')
        for j in range(3):line('red',(-13,-11),(-21-j*2,2),(-22-j*2,19),(-19-j*2,30))
        poly('rose',(-8,-14),(-16,-20),(-19,-10),(-15,-5),(-8,-9),edge='red')
    elif who=='fox':
        poly('ink',(-16,-11),(-19,-22),(-9,-17),(5,-17),(15,-22),(16,-6))
    elif who=='noir':
        for a in (-1,1):oval(a*13,7,6,9,'rose','wine')
    poly(skin,(-14,-9),(-7,-17),(7,-17),(14,-8),(13,8),(8,15),(1,19),
         (-8,14),(-14,7),edge=light)
    poly('ochre',(-13,4),(-7,12),(0,17),(9,12),(7,15),(1,18),(-7,14))
    if who in ('fox','crow','shadow'):
        brow='red' if who=='fox' else accent
        poly(mask,(-14,-3),(-13,-16),(-7,-11),(7,-11),(14,-17),(15,-3),
             (8,9),(1,15),(-6,9),edge=light)
        for a in (-1,1):
            line(brow,(a*12,-9),(a*8,-4),(a*4,-7),(a*2,-5))
            poly('plum' if who=='crow' else 'indigo',(a*13,-4),(a*7,-4),(a*4,-1),(a*10,2))
            line('cyan' if who=='fox' else 'red' if who=='crow' else 'white',(a*10,-2),(a*7,-1))
        line(brow,(0,1),(-2,8),(2,8),(0,1))
        if who=='crow':
            poly('indigo',(-5,3),(1,19),(7,4),edge='slate')
        return
    hairline=((-15,-7),(-15,-14),(-8,-20),(-1,-19),(5,-22),(10,-19),
              (15,-18),(16,-12),(13,-6),(10,-11),(5,-6),(5,-12),(1,-8),
              (-3,-13),(-8,-6),(-8,-12))
    poly(hair,*hairline,edge=light if who=='joker' else None)
    for j in range(6):
        line('slate' if who=='joker' else ('red' if who=='violet' else accent),
             (-12+j*4,-14-abs(j-3)*.3),(-9+j*3.5,-17),(-6+j*3,-11))
    if who=='echo':
        for a in (-1,1):
            poly('rose',(a*10,-4),(a*6,-5),(a*3,-3),(a*7,-2),(a*10,-1))
            line('wine',(a*11,-2),(a*8,1),(a*4,1))
        line('ochre',(1,1),(0,6),(-1,7),(2,7))
        line('rose',(-4,12),(0,13),(5,11))
        return
    if who=='noir':
        poly('wine',(-20,-11),(-16,-17),(-13,-17),(-11,-25),(0,-29),(11,-25),
             (15,-17),(21,-14),(15,-10),(2,-10),(-10,-7),edge='red')
        line('rose',(-13,-18),(-3,-20),(9,-20),(14,-18))
        oval(8,-20,2.4,2,'gold')
    if who=='panther':
        for a in (-1,1):
            poly('wine',(a*10,-11),(a*14,-19),(a*16,-15),(a*15,-5),edge='red')
    poly(mask,(-14,-3),(-10,-7),(-4,-5),(1,-2),(6,-5),(14,-7),(15,-1),
         (10,7),(5,7),(0,3),(-6,8),(-13,5),edge=light)
    for a in (-1,1):
        poly('ink',(a*12,-2),(a*5,-1),(a*3,1),(a*7,4),(a*11,2))
        line('red' if who=='joker' else ('cyan' if who in ('queen','noir') else 'white'),
             (a*10,1),(a*7,1))
    line('rose' if who in ('panther','violet','noir') else 'wine',(-4,12),(1,13),(6,11))
    if who=='skull':
        line('white',(-11,8),(-7,13),(-5,11),(-4,15),(0,13),(2,15),(4,11),(8,12),(12,7))
    if who=='queen':
        poly('slate',(-11,6),(-8,15),(1,18),(9,13),(13,6),(5,8),(0,5),(-5,9),edge='navy')


# Root is breastbone. Arm and leg endpoints are relative, letting each shot
# pose silhouettes rather than panning the same sprite.
_POSES={
    'ready':((-20,8),(-23,21),(20,7),(28,15),(-12,37),(-15,57),(13,37),(20,57)),
    'run':((-19,13),(-29,1),(15,-3),(30,-13),(-12,27),(-29,44),(22,29),(23,48)),
    'aim':((-9,13),(21,7),(20,1),(37,-1),(-11,36),(-22,54),(15,36),(17,56)),
    'punch':((-17,4),(-7,1),(18,-4),(40,-7),(-12,37),(-27,45),(17,30),(28,40)),
    'lift':((-17,-10),(-25,-30),(13,-14),(26,-34),(-15,31),(-25,50),(17,24),(29,33)),
    'slash':((-24,-5),(-36,3),(22,-11),(40,-23),(-14,40),(-25,54),(21,30),(35,36)),
    'float':((-19,-6),(-39,-1),(20,-11),(37,-23),(-13,32),(-31,43),(18,28),(29,42)),
    'kick':((-19,4),(-31,-6),(25,-2),(41,-16),(-10,38),(-21,54),(26,27),(53,18)),
    'trip':((-24,-2),(-39,-13),(18,1),(36,9),(-25,23),(-39,40),(13,23),(23,38)),
    'kneel':((-16,2),(-19,16),(19,2),(24,14),(-17,26),(-34,31),(15,21),(19,38)),
    'arc':((-12,-14),(-6,-29),(22,-16),(39,-30),(-15,24),(-27,30),(16,17),(39,29)),
    'reach':((-18,5),(-26,16),(19,-6),(36,-15),(-12,34),(-16,53),(15,32),(24,51)),
    'dip':((-21,4),(-28,0),(20,-4),(33,1),(-18,26),(-34,32),(14,34),(25,50)),
}


def actor(s,who,x,y,k=1,d=1,pose='ready',roll=0):
    a=roll*pi/180
    def pt(dx,dy):
        return (x+k*(dx*d*cos(a)-dy*sin(a)),y+k*(dy*cos(a)+dx*d*sin(a)))
    if who=='mona':
        s.oval(x,y+10*k,11*k,17*k,'ink',edge='teal')
        s.path('slate',pt(-7,17),pt(-18,28),pt(-29,24),pt(-35,12),pt(-40,10))
        s.face('gold',pt(-14,3),pt(10,2),pt(14,9),pt(2,13),pt(-5,9),pt(-21,13))
        for side in (-1,1):
            limb(s,pt(side*6,12),pt(side*15,21),3*k,'navy','slate')
            limb(s,pt(side*4,21),pt(side*11,30),3*k,'navy','slate')
            ex,ey=pt(side*11,30); s.oval(ex,ey,4*k,2*k,'white')
        cx,cy=pt(0,-5);face(s,who,cx,cy,k,d)
        return pt(19,8)
    hair,coat,light,accent,mask,skin=_SKINS[who]
    el,hand,er,grip,kl,fl,kr,fr=_POSES[pose]
    if who in ('joker','fox','crow','skull'):
        extra= -30 if pose in ('run','kick','slash','float','arc','punch') else -10
        s.face(coat,pt(-9,1),pt(9,5),pt(extra-1,36),pt(extra-13,46),pt(extra-14,33),
               pt(extra-33,40),pt(-11,12),edge=light)
        if who=='joker':s.face('wine',pt(-7,7),pt(-5,24),pt(extra-13,42),pt(extra-10,31))
        for j in range(3):s.path(light,pt(-9+j*3,9),pt(extra-5-j*4,28+j*3),pt(extra-14-j*3,38+j))
    for hip,knee,foot in ((-8,kl,fl),(8,kr,fr)):
        limb(s,pt(hip,20),pt(*knee),5.4*k,coat,light)
        limb(s,pt(*knee),pt(*foot),3.6*k,coat,light)
        s.face(light,pt(foot[0]-4,foot[1]-4),pt(foot[0]+3,foot[1]-4),pt(foot[0]+9,foot[1]+2),
               pt(foot[0]+4,foot[1]+5),pt(foot[0]-5,foot[1]+3),edge=coat)
        if who in ('queen','violet'):s.line(pt(knee[0]-3,knee[1]),pt(knee[0]+3,knee[1]),accent)
    s.face(coat,pt(-13,-8),pt(12,-8),pt(14,4),pt(8,15),pt(11,24),pt(-11,24),pt(-9,12),pt(-16,3),edge=light)
    if who=='panther':
        for side in (-1,1):
            s.face('red',pt(0,-4),pt(8*side,-8),pt(10*side,3),pt(7*side,16),pt(11*side,21),pt(2*side,21),edge='rose')
        s.face('white',pt(-5,-7),pt(0,-2),pt(7,-7),pt(2,4),pt(-2,3))
    elif who in ('noir','violet','echo'):
        s.face(accent,pt(-10,-6),pt(-3,7),pt(0,14),pt(6,4),pt(11,-6),pt(0,-1))
        s.face(coat,pt(-10,18),pt(10,18),pt(17,29),pt(6,32),pt(-5,29),pt(-17,31),edge=accent)
        if who=='echo':
            for side in (-1,1):
                for j in (2,5,8):
                    s.path('rose',pt(side*j,6),pt(side*(j+2),16),pt(side*(j+3),26))
    else:
        s.path(light,pt(-12,-7),pt(-4,9),pt(-8,20))
        s.path(accent,pt(9,-6),pt(2,-1),pt(7,7),pt(2,20))
        for j in range(3):
            bx,by=pt(-1,5+j*5);s.oval(bx,by,.75*k,.95*k,accent)
    for side,eb,hd in ((-1,el,hand),(1,er,grip)):
        shoulder=pt(12*side,-4)
        limb(s,shoulder,pt(*eb),4.5*k,coat,light)
        limb(s,pt(*eb),pt(*hd),3.7*k,coat,accent if who=='panther' else light)
        hx,hy=pt(*hd);s.oval(hx,hy,3.6*k,3.9*k,accent,edge=light)
        s.line(pt(hd[0]-2,hd[1]+1),pt(hd[0]+2,hd[1]+1),coat)
    face(s,who,*pt(0,-18),k*.78,d)
    return pt(*grip)


def prop(s,name,x,y,k=1,angle=0):
    def pt(a,b):return x+k*(a*cos(angle)-b*sin(angle)),y+k*(a*sin(angle)+b*cos(angle))
    def poly(c,*pts,edge=None):s.face(c,*(pt(*p) for p in pts),edge=edge)
    def path(c,*pts):s.path(c,*(pt(*p) for p in pts))
    if name in ('gun','launcher','smg'):
        wide=5 if name=='launcher' else 3.5 if name=='smg' else 2.2
        end=28 if name=='launcher' else 22 if name=='smg' else 14
        poly('slate',(-7,-wide),(end,-wide),(end,wide),(-4,wide),(-6,8),(-11,8),
             (-10,wide),(-13,wide),(-13,-wide),edge='navy')
        path('white',(-9,-wide),(end-2,-wide));path('navy',(-8,0),(end-2,0))
        if name!='gun':
            poly('navy',(-1,wide),(4,wide),(3,13),(-3,14),edge='slate')
            for j in range(7):path('navy',(j*1.6+6,-wide),(j*1.6+6,wide))
        return pt(end+1,0)
    if name in ('katana','blade'):
        end=42 if name=='katana' else 25
        poly('white',(0,-2),(end-6,-2),(end,-4),(end-2,1),(end-8,2),(0,3),edge='slate')
        path('cyan' if name=='katana' else 'rose',(2,1),(end-8,0),(end,-4))
        path('gold',(0,-5),(0,5));path('navy',(-9,0),(0,0))
        for j in range(4):path('rose',(-8+j*2,-1),(-7+j*2,1))
        return pt(end,0)
    if name=='pipe':
        path('white',(-8,0),(25,0),(29,-4),(29,-7));path('slate',(-8,1),(26,1),(30,-4))
        return pt(29,-7)
    if name=='can':
        poly('rose',(-4,-7),(4,-7),(5,7),(-4,7),edge='white')
        path('white',(-3,-4),(3,-3),(-3,0),(3,4));path('slate',(-4,5),(4,5))
    if name=='bomb':
        s.oval(x,y,8*k,8*k,'navy',edge='slate')
        s.oval(x-3*k,y-3*k,1.8*k,2.5*k,'white')
        path('gold',(2,-7),(5,-11),(8,-12),(9,-15));path('red',(5,-14),(13,-15));path('white',(9,-12),(9,-18))
    if name=='parasol':
        poly('red',(-26,-7),(-22,-13),(-13,-19),(0,-22),(14,-19),(22,-14),(27,-7),
             (18,-10),(9,-7),(0,-10),(-10,-7),(-18,-10),edge='rose')
        for j in range(-3,4):path('wine',(0,-22),(j*4,-17),(8*j,-9))
        path('white',(0,-23),(0,-21));path('gold',(0,-21),(0,8),(3,10),(6,7))
    return x,y
