"""Real 65x25 keyboard QA: python -B qa_depths_floor_pty.py (uses pexpect)."""
from pathlib import Path
from tempfile import TemporaryDirectory

from campaign_combat import build_stage
from campaign_data import CHAPTERS, NODES
from campaign_state import Campaign, TestingCampaign
from qa_telegraph import ENTER, ESC, RIGHT, Terminal

NODE = 'depths-floor'
SEED = 2
UP, DOWN, LEFT = '\x1bOA', '\x1bOB', '\x1bOD'
CHAPTER, OPERATION = next((i,j) for i,c in enumerate(CHAPTERS)
                          for j,n in enumerate(c['nodes']) if n['id']==NODE)


def need(term, k, expected, *extra):
    screen = term.need(k, expected)
    for fragment in extra:
        assert fragment in screen, (fragment,screen)
    return screen


def brief(term):
    return need(term,str(OPERATION+1),'OPERATION BRIEF','P TILES','ENTER DEPLOY')


def floor(term):
    return need(term,'p','DEPTHS / LIGHT FLOOR','BLUE 3/9','STEPS 0',
                'START','EXIT','+ BLUE / ON','- YELLOW / OFF','X RESET','S SKIP','ESC BACK')


def inventory(term,count):
    need(term,'5',f'Soul Drop ×{count}')
    need(term,ESC,'NOW ')


def leave_to_brief(term,story):
    need(term,ESC,'RETURN TO THE PALACE MAP?')
    screen = need(term,ENTER,'DEPTHS MAP')
    if story:
        assert any('▣' in row and 'A Treasure That Will Not Fall' in row
                   for row in screen.splitlines()), screen
    brief(term)


def solve(term):
    need(term,ENTER,'6 still yellow','STEPS 0')
    need(term,LEFT,'Wall. Stay on the floor.','BLUE 3/9','STEPS 0')
    need(term,UP,'Wall. Stay on the floor.','BLUE 3/9','STEPS 0')
    need(term,RIGHT,'STEPS 1','BLUE 2/9')
    need(term,'x','Floor reset.','BLUE 3/9','STEPS 0')
    need(term,DOWN*2+RIGHT*2,'STEPS 4','BLUE 7/9')
    need(term,ENTER,'2 still yellow','STEPS 4')
    need(term,'X','Floor reset.','BLUE 3/9','STEPS 0')
    need(term,DOWN*2+RIGHT+UP+RIGHT,'STEPS 5','BLUE 6/9')
    need(term,UP+DOWN,'STEPS 7','BLUE 8/9')
    ready = need(term,DOWN,'EXIT READY','BLUE 9/9','STEPS 8')
    assert 'NOW ' not in ready, ready
    need(term,ENTER,'NOW ')


def check(path,story):
    if story:
        store=Campaign(path)
        store.new_game()
        for operation in NODES:
            if operation['id']==NODE:
                break
            store.clear(operation['id'],'B')
        original=path.read_bytes()
        assert not store.can_play('depths-grail')
    else:
        store=TestingCampaign()
    standard=build_stage(store,NODE,SEED).items['Soul Drop']
    term=Terminal(path,SEED)
    try:
        if story:
            need(term,'1','DEPTHS MAP')
        else:
            need(term,'3','TESTING MODE')
            need(term,RIGHT*CHAPTER,'DEPTHS MAP')
        brief(term)
        floor(term)
        need(term,RIGHT,'STEPS 1')
        need(term,ESC,'OPERATION BRIEF','P TILES')
        floor(term)  # Back then reopen must recalculate the initial entry once.
        need(term,ESC,'OPERATION BRIEF')
        need(term,ENTER,'NOW ')
        inventory(term,standard)
        leave_to_brief(term,story)
        floor(term)
        need(term,'s','NOW ')
        inventory(term,standard)
        leave_to_brief(term,story)
        floor(term)
        solve(term)
        need(term,'l','The light floor cache yields one extra Soul Drop')
        need(term,'l','NOW ')
        inventory(term,standard+1)
        need(term,'r','RESTART THIS FIGHT?')
        need(term,ENTER,'NOW ')
        inventory(term,standard)
        leave_to_brief(term,story)
    finally:
        term.close()
    if story:
        assert path.read_bytes()==original
    else:
        assert not path.exists()
    scope = 'Story byte-identical, Grail locked' if story else 'Testing save absent'
    print(f'{scope}; direct/skip/solve/restart Soul Drop: '
          f'{standard}/{standard}/{standard+1}/{standard}.',flush=True)


if __name__ == '__main__':
    with TemporaryDirectory(prefix='phantom-depths-floor-') as tmp:
        check(Path(tmp)/'story.json',True)
        check(Path(tmp)/'missing.json',False)
