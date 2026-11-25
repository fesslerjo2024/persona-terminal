import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from battle_data import SKILLS, TEAM
from campaign_combat import build_stage
from campaign_data import CHAPTERS, ENEMY_DATA, FUSIONS, NODES, PERSONA_DATA
from campaign_state import Campaign, CampaignError, TestingCampaign
from weekend_bosses import enemy_step, on_round


class CampaignProgressTests(unittest.TestCase):
    def test_all_routes_have_unique_id_and_legal_references(self):
        self.assertEqual(tuple(c['id'] for c in CHAPTERS),
                         ('castle','museum','bank','pyramid','spaceport','casino','cruiser','depths','laboratory'))
        ids = [n['id'] for n in NODES]
        self.assertEqual(len(ids), len(set(ids)))
        c = TestingCampaign()
        for n in NODES:
            b = build_stage(c, n['id'], seed=41)
            self.assertFalse(b.actor.enemy, n['id'])
            self.assertEqual(b.seen, {})
            self.assertTrue(all(enemy in ENEMY_DATA for wave in n['waves'] for enemy in wave))
            self.assertTrue(set(n['reward'].get('teammates',())) <= TEAM.keys())
        self.assertFalse(c.data['cleared'])

    def test_story_unlock_is_ordered_and_manual_fusion_survives_reload(self):
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / 'save.json'
            c=Campaign(source)
            c.new_game()
            before=source.read_bytes()
            self.assertTrue(c.can_play(NODES[0]['id']))
            self.assertFalse(c.can_play(NODES[1]['id']))
            self.assertTrue(TestingCampaign().can_play(NODES[-1]['id']))
            self.assertEqual(before,source.read_bytes())
            self.assertIsInstance(c.clear(NODES[0]['id'],'B'),dict)
            self.assertTrue(c.can_play(NODES[1]['id']))
            recipe = next(r for r in FUSIONS if r['result']=='High Pixie')
            self.assertTrue(c.fusion_options(recipe['result'])['available'])
            c.fuse(recipe['result'])
            self.assertIn('High Pixie',Campaign(source).data['personas'])

    def test_queen_robin_hood_and_solo_gates(self):
        c=TestingCampaign()
        c.equip_squad(('Crow','Violet','Queen'))
        b=build_stage(c,'casino-service',seed=9)
        team={u.name:u for u in b.allies}
        self.assertIn('Makouga', team['Crow'].skills)
        self.assertNotIn('Violet',team)
        b=build_stage(c,'cruiser-duel',seed=9)
        self.assertEqual([u.name for u in b.allies],['Joker'])
        self.assertGreater(b.items['Medicine'],3)

    def test_bank_bait_cancels_telegraph_without_affinity_reveal(self):
        b=build_stage(TestingCampaign(),'bank-boss',seed=41)
        a=b.enemies[0]
        b._boss_state.update(pig_turn=1)
        enemy_step(b,a)
        self.assertIn('MARCH',b.story_intent)
        count=b.items['Medicine']
        self.assertIsNone(b.act('story-special'))
        self.assertEqual(b.items['Medicine'],count-1)
        self.assertEqual(b.seen,{})
        self.assertNotIn('pending',b._boss_state)
        self.assertFalse(b.actions('story-special'))

    def test_pyramid_ballista_and_robot_shift_reissue(self):
        b=build_stage(TestingCampaign(),'pyramid-boss',seed=2)
        a=b.enemies[0]
        b.round=3
        on_round(b)
        self.assertTrue(b.actions('story-special'))
        old=a.hp
        self.assertIsNone(b.act('story-special'))
        self.assertLess(a.hp,old)
        self.assertTrue(b._boss_state.get('grounded'))
        b=build_stage(TestingCampaign(),'spaceport-boss',seed=5)
        a=b.enemies[0]
        a.hp=1;b.round=3
        on_round(b)
        self.assertEqual(a.hp,a.max_hp)
        a.hp=1
        on_round(b)
        self.assertEqual(a.hp,1)
