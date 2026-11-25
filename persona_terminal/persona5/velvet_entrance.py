"""The Persona 5 prison opens as original, layered 2×4 terminal dot art."""
from math import cos, pi, sin

from ..shared.detail_canvas import DotCanvas

DURATION = 2.85


def _ease(t):
    t = min(1., max(0., t))
    return t*t*(3-2*t)


def _rectangle(c,x,y,w,h,ink, density=8, edge=None):
    c.face(((x,y),(x+w,y),(x+w,y+h),(x,y+h)),ink,density,edge)


def _arched_frame(c,x,y,rx,ry,foot,dark,rim):
    c.ring(x,y,rx,ry,dark,pi,2*pi,steps=72)
    c.ring(x,y,rx-2,ry-2,rim,pi,2*pi,steps=72)
    for side in (-1,1):
        c.line((x+side*rx,y),(x+side*rx,foot),dark)
        c.line((x+side*(rx-2),y),(x+side*(rx-2),foot-1),rim)


def _vault(c,t,open_,approach):
    w,h=c.w,c.h
    mid=w*.5
    horizon=h*(.59+.10*approach)
    vanish=(mid,h*(.48+.04*approach))
    # Cylindrical ceiling and opposing upper galleries. The farther vault
    # stays fixed while foreground ironwork moves past the camera.
    for j in range(4,-1,-1):
        depth=.23+j*.17
        rx=w*depth*.49
        ry=h*(.12+j*.050)
        spring=h*(.30-j*.021+approach*.014)
        base=horizon+h*(j*.055)
        _arched_frame(c,mid,spring,rx,ry,base,'navy','slate' if j<3 else 'navy')
    for side in (-1,1):
        panel=(mid+side*w*.17,h*.48)
        end=(mid+side*w*.49,h*.37)
        c.face((panel,end,(end[0],horizon+h*.15),(panel[0],horizon)),
               'navy',2,'navy')
        for j in range(3):
            x=mid+side*w*(.23+j*.104)
            y=h*(.42-.045*j)
            foot=horizon+h*(.014+.052*j)
            r=w*(.018+j*.004)
            _arched_frame(c,x,y,r,h*(.052+j*.013),foot,'navy','slate')
            for i in range(-2,3):
                u=x+i*r/3
                c.line((u,y-h*(.045+j*.008)),(u,foot),'navy')
            c.ellipse(x,h*(.34-.044*j),1.8+j*.7,2.4+j*.35,'teal' if open_>.5 else 'navy',6,
                      'slate')
            c.line((x-2,foot),(x+2,foot),'slate')
        c.line((mid+side*w*.14,h*.45),(mid+side*w*.5,h*.28),'slate')
        c.line((mid+side*w*.13,h*.46),(mid+side*w*.5,h*.32),'navy')
        for i in range(15):
            q=(i+1)/15
            xx=mid+side*w*(.14+.36*q); yy=h*(.45-.17*q)
            c.line((xx,yy),(xx,yy+h*(.007+.031*q)),'navy')
    # Cold polished checker stone in single point perspective.
    bands=(0,.09,.16,.24,.35,.48,.65,.85,1.1)
    for j,(a,b) in enumerate(zip(bands,bands[1:])):
        y=horizon+(h-horizon)*a;yy=horizon+(h-horizon)*b
        scale=.16+a*.88; other=.16+b*.88
        for i in range(-8,8):
            x0=(i/8)*w*.65; x1=((i+1)/8)*w*.65
            c.face(((mid+x0*scale,y),(mid+x1*scale,y),(mid+x1*other,yy),
                    (mid+x0*other,yy)),'navy' if (i+j)%2==0 else 'slate',density=3 if j else 2)
        c.line((mid-w*scale*.62,y),(mid+w*scale*.62,y),'navy')
    for i in range(-7,8):
        c.line(vanish,(mid+w*i*.107,h-1),'navy')
    for i in range(82):
        x=(i*149+i*i*17+round(sin(t*1.03)*i*2))%max(1,w)
        y=(i*23+i*i*3+round(t*6*(1+i%4)))%max(1,round(horizon))
        if i%3 or open_>.28:c.put(x,y,'teal' if i%11==0 else 'navy')
    return horizon


