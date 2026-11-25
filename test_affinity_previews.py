import unittest

from battle_ui import BattleUI
from campaign_combat import build_stage
from campaign_state import TestingCampaign


class AffinityPreviewTests(unittest.TestCase):
    def setup_museum(self):
        self.view=BattleUI()
        self.b=self.view._b_battle=build_stage(TestingCampaign(),'museum-throne',0)
        return self.b.enemies

    def test_successful_probe_only_and_no_change_to_target_legality(self):
        eyes,nose,mouth=self.setup_museum()
        b=self.b
        joker=b.allies[0]
        self.assertEqual(self.view._b_known_matchups('skill:Eiga'),{})
        b._strike(joker,nose,dict(b._spec('skill:Eiga'),accuracy=0))
        self.assertEqual(self.view._b_known_matchups('skill:Eiga'),{})
        b._strike(joker,nose,dict(b._spec('skill:Eiga'),accuracy=100))
        self.assertEqual(self.view._b_known_matchups('skill:Eiga'),{nose:'drain'})
        self.assertIn(nose,b.targets('skill:Eiga'))
        self.assertEqual((nose.affinity['Curse'],b.seen[nose.name]['Curse']),('drain','drain'))
        self.assertEqual(self.view._b_known_matchups('skill:Agilao'),{})

    def test_group_priority_and_existing_weak_single(self):
        eyes,nose,mouth=self.setup_museum()
        b=self.b
        b.seen={eyes.name:{'Fire':'drain'},nose.name:{'Fire':'repel'},mouth.name:{'Fire':'weak'}}
        aid='skill:Maragion'
        preview=self.view._b_skill_preview(aid,'Maragion','Power')
        self.assertEqual(preview,('Maragion [DRAIN 1 REPEL 1 WEAK 1]',
            'Drain: Madarame’s Eyes; Repel: Madarame’s Nose; Weak: Madarame’s Mouth'))
        self.assertEqual(self.view._b_skill_preview('skill:Agilao','Agilao','Power'),
                         ('Agilao [WEAK]','Power'))
        del b.seen[eyes.name],b.seen[nose.name]
        self.assertEqual(self.view._b_skill_preview(aid,'Maragion','Power'),
                         ('Maragion [WEAK]','Weak: Madarame’s Mouth'))

    def test_hidden_dead_and_affinity_bypass_are_not_previewed(self):
        eyes,nose,mouth=self.setup_museum()
        b=self.b
        b.seen={eyes.name:{'Gun':'drain'},nose.name:{'Gun':'repel','Almighty':'drain'},
                mouth.name:{'Gun':'weak','Fire':'null'}}
        b._boss_state['arms']={eyes.name:eyes}  # Controlled hidden, still-HP-positive fixture.
        nose.hp=0
        self.assertEqual(self.view._b_known_matchups('gun'),{mouth:'weak'})
        nose.hp=1;nose.status='freeze'
        self.assertEqual(self.view._b_known_matchups('gun'),{mouth:'weak'})
        b._boss_state.pop('arms')
        eyes.status='freeze'
        self.assertEqual(self.view._b_known_matchups('skill:Riot Gun'),{mouth:'weak'})
        self.assertEqual(self.view._b_known_matchups('skill:Megido'),{})
        self.assertEqual(self.view._b_known_matchups('skill:Agilao'),{})
        self.assertEqual(self.view._b_known_matchups('skill:Rakunda'),{})


if __name__=='__main__':
    unittest.main()
