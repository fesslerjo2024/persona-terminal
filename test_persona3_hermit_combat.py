"""Hermit charge timing and defensive/offensive counterplay."""
from unittest import TestCase

from persona3_combat import DEFAULT_PARTY, LEAD_ID, P3Battle


class HermitCombatTests(TestCase):
    def fight(self, **kwargs):
        return P3Battle('hermit',seed=4,level=9,**kwargs)

    def trigger(self,b,hp):
        # Reach the edge of a window without relying on prior damage rolls;
        # the transition itself must come from an actual committed hit.
        foe=b.enemies[0]
        foe.hp=foe.max_hp*hp//100+5
        self.assertIsNone(b.act('attack',foe))
        return foe

    def test_september_roster_never_deploys_junpei(self):
        with self.assertRaisesRegex(ValueError,'Junpei is unavailable'):
            self.fight(party=DEFAULT_PARTY)
        self.assertNotIn('Junpei',[u.name for u in self.fight().allies])
        self.assertIn('Junpei',[u.name for u in P3Battle('thebel-patrol').allies])

    def test_early_charge_counts_damage_not_reading_and_is_interruptible(self):
        b=self.fight()
        foe=self.trigger(b,90)
        tracker=b.hermit_cycle
        self.assertIn('MEGA SPARK CHARGING',b.threat)
        old=(tracker.stagger,tracker.beats,foe.hp,b.actor)
        self.assertIsNone(b.act('analyze',foe))
        self.assertEqual((tracker.stagger,tracker.beats,foe.hp,b.actor),old)
        while tracker.window is not None:
            self.assertIsNone(b.act('attack',foe))
        self.assertTrue(any('Mega Spark interrupted' in line for line in b.log))
        self.assertFalse(any('releases Mega Spark' in line for line in b.log))

    def test_null_affinity_cannot_tick_stagger_meter(self):
        b=self.fight(persona='Naga')
        foe=self.trigger(b,90)
        while b.actor is not b.allies[0]:
            self.assertIsNone(b.act('guard'))
        snapshot=(foe.hp,b.hermit_cycle.stagger)
        self.assertIsNone(b.act('skill:Zionga',foe))
        self.assertEqual((foe.hp,b.hermit_cycle.stagger),snapshot)
        self.assertEqual(b.seen[foe.name]['Electric'],'null')

    def test_later_accelerated_spark_gives_time_to_guard_and_guard_matters(self):
        def resolve(protect):
            b=self.fight(party=(LEAD_ID,'Yukari','Mitsuru'))
            b.enemies[0].attack=-1
            self.trigger(b,22)
            self.assertEqual(b.enemies[0].defense,-1)
            self.assertIn('TERA SPARK CHARGING',b.threat)
            while b.hermit_cycle.beats>1:
                self.assertIsNone(b.act('guard'))
            self.assertIn('TERA SPARK NEXT',b.threat)
            lead=b.allies[0]
            hp=lead.hp
            move=('guard',None) if protect else ('skill:Tarunda',b.enemies[0])
            self.assertIsNone(b.act(*move))
            while not any('releases Tera Spark' in line for line in b.log):
                self.assertIsNone(b.act('guard'))
            return hp-lead.hp

        guarded,unguarded=resolve(True),resolve(False)
        self.assertLess(guarded,unguarded)
        self.assertGreater(unguarded,65)

    def test_finishing_hit_does_not_create_or_fire_charge(self):
        b=self.fight()
        b.enemies[0].hp=1
        self.assertIsNone(b.act('attack',b.enemies[0]))
        self.assertEqual(b.outcome,'win')
        self.assertEqual(b.threat,'')
        self.assertFalse(any('Charging' in line for line in b.log))
