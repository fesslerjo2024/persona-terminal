"""Original 2×4 dot-art Calling Card animation for the live Persona 5 title."""
from math import cos, hypot, pi, sin

from ..shared.detail_canvas import DotCanvas

DURATION = 5.0
TAU=2*pi
HAT=((-1,-.34),(-.63,-.44),(-.58,-.96),(-.36,-1.04),(.41,-.96),
     (.54,-.85),(.55,-.44),(.99,-.32),(.93,-.19),(.68,-.12),(-.65,-.12),(-1,-.21))
BAND=((-.62,-.49),(.54,-.46),(.56,-.35),(-.65,-.38))
FLAME=((.49,-.49),(.28,-.66),(.39,-.87),(.35,-1.14),(.53,-1.01),
       (.67,-1.21),(.68,-.96),(.87,-.84),(.86,-.60),(.69,-.46))
MASK=((-1,-.10),(-.83,.27),(-.64,.55),(-.42,.69),(-.21,.53),(0,.72),
      (.21,.53),(.42,.69),(.64,.55),(.83,.27),(1,-.10),(.59,.04),(.25,.11),
      (0,.22),(-.25,.11),(-.59,.04))
LEFT_EYE=((-.77,.13),(-.48,.19),(-.23,.31),(-.41,.45),(-.57,.37))
RIGHT_EYE=tuple((-x,y) for x,y in LEFT_EYE)


def _ease(t):
    t=min(1.,max(0.,t))
    return t*t*(3-2*t)


def _city(c,t):
    w,h=c.w,c.h
    depth=.12*_ease(t/4.0)
    horizon=h*.69
    # Tokyo's stacked towers, antennae, lit window clusters and reflective ledge.
    for layer in range(3):
        step=w/(13+layer*.7)
        offset=-w*(depth*(layer-1)+.04)
        for i in range(-1,18):
            x=offset+i*step
            bw=step*(.72+.17*(i*3%5)/5)
            roof=h*(.53+layer*.062-.085*((i*401+layer*53)%11)/11)
            base=horizon+layer*h*.088
            ink=('wine','wine','navy')[layer]
            edge='wine' if layer!=1 else 'red'
            c.face(((x,base),(x,roof+2),(x+bw*.18,roof+1),(x+bw*.22,roof),
                    (x+bw*.61,roof),(x+bw*.66,roof-4),(x+bw*.83,roof-4),
                    (x+bw*.83,roof),(x+bw,roof+3),(x+bw,base)),
                   ink,2 if layer<2 else 4,edge)
            if i%4==2:
                cx=x+bw*.67
                c.line((cx,roof-3),(cx,roof-11-layer),'wine' if layer==0 else 'rose')
                c.put(round(cx),round(roof-12-layer),'rose')
            for j in range(round(roof+5),round(base-2),5):
                for k in range(1,4):
                    q=x+bw*k/4
                    if (i*23+j*17+k*11)%17 < (13 if layer==1 else 8):
                        c.line((q,j),(q+1,j),
                               'ochre' if (i*j+k)%16==0 else 'rose' if layer==1 else 'wine')
    for k in range(3):
        y=h*(.845+k*.020)
        c.line((0,y),(w-1,y+h*.057),'red' if k==0 else 'wine')
    for i in range(70):
        x=(i*91+i*i*17+round(t*5*(i%3)))%max(1,w)
        y=round(h*.88+(i*117)%max(1,round(h*.118)))
        c.line((x,y),(x+1+i%6,y+2+i%2),'wine' if i%5 else 'red')
    for i in range(76):
        x=(i*79+i*i*17+round(t*3*(i%4)))%max(1,w)
        y=(i*73+i*i*13)%max(1,round(h*.59))
        c.put(x,y,'wine' if i%9 else 'rose')


def _sheet(c, x, y, a, b, angle, *, front, edge='white'):
    co,si=cos(angle),sin(angle)

    def xy(u,v):
        uu,vv=u*a,v*b
        return x+co*uu-si*vv,y+si*uu+co*vv

    def shape(points,ink,density=8,outline=None):
        c.face(tuple(xy(u,v) for u,v in points),ink,density,outline)

    # Slight skew is drawn into the paper itself, not stamped in terminal cells.
    cover=((-1,-.94),(.94,-1),(1,-.89),(1,.92),(.91,1),(-1,.97))
    shape(cover,'wine' if front else 'slate',7 if front else 3,
          'rose' if front else edge)
    inner=((-.94,-.89),(.9,-.94),(.94,.88),(.87,.94),(-.94,.91))
    shape(inner,'red' if front else 'navy',6 if front else 3,'rose' if front else 'slate')
    if a<=4 or b<=3:
        return xy

    if front:
        # Foreshortened printed target rings. Keep them inside the paper's edge.
        for rx,ry,pigment in ((.87,.88,'wine'),(.76,.78,'rose'),(.63,.68,'wine'),
                              (.49,.53,'rose'),(.35,.36,'wine'),(.2,.2,'rose')):
            c.path([xy(rx*cos(j*TAU/80),ry*sin(j*TAU/80)) for j in range(81)],pigment)
        def logo(coords,ink,outline=None,density=8):
            shape(tuple((u*.53,(v+.10)*.57) for u,v in coords),ink,density,outline)
        logo(HAT,'wine','white',7)
        logo(BAND,'red','rose',8)
        logo(FLAME,'white','rose',8)
        logo(MASK,'white','rose',8)
        logo(LEFT_EYE,'navy',density=8)
        logo(RIGHT_EYE,'navy',density=8)
        for corner,side in zip(((-.83,-.81),(.81,.81)),(1,-1)):
            u,v=corner
            c.path(tuple(xy(i,j) for i,j in ((u+side*.17,v),(u,v),(u,v+side*.17))), 'white')
    else:
        # Quiet fold lines on the back. No text embedded in the animation.
        for j in range(-4,5):
            h=j*.17
            c.line(xy(-.83,h),xy(.83,h-0.045),'navy')
        c.path(tuple(xy(u,v) for u,v in ((-.89,.8),(0,-.14),(.89,.8))),'slate')
        c.path(tuple(xy(u,v) for u,v in ((-.89,-.79),(0,.15),(.89,-.79))),'slate')
    return xy


