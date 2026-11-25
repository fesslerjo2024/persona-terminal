"""Original opening beats and native art for Persona 3 Terminal's spring demo."""
from dataclasses import dataclass
from math import cos, pi, sin
from types import MappingProxyType

from wide_canvas import Canvas

TRANSITION_SECONDS = 1.45


@dataclass(frozen=True)
class Beat:
    id: str
    date: str
    heading: str
    lines: tuple[str, ...]
    art: str


# Original scenes, not a transcription of the game.
BEATS = (
    Beat('arrival', '04/06', 'LAST TRAIN TO IWATODAI', (
        'The last train pulls out of Iwatodai. Outside the station, the streetlights are on, but none of the clocks are moving.',
        'The dorm is still lit. Yukari slides a room key across the desk. “Get some sleep. You can ask about the station in the morning.”',
    ), 'arrival'),
    Beat('awakening', '04/09', 'THE ROOFTOP', (
        'The dorm lights cut out. Yukari pulls you onto the roof, then stops short. Something has followed you up the stairs.',
        'Yukari: “You saw it too, right? Okay. Good. I really needed someone else to see it.”',
        'The shape closes in. When you stand between it and Yukari, something answers: Orpheus.',
    ), 'awakening'),
    Beat('tartarus', '04/20', 'THE FIRST CLIMB', (
        'At midnight, the school becomes Tartarus. Mitsuru takes the radio. The rest of you take the stairs.',
        'Mitsuru: “This is reconnaissance. Listen for my signal, and come back as a group.”',
        'Junpei: “Right. First day on the job and we’re climbing the world’s worst staircase.”',
    ), 'tartarus'),
    Beat('relay', '04/21', 'KEEP THE SIGNAL', (
        'Mitsuru taps the dorm receiver. The signal thins above the first floors of Thebel. A relay point would make the return trip safer.',
        'Akihiko: “You don’t have to prove anything by staying out. Get the route down, then get home.”',
    ), 'relay'),
    Beat('monorail', '05/09', 'THE LAST CAR', (
        'A Shadow signal is moving along the monorail. The station is deserted, but a train is still on the track.',
        'Mitsuru: “The strongest reading is in the lead car. Stay together and work your way forward.”',
        'Junpei: “Sure. Last train, no ticket, one very bad passenger. I can work with that.”',
    ), 'monorail'),
    Beat('finale', '05/10', 'FIRST LIGHT', (
        'The first train of the morning pulls into Iwatodai. To everyone else, it is just Sunday.',
        'Yukari sets a paper cup beside your notebook. “I got you one, too. Don’t ask what it is. Just drink it while it’s hot.”',
    ), 'finale'),
)
BY_ID = MappingProxyType({beat.id: beat for beat in BEATS})


def _arc(c,x,y,rx,ry,ink,start=0,stop=2*pi):
    last=(x+rx*cos(start),y+ry*sin(start))
    for i in range(1,33):
        a=start+(stop-start)*i/32
        here=(x+rx*cos(a),y+ry*sin(a))
        c.line(*last,*here,ink)
        last=here


