"""Castle cutaway, Museum gallery hall and Bank deposit-door map designs."""
from math import cos, pi, sin

from palace_design import draw_design
from palace_map_art import MARKS, smooth

def _vertical(n, a=8, b=53):
    return tuple(a+(b-a)*i/max(1,n-1) for i in range(n))


def _node(s,x,y,on,bright='amber',quiet='slate'):
    s.shape('ink',(x-2.8,y),(x,y-2.8),(x+2.8,y),(x,y+2.8),edge=bright if on else quiet)
    s.oval(x,y,.82,1.1,bright if on else quiet)


def _stair(s,points,selected,available):
    """Cut a clear well into the masonry, then lay treads between landings."""
    for i,((x,y),(u,v)) in enumerate(zip(points,points[1:])):
        open_run=available(i) and available(i+1)
        focused=open_run and selected in (i,i+1)
        ink='gold' if focused else 'amber' if open_run else 'slate'
        lip='ochre' if open_run else 'navy'
        # Each stair runs between the same two detents. The hollow strip
        # removes the wall's grain under the short staircases at 65×25.
        s.shape(None,(x-2.2,y),(x+2.2,y-1),(u+2.2,v),(u-2.2,v+1))
        step=(u-x)/4
        rise=(v-y)/4
        previous=y
        for j in range(4):
            a=x+j*step
            b=y+(j+.5)*rise
            s.line(ink,(a,previous),(a,b),(a+step,b))
            s.line(lip,(a+.4,b+.9),(a+step,b+.9))
            previous=b
        s.line(ink,(u,previous),(u,v))
    for i,(x,y) in enumerate(points):
        _node(s,x,y,i==selected and available(i),'amber','ochre' if available(i) else 'slate')


def _blocks(s,x,y,u,v,base='umber',seam='ochre',grain=5):
    s.box(x,y,u,v,base,edge=seam,grain=grain)
    step=max(2.7,(v-y)/12)
    row=0
    while (k:=y+step*row)<v:
        s.line('ink',(x,k),(u,k))
        for j in range(11):
            a=x+(u-x)*(j+(row%2)*.52)/10
            if x<a<u:s.line('ink',(a,k),(a,min(v,k+step-.3)))
        row+=1


def _tower(s,x,y,u,v,tone='umber',edge='ochre'):
    _blocks(s,x,y+4,u,v,tone,edge)
    for j in range(4):
        a=x+(u-x)*j/4
        s.shape(tone,(a,y+4),(a,y),(a+(u-x)*.14,y),(a+(u-x)*.14,y+4),edge=edge)
    for q in (0.37,.70):
        a=(x+u)/2;b=y+(v-y)*q
        s.shape('ink',(a-1.5,b+2),(a-1.5,b-2),(a,b-3.2),(a+1.5,b-2),(a+1.5,b+2),edge=edge)


def _door(s,x,y,k=1,lit=False):
    ink='amber' if lit else 'ochre'
    s.shape('ink',(x-3.7*k,y+3.4*k),(x-3.7*k,y-1.5*k),(x,y-4.8*k),
            (x+3.7*k,y-1.5*k),(x+3.7*k,y+3.4*k),edge=ink)
    for i in (-2,-1,0,1,2):s.line(ink if lit else 'wine',(x+i*k,y-2.8*k),(x+i*k,y+2.8*k))
    s.line('gold' if lit else 'ochre',(x-4.5*k,y+3.5*k),(x+4.5*k,y+3.5*k))


def _torch(s,x,y,k=1):
    s.oval(x,y,2.8*k,4.0*k,'umber',edge='wine',grain=6)
    s.shape('amber',(x-1.8*k,y+1.5*k),(x-1.1*k,y-1.5*k),(x+.7*k,y-3.9*k),
            (x+.9*k,y-1.5*k),(x+1.6*k,y+.4*k),(x+.9*k,y+2.2*k),edge='gold')
    s.line('ochre',(x-1.2*k,y+2.6*k),(x,y+4.1*k),(x+1.3*k,y+2.6*k))


