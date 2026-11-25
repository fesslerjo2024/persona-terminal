"""Read-only animation previews, independent of campaign progress and battle state."""
from dataclasses import dataclass
import curses as C
import time
from math import sin

from wide_canvas import Canvas

from battle_ui import BattleUI, ENTER, ESC, GOLD, CYAN, WHITE, DIM
import cutins


@dataclass(frozen=True)
class Clip:
    title: str
    duo: tuple[str, ...] = ()
    preview_only: bool = False
    hp: tuple[int, int] | None = None

    @property
    def duration(self):
        return 2.0 if self.hp else cutins.duration(self.title)


@dataclass(eq=False)
class PreviewHP:
    hp: int
    max_hp: int = 100


def catalog():
    order = tuple(cutins.ALL_OUT)
    return (
        ('SHOWTIMES', tuple(Clip(card[0], tuple(n for n in order if n in pair))
                            for pair, card in cutins.SHOWTIMES.items())),
        ('ALL-OUT ATTACKS', tuple(Clip(card[0]) for card in cutins.ALL_OUT.values())),
        ('ORACLE SUPPORT', (
            Clip(cutins.ORACLE_SUPPORT[0]),
            Clip(cutins.FINAL_GUARD[0], preview_only=True),
            Clip(cutins.ORACLE[0]),
        )),
        ('BATTLE EFFECTS', (
            Clip('DAMAGE FLASH', hp=(100, 56)),
            Clip('FINAL HIT / WAVE CLEAR', hp=(68, 0)),
        )),
    )


class AnimationGallery:
    def __init__(self):
        self.groups = catalog()
        self.group = self.index = 0
        self.started = None
        self.reel = False
        self.loop = False

    @property
    def clips(self):
        return self.groups[self.group][1]

    @property
    def clip(self):
        return self.clips[self.index]

    def _advance(self, now, *, manual=False):
        if self.loop:
            if manual:
                self.loop=False
                self.started=None
            else:
                self.started=now
        elif not self.reel:
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
                self.loop = False
            elif key in ('r', 'R'):
                self.started = now
            elif key in ENTER or key == ' ':
                self._advance(now,manual=True)
            return True
        if key == ESC:
            return False
        if key in (C.KEY_LEFT, C.KEY_RIGHT):
            self.group = (self.group + (1 if key == C.KEY_RIGHT else -1)) % len(self.groups)
            self.index = 0
            return True
        if key in ('l', 'L'):
            self.loop = True
            self.started = now
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
            if now - self.started >= clip.duration:
                self._advance(now)
                clip = self.clip
        if self.started is None:
            app.frame('ANIMATION GALLERY', '←→ GROUP  ↑↓ SELECT  ↵ PLAY  R REPLAY  L LOOP  P ALL  ESC BACK')
            app.put(5, 3, f'‹ {self.groups[self.group][0]} ›  {self.group+1}/{len(self.groups)}', CYAN, True)
            rows = []
            for entry in self.clips:
                extra = ' + '.join(entry.duo) if entry.duo else 'Preview only' if entry.preview_only else ''
                label = f'{entry.title}  ·  {extra}' if extra else entry.title
                rows.append((label, '', True))
            app._b_list(rows, 7, 4, app.w-8, min(len(rows),app.h-11), self.index)
            return
        elapsed = now - self.started
        if clip.hp is None:
            app.draw_cutin(clip.title, elapsed)
            return
        before, after = clip.hp
        impact = self.started + 0.35
        unit = PreviewHP(before if now < impact else after)
        # Draw a viewport-sized perspective grid around the actual health
        # effect. The health bar itself spans the useful action area.
        width = min(app.w-6,round(app.w*.80))
        app.draw_scene_rows(_effect_floor(app.w-1,app.h,elapsed))
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
                shift=max(0,round((1.86-elapsed)*app.w*.45))
                spread=max(12,round(app.w*.19))
                for i,x in enumerate((-spread,0,spread)):
                    app.put(center-4,app.w//2-3+x+shift,r' /\\_/\\ ', DIM if tick%2 else CYAN, True)
                    app.put(center-3,app.w//2-3+x+shift,' ( * * ) ', GOLD if i==1 else CYAN, True)



def _effect_floor(w,h,t):
    c=Canvas(w,h)
    horizon=h//2-3
    for x in range(-w//3, 4*w//3, max(4,w//9)):
        c.line(w//2+(x-w//2)//7,horizon,x,h-1,'navy','.')
    for i in range(4):
        y=h-1-round(i*i*(h-horizon)/16)-int(t*4)%2
        c.put(0,y,'- '*((w+1)//2),'slate')
    for i in range(max(12,w//3)):
        x=(i*19+round(sin(t*2+i)*3))%w
        y=(i*7+int(t*4)*(1+i%2))%max(1,horizon-3)
        c.put(x,y,'.' if i%4 else '+','slate')
    if .35<t<.82:
        f=(t-.35)/.47
        for side in (-1,1):
            reach=round(f*w*.48)
            for off in (0,3,7):
                x=w//2+side*(reach+off)
                c.put(x,h//2-3+off//3,'*' if off==0 else '.','gold' if f<.7 else 'slate')
    return c.finish()


class HPPreview:
    def __init__(self, app, trails):
        self._b_put = app._b_put
        self._b_hp_trails = trails

    draw = BattleUI._b_hp_draw
