import unittest

from persona3_allout import FINISHERS, FINISH_SECONDS, IMPACT_SECONDS, render_all_out
from reel_palette import IDS


class AllOutArtworkTest(unittest.TestCase):
    def test_terminal_native_frames_and_unique_finisher_poses(self):
        inks=set(IDS)|{'red','gold','cyan','white','dim','green'}
        for w,h in ((64,25),(95,35),(130,42)):
            finals=set()
            for name in FINISHERS:
                frames=[render_all_out(name,t,w,h) for t in (0.,.25,.45,.62,.81,1.,FINISH_SECONDS-.1)]
                for rows in frames:
                    self.assertEqual(len(rows),h)
                    for row in rows:
                        self.assertEqual(sum(len(run) for run,_ in row),w)
                        self.assertTrue(all(ink in inks and all(ch.isascii() or
                            ('\u2801'<=ch<='\u28ff' or ch in '─█') for ch in run)
                            for run,ink in row))
                self.assertGreater(sum('\u2800'<ch<='\u28ff' for row in frames[-1]
                                       for run,_ in row for ch in run),w*h//8)
                partial={ch for row in frames[-1] for run,_ in row for ch in run
                         if '\u2800'<ch<'\u28ff'}
                self.assertGreater(len(partial),30)
                # The final poster intentionally holds steady for readability.
                self.assertEqual(len(set(frames[:5])),5)
                finals.add(tuple(''.join(text for text,_ in row) for row in frames[-1]))
            self.assertEqual(len(finals),9)

    def test_shared_impact_uses_standing_cast_and_target_count(self):
        # Compare an early frame where combatants are still visible.
        solo=render_all_out('Makoto',.12,95,35,finishing=False,cast=('Makoto',),targets=1)
        squad=render_all_out('Makoto',.12,95,35,finishing=False,cast=FINISHERS[:4],targets=3)
        self.assertNotEqual(solo,squad)
        for art in (solo,squad):
            self.assertGreater(sum('\u2800'<ch<='\u28ff' for row in art
                                   for run,_ in row for ch in run),100)
        late=render_all_out('Makoto',IMPACT_SECONDS,95,35,finishing=False)
        self.assertNotEqual(late,render_all_out('Makoto',FINISH_SECONDS,95,35))
