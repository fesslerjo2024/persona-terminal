"""All-Out uses the same native scenes from combat and the gallery."""
import curses
import unittest
from unittest.mock import patch

from persona3_allout import FINISHERS, FINISH_SECONDS, IMPACT_SECONDS
from persona3_combat import LEAD_ID, PARTY, P3Battle
from persona3_extras import Persona3Extras
from test_persona3_arqa_combat import Surface


class AllOutPlaybackTests(unittest.TestCase):
    @staticmethod
    def ready(hp, low_motion=False):
        b=P3Battle('venus-eagles',seed=4,low_motion=low_motion)
        b.actor=b.allies[2]
        b.one_more=True
        for u in b.enemies:
            u.hp=hp
            u.down=True
        return b

    def test_winning_all_out_plays_initiator_and_holds_continuation(self):
        for size in ((65,25),(96,35)):
            b=self.ready(30)
            with patch('persona3_combat.monotonic',return_value=200):
                self.assertTrue(b.key('6'))
            self.assertEqual(b.outcome,'win')
            self.assertEqual(b.reel,('Junpei',200,200+FINISH_SECONDS))
            self.assertIs(b._all_out_reel,True)
            view=Surface(*size)
            with patch('persona3_combat.monotonic',return_value=200+FINISH_SECONDS*.8):
                b.draw(view)
            self.assertNotIn('CONTINUE',view.text())
            with patch('persona3_combat.monotonic',return_value=200+FINISH_SECONDS*.81):
                self.assertTrue(b.key('\n'))
            self.assertIsNone(b.reel)
            self.assertTrue(b.meters.active(200+FINISH_SECONDS*.81))
            self.assertFalse(b.key('\n'))

    def test_survivors_use_impact_and_low_motion_stays_short(self):
        for low_motion in (False,True):
            b=self.ready(10000,low_motion)
            with patch('persona3_combat.monotonic',return_value=10):
                self.assertTrue(b.key('6'))
                self.assertFalse(b.outcome)
                self.assertIs(b._all_out_reel,False)
                self.assertAlmostEqual(b.reel[2]-10,min(.55,IMPACT_SECONDS) if low_motion else IMPACT_SECONDS)
                self.assertTrue(b.key(' '))
                self.assertIsNone(b.reel)

    def test_gallery_covers_playable_roster_and_shared_rush(self):
        gallery=Persona3Extras(None,'gallery')
        gallery.key(curses.KEY_LEFT)
        self.assertEqual(gallery.groups[gallery.group][0],'All-Out Attacks')
        roster=(set(PARTY)-{LEAD_ID})|{'Makoto'}
        self.assertEqual(set(FINISHERS),roster)
        self.assertEqual({item[0] for item in gallery.entries},roster|{'Squad Rush'})
