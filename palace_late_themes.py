"""Terminal-platform and clinical-form maps, with gated late-route variants."""

from palace_design import draw_design

_DEPTH_CROSSING = 'depths-rebellion'
_LAB_LIGHTS = 'laboratory-colors'


def _focus_reaches(p, gate):
    """Use the story's existing availability and the actual focused route."""
    return p.available(p.selected) and any(
        row.id==gate and p.available(i) for i,row in enumerate(p.rows[:p.selected+1])
    )


def _lanes(p,x,y,last,width):
    step=(last-y)/max(1,p.count-1)
    for i in range(p.count):
        p.mission(i,x,y+step*i,width=width)


def _platform(p):
    """DP-04: clean departure board, double route rail, and route-only status."""
    a=p.art
    tight=p.height<15
    top=8 if tight else 13
    bottom=54
    step=(bottom-top)/max(1,p.count-1)
    a.shape('indigo',(1,1),(99,1),(99,3.5),(1,3.5),edge='slate',grain=3)
    a.line('navy',(1,58),(96,58),(99,56))
    a.line('slate',(6,top-3),(6,bottom+2))
    a.line('teal',(10,top-3),(10,bottom+2))
    for i in range(p.count):
        y=top+step*i
        if tight and i<p.count-1:
            a.line('ink',(15,y+3.4),(85,y+3.4))
        if not tight:
            a.line('slate',(15,y+3.5),(79,y+3.5))
        ink='cyan' if p.available(i) else 'slate'
        # Selection on a hidden row never lights up the associated route.
        a.oval(8,y,1.2,1.25,'white' if i==p.selected and p.available(i) else 'ink',edge=ink)
    _lanes(p,14,top,bottom,78)
    # End of the platform, separated from the text and route indication.
    for j in range(4):
        x=87+j*3
        a.line('wine' if j==0 else 'navy',(x,top+3),(x,bottom-3))


def _fracture(p,left,top,right,bottom):
    a=p.art
    def pt(x,y):
        return left+(right-left)*x/100,top+(bottom-top)*y/60
    def plane(ink,*points,edge=None,grain=8):
        a.shape(ink,*(pt(*a) for a in points),edge=edge,grain=grain)
    def beam(ink,*points):
        a.line(ink,*(pt(*a) for a in points))

    plane('plum',(0,0),(25,0),(35,16),(36,24),(39,28),(26,44),(18,49),(10,59),(0,59),
          edge='wine',grain=3)
    plane('indigo',(72,0),(100,0),(100,59),(73,59),(65,50),(60,33),(67,29),(62,15),
          edge='wine',grain=3)
    plane('slate',(2,15),(34,15),(42,22),(37,23),(40,28),(1,28),edge='rose',grain=3)
    plane('slate',(67,26),(98,26),(98,41),(66,41),(63,37),(68,32),(62,30),edge='red',grain=4)
    beam('white',(6,19),(37,19),(43,27))
    beam('red',(64,31),(93,31))
    # Falling debris recedes into the chasm. The lighter dotted approach
    # to operation 04 should read first, not this diagonal toward 06.
    beam('plum',(45,31),(50,37),(53,42))
    beam('indigo',(53,42),(55,45),(57,51))
    a.point(*pt(47,32),'plum')
    a.point(*pt(54,41),'indigo')
    a.point(*pt(58,48),'indigo')


def _bridge(p):
    """DP-05: the surviving routes occupy opposite edges of a broken span."""
    if p.width<81 or p.height<17:
        _fracture(p,72,5,99,57)
        # Labels stack at minimum width; keep the 03 → 04 cue near the
        # labels rather than floating it out across the side illustration.
        for x,y in ((3,26),(2,29),(2,32),(3,34)):
            p.art.point(x,y,'slate')
        p.art.point(3.4,34.6,'violet')
        _lanes(p,4,7,53,65)
        return
    _fracture(p,2,2,98,58)
    # A sparse approach marker bends across the gap between the third
    # operation and the first operation on the far ledge. No solid bridge.
    for x,y in ((45,49),(47,45),(48.5,41),(49.5,37),(49.8,32),(50,28),
                (50.4,23),(51,19),(51.7,15),(53,11)):
        p.art.point(x,y,'slate')
    p.art.point(53.3,10,'violet')
    y_left=(6,35,50)
    y_right=(8,23,51)
    for i in range(p.count):
        left=i<3
        p.mission(i,4 if left else 54,(y_left if left else y_right)[i%3],
                  width=43 if left else 45)


