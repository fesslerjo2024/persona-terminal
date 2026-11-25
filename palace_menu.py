"""Shared Palace navigation chrome and read-only render inputs."""
from dataclasses import dataclass
from functools import lru_cache
from importlib import import_module

from battle_ui import RED, GOLD, CYAN, WHITE, DIM, GREEN
from reel_palette import IDS


@dataclass(frozen=True)
class Operation:
    id: str
    title: str
    mark: str
    status: str
    medal: str
    selected: bool


@dataclass(frozen=True)
class MapView:
    rows: tuple[Operation, ...]
    selected: int
    testing: bool
    detail: str
    motion: float = 1.0
    previous: int = 0
    cleared: int = 0


@dataclass
class Timeline:
    state: tuple[str, int] | None = None
    previous: int = 0
    at: float | None = None

    def cue(self, chapter, selected, now):
        state = (chapter, selected)
        if self.state != state:
            self.previous = self.state[1] if self.state and self.state[0] == chapter else selected
            self.at = now if self.state is not None else None
            self.state = state
        return (1. if self.at is None else min(1., max(0., now-self.at)), self.previous)


@dataclass(frozen=True)
class Skin:
    accent: int
    brief: str
    seam: str
    ruled: str = '─'
    brackets: tuple[str, str] = ('┌', '┐')


SKINS = {
    'castle':     Skin(IDS['amber'], 'GUARD ORDERS', '|', '═', ('╒','╕')),
    'museum':     Skin(IDS['rose'], 'EXHIBIT LABEL', '│', '─', ('╔','╗')),
    'bank':       Skin(IDS['ochre'], 'DEPOSIT SLIP', ':', '·', ('[',']')),
    'pyramid':    Skin(IDS['teal'], 'CHAMBER TABLET', '▏', '·', ('╱','╲')),
    'spaceport':  Skin(GREEN, 'FACTORY DISPATCH', '┃', '━', ('▛','▜')),
    'casino':     Skin(GOLD, 'ELEVATOR PASS', '│', '═', ('╟','╢')),
    'cruiser':    Skin(IDS['navy'], 'BOARDING PASS', '┊', '┄', ('╭','╮')),
    'depths':     Skin(IDS['violet'], 'ROUTE RECORD', '│', '╌', ('○','○')),
    'laboratory': Skin(CYAN, 'TREATMENT TERMINAL', '│', '─'),
}

THEME_MODULES = ('palace_early_themes', 'palace_middle_themes', 'palace_casino_theme', 'palace_late_themes')


@lru_cache(maxsize=1)
def renderers():
    result = {}
    for module in THEME_MODULES:
        for id, renderer in import_module(module).THEMES.items():
            if id in result:
                raise ValueError(f'Duplicate Palace menu for {id!r}.')
            result[id] = renderer
    if result.keys() != SKINS.keys():
        raise ValueError('Every Palace needs one renderer and one skin.')
    return result


def map_view(app, now):
    chapter = app.chapters[app.ch]['id']
    nodes = app.nodes()
    cleared = app.store.data['cleared']
    active = app.pick
    rows = []
    for idx, node in enumerate(nodes):
        key = node['id']
        can_play = app.store.can_play(key)
        medal = '' if app.testing else cleared.get(key, '')
        status = 'clear' if medal else 'open' if can_play else 'locked'
        rows.append(Operation(key, node['title'] if can_play else '???',
                              node.get('map_mark', '') if can_play else '',
                              status, medal, idx == active))
    rows = tuple(rows)
    if rows[active].status == 'locked':
        detail = 'Locked. Clear the previous operation to reveal it.'
    else:
        detail = nodes[active].get('brief','')
    elapsed, previous = app.palace_timeline.cue(chapter,active,now)
    return MapView(rows,active,app.testing,detail,elapsed,previous,
                   sum(r.status=='clear' for r in rows))


