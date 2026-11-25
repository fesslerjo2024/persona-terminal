"""Run both live 65x25 curses paths from Testing Mode, with absent temp saves.

Optional dependency: pexpect. Run: python -B qa_crown_dispatch_pty.py
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from campaign_combat import build_stage
from campaign_state import TestingCampaign
from crown_dispatch import ACTION
from qa_telegraph import Terminal, ESC, line


def apply(t,b,aid,key,target=None):
    assert b.act(aid,target) is None,(aid,b.last_error)
    screen=t.keys(key,.28)
    if b.phase=='win':
        if 'PRACTICE WIN' not in screen:screen=t.keys('',.9)
        assert 'PRACTICE WIN' in screen,screen
    elif b.phase=='turn':
        if 'NOW '+b.actor.name not in screen:screen=t.keys('',.55)
        assert 'NOW '+b.actor.name in screen,screen
    else:
        raise AssertionError((b.phase,b.log[-10:],screen))
    return screen


def damage(t,b,foe):
    choices=[]
    for index,(aid,_,_) in enumerate(b.actions('skills')):
        spec=b._spec(aid)
        target=foe if spec['target']=='enemy' else None
        if spec['kind']=='damage' and spec['target'] in ('enemy','enemies') and not b.action_block(aid,target):
            aff=.5 if foe.affinity.get(spec['element'])=='resist' else 1
            choices.append((spec['power']*aff,aid,target,'1'+str(index+1)))
    basic = [('attack','2'),('gun','3')]
    for aid,key in basic:
        spec=b._spec(aid)
        if not b.action_block(aid,foe):
            aff=.5 if foe.affinity.get(spec['element'])=='resist' else 1
            choices.append((spec['power']*aff,aid,foe,key))
    _,aid,target,key=max(choices,key=lambda row:row[0])
    if target is not None:key+=str(b.targets(aid).index(target)+1)
    return apply(t,b,aid,key,target)


def run(save,dispatch,seed=0):
    b=build_stage(TestingCampaign(),'throne-room',seed)
    king,trophy=b.enemies
    t=Terminal(save,seed)
    try:
        screen=t.launch('throne-room',b)
        assert not b.actions(ACTION)
        assert t.keys('c')==screen   # no early special or turn consumption
        for _ in range(8):
            if b.actions(ACTION):break
            screen=damage(t,b,trophy)
        assert not trophy.alive and b.actions(ACTION)
        assert line(screen,'TROPHY BROKEN') and 'C: Send a runner' in screen,screen
        if dispatch:
            before=b.actor
            first_target=b.targets(ACTION)[0]
            picker=t.need('c','TARGET  /  Send Crown Runner [C]')
            assert not line(picker,'Unknown action') and not line(picker,'1 Joker'),picker
            assert first_target.name in picker
            t.need(ESC,'NOW '+before.name)
            t.need('C','TARGET  /  Send Crown Runner [C]')
            screen=apply(t,b,ACTION,'1',first_target)
            assert line(screen,first_target.name+' [AWAY]'),screen
            assert line(screen,'CROWN RUN') and '0/2' in screen,screen
            assert first_target.name not in line(screen,'NEXT').split('NEXT',1)[1]
            status=t.need('i','FIELD STATUS')
            rows=status.splitlines()
            assert any('AWAY' in ' '.join(rows[i:i+2]) for i,r in enumerate(rows) if first_target.name in r)
            t.need('i','NOW '+b.actor.name)
            samples=[]
            for _ in range(7):
                if not first_target.away:break
                screen=damage(t,b,king)
                assert b.actor is not first_target or not first_target.away
                if line(screen,'CROWN RUN'):
                    samples.append(line(screen,'CROWN RUN'))
            assert any('1/2' in row for row in samples),samples
            assert not first_target.away and '[AWAY]' not in screen and line(screen,'CROWN STOLEN'),screen
        for _ in range(20):
            if b.phase=='win':break
            if 'ROYAL SMASH' in b.story_intent and not dispatch:
                screen=apply(t,b,'guard','4')
            else:
                screen=damage(t,b,king)
        if not dispatch:
            assert not b._boss_state.get('crown_used') and not any('AWAY' in s for s in b.log)
        assert b.phase=='win' and 'PRACTICE WIN' in screen and not save.exists(),screen
        print(('dispatch' if dispatch else 'direct')+' route passed at 65x25; save remained absent.')
    finally:
        t.close()


if __name__=='__main__':
    with TemporaryDirectory(prefix='crown-pty-') as d:
        for variant in (True,False):
            run(Path(d)/f'{variant}.json',variant)