def _intake(p):
    """LB-01: a sparse paper form and embossed clinical seal."""
    a=p.art
    tight=p.width<80 or p.height<15
    left,top,right,bottom=3,2,73 if tight else 69,58
    a.shape('indigo',(left,top),(right-3,top),(right,top+3),(right,bottom),
            (left,bottom),(left,top),edge='white',grain=0)
    a.shape('indigo',(left+1,top+1),(right-4,top+1),(right-1,top+5),(right-1,top+6),
            (left+1,top+6),edge='slate',grain=0)
    start,last=(11,51) if tight else (13,51)
    step=(last-start)/max(1,p.count-1)
    for i in range(p.count-1):
        y=start+step*i+(step-1)*.56
        a.line('navy',(left+3,y),(right-4,y))
    _lanes(p,left+3,start,last,right-left-4)
    mid=(right+99)/2
    a.oval(mid,26,8,11,'indigo',edge='slate',grain=4)
    a.ring(mid,26,7,9,'teal')
    a.line('white',(mid,20),(mid,32))
    a.line('white',(mid-4,26),(mid+4,26))
    for i,ink in enumerate(('cyan','teal','slate')):
        a.line(ink,(right+4,41+3*i),(96-i,41+3*i))


def _prism(p,left,top,right,bottom):
    a=p.art
    def pt(x,y):
        return left+(right-left)*x/100,top+(bottom-top)*y/60
    def beam(ink,*points):
        a.line(ink,*(pt(*a) for a in points))
    beam('white',(3,29),(30,29),(49,27))
    # This is a map-focus cue, not the current switch state inside the
    # route. Only the accessible Twilight Corridor focus lights the span.
    bridge_focused=p.rows[p.selected].id==_LAB_LIGHTS and p.available(p.selected)
    for end,ink in ((14,'cyan'),(27,'green'),(45,'rose')):
        beam(ink,(49,27),(63,(27+end)/2),(96,end))
    if bridge_focused:
        beam('teal',(48,27),(63,22),(96,15))
        beam('cyan',(48,25),(63,19),(96,12))
        beam('white',(60,22),(73,19),(87,16),(96,14))
    a.shape('navy',pt(41,38),pt(49,14),pt(60,38),edge='white',grain=3)
    beam('slate',(46,34),(49,23),(54,34))
    beam('teal',(2,24),(12,24),(12,34),(2,34))
    for end,ink in ((14,'cyan'),(27,'green'),(45,'rose')):
        x,y=pt(96,end)
        active=bridge_focused and ink=='cyan'
        a.oval(x,y,2.1 if active else 1.2,2 if active else 1.4,
               'cyan' if active else 'ink',edge='white' if active else ink)


def _color_route(p):
    """LB-03: a single prism shows the three distinct light paths."""
    if p.width<81 or p.height<17:
        _prism(p,70,8,98,55)
        _lanes(p,4,7,53,65)
        return
    _prism(p,2,16,98,45)
    for i in range(p.count):
        x=4 if i<3 else 55
        # Offset the two banks around the light diagram while keeping full
        # phrases at ordinary desktop widths.
        y=(5,13,54)[i%3] if i<3 else (6,46,54)[i%3]
        p.mission(i,x,y,width=43 if i<3 else 44)


def _depth_layout(p):
    (_bridge if _focus_reaches(p,_DEPTH_CROSSING) else _platform)(p)


def _lab_layout(p):
    (_color_route if _focus_reaches(p,_LAB_LIGHTS) else _intake)(p)


def draw_depths(app,view):
    draw_design(app,view,'violet',_depth_layout)


def draw_laboratory(app,view):
    draw_design(app,view,'cyan',_lab_layout)


THEMES={'depths':draw_depths,'laboratory':draw_laboratory}