def map_screen(app, now):
    chapter=app.chapters[app.ch]
    skin=SKINS[chapter['id']]
    view=map_view(app,now)
    footer=('←→ PALACE  ↑↓ PICK  ↵ BRIEF  S SQUAD  V VELVET',
            'T CLASSIC TRIALS  ESC EXTRAS' if view.testing else 'H FIELD DRILL  ESC TITLE')
    app.frame('PALACE MAP',footer,accent=skin.accent)
    progress='' if view.testing else f'  /  {view.cleared}/{len(view.rows)} CLEARED'
    app.put(4,3,(chapter['title'].upper()+progress)[:app.w-6],skin.accent,True)
    count=app.opened()
    tabs='  /  '.join(f'[ {app.label(i)} ]' if i==app.ch else app.label(i) for i in range(count))
    if len(tabs)>app.w-6:
        tabs=f'‹ {app.label((app.ch-1)%count)}  [ {app.label()} ]  {app.label((app.ch+1)%count)} ›  {app.ch+1}/{count}'
    app.put(5,3,tabs[:app.w-6],DIM,True)
    renderers()[chapter['id']](app,view)
    y=app.h-7
    app.put(y,3,skin.ruled*(app.w-6),skin.accent)
    current=view.rows[view.selected]
    app.lines(y+1,3,view.detail,app.w-6,3,GOLD if current.status=='locked' else WHITE)
    if app.notice:
        # A save/load or rejected action is more important than the last
        # line of detail, and it belongs next to what the player can do next.
        app.put(app.h-4,3,app.notice[:app.w-6].ljust(app.w-6),GOLD,True)


def brief_frame(app, chapter, heading, footer):
    skin = SKINS[chapter]
    app.frame(skin.brief,footer,accent=skin.accent)
    app.put(4,3,heading[:app.w-6],skin.accent,True)
    bottom = app.h-4 if not app.notice else app.h-5
    # A ledger, display plaque, ticket or readout: a decorative form detail
    # never consumes a copy row or doubles as an instruction.
    left,right=skin.brackets
    app.put(5,1,left+skin.ruled*(app.w-5)+right,skin.accent)
    if chapter in ('bank','spaceport','cruiser','laboratory'):
        app.put(11,3,skin.ruled*(app.w-6),DIM)
    # Themed slip/record edge, not a second header or instruction block.
    for y in range(6,bottom+1):
        app.put(y,1,skin.seam,skin.accent)
        app.put(y,app.w-3,skin.seam,skin.accent)
    if app.notice:app.put(app.h-4,3,app.notice[:app.w-6],GOLD,True)
    return skin


def transition_frame(app, chapter, footer):
    skin=brief_frame(app,chapter['id'],chapter['title'].upper(),footer)
    app.lines(8,3,chapter.get('brief','A new Palace is open.'),app.w-6,5)
    app.put(7,3,skin.ruled*(app.w-6),skin.accent)


def airlock(app, elapsed):
    """A brief sliding header hatch; battle controls remain live underneath."""
    if not 0<=elapsed<.74:
        return
    app.put(2,2,' '*(app.w-4),DIM)
    for x, run, color in _airlock_strip(app.w-4, round(elapsed/.74*50)):
        app.put(2,2+x,run,color,True)


@lru_cache(maxsize=72)
def _airlock_strip(width,frame):
    """A four-dot-tall row of retracting pressure doors and an active seal."""
    from detail_canvas import DotCanvas
    canvas=DotCanvas(width,1)
    span=canvas.w
    half=span//2
    gap=min(half,round(half*(frame/50)**.75))
    for i in range(0,span-1,9):
        canvas.put(i,2,'slate')
    for side in (-1,1):
        limit=half+side*gap
        for j in range(3,width,3):
            x=limit+side*j*2
            canvas.line((x,1),(x+side*2,0),'forest')
            canvas.line((x,2),(x+side*2,3),'forest')
        canvas.line((limit+side*3,0),(limit+side*3,3),'green')
        canvas.line((limit+side*2,1),(limit+side*6,1),'white' if frame<11 else 'teal')
    inks={'white':WHITE,'green':GREEN,**IDS}
    rows=canvas.finish()
    x=0
    ret=[]
    for run,pigment in rows[0]:
        if run.strip():ret.append((x,run,inks[pigment]))
        x+=len(run)
    return tuple(ret)
