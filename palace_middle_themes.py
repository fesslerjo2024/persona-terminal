"""Packed-dot Pyramid cutaway, Spaceport factory and Cruiser deck route."""
from functools import lru_cache
from math import cos, pi, sin

from palace_design import draw_design
from palace_map_art import Art, MARKS, TOP, caption, fixture, paint, place, row_ink, seed, volume

# The mapped spaces follow the terminal adaptation's navigation order.
_TOMBS = ((5,), (4,), (2,3), (0,1))
_MURAL = ('/\\', '<>', '~^', '[]', '><', '^*')
_MURAL_INK = ('teal','amber','cyan','teal','gold','cyan')
_CRUISER_DECKS = (('Passenger Deck',.73,1),('Outer Deck',.91,1),
                  ('Engine Room',.24,3),('Bulkhead',.55,3),
                  ('Central Hall',.43,2),('Central Hall',.66,2))
_LETTER_SOURCES = ('cruiser-guests','cruiser-guests','cruiser-industry',
                   'cruiser-industry','cruiser-cleaner')


def _passage(points):
    out=[]
    for (x,y),(tx,ty) in zip(points,points[1:]):
        n=max(abs(tx-x),abs(ty-y),1)
        for j in range(n):
            pt=x+round((tx-x)*j/n),y+round((ty-y)*j/n)
            if not out or pt!=out[-1]:out.append(pt)
    return tuple(out+[points[-1]])


@lru_cache(maxsize=60)
def _pyramid(w,h):
    """Cross-Section at Dusk: quiet rooms below a single dusk-lit silhouette."""
    s=Art(w,h)
    mid=w//2;frieze=h-1
    starts=tuple(round((h-1)*f/11) for f in (1,4,7,9))
    widths=tuple(round(mid*f) for f in (.52,.66,.83,.97))
    rooms={};centers={};baffles={}
    s.shape('umber',(1,56),(49,1),(99,56),(99,58),(1,58),
            edge='ochre',grain=2)
    s.shape('plum',(49,1),(99,56),(99,58),(49,58),edge='wine',grain=1)
    s.line('amber',(1,56),(49,1),(71,25))
    s.line('wine',(71,25),(99,56))
    s.line('ochre',(5,55),(48,6))
    # Uncluttered dark plates sit across the section; the interior remains a map.
    for tier,indices in enumerate(_TOMBS):
        y=starts[tier];base=starts[tier+1]-1 if tier<3 else frieze-1
        left=max(0,mid-widths[tier]);right=min(w-1,mid+widths[tier])
        x=left*100/(w-1);u=right*100/(w-1)
        top=y*60/(h-1); bottom=min(58,(base+.68)*60/(h-1))
        s.shape('ink',(x,top),(u,top),(u,bottom-.5),(u-1.5,bottom),
                (x+1.5,bottom),(x,bottom-.5),edge='ochre',grain=0)
        s.line('amber',(x+1.2,top+.7),(x+8,top+.7))
        s.line('wine',(u-8,bottom-.1),(u-1.5,bottom-.1))
        if bottom-top>=10:
            for k in range(3):
                for side in (x+4,u-5):
                    px=side+k*.75
                    s.line('ochre' if k==0 else 'umber',
                           (px,top+3),(px,bottom-2))
        if len(indices)==2:
            s.line('wine',(49.5,top+1),(49.5,bottom-1))
            spans=((left+1,mid-1),(mid+1,right-1))
        else:
            spans=((left+2,right-2),)
        for idx,(left_span,right_span) in zip(indices,spans):
            centers[idx]=(left_span+right_span)//2
            rooms[idx]=(left_span,right_span,y,y+1)
        baffles[tier]=(left+1,y)
    # The exterior rim is laid over the section so the overall Pyramid still
    # reads as a single rising silhouette, not only a staircase of rooms.
    s.line('ochre',(1,56),(49,1),(78,34))
    s.line('wine',(78,34),(99,56))
    s.line('umber',(5,56),(49,5),(94,55))
    s.line('ochre',(1,56.5),(99,56.5))
    for px in (2,5,8,92,95,98):
        s.line('ochre',(px-1,59),(px,57.5),(px+1,59))
    routes={}
    for idx,(_,_,y,_) in rooms.items():
        doorway=centers[idx]+(6 if idx in (1,3,4,5) else -7)
        if idx in (4,5):
            lx,ly=baffles[1]
            op=[(mid,frieze-1),(mid,starts[2]-1),(lx,starts[2]-1),(lx,ly)]
            if idx==5:
                ux,uy=baffles[0];op.extend(((lx,starts[1]-1),(ux,starts[1]-1),(ux,uy)))
            op.append((doorway,y))
        else:
            op=[(mid,frieze-1),(mid,y),(doorway,y)]
        routes[idx]=_passage(op)
    return s.c.finish(),rooms,routes


