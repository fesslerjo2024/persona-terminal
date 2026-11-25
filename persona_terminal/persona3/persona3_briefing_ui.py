"""Dorm briefing wall and isolated presentation for the squad editor."""
from dataclasses import dataclass
from datetime import date
from textwrap import wrap

from persona_terminal.shared.terminal_constants import CYAN, DIM, GOLD, WHITE
from .persona3_dorm_notice import DormNote
from ..shared.reel_palette import IDS
from .persona3_menu_art import moon_medallion

TEAL=IDS['teal']
NAVY=IDS['navy']
SLATE=IDS['slate']
_MOON_COLORS={'white':WHITE,'cyan':CYAN,**IDS}
ROSTER_SECONDS=.32

_DIGITS={
    '0':('▄███▄','█   █','█   █','█   █','▀███▀'),
    '1':(' ▄█  ','  █  ','  █  ','  █  ','▄███▄'),
    '2':('▄███▄','    █','▄███▀','█    ','█████'),
    '3':('▄███▄','    █','  ██▄','    █','▀███▀'),
    '4':('█   █','█   █','▀████','    █','    █'),
    '5':('█████','█    ','▀███▄','    █','▀███▀'),
    '6':('▄███▄','█    ','████▄','█   █','▀███▀'),
    '7':('█████','    █','   █ ','  █  ','  █  '),
    '8':('▄███▄','█   █','▄███▄','█   █','▀███▀'),
    '9':('▄███▄','█   █','▀████','    █','▀███▀'),
}
_RADAR=(
    '   │    ',
    ' ╭─┼─╮  ',
    '─┤ ◆ ├─ ',
    ' ╰─┼─╯  ',
    '   │    ',
)


@dataclass(frozen=True)
class Briefing:
    day: date
    next_event: date
    event_title: str
    full_moon: date | None
    choices: tuple[str,...]
    block: str
    progress: str
    field_next: str
    deadlines: tuple[str,...]=()
    rescue: bool=False
    notice: DormNote | None=None
    earlier: str=''


@dataclass(frozen=True)
class Roster:
    title: str
    names: tuple[str,...]
    picked: frozenset[str]
    vitals: tuple[int,int]
    absence: str=''


def _divide(w):
    return max(32,w//2)


def draw_evening(app, view):
    split=_divide(app.w)
    left_width=split-6
    moon_now=view.next_event==view.full_moon
    days=max(0,(view.next_event-view.day).days)
    footer='↑↓ SELECT  ↵ OPEN'+('  R RESCUE BOARD' if view.rescue else '')+'  ESC CALENDAR'
    app.frame('IWATODAI DORM / S.E.E.S. BRIEFING',footer)
    app.put(6,4,'NEXT FULL MOON' if moon_now else 'NEXT EVENT',CYAN,True)
    for row in range(5):
        cells=' '.join(_DIGITS[d][row] for d in f'{days:02d}')
        app.put(7+row,4,cells,GOLD if moon_now else CYAN)
        if not moon_now:app.put(7+row,split-10,_RADAR[row],SLATE)
    if moon_now:
        for row,runs in enumerate(moon_medallion(),7):
            x=split-10
            for text,ink in runs:
                if text.strip():app.put(row,x,text,_MOON_COLORS[ink])
                x+=len(text)
    app.put(11,17,'DAY' if days==1 else 'DAYS',GOLD if moon_now else CYAN,True)
    subject=('S.E.E.S. DEPLOYMENT' if moon_now and view.event_title=='FULL MOON' else view.event_title)
    event_lines=wrap(subject,left_width)
    for row,line in enumerate(event_lines[:2],12):
        app.put(row,4,line,WHITE,True)
    app.put(14,4,f'{view.next_event:%m/%d}',GOLD)
    if view.full_moon and not moon_now:
        app.put(16,4,f'NEXT FULL MOON  {view.full_moon:%m/%d}',TEAL)
    if view.notice:
        app.put(17,4,f'DORM NOTICEBOARD / {view.notice.author.upper()}',TEAL,True)
        for row,part in enumerate(wrap(view.notice.body,left_width)[:3],18):
            app.put(row,4,part,WHITE)
    app.put(6,split+2,'TONIGHT',CYAN,True)
    app.put(7,split+2,'─'*(app.w-split-6),NAVY)
    width=app.w-split-5
    row=8
    for i,choice in enumerate(view.choices):
        current=i==app.i
        prefix=f'{"◆" if current else " "} {i+1} '
        for n,line in enumerate(wrap(choice,width-len(prefix))[:2]):
            body=(prefix if not n else ' '*len(prefix))+line
            app.put(row,split+2,body.ljust(width),CYAN if current else WHITE,current,current)
            row+=1
    status=max(15,row+1)
    app.put(status,split+2,'TARTARUS '+'─'*(width-9),TEAL,True)
    app.put(status+1,split+2,f'{view.block}  {view.progress}'[:width],WHITE,True)
    for n,line in enumerate(wrap(view.field_next,width)[:2],status+2):
        if n<=app.h-5:app.put(n,split+2,line,TEAL)
    if view.earlier and len(wrap(view.field_next,width))<=1 and status+3<=app.h-5:
        app.put(status+3,split+2,view.earlier,TEAL)
    for n,line in enumerate(view.deadlines,status+4):
        if n<=app.h-5:app.put(n,split+2,line[:width],GOLD)


def roster_offset(elapsed):
    p=max(0.,min(1.,elapsed/ROSTER_SECONDS))
    return round(11*(1-p)**3)


def draw_roster(app,view,elapsed):
    """Entry motion only changes presentation. Inputs stay live at every frame."""
    app.frame(view.title,'↑↓ SELECT  ↵ TOGGLE  S DEPLOY  ESC BACK')
    split=_divide(app.w)
    offset=roster_offset(elapsed)
    x=4+offset
    app.put(6,x,f'● Makoto  [LOCKED]   {len(view.picked)+1}/4 ACTIVE',TEAL)
    app.put(7,x,'─'*(split-x-1),NAVY)
    app.choices(tuple(('● ' if n in view.picked else '○ ')+n for n in view.names),
                8,x,split-x-1,step=1)
    if view.absence:app.put(17,4,view.absence,DIM)
    hp,sp=view.vitals
    name=view.names[app.i]
    app.put(8,split+3,name.upper(),CYAN,True)
    app.put(9,split+3,'─'*(app.w-split-7),NAVY)
    app.put(11,split+3,f'{hp} HP  /  {sp} SP',TEAL)
