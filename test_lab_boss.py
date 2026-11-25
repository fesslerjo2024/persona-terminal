"""Focused integration tests for the laboratory finale. No save access."""
import unittest

from battle_engine import Battle
from lab_boss import (AFFINITIES, ASSISTANCE, AZATHOTH, ENEMY_ADDITIONS, FUSED,
                      HEALING, PROTECTION, WAVES)


def run(waves, *, shuffle=False, seed=2):
    return Battle(('Skull', 'Mona', 'Queen'), 'Laboratory fight', seed=seed,
                  shuffle_turns=shuffle,
                  encounter_config={'id': 'laboratory-choice', 'waves': waves},
                  enemy_data=ENEMY_ADDITIONS)


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
