"""Packed-dot Casino lift; floor access still belongs to the frozen map view."""
from functools import lru_cache
from math import cos, pi, sin

from palace_map_art import Art, TOP, caption, paint, place, row_ink, smooth, volume

FLOORS=('STAFF ONLY','MEMBERS FLOOR','HIGH LIMIT')


def _floor(index):
    return min(index,2)


@lru_cache(maxsize=144)
def _elevator(w,h,stop,travel):
    """Brass Service Lift: subdued rails, strongly separate door and roof."""
    s=Art(w,h)
    q=stop*60/(h-1)
    s.shape('umber',(3,4),(14,1),(86,1),(97,4),(97,55),
            (86,59),(14,59),(3,55),edge='ochre',grain=2)
    # The shaft is deliberately hollow: a door seam and two amber lips remain
    # distinct even in the five-column compact treatment.
    for x,ink in ((14,'ochre'),(26,'wine'),(74,'wine'),(86,'ochre')):
        s.line(ink,(x,4),(x,56))
    for y in (10,30,50):
        s.line('wine',(26,y),(74,y))
    s.shape('ochre',(13,q-2.8),(26,q-6.3),(74,q-6.3),
            (87,q-2.8),(87,q+5.4),(13,q+5.4),edge='amber',grain=5)
    s.box(23,q-3.15,77,q+3.15,'plum',edge='gold',grain=3)
    s.line('rose',(24,q-2.2),(43,q-2.2),(48,q),(43,q+2.2),(24,q+2.2))
    s.line('rose',(76,q-2.2),(57,q-2.2),(52,q),(57,q+2.2),(76,q+2.2))
    s.line('gold' if travel else 'white',(50,q-2.55),(50,q+2.55))
    return s.c.finish()


@lru_cache(maxsize=42)
def _wheel_crop(w,h):
    """Wheel and Rail, a restrained cut at the right edge of the route."""
    s=Art(w,h)
    cx,cy=101,37
    for rx,ry,ink in ((93,31,'ochre'),(86,28,'wine'),(74,24,'ochre'),
                      (60,19,'wine'),(42,14,'ochre'),(21,7,'wine')):
        s.ring(cx,cy,rx,ry,ink,pi*.62,pi*1.47)
    for k in range(11):
        a=(.64+k*.083)*pi
        s.line('wine',(cx+83*cos(a),cy+27*sin(a)),
               (cx+74*cos(a),cy+24*sin(a)))
        if k%3==1:
            s.point(cx+91*cos(a),cy+30*sin(a),'amber')
    return s.c.finish()


def draw_casino(app,view):
    top=TOP;h=volume(app);bottom=top+h-1
    shaft_right=min(20,8+max(0,app.w-65)//3)
    heading_x=shaft_right+2; route_x=heading_x+15; route_w=app.w-route_x-3
    current=_floor(view.selected)
    previous=_floor(view.previous) if 0<=view.previous<len(view.rows) else current
    open_floors={_floor(i) for i,r in enumerate(view.rows) if r.status!='locked'}
    highest=max(open_floors,default=0)
    previous,current_dock=min(highest,previous),min(highest,current)
    high,low=top+2,bottom-2
    by_floor=(low,(high+low)//2,high)
    f=smooth(view.motion/.52)
    center=round(by_floor[previous]+(by_floor[current_dock]-by_floor[previous])*f)
    moving=previous!=current_dock and f<1.
    paint(app,3,top,_elevator(shaft_right-3,h,center-top,moving))
    stride=2 if bottom-top>=13 else 1
    y0=top+(bottom-top-(len(view.rows)-1)*stride)//2
    stages={y0+i*stride:(row,caption(row,i,route_w)) for i,row in enumerate(view.rows)}
    if highest==2:
        wheel=min(28,max(13,app.w//3-4))
        wheel_x=app.w-wheel-2
        for y,runs in enumerate(_wheel_crop(wheel,h-3),top+2):
            # Leave at least three quiet cells beyond any stage label even
            # at the compact size; never paint through a mission name.
            minimum=max(wheel_x,route_x+len(stages[y][1])+3) if y in stages else wheel_x
            x=wheel_x
            for text,ink in runs:
                trim=max(0,minimum-x)
                if text[trim:].strip():
                    place(app,x+trim,y,text[trim:],ink)
                x+=len(text)
    for floor,y in enumerate(by_floor):
        docked=floor==current_dock and not moving
        if docked:
            place(app,shaft_right,y,'╟─','gold',True)
        else:
            place(app,shaft_right+1,y,'·','ochre' if floor in open_floors else 'dim')
        label=FLOORS[floor] if floor in open_floors else f'FLOOR {floor+1:02}'
        color='gold' if docked else 'ochre' if floor in open_floors else 'dim'
        place(app,heading_x,y,label,color,docked or floor==current)
    for y,(row,label) in stages.items():
        color=row_ink(row,'white')
        place(app,route_x,y,label,color,row.selected,
              row.selected and row.status!='locked')


THEMES={'casino':draw_casino}
