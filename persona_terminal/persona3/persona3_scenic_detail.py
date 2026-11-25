"""Original, compact story plates staged on Persona 3's native dot grid."""
from math import cos, pi, sin, tau

from .persona3_detail_tools import Stage


def _line(s, ink, *points):
    s.path(points, ink)


def _polygon(s, ink, edge, *points, density=8):
    s.shape(points, ink, density, edge)


def _city(s, horizon, lit='teal'):
    for i in range(22):
        x=i*4.65-1
        y=horizon-4-(i*13+i*i*3)%13
        w=3.6+(i*7)%3
        _polygon(s,'navy','slate',(x,horizon),(x,y),(x+w,y),(x+w,horizon),density=6)
        if i%4==0:
            _line(s,'slate',(x+w*.42,y+1),(x+w*.42,y-5))
        for k in range(2,round(horizon-y),4):
            for j in (1,w-1):
                if (i+k+int(j))%4:
                    s.rect(x+j-.25,y+k,.62,1.1,lit if i%3==0 else 'slate',6)
    _line(s,'navy',(0,horizon),(100,horizon))


def _sky(s,t,ink='navy'):
    s.particles(t,ink,107,speed=.3,region=(0,0,100,64))
    for x,y in ((26,8),(59,14),(82,24),(95,11)):
        s.burst(x,y,.45,1.5,ink)


def _cup(s,x,y):
    _polygon(s,'wine','amber',(x-3,y),(x+3,y),(x+2,y+12),(x-2,y+12),density=7)
    s.disc(x,y,3.1,1.7,'navy',8,'amber')
    _line(s,'ochre',(x-1,y+10),(x+1,y+10))
    for i in (-1,1):
        _line(s,'white',(x+i,y-3),(x+i+.7,y-6),(x+i-.6,y-8),(x+i,y-11))


def platform(t,w,h,dawn=False):
    s=Stage(w,h)
    sky='ochre' if dawn else 'slate'
    glow='amber' if dawn else 'teal'
    _sky(s,t,sky)
    if dawn:
        s.disc(74,51,10,28,'ochre',4,'amber')
        for r in (12,14,16):s.ring(74,51,r,r*2.35,'ochre',pi,tau)
    _city(s,56,glow)
    _polygon(s,'navy','slate',(0,66),(44,55),(59,55),(100,68),(100,100),(0,100),density=8)
    for sign in (-1,1):
        for j in (0,2,9,11):
            _line(s,'slate' if j in (0,9) else 'navy',
                  (50+sign*(j/3+1),55),(50+sign*(j*2.1+t+7),100))
        _line(s,glow,(50+sign*7,55),(50+sign*46,99))
    for i in range(13):
        q=(i/13)**1.8
        _line(s,'slate' if i%3==0 else 'navy',(48-22*q,58+42*q),(52+22*q,58+42*q))
    _polygon(s,'navy','slate',(0,0),(37,20),(46,47),(0,24),density=8)
    for i in range(6):
        x=4+i*7
        y=9+i*5.2
        _line(s,'slate',(x,y),(x,85-i*5))
        _line(s,'navy',(x+1,y),(x+1,85-i*5))
        s.rect(x-2.5,y+3,4,2,glow,8)
    _line(s,'slate',(0,24),(46,47))
    for i in range(4):_line(s,'navy',(0,5+i*4),(43,43+i*2))
    if dawn:
        _cup(s,17,75)
        _polygon(s,'navy','amber',(21,91),(32,86),(37,93),(25,98),density=7)
        for j in range(3):_line(s,'ochre',(23+j,91+j),(31+j,88+j))
    else:
        # Hard-sided luggage beside the otherwise empty platform.
        _polygon(s,'navy','cyan',(19,77),(29,75),(31,89),(20,92),density=7)
        _line(s,'slate',(21,76),(21,72),(26,71),(27,75))
        _line(s,'slate',(22,81),(28,80),(28,88))
        s.rect(26,82,1.3,2,'white',8)
    return s.c.finish()


