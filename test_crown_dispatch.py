import random
import unittest

from battle_engine import Battle, DEFAULT_ATTACK
from campaign_combat import build_stage
from campaign_state import TestingCampaign
from crown_dispatch import ACTION, EXPOSED_HITS
import weekend_bosses as bosses


class CrownDispatchTests(unittest.TestCase):
    def make(self,seed=0):
        b=build_stage(TestingCampaign(),'throne-room',seed)
        king,trophy=b.enemies
        return b,king,trophy

    def land(self,b,king,*,accuracy=100,element='Fire',power=10):
        b._strike(b.allies[0],king,dict(DEFAULT_ATTACK,accuracy=accuracy,element=element,power=power))

    def test_optional_after_trophy_and_only_in_campaign_throne(self):
        b,king,trophy=self.make()
        self.assertEqual(b.actions(ACTION),[])
        self.assertEqual(b.targets(ACTION),[])
        self.assertIsNotNone(b.act(ACTION,b.allies[1]))
        trophy.hp=0
        self.assertIn('C: Send a runner',b.story_intent)
        self.assertEqual(b.actions(ACTION)[0][0],ACTION)
        self.assertEqual(b.actions('story-special'),[])
        self.assertEqual(b.targets(ACTION),b.allies[1:])
        self.assertIsNotNone(b.action_block(ACTION,b.allies[0]))
        self.assertIsNone(b.action_block(ACTION,b.allies[1]))
        self.assertIsNotNone(b.act(ACTION))
        b.allies[1].down=True
        b.allies[2].status='freeze'
        self.assertEqual(b.targets(ACTION),[])
        b.config={**b.config,'id':'some-other-room'}
        b.allies[1].down=False
        self.assertEqual(b.targets(ACTION),[])

    def test_runner_absence_changes_no_vitals_or_initiative(self):
        b,king,trophy=self.make()
        trophy.hp=0
        runner=b.allies[1]
        runner.hp-=41
        runner.sp-=8
        runner.status='burn'
        runner.status_turns=2
        runner.buffs['attack']=(1,3)
        vitals=lambda:(runner.hp,runner.sp,runner.status,runner.status_turns,runner.buffs.copy())
        snapshot=vitals()
        order=list(b.order)
        b._boss_state['pending']=set(b.allies)
        self.assertIsNone(b.act(ACTION,runner))
        self.assertTrue(runner.away)
        self.assertEqual(vitals(),snapshot)
        self.assertEqual(order,b.order)
        self.assertEqual(order,b.next_order)
        self.assertNotIn(runner,b.upcoming_turns())
        self.assertNotIn(runner,b._boss_state.get('pending',()))
        self.assertNotIn(runner,b.targets('item:Medicine'))
        self.assertNotIn(runner,b.targets('item:Life Ointment'))
        self.assertNotIn(runner,b._baton())
        self.assertEqual(b.allout_fighters,sum(u.alive and not u.down for u in b.allies)-1)
        self.assertIsNotNone(b.act(ACTION,b.allies[2]))
        b._execute(b.actor,dict(kind='heal',target='allies',power=1),None,'Group recovery')
        bosses._push(b,king,'Cleave','Physical',10,group=False)
        bosses._push(b,king,'Royal Smash','Almighty',49,group=True)
        self.assertEqual(vitals(),snapshot)
        for _ in range(len(order)+2):
            self.assertIsNot(b.actor,runner)
            if b.phase=='turn':b.act('guard')
        self.assertEqual(vitals(),snapshot)

    def test_charge_while_away_and_runner_cannot_enable_showtime(self):
        b,king,trophy=self.make()
        trophy.hp=0
        runner=b.allies[1]
        self.assertIsNone(b.act(ACTION,runner))
        bosses._charge(b,'The King winds up Royal Smash.')
        self.assertNotIn(runner,b._boss_state['pending'])
        self.assertIn('Guard',b.story_intent)
        b.actor=b.allies[2]
        b.config={**b.config,'showtime_pairs':((b.actor.name,runner.name),),
                  'available_thieves':(b.actor.name,runner.name,'Panther')}
        b._showtime_rng=random.Random(1)  # lower than offer threshold
        b._offer_showtime(baton=True)
        self.assertIsNone(b._showtime)
        b.config={**b.config,'showtime_pairs':((b.actor.name,'Panther'),)}
        b._showtime_rng=random.Random(1)
        b._offer_showtime(baton=True)
        self.assertEqual(b._showtime,(b.actor.name,'Panther'))

    def test_cover_needs_two_landed_hits_and_opening_is_capped(self):
        b,king,trophy=self.make()
        trophy.hp=0
        runner=b.allies[1]
        self.assertIsNone(b.act(ACTION,runner))
        b._boss_state['pending']=set(b.combat_allies)
        start=king.hp
        self.land(b,king,accuracy=0)
        self.assertEqual(king.hp,start)
        self.assertEqual(b._boss_state['crown_hits'],0)
        king.affinity['Ice']='null'
        self.land(b,king,element='Ice')
        self.assertEqual(b._boss_state['crown_hits'],0)
        self.land(b,king)
        self.assertEqual(b._boss_state['crown_hits'],1)
        self.assertTrue(runner.away)
        self.land(b,king)
        self.assertFalse(runner.away)
        self.assertNotIn('pending',b._boss_state)
        self.assertIn('CROWN STOLEN',b.story_intent)
        self.assertEqual(b._boss_state['crown_exposed'],EXPOSED_HITS)
        self.assertFalse(bosses.enemy_step(b,king))
        self.assertNotIn('crown_stagger',b._boss_state)
        self.assertIn('Kamoshida loses his action',b.log[-1])
        rng=b.rng.getstate()
        damage=[]
        for _ in range(EXPOSED_HITS+1):
            b.rng.setstate(rng)
            hp=king.hp
            self.land(b,king)
            damage.append(hp-king.hp)
        self.assertEqual(len(set(damage[:EXPOSED_HITS])),1)
        self.assertGreater(damage[0],damage[-1])
        self.assertEqual(b._boss_state['crown_exposed'],0)
        self.assertFalse(b.actions(ACTION))

    def test_king_can_die_on_first_or_second_hit_and_runner_returns(self):
        for first_hit in (True,False):
            with self.subTest(first_hit=first_hit):
                b,king,trophy=self.make()
                trophy.hp=0
                runner=b.allies[1]
                self.assertIsNone(b.act(ACTION,runner))
                if not first_hit:
                    self.land(b,king)
                king.hp=1
                self.land(b,king)
                self.assertEqual(king.hp,0)  # no threshold/floor
                self.assertTrue(b._state())
                self.assertEqual(b.phase,'win')
                self.assertFalse(runner.away)
                self.assertNotIn('crown_exposed',b._boss_state)
                self.assertTrue(any('returns as the King falls' in s for s in b.log))
                self.assertFalse(any('takes the crown and returns' in s for s in b.log))


if __name__=='__main__':
    unittest.main()
