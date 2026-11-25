"""Regression tests for October/November's scripted Persona 3 fights."""
import curses as C
from unittest import TestCase

from persona_terminal.persona3.persona3_autumn_operations import BRIDGE, CHIDORI, FORTUNE, STREGA, FortuneCycle
from persona_terminal.persona3.persona3_combat import LEAD_ID, P3Battle


class AutumnOperationTests(TestCase):
    def battle(self,encounter,**kwargs):
        return P3Battle(encounter,seed=6,level=12,**kwargs)

    def test_fortune_can_spin_from_cover_but_neither_target_nor_aoa_hits_it(self):
        b=self.battle(FORTUNE)
        strength,fortune=b.enemies
        self.assertEqual(b.targetable_enemies,[strength])
        self.assertIn('valid target',b.act('attack',fortune))
        strength.down=True;b.one_more=True
        self.assertTrue(b.all_out)
        self.assertIsNone(b.act('allout'))
        self.assertEqual(fortune.hp,fortune.max_hp)
        self.assertLess(strength.hp,strength.max_hp)
        while b.round==1:self.assertIsNone(b.act('guard'))
        self.assertTrue(all(u.attack==1 for u in b.allies))
        self.assertIn('62 HP',b.threat)
        yup=b.allies[1];before=yup.hp;yup.guard=True
        self.assertFalse(b.late_cycle.turn(b,fortune,False))
        self.assertEqual(yup.hp,before-FortuneCycle.WHEEL_DAMAGE)

    def test_strega_grenade_marks_a_stable_target_and_guard_prevents_down(self):
        for guarded in (True,False):
            with self.subTest(guarded=guarded):
                b=self.battle(STREGA,party=(LEAD_ID,'Yukari','Akihiko'))
                scout=b.late_cycle
                while b.round==1:self.assertIsNone(b.act('guard'))
                target=scout.grenade_target
                self.assertIn(target.label,b.threat)
                self.assertTrue(target.alive)
                target.guard=guarded
                self.assertEqual(scout.turn(b,scout.jin,False),not guarded)
                self.assertEqual(target.down,not guarded)

    def test_airborne_hanged_man_ignores_area_theurgy_and_all_out(self):
        b=self.battle(BRIDGE,party=(LEAD_ID,'Yukari','Mitsuru'),fuuka=True,theurgy=True,
                      registered=('Jack Frost',"Jack O'Lantern"),charge={LEAD_ID:100})
        boss,*seals=b.enemies
        self.assertEqual(len(b.late_cycle.visible),4)
        self.assertNotIn(boss,b.targetable_enemies)
        for s in seals:s.hp=s.max_hp=145
        self.assertIsNone(b.act('theurgy:jacks'))
        self.assertEqual(boss.hp,boss.max_hp)
        self.assertTrue(all(s.hp<s.max_hp for s in seals))
        self.assertNotIn(boss,b.targetable_enemies)
        for seal in seals:
            if seal.alive:seal.down=True
        b.one_more=True
        self.assertTrue(b.all_out)
        self.assertIsNone(b.act('allout'))
        self.assertTrue(all(not s.alive for s in seals))
        self.assertIn(boss,b.targetable_enemies)
        self.assertEqual(boss.hp,boss.max_hp)

    def test_hanged_man_reseals_cannot_be_skipped_and_old_affinities_are_cleared(self):
        b=self.battle(BRIDGE)
        c=b.late_cycle
        for u in c.seals:
            b.seen[u.name]={'Ice':'weak'}
            u.hp=0
        self.assertFalse(b._ended())
        c.boss.hp=0
        self.assertFalse(b._ended())
        self.assertEqual(c.stage,2)
        self.assertTrue(c.airborne)
        self.assertEqual(len(b.targetable_enemies),3)
        self.assertFalse(b.seen)
        for u in c.seals:u.hp=0
        self.assertFalse(b._ended())
        c.boss.hp=0
        self.assertFalse(b._ended())
        self.assertEqual([u.name for u in b.targetable_enemies],['Great Statue'])

    def test_compact_hanged_man_draw_keeps_all_targets_and_commands_readable(self):
        class Screen:
            w,h=65,25

            def __init__(self):
                self.rows=[[' ']*self.w for _ in range(self.h)]

            def put(self,y,x,text,*_):
                self.rows[y][x:x+len(text)]=text

            def text(self):
                return '\n'.join(''.join(row) for row in self.rows)

        b=self.battle(BRIDGE,fuuka=True,theurgy=True)
        app=Screen();b.draw(app)
        for text in ('1 Skills','2 Attack','3 Guard','4 Items','5 Shift','6 All-Out','7 Analyze',
                     '8 Fuuka','9 Theurgy','Hanged Man','Left Statue','Center Statue','Right Statue'):
            self.assertIn(text,app.text())
        b.key('2');b.key(C.KEY_DOWN);b.key(C.KEY_DOWN)
        app=Screen();b.draw(app)
        for text in ('1 Left Statue','2 Center Statue','▶ 3 Right Statue','AFFINITY / Right Statue'):
            self.assertIn(text,app.text())

    def test_chidori_lethal_hit_triggers_heal_once_then_battle_ends_without_ko(self):
        b=self.battle(CHIDORI)
        chidori=b.enemies[0]
        chidori.hp=1
        self.assertIsNone(b.act('attack',chidori))
        self.assertIsNone(b.outcome)
        self.assertEqual(chidori.hp,chidori.max_hp)
        chidori.hp=1
        self.assertIsNone(b.act('attack',chidori))
        self.assertEqual(b.outcome,'win')
        self.assertTrue(chidori.alive)
        self.assertEqual(sum('Spring of Life' in s for s in b.log),1)
        self.assertIn('confrontation ends',b.log[-1])
