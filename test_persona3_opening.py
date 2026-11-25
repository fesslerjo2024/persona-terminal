"""Original spring-demo story beats and the native Dark Hour transition."""
import re
import unittest

from persona3_opening import BEATS, BY_ID, TRANSITION_SECONDS, render


class OpeningTests(unittest.TestCase):
    def test_calendar_has_six_spoiler_bounded_checkpoints(self):
        expected = [
            ('arrival','04/06'), ('awakening','04/09'), ('tartarus','04/20'),
            ('relay','04/21'), ('monorail','05/09'), ('finale','05/10'),
        ]
        self.assertEqual([(b.id,b.date) for b in BEATS],expected)
        self.assertTrue(all(BY_ID[b.id] is b for b in BEATS))
        self.assertTrue(all(2 <= len(b.lines) <= 3 for b in BEATS))
        early=' '.join(' '.join(b.lines) for b in BEATS)
        self.assertIn('Orpheus',early)
        self.assertIn('Mitsuru takes the radio',early)
        for forbidden in ('Fuuka','Theurgy'):
            self.assertNotIn(forbidden,early)

    def test_every_scene_is_native_exact_at_compact_and_wide(self):
        art=(*BY_ID,'dark_hour','dorm','thebel','velvet')
        for w,h in ((64,25),(95,34),(28,12)):
            sampled=[]
            for key in art:
                with self.subTest(size=(w,h),key=key):
                    frame=render(key,.81,w,h)
                    self.assertEqual(len(frame),h)
                    self.assertTrue(all(sum(len(text) for text,_ in row)==w for row in frame))
                    self.assertTrue(any(text.strip() for row in frame for text,_ in row))
                    self.assertTrue(all(text.isascii() and not re.search('[A-Za-z]{2,}',text)
                                        for row in frame for text,_ in row))
                    sampled.append(frame)
            self.assertEqual(len(set(sampled)),len(art)-1)  # First climb uses Thebel's same stairs.

    def test_transition_changes_palette_and_motion_then_clamps(self):
        for w,h in ((64,25),(95,34)):
            frames=[render('dark_hour',i*TRANSITION_SECONDS/35,w,h) for i in range(36)]
            inks=lambda frame:{ink for row in frame for text,ink in row if text.strip()}
            self.assertGreaterEqual(len(set(frames)),31)
            self.assertNotIn('forest',inks(frames[0]))
            self.assertIn('forest',inks(frames[-1]))
            self.assertIn('white',inks(frames[14]))
            self.assertNotIn('white',inks(frames[-1]))
            self.assertEqual(frames[-1],render('dark_hour',10,w,h))
