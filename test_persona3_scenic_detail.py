"""Static story plates stay native and distinct in the live art bands."""
import unittest

from persona3_club_art import render as club
from persona3_hotel_art import render as hotel_still
from persona3_operation_art import hotel
from persona3_summit import ascent_art, seal_art
from persona3_yabbashah import shore


class SceneDetailTests(unittest.TestCase):
    def test_still_plates_are_distinct_native_drawings_at_live_sizes(self):
        for width,height in ((60,6),(60,9),(91,8),(91,12)):
            frames=[club(width,height), hotel_still('reunite',1.,width,height),
                    hotel_still('exit',1.,width,height),
                    *(hotel(width,height,i,3,0) for i in (0,1)),
                    *(shore(i,width,height) for i in range(3)),
                    *(ascent_art(i,width,height) for i in range(2)),
                    *(seal_art(i,width,height) for i in range(3)),
                    seal_art(0,width,height,True)]
            self.assertEqual(len(set(frames)),len(frames))
            for frame in frames:
                self.assertEqual(len(frame),height)
                for row in frame:
                    self.assertEqual(sum(len(run) for run,_ in row),width)
                dots=tuple(ch for row in frame for run,_ in row for ch in run if ch!=' ')
                self.assertTrue(all(0x2801<=ord(ch)<=0x28ff for ch in dots))
                self.assertGreater(len(dots),width*height//4)
