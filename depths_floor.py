"""Optional Depths traversal: Royal's entry-toggle rule, an original board."""
import curses as C

from battle_ui import CYAN, DIM, ENTER, ESC, GOLD, GREEN, WHITE


SIZE = 3
START = (0, 0)
EXIT = (2, 2)
INITIAL_BLUE = frozenset({(0, 1), (1, 2)})
DIRECTIONS = {C.KEY_UP: (-1, 0), C.KEY_DOWN: (1, 0),
              C.KEY_LEFT: (0, -1), C.KEY_RIGHT: (0, 1)}


class DepthsLightFloor:
    """Local puzzle only; the caller owns the single-attempt battle reward."""

    def __init__(self):
        self.result = None
        self.reset()

    def reset(self):
        self.blue = set(INITIAL_BLUE)
        self.position = START
        self.moves = 0
        self.blue.symmetric_difference_update((START,))
        self.message = 'Entry flipped the START tile.'

    @property
    def ready(self):
        return self.position == EXIT and len(self.blue) == SIZE * SIZE

    def key(self, key):
        if self.result:
            return self.result
        if key in (ESC, 27):
            self.result = 'back'
        elif key in ('s', 'S'):
            self.result = 'bypass'
        elif key in ('x', 'X'):
            self.reset()
            self.message = 'Floor reset. Entry flipped START again.'
        elif key in ENTER or key in (10, 13):
            if self.ready:
                self.result = 'solved'
            elif len(self.blue) == SIZE * SIZE:
                self.message = 'All nine are blue. Submit from EXIT.'
            else:
                remaining = SIZE * SIZE - len(self.blue)
                self.message = f'{remaining} still yellow. Finish with all nine blue on EXIT.'
        elif key in DIRECTIONS:
            dy, dx = DIRECTIONS[key]
            y, x = self.position
            next_tile = (y + dy, x + dx)
            if any(n < 0 or n >= SIZE for n in next_tile):
                self.message = 'Wall. Stay on the floor.'
            else:
                self.position = next_tile
                self.moves += 1
                self.blue.symmetric_difference_update((next_tile,))
                self.message = ''
        return self.result

    def draw(self, app):
        app.frame('DEPTHS / LIGHT FLOOR', '← ↑ ↓ → MOVE   ENTER CHECK   X RESET   S SKIP   ESC BACK')
        app.mid(4, 'PRISON PASSAGE / LIGHT FLOOR', WHITE, True)
        app.mid(6, 'Every step flips the tile you enter.', DIM)
        app.mid(7, 'Make all nine BLUE and reach EXIT.', WHITE)
        for row in range(SIZE):
            for col in range(SIZE):
                position = row, col
                lit = position in self.blue
                here = position == self.position
                flag = 'START' if position == START else 'EXIT' if position == EXIT else ''
                left, right = ('[', ']') if here else (' ', ' ')
                label = '+ BLUE' if lit else '- YELLOW'
                cell = f'{left}{label:^8}{right} {flag:<5}'
                x = (app.w - (16 * SIZE + 2 * (SIZE - 1))) // 2 + col * 18
                app.put(10+row*2, x, cell, CYAN if lit else GOLD, here)
        app.mid(16, '[ ] You     + BLUE / ON     - YELLOW / OFF', DIM)
        app.mid(18, f'BLUE {len(self.blue)}/9    /    STEPS {self.moves}', CYAN, True)
        if self.ready:
            app.mid(20, 'EXIT READY / Enter to take the supply and deploy.', GREEN, True)
        elif self.message:
            app.mid(20, self.message, GOLD, True)
