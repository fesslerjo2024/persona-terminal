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
    rows = tuple(Operation(n['id'],n['title'],n.get('map_mark',''),
                 'clear' if not app.testing and n['id'] in cleared else
                 'open' if app.store.can_play(n['id']) else 'locked',
                 cleared.get(n['id'],'') if not app.testing else '',idx==active)
                 for idx,n in enumerate(nodes))
    row = rows[active]
    if row.status=='locked':
        if active:
            required = nodes[active-1]['title']
        elif app.ch:
            required = app.nodes(app.ch-1)[-1]['title']
        else:
            required = 'the previous operation'
        detail = f'Clear {required} first.'
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
            ('G ANIMATION GALLERY  T CLASSIC TRIALS' if view.testing
             else 'H HELP  T CLASSIC TRIALS')+'  ESC TITLE')
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
    width=app.w-4
    half=width//2
    gap=min(half-1,round(half*(elapsed/.74)**.7))
    left=half-gap
    right=width-half-gap
    app.put(2,2,'╾'+'═'*(left-1),GREEN,True)
    if right:
        app.put(2,2+width-right,'═'*(right-1)+'╼',GREEN,True)
    if gap:
        app.put(2,2+left,'·'*(gap*2),DIM)
