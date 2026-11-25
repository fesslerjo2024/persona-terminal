"""Durable discoveries and one-time enlistment on a replay, not reward farming."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from persona_terminal.persona5.battle_data import SKILLS
from persona_terminal.persona5.campaign_combat import build_stage
from persona_terminal.persona5.campaign_state import Campaign, TestingCampaign
from persona_terminal.persona3.persona3_combat import P3Battle
from persona_terminal.persona5.shadow_contract import Offer


class FieldMemoryTests(unittest.TestCase):
    def story(self):
        temp=TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        c=Campaign(Path(temp.name)/'story.json')
        c.new_game()
        while c.next_node!='east-gallery':c.clear(c.next_node)
        return c

    def test_only_attacked_elements_carried_after_victory_and_reload(self):
        c=self.story()
        b=build_stage(c,'east-gallery',10)
        eligor=b.enemies[0]
        self.assertFalse(b.seen)
        # Explicit 100% accuracy isolates the observation from the RNG;
        # this is one genuine damage-resolution call, not a playthrough.
        b._strike(b.allies[0],eligor,{**SKILLS['Eiga'],'accuracy':100},'Eiga')
        self.assertEqual(b.affinity_updates,{'Eligor':{'Curse':'resist'}})
        self.assertFalse(c.data.get('affinity_memory'))
        c.clear('east-gallery',affinity_updates=b.affinity_updates)
        c=Campaign(c.path)
        self.assertEqual(build_stage(c,'east-gallery',10).seen,{'Eligor':{'Curse':'resist'}})
        self.assertEqual(build_stage(TestingCampaign(),'east-gallery',10).seen,{})
        self.assertNotIn('Electric',c.data['affinity_memory']['Eligor'])

    def test_missed_contract_joins_on_replay_once_without_growth(self):
        c=self.story();c.clear('east-gallery','A')
        before=c.data
        b=build_stage(c,'east-gallery',10)
        offer=b.config['contract_offers']['Eligor']
        self.assertEqual(offer,Offer('east-gallery','Eligor','Eligor'))
        self.assertEqual(c.clear('east-gallery','B',contract=offer),{'personas':['Eligor']})
        c=Campaign(c.path);after=c.data
        self.assertIn('Eligor',after['stock'])
        for field in ('credits','skill_cards','joker_hp','joker_sp','cleared','loadout'):
            self.assertEqual(after[field],before[field],field)
        self.assertNotIn('Eligor',build_stage(c,'east-gallery',10).config['contract_offers'])
        original=c.path.read_bytes()
        self.assertFalse(c.clear('east-gallery','B',contract=offer))
        self.assertEqual(c.path.read_bytes(),original)

    def test_p3_uses_species_not_variant_display_name(self):
        lesson=P3Battle('awakening',seed=1)
        self.assertFalse(lesson.seen)
        lesson._hit(lesson.allies[0],lesson.enemies[0],'Fire',38)
        self.assertEqual(lesson.affinity_updates,{'maya':{'Fire':'weak'}})
        b=P3Battle('thebel-patrol',affinity_memory=lesson.affinity_updates)
        self.assertEqual(b.seen,{'Cowardly Maya':{'Fire':'weak'}})
        self.assertNotIn('Slash',b.seen['Cowardly Maya'])
        arcana=P3Battle('emperor-empress',affinity_memory={'emperor':{'Fire':'null'}})
        self.assertFalse(arcana.seen)

    def test_p3_award_and_intel_are_one_durable_transaction(self):
        from persona_terminal.persona3.persona3_state import P3Store, TUTORIAL
        temp=TemporaryDirectory();self.addCleanup(temp.cleanup)
        path=Path(temp.name)/'persona3.json'
        s=P3Store(path);s.new_game()
        s.grant_xp(35,phase='tartarus',day=TUTORIAL,affinity_updates={'maya':{'Fire':'weak'}})
        saved=P3Store(path).state
        self.assertEqual((saved.xp,saved.affinity_index),(35,{'maya':{'Fire':'weak'}}))
        b=P3Battle('thebel-patrol',affinity_memory=saved.affinity_index)
        self.assertEqual(b.seen,{'Cowardly Maya':{'Fire':'weak'}})
