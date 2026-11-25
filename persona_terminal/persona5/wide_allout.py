"""Persona 5 finishers repainted on the 2×4 terminal microgrid."""
from math import cos, sin, pi, tau
from ..shared.detail_canvas import DotCanvas
from .allout_scenes import SECS, TITLES

BY_TITLE={title:who for who,title in TITLES.items()}

# Accent, saturated shadow, glint, portrait side and hand-painted artwork cue.
THEME={
    'Joker':   ('red','wine','rose', .73,'cards'),
    'Mona':    ('cyan','navy','amber',.70,'paws'),
    'Skull':   ('amber','ochre','red',.72,'tape'),
    'Panther': ('rose','wine','violet',.73,'stars'),
    'Fox':     ('teal','navy','red',.29,'brush'),
    'Queen':   ('cyan','navy','amber',.72,'grid'),
    'Noir':    ('rose','violet','amber',.30,'lace'),
    'Crow':    ('red','wine','white',.74,'fracture'),
    'Violet':  ('rose','violet','white',.73,'ribbons'),
}

def ease(p):
    q=max(0.,min(1.,p))
    return 1-(1-q)**3

def m(x,a,b):
    return a+(b-a)*x

class Rig:
    """Local drawing coordinates projected onto a responsive portrait crop."""
    def __init__(self,c,x,y,sx,sy,flip=1,angle=0.):
        self.c=c; self.x=x; self.y=y; self.sx=sx*flip; self.sy=sy
        self.cos=cos(angle);self.sin=sin(angle)
    def p(self,x,y):
        u,v=x*self.cos-y*self.sin,x*self.sin+y*self.cos
        return round(self.x+u*self.sx),round(self.y+v*self.sy)
    def plane(self,ink,pts,d=8,e=None):self.c.face(tuple(self.p(*p) for p in pts),ink,d,e)
    def line(self,ink,*pts):self.c.path(tuple(self.p(*p) for p in pts),ink)
    def disk(self,ink,x,y,rx,ry,d=8,e=None):
        self.c.ellipse(*self.p(x,y),abs(rx*self.sx),ry*self.sy,ink,d,e)
    def ring(self,ink,x,y,rx,ry,a=0.,b=tau):
        self.c.ring(*self.p(x,y),abs(rx*self.sx),ry*self.sy,ink,a,b)