def roof(t,w,h):
    s=Stage(w,h)
    _sky(s,t,'forest')
    s.disc(77,30,10,24,'forest',7,'teal')
    for i in range(6):s.ring(77,30,9-i,22-i*2,'green' if i in (0,3) else 'teal',pi*.14,pi*1.7)
    _city(s,53,'teal')
    for x in range(0,102,8):
        _line(s,'slate',(x,41),(x,67))
        for dj in (0,8):
            _line(s,'navy',(x-4,47+dj),(x,51+dj),(x+4,47+dj))
    for y in (43,61,67):_line(s,'slate',(0,y),(100,y))
    _polygon(s,'navy','teal',(0,73),(41,65),(61,65),(100,73),(100,100),(0,100),density=8)
    for i in range(7):_line(s,'slate',(50+i*3-9,68),(50+i*17-51,100))
    # Lyre and collar reference Orpheus, above the rooftop rail instead of a caption.
    x,y=47,56
    _polygon(s,'teal','cyan',(x-7,y-4),(x-10,y+7),(x-12,y+25),(x-3,y+32),(x,y+28),
             (x+3,y+32),(x+11,y+25),(x+9,y+7),(x+7,y-4),density=6)
    for d in (-1,1):
        _line(s,'cyan',(x+d*7,y-5),(x+d*11,y-22),(x+d*10,y-38),
              (x+d*5,y-39),(x+d*5,y-33),(x+d*8,y-31),(x+d*7,y-16),(x+d*4,y-9))
    s.disc(x,y-18,3.3,9,'navy',8,'white')
    s.disc(x,y-16,1.8,5,'slate',7,'cyan')
    _line(s,'white',(x-8,y-29),(x+8,y-29))
    for i in (-2,-1,1,2):
        _line(s,'cyan',(x+i*1.7,y-29),(x+i*1.15,y+6))
    s.ring(x,y+17,4,8,'cyan')
    for i in range(12):
        a=i*tau/12+t*.5
        s.burst(x+19*cos(a),47+35*sin(a),.3,1.3,'teal')
    return s.c.finish()


def _chair(s,x,y):
    _polygon(s,'navy','slate',(x-2,y-17),(x+2,y-16),(x+3,y),(x-1,y-1),density=7)
    _line(s,'slate',(x-3,y),(x+4,y),(x+3,y+2),(x-2,y+2),(x-2,y+10))
    _line(s,'navy',(x+3,y+2),(x+4,y+10))


