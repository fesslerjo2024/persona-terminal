"""Native terminal-cell worlds for two full-viewport Showtimes."""
from bisect import bisect_right
from math import cos, pi, sin
from ..shared.wide_canvas import Canvas

ROSE = (1.08, 2.12, 3.08, 4.45, 5.63, 6.12, 7.78)
ROAD = (1.06, 2., 2.93, 4.65, 5.79, 6.23, 7.91)
_LABELS = (
    ("Flower field", "A rose", "Panther turns", "Crossfire", "The toss", "Flower burst", "Petal shower"),
    ("Dust on the horizon", "Skull winds up", "Handoff", "Queen's rush", "Last punch", "Dust impact", "Dust settles"),
)
_HEADS = {
    'panther': ((' .//^\\^\\. ',r'/~/\__/\~\ ',r'|~{>--<}~|',r' \ \__/ / ',r'  \_==_/  '),'rose','face','red'),
    'mona': ((r' /\____/\ ',r'/          \ ',r'| (o)  (o) |',r'\_ /^^\ __/',r'  <-==->  '),'navy','cyan','gold'),
    'skull': ((r' .<~\//>. ',r'/~\\_//~\ ',r'| \O/\O/ |',r'\ \+==+/ /',r'  \_--_/  '),'ochre','white','slate'),
    'queen': ((r' .======. ',r'/ // /// \ ',r'|[======]|',r'\__[]____/',r'   ||||   '),'navy','cyan','queen'),
    'foe': ((r'  /\_/\  ',r' /|/|\|\ ',r'< {o o} >',r' \__*__/ ',r'   |_|   '),'wine','violet','slate'),
}
_COAT = {
    'panther': (r'  _\()/_  ',r' /<<==>>\ ',r'|< [<>] >|',r' \_\==/_/ ',r'   /\/\   '),
    'mona': ('  <>==<>  ',r' /{====}\ ',r'| (....) |',r' \_^^^^_/ ',r'   |__|   '),
    'skull': (r'  _\||/_  ',r' /=\**/=\ ',r'|[]|..|[]|',r' \_|==|_/ ',r'   |##|   '),
    'queen': (r'  _[==]_  ',r' /#\||/#\ ',r'|#<####>#|',r' \#||||#/ ',r'   [##]   '),
    'foe': (r'   _@@_   ',r' /\====/\ ',r'< {|++|} >',r' \_\@@/_/ ',r'   |##|   '),
}
_HELD = {
    'rose': (r'    {@}',r'---<|/ '), 'gun': (r' _______',r'[##===]>', r'  \_\ '),
    'pipe': ('    []','   //','  //',' []'), 'bomb': ("   .'",r' .-*. ', '( @ )'," `-'  "),
    'fist': (r'.-::-.',r'[====}>'," `--' "),
}


def _fract(n):
    return ((n * 25173 + 13849) & 65535) / 65536


def _seek(points, t):
    """Interpolate world positions between timed keyframes, not scaled pixels."""
    for (a, x, y), (b, u, v) in zip(points, points[1:]):
        if a <= t <= b:
            f = (t-a)/(b-a)
            return x+(u-x)*f, y+(v-y)*f
    return points[0][1:] if t < points[0][0] else points[-1][1:]


def _world(c, pos):
    return round((c.w-1)*pos[0]), round((c.h-1)*pos[1])


def _glints(c, t, n, a, b, lo, hi, inks, marks, wind=1):
    # Density in column space remains roughly fixed at larger viewports.
    for j in range(n):
        z=j*133+1099
        x = a + int((( _fract(z) + t*wind*(.015+.055*_fract(z*5)))%1)*(b-a))
        y = lo + int((( _fract(z*3) + t*(.018+_fract(z*7)*.073))%1)*(hi-lo))
        c.put(x,y,marks[(j+int(t*(1+j%3)))%len(marks)],inks[j%len(inks)])


def _sun(c, x, y, r, ink):
    for j in range(-r, r+1):
        span = round(1.9*(max(0,r*r-j*j)**.5))
        if span:
            c.line(x-span,y+j,x+span,y+j,ink, '=' if j%2==0 else '-')
        else:
            c.put(x,y+j,'*',ink)


