"""The Persona 5 Terminal calling card, rendered in physical terminal cells."""
from math import cos, hypot, pi, sin
from wide_canvas import Canvas

DURATION = 5.0
_EMBLEM_X = 1.50 * 1.12
_EMBLEM_Y = 1.32 * 1.12
# Character-cell interpretation of the calling-card emblem. The tilted
# top hat and its flame sit above the domino mask, not in the eye cutout.
# Reference: Sega's Royal announcement and the licensed Artovision card.
_HAT = ((-.64,-.91),(.43,-.86),(.60,-.71),(.51,-.24),(.87,-.17),
        (.92,-.05),(.66,.08),(-.65,.06),(-.93,-.04),(-.89,-.19),(-.58,-.24))
_BAND = ((-.59,-.36),(.52,-.40),(.53,-.26),(-.57,-.22))
_FLAME = ((.42,-.40),(.28,-.52),(.38,-.68),(.29,-.84),(.47,-.76),
          (.55,-.96),(.61,-.72),(.74,-.67),(.73,-.51),(.61,-.37))
_MASK = (
    (-.93,.09),(-.58,.19),(-.24,.20),(0,.29),(.24,.20),(.58,.19),(.93,.09),
    (.86,.38),(.69,.59),(.44,.62),(.21,.49),(0,.68),(-.21,.49),
    (-.44,.62),(-.69,.59),(-.86,.38),
)
_LEFT_EYE = ((-.75,.29),(-.49,.29),(-.20,.39),(-.39,.50),(-.58,.46))
_RIGHT_EYE = tuple((-x,y) for x,y in _LEFT_EYE)


def _smooth(x):
    x = min(1., max(0.,x))
    return x*x*(3-2*x)


def _inside(x,y,polygon):
    hit = False
    px,py = polygon[-1]
    for nx,ny in polygon:
        if (py>y)!=(ny>y) and x < (nx-px)*(y-py)/(ny-py)+px:
            hit=not hit
        px,py=nx,ny
    return hit


def _closed(c,poly,ink):
    for a,b in zip(poly,poly[1:]+poly[:1]):
        c.line(*a,*b,ink)