def _shoulders(r,who,ink,shade,lit,t):
    left,right=(-60,63) if who in ('Queen','Crow','Skull') else (-49,56)
    r.plane('navy',((left,95),(-42,54),(-20,37),(-15,21),(17,20),(23,39),(46,46),(right,86),(right,103),(left,103)),8,ink)
    r.plane(shade,((left,95),(-42,54),(-20,37),(-12,53),(-23,76),(-29,103),(left,103)),7,'navy')
    r.plane(ink,((17,33),(46,46),(right,86),(right,102),(32,99),(30,68),(10,50)),5,lit)
    r.plane('slate',((-19,34),(-10,29),(3,33),(16,28),(23,38),(11,56),(-10,53)),7,shade)
    r.plane('white' if who in ('Fox','Violet','Crow') else ink,
            ((-23,45),(-16,36),(-4,50),(-1,82),(-11,68),(-25,60)),7,lit)
    r.plane('white' if who in ('Fox','Violet','Crow') else ink,
            ((18,36),(27,44),(20,66),(6,83),(5,68),(10,51)),7,lit)
    r.line(lit,(-46,72),(-41,57),(-29,49));r.line(shade,(40,58),(50,70),(55,84))
    r.line('slate',(-35,77),(-40,102));r.line('slate',(38,73),(43,102))
    for j in range(3):
        r.disk(lit,-3,68+j*9,1.1,1.6)
    if who=='Joker':
        r.plane('red',((-35,102),(-27,91),(-10,81),(4,76),(14,74),(17,77),(7,84),(8,88),(-8,93),(-20,103)),8,'rose')
        for j in range(3):r.line('wine',(-14+j*5,88),(-2+j*5,83))
        r.plane('navy',((-59,105),(-52,69),(-39,55),(-21,52),(-7,65),(-15,86),(-30,102)),8,'red')
        r.line('rose',(-53,83),(-44,69),(-28,62),(-16,66))
        r.line('slate',(-48,96),(-38,83),(-25,81))
    elif who=='Skull':
        r.plane('red',((-18,40),(-7,46),(7,45),(23,37),(18,50),(2,54),(-13,52)),7,'rose')
        r.plane('wine',((15,37),(26,37),(49,29),(58,33),(47,47),(24,54),(11,49)),6,'red')
    elif who=='Panther':
        r.plane('red',((-26,46),(-10,47),(2,58),(11,47),(24,43),(22,69),(9,88),(-13,88),(-24,67)),7,'rose')
        r.plane('wine',((-7,60),(4,57),(13,65),(7,90),(-5,91)),6,'violet')
        r.ring('white',3,73,4,7)
        p=1-ease(t/.42)
        # Panther's coat-side arm rises into an emphatic two-finger gesture.
        dy=13*p
        r.plane('wine',((-48,89),(-42,70),(-41,46),( -39,29+dy),(-31,31+dy),(-30,50),(-28,68),(-32,87)),8,'rose')
        r.plane('red',((-43,34+dy),(-44,20+dy),(-49,14+dy),(-51,5+dy),(-47,4+dy),(-40,16+dy),
                       (-39,7+dy),(-35,5+dy),(-33,18+dy),(-26,16+dy),(-21,20+dy),
                       (-24,28+dy),(-30,36+dy),(-39,37+dy)),8,'white')
        r.line('wine',(-39,22+dy),(-35,27+dy),(-26,22+dy))
    elif who=='Fox':
        r.plane('white',((-35,65),(-27,58),(-18,65),(-8,89),(-16,103),(-28,102)),6,'cyan')
        r.line('red',(-50,97),(-25,81),(-1,73),(31,63),(58,56))
        r.line('white',(-43,95),(-24,87),(15,74),(54,59))
    elif who=='Queen':
        r.plane('navy',((-38,60),(-28,44),(-16,49),(-12,55),(-20,63),(-33,70)),8,'white')
        r.plane('navy',((20,45),(36,42),(47,51),(47,63),(33,66),(22,58)),8,'white')
        shift=9*(1-ease(t/.38))
        r.plane('slate',tuple((x+shift,y) for x,y in ((8,92),(12,74),(9,64),(14,57),(20,59),(25,55),(35,58),(38,67),(29,91),(21,104),(11,105))),8,'cyan')
        for j in range(4):r.line('white',(15+shift+j*5,64),(17+shift+j*5,61),(20+shift+j*5,65))
        shift2=12*(1-ease((t-.12)/.55))
        r.plane('navy',((-41,99),(-38,86),(-24,78),(-10,71-shift2),(1,69-shift2),(9,75-shift2),
                        (6,83-shift2),(14,88-shift2),(12,92-shift2),(-3,93-shift2),(-19,99)),8,'cyan')
        r.line('white',(-23,86),(-10,81-shift2),(-2,80-shift2),(4,83-shift2))
        r.line('slate',(-12,92-shift2),(-2,88-shift2),(9,92-shift2))
    elif who=='Noir':
        r.plane('violet',((-18,39),(0,48),(20,38),(14,54),(0,63),(-14,54)),8,'rose')
        r.disk('rose',0,55,4,5,7,'white')
        f=7*(1-ease(t/.37))
        r.disk('white',29,81+f,15,2.3,8,'rose')
        r.plane('white',((20,67+f),(35,67+f),(34,75+f),(31,80+f),(24,80+f),(21,75+f)),8,'rose')
        r.ring('amber',33,71+f,5,5,-pi/2,pi/2)
        r.ring('violet',27,67+f,8,2)
        r.line('amber',(24,63+f),(23,59+f),(26,54+f));r.line('white',(30,63+f),(31,58+f),(29,53+f))
    elif who=='Crow':
        r.plane('red',((-24,38),(-5,44),(5,50),(1,69),(-4,66),(-14,54)),7,'rose')
        r.plane('wine',((14,39),(22,41),(27,60),(11,67),(7,58)),7,'violet')
    elif who=='Violet':
        r.plane('rose',((-42,82),(-19,60),(-12,61),(-6,71),(-17,79),(-39,99),(-48,96)),7,'white')
        r.plane('white',((-45,94),(-23,80),(1,70),(38,54),(55,46),(52,50),(16,68),(-16,84),(-42,99)),6,'rose')