def _wisps(c, t, ink, level, pace):
    w,h=c.w,c.h
    for j in range(5):
        x=round(((_fract(j*761+121)+t*pace)%1.22-.11)*w)
        y=round(level*h + (j%3-1)*h*.06)
        span=round(w*(.033+.065*_fract(j*11+5)))
        c.line(x-span,y,x,y-1,ink,'_')
        c.line(x,y-1,x+span,y-1,ink,'~')
        if j%2==0:
            c.put(x+span//2,y+1,'- . -',ink)


def _flowerridge(c, t, x, y, bloom, near=False):
    sway = round(sin(t*3+x*.39))
    size = 2 if near else 1
    top = y-size
    c.line(x,y,x+sway,top,'forest','|')
    c.put(x-1,y,r'\|/' if near else '|','teal')
    if near:
        c.put(x+sway-1,top-1,('@%&'[bloom%3])+('o' if bloom%4 else '*'),('rose','wine','white','amber')[bloom%4])
        c.put(x+sway-2,top,'{ @ }',('rose','wine','rose','amber')[bloom%4])
    else:
        c.put(x+sway,top,'*@o%'[bloom%4],('rose','wine','white','amber')[bloom%4])


def _meadow(c, t):
    w,h=c.w,c.h
    _glints(c,t,w//3,0,w,0,h//2,('violet','rose','amber','white'),'.`+*',.55)
    _wisps(c,t,'violet',.24,.012)
    _sun(c,round(w*.70),round(h*.19),max(2,h//10),'amber')
    for band,(level,ink) in enumerate(((.39,'violet'),(.46,'wine'),(.53,'forest'),(.59,'teal'))):
        last=None
        for x in range(0,w+2,3):
            y=round(h*level+sin(x*.096+band*1.01)*h*(.062-band*.008)+sin(x*.31+band)*.7)
            if last:
                c.line(*last,x,y,ink)
                if band>1 and x%6==0: c.line(x,y+1,x+2,y+1,ink,'.')
            last=(x,y)
    # Layer sizes change with distance; nearer stems lean independently in the wind.
    for z, depth in enumerate((.61,.68,.76,.85,.94,1.015)):
        pitch=(3,4,5,6,7,8)[z]
        for x in range(-pitch,w+pitch,pitch):
            y=round(depth*h+sin(x*.29+z)*(1+z*.32))
            _flowerridge(c,t,x+(z*5)%pitch,y,x+z*13,z>=3)
    _glints(c,t,w//2,0,w,1,h,('amber','white','rose','violet'),'+.*%~',1.3)


def _mesa(c, x, y, r, d, ink):
    # Irregular cliffs are continuous parts of the sky rather than a rectangle.
    pts = [(x-r,y),(x-r*2//3,y-1),(x-r//2,y-d),(x+r//3,y-d),
           (x+r//2,y-d+2),(x+r*2//3,y-2),(x+r,y)]
    for a,b in zip(pts,pts[1:]):
        c.line(*a,*b,ink)
    for j in range(2,d+1,2):
        c.line(x-r+j,y-j+1,x+r-j,y-j+1,ink,'.')


def _desert(c,t):
    w,h=c.w,c.h; horizon=round(.47*h)
    _glints(c,t,w//4,0,w,0,horizon,('ochre','amber','slate'),'.-`',.8)
    _wisps(c,t,'ochre',.26,-.018)
    _sun(c,round(w*.28),round(h*.17),max(2,h//11),'amber')
    for i,(u,d) in enumerate(((-.02,3),(.14,5),(.36,3),(.60,6),(.79,4),(1.00,5))):
        _mesa(c,round(w*u),horizon+i%2,round(w*.14),round(d*h/34),('ochre','wine','slate')[i%3])
    # Converging road shoulder and dash marks flow from the distant horizon.
    vanish=round(w*.49)
    c.line(0,horizon+1,w-1,horizon+1,'ochre','.')
    for p in (-.78,-.64,.61,.75):
        c.line(vanish,horizon,round(vanish+p*w),h-1,'slate' if abs(p)>.65 else 'gold')
    for j in range(9):
        f=(j/9+t*.34)%1
        yi=horizon+round((h-horizon-1)*f*f)
        xi=vanish+round(w*.12*f)
        c.line(xi,yi,xi+round(2*f),yi+round(1.5*f),'gold','=')
    for j in range(6):
        p=(j*.22+t*.13)%1
        y=horizon+round((h-horizon-1)*p)
        side=-1 if j%2 else 1
        x=round(vanish+side*w*p*.7)
        c.put(x-1,y-max(1,round(p*3)),r'~' if p<.5 else ':^:' ,'ochre')
        c.line(x,y,x,y-max(1,round(p*3)),'slate','|')
    for side in (0,1):
        a,b=(0,w//5) if not side else (4*w//5,w)
        _glints(c,t,w//3,a,b,horizon+1,h,('ochre','wine','amber'),'.~:_',-1)
    _glints(c,t,w//5,0,w,horizon-1,h,('ochre','amber','slate'),'.`~',-2)
    for j in range(w//6):
        u=(_fract(337*j+71)-.06*t)%1
        if .07<u<.93 and j%3:
            continue
        x=int(u*w)
        c.put(x,h-1,'._' if j%2 else '--','ochre')


def _figure(c, name, pos, t, pose='stand', prop=None):
    """Compose readable costume cels with independent shoulders, legs, and arms."""
    x,y=_world(c,pos)
    tall=c.h>=30 and c.w>=76
    head, trim, bright, cloth=_HEADS[name]
    n=12 if tall else 9
    if name=='mona':
        n-=3
    top=y-n
    torso=top+(5 if tall else 4)
    sash = ('red' if name=='panther' else 'gold' if name=='mona' else bright)
    # A two-tier shadow anchors feet to the floor when not airborne.
    if pose not in ('jump','fall','throw'):
        c.put(x-6,y, '._--______--_.' if tall else '._-____-_.', 'forest' if name in ('mona','panther') else 'slate')
    if pose=='fall':
        c.put(x-6,y-2,('   .---.  ___ ',r'__/[^*^]\//_/\ ',r'\____##==\___/'),'foe')
        return x+4,y-2
    if pose=='stagger':
        x+=round(-sin(14*t)*1.7)
        top+=1
        torso+=1
    width=10
    # Opaque at actual contours only: no gray art-plate or padded rectangles.
    for j,rows in enumerate(((head if tall else head[1:]), (_COAT[name] if tall else _COAT[name][1:4]))):
        base=top if not j else torso
        for k,row in enumerate(rows):
            cropped=row.strip()
            first=row.index(cropped)
            color=(bright if k==2 or (name=='mona' and k==1) else trim) if not j else (sash if k==1 else cloth)
            c.put(x-width//2+first,base+k,cropped,color,opaque=True)
    sy=torso+1
    hip=min(y-2,torso+(4 if tall else 3))
    # Bend at elbows/knees; stance fidgets even during an attack held for a few frames.
    stride=sin(t*(24 if pose in ('run','dash') else 6))
    kick=round(4*stride) if pose in ('run','dash') else round(stride)
    rise=round(abs(stride)*2) if pose in ('run','dash','jump') else 0
    for sign in (-1,1):
        toe=x+sign*(4 if tall else 3)+kick*sign
        knee=x+sign*2+kick//2
        fy=y-(rise if (sign>0)==(stride>0) else 0)
        c.line(x+sign,hip,knee,hip+1,cloth)
        c.line(knee,hip+1,toe,fy-1,cloth)
        c.put(toe-(2 if sign<0 else 1),fy-1,'[_]' if tall else '[]',trim)
    left=(x-6+(kick//2),sy+2+(1 if pose=='stand' else 0))
    right=(x+5,sy+2)
    if pose in ('aim','shoot','offer','dash','punch'):
        reach=(8 if tall else 6)+(round(abs(stride)*2) if pose in ('shoot','punch','dash') else 0)
        d=round(sin(t*28)) if pose in ('shoot','punch') else 0
        right=(x+reach,sy+d-1)
        if pose in ('aim','shoot','punch'):
            left=(x+reach-3,sy+d+1)
    elif pose=='throw':
        right=(x+7,sy-4)
        left=(x-7,sy)
    elif pose=='wind':
        right=(x-8,sy-4)
        left=(x-8,sy-1)
    elif pose in ('run','jump'):
        right=(x+6+kick,sy-1)
    for sign,(ex,ey) in zip((-1,1),(left,right)):
        sx=x+sign*4
        mx=round((sx+ex)/2)+sign; my=round((sy+ey)/2)+1
        c.line(sx,sy,mx,my,cloth)
        c.line(mx,my,ex,ey,trim)
        c.put(ex,ey,'o' if name=='mona' else '+' if pose=='punch' else '#',bright)
    if prop:
        color={'bomb':'gold','rose':'rose','gun':'white','pipe':'slate','fist':'cyan'}[prop]
        px,py=right
        c.put(px-3 if prop in ('pipe','bomb') else px,py-3 if pose=='wind' else py-1,_HELD[prop],color)
    return right


def _impact(c,x,y, f, inks, n=35):
    span=max(3,int(c.w*(.10+f*.27)))
    for j in range(n):
        a=2*pi*j/n+sin(j*8.1)*.25
        d=span*(.32+.68*_fract(j*177+59))
        xx=x+round(cos(a)*d); yy=y+round(sin(a)*d*.42+f*f*6)
        if j%4==0 and f<.48:
            c.line(x+round(cos(a)*d*.46),y+round(sin(a)*d*.20),xx,yy,inks[j%len(inks)])
        c.put(xx,yy,'*.+@~'[j%5],inks[j%len(inks)])
    if f<.43:
        c.put(x-4,y-1, (r'\ .|. /',r'--{*}--',r'/ `|` \ '),inks[0])


def _streak(c, origin, to, t, ink, gun=True):
    x,y=origin; u,v=to
    phase=(t*(15 if gun else 12))%1
    a=min(.91,phase)
    b=min(1.,a+(0.42 if gun else .55))
    c.line(x+(u-x)*a,y+(v-y)*a,x+(u-x)*b,y+(v-y)*b,ink,'-' if gun else '=')
    if gun and phase<.54:
        c.put(x-1,y-1,(r' \|/',r'<-*>',r' /|\ '),'amber')


def _rose(c,t,i):
    _meadow(c,t)
    mona=_seek(((0,.10,.83),(1.1,.23,.82),(2.12,.32,.82),(3.1,.25,.83),
                (4.45,.21,.85),(5.06,.32,.76),(5.63,.24,.85),(6.15,.16,.87),(7.78,.26,.85)),t)
    panther=_seek(((0,.58,.83),(1.08,.54,.83),(2.12,.52,.83),(3.08,.55,.81),
                   (4.45,.56,.82),(5.63,.51,.86),(6.12,.45,.84),(7.78,.47,.84)),t)
    foe=_seek(((0,.92,.77),(1.08,.83,.78),(3.08,.82,.78),(4.45,.89,.77),
               (5.63,.85,.80),(6.12,.92,.91),(7.78,.97,.93)),t)
    ft=_world(c,foe)
    _figure(c,'foe',foe,t,'stagger' if i in (3,5) else 'fall' if i==6 else 'run' if i==0 else 'stand')
    mpose=('run','offer','stand','stand','throw','jump','run')[i]
    _figure(c,'mona',mona,t,mpose,'rose' if i in (0,1,6) else 'bomb' if i==4 and t<4.74 else None)
    if i==2:
        x,y=_world(c,panther)
        c.put(x-11,y-8+round(sin(t*20)),r'^/~----','rose')
    ppose=('stand','stand','aim','shoot','aim','jump','stand')[i]
    muzzle=_figure(c,'panther',panther,t,ppose,'gun' if 2<=i<=4 else None)
    if i==3:
        for j in range(2):
            _streak(c,(muzzle[0]+4,muzzle[1]+j), (ft[0] - 2,ft[1]-8+j),t+.035*j,'white' if j==0 else 'amber')
        if int(t*14)%3!=1:
            _impact(c,ft[0],ft[1]-8,(t*4)%1,('white','amber','rose'),11)
    elif i==4 and t>=4.74:
        f=(t-4.74)/.89
        x,y=_world(c,(.38+f*.47,.56-.41*sin(pi*f)))
        c.put(x-2,y-3,_HELD['bomb'],'gold',opaque=False)
        for j in range(1,7):
            q=max(0,f-j*.025)
            sx,sy=_world(c,(.38+q*.47,.57-.41*sin(pi*q)))
            c.put(sx-1,sy,'*' if j<3 else '.',('amber','rose','white')[j%3])
    elif i>=5:
        f=(t-5.63)/(7.78-5.63)
        _impact(c,ft[0]-3,round(c.h*.54),f,('white','rose','amber','wine'),max(25,c.w//2))
        _glints(c,t,c.w//2,0,c.w,0,c.h,('rose','wine','amber','white'),'@+*%.',1.4)


def _road(c,t,i):
    _desert(c,t)
    skull=_seek(((0,.12,.81),(1.06,.24,.81),(2,.30,.82),(2.5,.47,.81),(2.93,.39,.85),
                 (3.5,.29,.87),(4.65,.12,.88),(6.23,.14,.86),(7.91,.25,.87)),t)
    queen=_seek(((0,.035,.86),(1.06,.13,.86),(2,.14,.85),(2.93,.34,.8),(3.62,.49,.79),
                  (4.65,.61,.78),(5.79,.78,.78),(6.23,.65,.75),(7.91,.59,.84)),t)
    foe=_seek(((0,.92,.76),(1.06,.73,.76),(2,.70,.77),(2.93,.77,.77),
                (4.65,.88,.79),(5.79,.94,.84),(6.23,.96,.92),(7.91,.89,.91)),t)
    ft=_world(c,foe)
    _figure(c,'foe',foe,t,'fall' if i>=6 else 'stagger' if i>=2 else 'run')
    hand=_figure(c,'skull',skull,t,('run','wind','dash','stand','stand','jump','run')[i],
                 'pipe' if i<=2 or i==6 else None)
    fist=_figure(c,'queen',queen,t,('run','stand','run','punch','punch','jump','stand')[i],
                 'fist' if 3<=i<=5 else None)
    if i==2 and t>2.38:
        _streak(c,hand,(ft[0]-5,ft[1]-7),t,'amber',False)
        _impact(c,ft[0]-3,ft[1]-7,(t*5)%1,('amber','gold','cyan'),10)
    elif i in (3,4):
        for j in range(5 if i==3 else 3):
            f=(t*13+j*.25)%1
            x=round(fist[0]+(ft[0]-fist[0])*f)
            y=fist[1]+(j%3-1)*2+round(2*sin(f*pi))
            c.put(x-5,y,('==(o)>' if j%2 else '-(=)>'),('cyan','white','teal')[j%3])
        if i==4 or int(t*9)%2:
            _impact(c,ft[0]-3,ft[1]-7,(t*7)%1,('white','cyan','amber'),17)
    elif i>=5:
        f=(t-5.79)/(7.91-5.79)
        _impact(c,ft[0]-8,round(c.h*.63),f,('white','ochre','gold','amber'),max(26,c.w//2))
        _glints(c,t,c.w//2,0,c.w,c.h//3,c.h,('ochre','gold','amber','slate'),'~*-.',-2)


def render(title,t,w,h):
    """Return (internal beat label, exact-width colored ASCII runs)."""
    road=title.upper()=="HIGHWAY TO TROUBLE"
    intervals=ROAD if road else ROSE
    now=max(0.,min(float(t),intervals[-1]-.0001))
    i=bisect_right(intervals,now)
    c=Canvas(w,h)
    (_road if road else _rose)(c,now,i)
    return _LABELS[road][i],c.finish()
