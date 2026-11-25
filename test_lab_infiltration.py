"""Real campaign key routes for the small Laboratory decisions."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from battle_ui import ESC
from campaign_state import Campaign
from test_bank_and_grail_objectives import MeasuredSurface, before_operation


class LabInfiltrationTests(TestCase):
    def with_room(self, case, index, node_id, visit):
        for width, height in ((65, 25), (100, 35)):
            with self.subTest(case=case, width=width), TemporaryDirectory() as d:
                file = Path(d) / 'slot.json'
                c = Campaign(file)
                before_operation(c, node_id)
                original = file.read_bytes()
                a = MeasuredSurface(c)
                a.w, a.h, a.seed = width, height, 7
                a.key('1');a.key(index)
                self.assertEqual(a.node['id'], node_id)
                a.brief()
                self.assertIn('ENTER '+a.deployment_label(), ' '.join(a.out))
                a.key('\n')
                self.assertEqual(a.page, 'lab-route')
                a.out.clear();a.lab_route.draw(a)
                visit(a, ' '.join(a.out))
                self.assertEqual(file.read_bytes(), original)

    def test_archive_has_two_readable_records_and_neither_is_a_quiz(self):
        def visit(a, first):
            self.assertIn('PATIENT RECORDS', first)
            a.key('1')
            a.out.clear();a.lab_route.draw(a)
            self.assertIn('She can no longer remember why', ' '.join(a.out))
            a.key(ESC)
            self.assertEqual(a.page, 'lab-route')
            a.key('2')
            a.out.clear();a.lab_route.draw(a)
            self.assertIn('AUTHORIZATION NOT REQUIRED', ' '.join(a.out))
            a.key('\n')
            self.assertEqual(a.page, 'battle')
            self.assertEqual(a._b_battle.wave, 1)
            self.assertTrue(any('opens the archive' in row for row in a._b_battle.log))
        self.with_room('archive', '3', 'laboratory-records', visit)

    def test_both_consultation_choices_deploy_with_distinct_opening_states(self):
        for decision, approved in (('1', True), ('2', False)):
            def visit(a, first):
                self.assertIn('A pianist hurt her hand', first)
                a.key(decision)
                a.out.clear();a.lab_route.draw(a)
                self.assertIn('TREATMENT '+('ACCEPTED' if approved else 'REJECTED'), a.out)
                a.key('\n')
                self.assertEqual(a.page, 'battle')
                b = a._b_battle
                if approved:
                    self.assertTrue(all(u.buffs.get('defense') == (1, 1) for u in b.allies))
                    actor = b.actor
                    b.act('guard')
                    self.assertNotIn('defense', actor.buffs)
                else:
                    self.assertFalse(any('defense' in u.buffs for u in b.allies))
                    self.assertTrue(any('maintenance hatch' in row for row in b.log))
            self.with_room('consultation '+decision, '4', 'laboratory-counseling', visit)

    def test_dark_span_cannot_be_crossed_and_switch_has_visible_effect(self):
        def visit(a, first):
            self.assertIn('Red span leads to the closed ward', first)
            a.key('2')
            self.assertEqual(a.page, 'lab-route')
            a.out.clear();a.lab_route.draw(a)
            self.assertIn('Stay on this side', ' '.join(a.out))
            a.key('1')
            a.out.clear();a.lab_route.draw(a)
            self.assertIn('Blue span leads to Eden.', a.out)
            a.key(ESC)
            self.assertEqual(a.page, 'brief')
            a.key('\n')
            self.assertFalse(a.lab_route.blue)
            a.key('1');a.key('2')
            self.assertEqual(a.page, 'battle')
            self.assertEqual(a._b_battle.enemies[0].name, 'Fafnir')
        self.with_room('bridge', '5', 'laboratory-colors', visit)
