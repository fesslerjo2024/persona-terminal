"""Native-size rooftop and chapel choreography; no caption or matte layer.

Actual-game reference: https://www.youtube.com/watch?v=F6BYdZ34KOM and
https://www.youtube.com/watch?v=3XaOOKnntOw . Images are entirely original.
"""
from bisect import bisect_right
from math import cos, pi, sin, tau

from wide_canvas import Canvas

MASK = 'TWO SIDES OF THE MASK'
WALTZ = 'THE LAST WALTZ'
DURATIONS = {MASK:7.30, WALTZ:7.98}
_MASK = ((.86,'storm'),(1.83,'berserk'),(2.95,'assault'),(3.80,'knife'),
         (5.35,'flurry'),(6.27,'shot'),(7.30,'departure'))
_WALTZ = ((.95,'entry'),(2.55,'swing'),(3.40,'flight'),(4.29,'reach'),
          (5.83,'duet'),(6.49,'crossing'),(7.98,'dip'))

# Figure construction re-rasterizes independent articulated strokes. Limbs
# use different angles, native cell counts, and foreshortening per pose.
# Hand and foot vectors, measured at the shoulder and waist joints.
_POSE = {
    'ready':((-1.7,1.6),(1.7,1.0),(-.83,2.0),(1.16,2.05)),
    'run':((-1.3,1.4),(2.25,.83),(-1.35,1.9),(1.7,.95)),
    'leap':((-1.55,.12),(1.25,-2.12),(-1.8,1.35),(1.2,.73)),
    'drop':((-1.68,-.55),(1.77,-1.08),(-.36,2.0),(.77,1.86)),
    'slash':((-1.2,1.16),(2.54,.78),(-1.54,1.8),(1.34,1.95)),
    'high':((-1.50,.14),(2.36,-1.05),(-1.68,1.56),(1.35,1.37)),
    'low':((-.79,1.0),(2.45,1.55),(-1.44,1.13),(1.17,1.64)),
    'aim':((-1,.95),(2.20,.03),(-.89,1.96),(1.12,2.0)),
    'rage':((-1.91,-.94),(2.09,-.78),(-1.55,1.96),(1.53,1.91)),
    'reach':((-1.42,.86),(2.25,-.30),(-.53,2.0),(1.4,1.47)),
    'spin':((-2.38,-.13),(2.30,-.34),(-.41,2.07),(1.94,1.35)),
    'reel':((-1.57,-.64),(1.75,.21),(-1.04,2.01),(1.52,1.01)),
    'hold':((-1.40,1.04),(2.35,.34),(-1.44,1.52),(1.36,1.94)),
}
_COSTUME = {
    'joker':('wine','red','white','slate'),
    'crow':('navy','red','amber','wine'),
    'violet':('violet','rose','white','wine'),
    'echo':('teal','white','cyan','navy'),
    'shadow':('slate','ochre','gold','wine'),
}


def _cut(t,spec):
    i = min(len(spec)-1,bisect_right([end for end,_ in spec],t))
    start = 0 if i == 0 else spec[i-1][0]
    return i,(t-start)/(spec[i][0]-start),spec[i][1]


def _xy(w,h,x,y):
    return round((w-1)*x),round((h-1)*y)


def _poly(c, pts, bright, shade=None, phase=0, material='cloth'):
    sides = tuple(zip(pts,pts[1:]+pts[:1]))
    texture = (':', '.', ';') if material=='cloth' else ('.',':','=')
    for y in range(min(y for x,y in pts),max(y for x,y in pts)):
        xs=sorted(x0+(y-y0)*(x1-x0)/(y1-y0)
                  for (x0,y0),(x1,y1) in sides if min(y0,y1)<=y<max(y0,y1))
        for a,b in zip(xs[::2],xs[1::2]):
            if a==b:continue
            xi,xf=round(a),round(b)
            c.put(xi,y,''.join(texture[(x+y+phase)%3] if (x+y*3+phase)%5 in (0,1)
                               else ' ' for x in range(xi,xf+1)),shade or bright,True)
    for (x0,y0),(x1,y1) in sides:
        c.line(x0,y0,x1,y1,bright)


