"""The offline title picker, separate from campaign save configuration."""
from dataclasses import dataclass
import curses as C
import time

from battle_ui import CYAN, DIM, ENTER, ESC, GOLD, RED, WHITE
from terminal_surface import TerminalSurface
from persona3_state import DEFAULT_SAVE as DEFAULT_P3_SAVE, P3Store, P3SaveError
from suite_art import OPEN_SECONDS, PULSE_SECONDS, TUMBLE_SECONDS, emblem_runs


@dataclass(frozen=True)
class Title:
    number: int
    enabled: bool
    ink: int
    animation_seconds: float = PULSE_SECONDS
    opening_seconds: float = OPEN_SECONDS


TITLES=(
    Title(3,True,CYAN),
    Title(4,False,GOLD),
    Title(5,True,RED,TUMBLE_SECONDS,TUMBLE_SECONDS),
)


@dataclass(frozen=True)
class Card:
    left: int
    top: int
    width: int
    height: int

    def contains(self,x,y):
        return self.left<=x<self.left+self.width and self.top<=y<self.top+self.height


def cards(width,height):
    card_width=min(31,(width-8)//3)
    gap=2 if width<76 else 3
    total=3*card_width+gap*2
    left=(width-total)//2
    top=max(5,height//2-7)
    return tuple(Card(left+i*(card_width+gap),top,card_width,13) for i in range(3))


def draw(app,selection,elapsed=None):
    app.mid(max(2,app.h//2-10),'P E R S O N A   /   T E R M I N A L',WHITE,True)
    for i,(title,card) in enumerate(zip(TITLES,cards(app.w,app.h))):
        x,y,w=card.left,card.top,card.width
        active=i==selection
        ink=title.ink
        app.put(y,x,'╔'+'═'*(w-2)+'╗',ink,active)
        for dy in range(1,card.height-1):
            app.put(y+dy,x,'║',ink)
            app.put(y+dy,x+w-1,'║',ink)
        app.put(y+card.height-1,x,'╚'+'═'*(w-2)+'╝',ink,active)
        for dy,row in enumerate(emblem_runs(title.number,w-2,ink,elapsed if active else None),2):
            for offset,line,color in row:app.put(y+dy,x+1+offset,line,color,True)
        label=f' PERSONA {title.number} '
        app.put(y+10,x+(w-len(label))//2,label,ink,True,active)
    app.mid(app.h-2,'←→ SELECT  ENTER / CLICK OPEN  3–5  Q QUIT',DIM)


class SuiteMenu(TerminalSurface):
    def __init__(self,screen,p3_save=DEFAULT_P3_SAVE,seed=None):
        self.s=screen;self.p3_save=p3_save;self.seed=seed
        self.selection=0
        self.pulse_started=None

    @staticmethod
    def _click():
        try:_,x,y,_,buttons=C.getmouse()
        except C.error:return None
        if not buttons & (C.BUTTON1_CLICKED|C.BUTTON1_RELEASED):
            return None
        return x,y

    def _pulse(self):
        self.pulse_started=time.monotonic()

    def choose(self,k):
        """Return a title number only for a committed, enabled card."""
        if k in (C.KEY_LEFT,C.KEY_UP,C.KEY_RIGHT,C.KEY_DOWN):
            step=-1 if k in (C.KEY_LEFT,C.KEY_UP) else 1
            self.selection=(self.selection+step)%len(TITLES)
            self._pulse()
            return None
        if k==C.KEY_MOUSE:
            point=self._click()
            if point is None:return None
            target=next((i for i,card in enumerate(cards(self.w,self.h)) if card.contains(*point)),None)
            if target is None:return None
            self.selection=target
        elif isinstance(k,str) and k in ('3','4','5'):
            self.selection=int(k)-3
        elif k not in ENTER:return None
        title=TITLES[self.selection]
        self._pulse()
        return title.number if title.enabled else None

    def _preview(self):
        import persona3_title
        from persona3_app import P3App

        store=P3Store(self.p3_save)
        started=None;skipped=False;confirming=False
        selection=0 if store.status=='ready' else persona3_title.MENU_DEFAULT
        notice={'unreadable':'Persona 3 save could not be read.',
                'foreign':'Choose a separate Persona 3 save path.'}.get(store.status,'')
        self.s.timeout(32)
        mouse=False
        try:
            while True:
                self.s.erase();self.h,self.w=self.s.getmaxyx()
                small=self.h<25 or self.w<65
                now=time.monotonic()
                if started is None and not small:started=now
                intro=not skipped and (started is None or now-started<persona3_title.DURATION)
                if not mouse and not small and not intro:
                    self._mouse(C.BUTTON1_CLICKED|C.BUTTON1_RELEASED)
                    self.s.timeout(80)
                    mouse=True
                choices=persona3_title.menu(store.status=='ready')
                if small:self._size_notice()
                elif intro:persona3_title.draw_intro(self,now-started)
                elif confirming:
                    self.mid(5,'PERSONA 3 / NEW GAME',CYAN,True)
                    self.mid(9,'Start over and back up the existing Persona 3 save?',WHITE)
                    self.mid(self.h-2,'N CONFIRM  ESC KEEP SAVE',CYAN)
                    if notice:self.mid(self.h-4,notice,GOLD)
                else:persona3_title.draw_menu(self,selection,choices,notice)
                self.s.refresh()
                try:k=self.s.get_wch()
                except C.error:continue
                if k in ('q','Q'):return False
                if small:continue
                if intro:
                    if k in (*ENTER,ESC,' '):skipped=True
                    continue
                if confirming:
                    if k==ESC:confirming=False;notice=''
                    elif k not in ('n','N'):continue
                    else:
                        try:store.new_game(confirm=True)
                        except (OSError,P3SaveError) as exc:notice=str(exc);continue
                        confirming=False
                        self._mouse(0);mouse=False
                        if not P3App(self.s,store,self.seed).run():return False
                        store.reload();selection=0;notice=''
                    continue
                if k==ESC:return True
                if k==C.KEY_UP:selection=(selection-1)%len(choices)
                elif k==C.KEY_DOWN:selection=(selection+1)%len(choices)
                elif k in ('1','2','3'):selection=int(k)-1
                elif k==C.KEY_MOUSE:
                    point=self._click()
                    target=persona3_title.menu_hit(self,*point) if point else None
                    if target is None:continue
                    selection=target
                elif k not in ENTER:continue
                if k not in (*ENTER,'1','2','3',C.KEY_MOUSE):continue
                if selection==2:return True
                if selection==0:
                    store.reload()
                    if store.status!='ready':notice='No readable Persona 3 save.';continue
                elif store.status=='foreign':
                    notice='That save belongs to another game.';continue
                elif store.status!='missing':
                    confirming=True;notice='';continue
                else:
                    try:store.new_game()
                    except (OSError,P3SaveError) as exc:notice=str(exc);continue
                self._mouse(0);mouse=False
                if not P3App(self.s,store,self.seed).run():return False
                store.reload();selection=0;notice=''
        finally:
            if mouse:self._mouse(0)

    def _size_notice(self):
        self.mid(self.h//2,'Widen the terminal to at least 65 × 25. Q quits.',GOLD)

    @staticmethod
    def _mouse(mask):
        try:C.mousemask(mask)
        except C.error:pass  # Keyboard remains available with no mouse reporting.

    def _selection(self):
        self._mouse(C.BUTTON1_CLICKED|C.BUTTON1_RELEASED)
        self.s.timeout(32)
        pending=None
        try:
            while True:
                self.s.erase();self.h,self.w=self.s.getmaxyx()
                small=self.h<25 or self.w<65
                now=time.monotonic()
                elapsed=None if self.pulse_started is None else now-self.pulse_started
                title=TITLES[self.selection]
                if small:self._size_notice()
                elif pending is not None and elapsed>=title.opening_seconds:return pending
                else:
                    moment=elapsed*title.animation_seconds/title.opening_seconds if pending is not None else elapsed
                    draw(self,self.selection,moment)
                self.s.refresh()
                try:k=self.s.get_wch()
                except C.error:continue
                if k in ('q','Q'):return None
                if k==ESC:
                    if pending is None:return None
                    pending=None
                elif not small and pending is None:
                    # Input while opening never leaks into a game's intro.
                    pending=self.choose(k)
        finally:self._mouse(0)

    def run(self,open_persona5):
        while (choice:=self._selection()) is not None:
            if choice==3:
                if not self._preview():return
            elif not open_persona5():return
