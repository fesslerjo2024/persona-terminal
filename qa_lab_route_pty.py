"""Optional 65x25 Exam Room QA through the real terminal; no save is opened.

Run `python -B qa_lab_route_pty.py` with the pexpect test dependency.
"""
from pathlib import Path
from tempfile import TemporaryDirectory

from battle_data import ITEMS
from campaign_data import CHAPTERS
from qa_telegraph import ENTER, ESC, RIGHT, Terminal


def open_brief(term):
    path = 'laboratory-counseling'
    ch, pos = next((i, j) for i, data in enumerate(CHAPTERS)
                   for j, n in enumerate(data['nodes']) if n['id'] == path)
    term.need('3', 'TESTING MODE')
    term.need(RIGHT * ch, 'LABORATORY MAP')
    term.need(str(pos + 1), 'OPERATION BRIEF')
    term.need('', 'P EXAM')


def check(save, mode):
    expected = ITEMS['Soul Drop']['count'] + (mode == 'solved')
    term = Terminal(save, 2)
    try:
        open_brief(term)
        term.need('p', 'CONSULTATION 1/3')
        if mode == 'direct':
            term.need(ESC, 'OPERATION BRIEF')
            term.need(ENTER, 'NOW ')
        elif mode == 'bypass':
            term.need('s', 'NOW ')
        else:
            term.need('a', 'Treatment detour flagged.')
            term.need('h', 'HUDDLE / A teacher')
            term.need('b', 'CONSULTATION 2/3')
            term.need('c', 'CONSULTATION 3/3')
            screen = term.need('', 'Leave every heart alone.')
            assert 'Change harmful hearts to build a better society.' in screen, screen
            term.need('d', 'NOW ')
        term.need('5', f'Soul Drop ×{expected}')
        assert not save.exists(), 'Testing Mode created a save'
        print(f'Exam Room {mode}: Soul Drop ×{expected}; no save created.')
    finally:
        term.close()


if __name__ == '__main__':
    with TemporaryDirectory(prefix='phantom-lab-exam-') as work:
        save = Path(work) / 'absent.json'
        for mode in ('direct', 'bypass', 'solved'):
            check(save, mode)
