"""Actual 65×25 timing regressions, always on absent Testing Mode saves.

Run python -B qa_timing_pty.py with pexpect. Museum 1/4 and both Lab
response paths use unmodified battles and keyboard actions. The separate
cancellation probe enters the real pending phase in an isolated subprocess
then changes two enemy HP values, to make the finishing action deterministic.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import curses
import os
import sys

import pexpect

import campaign
from campaign_combat import build_stage
from campaign_state import Campaign, TestingCampaign
from qa_telegraph import ROOT, Screen, Terminal

LAB = 'laboratory-choice'
MUSEUM = 'museum-security'
STANCE = 'TYRANT STANCE / Guard before Tyrant Chaos.'
LAB_OPENER = (
    ('skill:Cleave', 'Tentacle of Protection'),
    ('skill:Eiga', 'Maruki Azathoth'),
    ('skill:Mazionga', None),
    ('skill:Tempest Slash', 'Maruki Azathoth'),
    ('skill:Garula', 'Maruki Azathoth'),
)
MUSEUM_OPENERS = {
    1: (('item:Freeze Spray','Ippon-Datara'), ('skill:Mazionga',None),
        ('skill:Cleave','Koppa Tengu'), ('skill:Mediarama',None), ('attack','Ippon-Datara')),
    4: (('item:Freeze Spray','Ippon-Datara'), ('pass:Skull',None),
        ('skill:Mazionga',None), ('skill:Mazionga',None)),
}
NON_GUARD = {
    'Joker': ('skill:Rakunda','Maruki Azathoth'),
    'Skull': ('skill:Tarukaja','Skull'),
    'Mona': ('skill:Sukunda','Tentacle of Protection'),
}
SHORTCUTS = {'skills':'1','attack':'2','guard':'4','items':'5','baton':'6'}
PREFIXES = {'skill':'skills','item':'items','pass':'baton'}


def indices(b,a,target):
    category = PREFIXES.get(a.split(':')[0],a)
    rows = b.actions(category)
    index = next(i for i,r in enumerate(rows,1) if r[0]==a)
    targets = b.targets(a)
    selected = next((u for u in targets if u.name==target),None)
    assert (target is None) == (selected is None),(a,target,targets)
    key = SHORTCUTS[category]
    if category not in ('attack','guard'):
        key += str(index)
    if selected:
        key += str(targets.index(selected)+1)
    return key,selected


def act(b,a,target):
    key,selected = indices(b,a,target)
    old_wave=b.wave
    error=b.act(a,selected)
    assert error is None,(a,error)
    return key, b.wave!=old_wave


def play(t,b,a,target=None):
    key,swap = act(b,a,target)
    expected = f'NOW {b.actor.name}'
    screen=t.need(key,expected,.88 if swap else .19)
    return screen


def museum_test(save,seed):
    b=build_stage(TestingCampaign(),MUSEUM,seed)
    initial_allies=[u.name for u in b.order if not u.enemy]
    orig_order=[u.name for u in b.order]
    t=Terminal(save,seed)
    try:
        screen=t.launch(MUSEUM,b)
        for a,target in MUSEUM_OPENERS[seed]:
            finisher=b.actor.name
            screen=play(t,b,a,target)
        assert b.wave==2 and b.round==1, b.log
        assert '2/2  ROUND 1' in screen and 'Silky' in screen and 'Bicorn' in screen, screen
        second=[u.name for u in b.order]
        after=[u.name for u in b.order if not u.enemy]
        cyclic=' '.join(initial_allies+initial_allies)
        assert ' '.join(after) in cyclic
        seen=[]
        while b.round==1:
            name=b.actor.name
            assert name not in seen and len(seen)<len(b.allies),(seed,seen,b.log)
            assert 'NOW '+name in screen,screen
            seen.append(name)
            screen=play(t,b,'guard')
        transcript=t.need('l','Round 2.')
        if seed==1:
            assert finisher=='Skull' and seen==['Joker','Mona']
            assert second==['Silky','Joker','Bicorn','Mona','Skull']
            assert 'Skull loses the turn to sleep.' in transcript
        else:
            assert finisher=='Skull' and seen==['Mona','Joker','Skull']
            assert second==['Silky','Mona','Joker','Bicorn','Skull']
        print(f'Museum seed {seed}: {orig_order} → {second}; closing actor {finisher}; '
              f'visible first new-wave turns {seen}; no duplicated ordinary turn.',flush=True)
    finally:
        t.close()
    assert not save.exists()


def lab_response(save,guard):
    b=build_stage(TestingCampaign(),LAB,1)
    t=Terminal(save,1)
    try:
        screen=t.launch(LAB,b)
        for a,target in LAB_OPENER:
            assert STANCE not in screen,screen
            screen=play(t,b,a,target)
        opening=tuple(u.hp for u in b.allies)
        response=[]
        while b._boss_state.get('lab_charge'):
            name=b.actor.name
            assert name not in response and len(response)<len(b.allies),(response,b.log)
            assert STANCE in screen and 'NOW '+name in screen,screen
            assert not any(' → Tyrant Chaos.' in s for s in b.log)
            response.append(name)
            screen=play(t,b,'guard') if guard else play(t,b,*NON_GUARD[name])
        assert response==['Joker','Skull','Mona']
        assert STANCE not in screen,screen
        loss=tuple(p-u.hp for p,u in zip(opening,b.allies))
        if guard:
            assert loss==(26,25,27),(opening,loss,b.log)
        else:
            assert loss==(55,52,55),(opening,loss,b.log)
        transcript=t.need('l','Maruki Azathoth → Tyrant Chaos.')
        assert transcript.count('Maruki Azathoth → Tyrant Chaos.')==1, transcript
        for u,d in zip(b.allies,loss):
            expected=f'{u.name} takes {d} damage'+(' [GUARD].' if guard else '.')
            assert expected in transcript,(expected,transcript)
        print(f'Lab {"Guard" if guard else "no Guard"}: real HUD cue at each {response} turn, '
              f'opening HP {opening}; actual log confirms HP loss {loss} (Joker, Mona, Skull).',flush=True)
    finally:
        t.close()
    assert not save.exists()
    return opening,loss


def cancel_fixture(store,node,seed):
    assert isinstance(store,TestingCampaign) and node==LAB
    b=build_stage(store,node,seed)
    for a, target in LAB_OPENER:
        act(b,a,target)
    assert b._boss_state.get('lab_charge') and b.actor.name=='Joker'
    # Do not edit the pending cue or schedule. Shorten only core HP and its
    # protection, leaving normal item accuracy, damage, and spawn behavior.
    b.enemies[3].hp=1
    b.enemies[0].hp=0
    return b


class CancelTerminal(Terminal):
    def __init__(self,save):
        self.screen=Screen(25,65)
        self.proc=pexpect.spawn(sys.executable,['-B',str(Path(__file__).resolve()),'__cancel__',str(save)],
            cwd=ROOT,env={**os.environ,'TERM':'xterm-256color','ESCDELAY':'25'},
            encoding='utf8',dimensions=(25,65))
        self.need('','NEW GAME',.35)


def cancellation(save):
    b=cancel_fixture(TestingCampaign(),LAB,1)
    t=CancelTerminal(save)
    try:
        start=t.launch(LAB,b)
        assert STANCE in start and 'Maruki Azathoth 1H' in start,start
        screen=play(t,b,'item:Molotov Cocktail','Maruki Azathoth')
        assert b.wave==2 and not b._boss_state.get('lab_charge')
        assert '2/3  ROUND 1' in screen and STANCE not in screen,screen
        transcript=t.need('l','Joker → Molotov Cocktail.')
        assert 'Maruki Azathoth → Tyrant Chaos.' not in transcript,transcript
        assert 'Maruki Azathoth takes' in transcript,transcript
        assert 'remaining tendrils collapse' in transcript,transcript
        assert 'Wave 2/3' in transcript,transcript
        print('Lab cancel (phase fixture): visible pending Stance → real Molotov downs core → '
              'actual wave 2; no Tyrant Chaos attack survives the transition.',flush=True)
    finally:
        t.close()
    assert not save.exists()


def main():
    if len(sys.argv)>1 and sys.argv[1]=='__cancel__':
        campaign.build_stage=cancel_fixture
        curses.wrapper(campaign.run_curses,Campaign(Path(sys.argv[2])),1)
        return
    with TemporaryDirectory(prefix='phantom-timing-pty-') as tmp:
        root=Path(tmp)
        for seed in (1,4):
            museum_test(root/f'museum-{seed}-absent.json',seed)
        guarded=lab_response(root/'guard-absent.json',True)
        open_=lab_response(root/'take-hit-absent.json',False)
        assert guarded[0]==open_[0]
        assert all(x<y for x,y in zip(guarded[1],open_[1]))
        cancellation(root/'cancel-absent.json')


if __name__=='__main__':
    main()
