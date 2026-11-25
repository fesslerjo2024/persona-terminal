"""Read-only Velvet Room surfaces for Persona 3 Terminal."""
from dataclasses import dataclass
import textwrap

from battle_ui import CYAN, DIM, GOLD, WHITE
from persona3_cinematics import render_fusion_review
from reel_palette import IDS

BLUE=IDS['navy']
TEAL=IDS['teal']
SLATE=IDS['slate']


@dataclass(frozen=True)
class Row:
    label: str
    detail: str = ''
    enabled: bool = True


@dataclass(frozen=True)
class View:
    screen: str
    index: int
    yen: int
    rows: tuple[Row, ...]
    detail: tuple[str | tuple[str,int], ...] = ()
    footer: str = ''
    review_elapsed: float | None = None


_TITLES={
    'stock':'VELVET ROOM / ACTIVE STOCK',
    'compendium':'VELVET ROOM / COMPENDIUM',
    'fusion':'VELVET ROOM / FUSION',
    'inherit':'VELVET ROOM / INHERITANCE',
    'confirm':'VELVET ROOM / CONFIRM FUSION',
    'resummon':'VELVET ROOM / CONFIRM RESUMMON',
}


def _short(s,width):
    if len(s)<=width:
        return s
    return s[:max(0,width-1)]+'…' if width else ''


def _clip(app,y,x,msg,ink=WHITE,active=False,reverse=False):
    width=max(0,app.w-x-2)
    if 0<=y<app.h-4 and width:
        app.put(y,x,_short(msg,width),ink,active,reverse)


def _details(app,lines,x,top,bottom):
    width=max(1,app.w-x-3)
    for item in lines:
        text,ink=(item,WHITE) if isinstance(item,str) else item
        for s in textwrap.wrap(text,width=width,break_on_hyphens=False) or ('',):
            if top>bottom:
                return
            if s:
                _clip(app,top,x,s,ink)
            top+=1


def _rows(app,view,top,bottom,width):
    if not view.rows:
        return
    n=len(view.rows)
    i=max(0,min(n-1,view.index))
    step=2 if any(row.detail for row in view.rows) else 1
    count=max(1,(bottom-top+1)//step)
    needs_window=count<n
    if needs_window:
        count=max(1,(bottom-top)//step)  # Reserve one row for window position.
    start=min(max(0,i-count//2),max(0,n-count))
    stop=min(n,start+count)
    for k in range(start,stop):
        row=view.rows[k]; active=k==i; y=top+(k-start)*step
        # The number picker exposes only 1–9. Don't advertise a fake 10 key.
        key=f'{k+1} ' if k<9 else '  '
        lead=('◆ ' if active else '  ')+key
        label=_short(lead+row.label,width).ljust(width)
        _clip(app,y,3,label,CYAN if active and row.enabled else GOLD if active else
              WHITE if row.enabled else DIM,active,active and row.enabled)
        if step==2 and row.detail:
            _clip(app,y+1,7,_short(row.detail,max(1,width-4)),
                  SLATE if row.enabled else DIM,False)
    if needs_window:
        marker=('↑ ' if start else '  ')+f'{start+1}–{stop}/{n}'+(' ↓' if stop<n else '')
        _clip(app,bottom,3,marker,SLATE)


def draw(app,view):
    """Paint an immutable controller-provided view without consulting the save."""
    title=_TITLES[view.screen]
    app.frame(title,view.footer)
    money=f'¥{view.yen:,}'
    _clip(app,4,app.w-3-len(money),money,GOLD,True)
    top=7
    bottom=app.h-6
    if view.screen in ('confirm','resummon'):
        # Transaction consequences and the price fit across the full width.
        if view.screen=='confirm' and view.review_elapsed is not None:
            ink_for={'navy':BLUE,'teal':TEAL,'cyan':CYAN,'slate':SLATE,'rose':IDS['rose']}
            for y,row in enumerate(render_fusion_review(view.review_elapsed,app.w-6),5):
                x=3
                for run,ink in row:
                    if run.strip():
                        _clip(app,y,x,run,ink_for.get(ink,DIM))
                    x+=len(run)
            top=10
        else:
            _clip(app,5,3,'╲'+'─'*min(app.w-8,42),BLUE)
        _details(app,view.detail,4,top,bottom)
        return

    split=max(31,min(44,app.w//2-1))
    x=split+2
    _clip(app,5,3,'╲'+'─'*(split-5),BLUE)
    _clip(app,5,x,'─'*min(app.w-x-3,35),BLUE)
    if view.rows:
        for y in range(top,bottom+1):
            _clip(app,y,split,'│',BLUE)
        _rows(app,view,top,bottom,split-4)
    _details(app,view.detail,x if view.rows else 4,top,bottom)
