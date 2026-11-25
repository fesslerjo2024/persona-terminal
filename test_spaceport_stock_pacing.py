"""Regression checks for the Executive Floor's bounded learning/resource relief."""
from unittest import TestCase
from unittest.mock import patch

from battle_engine import DEFAULT_ATTACK
from campaign_combat import build_stage
from campaign_state import TestingCampaign
from weekend_bosses import on_round


class ExecutiveFloorPacingTests(TestCase):
    def battle(self, node='spaceport-boss'):
        return build_stage(TestingCampaign(),node,seed=4)

    def test_eight_waves_and_no_published_exact_affinity(self):
        b=self.battle()
        self.assertEqual(tuple(b.config['spaceport_clock']),(2,2,2,2,2))
        self.assertEqual([len(w) for w in b.waves],[3,3,3,3,3,1,1,1])
        self.assertEqual(len({w[0] for w in b.waves[:5]}),5)
        self.assertFalse(b.config.get('affinity_intel'))
        self.assertEqual(b.seen,{})
        b.act('analyze',b.enemies[0])
        self.assertFalse(b.seen)

    def test_rank_affinity_is_shared_only_after_a_landed_probe(self):
        b=self.battle()
        target=b.enemies[0]
        with patch.object(b.rng,'randrange',return_value=99):
            b._strike(b.allies[0],target,DEFAULT_ATTACK)
        self.assertEqual(b.seen,{})
        with patch.object(b.rng,'randrange',return_value=0):
            b._strike(b.allies[0],target,DEFAULT_ATTACK)
        self.assertEqual({u.name: {'Physical':'resist'} for u in b.enemies},b.seen)
        b.wave=2
        b._spawn()
        self.assertTrue(all(u.name not in b.seen for u in b.enemies))
        self.assertEqual(self.battle().seen,{})

    def test_reissued_workers_return_once_with_less_health(self):
        b=self.battle()
        self.assertTrue(all(u.hp==u.max_hp for u in b.enemies))
        b.enemies[0].hp=0
        b.enemies[1].hp=1
        b.round=3
        on_round(b)
        self.assertEqual([u.hp for u in b.enemies],
                         [round(u.max_hp*.70) for u in b.enemies])
        self.assertTrue(b._boss_state.get('reissued'))
        b.enemies[0].hp=1
        b.round=4
        on_round(b)
        self.assertEqual(b.enemies[0].hp,1)

    def test_only_fourth_wave_topup_and_no_free_revives(self):
        b=self.battle()
        joker,mona,skull=b.allies
        joker.hp,joker.sp=11,0
        skull.hp,skull.sp=0,0
        mona_before=(mona.hp,mona.sp)
        b.wave=3
        b._spawn()
        self.assertEqual((joker.hp,joker.sp),(11,0))
        b.wave=4
        b._spawn()
        self.assertEqual((joker.hp,joker.sp),(joker.max_hp*66//100,17))
        self.assertEqual((skull.hp,skull.sp),(0,0))
        self.assertEqual((mona.hp,mona.sp),mona_before)
        self.assertTrue(any('maintenance' in l.casefold() for l in b.log))
        joker.hp,joker.sp=12,0
        b.wave=5
        b._spawn()
        self.assertEqual((joker.hp,joker.sp),(12,0))

    def test_worker_and_executive_entries_offer_one_able_thief(self):
        b=self.battle()
        joker,mona,skull=b.allies
        joker.status='sleep'
        skull.hp=0
        for wave in range(2,9):
            with self.subTest(wave=wave):
                b.wave=wave
                b.log.clear()
                b._spawn()
                self.assertEqual(b.order,b.next_order)
                self.assertEqual(len(set(b.order)),len(b.allies)+len(b.enemies))
                openings=[line for line in b.log if 'A brief opening' in line]
                if wave<=6:
                    self.assertIs(b.order[0],mona)
                    self.assertEqual(len(openings),1)
                else:self.assertFalse(openings)

    def test_ordinary_spaceport_patrol_does_not_share_probe(self):
        b=self.battle('spaceport-entry')
        bots=[u for u in b.enemies if u.behavior=='space-worker']
        self.assertEqual(len(bots),2)
        with patch.object(b.rng,'randrange',return_value=0):
            b._strike(b.allies[0],bots[0],DEFAULT_ATTACK)
        self.assertIn('Physical',b.seen[bots[0].name])
        self.assertNotIn(bots[1].name,b.seen)
