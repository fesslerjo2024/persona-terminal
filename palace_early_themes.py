"""Castle section, Museum gallery wall, and Bank vault route maps."""
from math import cos, pi, sin

from battle_ui import CYAN, DIM, GOLD, GREEN, RED, WHITE
from reel_palette import IDS

AMBER, NAVY, OCHRE, ROSE, SLATE, TEAL, WINE = (
    IDS[name] for name in ('amber','navy','ochre','rose','slate','teal','wine')
)
TOP = 6
_STATE = {'clear': '✓', 'open': '◆', 'locked': '▣'}


def _bottom(app):
    return app.h-8


def _xput(app,y,x,s,ink=WHITE,b=False,reverse=False):
    # Bound the native decoration independently of the app's clipping.
    if TOP<=y<=_bottom(app) and x<app.w-2:
        if x<0:
            s=s[-x:]
            x=0
        if s:
            app.put(y,x,s[:app.w-2-x],ink,b,reverse)


def _ln(app,a,b,ink,char=None):
    x,y=a; xx,yy=b
    steps=max(abs(xx-x),abs(yy-y),1)
    if char is None:
        char='-' if abs(xx-x)>3*abs(yy-y) else '|' if abs(yy-y)>3*abs(xx-x) else '/' if (xx-x)*(yy-y)<0 else '\\'
    for k in range(steps+1):
        _xput(app,round(y+(yy-y)*k/steps),round(x+(xx-x)*k/steps),char,ink)


def _route(op,i,limit,testing):
    nav='▶' if op.selected else ' '
    state=_STATE[op.status] if not testing else ' '
    prefix=f'{nav}{i+1:02}{state} '
    medal=f' [{op.medal}]' if op.medal else ''
    if len(prefix)+len(op.title)+len(medal)>limit:
        medal=''
    width=max(1,limit-len(prefix)-len(medal))
    title=op.title if len(op.title)<=width else op.title[:max(0,width-1)]+'…'
    return prefix+title+medal


def _route_ink(op,selected=AMBER):
    return selected if op.selected else {'clear':GREEN, 'open':WHITE, 'locked':DIM}[op.status]


def _flame(app,x,y,when,ink=AMBER):
    flick=int(min(when,.999)*16)%3
    _xput(app,y-1,x-2,(".'^'."," .^^ ","  ^'.")[flick],ink,True)
    _xput(app,y,x-2,("/{*}\\"," /{*}","\\{*}/")[flick],GOLD,True)



def _stairs(app, gate, floors, selected):
    """Connect each landing to the next; treads meet at the switchbacks."""
    for i,y in enumerate(floors):
        edge=gate-(8 if i%2==0 else 3)
        _xput(app,y,edge,'┬'+'─'*(gate-edge-2)+'╢',AMBER if selected==i else OCHRE)
    for i,(a,b) in enumerate(zip(floors,floors[1:])):
        start=gate-(8 if i%2==0 else 3)
        stop=gate-(3 if i%2==0 else 8)
        rise=max(1,b-a)
        ink=OCHRE if selected in (i,i+1) else WINE
        travel=lambda k: round(start+(stop-start)*k/rise)
        for k in range(rise):
            x,nx=travel(k),travel(k+1)
            width=abs(nx-x)
            if nx>x:
                _xput(app,a+k,x,'└'+'─'*max(0,width-1)+'┐',ink)
            elif nx<x:
                _xput(app,a+k,nx,'┌'+'─'*max(0,width-1)+'┘',ink)
            else:
                _xput(app,a+k,x,'│',ink)
        _xput(app,b,stop,'┴' if i%2 else '┤',ink)


