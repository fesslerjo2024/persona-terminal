"""Isolated Shido tests using the real combat engine and scoped boss hooks."""
from unittest import TestCase
from unittest.mock import patch
from battle_data import PERSONAS, shadow
from battle_engine import Battle
import shido_boss
import weekend_bosses


class ShidoBossTests(TestCase):
    def setUp(self):
        hooks={name:getattr(shido_boss,name) for name in ('enemy_step','intent','block_hit')}
        p=patch.multiple(weekend_bosses, **hooks)
        p.start()
        self.addCleanup(p.stop)

    def battle(self, tag, squad=('Mona','Skull','Panther')):
        key='Shido'
        b=Battle(squad,'Shido Test',seed=8,shuffle_turns=False,
                 joker_stats={'hp':255,'sp':84},persona_pool=PERSONAS,
                 encounter_config={'id':'shido-test','waves':[[key]],'party_size':len(squad)+1},
                 enemy_data={key:shadow(shido_boss.FORM_HP[tag],80,[],{},tag,no_knockdown=True)})
        return b,b.enemies[0]

    def cycle_guard(self,b):
        starting_round=b.round
        for _ in range(30):
            self.assertIsNone(b.act('guard'))
            if b.round!=starting_round:
                return
        self.fail('Combat did not advance to its next round')

    def test_beast_reflects_first_hit_before_any_boss_turn(self):
        b,beast=self.battle('cruiser-beast')
        before=b.allies[0].hp
        b.rng.randrange=lambda n:5
        b.act('attack',beast)
        self.assertEqual(beast.hp,beast.max_hp)
        self.assertLess(b.allies[0].hp,before)
        self.assertEqual(b.seen['Shido']['Physical'],'repel')

    def test_install_profiles_keep_native_element_analysis(self):
        b,wings=self.battle('cruiser-wings')
        shido_boss.prepare(b)
        self.assertEqual(wings.affinity,dict.fromkeys(shido_boss.ELEMENTS,'resist'))
        b.rng.randrange=lambda n:50
        self.assertIsNone(b.act('skill:Agilao',wings,persona='Orthrus'))
        self.assertEqual(b.seen['Shido']['Fire'],'resist')
        self.assertGreater(wings.hp,wings.max_hp-40)
        b,tomb=self.battle('cruiser-tomb')
        shido_boss.prepare(b)
        self.assertEqual(tomb.affinity,{'Gun':'resist'})

    def test_distinct_charge_and_real_guard_window(self):
        expected={'cruiser-beast':'Beast King’s Wrath','cruiser-wings':'Royal Wing Beam',
                  'cruiser-tomb':'Pyramid Blast','cruiser-samael':'Tyrant’s Purge'}
        for tag,move in expected.items():
            with self.subTest(tag=tag):
                b,boss=self.battle(tag)
                for _ in range(4):
                    self.cycle_guard(b)
                    if 'shido_charge' in b._boss_state:break
                self.assertIn(move.upper(),b.story_intent)
                self.assertEqual(b._boss_state['shido_charge'][0],move)
                # Joker just got a selectable slot; other allies still need theirs.
                self.assertEqual(b._boss_state['pending'],set(b.allies[1:]))
                before=[u.hp for u in b.allies]
                shido_boss.enemy_step(b,boss)
                self.assertEqual(before,[u.hp for u in b.allies])
                if tag=='cruiser-samael':
                    self.assertNotEqual(b._boss_state['shido_charge'][-1].name,'Joker')
                self.cycle_guard(b)
                self.assertNotIn('shido_charge',b._boss_state)
                self.assertTrue(any(u.hp<hp for u,hp in zip(b.allies,before)))
                self.assertLessEqual(max(hp-u.hp for u,hp in zip(b.allies,before)),40)
                self.assertNotIn('Shido gets One More!',b.log)

    def test_freeze_skips_a_slot_not_the_charge_guard_opportunity(self):
        b,_=self.battle('cruiser-tomb')
        self.cycle_guard(b)
        self.cycle_guard(b)
        skull=b.allies[2]
        skull.status='freeze';skull.status_turns=1
        self.cycle_guard(b)
        self.assertIn(skull,b._boss_state['pending'])
        self.assertIn('PYRAMID BLAST',b.story_intent)
        self.cycle_guard(b)
        self.assertNotIn('shido_charge',b._boss_state)

    def test_duel_is_solo_and_announced_element_allows_persona_response(self):
        b,boss=self.battle('cruiser-duel',())
        self.assertEqual([u.name for u in b.allies],['Joker'])
        self.assertLess(boss.hp,shido_boss.FORM_HP['cruiser-duel'])
        self.assertIsNone(b.act('guard'))
        self.assertIsNone(b.act('guard'))
        self.assertIn('INFERNO (Fire)',b.story_intent)
        self.assertFalse(b.actions('baton'))
        b.rng.randrange=lambda n:50
        old_joker=b.allies[0].hp
        old_boss=boss.hp
        self.assertIsNone(b.act('skill:Agilao',boss,persona='Orthrus'))
        self.assertGreaterEqual(b.allies[0].hp,old_joker)
        self.assertLess(boss.hp,old_boss)
        self.assertNotIn('shido_charge',b._boss_state)

    def test_intent_is_read_only_and_no_op_outside_shido(self):
        b,boss=self.battle('cruiser-duel',())
        snapshot=(b.rng.getstate(),b.round,b.actor,list(b.log),dict(b._boss_state))
        self.assertEqual(shido_boss.intent(b),shido_boss.intent(b))
        self.assertEqual(snapshot,(b.rng.getstate(),b.round,b.actor,b.log,b._boss_state))
        boss.behavior='other'
        self.assertEqual(shido_boss.intent(b),'')
        self.assertIsNone(shido_boss.enemy_step(b,boss))
        self.assertFalse(shido_boss.block_hit(b,boss,{'element':'Gun'}))
