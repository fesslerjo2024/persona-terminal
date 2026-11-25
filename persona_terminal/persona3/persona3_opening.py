"""Original opening beats and native art for Persona 3 Terminal's spring demo."""
from dataclasses import dataclass
from math import cos, pi, sin
from types import MappingProxyType

from ..shared.wide_canvas import Canvas

TRANSITION_SECONDS = 2.68
STILL_SECONDS = 1.45
_STRIKE_AT = 1.80
_FREEZE_AT = 1.98


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
        'The dorm goes dark. A creature follows you and Yukari onto the roof.',
        'Yukari drops her Evoker, a gun-shaped device. You pick it up and hear a voice: “Orpheus.”',
        'Orpheus is your Persona. Call on him to protect Yukari from the Shadows.',
    ), 'awakening'),
    Beat('briefing', '04/20', 'THE HOUR BETWEEN DAYS', (
        'Mitsuru explains: the Dark Hour begins at midnight. Most people turn into coffins and never remember it. The creatures that hunt here are Shadows.',
        'Ikutsuki, the adviser to S.E.E.S., asks you to join. Mitsuru and the others investigate the Dark Hour and fight the Shadows.',
    ), 'dorm'),
    Beat('tartarus', '04/20', 'THE FIRST CLIMB', (
        'During the Dark Hour, your school turns into a tower called Tartarus. Mitsuru takes the radio.',
        'Mitsuru: “Tonight we’re mapping the first floor. Makoto, take Yukari and Junpei. Get the route down and come back together.”',
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


# Original three-row segment font for the foreground readouts.
_SEGMENTS = {
    '0': (' __ ', '|  |', '|__|'),
    '1': ('  /|', '   |', '   |'),
    '2': (' __ ', ' __|', '|__ '),
    '3': (' __ ', ' __|', ' __|'),
    '4': ('    ', '|__|', '   |'),
    '5': (' __ ', '|__ ', ' __|'),
    '6': (' __ ', '|__ ', '|__|'),
    '7': (' __ ', '  / ', ' /  '),
    '8': (' __ ', '|__|', '|__|'),
    '9': (' __ ', '|__|', ' __|'),
    ':': (' ', '*', '*'),
}


def _clock_point(cx,cy,angle,u,v):
    # Rotate in screen space, accounting for the aspect of terminal cells.
    return (cx+cos(angle)*u-1.9*sin(angle)*v,
            cy+sin(angle)*u/1.9+cos(angle)*v)


def _clock_arc(c,point,rx,ry,ink):
    n=max(24,int(rx*8))
    for i in range(n):
        a=i*2*pi/n
        x,y=point(rx*cos(a),ry*sin(a))
        xx,yy=point(rx*cos(a+.01),ry*sin(a+.01))
        dx,dy=xx-x,yy-y
        glyph='-' if abs(dy)<abs(dx)*.29 else '|' if abs(dx)<abs(dy)*1.30 else '/' if dx*dy<0 else '\\'
        c.put(round(x),round(y),glyph,ink)


def _digit_clock(c,cx,cy,angle,scale,label,ink):
    # Output remains native cells, with a tighter fall-back as the shot begins.
    if scale<.76:
        c.put(round(cx)-len(label)//2,round(cy),label,ink)
        return
    shapes=tuple(_SEGMENTS[s] for s in label)
    width=sum(len(s[0])+1 for s in shapes)-1
    rows=tuple(' '.join(shape[i] for shape in shapes) for i in range(3))
    for i,row in enumerate(rows):
        for j,ch in enumerate(row):
            if ch==' ':
                continue
            x,y=_clock_point(cx,cy,angle,(j-width/2)*scale,(i-1)*scale)
            c.put(round(x),round(y),ch,ink)
            if scale>1.2:
                c.put(round(x)+1,round(y),ch,ink)


def _analog(c,cx,cy,rx,ry,angle,second,ink,dim,roman=False):
    def point(u,v):
        return _clock_point(cx,cy,angle,u,v)

    if roman:
        # A matte face occludes the overlapping clocks inside the bezel only.
        yn=max(0,round(cy-ry*1.33)); yx=min(c.h,round(cy+ry*1.33)+1)
        xn=max(0,round(cx-rx*1.33)); xx=min(c.w,round(cx+rx*1.33)+1)
        for y in range(yn,yx):
            for x in range(xn,xx):
                u,v=_clock_point(0,0,-angle,x-cx,y-cy)
                if (u/rx)**2+(v/ry)**2<.91:
                    c.put(x,y,' ',dim,opaque=True)
    _clock_arc(c,point,rx,ry,ink)
    if roman:
        _clock_arc(c,point,max(1,rx-2.8),max(1,ry-1.43),dim)
    names=('XII','I','II','III','IV','V','VI','VII','VIII','IX','X','XI')
    for i in range(12):
        a=(i/6-.5)*pi
        x,y=point(rx*.86*cos(a),ry*.86*sin(a))
        if roman and rx>9 and ry>5 and (i%3==0 or rx>15):
            name=names[i]
            c.put(round(x)-len(name)//2,round(y),name,ink if i%3==0 else dim,opaque=True)
        else:
            c.put(round(x),round(y),'.' if i%3 else '+',dim)
    x0,y0=point(0,0)
    # Both hands converge on twelve. The thin second hand travels exactly
    # the last four seconds in lockstep with the digital surround.
    for length,offset,ch in ((.40, -.018 if second else 0.,'|'),
                             (.62,(-.105*(60-second)/4) if second else 0.,'|')):
        x,y=point(rx*length*sin(offset),-ry*length*cos(offset))
        c.line(x0,y0,x,y,ink,ch)
        if roman and length>.5 and rx>9:
            # A spear tip and long two-cell spine distinguish the main hands.
            c.put(round(x),round(y),'^',ink)
            c.line(x0,y0,x,y+1,ink,'|')
    if second:
        a=(second-60)*pi/30
        x,y=point(rx*.74*sin(a),-ry*.74*cos(a))
        c.line(x0,y0,x,y,dim,'.')
    c.put(round(x0),round(y0),'*' if roman else '+',ink)


def _hour(c,t):
    """Reload-like clock montage: rush in, count down, stop on the green frame."""
    frozen=t>=_FREEZE_AT
    progress=min(1.,t/1.13)
    pull=progress*progress*(3-2*progress)
    camera=.18+.82*pull
    w,h=c.w,c.h
    mid=w*.47; level=h*.49
    midnight=t>=_STRIKE_AT
    second=0 if midnight else 56+min(3,int(t/_STRIKE_AT*4))
    if frozen:
        ink,shade,back='green','forest','forest'
    elif t>.60:
        ink,shade,back='white','dim','slate'
    else:
        ink,shade,back='dim','dim','dim'

    def place(x,y):
        return mid+(w*x-mid)*camera,level+(h*y-level)*camera

    # Angled neighboring timepieces and different layers of digital readouts
    # follow the same camera, not an in-world skyline or a loading transition.
    for x,y,rx,ry,angle in ((.18,.26,.112,.23,-.21),(.85,.14,.138,.24,.25),
                            (.85,.86,.153,.23,-.31)):
        cx,cy=place(x,y)
        _analog(c,cx,cy,max(1.4,w*rx*camera),max(1.3,h*ry*camera),
                angle,second,back,back)

    for x,y,angle,zoom,is_24 in (
        (.065,.44,.04,1.10,False),(.86,.39,-.24,.71,True),
        (.89,.55,.06,.95,True),(.24,.74,-.31,.69,False),
        (.78,.82,-.10,1.43,False),(.65,.13,-.30,.66,True),
    ):
        if midnight:
            label='00:00' if is_24 else '0000'
        else:
            label='23:59' if is_24 else '1159'
        cx,cy=place(x,y)
        _digit_clock(c,cx,cy,angle,zoom*camera,label,shade if zoom<.8 else ink)

    cx,cy=place(.27,.91)
    _digit_clock(c,cx,cy,-.19,.81*camera,
                 '00:00:00' if midnight else f'11:59:{second:02}',ink)
    cx,cy=place(.474,.53)
    _analog(c,cx,cy,max(2,w*.235*camera),max(2,h*.39*camera),
            .23,second,ink,shade,roman=True)


def render(art,t,w,h):
    """Return native terminal-cell runs, without headers, controls or state."""
    c=Canvas(w,h)
    if not w or not h:
        return c.finish()
    t=max(0.,float(t))
    if art=='dark_hour':
        _hour(c,min(t,TRANSITION_SECONDS))
        return c.finish()
    if art in ('tartarus','thebel'):
        from .persona3_environment_reels import tartarus
        return tartarus(min(t,STILL_SECONDS),w,h)
    t=min(t,STILL_SECONDS)
    from .persona3_scenic_detail import lounge, monorail_plate, platform, roof
    if art in ('arrival','finale'):
        return platform(t,w,h,art=='finale')
    if art=='awakening':
        return roof(t,w,h)
    if art in ('dorm','relay','velvet'):
        return lounge(t,w,h,art)
    if art=='monorail':
        return monorail_plate(t,w,h)
    raise KeyError(art)