def _stars(c,t,ink='slate'):
    for i in range(max(8,c.w//4)):
        x=(i*41+i*i*3)%c.w
        y=(i*21+i*i//5)%max(1,int(c.h*.60))
        if (i+round(t*8))%6:
            c.put(x,y,'+' if (i+round(t*6))%11==0 else '.',ink)


def _city(c,horizon,dawn=False):
    for x in range(-2,c.w,6):
        k=x//6
        top=horizon-max(1,round(c.h*(.07+((k*k+3*k)%9)*.01)))
        size=3+(k*k)%5
        ink='slate' if k%3 else 'navy'
        c.line(x,top,x+size,top,ink,'_')
        c.line(x,top,x,horizon,ink,'|')
        c.line(x+size,top,x+size,horizon,ink,'|')
        for y in range(top+1,horizon,2):
            if (k+y)%3:
                c.put(x+1,y,'.' if k%2 else ':','amber' if dawn else 'teal' if k%4==0 else 'navy')
    c.line(0,horizon,c.w-1,horizon,'navy','_')


def _tracks(c,vx,vy,t):
    for j in (-2,-1,1,2):
        c.line(vx+j*1.2,vy,c.w*(.5+j*.185),c.h-1,'navy')
    for y in range(vy+1,c.h):
        stretch=(y-vy)/max(1,c.h-vy-1)
        if (y-vy+round(t*2))%int(2+4*stretch)==0:
            span=round(c.w*(.024+.37*stretch))
            c.put(round(vx)-span,y,'-'*(2*span+1),'slate')


def _platform(c,t,dawn=False):
    w,h=c.w,c.h
    _stars(c,t,'ochre' if dawn else 'slate')
    horizon=round(h*.58)
    if dawn:
        _arc(c,w*.69,horizon,w*.13,h*.21,'ochre',pi,2*pi)
        _arc(c,w*.69,horizon-1,w*.11,h*.18,'amber',pi,2*pi)
    _city(c,horizon,dawn)
    vx=round(w*.48)
    _tracks(c,vx,horizon,t)
    c.line(0,round(h*.073),vx-3,horizon-1,'navy')
    c.line(w-1,round(h*.32),vx+4,horizon-1,'navy')
    for i in range(4):
        x=round(w*(.08+i*.105))
        top=round(h*(.18+i*.088)); foot=round(h*(.89-i*.066))
        c.line(x,top,x,foot,'slate','|')
        c.put(x-1,top,'[--]' if i<2 else '[-]','amber' if dawn else 'cyan')
        if i<2:
            c.line(x+1,top+1,x+4,foot-1,'navy','.')
    c.put(round(w*.76),horizon-4,('.--------.','| .. ..  |','|   .    |','+--------+'),
          'ochre' if dawn else 'teal')
    if not dawn:
        x,y=round(w*.23),round(h*.79)
        c.put(x,y,('  _  ','_|_|_','|###|','|___|'),'slate')
        c.line(x+1,y+4,x+9,y+5,'navy','.')
    else:
        c.put(round(w*.18),round(h*.78),(' . ~ ' if int(t*4)%2 else '  ~ .',
              r' /---\ ',r' \___/ '),'amber')


_HARP = (
    r'     .-*-.',
    r'    / .-. \ ',
    r'   | /| |\ |',
    r'   | \| |/ |',
    r'   /\__|__/\\',
    r'  /  /||| \  \\',
    r' /__/ |||  \__\\',
    r'      \_/',
)


def _roof(c,t):
    w,h=c.w,c.h
    _stars(c,t)
    rim=round(h*.63)
    _arc(c,w*.72,h*.29,w*.12,h*.18,'teal')
    _arc(c,w*.72+1,h*.29,w*.10,h*.17,'navy',pi*.52,pi*1.48)
    _city(c,rim)
    for x in range(0,w,7):
        c.line(x,rim-3,x,rim+4,'navy','|')
        c.put(x,rim-4,'+','slate')
        c.put(x+1,rim-2,'/\\','navy')
        c.put(x+1,rim,'\\/','navy')
    c.line(0,rim+4,w-1,rim+4,'slate','=')
    for x in range(-4,w+5,12):
        c.line(w*.51+(x-w*.51)*.27,rim+5,x,h-1,'navy')
    x=round(w*.28); y=max(2,round(h*.26))
    for k,row in enumerate(_HARP):
        c.put(x,y+k,row,'teal' if k%3 else 'cyan',opaque=True)
    for i in range(11):
        angle=i*2*pi/11+t*.45
        xx=round(x+6+(w*.082+(i%2)*3)*cos(angle))
        yy=round(y+4+(h*.16+(i%3))*sin(angle))
        c.put(xx,yy,'.' if i%3 else '*','cyan' if i%4==0 else 'slate')


def _desk(c,t,variant):
    w,h=c.w,c.h
    floor=round(h*.70)
    c.line(0,round(h*.26),w-1,round(h*.26),'navy','_')
    for x in range(0,w,max(9,w//9)):
        if variant!='velvet':
            c.line(x,round(h*.27),x,floor,'navy','|')
            c.put(x+1,floor-2,'..','slate')
        else:
            _arc(c,x+w*.055,round(h*.42),w*.095,h*.26,'navy',pi,2*pi)
            for dx in (-4,0,4):
                c.line(x+dx,round(h*.31),x+dx,floor,'navy','|')
    c.line(0,floor,w-1,floor,'slate','=')
    for y in range(floor+1,h,3):
        c.put(0,y,('..    '*((w+5)//6))[:w],'navy')
    x=round(w*.69); y=max(1,floor-8)
    if variant=='velvet':
        c.put(x-3,y+1,(" .'. ","  |  "," _-_ "),'teal')
        c.put(x+13,y+1,(' .*. ','  |  ',' _-_ '),'teal')
        c.put(x,y+4,(r' /____\/____\ ',r'\\____/\____//','      |      '),'slate')
        c.put(x-7,y+7,'='*min(28,w-x+1),'teal')
        return
    c.put(x-5,y,(
        '.--------------.','|.------------.|','||            ||','||            ||',
        '||____________||','|___...________|',r'   /_____\     ',
    ),'slate',opaque=True)
    if variant=='relay':
        phase=int(t*7)%12
        c.put(x-2,y+2,'...:'+('/\\' if phase<6 else '\\/')+':..','teal')
        c.put(x-2,y+3,' _ . . . ','navy')
        c.put(x+14,y+1,('  /',' +','[=]','[:]','[_]'),'slate')
    else:
        c.put(x-2,y+2,'- .   _.','navy')
        c.put(x-2,y+3,' .-   -:','teal')
        c.put(x+14,y+4,(' _ ',r'/__\\',r'\__/'),'amber')
    c.put(x-6,floor+1,(' __    ____________ ',r'|__|  /____:____:_/ '),'slate')


def _stairs(c,t,animated=1.):
    w,h=c.w,c.h
    vx=w*.50; vy=round(h*.59)
    _stars(c,t,'forest' if animated>.62 else 'navy')
    for i in range(4):
        r=(.11+i*.12)*w
        _arc(c,vx,vy-h*.12,r,h*(i*.12+.09),'forest' if i==0 else 'navy',pi,2*pi)
        for side in (-1,1):
            x=vx+side*r
            c.line(x,vy-h*.12,x,vy+i,'slate' if i%2 else 'navy','|')
    _tracks(c,vx,vy,t)
    c.put(round(vx)-4,vy-2,('.-------.','|  /|\\  |','+-------+'),'forest' if animated>.62 else 'teal')
    for k in range(4):
        x=round(vx+sin(k*1.45+t*.8)*w*.28)
        y=round(vy+h*.08+(k%3)*h*.075)
        c.put(x,y,'.' if k%2 else '+','forest')


def _monorail(c,t):
    w,h=c.w,c.h
    _stars(c,t)
    horizon=round(h*.60)
    _city(c,horizon)
    _tracks(c,w*.52,horizon,t)
    # The front and trailing vestibule skew separately into the elevated rail.
    front=round(w*.83); far=round(w*.20)
    top=round(h*.25); bottom=round(h*.74)
    c.line(far,horizon-2,front-5,top,'slate')
    c.line(far,horizon+3,front+2,bottom,'teal')
    for i in range(6):
        q=i/6
        x=round(far+(front-far)*q)
        y=round(horizon-2+(top-horizon+2)*q)
        b=round(horizon+3+(bottom-horizon-3)*q)
        c.line(x,y,x,b,'navy','|')
        z=max(2,round(w*(.025+q*.068)))
        c.put(x+1,y+1,'[_'+'-'*max(0,z-2)+']','teal')
        if i>2:
            c.put(x+2,y+2,'..','slate')
    c.put(front-6,top-1,(
        ' .------.',r'/.. .. ..\ ','| ._  _. |',r'|   \/   |','|:      :|',r' \======/ ',
    ),'cyan',opaque=True)
    for x in (front-6,front+3):
        c.line(x,top+4,x+(.13*w if x>front else -.09*w),bottom+2,'teal','.')
    for i in range(6):
        xx=(i*17+round(t*33))%w
        c.put(xx,bottom+1+i%3,'.---','navy')


def _hour(c,t):
    w,h=c.w,c.h
    t=min(t,TRANSITION_SECONDS)
    p=t/TRANSITION_SECONDS
    horizon=round(h*.62)
    if p<.47:
        _stars(c,t)
        _city(c,horizon)
        cx,cy=w*.50,h*.37
        rx,ry=w*.144,h*.28
        _arc(c,cx,cy,rx,ry,'slate')
        _arc(c,cx,cy,rx+2,ry+1,'navy',pi*.58,pi*1.55)
        x,y=round(cx),round(cy)
        a=max(0,1-p/.39)*.94
        c.line(cx,cy,cx,cy-ry*.46,'teal','|')
        c.line(cx,cy,cx-rx*.70*sin(a),cy-ry*.74*cos(a),'cyan','|' if p>.36 else None)
        c.put(x,y,'*' if p>.36 else '+','white' if p>.36 else 'teal')
    if p>.34:
        _stairs(c,t,p)
        right=round(w*(-.16+1.31*p))
        pale='teal' if p<.60 else 'forest'
        for j in range(4):
            x=right-j*max(3,w//16)
            c.line(x,0,x+w*.18,h-1,pale,'/' if j%2 else '.')
        for j in range(12):
            y=(j*13+j*j+int(p*13))%h
            x=(j*5+right-round((j%5)*w*.055))%w
            c.put(x,y,'*' if j%3==0 else '.', 'white' if p<.57 and j%3==0 else pale)


def render(art,t,w,h):
    """Return native terminal-cell runs, without headers, controls or state."""
    c=Canvas(w,h)
    if not w or not h:
        return c.finish()
    t=max(0.,float(t))
    if art in ('arrival','finale'):
        _platform(c,t,art=='finale')
    elif art=='awakening':
        _roof(c,t)
    elif art in ('tartarus','thebel'):
        _stairs(c,t)
    elif art in ('dorm','relay','velvet'):
        _desk(c,t,art)
    elif art=='monorail':
        _monorail(c,t)
    elif art=='dark_hour':
        _hour(c,t)
    else:
        raise KeyError(art)
    return c.finish()
