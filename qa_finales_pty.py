"""65x25 curses QA using temporary, seeded Testing Mode fixtures only.

Four independent PTYs start from the genuine campaign menu, with the stage
builder patched only inside those subprocesses to select a worst-case
four-person roster and/or a chosen boss wave. Actual menus, inputs, scenes
and damage resolution are unmodified. This is not a full campaign playtest.
Run python -B qa_finales_pty.py (optional pexpect).
"""
import curses
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pexpect
import campaign
import depths_boss
from campaign_combat import build_stage
from campaign_state import Campaign, TestingCampaign
from qa_telegraph import ROOT, ENTER, ESC, Screen, Terminal, line

NODES = dict(depths='depths-yaldabaoth', lab='laboratory-choice')

def fixture(store, node, seed, scenario):
    assert isinstance(store,TestingCampaign), 'Never fixture a Story save.'
    store.equip_squad(('Mona','Queen','Noir'))
    b=build_stage(store,node,seed)
    tail=scenario.endswith('finish')
    if node==NODES['depths'] or tail:
        b.wave=2 if node==NODES['depths'] else 3
        b.round=1
        b._spawn();b._advance()
    if scenario=='depths-finish':
        # Fast-forward HP only: the real attack and finale command still run.
        b.enemies[0].hp=1
    return b

class FinaleTerminal(Terminal):
    def __init__(self,save,seed,scenario):
        self.screen=Screen(25,65)
        self.proc=pexpect.spawn(sys.executable,
            ['-B',str(Path(__file__).resolve()),'__fixture__',scenario,str(save),str(seed)],
            cwd=ROOT,env={**os.environ,'TERM':'xterm-256color','ESCDELAY':'25'},
            encoding='utf8',dimensions=(25,65))
        self.need('','NEW GAME',.35)

def action(t,b,aid,key,target=None):
    assert b.act(aid,target) is None
    screen=t.keys(key,.16)
    if b.phase=='turn' and 'NOW '+b.actor.name not in screen:screen=t.keys('',.5)
    if b.phase=='turn':assert 'NOW '+b.actor.name in screen,screen
    return screen

def num_rows(screen,match):
    return [row.strip() for row in screen.splitlines() if match in row]

def capture_roster(t,b,screen):
    print('  arena foes:',[r[32:].strip() for r in screen.splitlines()[8:16]])
    status=t.need('i','FIELD STATUS')
    lines=status.splitlines()
    print('  status foes:',[(i+1,r.strip()) for i,r in enumerate(lines)
                           if i>=14 and ('HP ' in r or '━' in r)])
    for u in b.visible_enemies:
        assert u.name[:18] in status,(u.name,status)
    reopen=t.need('i','NOW '+b.actor.name)
    assert reopen==screen
    target=t.need('8','TARGET')
    choices=b.targets('analyze')
    assert choices
    # Scroll (don't select an invisible row with a shortcut) then inspect
    # the last detail card, and back through targeting to the same action.
    last=t.need('j'*(len(choices)-1),choices[-1].name)
    print('  target shortlist:',num_rows(target,' HP '),
          'last choice visible:',choices[-1].name in last)
    scan=t.need(ENTER,'AFFINITY SCAN')
    assert choices[-1].name.upper() in scan
    screen=t.need(ESC,'COMMAND')
    return screen

def run(save,scenario,seed):
    node=NODES[scenario.split('-')[0]]
    b=fixture(TestingCampaign(),node,seed,scenario)
    t=FinaleTerminal(save,seed,scenario)
    try:
        screen=t.launch(node,b)
        print(scenario, 'opener:',b.actor.name)
        if scenario=='depths-open':
            assert not any(name in screen for name in depths_boss.ARM_NAMES)
            print('  dormant arms hidden; opening:',line(screen,'GOD OF CONTROL'))
            for _ in range(25):
                if len(b.visible_enemies)==5:break
                screen=action(t,b,'guard','4')
            assert len(b.visible_enemies)==5
            print('  order shown:',line(screen,'NEXT'))
            print('  engine initiative:',[u.name for u in b.upcoming_turns()])
            capture_roster(t,b,screen)
        elif scenario=='lab-open':
            assert len(b.visible_enemies)==4
            assert line(screen,'SHIELD TENDRIL')
            print('  order shown:',line(screen,'NEXT'))
            print('  engine initiative:',[u.name for u in b.upcoming_turns()])
            capture_roster(t,b,screen)
        else:
            if scenario=='depths-finish':
                for _ in range(10):
                    if b.actions('story-special'):break
                    screen=action(t,b,'attack','21',b.enemies[0])
                assert '9: Sinful Shell / End the fight.' in screen,screen
            else:
                warning=None;guard_list=[]
                for _ in range(22):
                    if b.actions('story-special'):break
                    if 'FULL FORCE' in b.story_intent:
                        warning=line(screen,'FULL FORCE')
                        assert warning and 'Guard every standing ally' in warning,screen
                        guard_list.append((b.actor.name,warning))
                    screen=action(t,b,'guard','4')
                assert warning and 'OPENING / Joker: 9 Take the Shot.' in screen,screen
                print('  Guard readiness:',guard_list)
            expected='Sinful Shell' if scenario=='depths-finish' else 'Take the Shot'
            assert b.actions('story-special')[0][1]==expected
            print('  final warning:',line(screen,expected))
            assert b.act('story-special') is None
            assert b.phase=='win'
            victory=t.need('9','PRACTICE ONLY',1.3)
            print('  outcome:',line(victory,'PRACTICE ONLY'))
        assert not save.exists(),save
        if t.screen.unsupported:print('  unsupported terminal controls:',t.screen.unsupported)
    finally:t.close()

def main():
    if len(sys.argv)>1 and sys.argv[1]=='__fixture__':
        _,_,scenario,save,seed=sys.argv
        campaign.build_stage=lambda s,n,x:fixture(s,n,x,scenario)
        curses.wrapper(campaign.run_curses,Campaign(Path(save)),int(seed))
        return
    with TemporaryDirectory(prefix='phantom-finales-pty-') as dr:
        for scenario in ('depths-open','depths-finish','lab-open','lab-finish'):
            run(Path(dr)/(scenario+'-absent.json'),scenario,2)

if __name__=='__main__':main()