# The differences below are painted planes: head designs are not a glyph swap.
_HAIR={
    'Joker':('navy',((-35,-5),(-33,-31),(-25,-45),(-15,-47),(-4,-56),(7,-52),(20,-54),(30,-45),(41,-42),(46,-29),(44,-14),(36,-18),(36,-5),(28,-7),(24,2),(13,-9),(13,-1),(5,-5),(-2,-17),(-8,-8),(-12,-23),(-24,-9),(-22,-21),(-34,2))),
    'Skull':('amber',((-34,3),(-38,-14),(-35,-28),(-39,-39),(-27,-37),(-28,-51),(-15,-48),(-12,-56),(-6,-47),(6,-57),(12,-47),(25,-50),(24,-41),(38,-43),(35,-33),(45,-29),(38,-15),(41,-9),(36,3),(23,-18),(20,-29),(10,-27),(7,-35),(-5,-27),(-7,-31),(-15,-23),(-21,-10),(-27,-4))),
    'Panther':('amber',((-35,16),(-43,6),(-42,-31),(-33,-45),(-16,-55),(14,-54),(32,-49),(45,-28),(45,-9),(37,8),(31,-1),(37,-20),(24,-20),(11,-26),(3,-35),(-7,-33),(-18,-24),(-29,-5),(-29,16))),
    'Fox':('navy',((-36,-4),(-38,-31),(-30,-47),(-12,-54),(15,-55),(38,-40),(44,-23),(42,-10),(33,-6),(27,-20),(13,-27),(1,-23),(-10,-15),(-15,-18),(-26,5),(-35,9))),
    'Queen':('wine',((-37,7),(-43,-18),(-39,-40),(-21,-54),(13,-55),(34,-44),(42,-26),(43,-9),(36,7),(35,-15),(28,-14),(17,-23),(10,-17),(1,-30),(-5,-24),(-15,-28),(-21,-17),(-33,6),(-31,18))),
    'Noir':('ochre',((-38,20),(-40,-29),(-29,-47),(-18,-52),(12,-54),(33,-44),(42,-30),(45,10),(38,30),(34,19),(26,23),(26,12),(31,-9),(21,-16),(12,-26),(3,-24),(-10,-28),(-23,-12),(-24,2),(-20,20),(-27,26),(-31,18),(-35,24))),
    'Crow':('ochre',((-36,13),(-44,-14),(-37,-36),(-26,-52),(-13,-55),(6,-53),(20,-54),(36,-46),(44,-29),(43,-8),(34,8),(32,-20),(19,-16),(12,-25),(4,-30),(-3,-24),(-9,-34),(-24,-16),(-27,-3),(-29,15))),
    'Violet':('wine',((-32,5),(-41,-20),(-33,-43),(-12,-53),(16,-55),(36,-42),(44,-27),(42,-7),(32,8),(33,-14),(27,-16),(21,-24),(11,-22),(4,-31),(-5,-24),(-15,-23),(-23,-12),(-24,11))),
}