def lounge(t,w,h,variant):
    s=Stage(w,h)
    velvet=variant=='velvet'
    trim='cyan' if velvet else 'slate'
    light='cyan' if velvet else 'amber'
    for side in (-1,1):
        outside=50+side*50
        back=50+side*26
        _polygon(s,'navy','navy',(outside,0),(back,14),(back,73),(outside,99),density=8)
        for i in range(7):
            x=outside+(back-outside)*i/7
            _line(s,'slate' if i%2 else 'navy',(x,3+i*1.6),(x,99-i*4))
        _line(s,'slate',(outside,48),(back,48))
        _line(s,'navy',(outside,68),(back,53))
    _polygon(s,'navy',trim,(21,75),(39,58),(61,58),(81,75),(100,100),(0,100),density=6)
    for i in range(8):
        d=13+i*5
        _line(s,'navy',(50-d,62+i*5),(50+d,62+i*5))
    if velvet:
        s.ring(50,34,23,37,'navy',pi,tau)
        s.ring(50,34,20,34,'teal',pi,tau)
        _line(s,'cyan',(30,32),(30,72),(70,72),(70,32))
        for j in range(7):
            x=33+j*5.7
            _line(s,'slate',(x,14),(x,72))
        s.ring(50,29,5,8,'slate')
        _line(s,'white',(50,29),(52,22))
        for x in (33,67):
            _line(s,'cyan',(x,49),(x+1,61),(x-2,68),(x+3,68))
            s.disc(x,46,1,3,light,7)
        _polygon(s,'teal','cyan',(35,74),(43,64),(58,64),(66,74),(61,80),(39,80),density=5)
        _polygon(s,'navy','white',(43,65),(49,65),(51,68),(54,64),(59,65),(58,72),
                 (52,73),(50,72),(43,72),density=6)
        _line(s,'cyan',(50,67),(51,72))
        _line(s,'slate',(45,67),(48,68))
        _line(s,'slate',(54,67),(57,66))
    else:
        s.rect(28,10,30,29,'navy',7,'slate')
        s.rect(31,13,23,21,'navy',6,'slate')
        for x in range(34,54,4):
            _line(s,'ochre',(x,15),(x,32))
        for j in range(4):
            _line(s,'navy',(32,16+j*5),(53,16+j*5))
        for x in (33,42,52):_chair(s,x,82)
        _polygon(s,'navy',trim,(40,65),(64,47),(84,53),(69,75),(69,88),(40,79),density=7)
        _line(s,'slate',(42,68),(68,76),(83,57))
        _line(s,'ochre',(50,77),(63,81))
        if variant=='relay':
            _polygon(s,'navy','cyan',(53,53),(55,36),(67,36),(71,52),(64,57),density=8)
            _line(s,'teal',(56,46),(59,46),(61,41+sin(t*8)*2),(63,47),(67,47))
            _line(s,'cyan',(70,52),(73,35),(75,27))
            for i in range(3):s.ring(76,33,2+i*2,3+i*2,'slate',-1.35,1.0)
        else:
            _cup(s,74,48)
            _polygon(s,'navy','amber',(52,59),(55,54),(62,57),(60,62),density=6)
            s.ring(54,56,1.1,1.7,'amber')
            _line(s,'amber',(55,56),(59,57),(61,59))
    return s.c.finish()


def _train_plate(s,t):
    _sky(s,t,'forest')
    _city(s,58,'forest')
    # Elevated tracks and the terminal's exterior establishing view.
    for side in (-1,1):
        _line(s,'teal',(31+side*3,55),(67+side*24,100))
        _line(s,'slate',(32+side*4,57),(68+side*27,100))
    for i in range(8):
        q=i/8
        _line(s,'navy',(30+18*q,58+q*41),(36+43*q,58+q*41))
    _polygon(s,'navy','cyan',(9,45),(62,18),(76,15),(87,25),(92,61),(90,76),
             (82,86),(10,63),density=8)
    _polygon(s,'teal','cyan',(66,24),(76,18),(85,28),(88,63),(86,75),(82,80),
             (64,69),(63,46),density=6)
    _polygon(s,'navy','slate',(68,27),(77,24),(83,32),(85,54),(66,52),density=7)
    _line(s,'slate',(76,24),(76,53))
    for y in (62,70):
        _line(s,'cyan',(65,y),(86,y+4))
    s.disc(68,64,2.5,4,'amber',7,'white')
    s.disc(86,68,1.7,4,'amber',7,'white')
    for i in range(7):
        x=13+i*6.6
        y=46-i*2.7
        _polygon(s,'teal','navy',(x,y),(x+4.7,y-2.2),(x+5,y+8),(x,y+8.7),density=8)
        _line(s,'slate',(x+2.5,y),(x+2.5,y+7))
    _line(s,'forest',(2,83),(65,98))


def monorail_plate(t,w,h):
    s=Stage(w,h)
    _train_plate(s,t)
    return s.c.finish()


