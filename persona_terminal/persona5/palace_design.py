"""Live layout adapter for the approved Palace concept artwork."""
from dataclasses import dataclass, replace

from .palace_map_art import Art, TOP, caption, place, row_ink, volume


@dataclass(frozen=True)
class Label:
    text: str
    x: int
    y: int
    ink: str
    bold: bool = False
    reverse: bool = False


class Design:
    """Place operation labels in a 100×60 art plan without exposing locked data."""

    def __init__(self, app, view, accent):
        self.width,self.height=app.w-6,volume(app)
        self.art=Art(self.width,self.height)
        self.view=view
        self.rows=view.rows
        self.count=len(self.rows)
        self.selected=view.selected
        self.previous=view.previous
        self.motion=view.motion
        self.accent=accent
        self.titles=tuple(row.title for row in self.rows)
        self._missions={}
        self._notes=[]

    def available(self,index):
        return 0<=index<self.count and self.rows[index].status!='locked'

    def _row(self,y):
        return max(0,min(self.height-1,round((self.height-1)*y/60)))

    def _window(self,x,width,align,minimum=0):
        span=min(self.width,max(5,minimum,round(self.width*width/100)))
        anchor=round((self.width-1)*x/100)
        if align=='center':
            left=anchor-span//2
        elif align=='right':
            left=anchor-span+1
        else:
            left=anchor
        left=max(0,min(self.width-max(1,minimum),left))
        return left,min(span,self.width-left)

    @staticmethod
    def _align(left,span,text,align):
        adjust=span-len(text)
        return left+(adjust//2 if align=='center' else adjust if align=='right' else 0)

    def mission(self,index,x,y,width=40,align='left',short=None):
        row=self.rows[index]
        if index in self._missions:
            raise ValueError(f'Duplicate operation label: {row.id}')
        # The focused operation can use the real name even where a compact
        # alternate label is useful for one of its neighboring rooms.
        name='???' if row.status=='locked' else (short if short and not row.selected else row.title)
        entry=replace(row,title=name)
        minimum=len(caption(entry,index,self.width)) if row.selected else 0
        left,n=self._window(x,width,align,minimum)
        value=caption(entry,index,n)
        self._missions[index]=Label(value,self._align(left,n,value,align),self._row(y),
                                    row_ink(row,self.accent),row.selected,
                                    row.selected and self.available(index))

    def note(self,text,x,y,width=32,ink='slate',align='left'):
        left,n=self._window(x,width,align)
        if len(text)>n:text=text[:max(0,n-1)].rstrip()+'…'
        if text:
            self._notes.append(Label(text,self._align(left,n,text,align),self._row(y),ink))

    def labels(self):
        if self._missions.keys()!=set(range(self.count)):
            raise ValueError('Palace art did not place every operation exactly once')
        occupied={}
        def accept(q,y):
            start,end=q.x,q.x+len(q.text)
            spans=occupied.setdefault(y,[])
            if any(start<r and end>l for l,r in spans):return False
            spans.append((start,end))
            return True

        # Prioritize the focus. At 65x25 a pair of normalized anchors can
        # round into the same cell: separate them without hiding either.
        out=[]
        for i in sorted(self._missions,key=lambda i:(i!=self.selected,i)):
            q=self._missions[i]
            order=sorted(range(self.height),key=lambda y:abs(y-q.y))
            row=next(y for y in order if accept(q,y))
            out.append(replace(q,y=row))
        out.extend(q for q in self._notes if accept(q,q.y))
        return out


def draw_design(app,view,accent,layout):
    p=Design(app,view,accent)
    layout(p)
    p.art.paint(app,3,TOP)
    for q in p.labels():
        place(app,3+q.x,TOP+q.y,q.text,q.ink,q.bold,q.reverse)
    return p