def _painting(s,x,y,w,h,i,lit=False,mount=True):
    ink='amber' if lit else 'ochre'
    if mount:s.box(x-w/2,y-h/2,x+w/2,y+h/2,'ink',edge=ink)
    h=h*.82;w=w*.87
    shades=(('navy','teal','white'),('umber','rose','gold'),('plum','violet','rose'),
            ('ink','forest','amber'),('umber','red','rose'),('indigo','navy','cyan'))
    shadow,mid,hi=shades[i%6]
    s.box(x-w/2,y-h/2,x+w/2,y+h/2,shadow,edge='wine')
    if i%6==0:
        s.oval(x+w*.25,y-h*.20,w*.10,h*.12,'amber')
        s.shape(mid,(x-w*.45,y+h*.42),(x-w*.19,y-h*.29),(x+w*.04,y+h*.32),
                (x+w*.22,y-h*.12),(x+w*.45,y+h*.37),edge=hi)
    elif i%6==1:
        s.oval(x-w*.06,y-h*.10,w*.15,h*.25,'amber',edge='ochre')
        s.shape(mid,(x-w*.36,y+h*.43),(x-w*.18,y+h*.20),(x,y+h*.08),(x+w*.15,y+h*.16),
                (x+w*.34,y+h*.43),edge=hi)
        s.line('ink',(x-w*.15,y-h*.10),(x+w*.03,y-h*.12))
    elif i%6==2:
        s.line(hi,(x-w*.33,y+h*.41),(x-w*.20,y+h*.12),(x+w*.34,y-h*.36))
        for j in range(5):
            s.oval(x-w*.27+w*j*.137,y+h*.22-h*j*.125,w*.10,h*.106,mid,edge=hi)
    elif i%6==3:
        s.arch(x,y+h*.14,w*.3,h*.47,hi)
        s.shape(mid,(x-w*.26,y+h*.40),(x-w*.19,y-h*.2),(x+w*.23,y-h*.2),(x+w*.32,y+h*.40),grain=5)
        s.line('teal',(x-w*.26,y+h*.36),(x+w*.30,y+h*.36))
    elif i%6==4:
        for j in range(4):
            a=-.5+j*1.15
            s.shape(mid,(x,y),(x+cos(a)*w*.41,y+sin(a)*h*.43),
                    (x+cos(a+.51)*w*.39,y+sin(a+.51)*h*.42),edge=hi)
        s.oval(x,y,w*.08,h*.15,'amber')
    else:
        s.line(mid,(x-w*.4,y-h*.08),(x+w*.41,y-h*.08))
        for j in range(4):
            xx=x+(-.35+j*.22)*w
            s.shape(hi,(xx,y+h*.37),(xx+.06*w,y-h*.24),(xx+.11*w,y+h*.38),edge=mid)
        s.line('white',(x-w*.4,y+h*.24),(x+w*.43,y+h*.24))
    if lit:
        s.line('amber',(x-w*.42,y-h*.47),(x+w*.42,y-h*.47))
        s.line('amber',(x-w*.42,y+h*.46),(x+w*.42,y+h*.46))


def _deposit(s,x,y,w,h,selected=False):
    ink='teal' if selected else 'navy'
    s.shape('ink',(x,y-h),(x+w-3,y-h),(x+w,y-h+2.1),(x+w,y+h),
            (x,y+h),edge=ink)
    s.line('slate',(x+1,y+h-1),(x+w-1,y+h-1))
    x1=x+w-4
    s.ring(x1,y,1.5,1.6,'amber' if selected else 'slate')
    s.line('ochre' if selected else 'navy',(x1-2,y),(x1-.9,y+.1),(x1+.9,y))

def _title(p,index,x,y,width,align='left'):
    # Protect full route titles at 65 columns without moving their stair or
    # aisle anchor to an unrelated row. The adapter adds actual status/grade.
    need=len(p.rows[index].title)+7
    width=max(width,(need+.05)*100/p.width)
    if align=='left':
        x=min(x,100-(need+.5)*100/(p.width-1))
    p.mission(index,x,y,width,align)


