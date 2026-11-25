"""Presentation-only map layouts for the Pyramid, Spaceport, and Cruiser."""

from battle_ui import CYAN, DIM, GOLD, GREEN, RED, WHITE
from reel_palette import IDS
from wide_canvas import Canvas

_INKS = {'cyan': CYAN, 'dim': DIM, 'gold': GOLD, 'green': GREEN,
         'red': RED, 'white': WHITE, **IDS}
_MARKS = {'clear': '✓', 'open': '◆', 'locked': '▣'}
# Schematic positions correspond to the operation's established story
# locations. The last two fights share the central hall.
_CRUISER_DECKS = (
    ('Passenger Deck', .73, 1),
    ('Outer Deck', .91, 1),
    ('Engine Room', .24, 3),
    ('Bulkhead', .55, 3),
    ('Central Hall', .43, 2),
    ('Central Hall', .66, 2),
)
_LETTER_SOURCES = ('cruiser-guests', 'cruiser-guests', 'cruiser-industry',
                   'cruiser-industry', 'cruiser-cleaner')


def _ink(name):
    return _INKS[name]


def _operation(row, index, width, motif=''):
    mark = _MARKS[row.status]
    medal = f' [{row.medal}]' if row.medal else ''
    prefix = f'{"▶" if row.selected else " "} {index+1:02} {mark} '
    motif = motif if len(prefix+row.title+medal+motif) <= width else ''
    name = row.title[:max(0, width-len(prefix+medal+motif))]
    return (prefix+name+medal+motif).ljust(width)


def _row_color(row, accent):
    if row.status=='locked':
        return _ink('slate') if row.selected else DIM
    return GREEN if row.status=='clear' else _ink(accent) if row.selected else WHITE


def _art(app, x, y, c):
    for iy, row in enumerate(c.finish(), y):
        ix = x
        for run, ink in row:
            if run.strip():
                app.put(iy, ix, run, _ink(ink))
            ix += len(run)


