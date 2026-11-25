"""State, timing, and compact-view regressions for the August operation."""
import unittest

from persona_terminal.persona3.persona3_cinematics import render_theurgy
from persona_terminal.persona3.persona3_combat import LEAD_ID, P3Battle
from .test_persona3_arqa_combat import Surface

SQUAD=(LEAD_ID,'Aigis','Yukari','Akihiko')


class AugustCombat(unittest.TestCase):
    def make(self,**kwargs):
        return P3Battle('chariot-justice',party=SQUAD,level=8,seed=42,**kwargs)

    def test_visible_form_changes_without_phantom_targets(self):
        b=self.make()
        for width,height in ((65,25),(120,40)):
            view=Surface(width,height);b.draw(view)
            self.assertIn('Tank-Form Shadow',view.text())
            self.assertNotIn('Justice',view.text())
        self.assertEqual([u.role for u in b._targets('attack')],['tank'])
        self.assertEqual(b.seen,{})
        tank=b.tank_cycle.tank
        tank.hp=150
        self.assertIsNone(b.act('skill:Agi',tank))
        self.assertEqual([u.role for u in b._targets('attack')],['chariot','justice'])
        self.assertEqual(b.seen[tank.name],{'Fire':'resist'})
        view=Surface(65,25);b.draw(view)
        self.assertIn('Justice',view.text())
        self.assertNotIn('Tank-Form Shadow',view.text())

    def test_almighty_opens_before_shell_threshold(self):
        b=self.make(theurgy=True,charge={LEAD_ID:100},registered={"Jack O'Lantern",'Jack Frost'})
        self.assertIsNone(b.act('theurgy:jacks'))
        self.assertEqual(b.tank_cycle.stage,'split')
        self.assertTrue(all(u.hp==u.max_hp for u in b.tank_cycle.visible))

    def test_last_living_half_revives_unless_both_die(self):
        b=self.make()
        b.tank_cycle.settle(b,force=True)
        chariot,justice=b.tank_cycle.visible
        justice.hp=1
        self.assertIsNone(b.act('skill:Agi',justice))
        self.assertIn('REVIVAL INCOMING',b.threat)
        for _ in range(3):self.assertIsNone(b.act('guard'))
        self.assertEqual(justice.hp,justice.max_hp//3)
        self.assertTrue(any('revives Justice' in row for row in b.log))
        chariot.hp=justice.hp=1
        self.assertIsNone(b.act('guard'))  # Makoto passes to Aigis.
        self.assertIsNone(b.act('skill:Swift Strike'))
        self.assertEqual(b.outcome,'win')

    def test_recombine_preserves_separate_hp(self):
        b=self.make()
        b.tank_cycle.settle(b,force=True)
        chariot,justice=b.tank_cycle.visible
        chariot.hp,justice.hp=100,81
        for _ in range(12):
            self.assertIsNone(b.act('guard'))
        self.assertIn('RECOMBINE INCOMING',b.threat)
        for _ in range(4):
            self.assertIsNone(b.act('guard'))
        self.assertEqual(b.tank_cycle.stage,'tank')
        self.assertEqual(b.tank_cycle.hp,(100,81))
        b.tank_cycle.settle(b,force=True)
        self.assertEqual((chariot.hp,justice.hp),(100,81))

    def test_aigis_three_auto_volleys_and_one_cooldown(self):
        b=P3Battle('hotel-lovers',party=SQUAD,level=10,seed=11,
                   theurgy=True,charge={'Aigis':100})
        b.enemies[0].hp=b.enemies[0].max_hp=3000
        self.assertIsNone(b.act('guard'))
        self.assertIsNone(b.act('theurgy:orgia'))
        self.assertEqual(b.reel[0],'Orgia Mode')
        self.assertEqual(b.orgia,2)
        self.assertEqual(b._attack_element('theurgy:orgia'),'Pierce')
        self.assertEqual(b._affinity_tags('theurgy:orgia'),{})
        for _ in range(12):
            if b.actor.name=='Aigis':break
            self.assertIsNone(b.act('guard'))
        self.assertEqual(b.actor.name,'Aigis')
        self.assertEqual(sum('opens fire in Orgia Mode' in x for x in b.log),3)
        self.assertEqual(sum('Aigis cools down.' in x for x in b.log),1)
        self.assertFalse(b.orgia or b.orgia_cooldown)
        self.assertIsNone(b.act('skill:Marakukaja'))
        self.assertTrue(all(u.defense>0 for u in b.allies if u.alive))
        self.assertNotEqual(render_theurgy('Orgia Mode',.9,64,25),
                            render_theurgy('Cyclone Arrow',.9,64,25))


if __name__=='__main__':
    unittest.main()