def club(w,h):
    s=Stage(w,h)
    _polygon(s,'plum','violet',(0,0),(100,0),(89,78),(11,78),density=7)
    for i in range(16):
        x=i*6.4
        _line(s,'wine' if i%3 else 'violet',(x,0),(x+(50-x)*.22,77))
    for side in (-1,1):
        near=50+side*48
        inner=50+side*23
        _polygon(s,'navy','violet',(near,5),(inner,18),(inner,76),(near,92),density=7)
        for i in range(3):
            x=near+(inner-near)*i/3
            _line(s,'rose',(x,10+i*4),(x,80-i*2))
            _line(s,'wine',(x-1,10+i*4),(x-1,84-i*2))
        s.ring(50+side*36,35,2,8,'rose')
        s.disc(50+side*36,35,1,3,'white')
    _polygon(s,'navy','rose',(24,28),(30,15),(70,15),(76,28),(76,77),(25,77),density=8)
    for x in (27,73):
        _line(s,'cyan',(x,30),(x,76))
    s.rect(35,41,30,35,'plum',6,'violet')
    _line(s,'rose',(49,42),(49,76))
    _line(s,'rose',(51,42),(51,76))
    for x in (44,56):s.disc(x,62,1,3,'white')
    # Illuminated club monogram built as geometry, not an extra UI label.
    s.ring(50,30,13,10,'violet')
    _line(s,'white',(46,25),(43,23),(39,25),(38,30),(40,36),(44,36),(46,32))
    _line(s,'rose',(56,23),(50,23),(50,36),(56,36))
    _line(s,'rose',(50,29),(55,29))
    for i in range(5):
        y=77+i*i*.95
        d=23+i*5.5
        _line(s,'violet' if i%2 else 'navy',(50-d,y),(50+d,y))
    for side in (-1,1):
        _line(s,'wine',(50+side*14,77),(50+side*32,100))
        _line(s,'slate',(50+side*9,77),(50+side*22,100))
    return s.c.finish()


def room_prop(s, x, y, width, height, prop, mirrored=False, edge='slate'):
    """Five different furnishings, transformed into the available pane."""
    def points(coords):
        return tuple((x+width*(1-u if mirrored else u),y+height*v) for u,v in coords)

    def panel(ink,*coords,density=7):
        _polygon(s,ink,edge,*points(coords),density=density)

    def stroke(ink,*coords):
        _line(s,ink,*points(coords))

    def point(u,v):
        return points(((u,v),))[0]

    if prop==0:  # Vanity basin and faucet.
        panel('teal',(.04,.62),(.95,.62),(.8,.83),(.22,.83))
        stroke('slate',(.3,.82),(.37,1),(.67,1),(.72,.82))
        stroke(edge,(.48,.58),(.49,.21),(.64,.15),(.72,.27),(.72,.4))
        stroke('teal',(.16,.56),(.87,.56))
    elif prop==1:  # Curtains gathered at the ties.
        panel('wine',(.04,.08),(.94,.08),(.7,.49),(.93,.98),(.06,.98),(.3,.49))
        for i in range(1,7):
            u=i*.13
            stroke(edge,(u,.13),(.5+(u-.5)*.42,.49),(u,.94))
        stroke('teal',(.21,.49),(.79,.49))
    elif prop==2:  # Interior door.
        panel('navy',(.24,.09),(.77,.09),(.77,.98),(.24,.98))
        stroke(edge,(.31,.91),(.31,.16),(.69,.16),(.69,.91),(.31,.91))
        s.disc(*point(.63,.56),width*.043,height*.039,'white')
    elif prop==3:  # Bed and folded pillow.
        panel('wine',(.12,.55),(.15,.31),(.55,.36),(.9,.58),(.88,.91),(.12,.91))
        panel('navy',(.17,.32),(.45,.34),(.58,.50),(.25,.52),density=6)
        stroke(edge,(.17,.66),(.83,.67))
        stroke('teal',(.31,.70),(.31,.87),(.51,.87),(.51,.70))
    else:  # Twin-door cabinet.
        panel('wine',(.15,.05),(.87,.05),(.87,.99),(.15,.99))
        stroke(edge,(.22,.18),(.8,.18),(.8,.89),(.22,.89),(.22,.18))
        stroke(edge,(.51,.18),(.51,.89))
        for u in (.44,.58):
            s.disc(*point(u,.55),width*.035,height*.038,edge)


