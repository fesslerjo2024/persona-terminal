"""The first Palace skirmish: two commands, real turns, no campaign rewards."""
from .battle_data import shadow
from .battle_engine import Battle
from .battle_ui import CYAN, GOLD, GREEN, WHITE


SCENE_KEY = 'april-infiltration'
SCENE_ID = 'castle-return'
FIGHT = 'escape-fight'
RETURN_BEAT = 'return'
FOE = 'Cell Guard'


class EscapeFight:
    def __init__(self, seed):
        self.battle = Battle((), 'Cell Passage', seed=seed, shuffle_turns=False,
                             encounter_config={'id': 'first-escape', 'party_size': 1,
                                               'waves': [[FOE]]},
                             enemy_data={FOE: shadow(70, 0, (), no_knockdown=True)},
                             joker_stats={'hp': 135, 'sp': 0, 'ammo': 0})
        self.pick = 0
        self.feedback = ()

    def buttons(self, width):
        if self.battle.phase != 'turn':
            label = 'Follow Morgana' if self.battle.phase == 'win' else 'Try again'
            return ((14, 3, f' ▶  {label}  ', '\n'),)
        return tuple((12+i, 3, label.ljust(min(29, width-6)), str(i+1))
                     for i, label in enumerate(('Attack', 'Guard')))

    def act(self, action):
        b = self.battle
        before = len(b.log)
        problem = b.act(action, b.enemies[0] if action == 'attack' else None)
        self.feedback = ((problem,) if problem else
                         tuple(line.replace('Joker guards.', 'You guard.').replace('Joker takes', 'You take').replace('Joker', 'You')
                               for line in b.log[before:] if not line.startswith(('Round ', 'Trial cleared.'))))
        return b.phase

    def draw(self, app):
        b = self.battle
        if b.phase != 'turn':
            win = b.phase == 'win'
            app.panel('APRIL / CELL PASSAGE', 'THE PASSAGE IS CLEAR' if win else 'THE GUARD CUTS YOU OFF',
                      'ENTER SELECT  ESC TITLE')
            app.lines(8, 3, 'Morgana holds the side door open. Ryuji is already through.' if win else
                      'Morgana pulls you back behind the bars. Try again when you’re ready.', limit=3)
            row, col, label, _ = self.buttons(app.w)[0]
            app.put(row, col, label, CYAN, True, True)
            return
        app.panel('APRIL / CELL PASSAGE', 'A GUARD BLOCKS THE EXIT', '↑↓ SELECT  ENTER ACT  ESC TITLE')
        app.lines(6, 3, 'Morgana gets Ryuji through the side door. Hold the guard off, then follow.', limit=2)
        you, enemy = b.allies[0], b.enemies[0]
        app.put(9, 3, f'YOU  {you.hp}/{you.max_hp} HP', GREEN, True)
        app.put(10, 3, f'{FOE.upper()}  {enemy.hp}/{enemy.max_hp} HP', GOLD, True)
        rows = (('Attack', '', True), ('Guard', '', True))
        app._b_list(rows, 12, 3, min(29, app.w-6), 2, self.pick, details=False)
        app.lines(15, 3, ('Attack does damage.' if self.pick == 0 else
                           'Guard reduces damage from the guard’s next attack.'), limit=2, color=CYAN)
        for row, line in enumerate(self.feedback[-3:], 18):
            app.put(row, 3, line[:app.w-6], WHITE)
