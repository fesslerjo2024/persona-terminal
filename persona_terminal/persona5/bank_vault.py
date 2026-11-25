"""Temporary journal and PIN controls for the four Bank vault rings."""
import curses as C

from .battle_ui import CYAN, WHITE, GOLD, DIM, ENTER, ESC

VAULT_WORDS = ('RICH', 'REAP', 'HUGE', 'GOLD')
VAULT_MAP = dict(zip('RICHEAPUGOLD', '010293131841'))
_STAMP = dict(zip(VAULT_MAP, ('Bell', 'Crown', 'Eye', 'Key', 'Wing', 'Cup',
                             'Moon', 'Ring', 'Star', 'Mask', 'Coin', 'Sun')))


def pin_for(word):
    return ''.join(VAULT_MAP[letter] for letter in word)


def _clear_notes(app):
    app.dial_scraps = 0
    app.dial_hint = False


def reset_dials(app):
    app.dial = 0
    app.code = app.dial_notice = ''
    _clear_notes(app)


def draw_dials(app):
    word = VAULT_WORDS[app.dial]
    scraps = getattr(app, 'dial_scraps', 0)
    hint = getattr(app, 'dial_hint', False)
    auto = app.dial in (1, 2)
    app.panel('BANK / VAULT DIALS', f'◆ LOCK {app.dial + 1}/4  /  {word}',
              'ENTER TURN  ESC BACK' if auto else
              '0–9 DIALS  ← ERASE  ENTER TURN  J INSPECT  H HINT  ESC BACK')
    if app.dial == 0:
        app.lines(6, 3, 'The lock takes a digit for each letter, left to right.', limit=2)
        if not scraps:
            app.lines(9, 3, 'Two torn receipts are wedged under the lock.', limit=2, color=DIM)
        if scraps >= 1:
            app.put(9, 3, 'STAMP KEY', CYAN, True)
            app.put(10, 3, '  '.join(f'{letter}: {_STAMP[letter]}' for letter in sorted(word)), WHITE)
        if scraps == 1:
            app.lines(12, 3, 'The edge of a second receipt peeks out underneath.', limit=2, color=DIM)
        if scraps >= 2:
            app.put(12, 3, 'TELLER TOTALS', CYAN, True)
            app.put(13, 3, '  '.join(f'{_STAMP[letter]}: {VAULT_MAP[letter]}'
                                   for letter in sorted(word, key=_STAMP.get, reverse=True)), WHITE)
    elif auto:
        app.lines(8, 3, 'Oracle has transcribed these two entries from the receipts.', limit=2, color=DIM)
        app.put(12, 3, 'REJOINED JOURNAL  /  '+word+' → '+pin_for(word), CYAN, True)
    else:
        app.lines(6, 3, 'The last dial is missing its journal entry.', limit=2)
        app.lines(9, 3, 'There’s a rubbing of the pins on the back of the panel.', limit=2, color=DIM)
        if scraps:
            reverse = '   '.join(f'[{digit}]' for digit in reversed(pin_for(word)))
            app.put(12, 3, 'PIN RUBBING FROM BEHIND', CYAN, True)
            app.put(13, 3, f'LOCK EDGE   {reverse}   START EDGE', WHITE)
    if hint and not auto:
        app.put(15, 3, 'MATCHED: ' + '   '.join(f'{letter}={VAULT_MAP[letter]}' for letter in word), GOLD)
    code = pin_for(word) if auto else app.code
    app.mid(17, '   '.join(f'[{digit}]' for digit in code.ljust(4, '_')), WHITE, True)
    app.lines(19, 3, app.dial_notice, limit=2, color=GOLD)


def key_dials(app, key):
    lower = key.lower() if isinstance(key, str) else key
    if key == ESC:
        app.code = app.dial_notice = ''
        app.page = 'brief'
    elif app.dial in (1, 2) and key not in ENTER:
        return
    elif key in (C.KEY_LEFT, C.KEY_BACKSPACE, chr(127), chr(8)):
        app.code = app.code[:-1]
        app.dial_notice = ''
    elif lower == 'j':
        current = getattr(app, 'dial_scraps', 0)
        app.dial_scraps = (current + 1) % (3 if app.dial == 0 else 2)
    elif lower == 'h':
        app.dial_hint = not getattr(app, 'dial_hint', False)
    elif isinstance(key, str) and len(key) == 1 and key in '0123456789':
        app.code = (app.code + key)[:4]
        app.dial_notice = ''
    elif key in ENTER:
        code = pin_for(VAULT_WORDS[app.dial]) if app.dial in (1, 2) else app.code
        if len(code) < 4:
            app.dial_notice = 'Set all four digits before turning the lock.'
        elif code != pin_for(VAULT_WORDS[app.dial]):
            app.code = ''
            app.dial_notice = 'The lock held. Try again; nothing was spent.'
        else:
            app.dial += 1
            app.code = app.dial_notice = ''
            _clear_notes(app)
            if app.dial == len(VAULT_WORDS):
                app.page = 'brief'
                app.notice = 'DIALS OPEN'
