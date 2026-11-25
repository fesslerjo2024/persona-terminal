"""A native Persona 3 title scene. The controller supplies save-based choices."""
from functools import lru_cache
from persona3_title_detail import render as title_reel
from wide_canvas import Canvas
from detail_canvas import DotCanvas
from reel_palette import IDS

DURATION = 3.18
TITLE = 'Persona 3 Terminal'
MENU = (('Continue', False), ('New Game', True), ('Back to Selector', True))
MENU_DEFAULT = 1


def menu(continue_ready):
    return ((MENU[0][0],continue_ready),*MENU[1:])


def render(t,w,h):
    return title_reel(max(0.,min(float(t),DURATION)),w,h)


def draw_intro(app,elapsed):
    app.draw_scene_rows(render(elapsed,app.w-1,app.h))


@lru_cache(maxsize=6)
def _title_frame(w,h):
    c=Canvas(w,h)
    c.overlay(render(DURATION,w,h),0,0)
    # A single diagonal band across the clock, in contrast with the
    # off-axis tower. It becomes a stable title placement, not a menu box.
    y=round(h*.34)
    band=max(29,round(w*.47))
    x0=max(2,round(w*.075))
    for j in range(11):
        x=x0+2-j//2
        c.put(x,y+j,' '*band,'navy',opaque=True)
    # Stepped edge, stippled rail, and beveled cuts sit in the existing
    # title strip. They are never part of the foreground labels or hitboxes.
    bevel=DotCanvas(band+5,11)
    bw=bevel.w
    bevel.path(((1,3),(14,3),(22,0),(bw-8,0)),'teal')
    bevel.line((16,4),(bw-13,4),'navy')
    bevel.path(((0,40),(11,40),(17,43),(bw-18,43)),'slate')
    for j,ink in ((8,'teal'),(33,'slate')):
        x=bw-(14 if j==8 else 24)
        for offset in (0,5):
            bevel.line((x+offset,j),(x+offset-5,j+6),ink)
    c.overlay(bevel.finish(),x0-3,y)
    c.put(0,h-2,' '*w,'navy',opaque=True)
    return c.finish(), y, x0



def _choices(top,left,choices):
    for i,(name,enabled) in enumerate(choices):
        yield top+5+i*2,left+2,name,enabled


def draw_menu(app,selection=MENU_DEFAULT,choices=MENU,notice=''):
    rows,y,x=_title_frame(app.w-1,app.h)
    app.draw_scene_rows(rows)
    app.put(y+2,x+1,TITLE,IDS['teal'],True)
    for i,(row,xx,name,enabled) in enumerate(_choices(y,x,choices)):
        active=i==selection
        mark='▶' if active else ' '
        lock=' ' if enabled else '×'
        color=IDS['teal'] if enabled else IDS['slate']
        app.put(row,xx,f'{mark} {lock} {name}'.ljust(23),color,active,active and enabled)
    if notice:app.put(app.h-4,3,notice[:app.w-6],IDS['amber'],True)
    app.mid(app.h-2,'↑↓ SELECT  ↵ OPEN  ESC BACK',IDS['teal'])


def menu_hit(app,x,y):
    _,top,left=_title_frame(app.w-1,app.h)
    return next((i for i,(row,xx,_,_) in enumerate(_choices(top,left,MENU))
                 if y==row and xx<=x<xx+23),None)
