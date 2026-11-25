"""Integration checks for the Bank receipts and the Depths survival objective."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from persona_terminal.persona5.bank_vault import VAULT_WORDS, pin_for
from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona5.campaign_combat import build_stage
from persona_terminal.persona5.campaign_data import NODES
from persona_terminal.persona5.campaign_state import Campaign, TestingCampaign
from persona_terminal.persona5.depths_boss import FIRST_GRAIL, GRAIL
from .test_animation_gallery import Surface


class MeasuredSurface(Surface):
    def put(self, y, x, text, *args, **kwargs):
        assert 0 <= y < self.h, (y, text)
        assert 0 <= x and x + len(text) <= self.w, (x, text)
        super().put(y, x, text, *args, **kwargs)


def before_operation(c, target):
    c.new_game()
    for node in NODES:
        if node['id'] == target:
            return
        c.clear(node['id'])
    raise AssertionError(target)


class BankAndGrailObjectives(TestCase):
    def test_receipts_turn_real_dials_without_writing_until_combat(self):
        for width, height in ((65, 25), (100, 35)):
            with self.subTest(width=width), TemporaryDirectory() as d:
                path = Path(d) / 'slot.json'
                c = Campaign(path)
                before_operation(c, 'bank-vault')
                app = MeasuredSurface(c)
                app.seed = 25
                app.w, app.h = width, height
                before = path.read_bytes()
                app.key('1');app.key('4');app.key('\n')
                self.assertEqual(app.page, 'dials')
                app.draw_dials()
                self.assertIn('Two torn receipts are wedged under the lock.', app.out)
                self.assertNotIn('STAMP KEY', app.out)
                app.key('j');app.out.clear();app.draw_dials()
                self.assertIn('STAMP KEY', app.out)
                self.assertNotIn('TELLER TOTALS', app.out)
                app.key('j');app.out.clear();app.draw_dials()
                self.assertIn('TELLER TOTALS', app.out)
                self.assertTrue(any('R: Bell' in line for line in app.out))
                self.assertTrue(any('Bell: 0' in line for line in app.out))
                self.assertFalse(any(line.startswith('MATCHED:') for line in app.out))
                self.assertEqual(path.read_bytes(), before)

                for digit in '9999':app.key(digit)
                app.key('\n')
                self.assertEqual((app.dial, app.code), (0, ''))
                self.assertIn('nothing was spent', app.dial_notice)
                app.key('1');app.key('\n')
                self.assertEqual((app.dial, app.code), (0, '1'))
                app.key(ESC)
                self.assertEqual((app.page, app.dial, app.code), ('brief', 0, ''))
                app.key('\n');app.key('h');app.out.clear();app.draw_dials()
                self.assertTrue(any(line.startswith('MATCHED: R=0') for line in app.out))
                self.assertEqual(app.code, '')
                app.key('h')

                for word, code in zip(VAULT_WORDS, ('0102', '0931', '2319', '1841')):
                    self.assertEqual(pin_for(word), code)
                for digit in '0102':app.key(digit)
                app.key('\n')
                for ix, translation in ((1, 'REAP → 0931'), (2, 'HUGE → 2319')):
                    self.assertEqual(app.dial, ix)
                    app.out.clear();app.draw_dials()
                    self.assertTrue(any(translation in line for line in app.out))
                    app.key('\n')  # Keep a distinct ring on screen, but no repeated typing.
                self.assertEqual(app.dial, 3)
                app.key('j');app.out.clear();app.draw_dials()
                self.assertIn('PIN RUBBING FROM BEHIND', app.out)
                self.assertTrue(any('[1]   [4]   [8]   [1]   START EDGE' in line for line in app.out))
                for digit in '1481':app.key(digit)
                app.key('\n')
                self.assertEqual(app.dial, 3)
                self.assertIn('nothing was spent', app.dial_notice)
                for digit in '1841':app.key(digit)
                app.key('\n')
                self.assertEqual(app.page, 'brief')
                self.assertEqual(app.notice, 'DIALS OPEN')
                self.assertEqual(path.read_bytes(), before)
                app.key('\n')
                self.assertEqual(app.page, 'battle')
                self.assertEqual(app._b_battle.enemies[0].name, 'Black Ooze')
                self.assertEqual(path.read_bytes(), before)

    def test_first_grail_survival_does_not_destroy_boss_and_commits_route(self):
        with TemporaryDirectory() as d:
            path = Path(d) / 'slot.json'
            c = Campaign(path)
            before_operation(c, 'depths-grail')
            app = Surface(c)
            app.seed = 7
            before = path.read_bytes()
            app.key('1');app.key('3');app.key('\n')
            self.assertEqual(app.page, 'battle')
            b = app._b_battle
            grail = b.enemies[0]
            self.assertEqual(grail.behavior, FIRST_GRAIL)
            self.assertIn('SURVIVE', b.story_intent)
            grail.hp = 1
            # Lethal damage in itself never advances beyond the first encounter.
            b._execute(b.actor, dict(kind='damage', power=999, element='Almighty',
                                    target='enemy', accuracy=999), grail, 'Test strike')
            b._state()
            self.assertEqual((b.phase, grail.hp), ('turn', grail.max_hp))
            self.assertIn('Will of the People restores', b.log[-1])
            self.assertEqual(path.read_bytes(), before)
            telegraph_seen = False
            for _ in range(25):
                if b.phase != 'turn':
                    break
                telegraph_seen |= 'incoming' in b.story_intent
                self.assertIsNone(b.act('guard'))
            self.assertTrue(telegraph_seen)
            self.assertEqual((b.phase, b.wave, grail.hp), ('win', 1, grail.max_hp))
            self.assertTrue(any('survive Eternal Light' in line for line in b.log))
            app.record()
            self.assertEqual(Campaign(path).next_node, 'depths-rebellion')
            self.assertEqual(build_stage(TestingCampaign(),'depths-yaldabaoth', seed=7)
                             .enemies[0].behavior, GRAIL)

    def test_first_grail_lethal_hit_requires_an_unused_final_guard(self):
        for shield_spent in (False, True):
            with self.subTest(shield_spent=shield_spent):
                b = build_stage(TestingCampaign(), 'depths-grail', seed=7)
                while b.phase == 'turn' and 'pending' not in b._boss_state:
                    self.assertIsNone(b.act('guard'))
                self.assertEqual(b.phase, 'turn')
                self.assertIn('ETERNAL LIGHT', b.story_intent)
                b._final_guard_used = shield_spent
                b.allies[0].hp = 1
                while b.phase == 'turn':
                    self.assertIsNone(b.act('guard'))
                self.assertEqual(b.phase, 'loss' if shield_spent else 'win')
                self.assertTrue(b.enemies[0].alive)
                self.assertEqual(any('Final Guard' in line for line in b.log),not shield_spent)
