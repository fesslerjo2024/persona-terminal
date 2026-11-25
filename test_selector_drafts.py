from unittest import TestCase
from selector_draft_gallery import INKS, TITLES, candidates, picture


class SelectorDraftTests(TestCase):
    def test_nine_distinct_animated_drafts_per_game(self):
        for game in TITLES:
            names=[name for name,_ in candidates(game)]
            self.assertEqual(len(set(names)),9)
            for w,h in ((17,5),(21,9),(26,11),(38,16)):
                final=set()
                for i,name in enumerate(names):
                    with self.subTest(game=game,draft=name,viewport=(w,h)):
                        cuts=[picture(game,i,w,h,frame) for frame in (0,6,16,26,36)]
                        self.assertGreaterEqual(len(set(cuts)),3)
                        final.add(cuts[-1])
                        for frame in cuts:
                            self.assertEqual(len(frame),h)
                            self.assertTrue(all(sum(len(run) for run,_ in row)==w for row in frame))
                            self.assertTrue(all(ink in INKS for row in frame for _,ink in row))
                            self.assertGreater(sum('⠁'<=ch<='⣿' for row in frame for run,_ in row for ch in run),8)
                self.assertEqual(len(final),9)
