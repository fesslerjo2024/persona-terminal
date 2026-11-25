"""65x25 Museum affinity preview QA (optional pexpect dependency).

The first run is unmodified Museum; the second starts with Museum's actual
second formation, Panther in the squad and sturdier copies so they survive
one probe. Neither run seeds affinity knowledge or uses a Story save.
"""
import curses
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pexpect
import campaign
from campaign_combat import build_stage
from campaign_state import Campaign, TestingCampaign
from qa_telegraph import ROOT, ESC, Screen, Terminal, line

NODE='museum-throne'
SEED=0


def fixture(store,node,seed):
    assert node==NODE and isinstance(store,TestingCampaign)
    store.equip_squad(('Panther','Mona','Skull'))
    b=build_stage(store,node,seed)
    b.wave=2
    b._spawn()
    b._advance()
    for u in b.enemies:
        if u.behavior=='museum-copy':u.hp=u.max_hp=130
    return b


class MixedTerminal(Terminal):
    def __init__(self,save,seed):
        self.screen=Screen(25,65)
        self.proc=pexpect.spawn(sys.executable,
            ['-B',str(Path(__file__).resolve()),'__fixture__',str(save),str(seed)],
            cwd=ROOT,env={**os.environ,'TERM':'xterm-256color','ESCDELAY':'25'},
            encoding='utf8',dimensions=(25,65))
        self.need('','NEW GAME',.35)


def use(term,b,aid,key,target=None):
    assert b.act(aid,target) is None
    return term.need(key,'NOW '+b.actor.name,.33)


def guard_until(term,b,actor):
    for _ in range(8):
        if b.actor.name==actor:return
        use(term,b,'guard','4')
    raise AssertionError((actor,b.actor.name,b.log))


def skill_button(b,skill):
    return str(next(i for i,(aid,_,_) in enumerate(b.actions('skills'),1) if aid==skill))


def real_museum(save):
    b=build_stage(TestingCampaign(),NODE,SEED)
    t=Terminal(save,SEED)
    try:
        t.launch(NODE,b)
        guard_until(t,b,'Joker')
        spell='skill:Eiga'
        key=skill_button(b,spell)
        nose=b.enemies[1]
        before=t.need('1'+key,'TARGET  /  Eiga')
        assert nose.name in before and '[DRAIN]' not in before and not b.seen,before
        use(t,b,spell,'2',nose)
        assert b.seen[nose.name]['Curse']=='drain'
        guard_until(t,b,'Joker')
        after=t.need('1'+key,'[DRAIN] '+nose.name)
        assert '[DRAIN]' not in line(after,b.enemies[0].name) and '[DRAIN]' not in line(after,b.enemies[2].name)
        use(t,b,spell,'2',nose)  # Warning does not prevent intentional selection.
        assert sum('drains Curse!' in row for row in b.log)==2
        assert not save.exists()
        print('Real Museum: Eiga target unknown, then [DRAIN] on Nose only; target remains selectable.')
    finally:t.close()


def mixed_group(save):
    b=fixture(TestingCampaign(),NODE,2)
    t=MixedTerminal(save,2)
    try:
        t.launch(NODE,b)
        guard_until(t,b,'Panther')
        spell='skill:Maragion'
        key=skill_button(b,spell)
        before=t.need('1','Maragion')
        assert '[DRAIN' not in before and '[WEAK' not in before and not b.seen,before
        use(t,b,spell,key)
        assert b.seen['Scarlet Copy']['Fire']=='drain' and b.seen['Cerulean Copy']['Fire']=='weak',b.log
        guard_until(t,b,'Panther')
        after=t.need('1','Maragion [DRAIN 1 WEAK 1]')
        selected=t.need('j','Drain: Scarlet Copy; Weak: Cerulean Copy')
        assert 'Maragion [DRAIN 1 WEAK 1]' in selected and 'Drain: Scarlet Copy; Weak: Cerulean Copy' in selected
        assert not save.exists()
        print('Mixed Museum fixture: Maragion starts unmarked; group preview reports DRAIN 1 / WEAK 1 and both names.')
    finally:t.close()


def main():
    if len(sys.argv)>1 and sys.argv[1]=='__fixture__':
        _,_,save,seed=sys.argv
        campaign.build_stage=fixture
        curses.wrapper(campaign.run_curses,Campaign(Path(save)),int(seed))
        return
    with TemporaryDirectory(prefix='phantom-affinity-pty-') as tmp:
        real_museum(Path(tmp)/'absent-real.json')
        mixed_group(Path(tmp)/'absent-fixture.json')


if __name__=='__main__':
    main()