def _head(r,who,ink,shade,lit,t):
    if who=='Panther':
        r.plane('ochre',((-33,-38),(-52,-45),(-62,-20),(-60,2),(-50,25),(-56,53),(-45,61),(-42,45),(-36,56),(-30,38),(-39,16),(-41,-5)),7,'amber')
        r.plane('ochre',((33,-38),(51,-43),(60,-24),(59,4),(51,26),(58,49),(51,62),(40,52),(35,58),(34,37),(41,12),(39,-6)),7,'amber')
        r.line('rose',(-49,-36),(-30,-30));r.line('rose',(34,-32),(52,-35))
    if who=='Violet':
        r.plane('wine',((29,-30),(50,-46),(62,-33),(64,-13),(58,12),(47,24),(42,52),(30,54),(32,27),(40,13),(43,-11),(36,-16)),8,'rose')
        r.plane('red',((40,-38),(49,-42),(51,-21),(45,-17),(37,-23)),7,'white')
        r.line('rose',(47,-34),(54,-22),(52,6),(45,26),(39,48))
    r.plane('white',((-29,-23),(-15,-35),(18,-35),(33,-23),(32,5),(27,22),(13,37),(2,42),(-17,35),(-30,23),(-32,5)),
            7,lit)
    r.plane('slate',((-27,-16),(-8,-12),(-12,0),(-21,13),(-15,30),(-20,34),(-30,23),(-32,5)),6,'navy')
    r.plane('slate',((17,8),(31,0),(28,22),(17,35),(7,39),(10,27)),5,shade)
    r.line('slate',(4,-3),(7,8),(2,11),(-1,10));r.line(shade,(-9,22),(0,24),(9,21));r.line('slate',(-4,28),(4,29))
    if who=='Skull':
        r.plane('navy',((-31,-16),(-18,-21),(-7,-15),(0,-10),(9,-16),(22,-20),(35,-17),(33,11),(25,20),(15,18),(9,12),(4,17),(-3,18),(-9,13),(-16,19),(-29,13)),8,'amber')
        r.plane('white',((-28,-14),(-18,-17),(-7,-12),(-12,-3),(-22,-5)),8)
        r.plane('white',((9,-11),(21,-17),(31,-14),(24,-5),(13,-3)),8)
        r.plane('white',((-15,5),(-8,8),(3,8),(14,5),(13,13),(1,17),(-9,14)),8)
        for j in range(6):r.line('navy',(-12+j*5,8),(-12+j*5,14))
    elif who=='Queen':
        r.plane('slate',((-34,-18),(-14,-24),(0,-16),(13,-23),(35,-20),(36,-3),(28,9),(15,9),(3,1),(-6,4),(-22,10),(-32,4)),8,'white')
        for side in (-1,1):
            r.plane('navy',tuple((x*side,y) for x,y in ((6,-13),(19,-18),(28,-16),(27,-11),(17,-7),(9,-7))),8,'cyan')
            r.disk('rose',side*17,-12,2.1,2.4)
        for j in range(3):r.line('white',(19+j*4,4),(22+j*4,2))
    elif who=='Crow':
        r.plane('red',((-38,-4),(-32,-26),(-23,-37),(-13,-22),(-5,-18),(2,-16),
                       (15,-21),(28,-38),(33,-26),(38,-7),(31,4),(16,6),(7,1),(2,17),
                       (-5,21),(-3,5),(-16,8),(-31,6)),8,'white')
        r.plane('wine',((-33,-12),(-21,-22),(-5,-18),(-3,-9),(-14,0),(-26,-1)),8,'violet')
        r.plane('navy',((7,-12),(24,-22),(34,-14),(30,-5),(18,0),(8,-4)),8,'rose')
        r.plane('white',((10,-8),(20,-16),(29,-13),(25,-9),(17,-4)),8)
        r.plane('white',((-31,-11),(-19,-15),(-9,-10),(-18,-6),(-27,-6)),7)
        r.disk('red',22,-11,3.0,4);r.disk('white',22,-13,1.2,1.7)
        r.line('white',(2,-9),(4,1),(2,14),(-5,18));r.line('rose',(-30,1),(-19,4),(-8,2))
    elif who=='Fox':
        r.plane('white',((-35,-5),(-34,-30),(-27,-40),(-20,-26),(-8,-18),(8,-17),(21,-29),(29,-40),(34,-30),(37,-6),(28,8),(13,11),(4,22),(-4,24),(-12,15),(-27,11)),7,'cyan')
        r.plane('red',((-32,-25),(-27,-29),(-22,-17),(-29,-18)),8);r.plane('red',((21,-19),(28,-30),(32,-25),(31,-16)),8)
        r.line('navy',(-29,-7),(-19,-10),(-10,-6),(-16,-3),(-28,-4));r.line('navy',(10,-6),(20,-10),(31,-6),(22,-3),(16,-3))
        r.line('red',(-29,6),(-20,6),(-16,12));r.line('red',(15,12),(21,6),(28,5));r.disk('navy',1,15,3,3)
    else:
        horn=-31 if who=='Panther' else -17
        base='red' if who=='Panther' else 'navy' if who=='Noir' else 'white'
        r.plane(base,((-35,-10),(-31,horn),(-17,-19),(-4,-14),(5,-16),(20,-18),(32,horn),(37,-9),(30,1),(15,3),(6,-3),(-5,-2),(-15,4),(-29,2)),8,lit)
        for s in (-1,1):
            r.plane('navy',tuple((s*x,y) for x,y in ((8,-11),(21,-16),(30,-12),(23,-7),(12,-5))),8)
            r.disk('rose' if who in ('Panther','Violet') else shade,s*19,-11,2,2.5)
        r.line('slate' if base=='white' else 'white',(-30,-7),(-22,-4),(-13,-5))
        r.line('slate' if base=='white' else 'white',(11,-5),(22,-4),(32,-8))
    hair,points=_HAIR[who]
    # Fox wears his ears above the eye line rather than beneath the fringe.
    r.plane(hair,points,8,lit)
    bends={
        'Joker':((-28,-21),(-22,-36),(-8,-46),(5,-49),(16,-44),(25,-43),(35,-37)),
        'Skull':((-28,-27),(-17,-35),(-14,-44),(-7,-37),(0,-48),(11,-35),(16,-42),(29,-32)),
        'Panther':((-30,-13),(-26,-30),(-13,-44),(1,-48),(19,-38),(28,-32),(38,-18)),
        'Fox':((-35,-15),(-28,-36),(-20,-44),(-2,-48),(13,-45),(27,-39)),
        'Queen':((-36,-14),(-31,-32),(-21,-43),(-5,-47),(15,-45),(30,-38),(36,-23)),
        'Noir':((-32,0),(-34,-24),(-20,-43),(-2,-47),(15,-43),(32,-31),(38,-16)),
        'Crow':((-34,-5),(-28,-25),(-18,-43),(-6,-47),(14,-44),(30,-38),(39,-20)),
        'Violet':((-31,-10),(-29,-31),(-16,-45),(3,-48),(24,-38),(34,-31),(38,-18)),
    }
    r.line(lit,*bends[who])
    if who=='Fox':
        r.plane('white',((-33,-12),(-30,-37),(-25,-44),(-16,-23),(-22,-13)),8,'cyan')
        r.plane('white',((18,-22),(25,-41),(30,-39),(34,-31),(36,-12),(27,-13)),8,'cyan')
        r.line('red',(-29,-23),(-27,-34),(-21,-20));r.line('red',(25,-20),(29,-33),(31,-20))
    elif who=='Noir':
        r.plane('navy',((-52,-31),(-36,-41),(-35,-57),(-22,-70),(-2,-73),(19,-65),(32,-49),(34,-40),(48,-36),(55,-29),(41,-22),(15,-24),(-15,-27),(-40,-25)),8,'rose')
        r.plane('violet',((-35,-47),(-20,-44),(-1,-43),(15,-43),(35,-47),(34,-38),(13,-34),(-12,-35),(-35,-39)),8,'amber')
        r.line('white',(-32,-54),(-22,-63),(-9,-66),(7,-64))
        r.disk('rose',28,-45,4,5,8,'white')
    elif who=='Violet':
        r.plane('red',((23,-43),(39,-57),(46,-55),(45,-45),(36,-35),(26,-34)),7,'rose')
        r.plane('red',((36,-43),(57,-52),(59,-43),(52,-34),(41,-33)),7,'rose')