@lru_cache(maxsize=42)
def _desert(w,h):
    """Approach Across the Dunes, with the mural reserved below the exterior."""
    s=Art(w,h)
    s.oval(55,14,20,13,'ochre',edge='amber',grain=5)
    s.shape('umber',(12,52),(61,15),(91,49),(97,54),(6,56),
            edge='ochre',grain=3)
    s.shape('wine',(61,15),(91,49),(97,54),(64,56),grain=3)
    s.line('amber',(12,52),(61,15),(73,29))
    s.line('ochre',(73,29),(91,49),(97,54))
    s.line('ochre',(60,17),(24,51),(21,52))
    s.shape('plum',(36,53),(42,46),(51,45),(56,37),(63,37),
            (66,42),(75,46),(78,54),edge='ochre',grain=4)
    s.line('ochre',(78,44),(86,46),(91,51))
    for j in range(3):
        d=j*3.4
        s.line('ochre' if j==0 else 'wine',(0,50+d),(19,51+d),(34,51+d),
               (62,54+d),(82,53+d),(100,55+d))
    return s.c.finish()


def _trace(app,x,y,points,reach,ink,head='',active=False):
    count=min(len(points),1+round((len(points)-1)*reach))
    for wx,wy in points[:count]:
        place(app,x+wx,y+wy,'•' if active else '·',ink)
    if head:
        wx,wy=points[count-1];place(app,x+wx,y+wy,head,ink)


def _mural(app,view,x,y,w,earned):
    start=x+(w-len(view.rows)*5+1)//2
    for i,row in enumerate(view.rows):
        if i in earned:
            tile,ink='['+_MURAL[i]+']',_MURAL_INK[i]
        elif view.testing and i==view.selected:
            tile,ink='‹'+_MURAL[i]+'›','violet'
        else:
            tile,ink='[··]','slate'
        place(app,start+i*5,y,tile,ink)
    if view.testing:place(app,max(3,start-9),y,'PREVIEW','violet')


