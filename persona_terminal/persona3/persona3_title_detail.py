"""A midnight waterfront, lunar shift, and emergent Tartarus for the title."""
from math import cos, pi, sin, sqrt
from ..shared.detail_canvas import DotCanvas


def _ease(x):
    x=max(0.,min(x,1.))
    return x*x*(3-2*x)


def render(t,w,h):
    c=DotCanvas(w,h)
    if not w or not h:return c.finish()
    W,H=c.w,c.h
    turn=_ease((t-.83)/1.16)
    leave=_ease((t-1.44)/1.42)
    shore=round(H*.77)
    x0,y0=W*.72,H*.33
    for j in range(52):
        x=(j*79+j*j*11)%W
        y=(j*41+j*j*3)%max(1,shore)
        c.put(x,y,'teal' if (j+round(t*5))%11==0 else 'navy')
    rx,ry= W*(.081+.049*turn),H*(.154+.054*turn)
    moon='forest' if turn>.42 else 'navy'
    c.ellipse(x0,y0,rx,ry,moon,3,'teal' if turn>.42 else 'slate')
    for dx,dy,s in ((-.48,-.22,.18),(.19,-.36,.22),(.45,.11,.15),(-.26,.48,.20),(-.03,.06,.13)):
        c.ellipse(x0+dx*rx,y0+dy*ry,s*rx,s*ry,'teal' if turn>.5 else 'slate',2)
    for j in range(-1,W//8+2):
        x=j*8
        y=shore-5-(j*j*37+j*11)%max(3,H//9)
        bw=6+j%5
        c.face(((x,shore),(x,y),(x+bw,y),(x+bw,shore)), 'navy',5,'slate')
        if j%3==1:
            c.line((x+2,y),(x+2,y-4),'navy')
        for m in range(y+3,shore,4):
            if (j+m)%3!=0:c.put(x+3,m,'teal')
    c.line((0,shore),(W-1,shore),'teal')
    for j in range(28):
        y=shore+2+(j*j+7*j)%max(1,H-shore-2)
        x=(j*77+j*j*13+round(t*7))%W
        color='forest' if turn>.4 and x>W*.5 else 'navy'
        c.line((x,y),(x+3+(j*7)%14,y),color)
    # Tower wedges occlude the moon, instead of being drawn on top of the
    # waterfront as outlines. Stacked slits and a broken crown mark the rise.
    if turn>.02:
        base=W*.815
        tower_h=H*.65*turn
        def tower(x,y):return (base+x*W*.15,shore-y*tower_h)
        def plane(p,ink,d=8,edge=None):
            c.face(tuple(tower(x,y) for x,y in p),ink,d,edge)
        plane(((-.51,0),(-.38,.13),(-.3,.31),(-.37,.37),(-.22,.47),(-.27,.55),(-.12,.65),
               (-.18,.78),(-.06,.83),(-.07,.92),(.045,1.02),(.15,.92),(.13,.82),
               (.28,.79),(.21,.64),(.4,.53),(.31,.42),(.43,.29),(.52,.19),(.55,0)),None)
        plane(((-.51,0),(-.28,.44),(-.12,.65),(-.18,.78),(-.06,.83),(.045,1.02),
               (.02,.82),(.05,.51),(.04,.29),(.2,0)), 'navy',5,'slate')
        plane(((.20,0),(.04,.29),(.05,.51),(.02,.82),(.045,1.02),(.13,.82),
               (.28,.79),(.21,.64),(.4,.53),(.31,.42),(.55,0)), 'teal',3,'navy')
        for k in range(11):
            y=.06+.071*k
            c.line(tower((-.44+.035*k),y),tower((.46-.029*k),y+.01),'slate')
            if k%3!=2:c.line(tower((.25-.012*k),y+.012),tower((.25-.012*k),y+.040),'teal')
        if turn>.7:
            c.ring(*tower(.045,1.02),W*.025,H*.045,'forest')
            c.put(*map(round,tower(.045,1.02)),'white')
    # Large oblique face. The top arc catches the light before the city turns.
    cx,cy=W*(.352-.076*leave),H*(.443-.028*leave)
    rx,ry=W*(.228-.036*leave),H*(.331-.017*leave)
    def clock(a,d):return (cx+rx*cos(a)*d,cy+ry*sin(a)*d)
    if leave<.92:
        c.ellipse(cx,cy,rx*.93,ry*.93,None)
        c.ellipse(cx,cy,rx*.91,ry*.91,'navy',2)
    c.ring(cx,cy,rx*1.07,ry*1.07,'navy')
    c.ring(cx,cy,rx,ry,'slate' if leave>.80 else 'teal')
    c.ring(cx,cy,rx*.92,ry*.92,'navy')
    c.ring(cx,cy,rx*1.07,ry*1.07,'white' if .84<t<1.03 else 'teal',
           -2.85+turn*.50,-2.17+turn*.68,25)
    for k in range(60):
        a=pi*(k/30-.5)
        c.line(clock(a,.76 if k%5==0 else .865),clock(a,.90),
               'teal' if k%5==0 and leave<.92 else 'slate')
    if leave<.93:
        p=_ease(t/.87)
        for n,l,ink in ((-1.48,.72,'cyan'),(-.42,.48,'slate')):
            a=n*(1-p)-pi/2
            c.face((clock(a,l),clock(a+.19,.20),(cx+1,cy+3),
                    clock(a-.19,.20)),ink,8,'teal')
        c.ellipse(cx,cy,3,4,'teal',7,'white')
    if .87<t<1.58:
        p=(t-.87)/.71
        for k in range(32):
            a=pi*k/16
            d=1+p*.95
            c.line(clock(a,d),clock(a,d+.045),'white' if p<.16 else 'teal' if p<.6 else 'navy')
    out=c.pack()
    if leave<.75:
        for a,mark in ((-pi/2,'12'),(0,'3'),(pi/2,'6'),(pi,'9')):
            x,y=clock(a,.66)
            out.put(round(x/2)-len(mark)//2,round(y/4),mark,'white' if mark=='12' else 'teal')
    return out.finish()
