"""Native terminal staging for the kabuki duel and Noir's truck Showtime."""
from bisect import bisect_right
from math import cos, pi, sin
from wide_canvas import Canvas

DUEL='THE DUEL AT DUSK'
TEA='TEA IN THE CROSSHAIRS'
DUEL_END=(1.,2.1,3.35,4.57,5.67,6.31,8.4)
TEA_END=(1.,2.12,3.43,4.67,5.8,6.62,8.45)
DUEL_BEATS=('Advance','Draw','Floor panels','Parasol descent','Sweep','Impact','Aftershock')
TEA_BEATS=('Approach','Transform','Board','Accelerate','Rooftop salvo','Break through','Exit')
DURATIONS={DUEL:DUEL_END[-1],TEA:TEA_END[-1]}

_BIG={
    'fox':((r'    /|       |\   ',r'   / |_______| \  ',r'  < /  >   <  \ > ',
            r'    \_  ( )  _/   ',r'      \__^__/     '),
           (r' ___/\/\|V|/\/\__',r'<___/  |###| \___>',r'    \  /###\  /',
            r'     |//   \\|',r'    _//     \\_',r'   <_/       \_>')),
    'panther':((r'  |\  .----.  /|  ',r' /__\/ .--. \/__\ ',r'(####| o  o |####)',
                r' (###/\_v_/\###) ',r'   ~~~\___/~~~   '),
               (r' __/\/\}|{/\/\__',r'<__-/  |#|  \-__>',r'     __|#|__',
                r'    / /##\ \ ',r'  _/ /   \ \_',r' <__/     \__>')),
    'noir':((r'      .-~~-.      ',r'   __/.----|__   ',r' ==\____(o)__/== ',
             r'   {#(o . o)#}   ',r'    ~\__v__/~    '),
            (r'  __/\/}>  <{__',r' /__/  \__/ \__\ ',r'    \  .() /',r'     /|##|\ ',
             r'   _/ /  \ \_ ',r'  <__/    \__>')),
    'foe':((r'   /\___/\/\    ',r'  /   ^ ^   \   ',r' <  [ * * ]  >  ',r'   \___v___/   '),
           (r' /\_[(@)]_/\ ',r'/_/\[===]/\_\ ',r'    | @ |    ',r'    /___\ ',
            r'   /|   |\ ',r'  /_|   |_\ ')),
    'cat':((r'    /\____/\    ',r'   / /o  o\ \   ',r'  |  \_v__/  |  ',r'   \_.____._/  '),
           (r'    \====/===>',r'     /##\  ',r'    _/ \_  ')),
}
_SMALL={
    'fox':((r' /|___|\ ',r'<  > <  >',r' \_()_/ '),(r'_/V\__/[]',r' |##|  |',r'_/  \_ |')),
    'panther':((r'/\.__./\ ',r'(=/oo\=)',r' ~\v/~ '),(r' _/Y\_ ',r'/ |#| \ ',r' _/ \_ ')),
    'noir':((r'    /\ ',r'===/__)===',r' {(. .)} ',r'  \_v_/  '),(r' _/}>{\_ ',r'   /o\   ',r'  _| |_')),
    'foe':((r' /\  /\ ',r'<  * *  >',r' \__v__/ '),(r'__/[#]\__',r'  | @ | ',r' _/   \_ ')),
    'cat':((r' /\_/\ ',r'( O O )',r' \_v_/ '),(r'=/=/>>',r' (_|_)')),
}
_INK={'fox':'cyan','panther':'rose','noir':'noir','foe':'wine','cat':'cyan'}
_POSE={
    ('fox','swing'):(r'___/\/\|V|/-----',r'___/   |###|===/',r'       /##/',r'   ___/ /\___',r'  <____/  \__>'),
    ('panther','float'):(r'\_\___}|{___/_/',r' \___/|#|\___/',r'     /|#|\ ',r'    /_###_\ ',r'       \_\ '),
    ('panther','sweep'):(r' _/\/}|{=======',r'/__/ |#|  =====',r'  __/##\ ',r' / /   \____',r'<_/     \___>'),
    ('noir','leap'):(r'__/\}>  <{/\__',r'\___\ \__/ /__>',r'      /o| ',r'     /##\___',r'    /_/  \__>'),
    ('noir','fire'):(r'  __/\/}>{\_______ ',r' /__/  /[]/==[===]>',r'      /\#/ ',r'    _/  \ \_',r'   <_/    \_>'),
    ('cat','dash'):(r'    \====/====>',r'  __/####\ ',r' <__>    <__>'),
}
_COMPACT={
    ('fox','swing'):(r' _/V_/>====',r'//##| ',r'_/\__ '),
    ('panther','float'):(r'\__Y__/',r'  |#|  ',r' _/ \_ '),
    ('panther','sweep'):(r'__Y====',r' /##/ ',r'<_/ \_ '),
    ('noir','leap'):(r'__/}>{\__',r' \_/o\_> ',r'     \_  '),
    ('noir','fire'):(r'_/}>{\====',r'_\ /o\===>',r' _/\_ '),
    ('cat','dash'):(r'=/=/>>',r'<_ _>'),
}


