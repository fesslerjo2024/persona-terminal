import curses as C
import unittest

from puzzle_ui import PyramidSwitchboard


class CompactScreen:
    """Minimal CampaignApp rendering interface with strict 65-column bounds."""
    w, h = 65, 25

    def __init__(self):
        self.rows = [list(" " * self.w) for _ in range(self.h)]

    def put(self, y, x, text, *_):
        assert 0 <= y < self.h and 0 <= x < self.w
        assert x + len(text) < self.w, (x, text)
        self.rows[y][x:x + len(text)] = text

    def mid(self, y, text, *args):
        self.put(y, (self.w - len(text)) // 2, text, *args)

    def frame(self, title, footer):
        self.mid(1, title)
        self.mid(23, footer)

    def text(self):
        return "\n".join(map("".join, self.rows))


class PyramidSwitchboardTests(unittest.TestCase):
    def setUp(self):
        self.board = PyramidSwitchboard()

    def tap(self, sequence):
        for key in sequence:
            result = self.board.key(key)
        return result

    def render(self):
        screen = CompactScreen()
        self.board.draw(screen)
        return screen.text()

    def test_first_slab_clue_and_noncolor_controls_fit_compact(self):
        text = self.render()
        self.assertIn("BLUE 01010", text)
        self.assertIn("OFF  OFF  OFF  OFF  OFF", text)
        self.assertIn("> BLUE [B]", text)
        self.assertIn("LOCKED ON THIS SLAB", text)
        self.assertIn("S SKIP", text)
        self.assertIn("Optional:", text)

    def test_wrong_answer_preserves_bits_and_allows_correction(self):
        self.assertIsNone(self.tap("24\b3\r"))
        self.assertEqual(self.board.slab, 0)
        self.assertIn("BLUE mismatch", self.render())
        self.assertEqual(self.board._state("B"), "01110")
        self.assertIsNone(self.tap("3\n"))
        self.assertEqual(self.board.slab, 1)
        self.assertIn("RED 01100     BLUE 10011", self.render())
        self.assertEqual(self.board._state("B"), "00000")

    def test_second_slab_requires_both_rows_and_reset_stays_there(self):
        self.tap("24\rr23\r")
        self.assertIn("BLUE mismatch", self.render())
        self.assertEqual(self.board._state("R"), "01100")
        self.tap("x")
        self.assertEqual(self.board.slab, 1)
        self.assertEqual(self.board._state("R"), "00000")
        self.assertEqual(self.board._state("B"), "00000")
        self.board.key(C.KEY_UP)
        self.tap("23")
        self.board.key(C.KEY_DOWN)
        self.assertEqual(self.tap("145\r"), "solved")

    def test_locked_red_and_irrelevant_inputs_do_not_toggle(self):
        self.assertIsNone(self.tap("r7?"))
        self.assertIn("red row is locked", self.render())
        self.assertEqual(self.board.active, "B")
        self.assertEqual(self.board._state("B"), "00000")

    def test_optional_skip_and_back_are_distinct(self):
        self.assertEqual(self.tap("S"), "bypass")
        other = PyramidSwitchboard()
        self.assertEqual(other.key("\x1b"), "back")
        self.assertIsNone(PyramidSwitchboard().result)


if __name__ == "__main__":
    unittest.main()
