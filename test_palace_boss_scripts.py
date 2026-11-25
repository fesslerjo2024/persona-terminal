"""Integration tests: actual Testing battle commands, no game save or UI assumptions."""
import unittest

from campaign_combat import build_stage
from campaign_state import TestingCampaign
from depths_boss import ARM_NAMES
from lab_boss import AZATHOTH

SQUAD = ('Mona', 'Queen', 'Noir')


class ScriptedPalaceBossTests(unittest.TestCase):
    def battle(self, node, seed=25, squad=SQUAD):
        c = TestingCampaign()
        self.assertTrue(c.equip_squad(squad))
        return build_stage(c, node, seed=seed)

    def until(self, b, predicate, *, action=None, limit=28):
        for _ in range(limit):
            if predicate():
                return
            self.assertEqual(b.phase, 'turn')
            if action:
                action()
            else:
                self.assertIsNone(b.act('guard'))
        self.assertTrue(predicate(), (b.story_intent, b.log[-20:]))

    def test_sae_requires_observation_and_does_not_spend_resources(self):
        b = self.battle('casino-heist')
        sae = b.enemies[0]
        actor = b.actor
        before = actor.ammo, actor.sp, actor.hp, b.cursor, sae.hp
        self.assertIn('rigged wheel', b.act('gun', sae))
        self.assertEqual(before, (actor.ammo, actor.sp, actor.hp, b.cursor, sae.hp))
        self.assertFalse(b.actions('story-special'))
        self.until(b, lambda: b.actions('story-special'))
        self.assertIn('GLASS LID', b.story_intent)
        self.assertEqual(b.actions('story-special')[0][1], 'Snipe the Glass')
        shooter = b.actor
        self.assertIsNone(b.act('story-special'))
        self.assertTrue(b._boss_state['sae_open'])
        self.assertIsNot(b.actor, shooter)
        self.assertFalse(b.actions('story-special'))
        self.assertTrue(any(shooter.name + ' shatters' in x for x in b.log))

    def test_sae_skipped_clue_recovers_and_dance_resolves(self):
        outcomes = []
        for d in ('guard', 'unprepared'):
            b = self.battle('casino-heist')
            self.until(b, lambda: b._boss_state.get('sae_open'))
            self.assertTrue(any('takes the wager' in x for x in b.log))
            self.assertTrue(all(x.alive for x in b.allies))
            b.enemies[0].hp //= 2
            self.until(b, lambda: 'BERSERKER DANCE' in b.story_intent)
            before = sum(x.hp for x in b.allies)
            self.until(b, lambda: any('→ Berserker Dance.' in x for x in b.log),
                       action=(lambda: b.act('guard')) if d == 'guard' else b._advance)
            # Damage events measure the strike itself; Moral Support may also
            # restore HP on the same advance.
            outcomes.append(sum(prev-new for _, prev, new in b.damage_events)
                            if d == 'guard' else before-sum(x.hp for x in b.allies))
        self.assertGreater(outcomes[0], 0)
        self.assertLess(outcomes[0], .68*outcomes[1])

    def test_grail_healing_cannot_be_bypassed_and_satanael_finishes(self):
        for seed in range(8):
            with self.subTest(seed=seed):
                b = self.battle('depths-yaldabaoth', seed)
                grail = b.enemies[0]
                grail.hp = 1
                self.until(b, lambda: b.actions('story-special'),
                           action=lambda: b.act('attack', grail))
                self.assertEqual(b.wave, 1)
                self.assertTrue(grail.alive)
                self.assertEqual(b.actions('story-special')[0][1], 'Cut Supply Lines')
                self.assertIsNone(b.act('story-special'))
                self.assertFalse(b.actions('story-special'))
                grail.hp = 1
                self.until(b, lambda: b.wave == 2, action=lambda: b.act('attack', grail))
                body, *arms = b.enemies
                self.assertTrue(all(a in b.order for a in arms))
                self.assertEqual(b.visible_enemies, [body, *(a for a in arms if a.alive)])
                self.until(b, lambda: any(a.alive for a in arms))
                self.assertEqual([u.name for u in b.visible_enemies if u is not body],
                                 [ARM_NAMES[0]])
                body.hp = 1

                self.until(b, lambda: b._boss_state.get('finisher_ready'),
                           action=lambda: b.act('attack', body))
                self.assertEqual(b.phase, 'turn')
                self.assertIn('THE CITY CHEERS', b.story_intent)
                self.assertTrue(any('Over the radio' in line for line in b.log))
                if b.actor is not b.allies[0]:
                    self.assertFalse(b.actions('story-special'))
                self.until(b, lambda: b.actions('story-special'))
                self.assertIs(b.actor, b.allies[0])
                self.assertEqual(b.actions('story-special')[0][1], 'Sinful Shell')
                self.assertTrue(all(not a.alive for a in arms))
                self.assertIsNone(b.act('story-special'))
                self.assertEqual(b.phase, 'win')
                self.assertEqual(b.cut_in.title, 'SINFUL SHELL')
                self.assertTrue(b.cut_in.finishing)

    def test_laboratory_protection_affinity_rotation_and_rule(self):
        b = self.battle('laboratory-choice', seed=8)
        protection, assistance, healing, core = b.enemies
        self.assertEqual(core.behavior, AZATHOTH)
        self.assertIn('SHIELD TENDRIL', b.story_intent)
        self.assertIsNone(b.act('attack', core))
        self.assertEqual(core.hp, core.max_hp)
        protection.hp = 0
        b.seen[assistance.name] = {'Fire': 'weak'}
        core.hp = core.max_hp // 3
        self.until(b, lambda: b._boss_state.get('lab_shift'))
        self.assertNotIn(assistance.name, b.seen)
        self.assertTrue(protection.alive)
        self.assertIn('TYRANT STANCE', b.story_intent)
        self.until(b, lambda: b._boss_state.get('lab_no_baton'))
        self.assertIn('No Baton Pass', b.story_intent)
        b.one_more = True
        receiver = next(u for u in b.allies if u is not b.actor and u.alive)
        self.assertFalse(b.actions('baton'))
        self.assertIn('forbids Baton Pass', b.act(f'pass:{receiver.name}'))
        self.assertTrue(b.one_more)
        self.until(b, lambda: not b._boss_state.get('lab_no_baton'))
        self.assertTrue(b._boss_state['lab_rule_spent'])

    def test_fused_adam_cannot_be_burst_and_requires_coordinated_guard(self):
        b = self.battle('laboratory-choice', seed=2)
        b.wave = 3
        b._spawn()
        b._advance()
        fused = b.enemies[0]
        before = fused.hp
        self.assertIsNone(b.act('attack', fused))
        self.assertEqual(fused.hp, before)
        self.until(b, lambda: b._boss_state.get('lab_pending'))
        b._advance()  # Simulate an unguarded action; battle must remain recoverable.
        self.until(b, lambda: any('defense scatters' in x for x in b.log),
                   action=b._advance)
        self.assertEqual(b.phase, 'turn')
        self.until(b, lambda: b.actions('story-special'))
        self.assertEqual(b.actor.name, 'Joker')
        self.assertEqual(b.actions('story-special')[0][1], 'Take the Shot')
        self.assertIsNone(b.act('story-special'))
        self.assertEqual(b.phase, 'win')

    def test_violet_pair_unlock_only_on_late_laboratory_operations(self):
        pair = frozenset(('Joker', 'Violet'))
        from campaign_data import NODES
        eligible = {n['id'] for n in NODES
                    if pair in map(frozenset, n.get('showtime_pairs', ()))}
        self.assertEqual(eligible, {'laboratory-colors', 'laboratory-choice'})
        b = self.battle('laboratory-colors', seed=3, squad=('Mona', 'Queen', 'Violet'))
        b.actor = b.allies[0]
        class Roll:
            def random(self): return 0.0
            def choice(self, options): return options[-1]
        b._showtime_rng = Roll()
        b._offer_showtime(baton=True)
        self.assertEqual(frozenset(b._showtime), pair)
        self.assertIsNone(b.act('showtime', b.enemies[0]))
        self.assertTrue(any('Joker × Violet' in x for x in b.log))


if __name__ == '__main__':
    unittest.main()