def _actor(c,who,x,feet,large,pose='ready'):
    head,neutral=(_BIG if large else _SMALL)[who]
    body=(_POSE if large else _COMPACT).get((who,pose),neutral)
    x=round(x)-max(map(len,head))//2
    y=round(feet)-len(head)-len(body)+1
    for k,row in enumerate(head+body):
        c.put(x,y+k,row,'face' if k<len(head) else _INK[who],opaque=True)


def _knockdown(c,x,floor,large):
    rows=(r'    _---/\___/\___',r' __/[@]_\_*__*_/___\_',
          r'<______/___________/ ') if large else (r'__/\_/\_',r'_[#]**__')
    c.put(round(x)-len(rows[0])//2,round(floor)-len(rows)+1,rows,'wine',opaque=True)


def _phase(ends,t):
    t=max(0.,min(t,ends[-1]))
    i=min(bisect_right(ends,t),len(ends)-1)
    a=0 if not i else ends[i-1]
    return i,(t-a)/(ends[i]-a),t


def _curve(c,points,ink,char=None):
    for (x,y),(xx,yy) in zip(points,points[1:]):
        c.line(x,y,xx,yy,ink,char)


def _petals(c,t,w,h,n,energy=0,focus=.5):
    for k in range(n):
        x=(k*31+k*k*3+int(t*(3+k%3))+int(energy*(k%5-2)*w/5))%w
        y=(k*7+k*k//5+int(t*(1+k%3))+int(energy*(k%4-1)*h/6))%h
        champ=(k+int(t*5))%4
        c.put(x,y,".'*,"[champ],('rose','wine','amber','red')[k%4])
    if energy:
        for k in range(10):
            a=2*pi*k/10+t
            c.put(round(w*focus+(3+w*.15*energy)*cos(a)),round(h*.54+(2+h*.18*energy)*sin(a)),'.*'[k%2],'amber')


def _stage(c,t,w,h,floor):
    # Sloping tiled roof, drawn across physical margins. Curtain tongues flicker.
    lintel=max(2,round(h*.21))
    for y in range(lintel):
        step=max(4,w//16)
        for x in range(-step+(y*2)%step,w,step):
            c.put(x,y,('__/\\_' if y%3==0 else ' _._ ')[:step],'wine' if y%2 else 'ochre')
    c.put(0,lintel,('_=--='*((w+4)//5))[:w],'ochre')
    pin=max(8,w//11)
    for x in range(pin//2,w,pin):
        depth=floor-lintel-3
        c.line(x,lintel,x,floor-2,'ochre','|')
        c.line(x+1,lintel,x+1,floor-3,'wine','|')
        for r in range(5,depth,4):
            c.put(x+2,lintel+r,'-'*max(2,pin-2),'ochre')
            c.put(x+pin//2,lintel+r+1,':','wine')
    for x in range(pin,w,pin*2):
        sway=round(sin(t*2.8+x)*1.1)
        c.line(x,lintel-1,x+sway,lintel+2,'amber','|')
        c.put(x+sway-3,lintel+2,(" .-.-. ","( : : )", " '-=-' "), 'amber', opaque=True)
    cx=w//2
    # Stage depth is a whole scene plane, not the perimeter of a cel.
    c.line(0,floor-3,w-1,floor-3,'ochre','_')
    for k in range(-2,13):
        x=w*k/10
        c.line(cx+(x-cx)*.28,floor-3,x,h-1,'ochre')
    for y in range(floor+1,h,2 if h<28 else 3):
        dash=max(4,w//12)
        for x in range(-dash+(y*3)%dash,w,dash):
            c.put(x,y,'.'+'_'*(dash-2),'wine' if (y+x)%3 else 'ochre')
    # Irregular scalloped curtains stay far from the stage's central actors.
    for side in (0,1):
        for k in range(max(2,w//20)):
            edge=2*k+round(sin(t*1.4+k))
            x=edge if not side else w-1-edge
            yy=lintel+max(1,round(h*.11))-k//2
            c.line(x,0,x+(-2 if side else 2)*(-1)**k,yy,'wine','|')
            c.put(x,yy,').'[k%2],'rose')


def _canopy(c,x,y,r,opened,t,wipe=False):
    rx=max(2,round(r*opened)); ry=max(1,round(r/4))
    x,y=round(x),round(y)
    arc=[(x+rx*cos(k*pi/10),y-ry*sin(k*pi/10)) for k in range(11)]
    _curve(c,arc,'red' if wipe else 'rose')
    c.line(x-rx,y,x+rx,y,'rose','_')
    for q in (-1,-.5,0,.5,1):
        c.line(x,y-ry,x+rx*q,y,'wine' if q else 'rose')
    if rx>4:
        for j in range(-rx+2,rx-1,3):
            c.put(x+j,y-1,'.' if (j+int(t*8))%2 else ':','amber')
    shaft=ry+3
    c.line(x,y+1,x,y+shaft,'amber','|')
    c.put(x-1,y+shaft,r'\_/','amber')


def _flash(c,x,y,r,p,ink='amber'):
    x,y=round(x),round(y)
    c.put(x-2,y,'<*+*>','white' if p<.40 else ink)
    for k in range(14):
        a=2*pi*k/14
        n=r*(.25+.75*p)
        dx=cos(a)*n;dy=.52*sin(a)*n
        c.line(x+dx*.48,y+dy*.48,x+dx,y+dy,ink,'.' if p>.68 else None)
        if p<.8:
            c.put(round(x+dx),round(y+dy),'*' if k%2 else '+',ink)


def _duel(t,w,h):
    i,f,t=_phase(DUEL_END,t);c=Canvas(w,h)
    big=w>=74 and h>=28
    x=lambda p:p*(w-1)
    floor=round((h-1)*.69)
    _stage(c,t,w,h,floor)
    _petals(c,t,w,h,max(8,w//4),f if i==6 else 0,.73)
    r=max(5,w//10)
    if i<=1:
        fox=.09+.11*f if i==0 else .20+.23*f
        foe=.57-.02*f if i==0 else .55+.08*f
        _actor(c,'foe',x(foe),floor,big)
        _actor(c,'panther',x(.83),floor-1,big)
        _canopy(c,x(.83),floor-(13 if big else 8),r,.26,t)
        _actor(c,'fox',x(fox),floor-int(sin(f*pi)*2),big,'swing' if i==1 and f>.52 else 'ready')
        if i==1 and f>.52:
            p=(f-.52)/.48
            c.line(x(fox)+3,floor-4,x(.56+.11*p),floor-7-p*2,'white','-')
            _petals(c,t,w,h,w//6,p,.58)
    elif i==2:
        _actor(c,'fox',x(.43-.23*f),floor,big,'swing')
        _actor(c,'foe',x(.63+.10*f),floor-round(sin(pi*f)*h*.13),big)
        _actor(c,'panther',x(.83),floor-1,big)
        for k in range(8):
            p=min(1,max(0,1.6*f-k*.085))
            amp=sin(pi*p)
            xx=round(x(.28+.065*k)); yy=floor-round(h*.31*amp)
            if yy<floor-1:
                panel=max(2,w//21)
                c.put(xx,yy,(' _'+'_'*panel, '/_'+('_'*(panel-1))+'/\\','\\_'+('_'*(panel-1))+'\\/'),
                      'amber' if k%2 else 'red',opaque=True)
    elif i==3:
        _actor(c,'fox',x(.20),floor,big)
        _actor(c,'foe',x(.73+.07*f),floor,big)
        pan=.83-.43*f
        feet=floor-round(h*.29*sin(pi*f))
        _actor(c,'panther',x(pan),feet,big,'float')
        _canopy(c,x(pan)+(5 if big else 3),max(2,feet-(12 if big else 7)),r,.50+.50*sin(f*pi/2),t)
        for k in range(9):
            c.put(round(x(pan))+k+3,feet+k//4,"*+."[k%3],'rose')
    elif i<=5:
        pan=.40+.23*f if i==4 else .63+.12*f
        foe=.80+.06*f if i==4 else .86+.08*f
        _actor(c,'fox',x(.20-.04*f),floor,big)
        if i==4:
            _actor(c,'foe',x(foe),floor,big)
        else:
            _knockdown(c,x(foe),floor,big)
        _actor(c,'panther',x(pan),floor-round(2*sin(pi*f)),big,'sweep')
        _canopy(c,x(pan+.1),floor-(10 if big else 6),r,.9-.48*f,t,True)
        if i==4:
            wave=[(x(.45+.035*k+.09*f),floor-3-sin(pi*k/11)*h*.22) for k in range(12)]
            _curve(c,wave,'white','=')
        else:
            _flash(c,x(.83)+3*f,floor-(6 if big else 4),max(5,w*.16),f,'red')
            _petals(c,t,w,h,w//3,f,.83)
    else:
        _knockdown(c,x(.94-.025*f),floor,big)
        _actor(c,'fox',x(.16+.08*f),floor,big)
        _actor(c,'panther',x(.75-.22*f),floor-round(2*sin(pi*f)),big,'float' if f<.36 else 'ready')
        _canopy(c,x(.85-.22*f),floor-(11 if big else 6),r,max(.15,.55-f*.47),t)
        _petals(c,t,w,h,w//4,1-f,.85)
    return DUEL_BEATS[i],c.finish()


def _tunnel(c,t,w,h,floor,speed):
    apex=round(h*.34); pivot=w*.58
    # Native arch trusses sweep forward toward the viewer; the gaps open with depth.
    for k in range(7):
        dep=(k/7+t*(.12+.12*speed))%1
        r=dep*dep
        rx=w*(.18+.43*r); ry=h*(.11+.46*r)
        path=[(pivot+rx*cos(pi*j/18),apex-ry*sin(pi*j/18)) for j in range(19)]
        _curve(c,path,'slate' if r>.31 else 'navy')
        for sign in (-1,1):
            edge=(pivot+sign*rx,apex)
            c.line(*edge,pivot+sign*rx*1.13,floor-3,'navy','|')
            xx=round(pivot+sign*rx*.84); yy=round(apex-ry*.37)
            c.put(xx,yy,'[==]' if r>.42 else '.','teal' if r>.35 else 'slate')
            if k%3==1 and r>.39:
                c.put(xx-1,yy+1,'.--.','amber')
    for end in (-.1,.19,.53,.86,1.15):
        xx=w*end
        c.line(pivot+(xx-pivot)*.16,apex+1,xx,h-1,'teal' if end in (-.1,1.15) else 'navy','.')
    for y in range(apex+3,h):
        d=(y-apex)/max(1,h-apex-1); dl=max(1,int(d*6)); step=11+int(d*31)
        shift=(int(t*(22+20*speed)*d)+y*4)%step
        for x in range(-shift,w,step):
            c.put(x,y,('-' if y%3==0 else '.')*dl,'slate' if y%3==0 else 'navy')
    for x in range(0,w,8):
        p=(x*23+round(t*29*speed))%w
        y=floor+1+(x*7)%max(1,h-floor-1)
        c.put(p,y,':.' if x%3 else '...','slate')


def _van(c,cx,floor,w,h,p,t):
    # The truck chassis uses the full world's resolution instead of a sprite zoom.
    tw=round(max(9,w*.35)*p); th=max(2,round(max(4,h*.26)*p))
    x=round(cx-tw*.5); y=round(floor-th)
    if tw<11:
        c.put(x,y,(r'  /===\ ',r' /[]|[_\_>',r'|___^____|',r' (_o) (o)'), 'teal',opaque=True)
        return y
    a=max(3,tw//5)
    c.line(x+a,y,x+tw-a,y,'white','=')
    c.line(x+a,y,x+2,y+th//2,'cyan','/')
    c.line(x+tw-a,y,x+tw-2,y+th//2,'teal','\\')
    for j in range(1,th):
        lx=x+max(0,a-(j*a*2)//th)
        rx=x+tw-max(0,a-(j*a*2)//th)
        c.put(lx,y+j,' '+' '*(rx-lx-1)+' ','teal',opaque=True)
        c.put(lx,y+j,'/' if j<th//2 else '|','cyan')
        c.put(rx,y+j,'\\' if j<th//2 else '|','teal')
        if j<=max(2,th//3):
            for off in (a,tw//2,tw-a-3):
                c.put(x+off,y+j,'[_]' if j%2 else '[:]', 'slate' if off!=tw-a-3 else 'navy')
        elif j==th-2:
            c.put(x+2,y+j,'-='*((rx-lx-2)//2),'cyan')
    c.line(x,y+th-1,x+tw,y+th-1,'teal','=')
    for dx in (a,tw-a):
        rr='o' if int(t*19)%2 else '*'
        c.put(x+dx-2,y+th-1,('/-o-\\','( '+rr+' )', '\\___/'),'navy',opaque=True)
        c.put(x+dx,y+th,rr,'white')
    lamp=x+tw-2
    c.put(lamp,y+th-3,'[=]','amber',opaque=True)
    for k in range(3):
        dd=max(3,w//11)
        c.line(lamp+3,y+th-3,lamp+dd+int(sin(t*9)*2),y+th-4+k,'amber','.' if k!=1 else '-')
    return y


def _smoke(c,x,y,t,f,w,h):
    for k in range(18):
        d=(k/18+t*.7)%1
        xx=round(x-(.5+d)*w*.14+cos(k)*w*.055*f)
        yy=round(y-h*.20*d+((k*7)%11-5)*f)
        c.put(xx,yy,('...','. :','~~' if f<.4 else ':')[k%3],('slate','wine','amber')[k%3] if f<.5 else 'slate')


def _tea(t,w,h):
    i,f,t=_phase(TEA_END,t);c=Canvas(w,h)
    big=w>=74 and h>=28
    x=lambda p:p*(w-1)
    floor=round((h-1)*.73)
    _tunnel(c,t,w,h,floor,.27 if i<2 else .62 if i<4 else 1.)
    if i<=1:
        cat=.09+.12*f if i==0 else .21+.14*f
        _actor(c,'foe',x(.87-.04*f),floor-1,big)
        _actor(c,'noir',x(.63),floor,big,'ready')
        if i==0 or f<.24:
            _actor(c,'cat',x(cat),floor-round(2*sin(pi*t*4)**2),big,'dash')
            c.line(x(cat)-w*.08,floor-2,x(cat)-4,floor-2,'teal','-')
        else:
            p=min(1,.24+(f-.24)*1.2)
            _van(c,x(cat),floor,w,h,p,t)
            if f<.72:
                _flash(c,x(cat),floor-h*.12,w*.18,(f-.24)/.48,'cyan')
    elif i==2:
        pos=.35+.11*f
        roof=_van(c,x(pos),floor,w,h,1.,t)
        _actor(c,'foe',x(.83),floor-1,big)
        no=.63-.13*f
        feet=(1-f)*floor+f*roof-h*.13*sin(pi*f)
        _actor(c,'noir',x(no),feet,big,'leap' if f<.78 else 'fire')
        _smoke(c,x(pos-.13),floor,t,f,w,h)
    elif i<=4:
        pos=.46+.03*f if i==3 else .49+.06*f
        roof=_van(c,x(pos),floor-round(1.6*sin(t*11)**2),w,h,1.,t)
        _actor(c,'foe',x(.85+.05*f),floor-1,big)
        _actor(c,'noir',x(pos+.026),roof,big,'fire')
        _smoke(c,x(pos-.14),floor,t,f,w,h)
        if i==4:
            for j in range(4):
                p=f*3.15-j*.39
                if 0<=p<1.08:
                    rx=x(pos+.095+(.40-pos*.10)*p); ry=roof-h*.17+h*.11*p-(j%3)
                    c.line(rx-w*.10,ry+1,rx,ry,'amber','~')
                    c.put(round(rx),round(ry),'==>*','white' if j%2 else 'amber')
            if f>.54:
                _flash(c,x(.86),floor-h*.23,w*.17,(f-.54)/.46,'amber')
    elif i==5:
        pos=.55+.18*f
        for k in range(3):
            p=max(0,min(1,f*1.4-k*.17))
            if p:
                _flash(c,x(.80+.078*k),floor-(.20+.07*k)*h,w*.14,p,'rose' if k%2 else 'amber')
        _smoke(c,x(.80),floor-h*.15,t,f,w,h)
        _knockdown(c,x(.92),floor,big)
        roof=_van(c,x(pos),floor-round(h*.10*sin(f*pi)),w,h,1.,t)
        _actor(c,'noir',x(pos+.026),roof,big,'fire')
    else:
        pos=.73+.46*f
        _knockdown(c,x(.91),floor,big)
        _smoke(c,x(pos-.13),floor,t,f,w,h)
        _smoke(c,x(.89),floor-h*.12,t,1.,w,h)
        roof=_van(c,x(pos),floor-round(h*.15*sin(pi*f)),w,h,1.,t)
        _actor(c,'noir',x(pos+.026),roof,big,'leap' if f>.56 else 'fire')
    return TEA_BEATS[i],c.finish()


def render(title,t,w,h):
    """Render a full native-sized frame, returning only an internal beat label and art."""
    if title==DUEL:
        return _duel(t,w,h)
    if title==TEA:
        return _tea(t,w,h)
    raise KeyError(title)