def _approach(app,view,h,w):
    x=2;ay=TOP
    art_x=max(44,app.w//2+6);art_w=app.w-art_x-3
    paint(app,art_x,ay,_desert(art_w,h-1))
    stride=2 if h>=15 else 1
    y=ay+(h-2-(len(view.rows)-1)*stride)//2
    for i,row in enumerate(view.rows):
        px=4+min(i,4)
        ink=row_ink(row,'amber')
        s=caption(row,i,art_x-px-1)
        place(app,px,y+i*stride,s,ink,row.selected,row.selected and row.status!='locked')
        if row.selected and px+len(s)<art_x-3:
            # The sealed route remains visibly barred until the papyrus
            # turns this desert view into the internal chamber map.
            trail=' ·×' if row.status=='locked' else ' ·›'
            place(app,px+len(s),y+i*stride,trail,'amber',True)
    _mural(app,view,x,ay+h-1,w,set())


def draw_pyramid(app,view):
    h=volume(app);w=app.w-4;y=TOP;x=2
    earned={i for i,row in enumerate(view.rows) if row.status=='clear'} if not view.testing else set()
    if not view.testing and not earned:
        _approach(app,view,h,w)
        return
    art,rooms,routes=_pyramid(w,h)
    paint(app,x,y,art)
    for tunnel in routes.values():_trace(app,x,y,tunnel,1,'slate')
    if earned:
        next_open=next((i for i,row in enumerate(view.rows) if row.status=='open'),max(earned))
        _trace(app,x,y,routes[next_open],1,'teal','◦')
    row=view.rows[view.selected];t=min(1,view.motion/.69)
    _trace(app,x,y,routes[view.selected],1-(1-t)**2,
           'gold' if row.status=='locked' else 'violet' if view.testing else 'cyan',
           '×' if t==1 and row.status=='locked' else '✦',True)
    _mural(app,view,x,y+h-1,w,earned)
    for i,row in enumerate(view.rows):
        a,b,head,title=rooms[i];width=b-a+1
        core=f'{"▶" if row.selected else " "} {i+1:02} {MARKS[row.status]}'
        if row.medal:core+=f' [{row.medal}]'
        ink=row_ink(row,'cyan')
        hi=row.selected and row.status!='locked'
        place(app,x+a+(width-len(core))//2,y+head,core,ink,row.selected or row.status=='clear',hi)
        plaque=row.title
        place(app,x+a+(width-len(plaque))//2,y+title,plaque,ink,row.selected,hi)


@lru_cache(maxsize=122)
def _factory_canvas(w,h,tiers,selected,phase,open_rows):
    """Six Workcells: negative space between open, machine-like cases."""
    s=Art(w,h)
    for level,(y,z) in enumerate(tiers):
        y0=(y+.05)*60/h;y1=(z+.92)*60/h
        for side,(left,right) in enumerate(((2.5,44),(55,97))):
            op=level*2+side;live=op==selected and open_rows[op]
            ink='teal' if live else 'navy' if open_rows[op] else 'slate'
            s.shape('ink',(left+2,y0+.5),(right-2,y0+.5),(right,y0+2.3),
                    (right,y1-2),(right-2,y1-.25),(left+2,y1-.25),
                    (left,y1-2),(left,y0+2.3),edge=ink,grain=0)
            # Small notched corners, a roller rail, and a narrow illuminated rim.
            s.line('cyan' if live else 'navy',(left+2,y0+.5),(left+8,y0+.5))
            s.line('forest' if live else 'slate',(right-6,y1-.3),(right-2,y1-.3))
            yb=y1-2.4
            s.line(ink,(left+2,yb-.95),(right-2,yb-.95))
            for i in range(12):
                u=left+2+(i*(right-left-4)/12+(phase*.55 if live else 0))%(right-left-4)
                s.oval(u,yb,1.03,1.05,ink,grain=6)
                if live:s.point(u,yb-.3,'cyan')
            if z-y>=5:
                for bracket,sign in ((left+3,1),(right-3,-1)):
                    s.line(ink,(bracket,yb-1.2),(bracket,yb-4.6),
                           (bracket+sign*3,yb-6.1))
                    s.line('slate',(bracket+sign*.7,yb-1.2),
                           (bracket+sign*.7,yb-3.4))
        # Bridge the two lower roller rails with a short exposed span. Match
        # the rollers inside the cells so it reads as machinery, not a key.
        yb=y1-2.4
        link='navy' if open_rows[level*2] and open_rows[level*2+1] else 'slate'
        s.line(link,(43.2,yb-.95),(55.8,yb-.95))
        s.line(link,(43.2,yb+1.2),(55.8,yb+1.2))
        for roller in (45.6,48.6,51.6,54.6):
            s.oval(roller,yb,.91,1.05,link,grain=6)
    # These return chutes turn each workcell pair into the next one.
    for level in range(len(tiers)-1):
        _,last=tiers[level]
        first,_=tiers[level+1]
        # Drop the chute below the exposed span before folding back. Even
        # compact terminals get a gap between the belt and the return.
        start=(last+1.09)*60/h
        stop=(first+.72)*60/h
        turn=(start+stop)/2
        linked=open_rows[level*2+1] and open_rows[level*2+2]
        ink='slate' if linked else 'ink'
        s.line(ink,(55,start),(52.1,start),(51.4,turn),(47.5,turn),
               (46.7,stop),(44,stop))
        # One stamped vane on the chute points from this pair to the next.
        s.line('navy' if linked else ink,(50.1,turn-.85),(49,turn),(50.05,turn+.85))
    return s.c.finish()


def draw_spaceport(app,view):
    h=volume(app);w=app.w-4;tiers=tuple((i*h//3,(i+1)*h//3-1) for i in range(3))
    available=tuple(r.status!='locked' for r in view.rows)
    phase=round(min(view.motion,.64)*18)
    paint(app,2,TOP,_factory_canvas(w,h,tiers,view.selected,phase,available))
    gap=8;left=5;width=(app.w-2*left-gap)//2
    for i,row in enumerate(view.rows):
        tray,side=divmod(i,2);x=left+side*(width+gap);y=TOP+tiers[tray][0]
        grade=f' [{row.medal}]' if row.medal else ''
        head=f'{"▶" if row.selected else " "} {i+1:02} {MARKS[row.status]} {row.mark}{grade}'
        ink=row_ink(row,'teal')
        hi=row.selected and row.status!='locked'
        place(app,x,y+1,head,ink,row.selected)
        place(app,x+(width-len(row.title))//2,y+2,row.title,ink,row.selected,hi)


def _cruiser_broadside(p,left,top,right,bottom,deck):
    """A capitol-like silhouette with a distinct bow, flag, and waterline."""
    a=p.art
    box_w,box_h=right-left,bottom-top
    def pt(x,y):
        return left+x*box_w/100,top+y*box_h/60
    def plane(ink,*vertices,edge=None,grain=8):
        a.shape(ink,*(pt(*v) for v in vertices),edge=edge,grain=grain)
    def beam(ink,*vertices):
        a.line(ink,*(pt(*v) for v in vertices))

    if box_w>=43:
        for i in range(9):
            x=i*12+1; y=27+10*seed(i*399+61)
            plane('indigo',(x,y),(x+4,y-2),(x+8,y),(x+8,47),(x,45),edge='navy',grain=4)
        for i in range(15):
            a.point(*pt(seed(i*871+13)*100,seed(i*739+36)*32),'slate')
    plane('ink',(3,35),(96,35),(89,45),(78,52),(17,52),(7,47),edge='slate')
    plane('navy',(7,42),(91,41),(78,52),(17,52),(8,47),edge='teal',grain=6)
    beam('amber',(4,36),(96,36))
    plane('slate',(12,33),(16,26),(86,26),(93,33),edge='white',grain=4)
    plane('navy',(24,26),(28,19),(74,19),(82,26),edge='slate')
    plane('slate',(32,19),(35,15),(43,15),(45,8),(51,8),(54,4),(59,8),(64,8),
          (66,15),(74,15),(77,19),edge='white',grain=5)
    beam('white',(54,5),(54,-1))
    beam('amber',(54,-1),(65,1),(55,3))
    beam('slate',(2,54),(26,55),(69,55),(97,53))
    beam('teal',(12,58),(48,57),(85,58),(98,57))
    beam('teal',(25,49),(78,49),(91,43))
    for i in range(6 if box_w<43 else 11):
        x=23+i*(70/(6 if box_w<43 else 11))
        beam('gold',(x,29),(x+1.7,29))
    if deck is not None:
        _,position,level=_CRUISER_DECKS[deck]
        x=13+position*75
        y=(29,29,38,44)[level]
        # A warm spill and bright inner window stay legible even on the
        # smallest broadside, where a one-dot cross vanishes into the hull.
        plane('ochre',(x-13,y-2.6),(x+11,y-2.6),(x+12,y+2.6),(x-13,y+2.6),
              edge='amber',grain=6)
        beam('gold',(x-9,y),(x+9,y))
        beam('white',(x-3.5,y),(x+4,y))
        beam('white',(x,y-2.3),(x,y+2.3))


def draw_cruiser(app,view):
    draw_design(app,view,'amber',_cruiser_layout)


def _cruiser_layout(p):
    dense=p.width<80 or p.height<16
    # Keep full mission length on the compact terminal before reserving art.
    left=67 if dense else 52
    last=40 if dense else 48
    first=4
    each=(last-first)/max(1,p.count-1)
    p.art.line('slate',(2,first),(2,last))
    for i in range(p.count):
        y=first+each*i
        active=i==p.selected and p.available(i)
        ink='amber' if active else 'slate' if p.available(i) else 'navy'
        center=(round((p.height-1)*y/60)*4+1.5)*60/max(1,p.height*4-1)
        p.art.oval(2,center,.65,1.15,'white' if active else 'ink',edge=ink)
        p.mission(i,4,y,width=left-4)
    deck=p.selected if p.available(p.selected) else None
    _cruiser_broadside(p,left+1,4,98,40 if dense else 51,deck)
    if deck is not None:
        loc=_CRUISER_DECKS[deck][0]
        p.note(loc,(left+99)/2,47 if dense else 54,width=99-left,ink='white',align='center')
    # Recommendations were already earned by exactly these three missions.
    # Never substitute Battle Practice availability for authored letters.
    cleared={r.id for r in p.rows if r.status=='clear'} if not p.view.testing else set()
    flags=tuple(src in cleared for src in _LETTER_SOURCES)
    if dense:
        label_x,letters_x,y=4,35,55
    else:
        label_x,letters_x,y=4,26,58
    p.note(f'LETTERS {sum(flags)}/5',label_x,y,width=22,ink='white')
    for i,filled in enumerate(flags):
        p.note('[✓]' if filled else '[·]',letters_x+i*8,y,width=8,
               ink='gold' if filled else 'slate')

THEMES={'pyramid':draw_pyramid,'spaceport':draw_spaceport,'cruiser':draw_cruiser}
