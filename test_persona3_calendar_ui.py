"""The Dark Hour wall board uses dated content, not placeholder moons."""
from calendar import Calendar
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

import curses as C
from persona3_app import P3App
from persona3_calendar_ui import NIGHT_SWEEP_SECONDS, departure, departure_length
from persona3_state import P3Store
from persona3_upper import HOTEL_DAY


class CalendarUI(TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup)
        self.path=Path(t.name)/'p3.json'
        self.store=P3Store(self.path);self.store.new_game()

    def app(self,when,**changes):
        self.store.commit(day=when,phase='calendar',**changes)
        return P3App(None,self.store,seed=2)

    def paint(self,a,w,h):
        a.w,a.h=w,h
        lines=[]
        a.put=lambda y,x,t,*ink:lines.append((y,x,str(t),ink))
        before=self.path.read_bytes()
        a.draw()
        self.assertEqual(self.path.read_bytes(),before)
        for y,x,t,_ in lines:
            self.assertTrue(0<=y<h-1 and 0<=x<=x+len(t)<w,(y,x,t))
        return lines

    @staticmethod
    def day_cell(w,day):
        seam=32 if w<82 else min(40,w//2-3)
        left=2+(seam-32)//2
        weeks=Calendar().monthdayscalendar(day.year,day.month)
        for i,week in enumerate(weeks):
            if day.day in week:return 7+i,left+3+4*week.index(day.day)

    def test_june_map_displays_moon_case_training_and_regular_dates(self):
        a=self.app(date(2009,6,2))
        for w,h in ((65,25),(96,34),(120,40)):
            paint=self.paint(a,w,h)
            marks={(y,x):t for y,x,t,_ in paint}
            for d,m in ((8,'●'),(13,'◆'),(18,'!'),(26,'!'),(29,'·')):
                self.assertEqual(marks[self.day_cell(w,date(2009,6,d))],m)
            self.assertEqual(sum(y==h-2 for y,_,_,_ in paint),1)
        a.key(C.KEY_DOWN)
        self.assertEqual((a.page,a.i),('calendar',1))
        self.assertEqual(a.record.day,date(2009,6,2))

    def test_hotel_moon_ignores_expired_case_and_january_payoff_remains_hidden(self):
        a=self.app(date(2009,7,6),rescues=('ayako',))
        for date_,mark in ((date(2009,7,6),'!'),(HOTEL_DAY,'●')):
            self.assertIn((*self.day_cell(65,date_),mark),[(y,x,t) for y,x,t,_ in self.paint(a,65,25)])
        a=self.app(date(2010,1,2))
        y,x=self.day_cell(65,date(2010,1,21))
        self.assertIn((y,x,'·'),[(r,c,t) for r,c,t,_ in self.paint(a,65,25)])

    def test_quick_midnight_cue_is_only_triggered_on_departure(self):
        a=self.app(date(2009,4,22),depth=1)
        self.paint(a,65,25)
        a.key('4');a.key(C.KEY_DOWN);a.key(C.KEY_UP)
        self.assertEqual(a.page,'evening')
        a.key('1')
        self.assertEqual(a.page,'dark-hour')
        self.assertLess(NIGHT_SWEEP_SECONDS,departure_length(first=True))
        self.assertNotEqual(departure(.1,64,25),departure(.9,64,25))
        with patch('persona3_app.time.monotonic',return_value=a.started+NIGHT_SWEEP_SECONDS+.1):
            self.paint(a,65,25)
        self.assertEqual(a.page,'entrance')
