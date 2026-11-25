"""Compact/wide Tartarus lift map checks against the real entrance controls."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import curses as C

from persona3_app import P3App, BLOCKS
from persona3_state import P3Store
from persona3_elevator_ui import silhouette


def glyphs(rows):
    return tuple(''.join(run for run, _ in row) for row in rows)


class LiftMapTests(TestCase):
    def app(self, day, **progress):
        work=TemporaryDirectory();self.addCleanup(work.cleanup)
        self.path=Path(work.name)/'qa.json'
        store=P3Store(self.path)
        store.new_game()
        store.commit(phase='calendar',day=day,theurgy_intro_seen=True,**progress)
        app=P3App(None,store,seed=31)
        if app.page=='late-interlude':app.key('\n')
        app.key('4');app.key('1')
        if app.page=='roster':app.key('s')
        app.key(' ')
        self.assertEqual(app.page,'entrance')
        return app

    def draw(self, app, w=65, h=25):
        app.w,app.h=w,h
        writes=[]
        app.put=lambda y,x,txt,*args:writes.append((y,x,str(txt)))
        app.draw()
        for y,x,txt in writes:
            if txt.strip():
                self.assertTrue(0<=y<h,(y,txt))
                self.assertTrue(0<=x and x+len(txt)<=w-1,(x,txt))
        return '\n'.join(txt for _,_,txt in writes)

    def test_all_themes_distinct_and_actual_lift_marker_moves(self):
        for w,h in ((30,7),(47,13),(68,13)):
            designs=set()
            for block in BLOCKS:
                with self.subTest(block=block,w=w,h=h):
                    a,b=BLOCKS[block][0][0].number,BLOCKS[block][1]
                    low=glyphs(silhouette(block,w,h,floor=a,low=a,high=b))
                    high=glyphs(silhouette(block,w,h,floor=b,low=a,high=b))
                    self.assertEqual(len(low),h)
                    self.assertTrue(all(len(row)==w and all(
                        ch.isascii() or 0x2801<=ord(ch)<=0x28ff for ch in row)
                        for row in low+high))
                    masks={ch for row in low for ch in row if 0x2801<=ord(ch)<0x28ff}
                    self.assertGreater(len(masks),20)
                    self.assertIn(f'{a:02d}F',low[-2])
                    self.assertIn(f'{b:02d}F',high[1])
                    self.assertNotEqual(low,high)
                    designs.add(glyphs(silhouette(block,w,h)))
            self.assertEqual(len(designs),len(BLOCKS),w)

    def test_real_arrows_previews_and_selection_do_not_write(self):
        app=self.app(date(2009,12,10),harabah_upper=1)
        before=self.path.read_bytes()
        self.assertEqual(app.block,'harabah_upper')
        self.assertIn('Gatekeeper: Icebreaker Lion',self.draw(app))
        self.assertIn('203F Icebreaker Lion Gate',self.draw(app,96,34))
        app.key(C.KEY_DOWN)
        self.assertIn('○ 199F',self.draw(app))
        self.assertIn('Fresh patrols.',self.draw(app))
        app.key(C.KEY_LEFT)
        self.assertEqual((app.block,app.i),('harabah',0))
        self.assertIn('HARABAH',self.draw(app))
        app.key(C.KEY_RIGHT)
        self.assertEqual((app.block,app.i),('harabah_upper',1))
        app.key('\n')
        self.assertEqual(app.page,'teleport')
        app.key(' ')
        self.assertEqual((app.page,app.hall.floor.number),('hall',203))
        app.key('t')
        self.assertIn('Resume 203F',self.draw(app))
        app.key(C.KEY_LEFT)
        self.assertIn('Resume in Upper Harabah.',self.draw(app))
        app.key('\n');app.key(' ')
        self.assertEqual((app.page,app.block,app.hall.floor.number),('hall','harabah_upper',203))
        self.assertEqual(self.path.read_bytes(),before)

    def test_full_adamah_compact_keeps_every_checkpoint_and_actions(self):
        app=self.app(date(2010,1,1),adamah=len(BLOCKS['adamah'][0]))
        before=self.path.read_bytes()
        v=self.draw(app)
        self.assertIn('256F / Sealed Border',v)
        self.assertIn('255F Genocidal Merc',v)
        self.assertIn('255F Genocidal Mercenary Gate',self.draw(app,96,34))
        self.draw(app)
        self.assertIn('Summit opens January 31.',v)
        self.assertIn('10/10',v)
        self.assertIn('TAB',v)
        stops=app.entrance_targets()
        floors=[int(label.split('F')[0]) for _,label in stops]
        self.assertEqual(floors,sorted(floors))
        app.key(C.KEY_HOME)
        app.key('\t')
        self.assertEqual(stops[app.i][0],'border')
        self.assertIn('FRAGMENTS',v)
        self.assertIn('C CLOCK',v)
        self.assertIn('V VELVET',v)
        app.key(C.KEY_UP)
        actual=' '.join(self.draw(app).split())
        self.assertIn('Genocidal Mercenary defeated. Patrols only.',actual)
        self.assertIn('255F]',actual)
        app.key('c')
        self.assertEqual(app.overlay,'clock')
        app.key('\x1b')
        app.key('\n');app.key(' ')
        self.assertEqual((app.page,app.hall.floor.number,app.hall.replay),('hall',255,True))
        self.assertEqual(self.path.read_bytes(),before)

    def test_landmark_names_stay_on_rows_and_regular_stops_use_only_number(self):
        app=self.app(date(2009,8,9),yabba=6,yabba_upper=6)
        initial=self.path.read_bytes()
        for w,h in ((65,25),(96,34)):
            rows=self.draw(app,w,h).splitlines()
            self.assertTrue(any(row.strip().endswith('117F Monad Landing') for row in rows))
            self.assertTrue(any(row.strip().endswith('103F') for row in rows))
            self.assertFalse(any('103F ' in row.strip() for row in rows))
        app.key('6');app.key(' ')
        self.assertEqual((app.hall.floor.number,app.hall.replay),(117,True))
        self.assertEqual(self.path.read_bytes(),initial)
