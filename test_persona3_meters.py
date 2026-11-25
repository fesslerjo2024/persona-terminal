"""Timed presentation checks without sleeping or writing a campaign save."""
from unittest import TestCase
from unittest.mock import patch

from persona3_combat import RED, P3Battle, SCENE_INKS
from persona3_meters import MeterTrails


class Surface:
    def __init__(self,w=65,h=25):
        self.w,self.h=w,h
        self.paints=[]

    def put(self,y,x,text,color,*_):
        assert x>=0 and x+len(text)<self.w and 0<=y<self.h
        self.paints.append((y,x,text,color))

    def text(self):
        return '\n'.join(t for _,_,t,_ in self.paints)


class AnimatedMeters(TestCase):
    def test_meter_holds_drains_monotonically_and_settles(self):
        m=MeterTrails()
        m.record('enemy',100,43,10.)
        frames=[m.segments('enemy',43,100,10,t)
                for t in (10.,10.10,10.23,10.31,10.39,10.47,10.54)]
        self.assertEqual(frames[:2],[(4,6,0)]*2)
        self.assertEqual(frames[-1],(4,0,6))
        self.assertEqual([f[1] for f in frames],sorted((f[1] for f in frames),reverse=True))
        self.assertGreater(len(set(f[1] for f in frames)),3)
        self.assertTrue(all(sum(f)==10 for f in frames))

    def test_overlapping_losses_and_recovery_are_consistent(self):
        m=MeterTrails()
        m.record('u',100,65,1.)
        self.assertEqual(m.segments('u',65,100,10,1.05),(6,4,0))
        m.record('u',65,20,1.06)
        self.assertEqual(m.segments('u',20,100,10,1.07),(2,8,0))
        m.record('u',20,50,1.08)
        self.assertEqual(m.segments('u',50,100,10,1.09),(5,0,5))
        m.record('u',50,48,1.1)
        self.assertEqual(m.segments('u',48,100,4,1.12),(1,1,2))
        self.assertEqual(m.segments('u',48,100,4,1.63),(2,0,2))

    def test_curses_tracks_own_exact_numeric_change_and_input_continues(self):
        for w,h in ((65,25),(96,34)):
            with self.subTest(w=w):
                b=P3Battle('priestess',seed=2)
                lead=b.allies[0]
                with patch('persona3_combat.monotonic',return_value=20.):
                    for k in '111':b.key(k)
                    s=Surface(w,h);b.draw(s)
                    self.assertEqual((lead.sp,b.enemies[0].hp,b.clock),(50,338,29))
                    self.assertIn('HP 338/382',s.text())
                    self.assertIn('SP 50',s.text())
                    self.assertTrue(any(y==9 and color==SCENE_INKS['navy'] and '▄' in t
                                        for y,_,t,color in s.paints))
                    self.assertTrue(any(y==9 and color==RED and '▄' in t
                                        for y,_,t,color in s.paints))
                    b.key('3')  # An immediate guard while the bars still animate.
                    self.assertEqual(b.clock,28)
                    self.assertIs(b.actor,b.allies[2])
                with patch('persona3_combat.monotonic',return_value=20.7):
                    s=Surface(w,h);b.draw(s)
                    self.assertFalse(any(color in (RED,SCENE_INKS['navy']) and '▄' in t
                                         for _,_,t,color in s.paints))

    def test_final_blow_shows_zero_and_does_not_delay_continue(self):
        b=P3Battle('priestess',seed=2)
        b.enemies[0].hp=8
        with patch('persona3_combat.monotonic',return_value=10.):
            for k in '21':b.key(k)
            self.assertEqual(b.outcome,'win')
            s=Surface();b.draw(s)
            self.assertIn('HP 0/382',s.text())
            self.assertIn('Priestess KO',s.text())
            self.assertIn('VICTORY',s.text())
            self.assertFalse(b.key('\n'))
        with patch('persona3_combat.monotonic',return_value=10.55):
            settle=Surface();b.draw(settle)
            self.assertIn('▂'*17,settle.text())
            self.assertIn('Priestess KO',settle.text())
        with patch('persona3_combat.monotonic',return_value=10.7):
            result=Surface();b.draw(result)
            self.assertIn('VICTORY',result.text())
            self.assertNotIn('Priestess KO',result.text())
