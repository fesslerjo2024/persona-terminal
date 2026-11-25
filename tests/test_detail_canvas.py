"""Microgrid fixtures exercise real height, clipping, and Unicode cell width."""
from unittest import TestCase
from persona_terminal.shared.detail_canvas import DotCanvas
from persona_terminal.persona3.persona3_title_detail import render


class DotCanvasTests(TestCase):
    def test_each_pixel_lands_on_the_correct_braille_bit(self):
        for x,column in enumerate(((1,2,4,64),(8,16,32,128))):
            for y,bit in enumerate(column):
                dots=DotCanvas(1,1)
                dots.put(x,y,'teal')
                self.assertEqual(dots.finish(),(((chr(0x2800+bit),'teal'),),))

    def test_palette_and_negative_art_are_clipped_without_extra_columns(self):
        dots=DotCanvas(2,1)
        dots.face(((-4,-1),(4,-1),(4,6),(-4,6)),'red')
        dots.face(((-1,-1),(2,-1),(2,5),(-1,5)),None)
        art=''.join(v for v,_ in dots.finish()[0])
        self.assertEqual(len(art),2)
        # Clip the raster in pixel space; keep empty cells ordinary spaces.
        self.assertIn(' ',art)
        self.assertTrue(any('⠁'<=ch<='⣿' for ch in art))

    def test_title_has_distinct_night_midnight_and_dark_hour_frames(self):
        for w,h in ((64,25),(95,34),(145,45)):
            frames=[render(t,w,h) for t in (.06,.95,2.65)]
            self.assertEqual(len(set(frames)),3)
            for rows in frames:
                self.assertEqual(len(rows),h)
                self.assertTrue(all(sum(map(len,(run for run,_ in row)))==w for row in rows))
                self.assertGreater(sum('⠁'<=ch<='⣿' for row in rows for run,_ in row for ch in run),w)
            self.assertFalse(any(ink=='forest' for row in frames[0] for _,ink in row))
            self.assertTrue(any(ink=='forest' for row in frames[-1] for _,ink in row))