def _center(c, w, y, s, ink, opaque=False):
    c.put(max(0,(w-len(s))//2),y,s,ink,opaque)


def _motion(view):
    value = getattr(view,'motion',1)
    return max(0,min(1,value if isinstance(value,(float,int)) else 1))



# The cutaway faces the desert entrance. The six room indexes remain the
# same as the keyboard order; their physical tiers rise toward the Sphinx.
_TOMBS = ((5,), (4,), (2, 3), (0, 1))
_MURAL = ('/\\', '<>', '~^', '[]', '><', '^*')
_MURAL_INK = ('teal', 'amber', 'cyan', 'teal', 'gold', 'cyan')


def _passage(points):
    """Return cells in direction-of-travel order along the tunnel's bends."""
    out = []
    for (x, y), (tx, ty) in zip(points, points[1:]):
        n = max(abs(tx-x), abs(ty-y), 1)
        for step in range(n):
            p = x+round((tx-x)*step/n), y+round((ty-y)*step/n)
            if not out or p != out[-1]:
                out.append(p)
    return tuple(out+[points[-1]])


def _trace(canvas, points, reach, ink, head=None):
    count = min(len(points), 1+round((len(points)-1)*reach))
    for x, y in points[:count]:
        canvas.put(x, y, '·' if ink=='slate' else '•', ink)
    if head:
        canvas.put(*points[count-1], head, ink)


def _cutaway(w, h, view):
    """Stage geometry and paint (separate from the full-width label overlay)."""
    c = Canvas(w, h)
    mid = w//2
    stature = h-1
    frieze = stature
    starts = [round(stature*f/11) for f in (1,4,7,9)]
    widths = [round(mid*f) for f in (.59,.70,.88,.99)]
    room_centers = {}
    room_areas = {}
    routes = {}
    baffles = {}
    # Sand rises into four clear terraces, rather than a side illustration.
    # The outer serif of each roof grows separately at the wide terminal.
    last_l = last_r = mid
    for tier, indices in enumerate(_TOMBS):
        y = starts[tier]
        base = starts[tier+1]-1 if tier<3 else frieze-1
        left = max(0,mid-widths[tier]); right = min(w-1,mid+widths[tier])
        rim = 'amber' if tier%2==0 else 'ochre'
        if tier==0:
            for j in range(y):
                cap = max(1,round((j+1)*widths[tier]/max(2,y+1)))
                c.put(mid-cap,j,'╱'+'─'*(2*cap-1)+'╲',rim)
        else:
            c.line(left,y-1,last_l,y-1,rim,'_')
            c.line(last_r,y-1,right,y-1,rim,'_')
        c.put(left,y,'╔'+'═'*(right-left-1)+'╗',rim)
        for j in range(y+1,base+1):
            c.put(left,j,'╱' if j==base else '│',rim)
            c.put(right,j,'╲' if j==base else '│',rim)
        if base>y+1:
            c.put(left+1,base,'_'*(right-left-1),'ochre')
            for j in range(y+2,base):
                # Staggered masonry and small carved pilasters. Place the
                # pattern below the lettering so no art interrupts a title.
                for x in range(left+7+(j%2)*3,right-3,9):
                    c.put(x,j,'─┬─' if j%2 else '──┴','dim')
                if tier==0:
                    for x in (left+7,right-8):
                        c.put(x,j,'╎','ochre')
        if len(indices)==2:
            for j in range(y+1,base+1):
                c.put(mid,j,'║','ochre')
            # Leave more inside room on the right for Light Across the Chasm.
            spans=((left+2,mid-2),(mid+2,right-2))
        else:
            # Leave the left wall open for the bends of the upper passage.
            spans=((left+4,right-2),)
        for idx,(a,b) in zip(indices,spans):
            room_centers[idx]=(a+b)//2
            room_areas[idx]=(a,b,y,y+1)
        baffles[tier]=(left+2,y)
        last_l,last_r=left,right
    for idx,(a,b,y,_) in room_areas.items():
        doorway=room_centers[idx]+7
        if idx in (5,4):
            # The upper passage snakes around the great gallery.
            lx,ly=baffles[1]
            points=[(mid,frieze-1),(mid,starts[2]-1),(lx,starts[2]-1),(lx,ly)]
            if idx==5:
                ux,uy=baffles[0]
                points.extend(((lx,starts[1]-1),(ux,starts[1]-1),(ux,uy)))
            points.append((doorway,y))
        else:
            points=[(mid,frieze-1),(mid,y),(doorway,y)]
        routes[idx]=_passage(points)
    for path in routes.values():
        _trace(c,path,1,'slate')
    earned = {i for i,row in enumerate(view.rows) if row.status=='clear'} if not view.testing else set()
    if earned:
        next_open = next((i for i,row in enumerate(view.rows) if row.status=='open'),max(earned))
        _trace(c,routes[next_open],1,'teal','◦')
    selected=view.rows[view.selected]
    target=routes[view.selected]
    t = min(1,_motion(view)/.69)
    ease=1-(1-t)**2
    pigment=('gold' if selected.status=='locked' else
             'violet' if view.testing else 'cyan')
    _trace(c,target,ease,pigment,'×' if t==1 and selected.status=='locked' else '✦')
    # The frieze is part of the tomb. In Testing only one projected fragment
    # follows focus; the underlying slots stay blank and no path is earned.
    tiles_width = len(view.rows)*5-1
    start = (w-tiles_width)//2
    c.put(0,frieze,'╚'+'═'*(w-2)+'╝','ochre')
    for i,row in enumerate(view.rows):
        ghost=view.testing and i==view.selected
        restored=i in earned
        if restored:
            tile,ink='['+_MURAL[i]+']',_MURAL_INK[i]
        elif ghost:
            tile,ink='‹'+_MURAL[i]+'›','violet'
        else:
            tile,ink='[··]','slate'
        c.put(start+i*5,frieze,tile,ink,True)
    if view.testing:
        c.put(max(1,start-9),frieze,'PREVIEW','violet',True)
    return c,room_areas


def draw_pyramid(app, view):
    y=6
    h=app.h-13
    w=app.w-4
    c,rooms=_cutaway(w,h,view)
    _art(app,2,y,c)
    for i,row in enumerate(view.rows):
        a,b,header,title=rooms[i]
        w=b-a+1
        core=f'{"▶" if row.selected else " "} {i+1:02} {_MARKS[row.status]}'
        if row.medal:
            core+=f' [{row.medal}]'
        col=_row_color(row,'cyan')
        # Small lintel inset leaves the animated beam and door to its right.
        stencil=f'┤{core}├'
        app.put(y+header,2+a+(w-len(stencil))//2-2,stencil,col,
                row.selected or row.status=='clear',row.selected)
        # Leave the chamber dark: only its title and lintel carry selection.
        plaque=row.title
        app.put(y+title,2+a+(w-len(plaque))//2,plaque,col,row.selected,row.selected)


def _station_color(row):
    if row.selected:
        return 'amber' if row.status=='locked' else 'teal'
    return 'green' if row.status=='clear' else 'slate' if row.status=='locked' else 'navy'


def draw_spaceport(app, view):
    # Two checkpoints per belt section. Every tile is an actual selectable
    # operation: its header contains the shortcut/status and its name stays
    # intact at 65 columns. No second list or disconnected decorative copy.
    top=6
    h=app.h-13
    left=3
    gap=4
    width=(app.w-2*left-gap)//2
    step=max(4,min(6,h//3))
    offset=round(_motion(view)*12)
    for i,row in enumerate(view.rows):
        x=left+(i%2)*(width+gap)
        y=top+i//2*step
        pigment=_ink(_station_color(row))
        medal=f' [{row.medal}]' if row.medal else ''
        head=f'{"▶" if row.selected else " "} {i+1:02} {_MARKS[row.status]} {row.mark}{medal}'
        app.put(y,x,'╔'+head.ljust(width-2,'═')+'╗',pigment,True)
        title=row.title.center(width-2)
        app.put(y+1,x,'║'+title+'║',_row_color(row,'teal'),row.selected,row.selected)
        app.put(y+2,x,'╚'+'═'*(width-2)+'╝',pigment)
        # Roller spacing shifts briefly after selection. The rail can’t
        # consume input; focus and mission order come straight from MapView.
        wheels=''.join('o' if (j-offset)%5==1 else '-' for j in range(width-2))
        app.put(y+3,x,'['+wheels+']',pigment if row.selected else _ink('navy'))
        if not i%2:
            app.put(y+1,x+width+1,'→',_ink('teal'))
        if y+4<top+h and step>4:
            cap='[|::|]' if row.status=='locked' else '[|  |]'
            app.put(y+4,x+(width-len(cap))//2,cap,pigment)


def _passing(w, h, view):
    c=Canvas(w,h)
    # RSVP-style card holds exactly five certifications; unrelated fights
    # and practice mode cannot punch a letter.
    cleared={row.id for row in view.rows if row.status=='clear'} if not view.testing else set()
    total=sum(src in cleared for src in _LETTER_SOURCES)
    content=max(1,w-2)
    c.put(0,0,'+'+'-'*content+'+','amber')
    for j in (1,2,3):
        c.put(0,j,'|','amber');c.put(w-1,j,'|','amber')
    _center(c,w,1,'LETTERS  '+str(total)+'/5','white')
    spacing=max(3,(w-4)//5)
    start=(w-(spacing*4+3))//2
    for i,source in enumerate(_LETTER_SOURCES):
        c.put(start+i*spacing,2,'[o]' if source in cleared else '[.]',
              'green' if source in cleared else 'slate')
    _center(c,w,3,'. : . * . : .','ochre')
    c.put(0,4,'+'+'-'*content+'+','amber')
    return c


def _deck(w,h,view):
    c=Canvas(w,h)
    if w<14 or h<5:
        return c
    eye=_motion(view)
    # Deck bands share a longitudinal outline. The selected room marking
    # sits inside its actual band; the label identifies it, not the mission.
    deck_top=max(1,(h-5)//3)
    deck_end=deck_top+4
    mast=w//2+1
    hull_start=max(0,w//15)
    hull_end=w-1
    c.line(mast,0,mast,deck_top,'white','|')
    c.put(mast+1,0,'>~' if eye<.6 else '>','amber')
    c.line(w//4,deck_top,w*4//5,deck_top,'white','_')
    c.line(hull_start,deck_top+1,hull_end,deck_top+1,'amber','=')
    c.line(hull_start+1,deck_top+2,hull_end-1,deck_top+2,'navy','-')
    c.line(hull_start+2,deck_top+3,hull_end-2,deck_top+3,'navy','=')
    c.line(hull_start+3,deck_top+4,hull_end-3,deck_top+4,'white','_')
    c.line(hull_start,deck_top+1,hull_start+3,deck_end,'white','\\')
    c.line(hull_end,deck_top+1,hull_end-3,deck_end,'white','/')
    name,loc,offset=_CRUISER_DECKS[view.selected]
    cx=max(hull_start+3,min(hull_end-3,round((w-1)*loc)))
    if eye<.58:
        c.put(cx-2,deck_top+offset,'[+]', 'white',True)
    else:
        c.put(cx-2,deck_top+offset,'[+]', 'amber',True)
    for j in range(deck_end+1,h-1):
        x=(j*17+int(eye*9))%4
        c.put(x,j,'~  -  ~  '*(w//8+1),'navy' if j%2 else 'teal')
    _center(c,w,h-1,name,'white',True)
    return c


def draw_cruiser(app, view):
    h=app.h-13
    wide=app.w>=92
    body=max(38,app.w//2-8) if wide else min(41,app.w-24)
    route_x=3
    artx=route_x+body+2
    deckw=app.w-artx-2
    _art(app, artx,6,_deck(deckw,max(5,h-5),view))
    if wide:
        for i,row in enumerate(view.rows):
            y=6+i*min(3,max(2,(h-1)//len(view.rows)))
            app.put(y,route_x-1,'╎',_ink('navy'))
            app.put(y,route_x,_operation(row,i,body),_row_color(row,'amber'),
                    row.selected,row.selected)
        cardw=min(deckw,54)
        _art(app,artx+(deckw-cardw)//2,6+h-5,_passing(cardw,5,view))
    else:
        for i,row in enumerate(view.rows):
            y=6+i
            app.put(y,route_x-1,'╎',_ink('navy'))
            app.put(y,route_x,_operation(row,i,body),_row_color(row,'amber'),
                    row.selected,row.selected)
        cardw=min(body+2,app.w-6)
        _art(app,(app.w-cardw)//2,6+h-5,_passing(cardw,5,view))


THEMES={'pyramid': draw_pyramid, 'spaceport': draw_spaceport, 'cruiser': draw_cruiser}
