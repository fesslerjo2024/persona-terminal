"""65x25 keyboard QA for Joker/Violet. Only disposable Story prefixes.

The fixture forces a Showtime-eligible HP state and a favorable RNG draw.
It does not install, grant, or choose a pair outside the normal offer code.
Run: python -B qa_violet_showtime_pty.py (optional pexpect dependency).
"""
import curses
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import pexpect
import campaign
from campaign_combat import build_stage
from campaign_data import NODES
from campaign_state import Campaign
from qa_telegraph import ENTER, ROOT, Screen, Terminal

BEFORE='laboratory-counseling'
AFTER='laboratory-colors'
SEED=2


def seed_story(path,node):
    c=Campaign(path)
    c.new_game()
    for row in NODES:
        if row['id']==node:break
        c.clear(row['id'],'B')
    c.equip_squad(('Violet','Queen','Noir'))


def controlled_battle(store,node,seed):
    assert node in (BEFORE,AFTER)
    b=build_stage(store,node,seed)
    assert b.actor.name=='Violet'  # Keep actual seeded initiative.
    b.allies[0].hp=b.allies[0].max_hp//3
    b._showtime_rng=SimpleNamespace(random=lambda:0,choice=lambda options:options[-1])
    b._offer_showtime()
    return b


class ShowtimeTerminal(Terminal):
    def __init__(self,save):
        self.screen=Screen(25,65)
        self.proc=pexpect.spawn(sys.executable,
            ['-B',str(Path(__file__).resolve()),'__fixture__',str(save)],
            cwd=ROOT,env={**os.environ,'TERM':'xterm-256color','ESCDELAY':'25'},
            encoding='utf8',dimensions=(25,65))
        self.need('','NEW GAME',.35)


def check(path,node):
    seed_story(path,node)
    prior=path.read_bytes()
    ui=ShowtimeTerminal(path)
    title='ANSWERS HE WANTS TO HEAR' if node==BEFORE else 'A PATH TOWARD EDEN'
    try:
        ui.need('1','LABORATORY MAP')
        ui.need(ENTER,title)
        ui.need(ENTER,'NOW Violet')
        if node==BEFORE:
            screen=ui.need('t','NOW Violet')
            assert 'TARGET' not in screen and 'THE LAST WALTZ' not in screen,screen
        else:
            ui.need('t','TARGET  /  Showtime [T]')
            scene=ui.need('1','THE LAST WALTZ',.20)
            assert 'Two blades finish the dance.' in scene,scene
            ui.need('','NOW ',.85)
            notice=ui.need('l','Violet → SHOWTIME / Joker × Violet.')
            assert 'Fafnir takes' in notice,notice
        assert path.read_bytes()==prior
        print(f'{node}: '+('Showtime unavailable.' if node==BEFORE else
                           'THE LAST WALTZ rendered successfully.'),
              'Story bytes unchanged.',flush=True)
    finally:ui.close()


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='__fixture__':
        campaign.build_stage=controlled_battle
        curses.wrapper(campaign.run_curses,Campaign(Path(sys.argv[2])),SEED)
    else:
        with TemporaryDirectory(prefix='phantom-violet-pty-') as tmp:
            for node in (BEFORE,AFTER):check(Path(tmp)/(node+'.json'),node)
