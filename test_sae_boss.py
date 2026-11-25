"""Engine-path and state tests for the Casino heist."""
import unittest

from battle_data import SKILLS
from campaign_combat import build_stage
from campaign_state import TestingCampaign
from weekend_bosses import block_hit


class SaeTest(unittest.TestCase):
    def create(self):
        return build_stage(TestingCampaign(), 'casino-heist', seed=25)

    def clue(self, b):
        for _ in range(8):
            if b.actions('story-special'):
                return
            self.assertIsNone(b.act('guard'))
        self.fail('Sae never presents a player action after the roulette clue')

    def test_real_opening_offers_special(self):
        b = self.create()
        sae = b.enemies[0]
        self.assertIn('ROULETTE', b.story_intent)
        self.assertTrue(block_hit(b, sae, SKILLS['Agilao']))
        self.clue(b)
        self.assertIn('9: Break the glass', b.story_intent)
        self.assertIsNone(b.act('story-special'))
        self.assertFalse(b.actions('story-special'))
        self.assertTrue(b._boss_state['sae_open'])
        self.assertFalse(block_hit(b, sae, SKILLS['Agilao']))
        self.assertEqual({}, b.seen)
        self.assertFalse(any('claims its wager' in line for line in b.log))

    def test_ignore_special_does_not_softlock(self):
        b = self.create()
        self.clue(b)
        for _ in range(8):
            if b._boss_state.get('sae_open'):
                break
            b.act('guard')
        self.assertTrue(b._boss_state['sae_open'])
        self.assertTrue(any('claims its wager' in line for line in b.log))
        self.assertTrue(all(a.alive for a in b.allies))

    def test_guard_reduces_same_seed_finisher(self):
        outcomes = []
        for response in ('guard', 'untaken'):
            b = self.create()
            self.clue(b)
            b.act('story-special')
            b.enemies[0].hp //= 2
            for _ in range(12):
                if 'BERSERKER DANCE' in b.story_intent:
                    break
                b.act('guard')
            else:
                self.fail('No openly telegraphed Berserker Dance')
            before = sum(a.hp for a in b.allies)
            for _ in range(12):
                if response == 'guard':
                    b.act('guard')
                else:
                    # Advance a slot without defense or any RNG-consuming action.
                    b._advance()
                if any('→ Berserker Dance.' in line for line in b.log):
                    break
            else:
                self.fail('Sae failed to resolve the warned attack')
            outcomes.append(before - sum(a.hp for a in b.allies))
        self.assertGreater(outcomes[0], 0)
        self.assertLess(outcomes[0], .65 * outcomes[1])


if __name__ == '__main__':
    unittest.main()
