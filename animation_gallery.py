"""Read-only animation previews, independent of campaign progress and battle state."""
from dataclasses import dataclass
import curses as C
import time

from battle_ui import BattleUI, ENTER, ESC, GOLD, CYAN, WHITE, DIM
import cutins


@dataclass(frozen=True)
class Clip:
    title: str
    subtitle: str
    detail: str
    hp: tuple[int, int] | None = None


@dataclass(eq=False)
class PreviewHP:
    hp: int
    max_hp: int = 100


def catalog():
    order = tuple(cutins.ALL_OUT)
    return (
        ('SHOWTIMES', tuple(Clip(*card, ' + '.join(n for n in order if n in pair) + ' / ASCII scene')
                            for pair, card in cutins.SHOWTIMES.items())),
        ('ALL-OUT ATTACKS', tuple(Clip(*card, name + ' / animated finisher')
                                  for name, card in cutins.ALL_OUT.items())),
        ('ORACLE SUPPORT', (
            Clip(*cutins.ORACLE_SUPPORT, 'Futaba / squad support'),
            Clip(*cutins.FINAL_GUARD, 'Futaba / protects against a fatal hit'),
            Clip(*cutins.ORACLE, 'Futaba / animated aerial All-Out Attack'),
        )),
        ('BATTLE EFFECTS', (
            Clip('DAMAGE FLASH', 'Lost HP flashes red and drains to the new total.', 'HP bar / normal damage', (100, 56)),
            Clip('FINAL HIT / WAVE CLEAR', 'The last Shadow falls and the next formation comes in.', 'HP bar / knockout', (68, 0)),
        )),
    )


class AnimationGallery:
    def __init__(self):
        self.groups = catalog()
        self.group = self.index = 0
        self.started = None
        self.reel = False

    @property
    def clips(self):
        return self.groups[self.group][1]

    @property
    def clip(self):
        return self.clips[self.index]

    def _advance(self, now):
        if not self.reel:
            self.started = None
        elif self.index + 1 < len(self.clips):
            self.index += 1
            self.started = now
        elif self.group + 1 < len(self.groups):
            self.group += 1
            self.index = 0
            self.started = now
        else:
            self.reel = False
            self.started = None

    def key(self, app, key, now=None):
        now = time.monotonic() if now is None else now
        if self.started is not None:
            if key == ESC:
                self.started = None
                self.reel = False
            elif key in ENTER or key == ' ':
                self._advance(now)
            elif key in ('r', 'R'):
                self.started = now
            return True
        if key == ESC:
            return False
        if key in (C.KEY_LEFT, C.KEY_RIGHT):
            self.group = (self.group + (1 if key == C.KEY_RIGHT else -1)) % len(self.groups)
            self.index = 0
            return True
        if key in ('p', 'P'):
            self.group = self.index = 0
            self.reel = True
            self.started = now
            return True
        self.index = app.nav(key, self.index, len(self.clips))
        choice = app.commit(key, self.index, len(self.clips))
        if choice is not None or key in ('r', 'R', ' '):
            if choice is not None:
                self.index = choice
            self.started = now
        return True

    def draw(self, app, now=None):
        now = time.monotonic() if now is None else now
        clip = self.clip
        if self.started is not None:
            duration = 2.0 if clip.hp else cutins.duration(clip.title)
            if now - self.started >= duration:
                self._advance(now)
                clip = self.clip
        if self.started is None:
            app.frame('METAVERSE / ANIMATION GALLERY', '←→ CATEGORY  ↑↓ SELECT  ENTER PLAY  P PLAY ALL  ESC BACK')
            app.put(4, 3, '◆  ANIMATION GALLERY', GOLD, True)
            app.put(6, 3, f'‹  {self.groups[self.group][0]}  ›   {self.group+1}/{len(self.groups)}', CYAN, True)
            app.put(7, 3, 'Preview only. Story progress is not used.', DIM)
            rows = [(c.title, c.detail, True) for c in self.clips]
            app._b_list(rows, 9, 4, app.w-8, app.h-15, self.index)
            app.put(app.h-5, 4, clip.detail, GOLD)
            return
        elapsed = now - self.started
        footer = 'ENTER NEXT  R REPLAY  ESC STOP' if self.reel else 'ENTER / ESC BACK  R REPLAY'
        if clip.hp is None:
            app.draw_cutin(clip.title, clip.subtitle, elapsed, footer=footer)
            return
        app.frame('METAVERSE / BATTLE EFFECT', footer)
        app.mid(6, clip.title, GOLD, True)
        app.mid(9, clip.subtitle, WHITE)
        before, after = clip.hp
        impact = self.started + 0.35
        unit = PreviewHP(before if now < impact else after)
        app.mid(12, f'SHADOW HP   {unit.hp}/{unit.max_hp}', CYAN, True)
        width = min(36, app.w-12)
        # Use the real battle renderer but give it an isolated simulator state.
        renderer = HPPreview(app, {unit: (before, impact)} if now >= impact else {})
        renderer.draw(14, (app.w-width)//2, unit, width, now)
        if after == 0 and elapsed > 1.07:
            app.mid(17, 'WAVE CLEARED  /  NEXT FORMATION INCOMING', GOLD, True)


class HPPreview:
    def __init__(self, app, trails):
        self._b_put = app._b_put
        self._b_hp_trails = trails

    draw = BattleUI._b_hp_draw
