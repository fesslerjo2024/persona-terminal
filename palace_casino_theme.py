"""Sae's black-and-gold elevator directory, rendered without changing access."""
from battle_ui import GOLD, WHITE, DIM
from reel_palette import IDS

BRASS = IDS['ochre']
FLARE = IDS['amber']
FLOORS = ('STAFF ONLY', 'MEMBERS FLOOR', 'HIGH LIMIT')


def _floor(index):
    return min(index, 2)


def _operation(row, index, available, testing):
    # The route list still reads top to bottom with Up/Down and 1–6. Only the
    # real directory reverses that physical order, like the elevator shaft.
    state = (' ' if testing else {'clear':'✓', 'open':'◆', 'locked':'▣'}[row.status])
    cursor = '▶' if row.selected else ' '
    medal = f' [{row.medal}]' if row.medal else ''
    label = f'{cursor}{index+1:02}{state} {row.title}'
    if len(label)+len(medal)>available and row.medal:
        medal=f'[{row.medal}]'
    if len(label)+len(medal)>available:
        medal=''
    return (label+medal).ljust(available)


def draw_casino(app, view):
    top,bottom=6,app.h-8
    shaft_right=min(16,max(8,app.w//8))
    heading_x=shaft_right+2
    route_x=heading_x+15
    route_w=app.w-route_x-3
    shaft_span=shaft_right-3
    current=_floor(view.selected)
    previous=_floor(view.previous) if 0<=view.previous<len(view.rows) else current
    open_floors={_floor(i) for i,r in enumerate(view.rows) if r.status!='locked'}
    highest=max(open_floors,default=0)
    previous,current_dock=min(highest,previous),min(highest,current)
    high,low=top+2,bottom-2
    by_floor=(low,(high+low)//2,high)
    f=min(1.,view.motion/.52)
    travel=f*f*(3-2*f)
    center=round(by_floor[previous]+(by_floor[current_dock]-by_floor[previous])*travel)
    moving=previous!=current_dock and f<1.

    app.put(top,3,'╔'+'═'*(shaft_span-1)+'╗',BRASS,True)
    app.put(bottom,3,'╚'+'═'*(shaft_span-1)+'╝',BRASS,True)
    for y in range(top+1,bottom):
        app.put(y,3,'║',BRASS)
        app.put(y,shaft_right,'║',BRASS)
        if y<center:
            app.put(y,3+shaft_span//2,'┆',BRASS)
    inside=shaft_span-1
    app.put(center-1,4,'┏'+'━'*(inside-2)+'┓',FLARE,True)
    app.put(center,4,('╫' if moving else '│').center(inside,'╎'),GOLD,True,not moving)
    app.put(center+1,4,'┗'+'━'*(inside-2)+'┛',FLARE,True)
    for floor,y in enumerate(by_floor):
        docked=floor==current_dock and not moving
        if docked:
            # The open cabin, docking bridge and floor name share one row.
            app.put(y,shaft_right,'╟─',GOLD,True)
        else:
            app.put(y,shaft_right+1,'·',BRASS if floor in open_floors else DIM)
        label=FLOORS[floor]
        color=GOLD if docked else BRASS if floor in open_floors else DIM
        app.put(y,heading_x,label,color,docked or floor==current)

    stride=2 if bottom-top>=13 else 1
    y0=top+(bottom-top-(len(view.rows)-1)*stride)//2
    for i,row in enumerate(view.rows):
        color=WHITE if row.selected else DIM if row.status=='locked' else GOLD if row.status=='clear' else WHITE
        app.put(y0+i*stride,route_x,_operation(row,i,route_w,view.testing),color,row.selected,row.selected)


THEMES={'casino':draw_casino}
