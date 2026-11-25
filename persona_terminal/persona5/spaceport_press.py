"""One route switch before the Spaceport's press-side patrol."""
from dataclasses import dataclass

from .battle_ui import CYAN, GOLD, GREEN, WHITE, ENTER, ESC
from . import persona5_story_art as art

CROSSING_SECONDS = 8
_BREAKS = (('Short Break', 5), ('Lunch Break', 30))


@dataclass
class PressConsole:
    pick: int = 0
    held_for: int = 0

    @property
    def can_cross(self):
        return self.held_for >= CROSSING_SECONDS

    def key(self, app, key):
        if key == ESC:
            return 'back'
        if self.can_cross:
            return 'cross' if key in ENTER else None
        self.pick = app.nav(key, self.pick, len(_BREAKS))
        chosen = app.commit(key, self.pick, len(_BREAKS))
        if chosen is not None:
            self.pick = chosen
            self.held_for = _BREAKS[chosen][1]
        return None

    def draw(self, app):
        opening = self.can_cross
        app.panel('SPACEPORT / SHIFT CONTROL', 'HYDRAULIC PRESS',
                  '↵ CROSS  ESC BACK' if opening else '↑↓ SELECT  ↵ SET BREAK  ESC BACK')
        width=min(app.w-6,max(43,round(app.w*.67)))
        art.draw(app,art.press,(app.w-width)//2,5,width,7,
                 opening=opening,failed=bool(self.held_for and not opening))
        if opening:
            app.mid(13, 'PRESS LOCKED OPEN', GREEN, True)
            app.lines(15, 3, 'The ram lifts. Oracle has a clear line to the catwalk; the patrol is still on the far side.',
                      limit=2, color=WHITE)
        else:
            app.lines(13, 3, f'Oracle: We need {CROSSING_SECONDS} seconds to get everyone across.',
                      limit=2, color=CYAN)
            app._b_list([(f'{name}  /  {duration}s', '', True) for name, duration in _BREAKS],
                        16, 3, app.w-6, len(_BREAKS), self.pick)
            if self.held_for:
                app.lines(19, 3, f'The ram drops after {self.held_for}s. The crew stays back.',
                          limit=2, color=GOLD)
