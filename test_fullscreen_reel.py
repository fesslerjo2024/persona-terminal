"""Regression tests for live terminal dimensions, not the legacy 57x15 cel."""
import re
import unittest

import cinema
import cutins
from animation_gallery import _effect_floor
from wide_canvas import Canvas


def rows_of_art(frame):
    return [''.join(run for run,_ in row) for row in frame]


class FullScreenTests(unittest.TestCase):
    def test_canvas_clipping_line_and_opaque_overlay(self):
        c=Canvas(5,3)
        c.put(-1,0,'<*->','cyan')
        c.line(0,2,4,2,'red')
        c.overlay(((('  ','face'),('o ','gold')),),2,2)
        self.assertEqual(rows_of_art(c.finish()),['*->  ','     ','--  o'])

    def test_each_scene_draws_native_cells_outside_old_frame(self):
        cards=(*cutins.SHOWTIMES.values(),*cutins.ALL_OUT.values(),
               cutins.ORACLE_SUPPORT,cutins.FINAL_GUARD,cutins.ORACLE)
        for w,h in ((64,25),(95,34),(119,40),(145,45)):
            for title,_ in cards:
                with self.subTest(clip=title,viewport=(w,h)):
                    duration=cutins.duration(title)
                    made=[]
                    for frac in (.02,.13,.36,.55,.72,.87):
                        _,runs=cinema.paint(title,duration*frac,w,h,finishing=False)
                        art=rows_of_art(runs)
                        self.assertEqual(len(art),h)
                        self.assertTrue(all(len(row)==w for row in art))
                        full='\n'.join(art)
                        self.assertTrue(full.isascii())
                        self.assertIsNone(re.search(r'[A-Za-z]{3,}',full),full)
                        made.append(art)
                    self.assertGreaterEqual(len({tuple(art) for art in made}),5)
                    xs=set();ys=set()
                    for art in made:
                        for y,row in enumerate(art):
                            if row.strip():ys.add(y)
                            xs.update(i for i,ch in enumerate(row) if ch!=' ')
                    self.assertLessEqual(min(xs),round(w*.10))
                    self.assertGreaterEqual(max(xs),round((w-1)*.90))
                    self.assertLessEqual(min(ys),round(h*.23))
                    self.assertGreaterEqual(max(ys),round((h-1)*.83))

    def test_hp_floor_uses_edges_and_has_motion(self):
        for w,h in ((64,25),(119,40)):
            a=rows_of_art(_effect_floor(w,h,.2))
            b=rows_of_art(_effect_floor(w,h,.6))
            self.assertNotEqual(a,b)
            self.assertTrue(a[-1].strip())
            self.assertLessEqual(next(i for i,row in enumerate(a) if row.strip()),h//4)
            self.assertTrue(any(row[0]!=' ' for row in a))
            self.assertTrue(any(row[-1]!=' ' for row in a))

    def test_showtime_paint_never_uses_the_old_cel_and_has_scene_color(self):
        from unittest.mock import patch
        for title,_ in cutins.SHOWTIMES.values():
            with self.subTest(title=title), patch('cinema.get',side_effect=AssertionError('legacy cel call')):
                used=set()
                for t in (.42,2.18,4.33,6.56):
                    _, rows=cinema.paint(title,t,95,34)
                    self.assertTrue(any(len(run.strip())>0 for row in rows for run,_ in row))
                    used.update(ink for row in rows for run,ink in row if run.strip())
                from reel_palette import IDS
                self.assertGreaterEqual(len(used & IDS.keys()),2,used)
