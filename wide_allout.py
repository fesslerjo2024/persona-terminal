"""Borderless, responsive reblocking of the nine All-Out action reels.

Shapes follow paths measured against the actual viewport; authored marks,
masks and props remain single-cell ASCII, never stretched or duplicated.
"""
from math import cos, sin, pi, tau

from wide_canvas import Canvas
from allout_scenes import ACCENT, HEAD, PETALS, SECS, SHARDS, TITLES


BY_TITLE={title:who for who,title in TITLES.items()}


def R(x):
    return round(x)


def P(c,x,y,text,ink,opaque=False):
    c.put(R(x),R(y),text,ink,opaque=opaque)


def L(c,a,b,ink,ch=None):
    c.line(R(a[0]),R(a[1]),R(b[0]),R(b[1]),ink,ch)


def chain(c,pts,ink,ch=None):
    for a,b in zip(pts,pts[1:]): L(c,a,b,ink,ch)


def orbit(c,x,y,rx,ry,start,sweep,ink,ch='.',count=24):
    for i in range(count):
        arg=start+sweep*i/max(count-1,1)
        P(c,x+rx*cos(arg),y+ry*sin(arg),ch,ink)


def spark(c,x,y,ink,r=1):
    P(c,x,y,'*',ink)
    if r>1:
        for dx,dy,mark in [(-r,0,'-'),(r,0,'-'),(0,-1,'|'),(0,1,'|')]:
            P(c,x+dx,y+dy,mark,ink)


def _ghost(c,x,y,unit,phase,face=1):
    tint=ACCENT[unit]
    stride=sin(phase)*3
    P(c,x-2,y-2,HEAD[unit],'face',True)
    P(c,x-2,y+1,r'/##\\',tint)
    chain(c,((x,y+1),(x+face*3,y),(x+face*6,y+1)),tint)
    chain(c,((x,y+1),(x-face*2,y+2),(x-face*5,y+1)),'rail')
    chain(c,((x,y+2),(x+stride,y+3),(x+stride*1.5,y+6)),'face')
    chain(c,((x,y+2),(x-stride,y+4),(x-stride*1.2,y+6)),tint)


