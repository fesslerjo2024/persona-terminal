"""Movement-only All-Out reels: no titles, captions, or big portraits.

Royal reference reels: https://www.youtube.com/watch?v=8-tIjvQjXS8 and
https://www.youtube.com/watch?v=ZdVl3MnMqbc. Original character-cell animation.
"""
from math import cos, sin, tau, pi
from wrestling_scene import Canvas, WIDTH, HEIGHT

TITLES = {
    'Joker': 'JOKER // CURTAIN CALL', 'Mona': 'MONA // NINE LIVES',
    'Skull': 'SKULL // THUNDER RUN', 'Panther': 'PANTHER // FLASH POINT',
    'Fox': 'FOX // FINAL BRUSHSTROKE', 'Queen': 'QUEEN // REDLINE',
    'Noir': 'NOIR // AFTERNOON FINALE', 'Crow': 'CROW // CASE CLOSED',
    'Violet': 'VIOLET // STICK THE LANDING',
}
SECS = {'Joker':2.86, 'Mona':2.91, 'Skull':2.70, 'Panther':2.82,
        'Fox':3.19, 'Queen':2.71, 'Noir':3.10, 'Crow':2.95, 'Violet':3.20}
ACCENT = {'Joker':'red','Mona':'cyan','Skull':'gold','Panther':'red','Fox':'cyan',
          'Queen':'white','Noir':'rope','Crow':'red','Violet':'red'}

# Tiny heads anchor the body; hair, silhouette, limbs and props do the acting.
HEAD = {
 'Joker': (' //\\ ',r'([..])'), 'Mona': (r'/\__/\ ',r'(<..>)'),
 'Skull': (' ___^',r'[:":]'), 'Panther': (r'/\=/\ ',r'(>.<)'),
 'Fox': (r'/\_/\ ',r'\^-^/'), 'Queen': (' ____',r'[====]'),
 'Noir': (' _/-','===-=',r'{...}'), 'Crow': (' /==\\',r'<\::/>'),
 'Violet': (' .--\\',r'([..]})'),
}
SPRINTER = {
 'Joker': (r'/\--.',r'/=_>\ ',r'\_\ /',r' /  \ '),
 'Mona': (r'/\_/\ ',r'(<.>)',r' /_\-'),
 'Skull': (r'[::]',r'/==>>',r'_/ \ '),
 'Panther': (r'/\=/\ ',r'>.<\=',r'/\\_\ '),
}
FOE = (r'/\_/\ ',r'[":"]',r'/#=#\ ',r' / \ ')
PETALS = ("<","'",".",";", "*")
SHARDS = ('/','\\','<','>','|','.')
GROUND = 13


def _line(c, a, b, glyph, ink):
    x0,y0=a; x1,y1=b
    n=max(abs(round(x1-x0)),abs(round(y1-y0)),1)
    for i in range(n+1):
        c.put(round(x0+(x1-x0)*i/n),round(y0+(y1-y0)*i/n),glyph,ink)


def _limb(c,a,b,ink,flat='-'):
    dx,dy=b[0]-a[0],b[1]-a[1]
    glyph=flat if abs(dx)>3*abs(dy) else '|' if abs(dy)>=2*abs(dx) else ('\\' if dx*dy>=0 else '/')
    _line(c,a,b,glyph,ink)


def _chain(c,pts,ink,glyph=None):
    for a,b in zip(pts,pts[1:]):
        if glyph:_line(c,a,b,glyph,ink)
        else:_limb(c,a,b,ink)


def _trail(c,x,y,rx,ry,start,sweep,ink,glyph='.',count=14):
    for i in range(count):
        a=start+sweep*i/max(count-1,1)
        c.put(round(x+rx*cos(a)),round(y+ry*sin(a)),glyph,ink)


def _spark(c,x,y,ink,size=1):
    c.put(round(x),round(y),'*',ink)
    if size>1:
        c.put(round(x)-2,round(y),'-',ink)
        c.put(round(x)+2,round(y),'-',ink)
        c.put(round(x),round(y)-1,'|',ink)
        c.put(round(x),round(y)+1,'|',ink)


