"""Responsive native-cell Oracle cinematics. No overlays or textual artwork.

The scene graph sets perspective and coordinates from the actual viewport;
lines, details, and silhouettes are drawn anew at each size.
"""
from math import cos, pi, sin, sqrt, tau

from oracle_scene import GUARD, SUPPORT, TITLE
from wide_canvas import Canvas


def _p(t, a, b):
    return max(0.0, min(1.0, (t-a)/(b-a)))


def _pos(w, h, x, y):
    return round((w-1)*x), round((h-1)*y)


def _starfield(c, w, h, t, palette):
    """Independently moving deep stars, far ridges, and projected floor."""
    horizon = round(h*.71)
    for i in range(w*h//34):
        z = i%3+1
        x = (i*73 + 11*(i//7) - round(t*z*2)) % w
        y = (i*47 + 13*(i//11)) % (horizon+3)
        pulse = (i+round(t*9))%17
        c.put(x, y, '+' if pulse in (0,1) else '*' if i%11==0 else '.', palette if pulse==0 else 'dim')
    for x in range(0,w,2):
        flow = x + t*8
        y = horizon - round((sin(flow*.082) + .40*sin(flow*.207))*h*.043)
        c.put(x,y,('^','_','~')[x%3],'dim')
    vx = round(w*.51)
    for x in range(-w//3, w+w//3, max(8,w//12)):
        c.line(vx+(x-vx)//8, horizon+1, x, h-1, 'dim', '.' if x%3 else ':')
    for j in range(1,7):
        f = (j/6 + t*.35) % 1
        y = horizon+1+round(f*f*(h-horizon-2))
        step = max(4, int(2+f*9))
        for x in range((int(t*9)+j)%step,w,step):
            c.put(x,y,'_' if j%2 else '-','dim')
    for x,f in ((w//13,.12),(w//4,.07),(w*4//5,.10),(w*15//16,.14)):
        size = max(2,round(h*f))
        y = min(h-2,horizon+round((x%17)/17*(h-horizon)))
        c.line(x-size,y+1,x,y-size,'dim','/')
        c.line(x,y-size,x+size*2,y,'dim','\\')
        c.line(x-size,y+1,x+size*2,y,'dim','_')
    return horizon


def _ship(c, cx, y, width, h, tick):
    """A dome, shaped rim, vents and animated running lamps; no scaled text."""
    width = max(23,width)
    rad = width//2
    dome_h = max(3, round(h*.17))
    dome_w = round(rad*.46)
    lens = max(2,round(dome_w*.48))
    for k in range(dome_h+1):
        span = max(2,round(dome_w*sqrt(max(0,1-((k-dome_h)/dome_h)**2))))
        if k == 0:
            c.put(cx-span,y, '.'+'-'*(span*2-1)+'.','cyan',True)
        elif k < dome_h:
            inside = [' '] * (2*span-1)
            for i in range(len(inside)):
                dx = i-span+1
                if abs(dx)<lens and (i+k)%4==0:
                    inside[i]='.'
                if abs(dx)==lens and k>1:
                    inside[i]=':' if k%2 else '|'
            if k==dome_h-1:
                token = '<'+('*' if tick%4 else '+')+'>'
                inside[span-2:span+1] = token
            c.put(cx-span,y+k,'/'+''.join(inside)+'\\','cyan',True)
    base = y+dome_h
    c.put(cx-rad+4,base, '.-'+'='*(rad*2-10)+'-.','green',True)
    c.put(cx-rad,base+1, '<'+'='*(rad*2-1)+'>','green',True)
    p = max(3,rad//7)
    rim = [':' if i%4 else '_' for i in range(2*rad-3)]
    for i in range(2,len(rim)-1,p):
        rim[i] = ('o','*','O','*')[(tick//3+i//p)%4]
    c.put(cx-rad+1,base+2,'\\'+''.join(rim)+'/','green',True)
    tail = max(3, rad//4)
    c.put(cx-rad+3,base+3, '\\'+'_'*(rad-tail-4)+'/'+'='*(2*tail-1)+'\\'+'_'*(rad-tail-4)+'/','cyan',True)
    c.put(cx-tail+1,base+4,'<'+':'*(2*tail-3)+'>','white',True)
    return base+4


def _beam(c, sx, sy, tx, ty, radius, tick, ink):
    c.line(sx-2,sy,tx-radius,ty,ink)
    c.line(sx+2,sy,tx+radius,ty,ink)
    span = max(1,ty-sy)
    for y in range(max(0,sy+1),ty,2):
        f = (y-sy)/span
        cx = sx + round((tx-sx)*f)
        limit = max(1,round(radius*f))
        for dx in range(-limit+1,limit,4):
            c.put(cx+dx,y,'+' if (tick+y+dx)%5==0 else '.',ink)


def _ring(c, x,y,rx,ry,ink,t,arc=False):
    steps = max(19,rx*4)
    top = pi if arc else 0
    sweep = pi if arc else tau
    for i in range(steps+1):
        a = top + sweep*i/steps
        mark = ('o' if (i+round(t*24))%13==0 else ':' if i%2 else '.')
        c.put(x+round(cos(a)*rx),y+round(sin(a)*ry),mark,ink)


def _flare(c,x,y,w,h,t,inks):
    t = max(0,min(1,t))
    for i in range(35):
        a = tau*i/35
        r = (1-.30*(i%3)/3)*max(w*.20,9)*(t+.12)
        dx,dy = cos(a)*r, sin(a)*r*(h/w+.08)
        tx,ty = x+round(dx), y+round(dy)
        c.line(x+round(dx*.62),y+round(dy*.62),tx,ty,inks[i%len(inks)],
               '.' if t>.60 else None)
        c.put(tx,ty,'*' if i%2 else '+',inks[(i+1)%len(inks)])
    if t<.25:
        c.put(x-4,y-1,('   |   ',r'\--*--/','/--*--' + chr(92),'   |   '),'white')


READY = (
    ('  .~~.  ', ' <v==v> ', '  /--\\  ', ' _\\::/_ ', '  |::|  ', ' /|  |\\ ', '  /  \\ ', ' o/  \\o '),
    ('  /^\\   ', ' [===]  ', '  \\_/   ', '<^/##\\^>', ' \\|##|/ ', '  /##\\  ', ' /_/\\_\\ ', ' o/  \\o '),
    ('  .~^~. ', ' ( . . )', '  \\_v_/ ', ' _/\\|/\\_', '  |~|   ', ' / V \\  ', '  / \\   ', ' _/ \\_  '),
    ('   _<>  ', '  /==\\  ', '  \\_/>  ', ' _/\\Y/\\_', '  / V\\  ', ' /   |  ', '  /|/   ', ' _/ \\_  '),
)
INKS = ('red', 'cyan', 'gold', 'white')
SHADOW = ('^--_  _--^', '/(*)(*)\\', '\\ _WW_ /', '/###|###\\', '\\_######_/', '/_ /\\ _\\', '<_/    \\_>')
CROUCH = (' _/..\\_ ', '/_\\##/_\\', '  /_/\\_\\', '_/     \\_')
BRACE = ('  .--.  ', ' [====] ',r'_/\##/\_', ' /|##|\\ ', '/_    _\\', '\\_>  <_/')
MISSILE = ('    __ /./', '<<-[####]===========>>', '    -- \\.\\')


def _figure(c,x,y,rows,ink):
    # Spaces within a silhouette blank the scenery; spaces outside it do not.
    for j, row in enumerate(rows):
        left = len(row)-len(row.lstrip())
        c.put(x-len(row)//2+left,y+j,row.strip(),ink,True)


def _squad(c,w,h,t,ground,mode):
    group = (.15,.27,.39,.51) if mode == 'guard' else (.19,.39,.60,.81)
    for i, frac in enumerate(group):
        x = round(w*frac)
        y = ground+round(h*(.08+(i%2)*.04))
        if mode=='guard':
            braced = .8 < t < 1.85
            _figure(c,x,y-(5 if braced else 7),BRACE if braced else READY[i],INKS[i])
        else:
            ready = t >= 1.10 + i*.13
            c.put(x-4,y+1,'.........','dim')
            _figure(c,x,y-(7 if ready else 3),READY[i] if ready else CROUCH,INKS[i])


def _payload(c,w,h,t,ground):
    impact_x, impact_y = round(w*.60), round(h*.86)
    tick = round(t*36)
    fly = _p(t,0,.88)
    leave = _p(t,2.12,3.15)
    sx,sy = _pos(w,h,.12+.48*sin(fly*pi/2)+.74*leave**1.3,.06+.04*sin(pi*fly)-.27*leave)
    scan = _p(t,.2,1.10)
    power = _p(t,.88,1.70)
    hull = round(w*(.36+.17*fly-.10*leave))
    deck = sy+max(3,round(h*.17))+4
    if t<1.70:
        _figure(c,impact_x,impact_y-6,SHADOW,'foe')
        if scan:
            _beam(c,sx,deck,impact_x,impact_y,max(3,round(w*.20*scan)),tick,'green')
            if t>.44:
                _ring(c,impact_x,impact_y,round(w*.21*scan),max(1,h//16),'cyan',t)
        if power:
            bx = round(sx+(impact_x-sx)*power)
            by = round(deck+(impact_y-deck)*power**1.62)
            for j in range(3):
                c.put(bx-j%2,by-j-1,'.*+'[j],'gold')
            _figure(c,bx,by,(' ,*','_/_','/##\\','\\__/'),'gold')
    elif t<2.69:
        f = _p(t,1.70,2.69)
        _flare(c,impact_x,impact_y,w,h,f,('gold','white','red'))
        for k in range(w//3):
            dx = (k*37%(w//2)) - w//4
            px = impact_x+round(dx*sqrt(f))
            py = impact_y-round(f*(k%9+1)*(h/25))
            c.put(px,py,'.,*'[k%3],'dim' if f>.43 else 'gold')
    else:
        for k in range(w//4):
            px = impact_x+(k*29%(w//2))-w//4+round(leave*11)
            py = impact_y-round((k%8)*leave*h/24)
            c.put(px,py,'.' if k%3 else ',','dim')
    _ship(c,sx,sy,hull,h,tick)
    return 'flyover' if t<.88 else 'payload' if t<1.70 else 'blast' if t<2.69 else 'depart'


def _support(c,w,h,t,ground):
    sx,sy = _pos(w,h,.50+.045*sin(t*4),-.21+.25*_p(t,0,.65)-.26*_p(t,2.36,2.85))
    tick = round(t*32)
    deck = sy+max(3,round(h*.17))+4
    for i, frac in enumerate((.19,.39,.60,.81)):
        x, y = _pos(w,h,frac,.79+(i%2)*.04)
        delay = .42+i*.12
        f = _p(t,delay,delay+.43)
        off = 1-_p(t,2.08+i*.10,2.45+i*.09)
        if f and off:
            width = max(1,round(w*.09*f*off))
            _beam(c,sx,deck,x,y,width,tick+i,'cyan')
            p = (t*2.1+i*.16)%1
            _ring(c,x,y,max(2,round(width*(.8+.45*p))),max(1,round(h*.065*p)),'green',t)
            for j in range(max(4, w//13)):
                yr = max(deck+1,y-round((p+j*.07)%1*h*.29))
                xr = x+round(sin(j*16+t*9)*width*.9)
                c.put(xr,yr,'+.*'[j%3],'green')
    _squad(c,w,h,t,ground,'support')
    for i in range(4):
        x,y = _pos(w,h,(.19,.39,.60,.81)[i],.62)
        if 1.1+i*.13 < t < 1.58+i*.13:
            _flare(c,x,y,max(12,w//5),h,.48*_p(t,1.1+i*.13,1.58+i*.13),('green','cyan','white'))
    _ship(c,sx,sy,round(w*.45),h,tick)
    return 'relay' if t<.55 else 'transfer' if t<1.32 else 'rally'


def _guard(c,w,h,t,ground):
    cx,base = _pos(w,h,.34,.87)
    sx,sy = _pos(w,h,.30+sin(t*3.5)*.055,-.22+.26*_p(t,0,.54)-.22*_p(t,2.16,2.88))
    tick = round(t*35)
    radius = round(w*.30)
    dome_h = max(6,round(h*.52))
    growth = _p(t,.38,.96)
    shield = growth*(1-_p(t,2.17,2.85))
    shot = _p(t,0,1.12)
    target_x = cx+radius-1
    target_y = base-round(dome_h*.35)
    if t<1.14:
        mx = round(w*1.14 + (target_x-w*1.14)*shot**1.4)
        my = round(h*.12 + (target_y-h*.12)*shot**1.1)
        for j in range(7):
            c.line(mx+3,my+j%3-1,mx+round(w*.27),my-2-j%2,'red' if j%2 else 'gold','.')
        _figure(c,mx,my,MISSILE,'red')
    if shield > .05:
        rx, ry = max(1,round(radius*shield)),max(1,round(dome_h*shield))
        _ring(c,cx,base,rx,ry,'cyan',t,arc=True)
        if rx>2 and ry>2:
            _ring(c,cx,base,rx-2,ry-1,'green',t+.25,arc=True)
        if 1.12<=t<2.17:
            chase = _p(t,1.12,2.17)
            center = -.4-pi*chase
            for i in range(-6,7):
                a = center+i*.04
                if -pi<a<0:
                    c.put(cx+round(rx*cos(a)),base+round(ry*sin(a)),
                          '*+#'[i%3],'white' if i%2 else 'gold')
    _squad(c,w,h,t,ground,'guard')
    if t>.37 and t<2.44:
        deck = min(base,sy+max(3,round(h*.17))+4)
        _beam(c,sx,deck,cx,min(base,deck+max(2,h//6)),max(2,w//23),tick,'green')
    if 1.12<=t<2.04:
        phase = _p(t,1.12,2.04)
        _flare(c,target_x,target_y,w,h,phase,('gold','cyan','white'))
        for i in range(w//6):
            x = target_x+round((i*9%max(9,w//4))*phase)
            y = target_y-round(phase*(i%9+1)*h/27)
            c.put(x,y,'*' if i%3==0 else '.','gold' if phase<.6 else 'cyan')
    _ship(c,sx,sy,round(w*.40),h,tick)
    return 'incoming' if t<.42 else 'shield' if t<1.12 else 'deflect' if t<2.04 else 'clear'


_SCENES = {TITLE:(3.25,_payload,'green'), SUPPORT:(2.85,_support,'cyan'),
           GUARD:(2.90,_guard,'cyan')}


def render(title, elapsed, width, height):
    """Render one native-size (beat, rows) frame without persistent state."""
    duration,draw,ink = _SCENES[title]
    t = max(0,min(duration,elapsed))
    c = Canvas(width,height)
    ground = _starfield(c,width,height,t,ink)
    beat = draw(c,width,height,t,ground)
    return beat,c.finish()
