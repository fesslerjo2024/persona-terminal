import textwrap
import unittest

from persona3_mirror_art import observation, render
from persona3_upper import MIRRORS


def glyphs(rows):
    return tuple("".join(run for run, _ in row) for row in rows)


class MirrorArtTests(unittest.TestCase):
    def test_all_six_real_options_clue_visible_without_color(self):
        for width, height in ((59, 6), (59, 7), (61, 8), (90, 9), (95, 34)):
            for room in MIRRORS:
                fronts, mirrored = [], []
                for i, (_, show_reflection) in enumerate(room.mirrors):
                    with self.subTest(room=room.room, option=i, size=(width, height)):
                        rows = render(show_reflection, width, height, option=i, room=room.room)
                        view = glyphs(rows)
                        witness = glyphs(render(not show_reflection, width, height, option=i, room=room.room))
                        self.assertEqual(len(view), height)
                        self.assertTrue(all(len(row) == width and all(
                            ch == ' ' or 0x2801 <= ord(ch) <= 0x28ff for ch in row) for row in view))
                        self.assertEqual(view[-3:], witness[-3:])  # Sill and real party stay put.
                        center = slice(width*3//10, width*7//10)
                        glass = "\n".join(row[center] for row in view[:-3])
                        other = "\n".join(row[center] for row in witness[:-3])
                        # Compare shape alone: the reflected crew must change the
                        # central glass even if the user cannot distinguish inks.
                        present, absent = (glass, other) if show_reflection else (other, glass)
                        dot_count = lambda art: sum((ord(ch)-0x2800).bit_count()
                                                    for ch in art if 0x2801 <= ord(ch) <= 0x28ff)
                        self.assertGreater(dot_count(present), dot_count(absent))
                        self.assertNotEqual(glass, other)
                        self.assertGreater(dot_count(absent), 0)  # Glass still shows the room.
                        one = glyphs(render(show_reflection, width, height, option=i,
                                           room=room.room, members=1))
                        self.assertGreater(dot_count("\n".join(view[-2:])),dot_count("\n".join(one[-2:])))
                        fronts.append(glyphs(render(False, width, height, option=i, room=room.room)))
                        mirrored.append(glass)
                self.assertEqual(len(set(fronts)), 3)  # Distinct props/frames, even without party.
                self.assertEqual(len(set(mirrored)), 3)

    def test_description_matches_visible_observation_not_action(self):
        real, missing = observation(True), observation(False)
        self.assertIn("below the frame", real)
        self.assertIn("below the frame", missing)
        self.assertTrue(real.endswith("the room and your squad."))
        self.assertTrue(missing.endswith("the room, but nobody is in it."))
        for desc in (real, missing):
            self.assertEqual(len(textwrap.wrap(desc, width=55)), 2)
            self.assertNotIn("break", desc.lower())


if __name__ == "__main__":
    unittest.main()