def figure(s,x,y,rx,ry,style,palette,rev=False):
    """Profile, hair, coat and lapel. Mirror reverses the actual profiles."""
    ink, edge, light=palette
    direct=-1 if rev else 1
    def points(coords):
        return tuple((x+rx*u*direct,y+ry*v) for u,v in coords)
    contours=(
        ((-.61,.23),(-.62,-.24),(-.14,-.39),(.45,-.27),(.63,-.07),(.34,.05),(.23,.25),(.02,.44),(-.12,.17),(-.30,.27)),
        ((-.80,.52),(-.66,-.22),(-.32,-.42),(.40,-.37),(.65,-.17),(.73,.49),(.40,.51),(.37,.08),(.13,.06),(.03,.23),(-.28,.12),(-.38,.48)),
        ((-.65,.25),(-.70,-.06),(-.54,-.36),(-.21,-.41),(.21,-.48),(.49,-.34),(.66,-.13),(.39,.05),(.15,-.02),(-.05,.11),(-.39,.04)),
        ((-.68,.34),(-.65,-.27),(-.35,-.50),(.33,-.46),(.63,-.21),(.67,.51),(.45,.60),(.32,.15),(-.04,.24),(-.33,.05),(-.4,.47)),
    )
    _polygon(s,ink,edge,*points(((-1,1.45),(-.70,.80),(-.36,.65),(.34,.65),(.74,.82),(1,1.45))))
    s.disc(x,y+ry*.24,rx*.47,ry*.55,light,6,edge)
    _polygon(s,ink,edge,*points(contours[style]),density=8)
    _line(s,light,*points(((-.3,.70),(.02,1.16),(.36,.70))))
    if style==0:_line(s,'cyan',*points(((-.51,.35),(-.62,.74),(-.27,1.03))))
    if style==1:s.disc(x+rx*.46*direct,y+ry*.53,rx*.11,ry*.15,light)


def shoreline(part,w,h):
    s=Stage(w,h)
    # Three views of one shore: villa, a meeting on the dock, and the way home.
    s.disc(78,23,9,17,'ochre',4,'gold')
    for i in range(4):s.ring(78,23,10+i*2,18+i*3,'ochre',pi*1.1,pi*1.95)
    for y,x in ((17,18),(24,10),(32,33),(15,48)):
        _line(s,'slate',(x-6,y),(x-3,y-4),(x+5,y-3),(x+11,y))
        _line(s,'teal',(x-3,y+3),(x+8,y+3))
    for j,near in enumerate((False,True)):
        pts=((0,60),(0,37+j*8),(7,32+j*8),(14,15+j*18),(20,19+j*13),
             (27,34+j*8),(35,37+j*8),(39,47+j*5),(50-j*10,53+j*4),(54-j*11,59+j*3))
        _polygon(s,'navy' if near else 'slate','forest' if near else 'teal',*pts,density=7)
        for i in range(7):
            _line(s,'forest' if near else 'teal',(14+i*2,37+i*.7+j*5),(16+i*2,48+j*4+i*.3))
    _polygon(s,'teal','cyan',(0,59),(100,55),(100,100),(0,100),density=4)
    for i in range(45):
        x=(11+i*41)%101;y=61+(i*23)%39
        _line(s,'amber' if abs(x-78)<8 and i%3==0 else 'cyan' if i%3 else 'navy',
              (x,y),(min(100,x+1+((y-60)/4)*(i%3)),y-.3))
    if part==0:
        _polygon(s,'navy','forest',(0,100),(0,76),(15,62),(42,81),(55,100),density=7)
        _polygon(s,'wine','amber',(15,64),(24,49),(39,59),(39,83),(16,83),density=7)
        _polygon(s,'navy','ochre',(11,65),(23,45),(42,58),(39,63),(24,52),(14,67),density=8)
        for j in range(3):
            s.rect(18+j*7,65,4,8,'ochre',6,'amber')
        _line(s,'amber',(15,84),(39,84))
        for x in (4,8,44):
            _line(s,'forest',(x,78),(x+3,44),(x-4,49),(x+2,42),(x+8,53),(x+3,44))
    elif part==1:
        _polygon(s,'navy','amber',(14,100),(53,67),(72,66),(68,100),density=7)
        for i in range(7):
            p=i/6
            _line(s,'ochre',(53-p*39,68+p*30),(72-p*4,67+p*31))
        for x,y in ((50,70),(67,68),(36,80),(24,90),(70,84),(68,96)):
            _line(s,'slate',(x,y+7),(x,y-2))
        figure(s,61,61,3.2,11,3,('ochre','amber','white'))
        figure(s,39,74,4.2,14,0,('navy','cyan','slate'),True)
        _line(s,'rose',(59,70),(61,75),(64,72))
        s.disc(63,72,.55,1.0,'white')
    else:
        _polygon(s,'navy','white',(41,71),(49,71),(50,59),(64,53),(67,71),
                 (84,71),(77,82),(51,85),density=8)
        _line(s,'cyan',(45,77),(78,75))
        _line(s,'slate',(57,56),(55,44),(67,46))
        _line(s,'cyan',(68,64),(78,64),(78,71))
        for x in range(53,65,4):s.rect(x,60,2,5,'teal',7,'slate')
        for z in range(7):_line(s,'cyan',(45-z*4,82+z*2),(55-z*3,82+z*2))
    return s.c.finish()


