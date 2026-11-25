"""Save-free entry points to Persona 3's existing combat and animation renderers."""
from dataclasses import dataclass
from functools import partial
import curses as C
from time import monotonic

from battle_ui import CYAN, DIM, ENTER, ESC, GOLD, GREEN, RED, WHITE
import persona3_cinematics as cinema
from persona3_allout import FINISHERS, FINISH_SECONDS, IMPACT_SECONDS, render_all_out
import persona3_combat as combat
import persona3_hotel_art as hotel
from persona3_late import when
from persona3_menu_motion import ELEVATOR_SECONDS, render_elevator
import persona3_opening as opening
from persona3_summit import SUMMIT_LEVEL
import persona3_title as title
from reel_palette import IDS
from terminal_surface import TerminalSurface

INKS = {'red': RED, 'gold': GOLD, 'cyan': CYAN, 'white': WHITE,
        'dim': DIM, 'green': GREEN, **IDS}


@dataclass(frozen=True)
class Encounter:
    key: str
    month: int
    day: int
    level: int
    party: tuple[str, ...] = ('Yukari','Junpei')

    @property
    def label(self):
        return combat.ENCOUNTERS[self.key][0]

    def start(self, seed=None):
        """Build a fresh practice lineup. Never create or read a campaign store."""
        day = when(self.month,self.day)
        enabled = day >= when(6,13)
        roster = (combat.LEAD_ID, *self.party)
        if self.key == 'awakening':
            roster = (combat.LEAD_ID,)
        stock_names = (('Orpheus',) if self.key == 'awakening' else
                       ('Orpheus','Pixie','Angel','Apsaras') if not enabled else
                       ('Orpheus','Omoikane','Jack Frost',"Jack O'Lantern",'Take-Minakata','Principality') if self.level<12 else
                       ('Orpheus','Black Frost','Take-Minakata','Raphael','Chernobog','Surt'))
        bag = dict(combat.BAG)
        if self.level >= 12:
            bag.update(Medicine=5)
            bag.update({'Soul Drop': 3, 'Revival Bead': 2})
        if self.key.startswith('hotel-'):
            bag['Dis-Charm']=2
        return PracticeBattle(self.key, party=roster, level=self.level, day=day, seed=seed,
                              stock=dict.fromkeys(stock_names, ()), inventory=bag,
                              fuuka=day >= when(6,8), theurgy=enabled,
                              registered=(*stock_names,'Apsaras',"Jack O'Lantern",'Jack Frost') if enabled else stock_names,
                              charge={'Yukari':100} if self.key=='theurgy-drill' else {})


MID = ('Yukari','Junpei','Akihiko')
LATE = ('Yukari','Aigis','Akihiko')
PRACTICE_GROUPS = (
    ('Spring Operations', (
        Encounter('awakening',4,9,1,()),
        Encounter('thebel-patrol',4,21,2),
        Encounter('priestess',5,9,3),
        Encounter('arqa-ravens',5,24,4,MID),
        Encounter('emperor-empress',6,8,5,('Junpei','Akihiko')),
        Encounter('theurgy-drill',6,13,6,('Yukari','Akihiko','Mitsuru')),
    )),
    ('Summer Operations', (
        Encounter('hotel-hierophant',7,7,7,MID),
        Encounter('hotel-lovers',7,7,7,MID),
        Encounter('monad-door',7,18,8,MID),
        Encounter('chariot-justice',8,6,9,LATE),
        Encounter('hermit',9,5,10,LATE),
    )),
    ('Autumn & Winter', (
        Encounter('tziah-125',9,11,11,LATE),
        Encounter('fortune-strength',10,4,12,LATE),
        Encounter('takaya-jin',11,3,13,LATE),
        Encounter('hanged-man',11,3,13,LATE),
        Encounter('chidori',11,22,14,LATE),
        Encounter('winter-siblings',12,12,16,LATE),
    )),
    ('Tartarus Summit', (
        Encounter('adamah-approach',1,31,SUMMIT_LEVEL,LATE),
        Encounter('strega-jin',1,31,SUMMIT_LEVEL,LATE),
        Encounter('strega-takaya',1,31,SUMMIT_LEVEL,LATE),
        Encounter('nyx-avatar',1,31,SUMMIT_LEVEL,LATE),
    )),
)

GALLERY_GROUPS = (
    ('Story & Exploration', (
        ('Persona 3 Opening',title.DURATION,title.render),
        ('Dark Hour',opening.TRANSITION_SECONDS,partial(opening.render,'dark_hour')),
        ('Tartarus Approach',opening.STILL_SECONDS,partial(opening.render,'tartarus')),
        ('Tartarus Elevator',ELEVATOR_SECONDS,lambda t,w,h:render_elevator(t,w,h,1,22)),
        ('Champs de Fleurs',hotel.DURATION,partial(hotel.render,'intro')),
    )),
    ('Velvet Room', (
        ('Velvet Room',cinema.VELVET_SECONDS,cinema.render_velvet),
        ('Fusion Review',cinema.FUSION_REVIEW_SECONDS,cinema.render_fusion_review),
        ('Persona Fusion',cinema.FUSION_SECONDS,cinema.render_fusion),
    )),
    ('Theurgy & Oracle', (
        *((spec[0],cinema.THEURGY_SECONDS,partial(cinema.render_theurgy,spec[0]))
          for spec in combat.THEURGIES.values()),
        ('Oracle',cinema.THEURGY_SECONDS,partial(cinema.render_theurgy,'Oracle')),
    )),
    ('All-Out Attacks', (
        *((name,FINISH_SECONDS,partial(render_all_out,name)) for name in FINISHERS),
        ('Squad Rush',IMPACT_SECONDS,partial(render_all_out,'Makoto',finishing=False)),
    )),
)

