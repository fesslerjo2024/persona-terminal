"""Small moon and rescue-radio illustrations; not new HUD elements."""
from math import pi, sin
from detail_canvas import DotCanvas


def render(scene,t,w,h):
    c=DotCanvas(w,h)
    if not w or not h:return c.finish()
    W,H=c.w,c.h
    if scene=='calendar':
        x,y=W*.78,H*.46
        rx,ry=W*.10,H*.38
        c.ellipse(x,y,rx,ry,'slate',4,'slate')
        c.ellipse(x+rx*.40,y-ry*.15,rx*.92,ry*.87,None)
        for j in range(W//3):
            a=(j*41+j*j*23)%W
            b=(j*23+int(t*2))%max(1,H-3)
            if a>=W*.58 and abs(a-x)>rx*1.1:c.put(a,b,'navy')
        for j in range(8):
            a=W*(.57+j*.05)
            c.line((a,H*.90),(a+W*.025,H*.90),'navy')
    elif scene in ('briefing','signal'):
        # No radar. A short oscillogram escapes a canted handheld radio.
        def q(x,y):return W*(.74+.125*x),H*(.55+.45*y)
        def plane(v,ink,density=8,edge=None):
            c.face(tuple(q(x,y) for x,y in v),ink,density,edge)
        plane(((-.30,-.62),(.09,-.71),(.46,.48),(.32,.77),(-.05,.77),
               (-.36,-.37)),'navy',5,'slate')
        plane(((-.25,-.39),(.04,-.48),(.12,-.13),(-.17,-.01)),'teal',3,'slate')
        c.path(tuple(q(x,y) for x,y in ((-.30,-.58),(-.44,-.96),(-.45,-.99))),'teal')
        for i in range(4):
            c.line(q(-.10,.13+i*.11),q(.18,.05+i*.11),'teal' if i==1 else 'slate')
        for s in (-1,1):
            pts=[]
            for i in range(42):
                p=i/41
                x=W*(.43+.19*p) if s==-1 else W*(.81+.15*p)
                amp=(sin(p*pi)**2)*H*.22
                y=H*.54+amp*sin(t*7+7*pi*p)
                pts.append((x,y))
            c.path(pts,'teal' if s==-1 else 'slate')
    else:
        raise KeyError(scene)
    return c.finish()
