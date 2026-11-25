"""Read-only animation previews, independent of campaign progress and battle state."""
from dataclasses import dataclass
import curses as C
import time
from math import sin

from detail_canvas import DotCanvas

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
            Clip(cutins.FINAL_GUARD[0]),
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

    def stop(self):
        self.started = None
        self.reel = self.loop = False

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
                self.stop()
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
        app.draw_scene_rows(_effect_floor(app.w-1,app.h,elapsed,after==0))
        renderer = HPPreview(app, {unit: (before, impact)} if now >= impact else {})
        center = app.h//2
        if after > 0 or elapsed < 1.08:
            renderer.draw(center,(app.w-width)//2,unit,width,now)


def _shadow(c,cx,cy,scale,ink,phase):
    """Original Jack-o'-Lantern-shaped target for an existing HUD fixture."""
    def q(x,y):
        return cx+x*scale,cy+y*scale
    def poly(points,color,density=8,edge=None):
        c.face(tuple(q(x,y) for x,y in points),color,density,edge)
    bob=sin(phase*5)*scale*.45
    c.ellipse(cx,cy+scale*8,scale*8,scale*1.2,'navy',3)
    poly(((-13,1),(-8,-1),(-7,-5),(-2,-6),(1,-11),(3,-6),(8,-4),
          (9,-1),(13,1),(8,4),(-7,4)),'violet',6,'slate')
    c.ellipse(cx,cy+(3+bob/scale)*scale,scale*6,scale*5,'ochre',5,ink)
    poly(((-5,1),(-1,2),(-3,4)),ink)
    poly(((1,2),(5,1),(3,4)),ink)
    c.path(tuple(q(x,y) for x,y in ((-3,5),(-1,6),(0,5),(1,6),(3,5))),ink)
    c.ring(*q(0,1),scale*6.6,scale*5,'amber',.13,2.68,18)


def _effect_floor(w,h,t,wave_clear=False):
    c=DotCanvas(w,h)
    if not w or not h:return c.finish()
    W,H=c.w,c.h
    horizon=round(H*.475)
    for x in range(-W//2, 3*W//2, max(5,W//14)):
        c.line((W//2+(x-W//2)//11,horizon),(x,H-1),'navy')
    for i in range(6):
        y=H-1-round(i*i*(H-horizon)/36)-int(t*9)%3
        c.line((0,y),(W-1,y),'navy' if i%2 else 'slate')
    for i in range(max(18,W//3)):
        x=(i*31+round(sin(t*1.4+i)*5))%W
        y=(i*17+int(t*7)*(1+i%2))%max(1,horizon-12)
        c.put(x,y,'slate' if i%5 else 'violet')
    if t<1.08 or not wave_clear:
        _shadow(c,W*.5,H*.35,max(1.,H*.014),'gold' if .35<t<.53 else 'amber',t)
    elif t<1.48:
        p=(t-1.08)/.4
        for k in range(21):
            a=k*2.399
            x=W*.5+sin(a)*(6+32*p); y=H*.35+sin(a+1.57)*(4+17*p)
            c.line((x,y),(x+3*sin(a),y+3*sin(a+1.57)),'ochre' if k%4==1 else 'slate')
    else:
        shift=max(0.,(1.86-t)*W*.35)
        for i,s in enumerate((-.21,0.,.21)):
            _shadow(c,W*(.5+s)+shift,H*.35+abs(s)*10,max(.6,H*.012),
                    'amber' if i==1 else 'teal',t)
    if .35<t<.82:
        p=(t-.35)/.47
        c.ring(W*.5,H*.35,W*(.03+.41*p),H*(.02+.18*p),
               'gold' if p<.35 else 'ochre',.15,5.85)
        for side in (-1,1):
            reach=W*(.03+.35*p)*side
            y=H*.34
            c.path(((W*.5+reach-side*7,y-3),(W*.5+reach,y),(W*.5+reach-side*4,y+4)),
                   'white' if p<.35 else 'amber')
    return c.finish()


class HPPreview:
    def __init__(self, app, trails):
        self._b_put = app._b_put
        self._b_hp_trails = trails

    draw = BattleUI._b_hp_draw