def _body(c,kind,x,y,scale,pose,face=1,lean=0,tick=0,sword=False):
    """x,y is the shoulder. Head, torso, fabric, limbs and held prop are separate."""
    cloth,accent,mask,shade = _COSTUME[kind]
    wx,hy = scale,scale*.68
    def P(u,v):
        return x+round((u*face+v*lean)*wx),y+round(v*hy)
    thick = kind=='shadow'
    (a0,a1),(b0,b1),(c0,c1),(d0,d1)=_POSE[pose]
    neck=P(0,-.4); waist=P(.08,2.7)
    left,right=P(-1.1,.12),P(1.16,.12)
    width=1.0 if thick else .71
    points=[left,neck,right,P(width,2.76),P(-width,2.76)]
    for hip,k0,k1,knee in ((-.43,c0,c1,-.3),(.48,d0,d1,.25)):
        end=P(k0,2.75+k1); k=P((k0+hip)/2+knee,3.55+max(0,k1-1.4)*.34)
        c.line(*P(hip,2.64),*k,cloth); c.line(*k,*end,accent if thick else cloth)
        c.line(*end,*P(k0+(.44 if k0>0 else -.45),2.75+k1),mask,'_')
    if kind=='joker':
        flow=sin(tick*.8)*.46
        _poly(c,[P(-.79,1.1),P(.79,2.0),P(.63+flow,4.14),
                  P(-.02,3.49),P(-1.85+flow,4.30),P(-1.26,2.1)],cloth,shade,tick//2)
    if kind in ('violet','echo') and pose in ('spin','slash','leap','hold'):
        c.line(*P(-.6,2.1),*P(-2.15+sin(tick*.65)*.4,3.12),accent,'~')
    _poly(c,points,accent,shade,tick//3,'metal' if kind in ('crow','shadow') else 'cloth')
    c.line(*P(-.52,.4),*waist,mask)
    c.line(*P(.53,.4),*waist,accent)
    if thick or kind=='crow':
        c.put(*P(-.60,1.3), '[#]' if wx>=2.3 else '#',accent)
    hand = P(b0,b1)
    for start,end,side in ((left,P(a0,a1),-1),(right,hand,1)):
        el=P((a0 if side<0 else b0)*.75,.66+(a1 if side<0 else b1)*.43)
        c.line(*start,*el,cloth);c.line(*el,*end,accent)
        c.put(*end,'o' if kind in ('violet','echo') else '+',mask)
    head= P(0,-1.56)
    if wx<2.42:
        headgear={
            'joker':(' .~^~. ','<v===v>',r' \_-/ '),
            'crow':(' /^ ^\\ ','[##\\]> ',' \\###/ '),
            'violet':('  _<>. ',' (v=v) ','  \\_/  '),
            'echo':(' .~^~. ','( . . )','  \\_/  '),
            'shadow':('^--,--^','(o)(o) ','\\_><>_/'),
        }[kind]
    else:
        headgear={
            'joker':('   .~^^~.   ','  /_////_\\  ',' <v==--==v> ','  \\__--__/  '),
            'crow':('   /^--^\\   ',' _/[##]##\\_ ','<#\\######]> ','  \\###_##/  '),
            'violet':('    _<>~.  ','  ./(___)  ',' ( vv=v )> ','  \\__/_/~~ '),
            'echo':('   .~~^~.  ','  /_~ ~_\\  ',' ( .   . ) ','  \\_---_/  '),
            'shadow':('^-.      .-^','  (o)__(o)  ',' / ##<>## \\ ',' \\_#><>#_/ '),
        }[kind]
    for j,row in enumerate(headgear):
        if face<0:row=row[::-1].translate(str.maketrans('/\\<>','\\/><'))
        left_pad=len(row)-len(row.lstrip())
        col=head[0]-len(row)//2+left_pad
        c.put(col,head[1]+j-len(headgear)//2,row.strip(),
              cloth if j==0 else mask if j==len(headgear)-2 else accent,True)
    if sword:
        length=3.1 if kind in ('crow','violet','echo') else 1.15
        tip=P(b0+length,b1+(-1.35 if pose=='high' else .05 if pose=='low' else -.38))
        c.line(*hand,*tip,'white' if kind=='echo' else mask)
        c.put(*tip,'>' if face==1 else '<',accent)
    elif pose=='aim':
        tip=P(b0+1.18,b1)
        c.line(*hand,*tip,'slate','=')
    return hand


def _arc(c,x,y,rx,ry,phase,length,ink,density=.75,glyph='.'):
    n=max(9,round((rx+ry)*density))
    for i in range(n+1):
        a=phase+length*i/n
        c.put(x+round(rx*cos(a)),y+round(ry*sin(a)),
              '+' if (i%11==4 and glyph=='.') else glyph,ink)


def _firework(c,w,h,x,y,f,tick,colors,slash=False):
    # Nested expanding shock contours, and long pieces that fragment into dots.
    span=max(7,w*.23*(.13+f))
    for i in range(26):
        a=i*tau/26
        dx=round(cos(a)*span*(.64+(i%5)*.10))
        dy=round(sin(a)*span*(h/w+.11))
        col=colors[(i+tick//3)%len(colors)]
        c.line(x+round(dx*.62),y+round(dy*.62),x+dx,y+dy,col,'.' if f>.56 else None)
        c.put(x+dx,y+dy,('*','+','.')[(i+tick)%3],col)
    if f<.55:
        _arc(c,x,y,round(span*.70),max(1,round(span*h/w*.37)),0,tau,colors[0],1.5)
    if f<.28:
        c.put(x-3,y-1,('  \\|/  ',' --*-- ','  /|\\  '),'white')
    if slash:
        c.line(x-round(span),y+round(h*.19),x+round(span),y-round(h*.21),colors[0])


def _buildings(c,w,h,t):
    # Front parapet, middle-distance gridded buildings, far city towers and
    # moving rain. The design occupies the viewport, including the basin below.
    horizon=round(h*.60)
    unit=max(5,round(w*.083))
    for i,x in enumerate(range(-unit,w,unit)):
        off=round(sin(i*2.39+t*.8)*unit*.19)
        ww=unit-2+(i%3)
        top=max(1,round(h*(.09+(i*17%49)/100)))
        base=min(horizon,round(h*(.46+(i%3)*.083)))
        x+=off
        if base<=top:continue
        col=('navy','slate','wine')[i%3]
        c.line(x,top,x+ww,top,col,'_')
        if i%4==0:
            c.line(x+ww//2,max(0,top-3),x+ww//2,top,col,'|')
            c.put(x+ww//2,max(0,top-3),'*','red')
        for j in range(top+1,base):
            interior=''.join(':' if (j*5+k*7+i)%17 in (1,2,7) else ' '
                             for k in range(ww-1))
            c.put(x,j,'|'+interior+'|',col,True)
            if i%5==0 and j%4==0:
                c.put(x+ww//2,j,'.','amber')
    ticks=round(t*22)
    for k in range(w*h//28):
        y=(k*13+ticks)%h
        x=(k*37+8*(k//17)-ticks-y//2)%w
        c.put(x,y,'/' if k%3 else '.',('teal','navy','slate')[k%3])
    for y in (round(h*.68),round(h*.88),h-1):
        c.put(0,y,('=.' if y==round(h*.88) else '_ ')*(w//2+1),'slate')
    for i in range(9):
        sx=round(w*i/8)
        c.line(round(w*.5)+(sx-round(w*.5))//5,horizon,sx,h-1,'wine','.')
    for x in (round(w*.10),round(w*.34),round(w*.77),round(w*.92)):
        y=round(h*.77); g=max(3,round(w*.053)); rise=max(2,h//15)
        _poly(c,[(x-g,y),(x-g+2,y-rise),(x+g,y-rise),(x+g+2,y),(x+g-1,y+1)],
              'slate','navy',ticks//4,'metal')
        c.put(x-g+2,y,'#:'*(g-1),'navy')


def _chapel(c,w,h,t):
    # Gothic vault ribs run to the full screen corners, nested window tracery,
    # gold sconces, grazing lights, candle flames, and an aisle in perspective.
    top=round(h*.07); floor=round(h*.69); mid=w//2
    for j, rel in enumerate((.12,.32,.50,.68,.88)):
        x=round(w*rel); rad=max(4,round(w*(.073 if j==2 else .067)))
        start=top+(0 if j==2 else h//9)
        cap=start+max(3,h//9)
        base=floor-h//10
        c.line(x,start,x-rad,cap,'slate','/')
        c.line(x,start,x+rad,cap,'slate','\\')
        c.line(x-rad,cap,x-rad,base,'slate','|')
        c.line(x+rad,cap,x+rad,base,'slate','|')
        c.line(x-rad,base,x+rad,base,'ochre','_')
        for k in range(3):
            pane=x+round((k-1)*rad*.62)
            col=('rose','teal','violet','amber')[(j+k)%4]
            c.line(pane,cap-h//12+(k%2),pane,base-1,col,':')
            _arc(c,pane,(cap+base)//2,max(1,rad//5),max(1,h//12),0,tau,col,2.0)
        for k in (-1,1):
            c.line(x+k*rad,cap,x+k*(rad+max(1,w//45)),floor,'ochre','|')
        c.line(x,start,mid if j in (1,3) else (0 if j<2 else w-1),0,'wine')
    for j in range(8):
        f=(j/8+t*.25)%1
        y=floor+round(f*f*(h-floor-1))
        m=round((1-f)*w*.15)
        c.put(m,y,('_. ' if j%2 else '. =')*((w-2*m)//3),'navy')
    for i in range(-4,5):
        c.line(mid+i*max(2,w//23),floor,mid+i*round(w*.115),h-1,'ochre','.')
    for x in (w//18,w//5,w*4//5,w*17//18):
        y=floor+round(h*.07)
        c.line(x,y-3,x,y,'amber','|')
        c.put(x,y-4,('*','o','+')[(x+round(t*13))%3],'gold')
    for i in range(w*h//48):
        drift=(t*.28+i*.177)%1
        y=round(h*drift)
        x=(i*47+round(drift*w*.15))%w
        c.put(x,y,('.','*',',')[i%3],('rose','gold','teal','white')[i%4])


def _roof_scene(c,w,h,t,shot,f):
    _buildings(c,w,h,t)
    k = max(1.50,min(w/27,h/12))
    tick=round(t*15)
    def body(kind,x,y,pose='ready',face=1,lean=0,sword=False):
        return _body(c,kind,*_xy(w,h,x,y),k,pose,face,lean,tick,sword)
    if shot==0:
        # Crow stalks across the lower vents as Joker hops along the parapet.
        body('shadow',.84-.08*f,.53,'ready',-1)
        body('joker',.16+.12*f,.34+.05*f,'leap' if f<.65 else 'ready')
        body('crow',.15+.23*f,.54+.022*sin(tick*pi*.78),'run',1,-.19)
        if .24<f<.53:
            a=_xy(w,h,.83,0); b=_xy(w,h,.72,.17); d=_xy(w,h,.76,.17)
            c.line(*a,*b,'amber');c.line(*b,*d,'white','-')
            c.line(*d,*_xy(w,h,.63,.35),'amber')
    elif shot==1:
        body('joker',.28,.40,'ready')
        body('shadow',.76,.53,'reel' if f>.7 else 'ready',-1)
        x,y=_xy(w,h,.40+.035*f,.51)
        for j,col in enumerate(('wine','red','amber')):
            _arc(c,x,y,round(w*(.07+j*.014+f*.033)),
                 round(h*(.12+j*.025)),f*5+j,pi*1.6,col)
        body('crow',.40+.035*f,.54-.032*sin(f*pi),'rage',1,0,True)
    elif shot==2:
        jx=.28+.34*f
        jy=.40-.27*sin(pi*f*.83)
        c.line(*_xy(w,h,.65,.02),*_xy(w,h,jx+.04,jy-.1),'cyan','.')
        body('shadow',.76,.54,'ready',-1)
        body('crow',.44+.23*f,.58+.024*sin(tick*2.4),'run',1,-.18,True)
        body('joker',jx,jy,'leap',1,-.24)
    elif shot==3:
        jx=.62+.12*f; jy=.27+.23*f*f
        body('shadow',.77+.07*f,.54+.06*f,'reel',-1)
        body('crow',.65+.04*f,.59,'low',1,-.16,True)
        body('joker',jx,jy,'drop' if f<.53 else 'slash',1,-.18,True)
        if f>.41:
            fx,fy=_xy(w,h,jx+.054,jy+.07)
            _firework(c,w,h,fx,fy,(f-.41)*.93,tick,('red','gold','amber'),True)
    elif shot==4:
        body('joker',.54-.25*f,.50,'ready',-1)
        body('shadow',.82+.052*sin(f*tau*3),.54+.025*cos(f*tau*3),'reel',-1)
        x=.66+.078*sin(f*tau*2)
        hi=tick%4<2
        body('crow',x,.46 if hi else .57,'high' if hi else 'low',1,-.23,True)
        fx,fy=_xy(w,h,x+.16,.44 if hi else .62)
        _firework(c,w,h,fx,fy,.26+.48*((f*4)%1),tick,('wine','red','amber'),True)
    elif shot==5:
        body('crow',.55-.24*f,.58,'run',-1)
        body('shadow',.83+.07*f,.55+.12*f,'reel',-1)
        hand=body('joker',.29+.04*f,.52,'aim')
        if .32 < f < .67:
            fx,fy=_xy(w,h,.85,.56)
            span=(f-.32)/.35
            c.line(*hand,*_xy(w,h,.45+.44*min(1,span*2),.53),'gold','-')
            _firework(c,w,h,fx,fy,span,tick,('gold','amber','red'))
    else:
        body('crow',.30-.40*f,.58,'run',-1)
        body('joker',.34-.18*f,.52,'ready' if f<.25 else 'run',-1)
        if f<.30:
            body('shadow',.89+.14*f,.65+.07*f,'reel',-1)
        for i in range(w//3):
            d=(i*17%31)/31
            if f<(d+.30):
                x,y=_xy(w,h,.81+.15*d+.11*f,.51+.31*d+.07*f)
                c.put(x,y,'.,*'[i%3],'amber' if f<.2 else 'slate')


def _waltz_scene(c,w,h,t,shot,f):
    _chapel(c,w,h,t)
    k=max(1.45,min(w/27,h/12))
    tick=round(t*17)
    def body(kind,x,y,pose='ready',face=1,lean=0,sword=False):
        return _body(c,kind,*_xy(w,h,x,y),k,pose,face,lean,tick,sword)
    if shot==0:
        body('shadow',.85,.52,'ready',-1)
        body('joker',.08+.18*f,.52-.031*sin(f*pi),'run',1,-.22)
        body('violet',.20+.18*f,.50+.024*sin(tick*2),'run',1,-.21)
        left,top=_xy(w,h,.01,.87); right,_=_xy(w,h,.31,.98)
        for i in range(4):
            c.line(left+i*max(2,w//29),top+i,right,top+i,'ochre','_')
    elif shot==1:
        jx=.26+.43*f; jy=.49+.11*sin(pi*f)-.29*f
        body('shadow',.82,.50+.08*f,'reel' if f>.49 else 'ready',-1)
        c.line(*_xy(w,h,.59,.0),*_xy(w,h,jx+.04,jy-.17),'white','.')
        _arc(c,*_xy(w,h,.50,.24),round(w*.33),round(h*.34),.37,pi*.70,'teal',1.08)
        hand=body('joker',jx,jy,'leap',1,-.29)
        body('violet',jx-.082,jy+.14,'hold',1,-.39)
        if .35<f<.82 and tick%3:
            fx,fy=_xy(w,h,.81,.55)
            c.line(*hand,fx,fy,'amber','.')
            _firework(c,w,h,fx,fy,.21,tick,('gold','amber','rose'))
    elif shot==2:
        x=.62-.13*f; y=.34+.12*f-.11*sin(pi*f)
        body('shadow',.80,.57,'reel',-1)
        c.line(*_xy(w,h,.60,0),*_xy(w,h,.73+.25*f,.09),'slate','.')
        body('joker',.70+.30*f,.20-.13*f,'leap',1,-.31)
        body('violet',x,y,'spin',-1,.39*sin(f*pi))
        _arc(c,*_xy(w,h,x,y+.08),round(w*.12),round(h*.18),f*4,pi*1.42,'rose')
    elif shot==3:
        vx=.48+.04*f; vy=.41+.02*f
        ex=.72-.08*f; ey=.26+.13*f
        body('shadow',.86,.59,'reel',-1)
        p=body('violet',vx,vy,'reach',1,-.18)
        q=body('echo',ex,ey,'reach',-1,.13)
        if f>.58:
            x,y=(p[0]+q[0])//2,(p[1]+q[1])//2
            c.line(*p,*q,'white')
            _arc(c,x,y,round(w*.06*f),max(2,round(h*.06)),f*4,tau,'rose')
            c.put(x,y,'+','gold')
    elif shot==4:
        a=f*tau; dx=.14*cos(a);dy=.13*sin(a)
        body('shadow',.84,.57,'ready',-1)
        _arc(c,*_xy(w,h,.56,.52),round(w*.29),round(h*.23),a,pi*1.57,'rose',1.2)
        _arc(c,*_xy(w,h,.56,.51),round(w*.24),round(h*.18),a+pi,pi*1.06,'teal')
        figures=[('violet',.54+dx,.39+dy),('echo',.54-dx,.39-dy)]
        for who,x,y in sorted(figures,key=lambda row:row[2]):
            body(who,x,y,'spin' if f<.75 else 'slash',
                 1 if x<.55 or f>=.75 else -1,sin(a)*.16,f>=.75)
    elif shot==5:
        body('shadow',.83+.09*f,.50+.08*f,'reel',-1)
        body('violet',.55+.21*f,.54,'slash',1,-.19,True)
        body('echo',.60+.21*f,.29,'high',1,-.23,True)
        if f>.22:
            x,y=_xy(w,h,.83,.47)
            _firework(c,w,h,x,y,(f-.22)*1.22,tick,('rose','gold','white'),True)
            c.line(*_xy(w,h,.53,.12),*_xy(w,h,1,.82),'cyan')
    else:
        # Two moving body joints, not a static victory plate. Violet is
        # caught, dips in a sweeping arc, then rises into the last half-turn.
        g=min(1,f/.26)
        base=.34+.16*g
        dt=sin(pi*max(0,(f-.19)/.81))
        p=body('joker',base-.038*dt,.52+.040*dt,'hold',1,-.09-.21*dt)
        q=body('violet',.77-.17*g+.02*dt,.31+.20*g+.11*dt,
               'reach' if f<.3 else 'spin',-1,-.42*dt)
        if f>.20:
            c.line(*p,*q,'rose')
        _arc(c,*_xy(w,h,.51,.62),round(w*.24),round(h*.18),f*3,pi*1.26,'teal')
        for i in range(w//4):
            drift=(f*.65+i*.11)%1
            x,y=_xy(w,h,.08+((i*.157+drift*.09)%.86),.19+.74*drift)
            c.put(x,y,'.*,'[i%3],('rose','amber','violet')[i%3])


def render(title,t,w,h):
    """Draw directly into the screen dimensions; runs contain only ASCII art."""
    spec,draw = (_MASK,_roof_scene) if title==MASK else (_WALTZ,_waltz_scene)
    t=max(0,min(DURATIONS[title],t))
    i,f,beat=_cut(t,spec)
    c=Canvas(w,h)
    draw(c,w,h,t,i,f)
    return beat,c.finish()
