"""Verify the revisit route alongside normal story progress and save ownership."""
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase

from battle_ui import ESC
from persona3_app import P3App
from persona3_state import END, MOON, P3Store


class ThebelRevisitTests(TestCase):
    def setUp(self):
        td=TemporaryDirectory();self.addCleanup(td.cleanup)
        self.path=Path(td.name)/'p3.json'
        self.store=P3Store(self.path);self.store.new_game()
        self.store.commit(phase='calendar',day=date(2009,4,24),activity='lounge',depth=5,
                          masks=('Orpheus','Angel'),yen=200)
        self.app=P3App(None,self.store,seed=8)

    def depart(self):
        app=self.app
        app.deploy()
        app.key('\n')
        self.assertEqual(app.page,'entrance')
        return app

    def test_top_returns_to_entrance_and_reopens_older_checkpoints_without_writes(self):
        before=self.path.read_bytes()
        app=self.depart()
        self.assertEqual([label for _,label in app.entrance_targets()],
                         ['22F / Sealed Border','02F / Revisit','05F / Revisit','08F / Revisit',
                          '11F / Revisit','17F / Revisit'])
        app.key('\n')
        self.assertEqual(app.page,'border')
        app.key('\n')
        self.assertEqual(app.page,'entrance')
        app.key('3')
        hall=app.hall
        self.assertEqual(hall.floor.number,5)
        self.assertEqual(hall.encounter,'thebel-patrol')
        self.assertTrue(hall.stairs_open)
        self.assertEqual(self.path.read_bytes(),before)
        hall.pos=hall.floor.stairs
        app.key('\n')
        self.assertEqual(app.hall.floor.number,8)
        self.assertEqual(app.record.depth,5)

    def test_same_night_resume_keeps_exact_position_patrol_and_resources(self):
        app=self.depart()
        app.key('6')
        self.assertEqual(app.hall.encounter,'thebel-ascent')
        app.hall.step('up')
        hall=app.hall
        app.resources['Protagonist']=(53,14)
        app.inventory['Medicine']=0
        before=self.path.read_bytes()
        app.key('t')
        self.assertEqual(app.entrance_targets()[0],('resume','Resume 17F'))
        app.key('\n')
        self.assertIs(app.hall,hall)
        self.assertEqual(app.hall.steps,1)
        self.assertEqual(app.resources['Protagonist'],(53,14))
        self.assertEqual(app.inventory['Medicine'],0)
        self.assertEqual(self.path.read_bytes(),before)
        today=app.record.day
        app.key('x');app.key(ESC)
        self.assertEqual(app.record.day,today)
        app.key('x');app.key('\n')
        self.assertEqual(app.record.day,today+timedelta(days=1))
        self.assertEqual(app.record.depth,5)
        self.depart()
        app.key('6')
        self.assertIsNot(app.hall,hall)
        self.assertFalse(app.hall.defeated)

    def test_replay_victory_has_no_first_clear_bonus_but_can_award_replay_coins(self):
        app=self.depart();app.key('3')
        before=self.path.read_bytes()
        app.sp_bonus=False
        app.battle=SimpleNamespace(resources=app.resources,inventory=app.inventory)
        app._finish_hall_battle()
        self.assertEqual(app.page,'shuffle')
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual(app.shuffle_yen(),30)
        app.key('1')  # Already owns Angel.
        self.assertEqual(app.page,'shuffle')
        self.assertEqual(self.path.read_bytes(),before)
        app.key('2')
        self.assertEqual(app.record.yen,230)
        self.assertEqual(app.record.depth,5)
        self.assertEqual(app.record.masks,('Orpheus','Angel'))

    def test_only_accessed_floors_plus_one_frontier_are_available(self):
        self.store.commit(depth=1)
        app=self.depart()
        self.assertEqual([entry[0] for entry in app.entrance_targets()],[1,0])
        app.key('5')
        self.assertEqual(app.page,'entrance')
        app.key('\n')
        self.assertEqual(app.hall.encounter,'venus-eagles')
        app.battle=SimpleNamespace(resources=app.resources,inventory=app.inventory)
        app._finish_hall_battle()
        self.assertEqual(app.record.depth,2)
        self.assertEqual(app.record.yen,225)
        self.assertEqual(app.shuffle_yen(),90)

    def test_poststory_and_preboard_practice_leave_exact_save_and_unlock_only_temporarily(self):
        for phase,day,back in (('complete',END,'story'),('monorail',MOON,'operation')):
            with self.subTest(phase=phase):
                self.store.commit(phase=phase,day=day,activity='',depth=1)
                app=P3App(None,self.store,seed=5)
                before=self.path.read_bytes()
                app.key('t');app.key('\n')
                self.assertTrue(app.free_expedition)
                app.key('\n')
                self.assertEqual(app.hall.floor.number,5)
                app.resources['Protagonist']=(25,18)
                app.key('m')
                self.assertEqual(app.field_kits,0)
                app.battle=SimpleNamespace(resources=app.resources,inventory=app.inventory)
                app._finish_hall_battle()
                self.assertEqual((app.field_depth,app.record.depth,app.page),(2,1,'hall'))
                app.key('t');app.key('x');app.key('\n')
                self.assertEqual(app.page,back)
                self.assertEqual(self.path.read_bytes(),before)

    def test_compact_entrance_can_show_top_and_resume_in_one_screen(self):
        app=self.depart();app.key('6');app.key('t')
        app.w,app.h=65,25
        paint=[]
        app.put=lambda y,x,text,*_:paint.append((y,x,str(text)))
        app.draw()
        body=' '.join(t for _,_,t in paint)
        self.assertIn('22F / Sealed Border',body)
        self.assertIn('17F / Revisit',body)
        self.assertIn('Resume 17F',body)
        self.assertTrue(all(0<=y<24 and 0<=x<=x+len(t)<65 for y,x,t in paint))
