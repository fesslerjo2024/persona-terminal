"""Persona 3 temporary modifiers count completed recipient turns only."""
import curses as C
from unittest import TestCase

from persona3_combat import LEAD_ID, P3Battle, STAT_TURNS, stat_text
from test_persona3_arqa_combat import Surface


class ModifierTimerTests(TestCase):
    @staticmethod
    def setup(encounter='venus-eagles',**kwargs):
        return P3Battle(encounter,seed=4,level=30,party=(LEAD_ID,'Yukari','Akihiko'),**kwargs)

    def cast(self,b,name,target=None):
        self.assertIsNone(b.act('skill:'+name,target))

    def guard(self,b):
        self.assertIsNone(b.act('guard'))

    def until(self,b,u):
        for _ in range(12):
            if b.actor is u:return
            self.guard(b)
        self.fail(f'{u.label} did not take a turn.')

    def test_self_cast_has_three_subsequent_normal_turns_including_guard(self):
        b=self.setup()
        ally=b.allies[-1]
        self.until(b,ally)
        self.cast(b,'Tarukaja',ally)
        self.assertEqual((ally.attack,stat_text(ally)),(1,'ATK↑3'))
        for turns in (3,2,1):
            self.until(b,ally)
            self.assertEqual(stat_text(ally),f'ATK↑{turns}')
            self.guard(b)
        self.assertEqual((ally.attack,stat_text(ally)),(0,''))
        self.assertTrue(any('Akihiko: ATK modifier expires.'==x for x in b.log))

    def test_enemy_recast_refreshes_only_that_stat_and_enemy_extra_not_counted(self):
        b=self.setup('hermit',persona='Orpheus',stock={'Orpheus':('Rakunda',)})
        foe=b.enemies[0]
        self.cast(b,'Tarunda',foe)
        self.assertEqual(stat_text(foe),'ATK↓3')
        self.until(b,b.allies[0])
        self.assertIn('Hermit earns One More!',b.log)
        self.assertEqual(stat_text(foe),'ATK↓2')
        self.cast(b,'Rakunda',foe)
        self.assertEqual(stat_text(foe),'ATK↓2 DEF↓3')
        self.until(b,b.allies[0])
        self.cast(b,'Tarunda',foe)
        self.assertEqual(stat_text(foe),'ATK↓3 DEF↓2')
        self.until(b,b.allies[0])
        self.assertEqual(stat_text(foe),'ATK↓2 DEF↓1')
        self.guard(b)
        self.until(b,b.allies[0])
        self.assertEqual((foe.attack,foe.defense,stat_text(foe)),(-1,0,'ATK↓1'))

    def test_fresh_down_and_shift_share_a_slot_and_analyze_is_free(self):
        b=self.setup(stock={'Orpheus':('Rakukaja',)})
        lead,yukari,aki=b.allies
        self.cast(b,'Rakukaja',lead)
        self.until(b,lead)
        b.modify_stat(yukari,'agility',1)
        target=b.enemies[0]
        self.assertIsNone(b.act('analyze',target))
        self.assertEqual(stat_text(lead),'DEF↑3')
        self.cast(b,'Agi',target)
        self.assertTrue(b.one_more)
        self.assertEqual(stat_text(lead),'DEF↑3')
        self.assertIsNone(b.act('shift',yukari))
        self.guard(b)
        self.assertIs(b.actor,yukari)
        self.assertEqual(stat_text(lead),'DEF↑2')
        self.assertEqual(stat_text(yukari),'AGI↑3')
        self.guard(b)
        self.assertIs(b.actor,aki)
        self.assertEqual(stat_text(yukari),'AGI↑2')

    def test_free_oracle_crit_revolution_and_dormant_phase_effect(self):
        b=self.setup(fuuka=True,theurgy=True,charge={'Fuuka':100},stock={'Orpheus':('Revolution',)})
        lead=b.allies[0]; foe=b.enemies[0]
        # A named boss vulnerability must survive temporary stat overrides.
        foe.defense=-1
        b.modify_stat(foe,'defense',1)
        b.clear_stats(foe,sign=1)
        self.assertEqual((foe.defense,stat_text(foe)),(-1,''))
        self.assertIsNone(b.act('oracle'))
        self.assertIs(b.actor,lead)
        self.assertEqual(stat_text(lead),'DEF↑3')
        self.cast(b,'Revolution')
        self.assertEqual(stat_text(lead),'DEF↑3 CRIT↑3')
        self.assertEqual(stat_text(foe),'CRIT↑3')
        self.until(b,lead)
        self.assertEqual(stat_text(foe),'CRIT↑2')
        self.assertEqual(stat_text(lead),'DEF↑3 CRIT↑3')

    def test_cluster_of_party_and_enemy_durations_fits_compact_screen(self):
        b=self.setup()
        self.cast(b,'Tarunda',b.enemies[0])
        b.modify_stat(b.allies[0],'defense',1)
        b.key('i')
        for w,h in ((65,25),(120,40)):
            app=Surface(w,h); b.draw(app)
            body=app.text()
            for marker in ('DEF↑3','ATK↓3','Own turns left',b.enemies[0].label):
                self.assertIn(marker,body)
        b.key('\x1b');b.key('7');b.key('1')
        app=Surface(65,25);b.draw(app)
        self.assertIn(f'ATK↓{STAT_TURNS}  •  own turns left',app.text())
