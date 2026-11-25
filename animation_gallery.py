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
            app.put(7, 3, 'During playback: Enter skips, R replays, Esc stops.', DIM)
            rows = [(c.title, c.detail, True) for c in self.clips]
            app._b_list(rows, 9, 4, app.w-8, app.h-15, self.index)
            app.put(app.h-5, 4, clip.detail, GOLD)
            return
        elapsed = now - self.started
        if clip.hp is None:
            app.draw_cutin(clip.title, elapsed)
            return
        before, after = clip.hp
        impact = self.started + 0.35
        unit = PreviewHP(before if now < impact else after)
        width = min(36, app.w-12)
        renderer = HPPreview(app, {unit: (before, impact)} if now >= impact else {})
        center = app.h//2
        if after > 0 or elapsed < 1.08:
            app.mid(center-4, r' /\\_/\\ ', DIM if after == 0 and elapsed>.76 else WHITE, True)
            app.mid(center-3, ' ( * * ) ', GOLD if .35<elapsed<.53 else WHITE, True)
            renderer.draw(center,(app.w-width)//2,unit,width,now)
        if after == 0 and elapsed > 1.07:
            # Show the defeated silhouette breaking up, then the new wave
            # entering in formation. No announcer text in the effects reel.
            tick=int((elapsed-1.07)*14)
            if elapsed < 1.48:
                app.mid(center-3,' .  *    .  ' if tick%2 else '   .   .  ',DIM)
            else:
                shift=max(0,round((1.86-elapsed)*24))
                for i,x in enumerate((-12,0,12)):
                    app.put(center-4,app.w//2-3+x+shift,r' /\\_/\\ ', DIM if tick%2 else CYAN, True)
                    app.put(center-3,app.w//2-3+x+shift,' ( * * ) ', GOLD if i==1 else CYAN, True)



class HPPreview:
    def __init__(self, app, trails):
        self._b_put = app._b_put
        self._b_hp_trails = trails

    draw = BattleUI._b_hp_draw
