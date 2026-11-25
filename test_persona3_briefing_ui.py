"""Evening and squad UI: dates, conditional actions, and one-shot motion."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import curses as C

from persona3_app import P3App
from persona3_briefing_ui import ROSTER_SECONDS
from persona3_state import P3Store
from test_persona3_arqa_combat import Surface


class BriefingTests(TestCase):
    def open_evening(self,day,**state):
        folder=TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path=Path(folder.name)/'p3.json'
        self.store=P3Store(self.path)
        self.store.new_game()
        self.store.commit(phase='calendar',day=day,**state)
        app=P3App(None,self.store)
        if app.page in ('story','late-interlude'):app.key('\n')
        self.assertEqual(app.page,'calendar')
        app.key('4')
        self.assertEqual(app.page,'evening')
        return app

    def paint(self,app,w=65,h=25):
        out=Surface(w,h)
        app.w,app.h=w,h
        app.put=out.put
        app.draw()
        return out.text()

    def test_continue_at_evening_returns_to_briefing_without_writing(self):
        self.open_evening(date(2009,4,21))
        self.store.commit(activity='lounge',depth=1)
        before=self.path.read_bytes()
        app=P3App(None,self.store)
        self.assertEqual(app.page,'evening')
        view=self.paint(app,96,34)
        self.assertIn('S.E.E.S. BRIEFING',view)
        self.assertIn('TARTARUS',view)
        self.assertNotIn('●',view)
        self.assertEqual(self.path.read_bytes(),before)

    def test_full_moon_portrait_uses_subcell_detail(self):
        app=self.open_evening(date(2009,4,21))
        before=self.path.read_bytes()
        for w,h in ((65,25),(120,40)):
            view=self.paint(app,w,h)
            self.assertIn('NEXT FULL MOON',view)
            self.assertGreater(len({ch for ch in view if 0x2801<=ord(ch)<0x28ff}),10)
            self.assertNotIn(' ▓▓▒▓ ',view)
        self.assertEqual(self.path.read_bytes(),before)

    def test_unlock_is_not_mislabeled_as_full_moon_and_dates_fit(self):
        app=self.open_evening(date(2009,8,7))
        before=self.path.read_bytes()
        for w,h in ((65,25),(120,40)):
            view=self.paint(app,w,h)
            for part in ('S.E.E.S. BRIEFING','NEXT EVENT','08/08','UPPER YABBASHAH OPENS',
                         'NEXT FULL MOON  09/05','ESC CALENDAR'):
                self.assertIn(part,view)
            self.assertNotIn('R RESCUE BOARD',view)
            self.assertNotIn('08/08  /',view)
            self.assertEqual(view.count('DAY'),1)
            self.assertIn('LOWER YABBASHAH  0/6',view)
            self.assertIn('NEXT: 70F',view)
        app.key('4')
        self.assertEqual(app.overlay,'wait')
        app.key('\x1b')
        self.assertEqual(self.path.read_bytes(),before)

    def test_only_available_quest_gets_a_reminder_and_binding_still_works(self):
        app=self.open_evening(date(2009,11,8),junpei_flowers='bought')
        for w,h in ((65,25),(120,40)):
            view=self.paint(app,w,h)
            self.assertIn('FLOWERS  /  UNTIL 11/21',view)
            self.assertIn('6 Give Junpei the flowers',view)
        app.key('6')
        self.assertEqual(app.record.junpei_flowers,'given')
        self.assertNotIn('FLOWERS  /  UNTIL',self.paint(app))
        self.assertNotIn('Give Junpei the flowers',self.paint(app))

    def test_rescue_case_reminder_matches_available_key(self):
        app=self.open_evening(date(2009,6,25),upper=1)
        before=self.path.read_bytes()
        for w,h in ((65,25),(96,34)):
            body=self.paint(app,w,h).splitlines()
            for label in ('TARTARUS','UPPER ARQA  1/7','NEXT: 47F • GATEKEEPER','UNTIL 07/06'):
                self.assertTrue(any(line.find(label,w//2)>=0 for line in body),label)
        self.assertIn('R RESCUE BOARD',self.paint(app))
        app.key('r')
        self.assertEqual(app.page,'rescue-board')
        app.key('\x1b')
        self.assertEqual((app.page,self.path.read_bytes()),('evening',before))

    def test_closed_or_expired_deadlines_never_leave_stale_status_labels(self):
        app=self.open_evening(date(2010,1,2),adamah=11,junpei_flowers='bought')
        initial=self.path.read_bytes()
        for w,h in ((65,25),(96,34)):
            view=self.paint(app,w,h)
            self.assertIn('ADAMAH  11/11',view)
            self.assertIn('256F • SUMMIT 01/31',view)
            self.assertNotIn('UNTIL',view)
            self.assertNotIn('RESCUE BOARD',view)
            self.assertNotIn('Give Junpei the flowers',view)
        self.assertEqual(self.path.read_bytes(),initial)

    def test_squad_animates_once_per_entry_with_live_input(self):
        app=self.open_evening(date(2009,9,4),theurgy_intro_seen=True)
        before=self.path.read_bytes()
        with patch('persona3_app.time.monotonic',return_value=10):
            app.key('1')
            intro=self.paint(app)
        self.assertEqual(app.page,'roster')
        stamp=app._roster_started
        initial=app.roster_choices[1]
        selected=initial in app.roster_pick
        with patch('persona3_app.time.monotonic',return_value=10.05):
            app.key(C.KEY_DOWN);app.key('\n')
        self.assertNotEqual(initial in app.roster_pick,selected)
        self.assertEqual(app._roster_started,stamp)
        with patch('persona3_app.time.monotonic',return_value=10+ROSTER_SECONDS+.01):
            standard=self.paint(app)
            self.assertIn('S DEPLOY',self.paint(app,120,40))
        def lock_column(text):
            return next(line.index('● Makoto') for line in text.splitlines() if '● Makoto' in line)
        self.assertGreater(lock_column(intro),lock_column(standard))
        with patch('persona3_app.time.monotonic',return_value=20):
            app.key('\x1b')
            self.assertEqual(app.page,'evening')
            app.key('1')
            self.assertEqual(app._roster_started,20)
            self.assertEqual(lock_column(self.paint(app)),lock_column(intro))
        self.assertEqual(self.path.read_bytes(),before)

    def test_dorm_notice_is_one_authored_milestone_not_a_persistent_panel(self):
        events=((date(2009,5,23),'AKIHIKO',"I'm cleared to fight"),
                (date(2009,6,13),'FUUKA','The new gauges'),
                (date(2009,7,18),'FUUKA','A red door'),
                (date(2009,8,8),'MITSURU','Koromaru handles Dark'),
                (date(2009,8,28),'KEN','I can take a turn healing'))
        for day,author,line in events:
            with self.subTest(day=day):
                app=self.open_evening(day)
                before=self.path.read_bytes()
                for w,h in ((65,25),(96,34)):
                    out=self.paint(app,w,h)
                    self.assertEqual(out.count('DORM NOTICEBOARD'),1)
                    self.assertIn('DORM NOTICEBOARD / '+author,out)
                    self.assertIn(line,out)
                    self.assertNotIn('AKIHIKO IS BACK ON DUTY',out)
                    self.assertIn('TARTARUS',out)
                app.key('\x1b')
                self.assertEqual((app.page,self.path.read_bytes()),('calendar',before))
        # Adjacent quiet nights: don't leak roster or dungeon news early,
        # and don't let it become a standing banner after the milestone.
        for day in (date(2009,5,22),date(2009,5,24),date(2009,7,17),date(2009,7,19)):
            with self.subTest(day=day):
                self.assertNotIn('DORM NOTICEBOARD',self.paint(self.open_evening(day)))
