"""Calling Card startup and the live title screen that unfolds from it."""
from functools import lru_cache

from battle_ui import RED, GOLD, WHITE, DIM
import intro_calling_card as card
from reel_palette import IDS

PRODUCT_TITLE = 'Persona 5 Terminal'
WIPE_SECONDS = .52
STARTUP_SECONDS = card.DURATION + WIPE_SECONDS


def _fold(width, height, reveal):
    top = max(4, height//2-7)
    left = max(2, round(width*.48))
    span = min(width-left-2, max(27, round(width*.40)))
    rows = card.render(card.DURATION, width, height, menu=(reveal,top,left,span))
    return rows, top, left, span


@lru_cache(maxsize=4)
def _landed(width, height):
    return _fold(width, height, 1)


def draw_startup(app, elapsed):
    width, height = app.w-1, app.h
    if elapsed < card.DURATION:
        rows = card.render(elapsed, width, height)
    else:
        progress = min(1., (elapsed-card.DURATION)/WIPE_SECONDS)
        rows, _, _, _ = _fold(width, height, progress)
    app.draw_scene_rows(rows)


def draw_title(app, menu, index, notice='', *, back=False):
    rows, top, left, span = _landed(app.w-1, app.h)
    app.draw_scene_rows(rows)
    app.put(top+2, left+4, PRODUCT_TITLE, IDS['rose'], True)
    for i, (label, _, enabled) in enumerate(menu):
        offset = 4+2*i
        row, x = top+offset, left+3-offset//4
        prefix = '◆' if i == index else ' '
        text = f'{prefix} {i+1} {label}'
        if i == index:
            app.put(row, x, text.ljust(span-6), RED if enabled else DIM, True, True)
        else:
            app.put(row, x, text, WHITE if enabled else DIM)
    if notice:
        app.put(app.h-4, 3, notice[:app.w-6], GOLD)
    elif not menu[index][2]:
        app.mid(app.h-4, 'No readable campaign save.', DIM)
    app.mid(app.h-2, '↑↓ SELECT  ↵ OPEN  ESC TITLES' if back else '↑↓ SELECT  ↵ OPEN', RED)
