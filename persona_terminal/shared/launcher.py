"""Entry-point wiring for the series selector and legacy direct launch."""
import argparse
import curses as C
import os
from pathlib import Path

from ..persona3.persona3_state import DEFAULT_SAVE as DEFAULT_P3_SAVE, distinct_slots
from ..persona5.campaign import CampaignApp
from ..persona5.campaign_state import DEFAULT_SAVE, Campaign, TestingCampaign
from .reel_palette import install as install_scene_palette
from .suite_menu import SuiteMenu


def run_curses(s,save,seed,direct=False,p3_save=DEFAULT_P3_SAVE):
    try:C.curs_set(0)
    except C.error:pass
    C.start_color()
    try:C.use_default_colors();bg=-1
    except C.error:bg=C.COLOR_BLACK
    colors=[203,221,51,255,246,84] if C.COLORS>=256 else [
        C.COLOR_RED,C.COLOR_YELLOW,C.COLOR_CYAN,C.COLOR_WHITE,C.COLOR_WHITE,C.COLOR_GREEN]
    for i,color in enumerate(colors,1):C.init_pair(i,color,bg)
    install_scene_palette(bg)
    # Distinguish a lone Esc from an arrow sequence without a full-second wait.
    if 'ESCDELAY' not in os.environ:C.set_escdelay(55)
    s.keypad(True);s.timeout(80)
    def open_persona5():
        return CampaignApp(s,Campaign(save),seed).run(back_to_suite=not direct)
    extras_app=None
    def open_persona5_extra(kind):
        nonlocal extras_app
        if extras_app is None:extras_app=CampaignApp(s,TestingCampaign(),seed)
        extras_app.run_extra(kind)
    if direct:open_persona5()
    else:SuiteMenu(s,p3_save,seed).run(open_persona5,open_persona5_extra)

def main():
    p=argparse.ArgumentParser(description='Open the offline Persona terminal suite.')
    p.add_argument('--persona5',action='store_true',help='Skip the suite picker and open Persona 5 directly.')
    p.add_argument('--save',type=Path,default=Path(os.environ.get('PHANTOM_CAMPAIGN_SAVE',str(DEFAULT_SAVE))))
    p.add_argument('--p3-save',type=Path,default=Path(os.environ.get('PERSONA3_TERMINAL_SAVE',str(DEFAULT_P3_SAVE))),help='Use a separate Persona 3 save file.')
    p.add_argument('--seed',type=int,default=None,help=argparse.SUPPRESS)
    args=p.parse_args()
    if not args.persona5:
        try:
            if not distinct_slots(args.save,args.p3_save) or not distinct_slots(DEFAULT_SAVE,args.p3_save):
                p.error('Persona 3 and Persona 5 require separate save files.')
        except (OSError,RuntimeError) as exc:p.error(str(exc))
    try:C.wrapper(run_curses,args.save,args.seed,args.persona5,args.p3_save)
    except KeyboardInterrupt:pass