def _mona(r,ink,shade,lit,t):
    r.plane('navy',((-43,95),(-28,60),(-12,44),(14,43),(29,55),(47,93),(46,103),(-43,103)),8,'cyan')
    r.plane('amber',((-29,42),(-14,46),(4,48),(21,44),(32,49),(26,59),(5,67),(-22,55)),8,'gold')
    r.plane('amber',((19,51),(31,57),(53,53),(62,45),(58,60),(47,69),(24,66)),7,'gold')
    r.plane('navy',((-53,12),(-57,-18),(-52,-48),(-47,-57),(-25,-44),(-13,-36),(17,-38),(35,-51),(56,-56),(60,-41),(57,-14),(53,12),(36,36),(6,50),(-21,44),(-44,29)),8,'cyan')
    r.plane('cyan',((-49,-44),(-45,-46),(-30,-34),(-45,-23)),7,'navy')
    r.plane('cyan',((33,-33),(52,-46),(54,-31),(45,-22)),7,'navy')
    r.plane('white',((-45,1),(-31,-16),(-17,-19),(-6,-14),(-2,0),(7,-12),(21,-18),(34,-15),(48,-1),(46,21),(31,33),(3,39),(-24,36),(-43,23)),8,'slate')
    for side in (-1,1):
        r.disk('cyan',side*20,1,11,15,8,'navy')
        r.disk('navy',side*20,1,5,12);r.disk('white',side*22,-3,2,5)
        for j in range(3):r.line('slate',(side*30,16+j*3),(side*(45+j*3),13+j*5))
    r.disk('navy',0,16,4,3);r.line('navy',(0,18),(0,24),(-8,28));r.line('navy',(0,24),(8,26),(12,23))
    r.plane('white',((21,94),(28,83),(36,84),(38,77),(44,80),(48,88),(48,98),(38,103)),8,'cyan')
    for i in range(3):r.line('navy',(34+i*4,86),(34+i*4,92))

def _burst(c,x,y,rx,ry,ink,shade,t,spokes=27):
    for i in range(spokes):
        a=(i+.29)*tau/spokes
        r=.23+.57*((i*13)%17)/17
        step=.58+max(0,t)*.90
        v=(rx*cos(a)*step,ry*sin(a)*step)
        c.line((x+v[0]*r,y+v[1]*r),(x+v[0],y+v[1]),ink if i%4==0 else shade)
        if i%3==0:
            tip=(x+v[0]*(.74+r/5),y+v[1]*(.74+r/5))
            c.line(tip,(tip[0]+2*cos(a+.8),tip[1]+3*sin(a+.8)),ink)

def _cross(c,x,y,rx,ry,ink):
    c.line((x-rx,y),(x+rx,y),ink)
    c.line((x,y-ry),(x,y+ry),ink)

