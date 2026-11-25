"""Geometry and authored July hotel entrance animation tests."""
import unittest

from persona3_hotel_art import DURATION, render


def uses(frame):
    return {ink for row in frame for run,ink in row if run.strip()}


class HotelArtTests(unittest.TestCase):
    def test_static_scenes_are_distinct_and_fit_both_usable_screen_sizes(self):
        for w,h in ((64,25),(95,34),(59,6),(90,9)):
            scenes=[render(scene,.25,w,h) for scene in ('arrival','mirror','reunite','exit')]
            self.assertEqual(len(set(scenes)),4)
            for frame in scenes[:2]:
                self.assertGreater(sum(0x2801<=ord(ch)<=0x28ff for row in frame for run,_ in row for ch in run),w*h//5)
            self.assertIn('green',uses(scenes[0]))
            self.assertIn('rose',uses(scenes[1]))
            self.assertIn('amber',uses(scenes[2]))
            self.assertIn('ochre',uses(scenes[3]))
            for frame in scenes:
                self.assertEqual(len(frame),h)
                for row in frame:
                    self.assertEqual(sum(len(s) for s,_ in row),w)
                    self.assertTrue(all(all(ch.isascii() or 0x2801<=ord(ch)<=0x28ff for ch in s)
                                        and not any(x.isalpha() for x in s)
                                        for s,_ in row))

    def test_mirror_wipe_connects_exact_exterior_and_interior_cells(self):
        for w,h in ((64,25),(95,34)):
            frames=[render('intro',DURATION*i/48,w,h) for i in range(49)]
            self.assertEqual(frames[0],render('arrival',0.,w,h))
            self.assertEqual(frames[-1],render('mirror',0.,w,h))
            self.assertEqual(frames[-1],render('intro',15,w,h))
            self.assertIn('white',uses(render('intro',.62,w,h)))
            self.assertNotIn('white',uses(frames[0]))
            self.assertNotIn('white',uses(frames[-1]))
            self.assertGreater(len(set(frames)),25)
            self.assertTrue(all(len(frame)==h and all(sum(len(s) for s,_ in row)==w
                                                      for row in frame) for frame in frames))