def _entrance(s,x,y,opened,motion):
    """A foreground gate looking into the selected stair landing."""
    highlight='amber' if opened else 'slate'
    s.shape('ink',(x-7,y+7),(x-7,y-2),(x-3.6,y-7.4),(x+1.4,y-8.5),
            (x+6.5,y-5),(x+8,y-2),(x+8,y+7),edge='umber')
    for j,(rx,ry) in enumerate(((7,7),(5.25,5.25),(3.55,3.7))):
        anchor=x+j*.37
        s.ring(anchor,y-1,rx,ry,highlight if j!=1 else 'ochre',pi,2*pi)
        for side in (-1,1):
            s.line(highlight if j==2 else 'ochre',(anchor+side*rx,y-1),(anchor+side*rx,y+5.4-j*.7))
    grid=max(0.,smooth(motion/.32)) if opened else 0
    top=y-3.8-grid*.75
    bar_floor=y+4.5-grid*4
    for j in range(-2,3):
        xx=x+j*1.22+.55
        s.line('gold' if opened and j==0 else highlight,(xx,top),(xx,bar_floor))
    s.line('gold' if opened else 'slate',(x-2.5,bar_floor),(x+3,bar_floor))
    s.line('ochre',(x-5,y+6),(x-2.0,y+4.6),(x+4,y+4.6),(x+7,y+6))
    if opened:
        # The small warm point sets the entrance apart, not neighboring routes.
        s.shape('amber',(x-5.8,y+.8),(x-6.4,y-1.2),(x-5.3+grid*.39,y-3),
                (x-4.9,y-.4),(x-4.7,y+.5),edge='gold')


def _castle_design(p):
    s=p.art;ys=_vertical(p.count,8,54)
    coords=tuple((16+9*(i%2),y) for i,y in enumerate(ys))
    _tower(s,2,2,13,58)
    _tower(s,89,2,98,58)
    _blocks(s,13,6,33,56,'plum','wine',4)
    for i,y in enumerate(ys):
        active=i==p.selected
        ink='ochre' if active and p.available(i) else 'wine'
        s.line(ink,(coords[i][0],y),(29,y),(33,y-2),(88,y-2))
        s.line(ink,(31,y+2.7),(89,y+2.7))
        if active:
            s.line('amber' if p.available(i) else 'slate',(76,y+2.7),(84,y+2.7),(88,y+1))
    _stair(s,coords,p.selected,p.available)
    for i,y in enumerate(ys):
        _door(s,31,y,.76,i==p.selected and p.available(i))
        _title(p,i,36,y,49)
    y=ys[p.selected]
    _entrance(s,91.5,y,p.available(p.selected),p.motion)
    if p.available(p.selected):
        _torch(s,25.4,y+.9,.55)


def _curtain(s,x,y,w,h,active):
    s.box(x-w/2,y-h/2,x+w/2,y+h/2,'ink',edge='slate' if active else 'navy')
    s.shape('plum',(x-w*.45,y-h*.37),(x+w*.45,y-h*.37),(x+w*.48,y+h*.37),
            (x+w*.23,y+h*.30),(x,y+h*.39),(x-w*.20,y+h*.27),(x-w*.45,y+h*.38),
            edge='navy')
    for j in range(5):
        step=(j-2)*w*.175
        s.line('slate' if active else 'wine',(x+step,y-h*.33),(x+step*.94,y-.2),
               (x+step*.99,y+h*.28))


def _museum_design(p):
    s=p.art
    # The paired gallery walls converge past the operation plaques, retaining
    # the route's existing left-to-right reading order.
    for j in range(6):
        t=j/5
        color='ochre' if j%2==0 else 'wine'
        s.line(color,(5+25*t,58-16*t),(6+31*t,2+19*t),
               (94-31*t,2+19*t),(96-25*t,58-16*t))
    for i in range(7):
        x=i*12+15
        s.line('wine',(50,40),(x,60))
    for i,row in enumerate(p.rows):
        left=i%2==0; seq=i//2
        x=12+seq*7 if left else 87-seq*7
        y=10+seq*16
        active=i==p.selected
        if p.available(i):
            _painting(s,x,y,13-seq,10-seq,i,active)
            if row.status=='clear':
                # Geometric seal augments the real grade in the text plaque.
                dx=x+(5 if left else -5)
                s.ring(dx,y+3,2.4,2.2,'red')
                s.line('rose',(dx-1.25,y+3),(dx-.32,y+3.6),(dx+1.25,y+1.5))
            if active:
                glow=smooth(p.motion/.3)
                s.line('amber',(x-(7-seq),y-(5-seq*.5)-glow),
                       (x+(7-seq),y-(5-seq*.5)-glow))
        else:
            _curtain(s,x,y,13-seq,10-seq,active)
        _title(p,i,2 if left else 99,y+5,46,'left' if left else 'right')


