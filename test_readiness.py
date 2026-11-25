from unittest import TestCase
from campaign_state import TestingCampaign
from campaign_combat import build_stage, readiness

class ReadinessTests(TestCase):
    def test_only_equipped_team_and_solo_kit(self):
        c = TestingCampaign()
        c.equip_squad(('Crow','Violet','Queen'))
        before = c.data
        row = readiness(c,c.get_node('casino-service'))
        self.assertEqual(set(row),{'Joker','Crow','Queen'})
        self.assertIn('Bless',row['Crow'][0])
        self.assertNotIn('Violet',row)
        self.assertEqual(set(readiness(c,c.get_node('cruiser-duel'))),{'Joker'})
        self.assertEqual(c.data,before)

    def test_bank_response_first_when_a_fighter_can_act(self):
        for node in ('bank-security','bank-vault'):
            for seed in range(8):
                b = build_stage(TestingCampaign(),node,seed=seed)
                for u in b.allies:
                    u.status_turns=2
                    u.status='' if u.name=='Mona' else 'sleep'
                before = sum(u.hp for u in b.allies)
                b.wave=2
                b._spawn()
                b._advance()
                self.assertEqual(b.actor.name,'Mona')
                self.assertEqual(before,sum(u.hp for u in b.allies))
                self.assertEqual(b.round,1)
