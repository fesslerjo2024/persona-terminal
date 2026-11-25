"""Battle rendering keeps instructions contextual, including 65-column layouts."""
from functools import partial
import unittest

from persona_terminal.persona5.battle_engine import Battle
from persona_terminal.persona5.battle_ui import BattleUI, ESC


class Recorder(BattleUI):
    def __init__(self, width=65, height=25):
        self.w, self.h = width, height
        self.page = 'trials'
        self.battle_init()
        self._b_class = partial(Battle, shuffle_turns=False)
        self.written = []

    def frame(self, title, footer):
        self.last_title, self.last_footer = title, footer
        self.written.append((self.h-2, 2, footer))

    def put(self, y, x, value, *_):
        self.written.append((y, x, value))

    def mid(self, y, value, *_):
        self.put(y, 0, value)

    def render(self):
        self.written.clear()
        self.battle_page()
        return '\n'.join(v for _, _, v in self.written)


class InformationAudit(unittest.TestCase):
    def test_trial_setup_keeps_one_role_and_no_repeated_instructions(self):
        for width, height in ((65, 25), (110, 40)):
            ui = Recorder(width, height)
            screen = ui.render()
            self.assertEqual(screen.count('Wind • healing • critical hits'), 1)
            self.assertEqual(screen.count('Castle Downfall'), 1)
            self.assertEqual(screen.count('S DEPLOY'), 1)
            self.assertNotIn('Select three allies, then deploy.', screen)
            self.assertNotIn('ORACLE INTEL', screen)
            self.assertLessEqual(len(ui.last_footer), width-4)
            ui._b_trial = ui._b_trial_names.index('Wild Card: Joker Solo')
            screen = ui.render()
            self.assertIn('No allies or Baton Pass in this trial.', screen)
            self.assertNotIn('TOGGLE', screen)
            self.assertNotIn('critical hits', screen)

    def test_arena_info_is_contextual(self):
        for width, height in ((65, 25), (110, 40)):
            ui = Recorder(width, height)
            ui._b_launch()
            screen = ui.render()
            self.assertNotIn('W Weak', screen)
            self.assertIn('COMMANDS', screen)
            self.assertIn('NOW Joker', screen)
            self.assertIn('I STATUS', ui.last_footer)
            self.assertIn('? HELP', ui.last_footer)
            self.assertLessEqual(len(ui.last_footer), width-4)

            ui.battle_key('?')
            screen = ui.render()
            self.assertEqual(screen.count('W Weak'), 1)
            self.assertIn('P Repel D Drain', screen)
            self.assertEqual(ui.last_footer, 'E ELEMENTS  ESC BACK')
            ui.battle_key(ESC)

            ui.battle_key('1')
            screen = ui.render()
            self.assertIn('←→ PERSONA', ui.last_footer)
            self.assertNotIn('JOKER /', screen)
            ui.battle_key(ESC)
            ui.battle_key('2')
            screen = ui.render()
            self.assertIn('→ TARGET', screen)
            # HP/SP remains in the roster, not repeated underneath target rows.
            self.assertFalse(any('HP ' in value and '   SP ' in value
                                 for y, x, value in ui.written if y==height-4))
            ui.battle_key(ESC)

            ui.battle_key('i')
            screen = ui.render()
            self.assertNotIn('Number = turns left', screen)
            self.assertIn('PHANTOM THIEVES', screen)
            self.assertIn('SHADOWS', screen)
            ui._b_battle.allies[0].buffs['attack'] = (1, 2)
            screen = ui.render()
            self.assertIn('ATK↑2', screen)
            self.assertEqual(screen.count('Number = turns left'), 1)
            self.assertEqual(ui.last_footer, 'ESC BACK')
            ui.battle_key(ESC)
            current = ui._b_battle
            ui.battle_key(ESC)
            self.assertIs(ui._b_battle, current)
            self.assertEqual(ui.page, -1)


if __name__ == '__main__':
    unittest.main()
