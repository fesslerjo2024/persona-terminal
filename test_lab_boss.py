"""Focused integration tests for the laboratory finale. No save access."""
import unittest

from battle_engine import Battle
from campaign_combat import build_stage
from campaign_state import TestingCampaign
from lab_boss import (AFFINITIES, ASSISTANCE, AZATHOTH, ENEMY_ADDITIONS, FUSED,
                      HEALING, PROTECTION, WAVES)


def run(waves, *, shuffle=False, seed=2):
    return Battle(('Skull', 'Mona', 'Queen'), 'Laboratory fight', seed=seed,
                  shuffle_turns=shuffle,
                  encounter_config={'id': 'laboratory-choice', 'waves': waves},
                  enemy_data=ENEMY_ADDITIONS)


def reach_tyrant_stance(test):
    b = build_stage(TestingCampaign(), 'laboratory-choice', seed=1)
    core = next(u for u in b.enemies if u.behavior == AZATHOTH)
    guard = next(u for u in b.enemies if u.behavior == PROTECTION)
    test.assertEqual(b.actor.name, 'Joker')
    for aid, target in (('skill:Cleave', guard), ('skill:Eiga', core),
                        ('skill:Mazionga', None), ('skill:Tempest Slash', core),
                        ('skill:Garula', core)):
        test.assertFalse(b.story_intent.startswith('TYRANT STANCE'))
        test.assertIsNone(b.act(aid, target))
    test.assertTrue(b._boss_state.get('lab_shift'))
    test.assertEqual(b.story_intent, 'TYRANT STANCE / Guard before Tyrant Chaos.')
    test.assertFalse(any('→ Tyrant Chaos.' in line for line in b.log))
    return b, core


class LabBossTests(unittest.TestCase):
    def test_roles_have_distinct_effects(self):
        b = run(WAVES)
        t = {u.behavior: u for u in b.enemies}
        core, defender = t[AZATHOTH], t[PROTECTION]
        full = core.hp
        b._execute(b.allies[0], b._spec('attack'), core, 'Attack')
        self.assertEqual(core.hp, full)
        defender.down = True
        b._execute(b.allies[0], dict(b._spec('attack'), accuracy=100), core, 'Attack')
        self.assertLess(core.hp, full)
        injured = core.hp
        b._enemy_step(t[HEALING])
        self.assertGreater(core.hp, injured)
        b._enemy_step(t[ASSISTANCE])
        self.assertEqual(core.buffs['attack'][0], 1)
        self.assertEqual(defender.affinity, AFFINITIES[0])

    def test_single_regrowth_resets_only_tendril_intel(self):
        b = run(WAVES)
        defender = next(u for u in b.enemies if u.behavior == PROTECTION)
        core = next(u for u in b.enemies if u.behavior == AZATHOTH)
        b.seen = {defender.name: {'Physical': 'weak'}, core.name: {'Ice': 'normal'}}
        defender.hp = 0
        core.hp = core.max_hp // 2
        b._enemy_step(core)
        self.assertEqual(defender.hp, defender.max_hp // 2)
        self.assertEqual(defender.affinity, AFFINITIES[1])
        self.assertNotIn(defender.name, b.seen)
        self.assertIn(core.name, b.seen)
        defender.hp = 0
        b._enemy_step(core)
        self.assertFalse(defender.alive)
        core.hp = 0
        self.assertTrue(b._state())
        self.assertEqual(b.wave, 2)

    def test_stance_gives_every_scheduled_ally_a_response_and_guard_reduces_damage(self):
        def respond(guarding):
            b, core = reach_tyrant_stance(self)
            who = set()
            hp = {u.name: u.hp for u in b.allies}
            # Non-Guard choices don't consume RNG or alter defenses for comparison.
            without_guard = {
                'Joker': ('skill:Rakunda', core),
                'Skull': ('skill:Tarukaja', next(u for u in b.allies if u.name == 'Skull')),
                'Mona': ('skill:Sukunda', next(u for u in b.enemies if u.behavior == PROTECTION)),
            }
            for _ in b.allies:
                who.add(b.actor.name)
                self.assertTrue(b.story_intent.startswith('TYRANT STANCE'))
                aid, target = ('guard', None) if guarding else without_guard[b.actor.name]
                self.assertIsNone(b.act(aid, target))
            self.assertEqual(who, set(hp))
            self.assertFalse(b._boss_state.get('lab_charge'))
            self.assertEqual(sum('→ Tyrant Chaos.' in line for line in b.log), 1)
            return sum(hp[u.name] - u.hp for u in b.allies)

        guarded, exposed = respond(True), respond(False)
        self.assertGreater(guarded, 0)
        self.assertLess(guarded, exposed)

    def test_late_stance_leaves_two_normal_attacks_between_charges(self):
        b, core = reach_tyrant_stance(self)
        for _ in b.allies:
            self.assertIsNone(b.act('guard'))
        self.assertFalse(b._boss_state.get('lab_charge'))
        for _ in range(2):
            b._enemy_step(core)
            self.assertFalse(b._boss_state.get('lab_charge'))
        b._enemy_step(core)
        self.assertTrue(b._boss_state.get('lab_charge'))
        self.assertEqual(b._boss_state['pending'], {u for u in b.allies if u.alive})

    def test_azathoth_defeat_cancels_armed_chaos(self):
        b, core = reach_tyrant_stance(self)
        # Build a lethal opening, then take the real strike without guarding.
        core.hp = 1
        next(u for u in b.enemies if u.behavior == PROTECTION).hp = 0
        self.assertIsNone(b.act('item:Molotov Cocktail', core))
        self.assertEqual(b.wave, 2)
        self.assertNotIn('lab_charge', b._boss_state)
        self.assertFalse(any('→ Tyrant Chaos.' in line for line in b.log))

    def test_guard_and_joker_finisher_survive_shuffled_initiative(self):
        for seed in range(16):
            with self.subTest(seed=seed):
                b = run(WAVES[-1:], shuffle=True, seed=seed)
                boss = b.enemies[0]
                self.assertEqual(boss.behavior, FUSED)
                self.assertFalse(b.actions('story-special'))
                hp = boss.hp
                b.act('attack', boss)
                self.assertEqual(boss.hp, hp)
                for _ in range(20):
                    if b.actions('story-special'):
                        self.assertEqual(b.actor.name, 'Joker')
                        self.assertIsNone(b.act('story-special'))
                        break
                    b.act('guard')
                self.assertEqual(b.phase, 'win')
                self.assertTrue(all(u.alive for u in b.allies))

    def test_incomplete_guard_retries_and_full_force_is_nonlethal(self):
        b = run(WAVES[-1:])
        boss = b.enemies[0]
        for _ in range(len(b.allies)):
            b.act('attack', boss)
        self.assertTrue(b._boss_state.get('lab_pending'))
        for u in b.allies:
            u.hp = 1
        for _ in range(len(b.allies)):
            b.act('attack', boss)
        self.assertFalse(b.actions('story-special'))
        self.assertTrue(all(u.hp == 1 for u in b.allies))
        b.allies[1].hp = 0  # Remaining standing allies can still hold the fist.
        for _ in range(len(b.allies) - 1):
            b.act('guard')
        self.assertTrue(b.actions('story-special'))
        b.act('story-special')
        self.assertEqual(b.phase, 'win')


if __name__ == '__main__':
    unittest.main()