def _pattern(c,who,t,s,ink,shade,lit,focal):
    W,H=c.w,c.h
    closing=ease(t/.45)
    # Cropped matte diagonal and non-uniform halftone patches, original framing.
    cut=W*(.49+.06*sin(t*1.5))
    if focal<.5:
        c.face(((0,0),(cut+W*.18,0),(cut-W*.08,H),(0,H)),shade,3)
    else:
        c.face(((cut-W*.07,0),(W,0),(W,H),(cut-W*.18,H)),shade,3)
    for i in range(5):
        x=W*(.36+i*.036)+W*.19*(1-closing)
        c.line((x+W*.19,0),(x-W*.11,H),ink if i%3==0 else shade)
    for i in range(28):
        x=(i*53+round(t*7)*(i%3+1))%W
        y=(i*29+19*(i//7))%H
        if i%7==0:_cross(c,x,y,1,2,lit)
        else:c.put(x,y,shade if i%4 else ink)
    if s=='cards':
        for j,(xx,yy,size) in enumerate(((.17,.72,.07),(.32,.55,.045),(.39,.86,.052),(.86,.20,.093))):
            card=Rig(c,W*(xx+.035*sin(t*4+j)),H*(yy-.08*closing),W*size/16,H*size/16)
            card.plane('wine',((-8,-7),(6,-12),(11,7),(-4,13)),7,'red')
            card.plane('rose',((-2,-3),(3,-5),(5,1),(1,5)),6,'red')
    elif s=='paws':
        for j in range(7):
            x=W*(.06+j*.14);y=H*(.72+.09*sin(j*2.9)+.045*sin(t*4+j))
            c.ellipse(x,y,W*.028,H*.033,ink,5,lit)
            for k in range(3):c.ellipse(x+W*(k-1)*.021,y-H*(.049+.008*(k==1)),W*.009,H*.019,lit,6)
    elif s=='tape':
        for j in (0,1,2):
            y=H*(.58+j*.135)
            c.face(((0,y+H*.05),(W,y-H*.24),(W,y-H*.14),(0,y+H*.16)),shade,5,ink)
            for i in range(18):
                x=(i*W/17+t*W*.08)%W
                z=y+H*.05-x*H*.29/W
                c.line((x,z),(x-W*.012,z+H*.09),ink if i%3 else lit)
    elif s=='stars':
        for i in range(9):
            x=W*(.04+(i*31%92)/100);y=H*(.18+(i*39%70)/100)
            r=H*(.025+.027*max(0,sin(i+t*4)))
            c.face(tuple((x+(.9 if k%2==0 else .3)*r*cos(k*tau/10-pi/2),
                          y+(.9 if k%2==0 else .3)*r*sin(k*tau/10-pi/2)) for k in range(10)),lit,5,ink)
    elif s=='brush':
        for i in range(4):
            q=.68+i*.057
            r=Rig(c,W*.50,H*q,W/100,H/100)
            r.plane('red' if i%2 else shade,((-57,7),(-34,8),(-15,4),(2,-1),(24,-11),(46,-13),(54,-11),(45,-8),(26,-6),(6,3),(-14,9),(-35,12),(-56,13)),4 if i%2 else 7)
            r.line(ink,(-48,10),(-22,8),(4,0),(20,-3),(46,-11))
    elif s=='grid':
        for i in range(5):
            y=H*(.6+i*.084)
            c.line((0,y),(W,H*(.49+i*.084)),shade if i%2 else ink)
        for i in range(11):
            x=W*(i-1)/9
            c.line((W*.52+(x-W*.5)*.34,H*.53),(x,H),ink if i%3==0 else shade)
        for i in range(3):
            c.ring(W*.72,H*.53,W*(.24+i*.023),H*(.39+i*.027),lit if i==0 else shade,2.44,5.28)
    elif s=='lace':
        for i in range(9):
            x=W*(.09+i*.10);y=H*(.812+.085*sin(i*.7))
            r=H*(.033+.008*sin(i+t*3))
            c.ring(x,y,r*1.1,r,ink,.15,tau*.94)
            c.ring(x,y,r*.70,r*.63,lit,0,tau)
            for j in range(4):
                a=j*pi/2+pi/4
                c.ellipse(x+r*1.1*cos(a),y+r*sin(a),r*.20,r*.18,lit,5)
    elif s=='fracture':
        for i in range(5):
            y=H*(.10+i*.19);x=W*(.59-i*.036+.035*sin(i+t*3))
            c.path(((W,y*.37),(x+W*.15,y*.70),(x,y),(x-W*.055,y+H*.08),(x-W*.20,y+H*.19),(0,y+H*.34)),ink if i%2 else lit)
            c.path(((x,y),(x+W*.046,y+H*.12),(x+W*.19,y+H*.25)),shade)
    else:
        for i in range(5):
            q=i*.08
            c.ring(W*(.48+q*.33),H*(.70+q*.27),W*(.38+q),H*(.19+q),ink if i%2 else lit,
                   .28+closing,pi+1+closing,92)

def _runner(c,who,x,y,scale,face,t):
    ink,shade,lit,*_=THEME[who]
    r=Rig(c,x,y,scale*.69,scale,face)
    f=sin(t*tau)
    if who=='Mona':
        r.plane('navy',((-18,8),(-18,-18),(-12,-26),(-4,-17),(9,-19),(18,-26),(20,-15),(22,4),(14,12),(-3,15)),8,'cyan')
        r.plane('white',((-14,2),(-7,-10),(2,-5),(7,-11),(16,-5),(17,6),(8,10),(-9,10)),8,'cyan')
        r.disk('navy',-4,-1,2.3,3);r.disk('navy',9,-1,2.3,3)
        r.line('amber',(-14,11),(5,13),(18,11),(21,16),(9,19),(-19,15))
        r.line('cyan',(-14,20),(-24,23),(-30,19),(-35,11))
        r.plane('navy',((-14,16),(8,13),(12,22),(-8,29),(-22,26)),8,'cyan')
        r.line('white',(1,24),(13,22+f*3),(20,23+f*4))
        return
    r.plane('navy',((-22,10),(-13,-4),(9,-7),(17,0),(24,12),(14,20),(-7,17),(-22,29)),8,ink)
    r.plane(shade,((-12,9),(-1,1),(13,0),(21,9),(11,18),(1,17)),7,lit)
    r.plane('navy',((-12,15),(0,14),(-3,27),(-15-f*5,39),(-23-f*4,38),(-16-f*6,30)),8,ink)
    r.plane(shade,((0,13),(12,15),(20+f*8,25),(16+f*10,31),(7+f*6,25),(3,22)),8,ink)
    r.plane(ink,((10,2),(19,3),(30,8),(40,6),(41,10),(27,15),(21,13),(11,11)),8,lit)
    r.plane('white',((3,-6),(0,-21),(7,-29),(20,-28),(29,-18),(23,-5),(13,-2)),7,lit)
    r.plane(shade,((0,-15),(-4,-23),(6,-34),(20,-35),(25,-32),(30,-28),(26,-20),(17,-22),(10,-17),(2,-17)),8,ink)
    r.line('navy',(8,-17),(17,-18),(25,-15));r.line(lit,(16,-10),(24,-11))

def _shadow(c,x,y,sx,sy,ink='wine'):
    r=Rig(c,x,y,sx,sy)
    r.plane('navy',((-32,25),(-24,2),(-22,-16),(-28,-37),(-12,-24),(11,-25),(26,-37),(23,-14),(28,3),(35,26),(20,36),(-10,38)),8,ink)
    r.plane(ink,((-22,-15),(-12,-22),(12,-23),(20,-14),(14,4),(3,9),(-13,4)),6,'slate')
    r.disk('white',-10,-10,4,3);r.disk('white',11,-10,4,3)
    r.line('slate',(-18,23),(-10,19),(-1,29),(9,26),(19,23))

def _rush(c,t,ink,shade,lit,party,n):
    W,H=c.w,c.h
    cx,cy=W*.52,H*.47
    p=ease(t)
    _burst(c,cx,cy,W*.75,H*.70,ink,shade,.84-p*.19)
    for i in range(n):
        x=cx+W*.087*(i-(n-1)/2)
        y=H*(.49+((i*7)%3)*.034)
        _shadow(c,x,y,W/800,H/550,ink)
    for i,that in enumerate(party):
        side=1 if i%2==0 else -1
        fx=(.10+.24*p) if side==1 else (.89-.22*p)
        fy=(.26 if i<2 else .70)+(.18 if i<2 else -.18)*p
        x=W*fx;y=H*fy
        scale=min(W,H)*(.010+.009*p)
        for j in range(3):
            c.line((x-side*(8+j*9),y+j*3),(x-side*(35+j*11),y+4+j*3),shade if j%2 else ink)
        _runner(c,that,x,y,scale,side,2*t+i*.63)
    if t>.64:
        for i in range(5):
            a=i*tau/5;tint=lit if i%2 else ink
            c.ring(cx,cy,W*(.13+i*.016),H*(.12+i*.013),tint,a,a+.61)
    return 'rush'

def _hit(c,t,ink,shade,lit,n,finishing):
    W,H=c.w,c.h
    x,y=W*.52,H*.49
    p=ease(t)
    for i in range(n):
        xx=x+W*.07*(i-(n-1)/2)
        if t<.53 or not finishing:
            yy=y+H*.08*(p if finishing else sin(t*pi))
            _shadow(c,xx+sin(t*3+i)*W*.015,yy,W/760,H/530,lit if i%2 else ink)
        else:
            a=(i+1)*tau/n
            c.face(((xx+W*.19*p*cos(a),y+H*.16*p*sin(a)),
                    (xx+W*.19*p*cos(a)+4,y+H*.16*p*sin(a)-4),
                    (xx+W*.19*p*cos(a)+7,y+H*.16*p*sin(a)+3)),ink,6,lit)
    for i in range(5):
        c.ring(x,y,W*(.058+.036*i+.19*p),H*(.067+.032*i+.17*p),lit if i%3==0 else ink,
               t*.3+i*.2,(3.96 if not finishing else tau)+t*.3)
    for i in range(5):
        q=(i-2)*.043
        c.face(((W*(.13+q*.3),H*(.63+q)),(W*(.57+q),H*(.46+q)),
                (W*(.94+q*.4),H*(.26+q*.6)),(W*(.67+q),H*(.38+q*.5)),
                (W*(.50+q),H*(.45+q*.4)),(W*.17,H*(.67+q))),
               'white' if i==2 else lit,3 if i==2 else 5)
    _burst(c,x,y,W*.68,H*.70,ink,shade,t,36)
    return 'impact' if finishing else 'formation breaks'

def _resolve(c,t,ink,shade,lit,party,n):
    W,H=c.w,c.h
    cx,cy=W*.50,H*.57
    _burst(c,cx,cy,W*.59,H*.59,ink,shade,t,24)
    for i in range(n):
        _shadow(c,W*(.50+(i-(n-1)/2)*.097),H*(.49+(i%2)*.05),
                W/690,H/510,shade if i%2 else ink)
    for i,u in enumerate(party):
        side=-1 if i%2==0 else 1
        y=H*(.57+(i%3)*.14)
        x=cx+side*W*(.09+.34*ease(t))
        _runner(c,u,x,y,min(W,H)*(.015-.004*t),side,3*t+i)
    return 'regroup'

def _violet_land(c,t,ink,shade,lit):
    W,H=c.w,c.h
    p=ease(t)
    x=W*(.48+.105*p);y=H*(.49+.21*p-.14*sin(pi*p))
    sx=min(W,H)*.0115;sy=H*.0118
    r=Rig(c,x,y,sx,sy,1,-.50*(1-p))
    ribbon=tuple((x+W*(.29-.10*p)*cos(i*.11-p*3),y-H*.14+H*(.11+.16*p)*sin(i*.10-p*3))
                 for i in range(38))
    c.path(ribbon,'rose')
    c.path(tuple((a-2,b+3) for a,b in ribbon),'violet')
    r.plane('navy',((-13,16),(-26,26),(-38,34),(-50,33),(-54,39),(-45,44),(-31,40),(-7,30),(3,16)),8,'rose')
    r.plane('navy',((0,14),(8,14),(23,29),(18,41),(29,43),(32,48),(22,49),(10,44),(12,30),(2,24)),8,'white')
    r.plane('navy',((-17,15),(-16,-9),(-11,-14),(3,-17),(13,-9),(12,5),(8,15),(-3,20)),8,'rose')
    r.plane('white',((-15,-12),(-25,-18),(-30,-22),(-27,-28),(-20,-26),(-7,-22),(-4,-14)),7,'violet')
    r.plane('rose',((8,-14),(18,-21),(22,-34),(28,-34),(29,-27),(24,-11),(13,-7)),8,'white')
    r.plane('wine',((10,-25),(21,-42),(28,-38),(33,-21),(31,-14),(25,-16),(19,-29),(15,-20)),8,'rose')
    r.plane('wine',((-17,-18),(-20,-35),(-12,-45),(3,-45),(13,-37),(12,-22),(4,-16)),8,'rose')
    r.plane('white',((-12,-31),(-3,-38),(12,-31),(9,-21),(4,-16),(-9,-20)),8,'white')
    r.line('navy',(-10,-29),(-1,-28),(9,-32))
    r.line('rose',(-28,-31),(-52,-48));r.line('white',(-29,-31),(-32,-35))
    if t>.29:
        for i in range(6):
            q=i*pi/5
            c.line((x,y+H*.34),(x+W*.16*cos(q),y+H*.34-H*.061*sin(q)),'teal')
    return 'landing'

def _closing(c,who,t,ink,shade,lit,side,style):
    W,H=c.w,c.h
    _pattern(c,who,t,style,ink,shade,lit,side)
    jitter=sin(t*4)*.015
    slide=(1-ease(t/.25))*(.29 if side>.5 else -.26)
    x=W*(side+slide+jitter)
    y=H*(.425+.14*(1-ease(t/.38)))
    sx=min(W*.0047,H*.0062);sy=H*.00585
    if who=='Mona':sx*=.88;sy*=.96
    if who=='Noir':y+=H*.051
    # Drop noisy texture behind the head, without a caption or portrait box.
    c.ellipse(x,y-H*.02,abs(sx)*43,sy*52,shade,1)
    if who=='Violet' and t<.41:return _violet_land(c,t/.41,ink,shade,lit)
    flip=1 if side<.5 else -1
    torso_x=x-W*.049 if who=='Joker' else x
    r=Rig(c,torso_x,y,sx,sy,flip,
          -.15 if who=='Joker' else .11 if who=='Panther' else .20 if who=='Violet' else 0.)
    if who=='Mona':
        _mona(r,ink,shade,lit,t)
    else:
        _shoulders(r,who,ink,shade,lit,t)
        # Shoulder and face use independently blocked cameras. Joker turns
        # back over the coat; Violet stays on a distinct athletic diagonal.
        angle={'Joker':.17,'Panther':-.14,'Violet':.20,'Crow':-.11}.get(who,0.)
        turn=1-ease(t/.55) if who in ('Joker','Violet') else 0
        x+=W*(.010*turn if who=='Joker' else -.023*turn)
        hr=Rig(c,x,y,sx*(.92 if who=='Queen' else 1.),sy,-flip if who=='Joker' else flip,angle)
        _head(hr,who,ink,shade,lit,t)
    if t<.32:
        q=ease(t/.32)
        edge=W*((.2+q) if side>.5 else (.80-q))
        c.face(((edge-3,0),(edge+3,0),(edge-W*.26+3,H),(edge-W*.26-3,H)),ink,5,lit)
    return 'finishing pose'

def render(title,elapsed,width,height,*,cast=(),targets=0,finishing=True):
    """Paint the deployed cast; a nonlethal All-Out returns to formation."""
    who=BY_TITLE[title]
    c=DotCanvas(max(1,width),max(1,height))
    t=max(0.,min(elapsed,SECS[who]))
    ink,shade,lit,side,style=THEME[who]
    party=tuple(u for u in cast if u in THEME)
    if not party:
        party=('Joker','Mona','Skull','Panther') if who in ('Joker','Mona','Skull','Panther') else ('Joker','Mona','Skull',who)
    n=max(1,min(5,targets or 3))
    if t<.53:beat=_rush(c,t/.53,ink,shade,lit,party,n)
    elif t<.88:beat=_hit(c,(t-.53)/.35,ink,shade,lit,n,finishing)
    elif finishing:beat=_closing(c,who,t-.88,ink,shade,lit,side,style)
    else:beat=_resolve(c,(t-.88)/(SECS[who]-.88),ink,shade,lit,party,n)
    return beat,c.finish()
