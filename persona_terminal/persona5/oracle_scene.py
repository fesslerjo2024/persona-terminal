"""Oracle's original ASCII effects, from the Royal UFO/assist visual motifs.

References: https://p-ch.jp/news/3885/
and https://www.youtube.com/watch?v=W3J4rSjfgeE .
"""
from math import cos, sin, tau

from .wrestling_scene import Canvas, WIDTH

TITLE = 'ORACLE // UFO PAYLOAD'
SUPPORT = 'ORACLE // MORAL SUPPORT'
GUARD = 'ORACLE // FINAL GUARD'
SECONDS = 3.25

UFO = (
    '          .---------.',
    '       .-"  _/\\_/\\_  "-.',
    '   ___/   .-----------.  \\___',
    '_=/___/_____<*>_____\\___\\___\\=_',
    '<__o__o__o__[=====]__o__o__o__>',
    '   "\\________|===|_________/"',
    '             "\\_/"',
)
BOMB = ('  ,*', ' _/ ', '/  \\', '\\__/')
ALLY = ('  /\\ ', ' [..]', ' /##\\', '  || ', ' /  \\')
CROUCH = ('      ', ' [..] ', ' /##\\_', '/   \\_')
SHADOW = (' /\\_/\\ ', '( . . )',' /###\\ ', '/_/ \\_\\')
ALLIES = (10,23,36)
FLECKS = ('*','.','+')


def _sky(c,t):
    for i in range(20):
        x=(i*17+int(t*12)*(-1 if i%3 else 1))%WIDTH
        c.put(x,(i*31)%14,'.','dim')
    c.put(2,13,'_'*53,'dim')
    c.put(3,14,'- '*26,'dim')


def _circle(c,x,y,r,t,ink,amount=26):
    for i in range(amount):
        a=tau*i/amount+t
        c.put(x+round(cos(a)*r),y+round(sin(a)*r*.35),
              FLECKS[i%3],ink)


def _blast(c,x,y,f,inks=('gold','red','white')):
    for i in range(27):
        a=tau*i/27
        r=1+f*(6+i%7)
        c.put(x+round(cos(a)*r),y+round(sin(a)*r*.48),
              FLECKS[(i+int(f*8))%3],inks[i%3])
    if f<.4:
        c.put(x-2,y,('<-*->',' /|\\ '),'white')


def render(elapsed):
    c,t=Canvas(),max(0,elapsed)
    _sky(c,t)
    x=round(1+min(1,t/.88)*13+max(0,t-2.24)*34)
    if 1.67 <= t < 2.54:
        k=(t-1.67)/.87
        _blast(c,29,11,k)
        for j in range(19):
            c.put(29+round((j-9)*k*2),12-round((j%7)*k),'.','dim')
        if t>2.03:
            c.put(34+round(5*k),12,'.. .','dim')
    elif t<1.67:
        c.put(26,8,SHADOW,'foe',opaque=True)
        if t>.80:
            frac=(t-.80)/.87
            c.put(27,4+round(frac**1.65*6),BOMB,'gold',opaque=True)
        for j in range(3):
            radius=10+j*2+round(t*3)
            c.put(29-radius,7+j,'/','cyan')
            c.put(29+radius,7+j,'\\','cyan')
    else:
        for i in range(15):
            c.put(15+i*2,9+(i%4),'.','dim')
    c.put(x,max(-6,1-round(max(0,t-2.2)*6)),UFO,'green',opaque=True)
    return ('UFO flyover' if t<.8 else 'payload' if t<1.67 else
            'blast' if t<2.54 else 'depart'),c.finish()


def support(elapsed):
    c,t=Canvas(),max(0,elapsed)
    _sky(c,t)
    c.put(13,-3+min(3,int(t*7)),UFO,'green',opaque=True)
    for i,x in enumerate(ALLIES):
        delay=.48+i*.11
        f=max(0,t-delay)
        beat=(f*2.4)%1
        # The relay fans outward; the recovered fighters visibly stand up.
        if t>delay and t<2.38:
            for j in range(1,7):
                dest=round(28+(x+2-28)*j/6)
                c.put(dest,4+j,'.' if (j+int(t*22))%3 else '+','cyan')
            for j in range(4):
                c.put(x+j*2-1,10-round(beat*4)-(j%2),FLECKS[j%3],'green')
            _circle(c,x+2,10,2+beat*4,t,'green',15)
        c.put(x,9,CROUCH if t<delay+.56 else ALLY,'face',opaque=True)
        if delay+.62<t<delay+1.28:
            c.put(x+2,7-round((f-.62)*2),'+','green')
    return ('relay' if t<.55 else 'transfer' if t<1.32 else 'rally'),c.finish()


def guard(elapsed):
    c,t=Canvas(),max(0,elapsed)
    _sky(c,t)
    for i,x in enumerate((11,19,27)):
        c.put(x,8,ALLY,'face',opaque=True)
    c.put(3+int(min(.7,t)*9),-4,UFO,'green',opaque=True)
    if t<1.13:
        x=52-round(t*15)
        c.put(x,8,('<##===>',r'   \\==='),'red',opaque=True)
        c.put(x+2,9,'======','gold')
    if .42<t<2.5:
        # An arc drops around the squad. At contact a ripple travels along it.
        f=min(1,(t-.42)/.52)
        for i in range(32):
            a=tau*i/32
            ry=11+round(sin(a)*7*f)
            rx=21+round(cos(a)*16*f)
            if ry<13:
                pulse=1.13<t<1.66 and abs(ry-(8-round((t-1.13)*8)))<2
                c.put(rx,ry,'#' if pulse else ':' if i%2 else '+',
                      'white' if pulse else 'cyan')
    if 1.12<=t<2.04:
        _blast(c,36,8,(t-1.12)/.92,('gold','cyan','white'))
    if t>2.14:
        _circle(c,22,9,max(1,15*(2.85-t)/.71),t,'green',21)
    return ('incoming' if t<.42 else 'shield' if t<1.12 else
            'deflect' if t<2.04 else 'clear'),c.finish()


SCENES = {TITLE:(SECONDS,render), SUPPORT:(2.85,support), GUARD:(2.90,guard)}
