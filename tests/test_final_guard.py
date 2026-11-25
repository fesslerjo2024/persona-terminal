"""Final Guard is a live, one-use cut-in, not a gallery-only effect."""
import unittest

from persona_terminal.persona5.battle_engine import Battle
from persona_terminal.persona5.campaign_combat import build_stage
from persona_terminal.persona5.campaign_state import TestingCampaign
from persona_terminal.persona5.cutins import FINAL_GUARD
from .test_battle_information import Recorder


class FinalGuardTests(unittest.TestCase):
    def battle(self, active=True):
        return Battle((), 'Shield exercise', seed=4, shuffle_turns=False,
                      encounter_config={'waves': [['Attacker'], ['Attacker']], 'party_size': 1,
                                        'oracle_features': ('guard',) if active else ()},
                      enemy_data={'Attacker': {'hp': 180, 'skills': []}})

    def test_lethal_enemy_turn_plays_cut_then_returns_to_control_once(self):
        b=self.battle()
        joker=b.allies[0]
        joker.hp=1
        ui=Recorder(96,35)
        ui._b_battle=b; ui._b_screen='command'
        ui.battle_key('4')
        self.assertEqual(b.phase,'turn')
        self.assertIs(b.actor,joker)
        self.assertEqual(joker.hp,1)
        self.assertFalse(joker.down)
        self.assertEqual(b.damage_events,[])
        self.assertEqual(ui._b_cut_in[0],FINAL_GUARD[0])
        ui.battle_key(' ')
        self.assertIn('FINAL GUARD',ui.render())
        ui.battle_key('4')
        self.assertEqual(b.phase,'loss')
        self.assertFalse(joker.alive)
        self.assertEqual(sum('Final Guard' in line for line in b.log),1)

    def test_nonfatal_and_locked_guard_do_not_trigger(self):
        b=self.battle()
        joker=b.allies[0]
        self.assertIsNone(b.act('guard'))
        self.assertLess(joker.hp,joker.max_hp)
        self.assertFalse(b._final_guard_used)
        b=self.battle(active=False)
        b.allies[0].hp=1
        self.assertIsNone(b.act('guard'))
        self.assertEqual(b.phase,'loss')
        self.assertIsNone(b.cut_in)

    def test_guard_cannot_grant_enemy_bonus_or_import_status(self):
        b=self.battle()
        joker=b.allies[0]
        joker.hp=1
        joker.affinity['Fire']='weak'
        self.assertFalse(b._strike(b.enemies[0],joker,dict(element='Fire',
                         power=100,accuracy=100,status='burn',chance=100)))
        self.assertEqual((joker.hp,joker.down,joker.status),(1,False,''))

    def test_uses_op_instead_of_wave_and_respects_campaign_availability(self):
        stock=TestingCampaign()
        self.assertNotIn('guard', build_stage(stock,'castle-gate',1).config['oracle_features'])
        self.assertIn('guard', build_stage(stock,'spaceport-boss',1).config['oracle_features'])
        b=self.battle(); b.allies[0].hp=1
        b.act('guard')
        b.enemies[0].hp=0
        b._state()
        self.assertEqual(b.wave,2)
        self.assertTrue(b._final_guard_used)