def _motion(c,x,y,t):
    for i in range(50):
        f=(i*.053+t*(.21+(i%9)*.039))%1
        if f>.83:continue
        a=x-c.w*(.035+.61*f);b=y+c.h*(.022+.235*f)+(i%9-4)*2
        n=(1-f)*(5+i%12)
        c.line((a,b),(a+n,b-n*.29),'rose' if i%8==1 else 'red' if i%3==0 else 'wine')


def _impact(c,x,y,t):
    f=(t-2.39)/.65
    if not 0<f<1:
        return
    for i in range(34):
        a=pi*(1.0+i/34)
        r=(9+f*c.w*.26)*(1+(i%6)*.088)
        sx,sy=x+r*cos(a),y+r*.63*sin(a)
        n=2+i%5
        c.line((sx,sy),(sx+n*cos(a),sy+n*sin(a)),
               'white' if i%8==0 else 'rose' if i%3 else 'red')


def _landing(c,menu):
    reveal,top,left,span=menu
    if reveal<=0:return
    # The panel is the opened card's inner right-hand page, dark enough
    # for the real title and keyboard choices the host adds after landing.
    x,y=left*2,top*4
    b=min(15*4,c.h-y-2)*reveal
    a=span*2
    drift=(1-reveal)*min(9,c.w//16)*2
    shear=b*.12
    points=((x+drift,y),(x+a+drift,y+1),
            (x+a+drift-shear,y+b),(x+drift-shear,y+b))
    c.face(points,'wine',density=1,edge='rose')
    inner=((x+4+drift,y+3),(x+a-4+drift,y+3),
           (x+a-4+drift-shear,y+b-3),(x+4+drift-shear,y+b-3))
    if b>8:c.face(inner,'wine',density=0,edge='wine')
    if reveal>=1:
        for row in (c.h//4-4,c.h//4-2):
            if row<0:continue
            for micro in range(row*4,min(c.h,row*4+4)):
                c.rows[micro]=[None]*c.w


def render(t,w,h,*,menu=None):
    """Return animated scene rows at the live viewport, never a rescaled cel."""
    t=max(0.,min(float(t),DURATION))
    c=DotCanvas(w,h)
    if not w or not h:return c.finish()
    _city(c,t)
    width,height=c.w,c.h
    a,b=width*.211,height*.265
    if t<2.39:
        p=t/2.39
        path=1-(1-p)**1.63
        x=width*(-.105+.677*path)
        y=height*(.05+.52*p-.087*sin(pi*p))
        squash=cos(p*4*pi)
        scale=.50+.50*path
        _motion(c,x,y,t)
        _sheet(c,x,y,max(1.0,a*scale*abs(squash)),b*scale,
               .75*sin(p*4*pi)*(1-p)+.17,front=squash>0)
    elif t<3.08:
        p=(t-2.39)/.69
        x=width*(.572-.02*_ease(p));y=height*(.57+.037*p-.051*sin(pi*p)*(1-p))
        _impact(c,x,y+b,t)
        _sheet(c,x,y,a,b,.17-.11*_ease(p),front=True)
    else:
        f=_ease((t-3.08)/1.22)
        hinge=width*(.552-.167*(1-f))
        y=height*.607
        thickness=cos(pi*f)
        _sheet(c,hinge+a*.94,y,a*.98,b,.031,front=False,edge='slate')
        if thickness>=0:
            _sheet(c,hinge+a*max(.025,thickness),y-(1-f)*2,a*max(.025,thickness),
                   b,.05*(1-f),front=True)
        else:
            _sheet(c,hinge+a*thickness,y+f*1.2,max(.6,a*abs(thickness)),b,
                   -.041,front=True)
        if f>.38:
            c.line((hinge,y-b),(hinge,y+b),'rose')
    if menu is not None:
        _landing(c,menu)
    return c.finish()
