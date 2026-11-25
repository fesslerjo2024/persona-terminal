"""Visual phases in the middle Palace maps keep story unlocks and saves intact."""
import curses
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from campaign_state import Campaign
from campaign_data import CHAPTERS
from palace_map_art import TOP, volume
from palace_menu import map_view, renderers
from test_bank_and_grail_objectives import before_operation
from test_palace_menu import RecordedSurface


def draw(app, time):
    app.reset()
    renderers()[app.chapters[app.ch]['id']](app, map_view(app, time))
    return app.calls


def pixels(calls):
    return [(y, x, s, color) for y, x, s, color, *_ in calls
            if s and all('⠁' <= c <= '⣿' for c in s)]


class MiddlePalaceVisualTests(TestCase):
    def test_practice_pyramid_cutaway_is_stable_through_all_six_selections(self):
        with TemporaryDirectory() as d:
            slot = Path(d) / 'slot.json'
            app = RecordedSurface(Campaign(slot))
            app.begin_extra('practice')
            app.ch = next(i for i, chapter in enumerate(CHAPTERS) if chapter['id'] == 'pyramid')
            for w, h in ((65, 25), (96, 35)):
                app.w, app.h = w, h
                app.pick = 0
                cutaway = pixels(draw(app, 1))
                self.assertTrue(any(x < w//2 for _, x, *_ in cutaway))
                self.assertIn('‹/\\›', app.out)
                for i in range(1, 6):
                    app.key(curses.KEY_DOWN)
                    self.assertEqual(pixels(draw(app, 1+i)), cutaway)
                    self.assertIn(app.nodes()[i]['title'], app.out)
            self.assertFalse(slot.exists())

    def test_pyramid_dunes_stay_until_the_papyrus_is_earned(self):
        for w, h in ((65, 25), (96, 35)):
            with self.subTest(size=(w, h)), TemporaryDirectory() as d:
                slot = Path(d) / 'slot.json'
                campaign = Campaign(slot)
                before_operation(campaign, 'pyramid-desert')
                app = RecordedSurface(campaign)
                app.w, app.h = w, h
                app.key('1')
                before = slot.read_bytes()
                approach = pixels(draw(app, 1))
                self.assertTrue(approach)
                self.assertTrue(all(x >= max(44, w//2+6) for _, x, *_ in approach))
                self.assertEqual(app.out.count('[··]'), 6)
                self.assertIn('???', '\n'.join(app.out))
                app.pick = 1
                self.assertEqual(pixels(draw(app, 2)), approach)
                self.assertEqual(before, slot.read_bytes())
                campaign.clear('pyramid-desert', 'A')
                after = slot.read_bytes()
                cutaway = pixels(draw(app, 3))
                self.assertTrue(any(x < w//2 for _, x, *_ in cutaway))
                self.assertEqual(app.out.count('[··]'), 5)
                self.assertIn('Light Across the Chasm', app.out)
                self.assertIn('[A]', '\n'.join(app.out))
                self.assertEqual(after, slot.read_bytes())

    def test_casino_wheel_is_absent_until_the_high_limit_unlock(self):
        for w, h in ((65, 25), (96, 35)):
            with self.subTest(size=(w, h)), TemporaryDirectory() as d:
                slot = Path(d) / 'slot.json'
                campaign = Campaign(slot)
                before_operation(campaign, 'casino-rigging')
                app = RecordedSurface(campaign)
                app.w, app.h = w, h
                app.key('1')
                before = slot.read_bytes()
                locked = pixels(draw(app, 1))
                self.assertTrue(locked)
                self.assertFalse(any(x > w//2 for _, x, *_ in locked))
                self.assertNotIn('HIGH LIMIT', app.out)
                app.pick = 5
                self.assertEqual(pixels(draw(app, 2)), locked)
                self.assertEqual(before, slot.read_bytes())
                campaign.clear('casino-rigging', 'B')
                after = slot.read_bytes()
                wheel = [q for q in pixels(draw(app, 3)) if q[1] > w//2]
                self.assertTrue(wheel)
                self.assertIn('HIGH LIMIT', app.out)
                longest = 'Turn the House Against Itself'
                row_y, row_x, row_label, *_ = next(call for call in app.calls if longest in call[2])
                self.assertTrue(all(y != row_y or x >= row_x+len(row_label)+3
                                    for y, x, *_ in wheel))
                app.pick = 0
                self.assertEqual(wheel, [q for q in pixels(draw(app, 4)) if q[1] > w//2])
                self.assertEqual(after, slot.read_bytes())

    def test_spaceport_locked_focus_neither_animates_nor_looks_enabled(self):
        with TemporaryDirectory() as d:
            slot = Path(d) / 'slot.json'
            campaign = Campaign(slot)
            before_operation(campaign, 'spaceport-entry')
            app = RecordedSurface(campaign)
            app.key('1')
            before = slot.read_bytes()
            chosen = pixels(draw(app, 1))
            app.pick = 1
            locked = list(draw(app, 1.25))
            self.assertNotEqual(pixels(locked), chosen)
            self.assertTrue(any(s == '???' and not reverse for _, _, s, _, _, reverse in locked))
            self.assertFalse(any(rev for _, _, _, _, _, rev in locked))
            self.assertEqual(pixels(locked), pixels(draw(app, 2.5)))
            self.assertEqual(before, slot.read_bytes())

    def test_spaceport_conveyor_links_each_pair_to_the_next_pair(self):
        with TemporaryDirectory() as d:
            slot = Path(d) / 'slot.json'
            app = RecordedSurface(Campaign(slot))
            app.begin_extra('practice')
            app.ch = next(i for i, chapter in enumerate(CHAPTERS) if chapter['id'] == 'spaceport')
            for w, h in ((65, 25), (96, 35)):
                app.w, app.h = w, h
                calls = draw(app, 2)
                art = pixels(calls)
                self.assertFalse(any('→' in text for _, _, text, *_ in calls))
                for level in range(3):
                    belt = TOP+(level+1)*volume(app)//3-1
                    self.assertTrue(any(abs(y-belt) <= 1 and x <= w//2
                                        and x+len(s) > w//2 for y, x, s, _ in art))
                for level in (1, 2):
                    boundary = TOP+level*volume(app)//3
                    self.assertTrue(any(abs(y-boundary) <= 1 and x < w//2+2
                                        and x+len(s) >= w//2-1 for y, x, s, _ in art))
            self.assertFalse(slot.exists())
