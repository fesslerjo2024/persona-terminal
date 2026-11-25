"""Read-only visual changes for the live field interaction panels."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from campaign_state import Campaign
from casino_route import CasinoRoute
from lab_infiltration import LabInfiltration
from spaceport_press import PressConsole
from test_bank_and_grail_objectives import MeasuredSurface


def dots(writes):
    return tuple(val for val in writes if any('\u2801' <= ch <= '\u28ff' for ch in val))


class StoryArtTests(TestCase):
    def test_press_and_bridge_change_drawn_geometry_without_changing_keys(self):
        for width,height in ((65,25),(96,35)):
            with self.subTest(width=width), TemporaryDirectory() as d:
                path=Path(d)/'disposable.json'
                store=Campaign(path)
                store.new_game()
                save=path.read_bytes()
                app=MeasuredSurface(store);app.w,app.h=width,height
                press=PressConsole()
                press.draw(app)
                down=dots(app.out)
                self.assertGreater(len(down),6)
                self.assertIsNone(press.key(app,'2'))
                app.out.clear();press.draw(app)
                self.assertNotEqual(down,dots(app.out))
                self.assertIn('PRESS LOCKED OPEN',app.out)
                self.assertEqual(press.key(app,'\n'),'cross')
                bridge=LabInfiltration('laboratory-colors','bridge')
                app.out.clear();bridge.draw(app)
                red=dots(app.out)
                self.assertGreater(len(red),6)
                self.assertIn('CLOSED WARD',app.out)
                self.assertIn('EDEN',app.out)
                self.assertIsNone(bridge.key(app,'2'))
                self.assertIn('Stay on this side',bridge.warning)
                self.assertIsNone(bridge.key(app,'1'))
                app.out.clear();bridge.draw(app)
                self.assertNotEqual(red,dots(app.out))
                self.assertIn('Blue span leads to Eden.',app.out)
                self.assertEqual(bridge.key(app,'2'),'deploy')
                self.assertEqual(path.read_bytes(),save)

    def test_existing_slot_result_is_visible_beside_native_art(self):
        for width,height in ((65,25),(96,35)):
            with self.subTest(width=width), TemporaryDirectory() as d:
                path=Path(d)/'disposable.json'
                store=Campaign(path)
                store.new_game()
                save=path.read_bytes()
                app=MeasuredSurface(store);app.w,app.h=width,height
                route=app.casino_route=CasinoRoute(coins=5_000)
                route.open('slots')
                app.draw_casino_route()
                before=dots(app.out)
                self.assertGreater(len(before),6)
                self.assertIn('[   ]   [   ]   [   ]',app.out)
                self.assertNotIn('[ 7 ]   [ 7 ]   [ 7 ]',app.out)
                for action in ('scan','green','red','spin'):route.choose(action)
                app.out.clear();app.draw_casino_route()
                self.assertNotEqual(before,dots(app.out))
                self.assertIn('[ 7 ]   [ 7 ]   [ 7 ]',app.out)
                self.assertIn('Buy the High Limit card', '\n'.join(app.out))
                self.assertEqual(path.read_bytes(),save)