def _hotel_arch(s,cx,spring,rx,ry,bottom,ink):
    s.ring(cx,spring,rx,ry,ink,pi,tau)
    for side in (-1,1):
        x=cx+rx*side
        _line(s,ink,(x,spring-1),(x,bottom))
        _line(s,'wine',(x+side*1.5,spring),(x+side*1.5,bottom))


def hotel_hall(w,h,floor,room_count,focus):
    s=Stage(w,h)
    boundary='violet' if floor else 'rose'
    _polygon(s,'wine',boundary,(0,3),(100,3),(95,77),(5,77),density=5)
    for y in (16,22,47,66,72,78):
        _line(s,'violet' if y==22 else 'wine',(0,y),(100,y))
    for i in range(0,100,3):
        _line(s,'wine',(i,21),(i,69))
    _polygon(s,'navy','rose',(5,78),(95,78),(100,100),(0,100),density=7)
    for i in range(6):
        y=79+i*i*.86
        _line(s,'wine' if i%2 else 'violet',(0,y),(100,y))
    step=min(27,78/max(1,room_count))
    for i in range(room_count):
        x=50+(i-(room_count-1)*.5)*step
        half=step*.32
        color='rose' if i==focus else boundary
        s.rect(x-half,36,half*2,40,'navy',7,'wine')
        _hotel_arch(s,x,36,half,17,76,color)
        _hotel_arch(s,x,37,half*.76,11,74,'slate')
        s.rect(x-half*.54,42,half*1.09,16,'wine',5,'violet')
        s.disc(x+half*.46,65,1,2,'amber' if i==focus else 'slate')
        s.ring(x,18,2,4,'amber' if i==focus else 'wine')
        _line(s,'rose',(x-half,78),(x-half*1.45,100))
        _line(s,'wine',(x+half,78),(x+half*1.45,100))
    return s.c.finish()


def hotel_still(scene,t,w,h):
    s=Stage(w,h)
    if scene=='exit':
        # Indigo of the pre-dawn city fades into warm stone and an open entrance.
        _sky(s,t,'ochre')
        _city(s,75,'amber')
        s.disc(80,43,9,24,'ochre',4,'amber')
        _polygon(s,'navy','ochre',(25,80),(25,46),(32,46),(32,32),(40,32),(40,20),
                 (60,20),(60,32),(68,32),(68,46),(75,46),(75,80),density=8)
        for x in (29,34,39,61,66,71):
            for y in (51,61,71):s.rect(x,y,2.3,4,'amber',5,'ochre')
        _hotel_arch(s,50,56,11,16,79,'amber')
        s.rect(43,58,14,21,'navy',8,'ochre')
        _line(s,'rose',(50,56),(50,78))
        for i in range(7):
            p=i/6
            _line(s,'ochre' if i%2 else 'slate',(36-p*14,81+p*p*18),(64+p*14,81+p*p*18))
    elif scene=='reunite':
        for j in range(5):
            rx=14+8*j
            _hotel_arch(s,50,50-j*2,rx,12+j*4,70+j*5,'wine' if j%2 else 'violet')
            for dx in (-1,1):
                x=50+dx*(rx-2)
                _line(s,'wine',(x,56-j*2),(x,72+j*5))
        for x in (41,59):
            _hotel_arch(s,x,51,7,13,73,'amber')
            s.rect(x-4,52,8,21,'navy',6,'ochre')
        for j in range(6):
            y=70+j*j*.98
            _line(s,'rose' if j%2 else 'wine',(26-j*4,y),(74+j*4,y))
        for x in (28,72):
            s.ring(x,39,2,8,'rose')
            s.disc(x,39,1,3,'white')
        figure(s,48,71,2.6,11,0,('navy','cyan','slate'))
        figure(s,56,69,2.8,11,1,('wine','rose','amber'),True)
    else:
        raise KeyError(scene)
    return s.c.finish()


