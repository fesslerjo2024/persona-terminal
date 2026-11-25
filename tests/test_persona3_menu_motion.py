"""Native P3 floor transfer and optional briefing/calendar cues."""
import re
import unittest

from persona_terminal.persona3.persona3_menu_motion import ELEVATOR_SECONDS, render, render_elevator, render_signal


def picture(frame):
    return '\n'.join(''.join(text for text,_ in row) for row in frame)


def colors(frame):
    return {ink for row in frame for text,ink in row if text.strip()}


class MenuMotionTests(unittest.TestCase):
    def test_transfer_shows_requested_floors_and_visibly_moves_between(self):
        for w,h in ((64,25),(95,34),(119,40)):
            for start,end,direction in ((1,43,'^'),(43,8,'v'),(100,264,'^')):
                with self.subTest(size=(w,h),route=(start,end)):
                    values=[i*ELEVATOR_SECONDS/48 for i in range(49)]
                    frames=[render_elevator(t,w,h,start,end) for t in values]
                    self.assertGreaterEqual(len(set(frames)),37)
                    self.assertIn(f'| {start:02d} {direction}|',picture(frames[0]))
                    self.assertIn(f'| {end:02d} -|',picture(frames[-1]))
                    self.assertIn('white',colors(render_elevator(.62,w,h,start,end)))
                    self.assertNotIn('white',colors(frames[-1]))
                    self.assertEqual(frames[-1],render_elevator(9,w,h,start,end))
                    for frame in frames:
                        self.assertEqual(len(frame),h)
                        self.assertTrue(all(sum(len(text) for text,_ in row)==w for row in frame))
                        self.assertGreater(sum(0x2801<=ord(ch)<=0x28ff for row in frame for run,_ in row for ch in run),w*h//8)
                        self.assertTrue(all(all(ch.isascii() or 0x2801<=ord(ch)<=0x28ff for ch in text)
                                            and not re.search('[A-Za-z]{2,}',text)
                                            for row in frame for text,_ in row))

    def test_quiet_cues_keep_detail_uncluttered_in_a_small_band(self):
        for w,h in ((59,5),(90,8)):
            moon=render('calendar',.7,w,h)
            signal=render_signal(.7,w,h)
            self.assertEqual(signal,render('briefing',.7,w,h))
            self.assertNotEqual(moon,signal)
            for frame in (moon,signal):
                self.assertEqual(len(frame),h)
                for row in frame:
                    self.assertEqual(sum(len(text) for text,_ in row),w)
                    if frame==signal:
                        self.assertEqual(''.join(text for text,_ in row)[:w//3].strip(),'')
            self.assertLessEqual(colors(moon),{'slate','navy'})
