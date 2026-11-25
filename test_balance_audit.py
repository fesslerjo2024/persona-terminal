"""Audit balance changes preserve real turn and save rules."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from battle_engine import Battle
from campaign_combat import build_stage, solo_readiness
from campaign_data import NODES
from campaign_state import Campaign, TestingCampaign
from test_animation_gallery import Surface


class SoloReadinessChecks(unittest.TestCase):
    def test_warning_is_based_on_equipped_masks_and_does_not_write_save(self):
        with TemporaryDirectory() as temp:
            path=Path(temp)/'disposable.json'
            store=Campaign(path)
            store.new_game()
            for n in NODES:
                if n['id']=='cruiser-duel':break
                store.clear(n['id'],'S')
            n=store.get_node('cruiser-duel')
            self.assertIn('Ice',solo_readiness(store,n))
            app=Surface(store);app.key('1');app.node=n
            self.assertEqual(app.label(),'CRUISER')
            before=path.read_bytes()
            app.brief()
            self.assertTrue(any('weak to Ice' in line for line in app.out))
            self.assertEqual(path.read_bytes(),before)
            store.equip_personas(('Shiki-Ouji','High Pixie'),'Shiki-Ouji')
            self.assertEqual(solo_readiness(store,n),'')
            self.assertEqual(solo_readiness(store,store.get_node('cruiser-sacrifice')),'')

    def test_guard_turn_opens_shido_instead_of_consuming_two_casts(self):
        store=TestingCampaign()
        b=build_stage(store,'cruiser-duel',seed=13)
        joker=b.allies[0]
        shido=b.enemies[0]
        self.assertFalse(joker.guard)
        self.assertAlmostEqual(shido.max_hp,440*.72,delta=.5)
        self.assertIn('Physical attack next',b.story_intent)
        self.assertIsNone(b.act('guard'))
        self.assertIn('SHIDO READIES',b.story_intent)
        self.assertIsNone(b.act('guard'))
        self.assertIn('SHIDO IS OPEN',b.story_intent)
        self.assertEqual(shido.buffs['defense'],(-1,1))
        before=joker.hp
        self.assertIsNone(b.act('attack',shido))
        self.assertEqual(joker.hp,before)
        self.assertIn('SHIDO READIES',b.story_intent)
        self.assertFalse(b.one_more)

    def test_unguarded_weakness_one_more_has_a_different_followup(self):
        store=TestingCampaign()
        for seed in range(100):
            b=build_stage(store,'cruiser-duel',seed=seed)
            shido=b.enemies[0]
            b.act('attack',shido)
            if 'READIES ICE' not in b.story_intent:continue
            log=len(b.log)
            b.act('attack',shido)
            latest=b.log[log:]
            if not any('Shido Final Duel gets One More!' in s for s in latest):continue
            self.assertEqual(sum(s=='Shido Final Duel → Bufula.' for s in latest),1)
            self.assertEqual(sum(s=='Shido Final Duel → Rising Slash.' for s in latest),1)
            break
        else:
            self.fail('Expected a real weak hit and One More in this seeded set.')


class TrialRecoveryChecks(unittest.TestCase):
    def _after_transition(self, trial, difficulty):
        b=Battle(('Mona','Queen','Fox'),trial,difficulty,seed=4)
        joker,mona=b.allies[:2]
        joker.hp=100;joker.sp=12;mona.hp=0
        b.wave=2;b._spawn()
        self.assertEqual(mona.hp,0)
        return joker.hp,joker.sp

    def test_configured_classic_break_heals_standing_fighters_only(self):
        self.assertEqual(self._after_transition('Wardens’ Examination','Normal'),(145,20))
        self.assertEqual(self._after_transition('Wardens’ Examination','Hard'),(131,18))
        self.assertEqual(self._after_transition('Wardens’ Examination','Merciless'),(120,16))
        self.assertEqual(self._after_transition('Castle Downfall','Normal'),(100,12))

    def test_solo_rehearsal_has_distinct_rounds_and_same_rules(self):
        b=Battle((),'Wild Card: Joker Solo',seed=6)
        self.assertEqual([u.name for u in b.allies],['Joker'])
        self.assertEqual(b.wave_count,3)
        self.assertTrue(all(len(wave)==1 for wave in b.waves))
        self.assertFalse(b.actions('baton'))
        self.assertFalse(b.actions('allout'))
