"""Real 65x25 PTY HP/cut-in/save QA; all Story saves are disposable.

Run `python -B qa_cutins_save_pty.py` with the optional pexpect dependency.
Use --strict-readability to fail if the watched finisher's red loss display is
missing or compressed to a brief update, rather than only reporting timing.
"""
import argparse
import os
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

import pexpect

from campaign_state import Campaign
from qa_telegraph import ENTER, ESC, RIGHT, ROOT, Screen, Terminal

SEED = 4
# The sole Castle Gate enemy occupies row 8, columns 57–61 at 65x25.
ENEMY_BAR = (8, 57, 62)
RED = {'31', '38;5;203'}


class ColorScreen(Screen):
    """Subset of xterm SGR sufficient for recording actual Castle Guard HP."""
    def __init__(self):
        super().__init__(25, 65)
        self.foreground = None
        self.ink = {}

    def chars(self, txt):
        for char in txt:
            if ord(char) >= 32 and char != '\x7f':
                self.ink[self.y, self.x] = self.foreground
            super().chars(char)

    def handle(self, control):
        if control.startswith('\x1b[') and control.endswith('m'):
            values = (control[2:-1] or '0').split(';')
            while values:
                current = values.pop(0)
                if current in ('','0','39'):
                    self.foreground = None
                elif current == '38' and len(values) >= 2 and values[0] == '5':
                    self.foreground = f'38;5;{values[1]}'
                    del values[:2]
                elif current in {str(i) for i in range(30,38)}:
                    self.foreground = current
        # REP uses the copy's foreground in this app's HP bar updates.
        elif control.startswith('\x1b[') and control.endswith('b') and self.x:
            width = int(control[2:-1] or '1')
            for offset in range(width):
                self.ink[self.y,self.x+offset] = self.ink.get((self.y,self.x-1))
        super().handle(control)


class Probe(Terminal):
    def __init__(self, save):
        self.screen = ColorScreen()
        self.proc = pexpect.spawn(sys.executable,
            ['-B', str(ROOT/'campaign.py'), '--save', str(save), '--seed', str(SEED)],
            cwd=ROOT, env={**os.environ,'TERM':'xterm-256color','ESCDELAY':'25'},
            encoding='utf8', dimensions=(25,65))

    def sample(self, key='', until=0.95, skip_at=None, skip_key=ENTER):
        """Track independent screen updates with 10ms observation cadence."""
        if key:
            self.proc.send(key)
        started = monotonic()
        snapshots = []
        red_proofs = set()
        sent = False
        while (elapsed:=monotonic()-started) < until:
            if skip_at is not None and not sent and elapsed >= skip_at:
                self.proc.send(skip_key)
                sent = True
            try:
                chunk = self.proc.read_nonblocking(65536,timeout=.010)
            except pexpect.TIMEOUT:
                chunk = ''
            if chunk:
                self.screen.feed(chunk)
            y, left, right = ENEMY_BAR
            bar = ''.join(self.screen.lines[y][left:right])
            count = 0
            for x in range(left,right):
                if self.screen.lines[y][x] == '▓':
                    fg = self.screen.ink.get((y,x))
                    red_proofs.add(fg)
                    if fg in RED:
                        count += 1
            text = self.screen.dump()
            mark = ('cutin' if 'CURTAIN CALL' in text else
                    'debrief' if 'PALACE / DEBRIEF' in text else
                    'arena' if 'Castle Guard' in text else 'transition')
            snapshots.append((elapsed,mark,bar,count))
        return snapshots,red_proofs,sent


def progress_setup(term, *, testing=False):
    term.need('', 'NEW GAME')
    if testing:
        term.need('3','TESTING MODE')
    else:
        term.need('2','PROLOGUE')
        term.need(ESC,'TRAINING LINK')
        term.need(ESC,'CASTLE MAP')
    term.need('1','OPERATION BRIEF')
    term.need(ENTER,'NOW Joker')
    term.need('1','PERSONA: Arsène')
    term.need(RIGHT,'PERSONA: Pixie')
    term.need('1','TARGET  /  Zio')
    initial = term.screen.dump()
    assert 'Castle Guard 69H' in initial, initial


def damage_display(snapshots):
    return Counter((state,bar,red) for _,state,bar,red in snapshots
                   if state in ('arena','cutin','debrief'))


def duration(rows, check):
    selected = [at for at, state, bar, count in rows if check(state,bar,count)]
    # Add the sample cadence so a one-screen update isn't mistakenly called zero.
    return round((selected[-1]-selected[0])*1000+10) if selected else 0


