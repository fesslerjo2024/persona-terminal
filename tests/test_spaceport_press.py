"""Spaceport route interaction and briefing promises."""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import curses as C

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona5.campaign_data import NODES
from persona_terminal.persona5.campaign_state import Campaign
from persona_terminal.persona5.spaceport_press import CROSSING_SECONDS, PressConsole
from .test_bank_and_grail_objectives import MeasuredSurface, before_operation


class SpaceportPressTests(TestCase):
    def test_console_choices_are_safe_repeatable_and_fit(self):
        for width, height in ((65, 25), (100, 35)):
            with self.subTest(width=width), TemporaryDirectory() as d:
                path = Path(d) / 'slot.json'
                c = Campaign(path)
                before_operation(c, 'spaceport-factory')
                save = sha256(path.read_bytes()).hexdigest()
                app = MeasuredSurface(c)
                app.w, app.h = width, height
                console = PressConsole()

                console.draw(app)
                self.assertTrue(any(f'{CROSSING_SECONDS} seconds' in row for row in app.out))
                self.assertFalse(console.can_cross)
                self.assertEqual(console.key(app, ESC), 'back')
                self.assertIsNone(console.key(app, '\n'))  # Highlighted short break.
                self.assertFalse(console.can_cross)
                app.out.clear();console.draw(app)
                self.assertIn('The ram drops after 5s. The crew stays back.', app.out)
                self.assertIsNone(console.key(app, '\n'))  # Same retry remains safe.
                self.assertIsNone(console.key(app, C.KEY_DOWN))
                self.assertIsNone(console.key(app, '\n'))
                self.assertTrue(console.can_cross)
                app.out.clear();console.draw(app)
                self.assertIn('PRESS LOCKED OPEN', app.out)
                self.assertEqual(console.key(app, ESC), 'back')
                self.assertIsNone(console.key(app, '2'))  # Not an implicit proceed.
                self.assertEqual(console.key(app, '\n'), 'cross')
                self.assertEqual(sha256(path.read_bytes()).hexdigest(), save)

    def test_tactical_routes_describe_playable_goals(self):
        by_id = {node['id']: node for node in NODES}
        factory = by_id['spaceport-factory']
        self.assertTrue(factory['press_console'])
        self.assertIn('Stop the press', factory['tactic'])
        self.assertEqual(len(factory['waves']), 2)
        chasm = by_id['pyramid-light']
        self.assertIn('Jewel Warden', chasm['tactic'])
        self.assertTrue(any('Jewel Warden' in wave for wave in chasm['waves']))
        self.assertNotIn('pedestal', chasm['brief'].lower())
        hull = by_id['spaceport-airlocks']
        self.assertEqual(len(hull['waves']), 2)
        self.assertIn('patrols', hull['brief'])
        self.assertNotIn('switch', hull['tactic'].lower() + hull['brief'].lower())
