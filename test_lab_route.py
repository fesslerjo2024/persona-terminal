"""Focused tests for the optional Laboratory consultation board."""
import textwrap
import unittest

from battle_ui import ESC
from lab_route import EXAMS, LabConsultation


class MinimumView:
    h, w = 25, 65

    def __init__(self):
        self.body = {}

    def frame(self, title, footer):
        self.body[1] = title
        self.body[self.h - 2] = footer

    def put(self, y, x, value, *_style):
        if not 0 <= y < self.h or len(value) + x >= self.w:
            raise AssertionError(f"Outside frame at {y}, {x}: {value}")
        self.body[y] = value

    def lines(self, y, x, value, *, limit, color=None):
        wrapped = textwrap.wrap(value, self.w - 6)
        if len(wrapped) > limit:
            raise AssertionError(f"Would truncate at row {y}: {value}")
        for row, line in enumerate(wrapped, start=y):
            self.put(row, x, line, color)


class LabConsultationTests(unittest.TestCase):
    def test_three_canonical_answers(self):
        view = LabConsultation()
        self.assertIsNone(view.key('b'))
        self.assertEqual(view.room, 1)
        self.assertIsNone(view.key('C'))
        self.assertEqual(view.room, 2)
        self.assertEqual(view.key('d'), 'solved')

    def test_retry_is_free_and_does_not_reset_previous_room(self):
        view = LabConsultation()
        view.key('B')
        self.assertIsNone(view.key('A'))
        self.assertIn('Treatment detour', view.notice)
        self.assertEqual(view.room, 1)
        self.assertIsNone(view.key('C'))
        self.assertEqual(view.room, 2)

    def test_hint_reset_skip_and_back_actions(self):
        view = LabConsultation()
        view.key('H')
        self.assertTrue(view.huddle)
        view.key('B')
        self.assertFalse(view.huddle)
        view.key('X')
        self.assertEqual(view.room, 0)
        self.assertEqual(view.key('s'), 'bypass')
        self.assertEqual(LabConsultation().key(ESC), 'back')
        self.assertEqual(LabConsultation().key(27), 'back')

    def test_every_screen_fits_the_minimum_terminal(self):
        view = LabConsultation()
        for i, (_, _, options, correct, _) in enumerate(EXAMS):
            with self.subTest(room=i):
                body = MinimumView()
                view.draw(body)
                self.assertEqual(body.body[11], options[0])
                self.assertEqual(body.body[10+len(options)], options[-1])
                view.key('H')
                body = MinimumView()
                view.draw(body)
                self.assertIn("HUDDLE", body.body[17])
                self.assertIn("S SKIP", body.body[23])
                view.key(correct)


if __name__ == '__main__':
    unittest.main()