def _charge(c,w,h,t,ink):
    cx,cy=(w-1)*.5,(h-1)*.48
    for i in range(w//4+8):
        a=(i+.22)*tau/(w//4+8)
        near=1-.71*t
        end=(cx+(w*.7+3)*cos(a),cy+(h*.78+2)*sin(a))
        start=(cx+near*w*.34*cos(a),cy+near*h*.38*sin(a))
        L(c,start,end,'red' if i%3 else 'rail',SHARDS[(i+int(t*10))%len(SHARDS)])
    for i,(u,x,y,face) in enumerate((('Joker',.03,.15,1),('Mona',.94,.13,-1),
                                    ('Skull',.04,.77,1),('Panther',.93,.76,-1))):
        px=(x+( (.44 if face==1 else .56)-x)*t)*w
        py=(y+(.38-y)*t)*h+sin(t*tau+i)*.7
        L(c,(px-17*face,py+2),(px-3*face,py+2),ink,'-')
        _ghost(c,px,py,u,t*tau*2+i,face)
    for x in (-.08,0,.08):
        px=cx+x*w*(1-t)
        P(c,px-2,cy,('/\\ /\\','[:::]','/###\\'),'rail',True)


def _impact(c,w,h,t,ink):
    cx,cy=(w-1)/2,(h-1)*.47
    n=w//3+8
    for i in range(n):
        a=(i+.21)*tau/n
        d=max(w,h*1.7)*.05
        dx,dy=cos(a)*w,sin(a)*h
        point=lambda r:(cx+r*dx,cy+r*dy)
        start=.03+.52*t
        end=start+.51+.12*(i%3)
        L(c,point(start),point(end), 'white' if i%4==0 else ink,
          SHARDS[(i+int(t*5))%len(SHARDS)])
        fx,fy=point(start*.77+.06)
        if i%3==0:spark(c,fx,fy,'gold' if i%2 else 'red',2)
    r=5+w*t*.43
    orbit(c,cx,cy,r,r*h/w,0,tau,'white','*',w//3+13)


def _floor(c,w,h,t,mark,ink):
    iy=R(h*.84)
    for i in range(-1,w//8+2):
        x=i*8-R(t*18)%8
        P(c,x,iy,mark,ink)
        if i%2==0:P(c,x+3,iy+2,',','dim')
    # Short, separate reflections avoid both a frame and a horizon rule.
    for i in range(w//13+1):
        x=i*13+R(t*19)%13
        L(c,(x,h*.93),(x+5,h*.91),'dim','.')


def _field(c,w,h,t,who,x,y):
    rim=ACCENT[who]
    if who=='Joker':
        _floor(c,w,h,t,'.  .','rail')
        for j in range(w//3):
            a=j*tau/max(1,w//3)
            sx=x+(.15+.59*t)*w*cos(a)
            sy=y+(.14+.61*t)*h*sin(a)+t*t*(j%3)
            P(c,sx,sy,SHARDS[j%6],'red' if j%4==0 else 'rail')
        for i in range(5):
            L(c,(w*(.02+i*.05),h*(.22+i*.10)),(x-w*.08,y+2+i),rim,':')
    elif who=='Mona':
        for yy in (.12,.80):
            for xx in range(-4,w+4,6):
                P(c,xx-R(t*30)%6,yy*h,'[]','rail')
        for i in range(w//18):
            a=i*18+R(t*11)%18
            chain(c,((a,h*.2),(a+5,h*.19),(a+9,h*.42)),'dim','.')
        stamp=sin(pi*max(0,(t-.34)/.66))
        if t>.34:
            tx=w*(.83-.08*t); ty=h*(.64-.24*stamp)
            P(c,tx-6,ty-4,(' * * * * ','*       *','  (   )  ','  (___)  '),'red')
            orbit(c,tx-2,ty-2,7+8*t,3+3*t,t*tau,tau,'red','.',35)
    elif who=='Skull':
        _floor(c,w,h,t,'/!/','gold')
        for i in range(w//11+2):
            px=i*11-R(t*18)%11
            P(c,px,h*.16,'/!/','rail')
            if i%2:P(c,px-2,h*.73,'!/','dim')
        for j in range(8):
            px=w*(.49+.37*t)+j*2
            cy=h*.71-j
            if t>.20:L(c,(px-4,cy+2),(px+j,cy-j),'gold','+' if j%2 else '/')
    elif who=='Panther':
        for j in range(w//6+2):
            xx=(j*11+t*w*.9)%w
            yy=h*(.12+.68*((j*13)%31)/31)
            P(c,xx,yy,'<>' if j%3==0 else '*','rope' if j%2 else 'red')
        orbit(c,w*.53,h*.48,w*.49,h*.36,t*3,tau,'rope','.',w//2)
        _floor(c,w,h,t,'+ . +','rope')
    elif who=='Fox':
        _floor(c,w,h,t,'~  ~','dim')
        past=0
        for i in range(w//2):
            z=i/max(w//2-1,1)
            sx=w*(.08+.86*z); sy=h*(.32+.08*sin(z*tau*1.4-t*tau))
            if z<.44+.56*t:
                P(c,sx,sy,'~' if i%3 else '.','red')
                if i%3==0:P(c,sx+1,sy+1,'-','rail')
                past=(sx,sy)
        if past:
            P(c,past[0]-3,past[1]-2,(' /\\_/\\ ',r'<[. .]>',r' \_/_~~'),'red')
        for i in range(w//10):
            P(c,(i*23+w*t*.3)%w,(i*7+h*t*.4)%h,'*','rope')
    elif who=='Queen':
        _floor(c,w,h,t,'==  ==','rail')
        for j in range(3,max(4,R(h*.80)),3):
            for i in range((R(t*15)+j)%9,w,9):
                P(c,i,j,'<>' if (j//3)%2 else '[]','rail')
        for i in range(7):
            L(c,(x-w*.33,y+i-3),(x-5+i,y+i-3),'red' if i%3==0 else 'rail','-')
    elif who=='Noir':
        _floor(c,w,h,t,'.  .','rope')
        orbit(c,w*.53,h*.48,w*.46,h*.38,t*tau*.16,tau,'rope','.',w+12)
        orbit(c,w*.54,h*.48,w*.43,h*.34,-t*tau*.12,tau,'rail','.',w//2+4)
        for i in range(w//11+2):
            px=(i*19+R(w*.11*t))%w
            py=(i*7+R(h*.45*t))%max(1,R(h*.81))
            P(c,px,py,(' .*. ','*+*+*',r' \|/ '),'rope')
    elif who=='Crow':
        _floor(c,w,h,t,'/  /','dim')
        for yy in (.23,.73):
            for xx in range(0,w,4):
                if abs(xx-x)<t*w*.25:continue
                ypos=h*yy+(xx-w*.5)*(.10 if yy<.5 else -.08)
                P(c,xx,ypos,'-=-','red')
                P(c,xx+1,ypos-1,'/' if xx%8 else '\\','rail')
        for i in range(7):
            L(c,(x+w*.03+i*5,h*.87),(x+w*.3+i*3,h*.16),'dim','/')
    elif who=='Violet':
        _floor(c,w,h,t,'. .','rope')
        for i in range(w//2+8):
            a=i*tau/(w//2+8)+t*tau*.76
            rx=w*(.13+(i%6)*.045+.15*t)
            ry=h*(.09+(i%4)*.059)
            px=x+rx*cos(a); py=y+ry*sin(a)+h*.22*t*t
            P(c,px,py,PETALS[i%len(PETALS)],'red' if i%3 else 'rope')
        orbit(c,w*.60,h*.48,w*.39,h*.31,t*2,tau,'rope','.',w//2+14)


def _fighter(c,who,x,y,scale,dx,lean,back,main,left,right,phase):
    """Block torso and line-art sleeves/breeches rig around animated joints."""
    ink=ACCENT[who]
    if who=='Mona':scale*=.66
    s=scale
    shoulder=max(2,R(2.4*s)); hipw=max(1,R(1.7*s))
    hip=(x-lean*s,y+3*s)
    head=(x+lean*s*.15,y-1.5*s)
    for index,(sx,kick) in enumerate((left,right)):
        sign=-1 if not index else 1
        hipx=hip[0]+sign*hipw
        foot=(hip[0]+sx*s, y+(6.2-kick)*s)
        knee=((hipx+foot[0])*.5+dx*s*.9,hip[1]+(1.25-kick*.48)*s)
        tint='rail' if not index else 'face'
        chain(c,((hipx,hip[1]),knee,foot),tint)
        chain(c,((hipx+sign,hip[1]),(knee[0]+sign,knee[1]),
                 (foot[0]+sign,foot[1])),ink if index else 'dim')
        P(c,foot[0]-int(dx<0),foot[1],'__',ink)

    # Coat and tunic seams form a silhouette rather than magnified pixels.
    outer=[(x-shoulder,y),(x+shoulder,y),(hip[0]+hipw,hip[1]),
           (hip[0]-hipw,hip[1]),(x-shoulder,y)]
    chain(c,outer,ink)
    for side in (-1,1):
        A=(x+side*shoulder,y+.25*s)
        d=back if side==-1 else main
        hand=(x+d[0]*s,y+d[1]*s)
        elbow=((A[0]+hand[0])*.5+side*.55*s, (A[1]+hand[1])*.5+side*.63*s)
        tint='rail' if side==-1 else ink
        chain(c,(A,elbow,hand),tint)
        if s>=1.30:
            chain(c,((A[0],A[1]+1),(elbow[0],elbow[1]+1),(hand[0],hand[1]+1)),
                  tint)
        P(c,hand[0],hand[1],'+' if side==1 else '#',tint)
    rows=HEAD[who]
    P(c,head[0]-2,head[1]-max(len(rows)-2,0),rows,'face',True)
    if who in ('Joker','Crow','Violet'):
        fl=(6+2*abs(sin(phase*tau*2)))*s
        p0=(x-dx*shoulder,y+1)
        p1=(hip[0]-dx*fl,hip[1]+s)
        p2=(hip[0]-dx*(fl+1.5*s),hip[1]+2*s)
        chain(c,(p0,p1,p2,(hip[0]-dx*hipw,hip[1])),ink,':' if who=='Violet' else '\\')
        for z in range(1,max(2,R(s*3))):
            L(c,(p0[0],p0[1]+z*.5),(p2[0]+dx*z,p2[1]-z*.6),'rail','.')
    if who=='Queen':
        for side in (-1,1):
            P(c,x+side*(shoulder+1),y-.7*s,'^','white')
            P(c,x+side*(shoulder-1),y+.7*s,'[]','cyan')
    if who=='Noir':
        P(c,head[0]-4,head[1],'========','rope')
        P(c,x-1,y+.45*s,'><','rope')
    if who=='Skull':
        L(c,(x-dx*1,y+.85*s),(x-dx*6.5*s,y+sin(phase*tau)*s),'red','~')
    if who=='Mona':
        L(c,(x-1,y+1),(x-5*s,y+1.7*s),'gold','~')
    if who=='Panther':
        chain(c,(hip,(hip[0]-dx*5*s,hip[1]-s),
                (hip[0]-dx*7*s,hip[1]+sin(phase*tau)*s)),ink,'~')
    return x+main[0]*s,y+main[1]*s


def _mona_roll(c,x,y,scale,t):
    # One cartwheel, keeping the cat ears, four limbs and gold scarf
    # connected while the body turns through the apex of its jump.
    phase=max(0,min(1,(t-.09)/.78))
    angle=tau*phase
    s=scale*.82
    cs,sn=cos(angle),sin(angle)
    def pt(a,b):
        return x+s*(cs*a-2*sn*b),y+s*(.5*sn*a+cs*b)
    for ear in (-1,1):
        chain(c,tuple(pt(a*ear,b) for a,b in ((1,-2),(3,-3),(3,-.65))),'face')
    chain(c,tuple(pt(a,b) for a,b in ((-3,-.6),(-2.6,.6),(0,1),
                                  (2.6,.6),(3,-.6),(1,-2),(-1,-2),(-3,-.6))),'face')
    for side in (-1,1):
        P(c,*pt(side*1.3,-.5),'.','cyan')
        chain(c,tuple(pt(a*side,b) for a,b in ((1.1,.9),(2.6,1.7),(3.9,1.1))),'cyan')
        chain(c,tuple(pt(a*side,b) for a,b in ((1.3,2.1),(2,3),(3.2,3.4))),'rope')
    chain(c,tuple(pt(a,b) for a,b in ((-1,1),(-3.4,1.45),(-5.3,1.1))),'gold','~')
    chain(c,tuple(pt(a,b) for a,b in ((-1.35,2.25),(-1.15,1),(1.15,1),
                                  (1.35,2.25),(-1.35,2.25))),'cyan')
    return pt(3.8,1.1)


def _finish(c,w,h,t,who):
    s=max(.8,min(2.8,h*.064,w*.024))
    # Each fighter's shoulder trajectory (including the reversal for Fox and
    # Noir) and foot/hand offsets is choreographed in terminal coordinates.
    if who=='Joker':
        x=w*(.22+.52*(1-(1-t)**1.6)); y=h*(.45+.07*sin(pi*t))
        pose=(1,2.2,(-5,1.7),(7-8*t,-1+3*t),(-7,0),(7,.8))
    elif who=='Mona':
        x=w*(.16+.64*t); y=h*(.62-.37*sin(pi*t)**2)
        pose=(1,sin(t*tau),(-3,1.4),(4,-1),(-5,1.2),(4,1.7))
    elif who=='Skull':
        x=w*(.25+.36*t); y=h*(.56-.26*max(0,1-t*2.3))
        pose=(1,1,(-5,-.5),(7,-2-2*sin(pi*t)),(-6,.6),(5,0))
    elif who=='Panther':
        x=w*(.21+.51*t); y=h*(.52-.22*abs(sin(pi*t*1.38)))
        pose=(1,2,(-6,2),(5,-1),(-6,0),(7,2*sin(pi*t)))
    elif who=='Fox':
        x=w*(.75-.41*t); y=h*(.53-.17*sin(pi*t))
        pose=(-1,-2.4,(-5,1),(9*cos(pi*t),-2+4*t),(-7,0),(6,.8))
    elif who=='Queen':
        x=w*(.18+.54*t); y=h*(.53-.13*abs(sin(tau*t)))
        pose=(1,3.5,(-3,2.4),(6+5*sin(pi*t),0),(-8,1.0),(8,1.0))
    elif who=='Noir':
        x=w*(.44+.09*sin(pi*t)); y=h*(.53-.14*sin(pi*t))
        turn=cos(t*tau)
        pose=(1,1.5*turn,(-5,1),(5,-1),(-4-3*turn,0),(5-3*turn,1))
    elif who=='Crow':
        x=w*(.18+.57*(1-(1-t)**1.3)); y=h*(.58-.24*sin(pi*t))
        slash=.2+t*tau*.62
        pose=(1,3,(-6,0),(9*cos(slash),4*sin(slash)),(-8,1),(7,0))
    else:
        x=w*(.27+.46*t); y=h*(.57-.23*abs(sin(t*tau)))
        turn=sin(t*tau)
        pose=(1 if t<.5 else -1,2*turn,(-4+3*turn,-1),
              (7*cos(pi*t),-3.8*sin(pi*t)),(-5-5*turn,max(0,turn)*3),
              (6-5*turn,max(0,-turn)*2.7))
    _field(c,w,h,t,who,x,y)
    hx,hy=_mona_roll(c,x,y,s,t) if who=='Mona' else _fighter(c,who,x,y,s,*pose,t)
    if who=='Joker':
        L(c,(hx,hy),(hx+5*s,hy-1.5*s),'white','=')
        spark(c,hx+5*s,hy-1.5*s,'red',2)
    elif who=='Mona':
        # Staggered crescent follows the airborne full-body cartwheel arc.
        orbit(c,x-3*s,y,10*s,4*s,t*3+1.2,pi,'cyan','.',18)
    elif who=='Skull':
        P(c,hx-1,hy-1,r'| |','gold')
        P(c,hx-1,hy-2,r"' '",'gold')
    elif who=='Panther':
        points=[(hx+j/22*w*.30,hy+(j/22)*h*.23*sin(j*.29-t*tau*2))
                for j in range(23)]
        chain(c,points,'red','~')
        P(c,*points[-1],'<>','rope')
    elif who=='Fox':
        L(c,(hx,hy),(hx-10*s,hy-2*s),'white','=')
        orbit(c,x,y-1,w*.25,h*.19,t*pi+.45,pi*.64,'cyan','=',w//3)
    elif who=='Queen':
        for i in range(6):
            spark(c,hx+2+i*w*.026,hy+(i%3)-1,'red' if i%2 else 'white',1+(i%2))
    elif who=='Noir':
        throw=sin(pi*t)
        tx=hx+w*.20*throw; ty=hy-h*.28*throw
        P(c,tx,ty,(' ___ ',r'\___/)'," === "),'cyan')
        orbit(c,tx-1,ty+1,5*s,3*s,1.4,3,'white','.',20)
    elif who=='Crow':
        tip=(hx+cos(slash)*7*s,hy+sin(slash)*3*s)
        L(c,(hx,hy),tip,'white','=')
        orbit(c,x,y,w*.24,h*.28,slash-.4,1.9,'red','/',w//3)
    else:
        tip=(hx+6*s,hy-s)
        L(c,(hx,hy),tip,'white','=')
        spark(c,*tip,'red',2)


def render(title,elapsed,width,height):
    """Return an empty label and exactly one ASCII run-frame for the viewport."""
    who=BY_TITLE[title]
    w,h=max(1,width),max(1,height)
    c=Canvas(w,h)
    t=max(0,min(elapsed,SECS[who]))
    if t<.53:_charge(c,w,h,t/.53,ACCENT[who])
    elif t<.84:_impact(c,w,h,(t-.53)/.31,ACCENT[who])
    else:_finish(c,w,h,(t-.84)/(SECS[who]-.84),who)
    return '',c.finish()
