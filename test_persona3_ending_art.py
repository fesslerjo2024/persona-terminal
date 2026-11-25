"""Bounds, branch composition, and replay contracts for the ending reels."""
from unittest import TestCase
from unicodedata import east_asian_width

import persona3_ending_art as art
from reel_palette import IDS


def flat(rows):
    return tuple(''.join(run for run,_ in row) for row in rows)


class EndingArtTests(TestCase):
    def test_full_and_compact_playback_are_clipped_colored_and_reproducible(self):
        inks=set(IDS)|{'dim','white','gold','cyan','green','red'}
        for scene,duration in art.DURATIONS.items():
            for w,h in ((60,7),(65,25),(96,34),(120,40)):
                with self.subTest(scene=scene,w=w,h=h):
                    times=(0,.15,.36,.58,.72,.86,.96,1)
                    frames=[art.render(scene,q*duration,w,h) for q in times]
                    self.assertGreaterEqual(len(set(frames)),4)
                    self.assertEqual(frames[3],art.render(scene,times[3]*duration,w,h))
                    for rows in frames:
                        self.assertEqual(len(rows),h)
                        for row in rows:
                            self.assertEqual(sum(len(run) for run,_ in row),w)
                            for run,ink in row:
                                self.assertIn(ink,inks)
                                self.assertTrue(all(east_asian_width(ch) not in ('W','F') for ch in run))

    def test_paths_and_aftermath_look_different_without_captions(self):
        for w,h in ((60,8),(65,25),(120,40)):
            frames={scene:'\n'.join(flat(art.render(scene,time*.70,w,h)))
                    for scene,time in art.DURATIONS.items()}
            self.assertEqual(len(set(frames.values())),len(art.DURATIONS))
            # Rebuilt graduation, classroom and rooftop compositions are
            # real dot illustrations, not the older ASCII landmark glyphs.
            for scene,frame in frames.items():
                self.assertGreater(sum(0x2801<=ord(ch)<=0x28ff for ch in frame),w*h//9,scene)
            palettes={scene:{ink for row in art.render(scene,art.DURATIONS[scene]*.70,w,h)
                             for run,ink in row if run.strip()} for scene in frames}
            self.assertIn('wine',palettes['bad'])
            self.assertIn('forest',palettes['bridge'])
            self.assertIn('gold',palettes['roof'])
            self.assertIn('rose',palettes['reunion'])
            for scene,frame in frames.items():
                self.assertNotRegex(frame,r'(?i)makoto|aigis|graduation|continue|press enter|credits')

    def test_fades_go_dark_without_blank_graduation_holds(self):
        for scene in ('karaoke','credits','stars'):
            d=art.DURATIONS[scene]
            before='\n'.join(flat(art.render(scene,d*.76,65,25)))
            after='\n'.join(flat(art.render(scene,d*.96,65,25)))
            self.assertGreater(len(before.replace(' ','')),len(after.replace(' ','')))
            self.assertFalse(''.join(flat(art.render(scene,d,65,25))).strip())
        for scene in ('bad','roof','bridge','reunion'):
            self.assertTrue(''.join(flat(art.render(scene,art.DURATIONS[scene],65,25))).strip())

    def test_tiny_viewport_clears_without_wrapping_into_controls(self):
        rows=art.render('roof',1,14,2)
        self.assertEqual(flat(rows),(' '*14,)*2)
        self.assertEqual(art.render('roof',0,0,0),())
        with self.assertRaises(ValueError):
            art.render('tutorial',0,65,25)
