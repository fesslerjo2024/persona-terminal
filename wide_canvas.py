"""Clipped terminal-cell canvas. The art uses physical columns, never zoomed text."""
from itertools import groupby


class Canvas:
    def __init__(self,width,height):
        self.w,self.h=width,height
        self._data=[[(' ','dim')]*width for _ in range(height)]

    def put(self,x,y,rows,ink,opaque=False):
        if isinstance(rows,str):
            rows=(rows,)
        for j,row in enumerate(rows,y):
            if 0<=j<self.h:
                start,stop=max(0,-x),min(len(row),self.w-x)
                if start<stop:
                    dst=self._data[j]
                    if opaque:
                        dst[x+start:x+stop]=[(ch,ink) for ch in row[start:stop]]
                    else:
                        for i in range(start,stop):
                            if row[i]!=' ':
                                dst[x+i]=(row[i],ink)

    def line(self,x0,y0,x1,y1,ink,ch=None):
        """Integer line with an ASCII chord glyph chosen by slope by default."""
        x0,y0,x1,y1=map(round,(x0,y0,x1,y1))
        dx,dy=abs(x1-x0),abs(y1-y0)
        sx=1 if x0<x1 else -1
        sy=1 if y0<y1 else -1
        if ch is None:
            ch='-' if dx>3*dy else '|' if dy>3*dx else '\\' if sx==sy else '/'
        err=dx-dy
        while True:
            self.put(x0,y0,ch,ink)
            if x0==x1 and y0==y1:break
            e=2*err
            if e>-dy:err-=dy;x0+=sx
            if e<dx:err+=dx;y0+=sy

    def overlay(self,rows,left,top):
        for y,row in enumerate(rows,top):
            x=left
            for run,ink in row:
                self.put(x,y,run,ink,opaque=(ink not in ('dim','rope')))
                x+=len(run)

    def finish(self):
        return tuple(tuple((''.join(ch for ch,_ in run),ink)
                           for ink,run in groupby(row,key=lambda cell:cell[1]))
                     for row in self._data)
