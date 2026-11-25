"""Packed subcell geometry and original time phases for P5's three story reels."""
from unittest import TestCase

import cinema
import intro_calling_card as card
import satanael_scene as shell
import velvet_entrance as velvet


class StoryReels(TestCase):
    def test_viewport_geometry_and_phase_changes(self):
        animations=(
            (card.render, (.55,1.68,2.52,3.74,5.0)),
            (velvet.render, (.16,1.01,1.55,2.53,2.85)),
            (lambda t,w,h:cinema.paint(shell.TITLE,t,w,h)[1], (.26,.90,1.71,1.96,2.51)),
        )
        for w,h in ((64,25),(95,35)):
            for render,times in animations:
                frames=[]
                for t in times:
                    r=render(t,w,h);frames.append(r)
                    self.assertEqual(len(r),h)
                    self.assertTrue(all(sum(len(s) for s,_ in line)==w for line in r))
                    dots=[ch for line in r for s,_ in line for ch in s if ch!=' ']
                    self.assertTrue(dots)
                    self.assertTrue(all(0x2801<=ord(ch)<=0x28ff for ch in dots))
                    self.assertGreater(len(set(dots)),35)
                    self.assertGreater(len({ink for line in r for s,ink in line if s.strip()}),2)
                self.assertEqual(len({frameset for frameset in map(repr,frames)}),len(times))
