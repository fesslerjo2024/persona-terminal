"""Packed dot geometry for Palace Map art, separate from interactive text."""
from math import cos, pi, sin

from battle_ui import CYAN, DIM, GOLD, GREEN, RED, WHITE
from detail_canvas import DotCanvas
from reel_palette import IDS

INK = {'cyan': CYAN, 'dim': DIM, 'gold': GOLD, 'green': GREEN,
       'red': RED, 'white': WHITE, **IDS}
TOP = 6
MARKS = {'clear':'✓','open':'◆','locked':'▣'}


def clamp(value):
    return max(0,min(value,1))


def smooth(value):
    q=clamp(value)
    return q*q*(3-2*q)


def volume(app):
    return app.h-13


def seed(j):
    return ((j*25173+13849)&65535)/65536


def place(app,x,y,s,ink='white',bold=False,reverse=False):
    limit=app.w-2
    if s and TOP<=y<=app.h-8 and x<limit:
        if x<0:s=s[-x:];x=0
        app.put(y,x,s[:limit-x],INK[ink],bold,reverse)


def caption(row,i,width):
    mark=MARKS[row.status]
    prefix=f'{"▶" if row.selected else " "} {i+1:02} {mark} '
    grade=f' [{row.medal}]' if row.medal else ''
    if len(prefix+row.title+grade)>width:grade=''
    room=max(1,width-len(prefix+grade))
    name=row.title if len(row.title)<=room else row.title[:room-1]+'…'
    return prefix+name+grade


def row_ink(row,accent='amber'):
    return 'dim' if row.status=='locked' else accent if row.selected else (
        'green' if row.status=='clear' else 'white')


def positions(view,start,end):
    return tuple(round(start+(end-start)*i/max(1,len(view.rows)-1)) for i in range(len(view.rows)))


class Art:
    """Render geometric plans in abstract 100 × 60 coordinates."""
    def __init__(self,width,height):
        self.w=width;self.h=height
        self.c=DotCanvas(width,height)
        self.sx=(self.c.w-1)/100
        self.sy=(self.c.h-1)/60

    def xy(self,p):
        return p[0]*self.sx,p[1]*self.sy
    def point(self,x,y,ink):
        x,y=self.xy((x,y));self.c.put(round(x),round(y),ink)
    def line(self,ink,*p):
        self.c.path(tuple(map(self.xy,p)),ink)
    def shape(self,ink,*p,edge=None,grain=8):
        self.c.face(tuple(map(self.xy,p)),ink,grain,edge)
    def box(self,x,y,X,Y,ink,edge=None,grain=8):
        self.shape(ink,(x,y),(X,y),(X,Y),(x,Y),edge=edge,grain=grain)
    def oval(self,x,y,rx,ry,ink,edge=None,grain=8):
        self.c.ellipse(*self.xy((x,y)),rx*self.sx,ry*self.sy,ink,grain,edge)
    def ring(self,x,y,rx,ry,ink,a=0,b=2*pi):
        self.c.ring(*self.xy((x,y)),rx*self.sx,ry*self.sy,ink,a,b,steps=44)
    def arch(self,x,y,width,height,ink):
        self.line(ink,(x-width,y+height*.95),(x-width,y))
        self.ring(x,y,width,height,ink,pi,2*pi)
        self.line(ink,(x+width,y),(x+width,y+height*.95))
    def line_at(self,color,x,y,length):
        self.line(color,(x,y),(x+length,y))
    def paint(self,app,x,y):
        paint(app,x,y,self.c.finish())


def paint(app,x,y,rows):
    for iy,row in enumerate(rows,y):
        px=x
        for s,ink in row:
            if s.strip():
                place(app,px,iy,s,ink)
            px+=len(s)


def fixture(s,x,y,size,ink='slate',inner='ink'):
    s.oval(x,y,size,size*1.12,ink)
    s.oval(x,y,size*.61,size*.65,inner)
    s.point(x-size*.4,y-size*.41,'white' if ink=='amber' else 'slate')