def _surface(c,p,pattern='.',ink='dim'):
    stride=max(8,len(pattern)+3)
    for x in range(-(int(16*p)%stride),WIDTH,stride):
        c.put(x,GROUND,pattern,ink)
        if (x//stride)%2==0:c.put(x+3,GROUND+1,'.',ink)


def _body(c,who,x,y,steps,hands,*,lean=0,face=1,posture='stand'):
    """Full-body rig with two bent legs and arms; near shapes draw last."""
    x,y=round(x),round(y)
    tint=ACCENT[who]
    short=who=='Mona'
    hip=y+(2 if short else 3)
    hip_x=x-lean
    high=1 if short else 2
    leftfoot,rightfoot=steps
    back,front=hands
    for sign, (dx,lift) in zip((-1,1),(leftfoot,rightfoot)):
        foot=(hip_x+dx, y+(4 if short else 6)-lift)
        knee=(hip_x+round(dx/2)+face*(0 if posture=='stand' else 1),hip+1-round(lift/2))
        _chain(c,((hip_x+sign,hip),knee,foot),'rail' if sign==-1 else 'face')
        c.put(foot[0]-(face==-1),foot[1],'__',tint)
    torso='[==]' if who in ('Queen','Crow') else '/##\\'
    c.put(x-2,y+1,torso,tint)
    c.put(hip_x-1,hip,'==',tint)
    # Far arm lands behind the front line; neither arm is a floating prop.
    for side,(dx,dy) in ((-1,back),(1,front)):
        base=(x+side*2,y+high-1)
        hand=(x+dx,y+dy)
        elbow=(round((base[0]+hand[0])/2),round((base[1]+hand[1])/2)+side)
        _chain(c,(base,elbow,hand),'rail' if side==-1 else tint)
        c.put(round(hand[0]),round(hand[1]),'+' if side==1 else '#',tint)
    rows=HEAD[who]
    c.put(x-2,y-len(rows),rows,'face',opaque=True)
    if who in ('Joker','Crow','Violet'):
        tail=3+abs(lean)
        _chain(c,((x-face*2,y+1),(hip_x-face*tail,hip+1),(hip_x-face*(tail+2),hip+2)),tint,':' if who=='Violet' else '\\')
    if who=='Skull':
        c.put(x-face*4,y,'~~','red')
    if who=='Noir':
        c.put(x-4,y-len(rows)+1,'========','rope')
    if who=='Panther':
        _chain(c,((hip_x-face,hip),(hip_x-face*4,hip-2),(hip_x-face*6,hip-1)),tint,'~')


def _charge(c,p,accent):
    cx,cy=28,7
    for i in range(19):
        angle=i*tau/19
        edge=(round(cx+32*cos(angle)),round(cy+13*sin(angle)))
        r=23-15*p
        inner=(round(cx+r*cos(angle)),round(cy+.36*r*sin(angle)))
        _line(c,edge,inner,SHARDS[(i+int(7*p))%len(SHARDS)],'red' if i%3 else 'rail')
    for i,(who,x,y,dx,dy) in enumerate((
            ('Joker',0,2,22,2), ('Mona',53,1,-22,3),
            ('Skull',3,11,20,-3), ('Panther',52,11,-19,-3))):
        xx=round(x+dx*p); yy=round(y+dy*p+sin(p*tau*2+i)*.7)
        if i%2:_line(c,(min(56,xx+8),yy+2),(min(56,xx+18),yy+2),'-',accent)
        else:_line(c,(max(0,xx-10),yy+2),(max(0,xx-1),yy+2),'-',accent)
        c.put(xx,yy,SPRINTER[who],ACCENT[who],opaque=True)
    if p>.52:
        c.put(26,5,FOE,'dim',opaque=True)
    else:
        for x,y in ((22,7),(28,6),(33,7)):c.put(x,y,FOE,'dim',opaque=True)


def _impact(c,p,accent):
    r=max(1,5+round(22*p))
    for i in range(16):
        a=(i+.21)*tau/16
        origin=(round(28+(r-5)*cos(a)),round(7+.4*(r-5)*sin(a)))
        edge=(round(28+(r+12)*cos(a)),round(7+.5*(r+12)*sin(a)))
        _line(c,origin,edge,SHARDS[i%len(SHARDS)],'white' if i%3==0 else accent)
        if p>.4:
            _spark(c,edge[0],edge[1],'gold' if i%2 else 'red')
    _trail(c,28,7,r,.4*r,pi*.2,tau,'white','*',18)


def _joker(c,p):
    _surface(c,p,'.   .','rail')
    x=15+23*(1-(1-p)**2)
    y=6+sin(pi*p)*1.5
    hx=7-8*p
    for i in range(19):
        a=.1+i*tau/19
        r=8+25*p
        sx=round(25+r*cos(a)); sy=round(7+.45*r*sin(a)+2*p*p*(i%3))
        c.put(sx,sy,SHARDS[i%6],'red' if i%4==0 else 'rail')
    for i in range(4):
        _line(c,(max(0,round(x)-21+i*4),5+i%3),(round(x)-5,round(y)+2),':','red')
    _body(c,'Joker',x,y,((-6,0),(7,1)),((-6,2),(hx,-1+3*p)),lean=3,posture='lunge')
    _line(c,(x+hx,y-1+3*p),(x+hx+5,y-3+3*p),'=','white')
    _spark(c,x+hx+5,y-3+3*p,'red',2)


def _mona(c,p):
    # Film perforations continue scrolling during the cartwheel and paw stamp.
    for y in (1,14):
        ink='rail' if y==1 else 'dim'
        c.put(-round(p*16)%4-4,y,'[]=='*16,ink)
    x=15+25*p
    y=8-5*abs(sin(pi*p))
    form=((r' /\_/\ ',r'(<..>)',r' /_\--'),(r'\_/\ ',r'(<..>)-',' /--\\'),
          ('  /| ',r'(<..>)',r'\_/\/ '), (r'/\__/\ ',r'(>..<)',r'-/ _\ '))
    pose=form[min(3,int(p*4))]
    _trail(c,x-4,y+1,10,4,pi*.65,pi,'cyan','.',13)
    c.put(round(x)-3,round(y),pose,'face',opaque=True)
    c.put(round(x)-4,round(y)+3,' ~~~ ','gold')
    if p>.47:
        pat=(' * * * ','*     *','  ( )  ',' (___) ')
        xx=52-round(12*max(0,p-.62)); yy=4+round(4*max(0,p-.7))
        c.put(xx-3,yy,pat,'red')
        _trail(c,xx,yy+1,5+8*p,3,p*tau,tau*.78,'red','.',12)


def _skull(c,p):
    x=16+15*p
    landing=max(0,1-p*2.2)
    y=7-5*landing
    _surface(c,p,'/!/','gold')
    for j in range(5):
        _line(c,(j*10,12),(10+j*10,11),'.','rail')
    z=sin(pi*p)
    _body(c,'Skull',x,y,((-6,1),(5,0)),((-6,-1),(8,-2-2*z)),lean=1,posture='crouch')
    hx,hy=round(x+8),round(y-2-2*z)
    c.put(hx-1,hy-1,r'| |','gold')
    for i in range(7):
        spread=int((p-.24)*45)
        if spread>0:
            _line(c,(28+spread//2+i,12-i),(30+spread+i*2,11-i*2),'/' if i%2 else '+','gold')


def _panther(c,p):
    x=16+23*p
    y=7-3*abs(sin(tau*p/1.4))
    _surface(c,p,'+   +','rope')
    hand=(x+6,y-1)
    ribbon=[]
    for i in range(20):
        a=i/19
        ribbon.append((hand[0]+18*a,hand[1]+sin(a*tau-p*tau*2)*2.4*a))
    _chain(c,ribbon,'red','~')
    _body(c,'Panther',x,y,((-6,0),(9,round(3*sin(pi*p)))),((-7,2),(6,-1)),lean=2,posture='vault')
    for i in range(5):
        px=round(x+i*5-13*p);py=round(1+(i*3)%8-3*p)
        c.put(px,py,'<>' if i%3==0 else '*','rope' if i%2 else 'red')


def _fox(c,p):
    x=38-16*p
    y=7-2.5*sin(pi*p)
    _surface(c,p,'~   ~','dim')
    for i in range(29):
        a=i/28
        sx=5+49*a
        sy=6+sin(a*tau-2.7*p)*2.4
        if a<.35+.65*p:
            c.put(round(sx),round(sy-3),'~' if i%3 else '.','red')
    dragon=(' /\\_/\\ ',r'<[. .]>',r'  \_/_~~')
    c.put(round(13+12*p),round(1+sin(pi*p)),dragon,'red')
    reach=(round(10*cos(pi*p)), -2+round(5*p))
    _trail(c,x,y-1,15,5,pi*.07+p*pi,pi*.8,'cyan','=',18)
    _body(c,'Fox',x,y,((-7,0),(5,1)),((-4,2),reach),lean=-2,face=-1,posture='lunge')
    _line(c,(x+reach[0],y+reach[1]),(x+reach[0]-10,y+reach[1]-2),'=','white')
    for i in range(6):
        c.put(round((i*13+17*p)%57),round(1+(i*7)%10+2*p),'*','rope')


def _queen(c,p):
    x=15+26*p
    y=7-2*abs(sin(tau*p))
    for y_ in (2,4,10,12):
        for x_ in range((int(p*18)+y_)%7,WIDTH,7):
            c.put(x_,y_,'<>' if y_<7 else '[]','rail')
    _surface(c,p,'==  ==','rail')
    thrust=6+round(5*abs(sin(pi*p)))
    for i in range(5):
        _line(c,(x-21+i*3,y+i-3),(x-4+i,y+i-3),'-','rail')
    _body(c,'Queen',x,y,((-10,1),(8,1)),((-4,3),(thrust,0)),lean=4,posture='lunge')
    for i in range(4):
        _spark(c,x+thrust+2+i*3,y+(i%3)-1,'red' if i%2 else 'white',1+(i%2))


def _noir(c,p):
    x=27+5*sin(pi*p)
    y=7-2*abs(sin(pi*p))
    _surface(c,p,'.   .','rope')
    _trail(c,28,7,25,6,p*.3,tau,'rope','.',37)
    for i in range(6):
        xx=(i*11+6+int(p*7))%57
        yy=(i*5+int(p*12))%13
        c.put(xx,yy,(" .*. ","*+*+*"," \\|/"),'rope')
    throw=sin(pi*p)
    hx=round(10*throw)
    step=round(5*cos(tau*p))
    _body(c,'Noir',x,y,((-4-step,0),(6-step,1)),((-6,1),(6,-1)),lean=1 if p<.5 else -1)
    cupx=round(x+6+hx); cupy=round(y-2-5*throw)
    c.put(cupx,cupy,(' ___ ',r'\___/)'," === "),'cyan')
    _trail(c,cupx-2,cupy+3,5,3,1.2,3,'white','.',10)


def _crow(c,p):
    for y in (2,12):
        snap=round(15*p)
        for x in range(0,WIDTH-2,3):
            if abs(x-28)<snap:continue
            yy=round(y+(x-28)*(.08 if y==2 else -.07))
            c.put(x,yy,'-=','red')
            c.put(x+1,yy-1,'/' if (x//3)%2 else '\\','rail')
    x=14+25*(1-(1-p)**1.3)
    y=8-4*sin(pi*p)
    swing=.2+p*tau*.62
    hand=(round(cos(swing)*10),round(sin(swing)*5))
    _trail(c,x,y,16,7,swing-.7,2.1,'red','/',24)
    _body(c,'Crow',x,y,((-8,1),(8,0)),((-6,0),hand),lean=3,posture='lunge')
    _line(c,(x+hand[0],y+hand[1]),(x+hand[0]+cos(swing)*6,y+hand[1]+sin(swing)*3),'=','white')


def _violet(c,p):
    x=20+16*p
    y=7-3*abs(sin(p*tau))
    turn=sin(p*tau)
    lunge=sin(pi*p)
    _surface(c,p,' .  . ','rope')
    for i in range(20):
        a=i*tau/20+p*tau*.72
        rx=7+(i%4)*4+6*p
        ry=3+(i%3)
        px=round(x+rx*cos(a)); py=round(5+ry*sin(a)+4*p*p)
        c.put(px,py,PETALS[i%len(PETALS)],'red' if i%3 else 'rope')
    hand=(round(9*cos(pi*p)),round(-4*lunge))
    _body(c,'Violet',x,y,((-5-round(turn*6),round(max(0,turn)*4)),
                         (6-round(turn*7),round(max(0,-turn)*3))),
          ((-5+round(4*turn),-1),hand),lean=round(2*turn),face=1 if p<.5 else -1)
    _line(c,(x+hand[0],y+hand[1]),(x+hand[0]+5,y+hand[1]-1),'=','white')
    _spark(c,x+hand[0]+5,y+hand[1]-1,'red',2)


FINISH = {'Joker':_joker,'Mona':_mona,'Skull':_skull,'Panther':_panther,'Fox':_fox,
          'Queen':_queen,'Noir':_noir,'Crow':_crow,'Violet':_violet}


def _render(who,t):
    c=Canvas()
    t=max(0,min(t,SECS[who]))
    if t<.53:
        _charge(c,t/.53,ACCENT[who])
    elif t<.84:
        _impact(c,(t-.53)/.31,ACCENT[who])
    else:
        FINISH[who](c,(t-.84)/(SECS[who]-.84))
    return '',c.finish()


def _scene(who):
    return lambda elapsed: _render(who,elapsed)


SCENES={TITLES[who]:(SECS[who],_scene(who)) for who in TITLES}
