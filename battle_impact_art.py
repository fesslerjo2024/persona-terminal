"""Silhouette-free ink burst when a battle cue has no dedicated reel."""
from math import cos, sin, tau
from detail_canvas import DotCanvas


def draw_impact(elapsed,width,height):
    c=DotCanvas(width,height)
    if not c.w or not c.h:
        return c.finish()
    x,y=c.w*.5,c.h*.49
    p=max(0.,min(1.,elapsed/.7))
    push=1-(1-p)**2
    # Sparse ink fragments hit a bright seam; the falloff leaves black space
    # around the action instead of flashing the full terminal.
    for i in range(33):
        a=i*tau/33
        dx,dy=cos(a)*c.w*.43,sin(a)*c.h*.42
        r=.24+.61*push
        f=.04+(i*13%19)/96
        tail=r+f
        ink=('wine','red','rose','amber')[i%4]
        if i%3:
            c.line((x+dx*r,y+dy*r),(x+dx*tail,y+dy*tail),ink)
        else:
            c.face(((x+dx*r+2*sin(a),y+dy*r-2*cos(a)),
                    (x+dx*r-2*sin(a),y+dy*r+2*cos(a)),
                    (x+dx*tail,y+dy*tail)),ink,6)
    radius=.17+.15*push
    for side in (-1,1):
        dx,dy=c.w*radius*side,c.h*radius*side
        c.face(((x-dx*.94,y+dy), (x+dx,y-dy), (x+dx*.44,y-dy*.07),
                (x+dx*.85,y-dy*.54),(x-dx*.62,y+dy*1.34)),
               'red' if p>.25 else 'white',6,'rose')
    c.ring(x,y,c.w*(.11+.13*push),c.h*(.06+.13*push),'wine',.29,4.95)
    return c.finish()
