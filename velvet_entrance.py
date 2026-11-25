"""Native-cell entrance: a locked blue prison unfolds into the Velvet Room."""
from math import cos, pi, sin
from wide_canvas import Canvas

DURATION = 2.85


def _ease(t):
    t=min(1.,max(0.,t))
    return t*t*(3-2*t)


def _path(c, points, ink, limit=None):
    for (x,y),(xx,yy) in zip(points,points[1:]):
        c.line(x,y,xx,yy,ink,limit)


def _arch(c,x,y,rx,ry,foot,ink):
    crown=[(x+rx*cos(j*pi/14), y-ry*sin(j*pi/14)) for j in range(15)]
    _path(c,crown,ink)
    for edge in (x-rx,x+rx):
        c.line(edge,y,edge,foot,ink,'|')


def _room(c,t,open_,advance):
    w,h=c.w,c.h
    mid=w*.5
    floor=round(h*(.62+.045*advance))
    spring=h*(.35+.025*advance)
    # Farthest arch and barred blue alcove. The nearer vault is formed by
    # the corridor's ribs, with floor seams receding to the alcove threshold.
    rx=w*(.15+.035*advance)
    for d in (2,0):
        _arch(c,mid,spring,rx+d,max(1,h*.14+d*.17),floor,'navy' if d else 'slate')
    for i in range(-4,5):
        x=mid+rx*i/5
        y=spring-h*.14*(1-(i/5)**2)**.5
        c.line(x,y,x,floor-.5,'navy','|')
        c.put(round(x),floor,'+','slate')
    for side in (-1,1):
        for j in range(3):
            x=mid+side*w*(.23+j*.125)
            top=h*(.30-j*.115)
            base=floor+h*(.031+j*.087)
            c.line(x,top,x,base,'navy','|')
            c.line(x+side,top-1,x+side,base,'slate','|')
            c.line(x,top,mid+side*rx,spring,'navy')
            c.line(x,base,mid+side*rx,floor,'slate')
            for k in range(1,4):
                z=x+side*(j+2)*k
                zz=z-side*(j+1)*.66
                c.line(z,top+(k%2),zz,base-k*.24,'navy','|')
            if j<2:
                lamp_x=round(x+side*2)
                lamp_y=round(top+h*.16)
                c.put(lamp_x-1,lamp_y,('.','|||','-'),'teal' if open_>.6 else 'navy')
    for i in range(-4,5):
        x=w*(.5+i*.14)
        c.line(mid+rx*.27*i,floor,x,h-1,'navy')
    for y in range(floor+1,h):
        z=(y-floor)/max(1,h-floor)
        if (y-floor) not in {1,3,6,10,15,21}:
            continue
        stride=max(4,round(w*(.08+.032*z)))
        for x in range(-stride+(y*13)%stride,w,stride):
            c.put(x,y,'-.' if y%2 else '---','slate' if z>.4 else 'navy')
    # A soft rotating beam descends from the overhead vault.
    tick=round(t*13)
    sweep = sin(t*2.3-1.3)
    for i in range(max(16,w//4)):
        y=(i*17+tick*(i%3+1))%max(2,floor+1)
        x=round(mid+sweep*(i//9+1)+((i*23)%17-8)*(1+y/h))
        if (i+tick)%5<3:
            c.put(x,y,'.' if i%4 else '+','teal' if open_>.45 and i%4==0 else 'navy')
    if open_>.26:
        _table(c,t,floor,advance,open_)


def _table(c,t,floor,advance,open_):
    w,h=c.w,c.h; mid=round(w*.5)
    a=max(6,round(w*(.145+.075*advance)))
    depth=max(2,round(h*(.08+.025*advance)))
    rear=floor-1
    lip=rear+depth
    hem=min(h-3,lip+max(2,round(h*.16)))
    rim='slate' if open_<.65 else 'teal'
    for row in range(rear,lip+1):
        d=(row-rear)/depth
        span=round(a*(.72+d*.28))
        x=mid-span
        pattern='.' if row%2 else ':'
        ch='=' if row==lip else '-' if row==rear else None
        if ch:
            c.put(x,row,ch*(span*2+1),rim,opaque=True)
        else:
            c.put(x,row,pattern+' '*max(0,span*2-1)+pattern,'teal',opaque=True)
            for k in range(-span+4,span,6):
                c.put(mid+k,row,'.','navy')
    for y in range(lip+1,hem+1):
        span=a+round((y-lip)*.43)
        chars=[' ']*(span*2+1)
        chars[0],chars[-1]=('/','\\') if y%2 else ('|','|')
        for i in range(3,len(chars)-2,4 if advance<.45 else 5):
            chars[i]='.' if (i+y)%4==0 else ':'
        c.put(mid-span,y,''.join(chars),'navy',opaque=True)
        for x in (mid-span,mid+span):
            c.put(x,y,chars[0] if x<mid else chars[-1],rim)
        if y==hem:
            c.put(mid-span,y,('~_'*(span+1))[:span*2+1],'slate')
    # Page seams, a blue bookmark, and two flanking pools of candlelight.
    page=max(3,w//19)
    book_y=rear-1
    c.put(mid-page-1,book_y,'/_'+'-'*(page-2)+'\\'+'/'+ '-'*(page-2)+'_\\',rim,opaque=True)
    c.put(mid-page-1,book_y+1,'\\'+'_'*(page-1)+'_/\\_'+'_'*(page-1)+'/', 'white' if open_>.85 else 'slate',opaque=True)
    c.put(mid,book_y+2,'|','teal')
    for side in (-1,1):
        x=round(mid+side*a*.56)
        c.put(x-2,rear-3,(" .'." if int(t*11+side)%2 else " .*.",'  | ',' _T_ '),
              'teal' if open_<.82 else 'cyan')
    if open_>.8:
        for x in range(mid-a,mid+a+1,4):
            p=(x+round(t*8))%9
            if p<3:
                c.put(x+((p+1)%3)-1,lip+1,':','teal')


def _pillars(c,t,open_,camera):
    w,h=c.w,c.h
    cx=w*.5
    left=w*(.17-.10*camera-.06*open_)
    right=w-1-left
    top=h*(.23-.08*camera)
    base=h*(.83+.08*camera)
    rx=(right-left)*.5
    # Curved transom and foot track remain fixed while each leaf moves.
    for off in (2,0):
        _arch(c,cx,top,rx+off,h*(.13+off*.007),base+.85,'navy' if off else 'slate')
    for x,sign in ((left,-1),(right,1)):
        c.line(x,top,x,base,'slate','|')
        c.line(x+sign*2,top+1,x+sign*2,base+1,'navy','|')
        c.put(round(x)-2,round(top),'[::]','teal')
        c.put(round(x)-2,round(base)+1,'[_]','navy')
    c.line(left,base+1,right,base+1,'navy','_')
    return left,right,top,base


def _gate(c,t,left,right,top,base,open_):
    w,h=c.w,c.h
    cx=(left+right)*.5
    a=pi*.5*open_
    gate_rx=(right-left)*.5
    energy=.44<t<1.17
    beam=left+((t-.44)/.73)*(right-left)
    for hinge,sign in ((left,1),(right,-1)):
        # Doors hinge outward from the posts and foreshorten toward the
        # edge; the inside end drifts farther from the viewer in projection.
        thickness=max(5,round(w*.11))
        samples=max(7,thickness)
        def xy(u,v):
            z=sin(a)*u
            x=hinge+sign*gate_rx*cos(a)*u
            y=top+h*(.021*u+.095*z)+(base-top-h*.18*z)*v
            return x,y
        border=[xy(0,0),xy(1,0),xy(1,1),xy(0,1),xy(0,0)]
        _path(c,border,'slate')
        for height in (.06,.27,.70,.97):
            _path(c,[xy(j/12,height) for j in range(13)],'navy','=')
        for k in range(samples+1):
            u=k/samples
            x,y=xy(u,0)
            xx,yy=xy(u,1)
            near_light=energy and abs(x-beam)<max(2,w*.05)
            ink='cyan' if near_light else 'slate' if k%2 else 'navy'
            c.line(x,y,xx,yy,ink,'|' if k%3 else ':')
            if k%2 or near_light:
                cap_x,cap_y=xy(u,.265)
                c.put(round(cap_x),round(cap_y),'+' if near_light else ':',ink)
        # Each plate carries a keyed half of the same round center seal.
        x,y=xy(.97,.53)
        fx,fy=round(x),round(y)
        if open_<.19:
            if sign==1:
                c.put(fx-2,fy-1,('/-', '|<', '\\_'),'teal' if t>.48 else 'slate')
            else:
                c.put(fx+1,fy-1,('-\\','>|','_/'),'teal' if t>.48 else 'slate')
        elif .19<open_<.85:
            c.put(fx,fy,'.' if sign==1 else '+','teal')
    if open_<.14:
        x,y=round(cx),round(top+(base-top)*.53+h*.021)
        glow=.52<t<1.04
        c.put(x-1,y-1,('.-.','(*)','\\_/'),'white' if glow else 'teal',opaque=True)
        if glow:
            pulse=max(2,round((t-.50)*w*.15))
            for x,punc in ((x-pulse,'<'),(x+pulse,'>')):
                c.put(x,y,punc,'cyan')
    elif 1.12<t<1.65:
        f=(t-1.12)/.53
        for i in range(14):
            x=round(cx+(i%7-3)*f*w*.052)
            y=round(h*.52+(i//7*2-1)*(i%7+1)*f*.59)
            c.put(x,y,'.' if i%3 else '+','teal')


def render(t,w,h):
    """Return viewport-sized runs of (ASCII text, scene pigment)."""
    c=Canvas(w,h)
    if not w or not h:
        return c.finish()
    t=max(0.,min(DURATION,float(t)))
    approach=_ease(t/.65)
    opening=_ease((t-.91)/1.14)
    advance=_ease((t-1.62)/1.16)
    _room(c,t,opening,advance)
    gates=_pillars(c,t,opening,approach)
    _gate(c,t,*gates,opening)
    return c.finish()
