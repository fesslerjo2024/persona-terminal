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


def _pyramid_wall(w, h, view):
    c = Canvas(w,h)
    eye = _motion(view)
    completed = 0 if view.testing else min(6,view.cleared)
    peak = max(3,w//2-1)
    if h >= 9:
        # Native-cell silhouette: limestone ledges widen toward the foot.
        for i,y in enumerate(range(0,h)):
            r = max(2,min(peak-1,round(peak*(i+2)/(h+2))))
            x = peak-r
            inside = ''.join('.' if (iy*11+i*7)%13 in (0,2)
                             else ' ' for iy in range(2*r-1))
            c.put(x,y,'/'+inside+'\\','ochre')
            if i%2 == 0:
                c.put(x+1,y,'_'*(2*r-1),'amber')
            if i%3 == 1 and r>4:
                c.put(x+w//22,y,'.','gold')
    # Mural segments fill from left to right as operations are cleared.
    # Empty painted niches (dots) remain even in Testing, which never earns pieces.
    room = min(w-4,max(17,w*4//5))
    if w<21:
        room = w-2
    frame = max(3,(h-8)//2)
    ml=(w-room)//2
    c.put(ml,frame,'+'+'-'*(room-2)+'+','amber',True)
    c.put(ml,frame+4,'+'+'-'*(room-2)+'+','ochre',True)
    cell=max(1,(room-2)//6)
    tiles=(('/\\','./','/_'),('^^','|.','|_'),('>>','<>','<<'),
           ('{}','=','[]'),('/\\','<>','\\/'),('..','<<','^^'))
    for y in range(frame+1,frame+4):
        c.put(ml,y,'|'+' '*(room-2)+'|','ochre',True)
    for i,tile in enumerate(tiles):
        x=ml+1+i*cell
        for j, glyph in enumerate(tile,1):
            if i<completed:
                c.put(x,frame+j,glyph[:cell].ljust(cell,':'),
                      ('teal','amber','cyan','teal','amber','cyan')[i])
            elif view.testing and i==view.selected:
                # In Testing only, the selected cell is an illuminated
                # ghost. Changing selection removes it from the old cell.
                fragment = glyph[:cell].ljust(cell,'.')
                c.put(x,frame+j,fragment,'cyan' if eye<.68 else 'violet')
            elif j==2:
                c.put(x,frame+j,'.' * max(1,(cell+1)//2),'slate')
    # At the selected notch, Third Eye briefly lights a passage. A sealed
    # one remains crossed; the effect is cosmetic and never changes access.
    pulse = eye < .70
    bx = ml+1+view.selected*cell+cell//2
    anchor = view.rows[view.selected]
    y=frame+5
    if y+2<h:
        c.put(bx-1,y,'/\\' if anchor.status!='locked' else '><',
              'cyan' if pulse else 'teal')
        ray = min(3,1+int((1-eye)*3))
        for j in range(1,ray+1):
            c.put(bx+j//2,y+j,'.' if j%2 else '+','teal' if pulse else 'slate')
    if view.testing:
        _center(c,w,h-1,'PREVIEW','violet',True)
    elif h>=11:
        _center(c,w,h-1,'...:_     _::....','ochre')
    return c


def draw_pyramid(app, view):
    top=6
    h=app.h-7-top
    wide=app.w>=92
    spacing=min(3,max(2,(h-1)//6)) if wide else 2
    gap=4 if wide else 2
    route=app.w*48//100 if wide else min(39,app.w-24)
    artx=2+route+gap
    c=_pyramid_wall(app.w-artx-2,h,view)
    _art(app,artx,top,c)
    for i,row in enumerate(view.rows):
        # Steps read left to right without wasting title width at 65 columns.
        step=i%3 if wide else i//2
        x=2+step
        width=route-step
        y=top+i*spacing
        if i%2==0 and y+1<top+h:
            app.put(y+1,x,'_'*max(3,width-5),_ink('ochre'))
        app.put(y,x,_operation(row,i,width),_row_color(row,'teal'),
                row.selected or row.status=='clear',row.selected)


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