def one_story(save, skip):
    term = Probe(save)
    try:
        progress_setup(term)
        hit, hit_colors, _ = term.sample('1')
        hit_red_ms = duration(hit,lambda state,bar,red: state=='arena' and red>0)
        assert hit_red_ms >= 220, (hit_red_ms,damage_display(hit))
        assert len(hit_colors) == 1 and hit_colors <= RED, hit_colors
        states = [bar for _,state,bar,count in hit if state=='arena']
        for expected in ('██▓▓▓','██░░░'):
            assert expected in states, damage_display(hit)
        hold = term.screen.dump()
        assert 'Castle Guard 21H' in hold and 'HOLD UP!' in hold, hold

        finish, colors, sent = term.sample('7',until=1.66, skip_at=.12 if skip else None)
        assert sent == skip
        cutin_ms = duration(finish,lambda state,bar,red: state=='cutin')
        finisher_red_ms = duration(finish,lambda state,bar,red: state=='arena' and red>0)
        assert cutin_ms > 0, damage_display(finish)
        assert any(state=='debrief' for _,state,_,_ in finish), damage_display(finish)
        assert colors <= RED, colors
        assert 'FIRST-CLEAR REWARDS' in term.screen.dump()
        log = term.need('l','All-Out Attack! 3 standing')
        assert log.count('All-Out Attack! 3 standing') == 1, log
        assert log.count('JOKER // CURTAIN CALL.') == 1, log
        assert log.count('Trial cleared.') == 1, log
        checkpoint = Campaign(save).data
        assert checkpoint['credits']==425
        assert checkpoint['cleared']=={'castle-gate':'S'}
        assert checkpoint['teammates'].count('Panther')==1
        assert checkpoint['slots']==4
        print(f"{'Skipped' if skip else 'Watched'}: Zio red {hit_red_ms} ms {sorted(hit_colors)}; "
              f"cut-in {cutin_ms} ms; finishing red {finisher_red_ms} ms {sorted(colors)}; "
              f"observed updates {list(damage_display(finish))}; "
              "one All-Out, one battle clear, one reward.",flush=True)
    finally:
        term.close()
    before = save.read_bytes()
    next_term=Terminal(save,SEED)
    try:
        campaign_map=next_term.need('1','CASTLE MAP')
        assert '▶  02' in campaign_map and 'Guardhouse' in campaign_map,campaign_map
        next_term.need(ENTER,'OPERATION BRIEF')
        arena=next_term.need(ENTER,'NOW Joker')
        assert 'Guardhouse' in arena,arena
    finally:
        next_term.close()
    assert save.read_bytes()==before
    return before,cutin_ms,finisher_red_ms,damage_display(finish)


def absent_testing(save):
    term = Probe(save)
    try:
        progress_setup(term, testing=True)
        term.need('1','HOLD UP!')
        term.sample(until=.76)  # settle the setup strike before timing the KO
        frames, colors, _ = term.sample('7', until=1.62, skip_at=.12, skip_key=ESC)
        cutin_ms = duration(frames,lambda state,bar,red: state=='cutin')
        red_ms = duration(frames,lambda state,bar,red: state=='arena' and red>0)
        assert colors <= RED
        assert 'PRACTICE WIN' in term.screen.dump()
        assert 'FIRST-CLEAR REWARDS' not in term.screen.dump()
        term.need('l','All-Out Attack! 3 standing')
    finally:
        term.close()
    assert not save.exists(), 'Testing Mode created a save'
    print(f'Testing Escape: cut-in {cutin_ms} ms, red damage {red_ms} ms, practice win; no file created.')
    return cutin_ms,red_ms,damage_display(frames)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict-readability',action='store_true')
    args=parser.parse_args()
    with TemporaryDirectory(prefix='phantom-cutins-save-') as tmp:
        path=Path(tmp)
        watched,full_ms,full_red,full_frames=one_story(path/'watched.json',False)
        skipped,enter_ms,enter_red,enter_frames=one_story(path/'skipped.json',True)
        assert watched==skipped
        print("Watched and skipped Story saves are byte-identical. Actual Continue opens Guardhouse; no further save change.")
        esc_ms,esc_red,esc_frames=absent_testing(path/'no-testing-save.json')
    if args.strict_readability:
        for case, ms, frames in [('watched',full_red,full_frames),('Enter',enter_red,enter_frames),
                                 ('Escape',esc_red,esc_frames)]:
            assert ms >= 350, f"{case}: only {ms} ms of visible red damage."
            transitions = list(frames)
            red_frame = ('arena','▓▓░░░',2)
            empty_frame = ('arena','░░░░░',0)
            assert red_frame in transitions and empty_frame in transitions, (case,frames)
            assert transitions.index(red_frame) < transitions.index(empty_frame), (case,frames)
        assert max(enter_ms,esc_ms)+200 < full_ms, (full_ms,enter_ms,esc_ms)
    for name in ('battle_ui.py','campaign.py'):
        print(f"{sha256((ROOT/name).read_bytes()).hexdigest()}  {name}")


if __name__=='__main__':
    main()
