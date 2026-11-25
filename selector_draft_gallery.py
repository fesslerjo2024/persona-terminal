"""An isolated, save-free viewer for the Persona selector icon candidates."""
import curses as C
from functools import lru_cache
from importlib import import_module
from math import cos, pi
from time import monotonic

from detail_canvas import DotCanvas
from reel_palette import IDS,install

TITLES=(3,4,5)
INKS={'red':1,'gold':2,'cyan':3,'white':4,'dim':5,'green':6,**IDS}
ACCENTS={3:3,4:2,5:1}
SECONDS=1.45


@lru_cache(maxsize=3)
def candidates(title):
    if title not in TITLES:
        raise ValueError('No selector drafts for that game.')
    return import_module(f'selector_drafts_p{title}').DRAFTS


@lru_cache(maxsize=320)
def picture(title,index,w,h,frame=36):
    c=DotCanvas(w,h)
    candidates(title)[index][1](c,frame/36)
    return c.finish()


def _preview(screen):
    C.start_color()
    try:C.use_default_colors();bg=-1
    except C.error:bg=C.COLOR_BLACK
    try:C.curs_set(0)
    except C.error:pass
    if hasattr(C,'set_escdelay'):C.set_escdelay(55)
    pairs=(203,221,51,255,247,84) if C.COLORS>=256 else (
        C.COLOR_RED,C.COLOR_YELLOW,C.COLOR_CYAN,C.COLOR_WHITE,C.COLOR_WHITE,C.COLOR_GREEN)
    for i,color in enumerate(pairs,1):C.init_pair(i,color,bg)
    install(bg)
    screen.keypad(True)
    title,index,started=3,0,None
    while True:
        h,w=screen.getmaxyx()
        screen.erase()
        accent=ACCENTS[title]

        def put(y,x,txt,color=4,bold=False,reverse=False):
            if 0<=y<h-1 and 0<=x<w-1:
                try:screen.addnstr(y,x,txt,w-1-x,C.color_pair(color)
                                   | (C.A_BOLD if bold else 0) | (C.A_REVERSE if reverse else 0))
                except C.error:pass

        def draw_art(y,x,rows):
            for j,row in enumerate(rows):
                col=x
                for run,ink in row:
                    if run.strip():put(y+j,col,run,INKS[ink])
                    col+=len(run)

        def mid(y,txt,color=4,bold=False):
            put(y,max(0,(w-len(txt))//2),txt,color,bold)

        if w<65 or h<25:
            mid(h//2,'Resize to at least 65 × 25. Q quits.',4,True)
            screen.timeout(80)
        elif started is not None:
            p=min(1.,(monotonic()-started)/SECONDS)
            aw=min(38,w-8);ah=min(16,h-9)
            step=round((1-cos(pi*p))*18)
            name=candidates(title)[index][0]
            mid(2,f'PERSONA {title}  /  {title}-{index+1}  {name}',accent,True)
            draw_art((h-ah)//2,(w-aw)//2,picture(title,index,aw,ah,step))
            mid(h-2,'ENTER REPLAY   ESC COMPARE',5)
            screen.timeout(35 if p<1 else 90)
        else:
            mid(1,'SELECTOR ICONS  /  PREVIEW',4,True)
            mid(3,'  '.join(f'[{i} PERSONA {i}]' if i==title else f'{i} PERSONA {i}' for i in TITLES),accent)
            cw=min(35,(w-5)//3)
            rh=min(13,(h-6)//3)
            x0=(w-cw*3)//2
            y0=5+(h-6-rh*3)//2
            for i,(name,_) in enumerate(candidates(title)):
                y=y0+(i//3)*rh
                x=x0+(i%3)*cw
                label=f'{title}-{i+1} {name}'
                label=label[:cw-2]
                put(y,x+1,label.center(cw-2),accent if i==index else 5,i==index,i==index)
                aw,ah=min(26,cw-2),min(11,rh-1)
                draw_art(y+1,x+(cw-aw)//2,picture(title,i,aw,ah))
            mid(h-2,'3–5 GAME   ARROWS SELECT   ENTER PLAY   ESC QUIT',5)
            screen.timeout(95)
        screen.refresh()
        try:key=screen.get_wch()
        except C.error:continue
        if key in ('q','Q'):break
        if key=='\x1b':
            if started is None:break
            started=None
        elif key in ('3','4','5'):
            title,index,started=int(key),0,None
        elif key in (C.KEY_LEFT,C.KEY_RIGHT,C.KEY_DOWN,C.KEY_UP):
            index=(index+{C.KEY_LEFT:-1,C.KEY_RIGHT:1,C.KEY_DOWN:3,C.KEY_UP:-3}[key])%9
            if started is not None:started=monotonic()
        elif key in ('\n','\r',' ',C.KEY_ENTER):
            started=monotonic()


if __name__=='__main__':
    try:C.wrapper(_preview)
    except KeyboardInterrupt:pass
