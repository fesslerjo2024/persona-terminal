"""A native Persona 3 title scene. The controller supplies save-based choices."""
from functools import lru_cache
from math import cos, pi, sin
from wide_canvas import Canvas
from reel_palette import IDS

DURATION = 3.18
TITLE = 'Persona 3 Terminal'
MENU = (('Continue', False), ('New Game', True), ('Back to Selector', True))
MENU_DEFAULT = 1


def menu(continue_ready):
    return ((MENU[0][0],continue_ready),*MENU[1:])


def _pace(t):
    t=min(1.,max(0.,t))
    return t*t*(3-2*t)


def _arc(c,x,y,rx,ry,ink,start=0.,stop=2*pi,steps=40):
    prev=(x+rx*cos(start),y+ry*sin(start))
    for j in range(1,steps+1):
        a=start+(stop-start)*j/steps
        end=(x+rx*cos(a),y+ry*sin(a))
        c.line(*prev,*end,ink)
        prev=end


def _sky(c,t,turn):
    w,h=c.w,c.h
    ground=round(h*.73)
    for k in range(max(14,w//3)):
        x=(k*17+k*k*7+round(t*2))%w
        y=(k*11+k*k//6)%max(1,ground-2)
        c.put(x,y,'+' if (k+round(t*7))%9==0 else '.','slate' if k%4 else 'teal')
    for side in (0,1):
        for i in range(-1,w//6+3):
            x=i*6+(2 if side else 0)
            dx=3+(i*i*11+side*3)%9
            y=ground-2-(i*23+i*i)%max(2,h//(6 if side else 8))
            ink='navy' if side else 'slate'
            c.line(x,y,x+dx,y,ink,'_')
            for xx in (x,x+dx):
                c.line(xx,y,xx,ground,ink,'|')
            if side and (i+1)%3:
                for yy in range(y+2,ground,2):
                    c.put(x+2,yy,':','navy')
    c.line(0,ground,w-1,ground,'navy','_')
    for y in range(ground+1,h):
        d=(y-ground)/max(1,h-ground)
        stride=max(7,round(w*(.07+.16*d)))
        shifts=round(t*(8+4*d))
        for i in range(-stride+(y*7+shifts)%stride,w,stride):
            key=(i*11+y*13+round(t*9))%11
            bright=(turn>.42 and abs(i-w*.72) < w*(.28-.12*d) and key<6)
            c.put(i,y,'-.' if key%3 else '_----', 'teal' if bright else 'slate' if key<3 else 'navy')
    return ground


def _moon(c,t,turn):
    w,h=c.w,c.h
    x=w*(.685+.043*turn); y=h*(.32-.092*turn)
    rx=w*(.095+.031*turn); ry=h*(.18+.026*turn)
    if turn<.06:
        return
    _arc(c,x,y,rx,ry,'forest',.08*pi,1.92*pi)
    if turn>.26:
        _arc(c,x-1,y,rx-1,ry,'teal',.72*pi,1.62*pi,steps=14)
    for k in range(11):
        dy=(k-5)*ry/5
        if abs(dy)<ry:
            span=rx*(1-(dy/ry)**2)**.5
            left=x-span*.86
            length=round(span*(.48+(k%4)*.28))
            c.put(round(left),round(y+dy),('.-'*(length+1))[:length],
                  'forest' if k%3 else 'teal')
    if .21<turn<.75:
        for j in range(7):
            a=j*pi/3+2*t
            c.put(round(x+rx*1.29*cos(a)),round(y+ry*1.31*sin(a)),'.','teal')


def _tower(c,t,turn,bottom):
    if turn<.035:
        return
    w,h=c.w,c.h
    x=w*(.76+.054*turn)
    top=bottom-min(bottom-1,round(turn*h*.68))
    ht=max(1,bottom-top)
    bx=round(w*.091)
    # The tower leans in alternating steps as it rises. Its face cuts into
    # the moon, so the widening Dark Hour light has a real silhouette.
    for y in range(top,bottom+1):
        z=(y-top)/ht
        center=round(x+bx*(.48*sin(pi*(z+.16))*z-.24*z))
        a=max(1,round(bx*(.17+.85*z)+sin(z*19)*1.15))
        c.put(center-a,y,' '*(2*a+1),'navy',opaque=True)
        left,right=center-a,center+a
        edge='/' if (y-top)%4==1 else '|'
        c.put(left,y,edge,'slate')
        c.put(right,y,'\\' if edge=='/' else '|','teal' if (y-top)%5==1 else 'navy')
        if y==bottom:
            c.put(left-1,y,'='*(right-left+3),'navy')
        elif round(h*.10)<=y-top and (y-top)%max(2,h//13)==1:
            if right-left>6:
                for q in (-1,0,1):
                    lamp=':' if (y+q+round(t*8))%5 else '.'
                    c.put(center+q*max(2,a//2),y,lamp,'teal' if q==0 else 'slate')
        elif y>top and (y-top)%7==0:
            c.put(left-1,y,'--','navy')
            c.put(right,y,'--','teal')
    c.put(round(x)-2,top-2,(" .", " |", "/_\\"),'cyan')
    for k in range(3):
        a=round(x)+k*(1+k//2)
        y=bottom+2+k
        c.put(a-3,y, '._..' if k%2 else '-._-' ,'teal')


def _bezel(c,x,y,rx,ry,start,stop,ink):
    """Follow the face's tangent with stable marks, even at a small radius."""
    n=max(4,round(abs(stop-start)*max(rx,ry)*2))
    for j in range(n+1):
        a=start+(stop-start)*j/n
        vx=-rx*sin(a); vy=ry*cos(a)
        ch='-' if abs(vy)<abs(vx)*.43 else '|' if abs(vx)<abs(vy)*1.28 else '/' if vx*vy<0 else '\\'
        c.put(round(x+rx*cos(a)),round(y+ry*sin(a)),ch,ink)


def _clock(c,t,settle):
    w,h=c.w,c.h
    cx=w*(.365-.083*settle)
    cy=h*(.405-.020*settle)
    rx=max(8.,w*(.205-.029*settle));ry=max(4.,h*(.310-.024*settle))
    x,y=round(cx),round(cy)
    strike=.94<=t<1.15
    lit=settle<.90
    if lit:
        # A solid face keeps skyline noise out of the moving hand silhouettes.
        # At the handoff the dormant clock stays translucent behind the menu.
        for row in range(round(cy-ry+.5),round(cy+ry-.5)+1):
            rise=(row-cy)/ry
            if abs(rise)<1:
                span=rx*(1-rise*rise)**.5-1.3
                c.put(round(cx-span),row,' '*max(0,round(2*span)+1),'navy',opaque=True)
    _bezel(c,cx,cy,rx+2,ry+1,.13*pi,1.87*pi,'navy')
    _bezel(c,cx,cy,rx,ry,0.,2*pi,'teal' if lit else 'slate')
    _bezel(c,cx,cy,rx-1.8,ry-.93,.02*pi,.97*pi,'navy')
    _bezel(c,cx,cy,rx+2,ry+1,.96*pi,1.65*pi,'cyan' if strike else 'slate')
    handoff=_pace((t-.09)/.85)
    if lit:
        # The reflected sweep runs one quarter around the metal outer lip,
        # then collapses into the white twelve-o'clock crest.
        a=(-1.0+handoff*.5)*pi
        _bezel(c,cx,cy,rx+2,ry+1,a-.21,a+.24,'white' if strike else 'teal')
    for i in range(12):
        if i%3==0:
            continue
        a=(i/6-.5)*pi
        c.line(cx+rx*.77*cos(a),cy+ry*.77*sin(a),cx+rx*.88*cos(a),cy+ry*.88*sin(a),
               'slate','.' if lit else ':')
    if settle<.97:
        # A short broadsword hour hand and a longer needle converge exactly
        # at midnight. Their different marks keep them readable in mono.
        minute=-.88*(1-handoff)
        hour=-.27*(1-_pace((t-.17)/.77))
        for angle,length,shade,ch in ((hour,.39,'slate','#'),(minute,.63,'cyan','+')):
            hx=cx+rx*length*sin(angle)
            hy=cy-ry*length*cos(angle)
            c.line(cx,cy,hx,hy,'white' if strike else shade,'|' if strike else ch)
            if not strike and ch=='+':
                c.put(round(hx),round(hy),'*','cyan')
        c.put(x-1,y,'(*)' if strike else '(+)', 'white' if strike else 'teal',opaque=True)
    if lit:
        for dx,dy,num in ((0,-.72,'12'),(.73,0,'3'),(0,.72,'6'),(-.73,0,'9')):
            mark_x=round(cx+rx*dx)-len(num)//2
            mark_y=round(cy+ry*dy)
            col='white' if num=='12' else 'teal'
            c.put(mark_x,mark_y,num,col,opaque=True)
    if 1.02<t<1.61:
        p=(t-1.02)/.59
        for j in range(24):
            a=j*pi/12
            x1=round(cx+(rx+2+p*w*.11)*cos(a))
            y1=round(cy+(ry+1+p*h*.16)*sin(a))
            c.put(x1,y1,'+' if j%6==0 else '.', 'cyan' if p<.30 else 'navy' if p>.72 else 'teal')


def render(t,w,h):
    """Draw only original blue nighttime art at the physical viewport size."""
    c=Canvas(w,h)
    if not w or not h:
        return c.finish()
    t=max(0.,min(float(t),DURATION))
    settle=_pace((t-1.62)/1.37)
    turn=_pace((t-.97)/1.49)
    ground=_sky(c,t,turn)
    _moon(c,t,turn)
    _tower(c,t,turn,ground)
    _clock(c,t,settle)
    return c.finish()


def draw_intro(app,elapsed):
    app.draw_scene_rows(render(elapsed,app.w-1,app.h))


@lru_cache(maxsize=6)
def _title_frame(w,h):
    c=Canvas(w,h)
    c.overlay(render(DURATION,w,h),0,0)
    # A single diagonal band across the clock, in contrast with the
    # off-axis tower. It becomes a stable title placement, not a menu box.
    y=round(h*.34)
    band=max(29,round(w*.47))
    x0=max(2,round(w*.075))
    for j in range(11):
        x=x0+2-j//2
        c.put(x,y+j,' '*band,'navy',opaque=True)
    c.line(x0,y,x0+band-4,y,'teal','_')
    c.put(x0-3,y+10,'__'+'-'*(band-5),'navy')
    c.put(x0+band-3,y+2,'//','teal')
    c.put(x0+band-6,y+8,'//','slate')
    c.put(0,h-2,' '*w,'navy',opaque=True)
    return c.finish(), y, x0



def _choices(top,left,choices):
    for i,(name,enabled) in enumerate(choices):
        yield top+5+i*2,left+2,name,enabled


def draw_menu(app,selection=MENU_DEFAULT,choices=MENU,notice=''):
    rows,y,x=_title_frame(app.w-1,app.h)
    app.draw_scene_rows(rows)
    app.put(y+2,x+1,TITLE,IDS['teal'],True)
    for i,(row,xx,name,enabled) in enumerate(_choices(y,x,choices)):
        active=i==selection
        mark='▶' if active else ' '
        lock=' ' if enabled else '×'
        color=IDS['teal'] if enabled else IDS['slate']
        app.put(row,xx,f'{mark} {lock} {name}'.ljust(23),color,active,active and enabled)
    if notice:app.put(app.h-4,3,notice[:app.w-6],IDS['amber'],True)
    app.mid(app.h-2,'↑↓ SELECT  ↵ OPEN  ESC BACK',IDS['teal'])


def menu_hit(app,x,y):
    _,top,left=_title_frame(app.w-1,app.h)
    return next((i for i,(row,xx,_,_) in enumerate(_choices(top,left,MENU))
                 if y==row and xx<=x<xx+23),None)