def _staff(c,floor,opening,advance,t):
    w,h=c.w,c.h
    mid=w*.50
    y=h*(.40+.17*advance)
    s=min(w/154,h/110)*(.70+.48*advance)
    def face(x,y,coords,ink,density=8,edge=None):
        c.face(tuple((x+u*s,y+v*s) for u,v in coords),ink,density,edge)
    def line(x,y,a,b,ink):
        c.line((x+a[0]*s,y+a[1]*s),(x+b[0]*s,y+b[1]*s),ink)
    eye='white' if opening>.80 else 'teal'
    # The two smaller wardens bookend Igor's oversized chair.
    for side in (-1,1):
        x=mid+side*s*(33+5*advance)
        yy=y+2*s
        tilt=side*round(sin(t*1.3)*.5)
        face(x,yy,((-9,-4),(-12,-11),(-7,-15),(7,-15),(12,-11),
                   (10,-4),(8,-8),(-8,-8)),'navy',7,'teal')
        face(x,yy,((-7,-8),(-8,-3),(-7,4),(0,7),(7,3),(8,-5),(6,-9)),
             'slate',6,'teal')
        line(x,yy,(-6,-2),(-2,-2),eye if side<0 else 'navy')
        line(x,yy,(2,-2),(6,-2),eye if side>0 else 'navy')
        face(x,yy,((-8,6),(-12,13),(-13,28),(-8,29),(-5,20),(-7,37),
                   (8,37),(6,19),(10,29),(13,28),(12,13),(7,6)),'navy',7,'slate')
        line(x,yy,(-8,7),(0,17),'teal');line(x,yy,(7,7),(0,17),'teal')
        line(x,yy,(tilt,16),(0,26),'white')
        for dy in (20,23,26): c.put(round(x),round(yy+s*dy),'amber')
    # Tall chair back, gaunt cheek, long pointed nose, lapels and gloved hands.
    face(mid,y,((-16,-21),(-11,-29),(11,-29),(16,-21),(15,24),(-15,24)),
         'navy',6,'slate')
    face(mid,y,((-9,-14),(-7,-20),(6,-20),(10,-14),(9,-4),(5,5),(-5,5),(-9,-2)),
         'slate',6,'teal')
    face(mid,y,((-8,-2),(-4,-9),(-2,-9),(2,-3),(9,0),(9,2),(1,3),(-6,2)),
         'white' if opening>.78 else 'slate',5,'teal')
    for side in (-1,1):
        line(mid,y,(side*4,-11),(side*7,-9),eye)
        face(mid,y,((side*6,3),(side*15,8),(side*23,20),(side*12,20),
                    (side*4,11),(0,17),(0,7)),'navy',8,'slate')
        line(mid,y,(side*15,8),(side*6,12),'teal')
        line(mid,y,(side*4,20),(side*15,17),'slate')
    face(mid,y,((-11,18),(-4,16),(0,19),(5,16),(12,18),(10,21),(2,22),(-5,22)),
         'teal',6,'slate')
    # Dark ledger desk and one open compendium, near the final camera mark.
    desk=min(h*.89,max(floor,y+21*s))
    left=mid-w*(.16+.1*advance);right=w-left
    c.face(((left,desk),(right,desk),(right+w*.055,desk+s*12),(left-w*.055,desk+s*12)),
           'navy',7,'teal')
    c.line((left-w*.051,desk+s*10),(right+w*.051,desk+s*10),'slate')
    book=s*12
    c.face(((mid-book,desk+s*1.5),(mid-s*2,desk-s*2),(mid,desk),
            (mid+s*2,desk-s*2),(mid+book,desk+s*1.5),
            (mid+s*4,desk+s*5),(mid,desk+s*4),(mid-s*4,desk+s*5)),
           'slate',6,'white' if opening>.77 else 'teal')
    c.line((mid,desk),(mid,desk+s*4),'teal')
    for side in (-1,1):
        for i in range(3):
            c.line((mid+side*(2+i)*s,desk+s*(.7+i*.85)),
                   (mid+side*(8+i)*s,desk+s*(.1+i*.68)),'navy')


def _doors(c,t,release,push):
    w,h=c.w,c.h
    mid=w*.5
    l=(w*(.10-.09*push)); r=w-l
    top=h*(.20-.09*push);foot=h*(.83+.16*push)
    rx=(r-l)/2
    _arched_frame(c,mid,top,rx,h*(.105+.025*push),foot,'navy','slate')
    for edge,side in ((l,1),(r,-1)):
        a=pi*.5*release
        def local(u,v):
            angle=sin(a)*u
            return edge+side*rx*cos(a)*u,top+(foot-top)*v+h*.054*u*(1-v)+h*.081*angle
        for j in range(14):
            u=j/13
            a0=local(u,0);a1=local(u,1)
            ink='cyan' if .51<t<1.15 and abs(u-(.95-(t-.51)*.6))<.09 else 'slate' if j%3 else 'navy'
            c.line(a0,a1,ink)
            if j%2:
                c.line((a0[0]+side,a0[1]+1),(a1[0]+side,a1[1]-1),'navy')
        for v in (0.,.07,.68,.72,.96,1.):
            c.path([local(j/13,v) for j in range(14)],'slate' if v in (0.,1.) else 'navy')
    if release<.26:
        y=top+(foot-top)*.49+h*.036
        lock=max(4,min(w,h)*.065)
        light=_ease((t-.41)/.60)
        c.ellipse(mid,y,lock*1.23,lock,'navy',8,'teal')
        c.ring(mid,y,lock*.99,lock*.80,'cyan' if light>.36 else 'slate')
        c.ring(mid,y,lock*.73,lock*.57,'slate')
        c.ellipse(mid,y-lock*.19,lock*.21,lock*.21,'amber' if light>.3 else 'teal')
        c.face(((mid,y),(mid-lock*.22,y+lock*.37),(mid+lock*.22,y+lock*.37)),
               'amber' if light>.3 else 'teal')
        if .52<t<1.00:
            r=lock*(1.15+_ease((t-.51)/.49)*1.35)
            c.ring(mid,y,r,r*.75,'teal')


def render(t,w,h):
    c=DotCanvas(w,h)
    if not w or not h:return c.finish()
    t=max(0.,min(DURATION,float(t)))
    release=_ease((t-.85)/1.13)
    advance=_ease((t-1.24)/1.47)
    push=_ease(t/1.20)
    floor=_vault(c,t,release,advance)
    _staff(c,floor,release,advance,t)
    if release<.995:_doors(c,t,release,push)
    return c.finish()