def summit_ascent(step,w,h):
    s=Stage(w,h)
    hue='cyan' if step else 'teal'
    _sky(s,step,'slate')
    for side in (-1,1):
        for j in range(4):
            d=8+j*8
            _polygon(s,'navy','slate',(50+side*d,0),(50+side*(d+4),0),
                     (50+side*(d+13),88),(50+side*(d+9),100),density=7)
        for i in range(9):
            y=7+i*8
            _line(s,'teal' if i%2==step else 'navy',(50+side*(7+i/2),y),(50+side*(38+i),y+14))
    _polygon(s,'navy','slate',(41,59),(59,59),(92,100),(8,100),density=7)
    for j in range(12):
        spread=8+j*2.8
        y=58+j*j*.35
        _line(s,hue if (j+step)%3==0 else 'slate',(50-spread,y),(50+spread,y))
    _hotel_arch(s,50,38,9,19,63,hue)
    _hotel_arch(s,50,38,6.5,14,60,'slate')
    for x in (46,50,54):_line(s,'teal',(x,30),(x,61))
    for x in (39,61):s.disc(x,42,1.4,4,'white' if step else 'cyan',6)
    figure(s,49,80,3.7,11,0,('navy','cyan','slate'))
    return s.c.finish()


def summit_seal(beat,w,h,loss=False):
    s=Stage(w,h)
    core='gold' if beat==2 else 'rose' if loss else 'violet'
    ring='cyan' if beat==2 else 'wine' if loss else 'violet'
    _sky(s,beat,'slate')
    for j in range(7):
        rx=14+j*5
        ry=19+j*5
        s.ring(50,38,rx,ry,'navy' if j%3 else ring,.4+j*.2,tau-.3+j*.2)
    for j in range(15):
        a=j*tau/15+beat*.12
        r=15+(j*7)%29
        x=50+cos(a)*r
        y=37+sin(a)*r*1.5
        _line(s,'slate' if j%2 else ring,(x,y),(x+cos(a)*(3+j%5),y+sin(a)*(7+j%5)))
    s.disc(50,36,9.4,17,'navy',8,ring)
    s.ring(50,36,7,12,core)
    s.disc(50,36,4,7,core,5 if beat!=2 else 8)
    if beat==2:
        s.burst(50,36,4,10,'white')
        _line(s,'gold',(50,47),(50,79))
    else:
        for j in range(3):
            _line(s,core,(42+j*4,35),(45+j*3,38),(53+j-j%2,35))
    for side in (-1,1):
        _line(s,'slate',(50+side*6,59),(50+side*18,78),(50+side*38,99))
        _line(s,ring,(50+side*10,61),(50+side*24,84),(50+side*51,98))
    x=45 if loss else 50
    if loss:
        _polygon(s,'navy','slate',(40,94),(47,86),(55,88),(60,97),(45,97))
        s.disc(53,88,2.7,4,'navy',7,'slate')
    else:
        figure(s,x,79,4.1,10,0,('navy','cyan' if beat==2 else 'slate','white'))
        for side in (-1,1):
            _line(s,'gold' if beat==2 else 'white',(x+side*3,86),(x+side*6,76),(x+side*5,69))
    return s.c.finish()
