import unittest

from battle_engine import DEFAULT_ATTACK
from campaign_combat import build_stage
from campaign_state import TestingCampaign
from cutins import ALL_OUT, SHOWTIMES

class CutInTests(unittest.TestCase):
    def test_final_guard_once_and_not_available_before_recruitment(self):
        for name,guard_expected in [('guardhouse',False),('spaceport-boss',True)]:
            b=build_stage(TestingCampaign(),name,seed=37)
            foe,joker=b.enemies[0],b.allies[0]
            joker.hp=1
            attack=dict(DEFAULT_ATTACK,accuracy=200)
            b._strike(foe,joker,attack)
            self.assertEqual(guard_expected,joker.alive)
            if guard_expected:
                self.assertIn('FINAL GUARD',b.cut_in[0])
                self.assertFalse(b._strike(foe,joker,attack))
                self.assertFalse(joker.alive)

    def test_two_foe_finish_uses_oracle_only_after_recruitment(self):
        for name,oracle in [('guardhouse',False),('laboratory-reality',True)]:
            b=build_stage(TestingCampaign(),name,seed=1)
            self.assertGreaterEqual(len(b.enemies),2)
            b.one_more=True
            for u in b.enemies:u.hp=1;u.down=True
            self.assertIsNone(b.act('allout'))
            self.assertEqual(oracle,'ORACLE' in b.cut_in[0])

    def test_every_implemented_pair_and_all_out_actor_has_unique_cut(self):
        from campaign_data import NODES
        pairs={frozenset(pair) for row in NODES for pair in row.get('showtime_pairs',())}
        self.assertTrue(pairs<=SHOWTIMES.keys())
        self.assertEqual(len(set(ALL_OUT.values())),9)

if __name__ == "__main__":
    unittest.main()