def _city(c,t):
    w,h=c.w,c.h
    travel=_smooth(t/3.9)
    horizon=round(h*(.72+.03*travel))
    # Two silhouettes with misaligned periods. Behind the foreground towers
    # is a narrow vermilion side light, then the unpainted black of the sky.
    for k in range(-1,w//9+3):
        bw=5+(k*7)%11; j=k*9-round(10*travel)
        y=horizon-round(h*(.31+.19*cos(k*1234)))
        c.line(j,y,j+bw,y,'wine','_')
        c.line(j,y,j,horizon,'wine','|')
        c.line(j+bw,y,j+bw,horizon,'wine','|')
        if k%3==0:
            c.line(j+bw//2,y-3,j+bw//2,y,'wine','|')
            c.put(j+bw//2,y-4,'+','rose')
        for r in range(y+2,horizon,3):
            if (r+k*7)%8:
                c.put(j+2,r,'. '*max(1,(bw-2)//2),'wine')
    for k in range(-2,w//8+4):
        j=k*8+round(4*travel); bw=4+(k*11)%6
        y=horizon-round(h*(.11+.11*cos(k*731)))
        c.line(j,y,j+bw,y,'red','_')
        for r in range(y+1,horizon+2):
            strip='-' if (r+k)%7 else '#'
            c.put(j,r,'|'+strip*(bw-1)+'|','dim' if (k+r)%4 else 'wine',opaque=True)
            if r%3==1 and (r+k)%6!=1:
                c.put(j+2,r,':','red')
    # Foreshortened parapet and wet streaks below it.
    c.line(0,horizon+1,w-1,horizon+3,'red','_')
    c.line(0,horizon+2,w-1,horizon+4,'wine','-')
    for k in range(max(12,w//3)):
        x=(k*29+k*k*7+int(t*2)*(k%3+1))%w
        y=horizon+4+(k*11) % max(1,h-horizon-4)
        c.put(x,y,'..' if k%3 else '_-','wine' if k%3 else 'red')
    for k in range(max(9,w//5)):
        x=(k*19+k*k*5+int(t*4))%w
        y=(k*13+k*k//3+int(t*2)*(1+k%2)) % max(1,horizon-3)
        c.put(x,y,'.' if k%5 else '+','wine' if k%5 else 'red')


def _sheet(c,x,y,a,b,angle,kind,shade='white'):
    # Use physical aspect when rotating: one character cell is taller than
    # it is wide. Native rasterisation keeps edges sharp through the tumble.
    co,si=cos(angle),sin(angle)
    def xy(u,v):
        return (x+co*u*a-1.9*si*v*b,y+si*u*a/1.9+co*v*b)
    edge=(xy(-1,-1),xy(1,-1),xy(1,1),xy(-1,1))
    xs,ys=zip(*edge)
    lo=max(0,int(min(xs))); hi=min(c.w-1,round(max(xs)))
    for j in range(max(0,int(min(ys))),min(c.h-1,round(max(ys)))+1):
        for i in range(lo,hi+1):
            dx=i-x; dy=j-y
            u=(co*dx+1.9*si*dy)/a; v=(-si*dx/1.9+co*dy)/b
            if abs(u)>.999 or abs(v)>.999:
                continue
            if kind=='emblem':
                # Use card-space geometry so rings and crest follow the
                # tumble, squash edge-on, and stay inside the paper.
                radius=hypot(u*1.31,(v+.02)*.91)
                ring=int(radius*6.4)
                mark=' ' if ring%2 else '#'
                color='red' if radius<1.30 else 'wine'
                mx=u*_EMBLEM_X+.045
                my=(v-.025)*_EMBLEM_Y
                if _inside(mx,my,_HAT):
                    mark=' '
                if _inside(mx,my,_BAND):
                    mark,color=':','red'
                if _inside(mx,my,_FLAME):
                    mark,color='#','white'
                if _inside(mx,my,_MASK):
                    eye=_inside(mx,my,_LEFT_EYE) or _inside(mx,my,_RIGHT_EYE)
                    mark,color=(' ','dim') if eye else ('#','white')
                c.put(i,j,mark,color,opaque=True)
                continue
            # Plain inner paper at rest, brighter engraved border and a few
            # diagonal fibres. No rows of letters that can read as a title.
            closest=min((1-abs(u))*a,(1-abs(v))*b)
            if closest<.52:
                glyph='-'
            elif closest<1.1:
                glyph=':'
            elif kind=='plain':
                glyph='.' if (round(u*a)+round(v*b)*3)%7==1 else ' '
            else:
                glyph='.' if (round(u*a)-round(v*b)*3)%4 in (0,1) else ' '
            c.put(i,j,glyph,shade,opaque=True)
    _closed(c,edge,'red' if kind=='emblem' else shade)
    # A red printed two-stroke bevel and the faint inner corner, never text.
    for sx,sy in ((-1,1),(1,-1)):
        aa=xy(sx*.91,sy*.83)
        c.line(*aa,*xy(sx*.61,sy*.83),'red','.')
        c.line(*aa,*xy(sx*.91,sy*.61),'red','.')
    if kind=='emblem' and a>6 and b>3:
        emblem=lambda poly: tuple(xy((mx-.045)/_EMBLEM_X,my/_EMBLEM_Y+.025) for mx,my in poly)
        _closed(c,emblem(_HAT),'white')
        _closed(c,emblem(_MASK),'white')
    return xy


def _streak(c,t,x,y,w,h):
    for k in range(max(8,w//7)):
        s=(t*(.38+(k%4)*.08)+k*.097)%1
        if s>.80:
            continue
        x1=round(x-w*(.29+.31*s)+(k*11)%17)
        y1=round(y-h*(.20+.51*s)+k%5-2)
        length=1+round((1-s)*(w*.06))
        c.line(x1,y1,x1+length,y1+round(length*.16),'red' if k%4==0 else 'wine','-')


def _kick(c,w,h,x,y,t):
    p=(t-2.39)/.58
    if not 0<p<1:
        return
    for k in range(22):
        theta=pi*.08+pi*.84*k/21
        r=(w*.03+w*.26*p)*(1+(k%3)*.19)
        xx=x+cos(theta)*r
        yy=y-sin(theta)*r*.36+round(h*.08*p)
        c.put(round(xx),round(yy),('*','+','.')[(k+int(p*8))%3],('red','rose','white')[k%3])


def render(t,w,h):
    """Return scene rows. This renderer never reads menus, saves or key state."""
    t=max(0.,min(float(t),DURATION))
    c=Canvas(w,h)
    if not w or not h:
        return c.finish()
    _city(c,t)
    a=max(3.,w*.195); b=max(2.,h*.255)
    if t<2.39:
        # Flights across both axes and flips edge-on twice, not a fixed-center
        # dissolve. Each scale value is a projected polygon, not glyph zoom.
        f=t/2.39; drift=1-(1-f)**1.6
        x=w*(-.13+.73*drift)
        y=h*(.04+.52*f-.10*sin(f*pi))
        foreshorten=cos(f*4*pi)
        scale=.57+.43*drift
        angle=.84*(1-f)*sin(f*pi*4.1)+.25*(1-f)+.13
        _streak(c,t,x,y,w,h)
        _sheet(c,x,y,max(1.0,a*scale*abs(foreshorten)),b*scale,angle,
               'emblem' if foreshorten>0 else 'plain','white' if foreshorten>0 else 'slate')
    elif t<3.08:
        f=(t-2.39)/.69
        # Paper skips once on landing and its downward corner hits the ledge.
        x=w*(.60-.025*_smooth(f)); y=h*(.56+.025*f-.065*sin(f*pi*1.4)*(1-f))
        _kick(c,w,h,x,y+b,t)
        _sheet(c,x,y,a,b,.13-.055*_smooth(f),'emblem')
    else:
        f=_smooth((t-3.08)/1.22)
        angle=.075*(1-f)+.018*f
        x=w*(.575+.122*f); y=h*.585
        # The cover rolls left about its spine. Only the edge appears at 90°.
        # The inside right page's spread is drawn first and stays exposed.
        prog=cos(pi*f)
        back=a*(1+.04*f)
        hinge=x-back
        _sheet(c,x,y,back,b+.15*f,angle,'plain','white')
        open_a=max(.75,a*abs(prog))
        if prog<0:
            # A small curled inner edge creates a raised fold as it opens.
            left=hinge-open_a
            _sheet(c,left,y-.7*f,open_a,b+.35*f,-angle,'emblem','white')
        else:
            _sheet(c,hinge+open_a,y-.8*sin(pi*f),open_a,b,angle,'emblem','white')
        if f>.45:
            c.line(hinge,y-b+.5,hinge,y+b-.5,'slate','|')
            c.put(round(hinge)-1,round(y+b),r'\/','red')
    return c.finish()
