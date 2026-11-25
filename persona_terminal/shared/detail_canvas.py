"""Original illustration rasterizer: pack a 2×4 microgrid into Unicode Braille."""
from math import cos, sin, tau
from .wide_canvas import Canvas

_BITS=(1,2,4,64,8,16,32,128)
_PRECEDENCE={'navy':0,'slate':1,'teal':2,'red':3,'cyan':4,'rose':5,'white':6}


class DotCanvas:
    """Rasterize on a 2×4 microgrid and pack into single-width Braille cells."""

    def __init__(self,w,h):
        self.w=w*2; self.h=h*4
        self.rows=[[None]*self.w for _ in range(self.h)]

    def put(self,x,y,ink):
        if 0<=x<self.w and 0<=y<self.h:self.rows[y][x]=ink

    def line(self,a,b,ink):
        x,y=map(round,a); u,v=map(round,b)
        dx=abs(u-x); dy=-abs(v-y)
        sx=1 if x<u else -1; sy=1 if y<v else -1
        err=dx+dy
        while True:
            self.put(x,y,ink)
            if (x,y)==(u,v):return
            e=2*err
            if e>=dy:err+=dy;x+=sx
            if e<=dx:err+=dx;y+=sy

    def face(self,vertices,ink,density=8,edge=None):
        vertices=tuple((round(x),round(y)) for x,y in vertices)
        if len(vertices)<3:return
        low=max(0,min(y for _,y in vertices)); high=min(self.h,max(y for _,y in vertices)+1)
        segments=list(zip(vertices,vertices[1:]+vertices[:1]))
        for y in range(low,high):
            intersections=sorted(x+(y+.5-a)*(u-x)/(b-a)
                                 for (x,a),(u,b) in segments if min(a,b)<=y+.5<max(a,b))
            for start,end in zip(intersections[::2],intersections[1::2]):
                for x in range(max(0,round(start)),min(self.w,round(end)+1)):
                    self.rows[y][x]=ink if (x*3+y*5)%8<density else None
        if edge:
            for a,b in segments:self.line(a,b,edge)

    def ellipse(self,x,y,rx,ry,ink,density=8,edge=None):
        if rx<=0 or ry<=0:return
        n=max(20,min(128,round(max(rx,ry)*3)))
        self.face(tuple((x+rx*cos(j*tau/n),y+ry*sin(j*tau/n))
                        for j in range(n)),ink,density,edge)

    def path(self,points,ink):
        for a,b in zip(points,points[1:]):self.line(a,b,ink)

    def ring(self,x,y,rx,ry,ink,start=0.,stop=tau,steps=64):
        self.path(tuple((x+rx*cos(start+(stop-start)*j/steps),
                         y+ry*sin(start+(stop-start)*j/steps))
                        for j in range(steps+1)),ink)

    def finish(self):
        return self.pack().finish()

    def pack(self):
        out=Canvas(self.w//2,self.h//4)
        for cy in range(out.h):
            r0,r1,r2,r3=self.rows[cy*4:cy*4+4]
            for x in range(0,self.w,2):
                right=x+1
                microdots=(r0[x],r1[x],r2[x],r3[x],r0[right],r1[right],r2[right],r3[right])
                if microdots==(None,)*8:
                    continue
                mask=0
                pigments={}
                for ink,bit in zip(microdots,_BITS):
                    if ink is not None:
                        mask|=bit
                        pigments[ink]=pigments.get(ink,0)+1
                ink=next(iter(pigments)) if len(pigments)==1 else max(
                    pigments,key=lambda p:(pigments[p],_PRECEDENCE.get(p,0)))
                out.put(x//2,cy,chr(0x2800+mask),ink)
        return out