PRACTICE = tuple(entry for _,group in PRACTICE_GROUPS for entry in group)
GALLERY = tuple(entry for _,group in GALLERY_GROUPS for entry in group)


class PracticeBattle(combat.P3Battle):
    def _frame(self, app, heading, footer):
        if not self.outcome and not self.overlay and self.screen=='command':
            footer='↑↓ PICK  ↵ USE  I STATUS  L LOG  ? GUIDE  ESC BACK'
        super()._frame(app,heading,footer)


class Persona3Extras(TerminalSurface):
    def __init__(self, screen, kind, seed=None):
        if kind not in ('gallery','practice'):
            raise ValueError(f'Unknown Persona 3 extra: {kind}')
        self.s=screen
        self.kind=kind
        self.seed=seed
        self.group=0
        self.selections=[0]*len(self.groups)
        self.battle=None
        self.play_since=None
        self.confirm_exit=False
        self.done=False

    @property
    def groups(self):
        return GALLERY_GROUPS if self.kind=='gallery' else PRACTICE_GROUPS

    @property
    def entries(self):
        return self.groups[self.group][1]

    @property
    def index(self):
        return self.selections[self.group]

    @index.setter
    def index(self,value):
        self.selections[self.group]=value

    def frame(self, page, footer):
        self.put(1,2,'◆ PERSONA 3 / '+page,CYAN,True)
        self.put(2,2,'─'*(self.w-4),CYAN)
        self.put(self.h-3,2,'─'*(self.w-4),CYAN)
        self.mid(self.h-2,footer,DIM)

    def draw(self):
        if self.confirm_exit:
            self.frame('BATTLE PRACTICE','ENTER LEAVE  ESC STAY')
            self.mid(9,'Leave this practice battle?',GOLD,True)
            return
        if self.battle:
            self.battle.draw(self)
            return
        if self.play_since is not None:
            _,seconds,render=self.entries[self.index]
            elapsed=monotonic()-self.play_since
            if elapsed<seconds:
                for y,runs in enumerate(render(elapsed,self.w-1,self.h)):
                    x=0
                    for value,col in runs:
                        if value.strip():self.put(y,x,value,INKS.get(col,WHITE))
                        x+=len(value)
                return
            self.play_since=None
        gallery=self.kind=='gallery'
        self.frame('ANIMATION GALLERY' if gallery else 'BATTLE PRACTICE',
                   '←→ GROUP  ↑↓ SELECT  ENTER '+('PLAY' if gallery else 'DEPLOY')+'  ESC BACK')
        name,entries=self.groups[self.group]
        self.put(4,3,f'‹ {name.upper()} ›  {self.group+1}/{len(self.groups)}',CYAN,True)
        capacity=self.h-11
        start=max(0,min(self.index-capacity+1,len(entries)-capacity))
        for i,entry in enumerate(entries[start:start+capacity],start):
            selected=i==self.index
            name=entry[0] if gallery else entry.label
            self.put(6+i-start,3,('▶ ' if selected else '  ')+name, CYAN if selected else WHITE,selected)
        if len(entries)>capacity:
            self.put(3,self.w-11,f'{self.index+1}/{len(entries)}',DIM)
        if not gallery:
            entry=entries[self.index]
            party=', '.join(('Makoto',*entry.party)) if entry.key!='awakening' else 'Makoto'
            self.put(self.h-4,3,f'LV {entry.level}  /  {party}',DIM)

    def key(self,k):
        if self.confirm_exit:
            if k in ENTER:
                self.battle=None
                self.confirm_exit=False
            elif k==ESC:self.confirm_exit=False
            return
        if self.play_since is not None:
            if k in (*ENTER,ESC,' '):self.play_since=None
            return
        if self.battle is not None:
            b=self.battle
            if k==ESC and not b.outcome and not b.overlay and b.reel is None and b.screen=='command':
                self.confirm_exit=True
            elif not b.key(k):self.battle=None
            return
        if k==ESC:
            self.done=True
        elif k in (C.KEY_LEFT,C.KEY_RIGHT):
            self.group=(self.group+(-1 if k==C.KEY_LEFT else 1))%len(self.groups)
        elif k in (C.KEY_UP,C.KEY_DOWN,'k','j'):
            self.index=(self.index+(-1 if k in (C.KEY_UP,'k') else 1))%len(self.entries)
        elif k in ENTER:
            if self.kind=='gallery':self.play_since=monotonic()
            else:self.battle=self.entries[self.index].start(self.seed)

    def run(self):
        old_delay=self.s.getdelay() if hasattr(self.s,'getdelay') else 32
        self.s.timeout(32)
        try:
            while not self.done:
                self.s.erase()
                self.h,self.w=self.s.getmaxyx()
                small=self.h<25 or self.w<65
                if small:self.mid(self.h//2,'Widen the terminal to 65 × 25. Esc goes back.',GOLD)
                else:self.draw()
                self.s.refresh()
                try:k=self.s.get_wch()
                except C.error:continue
                if small:
                    if k==ESC:self.done=True
                else:self.key(k)
        finally:
            self.s.timeout(old_delay)


def run_persona3_extra(screen, kind, seed=None):
    """Open a Persona 3 gallery or practice leaf until the player backs out."""
    Persona3Extras(screen,kind,seed).run()
