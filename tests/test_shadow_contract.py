"""Exercise the optional Hold Up action, its UI, and atomic campaign reward."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from persona_terminal.persona5.battle_data import ENCOUNTERS
from persona_terminal.persona5.battle_engine import Battle
from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona5.campaign import CampaignApp
from persona_terminal.persona5.campaign_combat import build_stage
from persona_terminal.persona5 import campaign_data
from persona_terminal.persona5.campaign_state import Campaign, CampaignError, TestingCampaign
from persona_terminal.persona5.shadow_contract import Offer, offers


def advance_to(store, key):
    for node in campaign_data.NODES:
        if node['id']==key:
            return
        if node['id'] not in store.data['cleared']:
            store.clear(node['id'])


class ContractTests(unittest.TestCase):
    def setUp(self):
        temp=TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)/'play.json'
        self.store=Campaign(self.path)
        self.store.new_game()
        advance_to(self.store,'east-gallery')
        self.app=CampaignApp(None,self.store,seed=0)
        self.app.node=self.store.get_node('east-gallery')
        self.app.stage()
        self.b=self.app._b_battle

    def make_hold_up(self):
        elif_,silky=self.b.enemies
        self.assertEqual(self.b.actor.name,'Joker')
        self.assertFalse(self.b.actions('contract'))
        self.assertIsNone(self.b.act('skill:Zio',elif_,persona='Pixie'))
        self.assertFalse(self.b.actions('contract'))  # Only one Shadow down.
        self.assertIsNone(self.b.act('skill:Agi',silky,persona="Jack-o'-Lantern"))
        self.assertTrue(self.b.hold_up)
        return elif_,silky

    def test_ui_cancel_confirm_and_clear_are_distinct(self):
        eligor,silky=self.make_hold_up()
        before=self.path.read_bytes()
        commands=self.app._b_action_menu()
        self.assertTrue(any(cat=='allout' and enabled for cat,_,_,enabled in commands))
        self.assertTrue(any(cat=='contract' and 'on victory' in detail and enabled
                            for cat,_,detail,enabled in commands))
        self.app._b_index=next(i for i,row in enumerate(commands) if row[0]=='contract')
        self.app.key('\n')
        self.assertEqual(self.app._b_screen,'targets')
        self.assertEqual(self.b.targets('contract'),[eligor])
        self.app.key(ESC)
        self.assertEqual(self.app._b_screen,'command')
        self.assertIsNone(self.b.contract)
        self.assertEqual(self.path.read_bytes(),before)
        self.app.key('\n')
        self.app.key('\n')
        self.assertEqual(self.b.contract,Offer('east-gallery','Eligor','Eligor'))
        self.assertFalse(eligor.alive)
        self.assertTrue(silky.alive)
        self.assertEqual(silky.hp,50)  # No All-Out damage to the other Shadow.
        self.assertFalse(self.b.hold_up or self.b.one_more)
        self.assertNotIn('Eligor',self.b.personas)
        self.assertEqual(self.path.read_bytes(),before)
        self.assertTrue(any('Register Eligor on victory' in msg for msg in self.b.log))
        self.assertFalse(any(unit is eligor for unit,*_ in self.b.damage_events))
        self.assertEqual(self.b.actor.name,'Skull')
        self.assertIsNone(self.b.act('skill:Zionga',silky))
        self.assertEqual(self.b.phase,'win')
        self.app.record()
        self.assertEqual(self.app.reward['personas'],['Silky','Eligor'])
        reopened=Campaign(self.path)
        self.assertIn('Eligor',reopened.data['personas'])
        self.assertNotIn('Eligor',reopened.data['loadout'])
        self.assertEqual(reopened.persona_spec('Eligor')['skills'],['Agi','Cleave','Tarukaja'])
        self.assertFalse(build_stage(reopened,'east-gallery',0).config['contract_offers'])
        self.assertEqual(reopened.clear('east-gallery', 'B', contract=self.b.contract),{})

    def test_declined_contract_and_defeat_award_no_mask(self):
        eligor,_=self.make_hold_up()
        self.assertIsNone(self.b.act('allout'))
        self.assertEqual(self.b.phase,'win')
        self.app.record()
        self.assertNotIn('Eligor',self.store.data['personas'])
        advance_to(self.store,'treasure-route')
        self.app.node=self.store.get_node('treasure-route')
        self.app.stage()
        b=self.app._b_battle
        proof=Offer('treasure-route','Eligor','Eligor')
        self.assertIn(proof,b.config['contract_offers'].values())
        # Even a legitimate offer accepted before a defeat cannot be recorded.
        b.contract=proof
        before=self.path.read_bytes()
        b.allies[0].hp=0
        b._state()
        self.assertEqual(b.phase,'loss')
        self.app.record()
        self.assertEqual(self.path.read_bytes(),before)

    def test_unavailable_first_clear_owned_guaranteed_testing_and_boss(self):
        eligor,silky=self.make_hold_up()
        self.assertIsNotNone(self.b.act('contract',silky))
        self.assertTrue(eligor.alive and silky.alive and self.b.hold_up)
        self.assertEqual(self.b.actions('contract')[0][0],'contract')

        c=TestingCampaign(fusion_practice=True)  # Contract mask not preinstalled.
        battle=build_stage(c,'east-gallery',0)
        self.assertNotIn('Eligor',c.data['personas'])
        self.assertFalse(battle.config['contract_offers'])
        self.assertEqual(c.clear('east-gallery',contract=Offer('east-gallery','Eligor','Eligor')), {})
        self.assertNotIn('Eligor',c.data['personas'])
        # Neither a boss nor Classic grants the command even if manipulated
        # to look like a Hold Up by the test fixture.
        boss=build_stage(TestingCampaign(),'bank-boss',0)
        self.assertFalse(boss.config['contract_offers'])
        trial=Battle(('Mona','Skull','Panther'),next(iter(ENCOUNTERS)),seed=0)
        self.assertFalse(trial.actions('contract'))
        node=self.store.get_node('east-gallery')
        self.assertFalse(offers(node,{'Eligor':[]}))
        node['reward']['personas']={'Silky': (), 'Eligor': ()}
        self.assertFalse(offers(node,{}))

    def test_wrong_offer_is_atomic_and_duplicate_display_labels_are_safe(self):
        before=self.path.read_bytes()
        with self.assertRaises(CampaignError):
            self.store.clear('east-gallery',contract=Offer('bank-service','Fuu-Ki','Fuu-Ki'))
        self.assertEqual(self.path.read_bytes(),before)
        advance_to(self.store,'museum-gallery')
        b=build_stage(self.store,'museum-gallery',0)
        b.one_more=True
        for u in b.enemies:u.down=True
        self.assertEqual([t.name for t in b.targets('contract')],['Koppa Tengu A','Koppa Tengu B'])
        self.assertIsNone(b.act('contract',b.enemies[2]))
        self.assertEqual(b.contract,Offer('museum-gallery','Koppa Tengu','Koppa Tengu'))
        self.assertFalse(b.enemies[2].alive)
        self.assertTrue(b.enemies[1].alive)
        self.assertFalse(b.actions('contract'))


if __name__=='__main__':
    unittest.main()
