"""Dark Hour calendar board and the short repeat-departure cue.

The controller owns dates, activities and dispatch. Drawing never advances
time or writes progress.
"""
from calendar import Calendar
from dataclasses import dataclass
from datetime import date

from battle_ui import CYAN,DIM,GOLD,WHITE
from reel_palette import IDS
from persona3_opening import TRANSITION_SECONDS,render

BLUE=IDS['navy']
TEAL=IDS['teal']
ROSE=IDS['rose']
DARK_BLUE=IDS['slate']
NIGHT_SWEEP_SECONDS=1.05
MONTH_DAYS=('MON','TUE','WED','THU','FRI','SAT','SUN')
MARKS={'moon':('●',GOLD),'rescue':('!',ROSE),'event':('◆',TEAL),'open':('·',DARK_BLUE)}


@dataclass(frozen=True)
class CalendarView:
    day:date
    full_moons:frozenset[date]
    rescues:frozenset[date]
    events:frozenset[date]
    stat_lines:tuple
    choices:tuple
    detail:str=''
    cue:tuple=()


def marker(day,view):
    if day in view.full_moons:return 'moon'
    if day in view.rescues:return 'rescue'
    if day in view.events:return 'event'
    if day>=view.day:return 'open'
    return None


def draw(app,view):
    width=30
    seam=32 if app.w<82 else min(40,app.w//2-3)
    right=seam+2
    left=2+(seam-32)//2
    # The two rails form one board with a calendar cassette on the left
    # and the selectable time slots on the right.
    for y in range(5,21):app.put(y,seam,'│',BLUE)
    app.put(5,left,'╭'+'─'*(width-2)+'╮',BLUE)
    for n,label in enumerate(MONTH_DAYS):
        app.put(6,left+1+4*n,label,TEAL if n<5 else CYAN)
    weeks=Calendar().monthdayscalendar(view.day.year,view.day.month)
    for row,week in enumerate(weeks,7):
        for n,number in enumerate(week):
            if not number:continue
            day=view.day.replace(day=number)
            selected=day==view.day
            event=marker(day,view)
            badge,color=MARKS.get(event,(' ',DIM))
            x=left+1+4*n
            app.put(row,x,f'{number:>2}',CYAN if selected else WHITE if day>=view.day else DIM,selected,selected)
            if event:app.put(row,x+2,badge,color,selected)
    app.put(13,left,'╰'+'─'*(width-2)+'╯',BLUE)
    for i,(name,label) in enumerate((('moon','MOON'),('rescue','CASE'),('event','EVENT'),('open','FREE'))):
        pos=left+i*7
        badge,color=MARKS[name]
        app.put(14,pos,badge,color,True)
        app.put(14,pos+2,label,DIM)
    for y,(value,ink) in enumerate(view.stat_lines,16):
        app.put(y,left,value[:seam-left-1],ink,ink==CYAN)
    app.choices(view.choices,7,right,app.w-right-3)
    if view.detail:app.lines(18,right,view.detail,app.w-right-3,3,TEAL)
    if view.cue:
        label,target=view.cue
        app.lines(18,right,label,app.w-right-3,2,TEAL)
        app.put(20,right,f'{target:%m/%d}',GOLD,True)


def departure_length(first=False):
    return TRANSITION_SECONDS if first else NIGHT_SWEEP_SECONDS


def departure(elapsed,w,h,*,first=False):
    duration=departure_length(first)
    # Keep the first Tartarus reveal. Later departures start with the dial
    # already visible, strike midnight and hold green for a brief beat.
    t=elapsed if first else .78+min(1.,max(0.,elapsed/duration))*1.9
    return render('dark_hour',t,w,h)