def _bank_dial(p,cx,cy,rx,ry):
    s=p.art
    s.oval(cx,cy,rx,ry,'indigo',edge='slate',grain=4)
    s.oval(cx,cy,rx*.9,ry*.9,None,edge='teal')
    s.ring(cx,cy,rx*.78,ry*.78,'navy')
    for j in range(p.count*6):
        a=j*pi/(3*p.count)
        r=.73 if j%6==0 else .81 if j%2==0 else .875
        s.line('white' if j%6==0 else 'slate' if j%2==0 else 'navy',
               (cx+rx*.90*cos(a),cy+ry*.90*sin(a)),(cx+rx*r*cos(a),cy+ry*r*sin(a)))
    for i,row in enumerate(p.rows):
        angle=-pi/2+2*pi*i/p.count
        x=cx+rx*.7*cos(angle); y=cy+ry*.7*sin(angle)
        selected=i==p.selected
        # The row already carries the operation status; let one lit detent
        # and its number draw the eye instead of six bright labels.
        target=selected and p.available(i)
        ink='amber' if target else 'slate' if selected else 'dim'
        s.oval(x,y,rx*.067,ry*.066,'ink',edge=ink if selected else 'navy')
        s.oval(x,y,rx*.027,ry*.027,ink if selected else 'slate')
        # Use the same angle and radius multiplier on both axes, so the
        # number remains directly along the line through the aimed-at slot.
        angle_x=cx+rx*.93*cos(angle);angle_y=cy+ry*.93*sin(angle)
        tag=f'{i+1}{MARKS[row.status]}'
        p.note(tag,angle_x,angle_y,width=8,ink=ink,align='center')
    previous=p.previous if 0<=p.previous<p.count else p.selected
    old=-pi/2+2*pi*previous/p.count; target=-pi/2+2*pi*p.selected/p.count
    angle=old+((target-old+pi)%(2*pi)-pi)*smooth(p.motion/.32)
    u,v=cx+rx*.70*cos(angle),cy+ry*.70*sin(angle)
    allowed=p.available(p.selected)
    # A broad brass blade supplies body; the white central ridge makes its
    # direction legible even when a single terminal cell contains both tones.
    dx,dy=-sin(angle),cos(angle)
    s.shape('gold' if allowed else 'slate',(cx+2.7*dx,cy+3.5*dy),
            (u,v),(cx-2.7*dx,cy-3.5*dy),edge='amber' if allowed else 'slate')
    s.line('white' if allowed else 'slate',(cx,cy),(u,v))
    if allowed:
        for offset in (-1.14,1.14):
            s.line('white',(cx+dx*offset,cy+dy*offset),
                   (u+dx*offset*.55,v+dy*offset*.55))
        s.oval(u,v,1.45,1.55,'gold',edge='amber')
        s.point(u,v,'white')
        if .32<=p.motion<.49 and previous!=p.selected:
            s.line('white',(u-2.4,v),(u+2.4,v))
            s.line('amber',(u,v-2.7),(u,v+2.7))
    s.oval(cx,cy,rx*.15,ry*.15,'ochre' if allowed else 'navy',
           edge='amber' if allowed else 'slate')
    s.oval(cx,cy,rx*.073,ry*.08,'ink',edge='white' if allowed else 'slate')


def _bank_design(p):
    s=p.art
    s.shape('slate',(1,2),(40,2),(43,6),(43,55),(40,58),(2,58),(0,55),(0,6),
            edge='navy',grain=4)
    _bank_dial(p,21,30,18,24)
    for i,y in enumerate(_vertical(p.count,6,54)):
        active=i==p.selected
        _deposit(s,47,y,52,3.9,active and p.available(i))
        if active:
            s.line('amber' if p.available(i) else 'slate',(42,y),(46,y))
        _title(p,i,49,y,45)


def draw_castle(app,view):
    draw_design(app,view,'amber',_castle_design)


def draw_museum(app,view):
    draw_design(app,view,'rose',_museum_design)


def draw_bank(app,view):
    draw_design(app,view,'gold',_bank_design)


THEMES={'castle':draw_castle,'museum':draw_museum,'bank':draw_bank}
