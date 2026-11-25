"""Campaign initiative reuses a single circular slot pattern."""
import unittest
from unittest.mock import patch

from battle_engine import Battle
from campaign_combat import build_stage
from campaign_data import NODES
from campaign_state import TestingCampaign
from qa_campaign import Tactician, configure_adapted


def pattern(b, order=None):
    return tuple(b._story_slots[u] for u in (b.order if order is None else order))


def successor(b, anchor):
    ring=b._story_ring
    start=ring.index(anchor)+1
    return tuple(slot for slot in ring[start:]+ring[:start] if slot<len(b.allies+b.enemies))


class StoryInitiativeTests(unittest.TestCase):
    def make(self, *, response=False, shuffle=True, waves=None):
        return Battle(('Mona','Skull'), 'Initiative Check', seed=7, shuffle_turns=shuffle,
                      encounter_config={'party_size':3, 'wave_response':response,
                                        'waves':waves or [('Pixie',), ('Pixie','Pixie','Pixie'), ('Pixie',)]})

    def change(self,b):
        for foe in b.enemies:
            foe.hp=0
        self.assertTrue(b._state())

    def test_first_draw_unaffected_by_reserved_ranks(self):
        shorter=self.make(waves=[('Pixie',)])
        b=self.make()
        self.assertEqual(pattern(shorter),pattern(b))
        self.assertEqual(shorter.initiative_rng.getstate(),b.initiative_rng.getstate())
        self.assertTrue(all(u in b.order for u in b.allies+b.enemies))

    def test_repeat_and_resume_with_variable_enemy_counts(self):
        b=self.make()
        rng_state=b.initiative_rng.getstate()
        old=b._story_ring
        previous=b._story_slots[b._slot_actor]
        self.change(b)
        self.assertEqual(pattern(b),successor(b,previous))
        self.assertEqual(pattern(b),pattern(b,b.next_order))
        self.assertEqual(b.round,1)
        # Continue after an enemy slot not present in the new, smaller wave.
        b._slot_actor=b.enemies[2]
        previous=b._story_slots[b._slot_actor]
        self.change(b)
        self.assertEqual(pattern(b),successor(b,previous))
        self.assertEqual(b._story_ring,old)
        self.assertEqual(b.initiative_rng.getstate(),rng_state)

    def test_baton_uses_original_scheduled_slot_for_continuation(self):
        b=self.make(shuffle=False)
        original=b._slot_actor
        b.one_more=True
        self.assertIsNone(b.act('pass:Mona'))
        self.assertIsNot(b.actor,original)
        self.assertIs(b._slot_actor,original)
        previous=b._story_slots[original]
        self.change(b)
        self.assertEqual(pattern(b),successor(b,previous))

    def test_response_rotates_without_adding_or_reordering_slots(self):
        b=self.make(response=True,shuffle=False)
        joker,mona,skull=b.allies
        self.assertIs(b._slot_actor,joker)
        mona.status='sleep'
        self.change(b)
        self.assertIs(b.order[0],skull)
        self.assertEqual(pattern(b),(2,3,4,5,0,1))
        self.assertEqual(pattern(b),pattern(b,b.next_order))
        self.assertEqual(len(set(b.order)),len(b.allies+b.enemies))
        b._advance()
        self.assertIs(b.actor,skull)
        self.assertFalse(b.one_more)

    def test_response_falls_back_to_last_player_if_only_ready(self):
        b=self.make(response=True,shuffle=False)
        joker,mona,skull=b.allies
        mona.status='sleep';skull.hp=0
        self.change(b)
        self.assertIs(b.order[0],joker)
        self.assertEqual(b.order.count(joker),1)
        self.assertIn(skull,b.order)  # Revival still has a real place.

    def test_regression_museum_security_seed1_no_duplicate_finisher(self):
        b=build_stage(TestingCampaign(),'museum-security',seed=1)
        brain=Tactician(b,'informed')
        tested=False
        for _ in range(80):
            old=b.wave
            ordinary=not b.one_more
            actor=b.actor
            command,target,persona=brain.choose(b.story_intent,b.actions('story-special'))
            self.assertIsNone(b.act(command,target,persona=persona))
            if old!=b.wave:
                self.assertTrue(ordinary)
                self.assertEqual(actor.name,'Skull')  # Original first-wave seed preserved.
                self.assertIsNot(b.actor,actor)
                tested=True
                break
            if b.phase!='turn':
                break
        self.assertTrue(tested)

    def test_bank_heist_seed5_gets_a_response_before_physical_burst(self):
        c=TestingCampaign()
        node=next(n for n in NODES if n['id']=='bank-heist')
        configure_adapted(c,'bank',node,observed=True)
        b=build_stage(c,node['id'],seed=5)
        brain=Tactician(b,'observed')
        with patch.object(b,'_enemy_step',wraps=b._enemy_step) as enemy:
            for _ in range(80):
                last=b._slot_actor
                command,target,persona=brain.choose(b.story_intent,b.actions('story-special'))
                enemy.reset_mock()
                self.assertIsNone(b.act(command,target,persona=persona))
                if b.wave==2:
                    enemy.assert_not_called()
                    self.assertEqual(b.phase,'turn')
                    self.assertEqual(b.persona,'Decarabia')
                    self.assertTrue(b._ready_for_opening(b.actor))
                    self.assertIsNot(b.actor,last)
                    return
                if b.phase!='turn':
                    break
        self.fail('Could not reproduce the Bank Heist formation change.')


if __name__=='__main__':
    unittest.main()