def draw_castle(app,view):
    """A cross-section with a zigzag tower stair, portcullises, and torchlight."""
    w=app.w; bottom=_bottom(app); span=bottom-TOP+1
    left=3; right=w-5
    gate=max(12,min(29,w//5)); text=gate+12
    tw=right-text-5
    high=TOP+1
    # Tall flanking towers are quieter than the brightly lit playable floor.
    for x,ww in ((left,gate-5),(right-6,7)):
        _xput(app,TOP,x,('_|¯|'*((ww+3)//4))[:ww],OCHRE)
        for yy in range(TOP+1,bottom+1):
            row='|' + ('_.__' if (yy+x)%3 else '.___')*((ww-2+3)//4)
            _xput(app,yy,x,row[:ww-1]+'|',WINE if (yy+x)%3 else OCHRE)
    _xput(app,TOP,gate,'/-^-/\\' if w<84 else '/--^---^--/\\',OCHRE)
    n=len(view.rows)
    floors=tuple(high+(span-3)*i//max(1,n-1) for i in range(n))
    for i,op in enumerate(view.rows):
        y=floors[i]
        flank=4 if i%2 else 0
        tar=gate+flank
        row_ink=_route_ink(op)
        wall=right-10
        _xput(app,y,gate-1,' '*(wall-gate+2),WINE)
        if i and y-floors[i-1]>1:
            _xput(app,y-1,text,'._'*(max(1,tw)//2),OCHRE if op.selected else WINE)
        if op.status=='locked':
            _xput(app,y,tar,'[|||||]',SLATE)
        elif op.status=='clear':
            _xput(app,y,tar,'[  / ]',GREEN)
        else:
            _xput(app,y,tar,'/  :  \\',OCHRE)
        if op.selected:
            _flame(app,right-5,y,view.motion)
        _xput(app,y,text,_route(op,i,tw,view.testing),row_ink,op.selected)
    _stairs(app,gate,floors,view.selected)
    # A single charcoal basin links the stair to the lower foundation.
    _xput(app,bottom,gate,'\\___'+'_'*max(1,right-gate-14)+'___/',OCHRE)


_EXHIBITS = (
    (' /\\_   .', ' /^^\\  o ', ' ///.\\\\__'),
    (' <>-<> ',r'<>\|/<>', ' <>-<> '),
    (' .----. ',r'(< o >)', ' :----: '),
    (' /\\_/\\ ', '(( :. ))',r' \//\\/ '),
    ('  _.__  ',r' / /| \ ',r'<_/~\__>'),
    (' \\ .. / ', ' |::| ', ' / ^^ \\ '),
)
_ART = (ROSE, AMBER, TEAL, WINE, OCHRE, SLATE)



_BACKING = (
    (r'.-===-.',r'| \*/ |',r'>--+--<'),
    (r'.-|||-.',r'| ::: |',r'>:|||:<'),
    (r'._/^\_.',r'|< * >|',r'>--*--<'),
    (r'.-@@@-.',r'| ( ) |',r'>-(#)-<'),
    (r'._/=\_.',r'| [@] |',r'>-[#]-<'),
    (r'..---..',r'|>{*}<|',r'>-{*}-<'),
)


def _exhibit(app,op,i,x,y,bw,rows,motion,ink):
    """The canvas physically slides to expose a recess behind its mount."""
    art=_EXHIBITS[i%len(_EXHIBITS)]
    lip=x+(bw-9)//2
    slide=0
    if op.selected:
        motion=min(1.,motion/.30)
        slide=round(5*motion*motion*(3-2*motion))
        if slide>1:
            hidden=_BACKING[i%len(_BACKING)]
            for j,line in enumerate(hidden[-rows:]):
                _xput(app,y+j,lip+4,line,SLATE if op.status=='locked' else TEAL,True)
        if slide:
            # Leave screw heads and a brass right edge on the moving panel.
            _xput(app,y,lip-slide-2,'o',AMBER)
            if rows>=2:
                _xput(app,y+rows-1,lip-slide-2,'o',AMBER)
    for j,line in enumerate(art[-rows:]):
        _xput(app,y+j,lip-slide,line,ink,op.selected)
    if slide:
        _xput(app,y,lip-slide+len(art[0])-1,'/',AMBER,True)
        if rows>=2:
            _xput(app,y+rows-1,lip-slide+len(art[0])-1,'/',AMBER,True)


def draw_museum(app,view):
    """Framed miniatures; a stamped diagonal seals a completed exhibit."""
    w=app.w; bottom=_bottom(app); span=bottom-TOP+1
    # At 64–90 cols show two frames per bay; at wide view three fit comfortably.
    cols=3 if w>=103 else 2
    frames=(len(view.rows)+cols-1)//cols
    gap=2 if w<89 else 3
    bw=(w-4-(cols-1)*gap)//cols
    start=(w-cols*bw-(cols-1)*gap)//2
    for i,op in enumerate(view.rows):
        gy,gx=divmod(i,cols)
        y=TOP+span*gy//frames
        last=TOP+span*(gy+1)//frames-1
        x=start+gx*(bw+gap)
        height=last-y+1
        frame=AMBER if op.selected else OCHRE if op.status!='locked' else SLATE
        border=f'.{"="*(bw-2)}.'
        _xput(app,y,x,border,frame,op.selected)
        _xput(app,last,x,border[::-1],frame,op.selected)
        for r in range(y+1,last):
            _xput(app,r,x,'|',frame,op.selected)
            _xput(app,r,x+bw-1,'|',frame,op.selected)
        art_ink=_ART[i%len(_ART)] if op.status!='locked' else SLATE
        art_rows=max(1,min(3,height-3))
        _exhibit(app,op,i,x,y+1,bw,art_rows,view.motion,art_ink)
        if op.status=='clear':
            if op.medal and not _route(op,i,bw-2,view.testing).endswith(f' [{op.medal}]'):
                _xput(app,y+1,x+2,f'[{op.medal}]',GREEN,True)
            # The stamp crosses the upper-right of the artwork, never the title.
            sx=x+bw-8
            if height>4:
                _xput(app,y+1,sx+2,'..---',RED)
                _xput(app,y+3,sx-2,'---..',RED)
            _xput(app,y+(2 if height>4 else 1),sx,'/STOLEN',RED,True)
        elif op.status=='locked' and bw>=24:
            _xput(app,y+1,x+bw-7,'[::]',NAVY)
        if height>=6:
            _xput(app,last-2,x+2,'-'*(bw-4),frame)
        label=_route(op,i,bw-2,view.testing)
        _xput(app,last-1,x+1,label,_route_ink(op),op.selected)


def _ring(app,cx,cy,rx,ry,ink):
    prev=None
    for j in range(65):
        a=j*2*pi/64
        p=(round(cx+rx*cos(a)),round(cy+ry*sin(a)))
        if prev is not None and p!=prev:
            _ln(app,prev,p,ink)
        prev=p


def draw_bank(app,view):
    """Steel dial plus a numbered ledger of deposit boxes."""
    w=app.w; bottom=_bottom(app); span=bottom-TOP+1
    split=max(22,min(w//2-7, (w*43)//100))
    cx=split//2+1; cy=(TOP+bottom)//2
    rx=cx-4; ry=(span-2)//2
    _ring(app,cx,cy,rx,ry,SLATE)
    _ring(app,cx,cy,max(3,rx-3),max(2,ry-1),TEAL)
    # Status marks on the index dial mirror the unlocked route sequence.
    spots=[]
    for i,op in enumerate(view.rows):
        a=-pi/2+2*pi*i/len(view.rows)
        xx=cx+round((rx-4)*cos(a)); yy=cy+round((ry-1)*sin(a))
        spots.append((xx,yy))
    settle=False
    if spots:
        op=view.rows[view.selected]
        xx,yy=spots[view.selected]
        has_move=(view.previous is not None and 0<=view.previous<len(spots)
                  and view.previous!=view.selected)
        if has_move and view.motion<.32:
            # Sweep the shortest arc, so the needle stays the same length.
            start=(-.25+view.previous/len(spots))*2*pi
            end=(-.25+view.selected/len(spots))*2*pi
            delta=(end-start+pi)%(2*pi)-pi
            p=view.motion/.32
            p=p*p*(3-2*p)
            phase=start+delta*p
            xx=cx+round((rx-4)*cos(phase)); yy=cy+round((ry-1)*sin(phase))
        settle=(has_move and .32<=view.motion<.49)
        _ln(app,(cx,cy),(xx,yy),WHITE if settle else GOLD if op.status!='locked' else SLATE)
        if settle:
            # Two brief contact glints sit past the detent, not on its status.
            sx=1 if xx>=cx else -1
            sy=1 if yy>=cy else -1
            _xput(app,yy+sy,xx+2*sx,'*' if view.motion<.40 else '+',AMBER,True)
            _xput(app,yy,xx+2*sx,'.',WHITE,True)
    for i,(xx,yy) in enumerate(spots):
        op=view.rows[i]
        _xput(app,yy,xx-1,f'{i+1}',_route_ink(op),op.selected)
        _xput(app,yy,xx,_STATE[op.status] if not view.testing else ('+' if op.selected else '.'),_route_ink(op),op.selected)
    _xput(app,cy,cx-1,'(+)' if settle else '(o)',WHITE if settle else AMBER,True)
    _xput(app,cy+1,cx,'|',OCHRE)
    for y in (TOP+1,bottom-1):
        _xput(app,y,2,'[=]',SLATE)
        _xput(app,y,split-3,'[=]',SLATE)
    # Labels are on deposit doors, around a handle/bolt, not in an info table.
    start=split+2; width=w-start-4
    prior_y=TOP-1
    for i,op in enumerate(view.rows):
        y=TOP+1+i*(span-3)//max(1,len(view.rows)-1)
        ink=TEAL if op.selected else NAVY if op.status=='locked' else SLATE
        if y-prior_y>1:
            _xput(app,y-1,start,'+'+'-'*(width-2)+'+',ink)
        _xput(app,y,start,'|',ink)
        _xput(app,y,start+width-1,'|',ink)
        label=_route(op,i,width-2,view.testing)
        _xput(app,y,start+1,label,_route_ink(op),op.selected)
        end='[-]' if op.status=='locked' else '[=]' if op.status=='clear' else '[_]'
        if len(label)<=width-6:
            _xput(app,y,start+width-4,end,ink,op.selected)
        prior_y=y
    _xput(app,bottom,start,'+'+'='*(width-2)+'+',SLATE)


THEMES={'castle':draw_castle,'museum':draw_museum,'bank':draw_bank}
