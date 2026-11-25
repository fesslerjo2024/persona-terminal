"""Normalized staging tools for Persona 3's original microdot illustrations."""
from math import cos, sin, tau
from ..shared.detail_canvas import DotCanvas


def unit(t,a,b):
    return max(0.,min(1.,(t-a)/(b-a)))


def ease(t):
    return t*t*(3-2*t)


class Stage:
    """Coordinates in a 100 × 100 viewbox; shapes fill physical dot cells."""
    def __init__(self,w,h):
        self.c=DotCanvas(w,h)
        self.w=max(1,self.c.w-1);self.h=max(1,self.c.h-1)

    def p(self,x,y):return x*self.w*.01,y*self.h*.01

    def path(self,points,ink):
        self.c.path(tuple(self.p(*q) for q in points),ink)

    def shape(self,points,ink,density=7,edge=None):
        self.c.face(tuple(self.p(*q) for q in points),ink,density,edge)

    def rect(self,x,y,w,h,ink,density=7,edge=None):
        self.shape(((x,y),(x+w,y),(x+w,y+h),(x,y+h)),ink,density,edge)

    def disc(self,x,y,rx,ry,ink,density=8,edge=None):
        self.c.ellipse(*self.p(x,y),*self.p(rx,ry),ink,density,edge)

    def ring(self,x,y,rx,ry,ink,a=0,b=tau):
        self.c.ring(*self.p(x,y),*self.p(rx,ry),ink,a,b)

    def pt(self,x,y,ink):
        a,b=self.p(x,y);self.c.put(round(a),round(b),ink)

    def burst(self,x,y,r,ry,ink):
        self.path(((x-r,y),(x+r,y)),ink)
        self.path(((x,y-ry),(x,y+ry)),ink)

    def particles(self,t,ink='navy',n=140,*,speed=4,region=(0,0,100,100)):
        left,top,w,h=region
        for i in range(n):
            x=((i*37+i*i*13)%997/997+t*speed*.014*((i%4)+1))%1
            y=((i*347+i*i*51)%1021/1021-t*speed*.010*((i%3)+1))%1
            self.pt(left+x*w,top+y*h,ink)
