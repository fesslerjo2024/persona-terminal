"""Read-only dot-art inspection of the Champs de Fleurs mirrors."""
from .persona3_detail_tools import Stage
from .persona3_scenic_detail import figure, room_prop


def observation(reflection):
    """A text equivalent of the framed view, not an instruction to the player."""
    if reflection:
        return "Your squad stands below the frame. The glass shows the room and your squad."
    return "Your squad stands below the frame. The glass shows the room, but nobody is in it."


def _party(s, y, rx, ry, members, mirror=False):
    colors=(('navy','cyan','slate'),('wine','rose','amber'),
            ('ochre','amber','white'),('navy','violet','rose'))
    for i in range(members):
        member=members-1-i if mirror else i
        x=50+(i-(members-1)*.5)*(rx*2+1.5)
        figure(s,x,y,rx,ry,member,colors[member],mirror)


def render(reflection, w, h, *, option=0, room='205', members=4):
    """Only figures in the pane differ between mirrored and missing reflections."""
    s=Stage(w,h)
    if w<22 or h<6:
        return s.c.finish()
    members=max(1,min(4,members))
    prop=((2,3,4) if str(room)=='304' else (0,1,2))[option%3]
    # Cell-aligned band boundaries keep the sill and foreground independent.
    one=100/(s.c.h-1)
    sill=4*(h-3)*one
    near=4*(h-2)*one
    top=2*one
    left,right=19,81
    hue=('amber','rose','violet')[option%3]
    for side in (-1,1):
        x=50+side*36
        for i in range(6):
            px=x+side*i*2.3
            s.path(((px,0),(px,sill+2*one)), 'wine' if i%2 else 'navy')
        s.ring(x+side*5,sill*.44,1.9,sill*.13,'wine')
        s.disc(x+side*5,sill*.43,.8,sill*.045,'rose')
    s.shape(((left+3,top),(right-3,top),(right,top+2*one),(right,sill-2*one),
             (right-3,sill),(left+3,sill),(left,sill-2*one),(left,top+2*one)),
            'wine',7,hue)
    s.rect(left+2.0,top+2*one,right-left-4.0,sill-top-4*one,'navy',3,'slate')
    a,b=left+4,right-4
    for x in (a+5,a+14,b-14,b-5):
        s.path(((x,top+2*one),(x,top+sill*.64)), 'slate')
        s.path(((x,top+sill*.64),(max(a,min(b,x+(x-50)*.17)),sill-3*one)), 'slate')
    for j in range(4):
        y=(sill-top)*(.62+j*.086)+top
        s.path(((a,y),(b,y)), 'teal' if j%2==0 else 'slate')
    # The glass shows the same furnishings, camera angle and trim in either case.
    px=a+1 if option%2 else b-11
    room_prop(s,px,top+3*one,10,max(7,sill*.54),prop,True,'teal')
    for i in range(3):
        x=b-20+i*2.5 if option%2 else a+14+i*2.5
        s.path(((x,top+3*one),(x-3,top+sill*.42)), 'slate' if i%2 else 'teal')
    for side in (-1,1):
        for i in range(3):
            x=50+side*(6+i*7)
            y=top-1*one
            s.path(((x-1.2,y+one),(x,y),(x+1.2,y+one)), hue)
    if reflection:
        _party(s,top+(sill-top)*.42,3.65,(sill-top)*.27,members,True)
    # Foreground profiles stay in a different band so the physical team is
    # always legible, even on a monochrome terminal with six rows of artwork.
    _party(s,near+2*one,4.4,3.6*one,members)
    return s.c.finish()
