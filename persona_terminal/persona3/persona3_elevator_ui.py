"""Read-only Tartarus lift map: checkpoint rail, inspection and native block art.

See persona3_menu_art_references.md for the game environments behind each plate.
The app passes selectable destinations in input order; no save or game rules
can enter this presentation module.
"""
from dataclasses import dataclass

from persona_terminal.shared.terminal_constants import CYAN, DIM, GOLD, WHITE
from ..shared.reel_palette import IDS
from .persona3_menu_art import block_plate
from ..shared.wide_canvas import Canvas


@dataclass(frozen=True)
class Stop:
    label: str
    floor: int
    detail: str
    kind: str
    mapped: bool = True


@dataclass(frozen=True)
class LiftView:
    block: str
    name: str
    mode: str
    stops: tuple[Stop,...]
    selected: int
    low: int
    high: int
    cleared: int
    checkpoint_count: int
    kits: int
    fragments: int | None
    level: str
    block_number: int = 1
    block_count: int = 1
    previous: str = ""
    following: str = ""


_THEMES={
    'thebel':('teal','navy','forest'),
    'arqa':('rose','wine','violet'),
    'upper':('violet','wine','rose'),
    'yabba':('ochre','slate','teal'),
    'yabba_upper':('teal','slate','amber'),
    'tziah':('amber','ochre','wine'),
    'tziah_upper':('gold','ochre','amber'),
    'harabah':('rose','wine','amber'),
    'harabah_upper':('violet','wine','rose'),
    'adamah':('cyan','navy','rose'),
}
_STOP_MARK={'ascent':'◇','revisit':'○','resume':'↪','border':'⊣','crossing':'⇧'}
_COLORS={'gold':GOLD,'cyan':CYAN,'dim':DIM,'white':WHITE,**IDS}


def silhouette(block,w,h,*,floor=None,low=0,high=1):
    """Paint a tower and the selected lift level; no progress is inferred."""
    c=Canvas(w,h)
    if w<19 or h<6:return c.finish()
    hot,base,highlight=_THEMES[block]
    c.overlay(block_plate(block,w-8,h,(hot,base,highlight)),0,0)
    shaft=w-6
    for y in range(1,h-1):
        c.put(shaft,y,':',base)
        c.put(w-1,y,':',base)
    c.put(shaft,0,'+----+',base)
    c.put(shaft,h-1,'+----+',base)
    if floor is not None:
        ratio=(floor-low)/max(1,high-low)
        y=max(1,min(h-2,round(h-2-ratio*(h-3))))
        mark=f'{floor:02d}F'
        if len(mark)==3:mark=' '+mark
        c.put(shaft,y,'['+mark+']',hot,opaque=True)
        if shaft>=3:c.put(shaft-3,y,'-->','white')
    return c.finish()


def _fit_row(text,width):
    if len(text)<=width:return text
    # In tight panes preserve the distinctive part before a generic Gate tag.
    shortened=text.removesuffix(' Gate')
    return shortened if len(shortened)<=width else shortened[:width-1].rstrip()+'…'


def draw(app, v):
    """Render at 65×25 and up, reserving the baseline header/footer rows."""
    limit=app.w-1
    right=max(34,app.w//2)
    colw=limit-right
    leftw=right-7
    app.put(5,3,'CHECKPOINTS',DIM,True)
    ink=_COLORS[_THEMES[v.block][0]]
    counter=f'{v.block_number}/{v.block_count}'
    app.put(5,right,v.name.upper()[:max(0,colw-len(counter)-1)],ink,True)
    app.put(5,limit-len(counter),counter,ink,True)
    if v.previous:
        span=(colw-1)//2
        previous='‹ '+(v.previous if len(v.previous)<=span-2 else v.previous[:span-3]+'…')
        following='› '+(v.following if len(v.following)<=span-2 else v.following[:span-3]+'…')
        app.put(6,right,previous,DIM)
        app.put(6,limit-len(following),following,DIM)
    if not v.stops:
        app.put(8,4,'No checkpoint to select.',DIM)
        return
    selected=max(0,min(len(v.stops)-1,v.selected))
    pinned=v.stops[-1].kind in ('border','crossing')
    count=len(v.stops)-int(pinned)
    top=9 if pinned else 7
    room=app.h-4-top
    start=max(0,min(selected-room//2,count-room))
    if pinned:
        crossing=v.stops[-1]
        focus=selected==len(v.stops)-1
        app.put(7,3,'▶' if focus else _STOP_MARK[crossing.kind],ink,focus)
        app.put(7,5,('TAB '+crossing.label)[:leftw].ljust(leftw),ink if focus else WHITE,focus,focus)
        app.put(8,5,'─'*leftw,ink)
    for i in range(start,min(count,start+room)):
        stop=v.stops[i]
        y=top+i-start
        focus=i==selected
        app.put(y,3,'▶' if focus else '╵' if i==count-1 else '│',
                ink if focus else DIM,focus)
        mark=_STOP_MARK[stop.kind]
        key=f'{i+1:>2}' if i<9 else '  '
        text=f'{key} {mark} {stop.label}'
        app.put(y,5,_fit_row(text,leftw).ljust(leftw),ink if focus else WHITE,focus,focus)
    stop=v.stops[selected]
    art_h=min(13,max(6,app.h-18))
    app.draw_scene_rows(silhouette(v.block,colw,art_h,floor=stop.floor if stop.mapped else None,
                                  low=v.low,high=v.high),top=7,left=right)
    y=8+art_h
    head=f'{v.cleared}/{v.checkpoint_count} CLEARED   •   {v.level}'
    app.put(y,right,head[:colw],ink,True)
    app.lines(y+2,right,stop.detail,colw,2,WHITE)
    funds=f'KITS {v.kits}'
    if v.fragments is not None:funds+=f'   •   FRAGMENTS {v.fragments}'
    app.put(app.h-6,right,funds[:colw],DIM)
    if v.mode=='practice':app.put(app.h-5,right,'Practice only. No saved rewards.'[:colw],CYAN)
    else:app.put(app.h-5,right,'Travel keeps HP, SP, and items.'[:colw] if colw>=31 else 'Keep HP / SP / items.'[:colw],DIM)
