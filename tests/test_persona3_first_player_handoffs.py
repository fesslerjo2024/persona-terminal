"""First survey, optional Theurgy, and dated calendar handoffs."""
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_arqa import BRIDGE
from persona_terminal.persona3 import persona3_late as late
from persona_terminal.persona3.persona3_state import P3Store, TUTORIAL
from persona_terminal.persona3 import persona3_upper as upper
from .test_persona3_arqa_combat import Surface


class FirstPlayerHandoffs(TestCase):
    def setUp(self):
        folder=TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path=Path(folder.name)/'p3.json'
        self.store=P3Store(self.path)
        self.store.new_game()

    def paint(self,app,w=65,h=25):
        out=Surface(w,h)
        app.w,app.h,app.put=w,h,out.put
        app.draw()
        return ' '.join(out.text().split())

    def test_pull_out_reoffers_first_survey_and_success_confirms_the_objective(self):
        self.store.commit(day=TUTORIAL,phase='tartarus',xp=35)
        app=P3App(None,self.store)
        for k in ('1','1',' '):app.key(k)
        self.assertEqual((app.page,app.hall.floor.number),('hall',2))
        app.key('x')
        self.assertIn('Survey unfinished. You can return to 02F next evening.',self.paint(app))
        app.key('\n')
        self.assertEqual((app.record.day,app.record.depth),(TUTORIAL+timedelta(days=1),0))
        self.assertIn('Survey unfinished.',self.paint(app))
        app=P3App(None,P3Store(self.path))
        for k in ('4','1',' '):app.key(k)
        self.assertEqual((app.page,app.hall.floor.number),('hall',2))
        self.assertIn('Reach the sealed stairs.',self.paint(app))
        self.assertIn('Clear the Shadow.',self.paint(app))
        app.hall.pos=app.hall.floor.stairs
        app.battle=SimpleNamespace(resources=app.resources,inventory=app.inventory)
        app._finish_hall_battle()
        app.key('1')
        self.assertEqual((app.page,app.record.depth),('calendar',1))
        self.assertIn('02F mapped. The first Tartarus survey is complete.',self.paint(app))

    def test_theurgy_wait_and_first_deploy_intro_dont_require_a_battle(self):
        self.store.commit(day=BRIDGE-timedelta(days=1),phase='calendar')
        app=P3App(None,self.store)
        for k in ('4','4','\n','4','1'):app.key(k)
        for size in ((65,25),(100,35)):
            panel=self.paint(app,*size)
            for item in ('using their specialties','At 100%','Continue to squad','Try the drill'):
                self.assertIn(item,panel)
        before=self.path.read_bytes()
        app.key(ESC)
        self.assertEqual(self.path.read_bytes(),before)
        app.key('1');app.key('\n')
        self.assertEqual((app.page,app.record.day),('roster',BRIDGE))
        self.assertIsNone(app.battle)
        self.assertTrue(app.record.theurgy_intro_seen)
        self.assertFalse(app.record.theurgy_drill_seen)
        app=P3App(None,P3Store(self.path))
        app.key('4');app.key('1')
        self.assertEqual(app.page,'roster')
        app.key(ESC);app.key('5');app.key('2')
        self.assertEqual(app.encounter,'theurgy-drill')

    def test_wait_stops_twice_for_reports_and_warns_only_when_cases_expire(self):
        first,second=sorted(upper.REPORT_DAYS)
        self.store.commit(day=first-timedelta(days=1),phase='calendar')
        app=P3App(None,self.store)
        for day,names in ((first,('Ayako',)),(second,('Ayako','Kenjiro','Yoshimi'))):
            app.key('4');app.key('4')
            self.assertIn('Elizabeth will have new cases',self.paint(app))
            self.assertNotIn('will expire',self.paint(app))
            app.key('\n')
            self.assertEqual(app.record.day,day)
            self.assertIn('Elizabeth filed a missing-person report.',self.paint(app))
            app.key('r')
            for name in names:self.assertIn(name,self.paint(app))
            app.key(ESC)
        app.key('4');app.key('4')
        self.assertIn('Any remaining missing-person cases will expire.',self.paint(app))
        app.key('\n')
        self.assertEqual((app.page,app.record.day),('hotel',upper.HOTEL_DAY))

    def test_ryoji_callback_is_a_wait_stop_without_revealing_the_bridge(self):
        self.store.commit(day=late.RYOJI_RETURN_WALK-timedelta(days=1),phase='calendar')
        app=P3App(None,self.store)
        for k in ('4','4','\n'):app.key(k)
        self.assertEqual(app.record.day,late.RYOJI_RETURN_WALK)
        self.assertIn('Ryoji waits by the school gate.',self.paint(app))
        self.assertNotIn('Appriser',self.paint(app))
        app.key('\n')
        self.assertEqual(app.next_operation,late.BRIDGE)
