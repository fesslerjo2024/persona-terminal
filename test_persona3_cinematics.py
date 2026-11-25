"""Pure Persona 3 cut-in regression coverage. No UI, saves, or time loops."""
from functools import partial
import re
import unittest

from persona3_cinematics import (FUSION_SECONDS, THEURGY_SECONDS, VELVET_SECONDS,
                                 render_fusion, render_theurgy, render_velvet)
from reel_palette import IDS


from persona3_combat import THEURGIES

MOVES=tuple(spec[0] for spec in THEURGIES.values())+('Oracle',)


class Persona3CinematicsTests(unittest.TestCase):
    def test_primary_moves_have_distinct_native_art_and_legible_palette(self):
        allowed={'dim','red','gold','cyan','white','green',*IDS}
        for w,h in ((65,25),(96,34)):
            with self.subTest(w=w,h=h):
                starts=set()
                impacts=set()
                for name in MOVES:
                    fn=partial(render_theurgy,name)
                    starts.add(fn(.34,w,h))
                    impacts.add(fn(1.18,w,h))
                self.assertEqual(len(starts),len(MOVES))
                self.assertEqual(len(impacts),len(MOVES))
                cuts=[(partial(render_theurgy,m),THEURGY_SECONDS) for m in MOVES]
                cuts += [(render_velvet,VELVET_SECONDS),(render_fusion,FUSION_SECONDS)]
                for show,duration in cuts:
                    all_frames=set()
                    for i in range(21):
                        art=show(duration*i/20,w,h)
                        self.assertEqual(len(art),h)
                        for row in art:
                            self.assertEqual(sum(len(run) for run,_ in row),w)
                            self.assertTrue(all(all(ch==' ' or 0x2801<=ord(ch)<=0x28ff for ch in run)
                                                and ink in allowed for run,ink in row))
                        self.assertGreater(sum(0x2801<=ord(ch)<=0x28ff for row in art for run,_ in row for ch in run),w*h//8)
                        all_frames.add(art)
                    self.assertGreater(len(all_frames),14)

    def test_reduced_motion_freezes_all_stages_without_blank_art(self):
        cuts=[partial(render_theurgy,m) for m in MOVES]+[render_velvet,render_fusion]
        for show in cuts:
            at_start=show(0,65,25,low_motion=True)
            self.assertEqual(at_start,show(2,65,25,low_motion=True))
            self.assertGreater(sum(bool(run.strip()) for row in at_start for run,_ in row),15)


class VelvetDescentTests(unittest.TestCase):
    def test_ripple_widens_and_rises_before_room_reveals(self):
        def crest(frame):
            points=[]
            for y,row in enumerate(frame):
                x=0
                for run,ink in row:
                    if ink=='cyan':
                        points.extend((i,y) for i,ch in enumerate(run,x) if 0x2801<=ord(ch)<=0x28ff)
                    x+=len(run)
            return max(x for x,_ in points)-min(x for x,_ in points),min(y for _,y in points)
        for w,h in ((65,25),(96,34)):
            with self.subTest(w=w,h=h):
                early=render_velvet(.10,w,h)
                later=render_velvet(.32,w,h)
                w0,y0=crest(early)
                w1,y1=crest(later)
                self.assertGreater(w1,w0)
                self.assertLess(y1,y0)
                room=render_velvet(VELVET_SECONDS,w,h)
                self.assertEqual(room,render_velvet(0,w,h,low_motion=True))
                self.assertIn('gold',{ink for row in room for run,ink in row if run.strip()})

    def test_two_parent_cards_approach_but_never_become_result(self):
        from persona3_cinematics import FUSION_REVIEW_SECONDS,render_fusion_review
        def columns(frame):
            colors={}
            x=0
            for run,ink in frame[0]:
                if ink in ('cyan','rose') and run.strip():
                    colors.setdefault(ink,x)
                x+=len(run)
            return tuple(colors.get(k,-1) for k in ('cyan','rose'))
        for w in (59,90):
            with self.subTest(w=w):
                positions=[columns(render_fusion_review(t,w)) for t in (0,.29,FUSION_REVIEW_SECONDS,2)]
                self.assertTrue(all(0<cols[0]<cols[1]<w for cols in positions))
                self.assertTrue(positions[0][0]<positions[1][0]<positions[2][0])
                self.assertTrue(positions[0][1]>positions[1][1]>positions[2][1])
                self.assertEqual(positions[2],positions[3])
                self.assertEqual(columns(render_fusion_review(0,w,low_motion=True)),positions[2])
