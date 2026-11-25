"""Draw the three approved title emblems with their preview animation curves."""
from functools import lru_cache
from math import cos, pi

from battle_ui import CYAN, DIM, GOLD, GREEN, RED, WHITE
from detail_canvas import DotCanvas
from reel_palette import IDS
from selector_drafts_p3 import draw_dark_hour_clock
from selector_drafts_p4 import draw_golden_tube_tv
from selector_drafts_p5 import draw_pinned_calling_card

PULSE_SECONDS = .72
OPEN_SECONDS = .40
PIN_SECONDS = 1.25

DRAW = {3:draw_dark_hour_clock,4:draw_golden_tube_tv,5:draw_pinned_calling_card}
INKS = {'cyan':CYAN,'red':RED,'gold':GOLD,'white':WHITE,'green':GREEN,'dim':DIM,**IDS}


@lru_cache(maxsize=256)
def _emblem(number,width,height,phase):
    # Cap the raster to the approved full-size draft, reducing it for smaller cards.
    art_width=min(width,26)
    c=DotCanvas(art_width,height)
    DRAW[number](c,phase/36)
    left=(width-art_width)//2
    rows=[]
    for row in c.finish():
        x=left
        spans=[]
        for run,pigment in row:
            if run.strip():
                spans.append((x,run,INKS[pigment]))
            x+=len(run)
        rows.append(tuple(spans))
    return tuple(rows)


def emblem_runs(number,width,height,elapsed=None):
    duration=PIN_SECONDS if number==5 else PULSE_SECONDS
    phase=36 if elapsed is None or not 0<=elapsed<duration else round(
        (1-cos(pi*elapsed/duration))*18)
    return _emblem(number,width,height,phase)
