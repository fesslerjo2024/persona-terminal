"""Isolated boss controller checks (no campaign save or UI)."""
import unittest
from copy import deepcopy
from types import SimpleNamespace

import depths_boss as d
from battle_engine import _unit
from battle_data import TEAM


class LaboratoryBattle:
    def __init__(self, wave_index):
        self.enemies = [_unit(n,deepcopy(d.ENEMY_ADDITIONS[n]),True)
                        for n in d.DEPTHS_FINAL_WAVES[wave_index]]
        self.allies = [_unit('Mona',TEAM['Mona']),_unit('Queen',TEAM['Queen'])]
        self.actor = self.allies[0]
        self.phase = 'turn'
        self.round = 1
        self._boss_state = {}
        self.log = []
        self.attacks = []
        self.advances = 0
        d.on_spawn(self)

    def _say(self, message): self.log.append(message)
    def _hurt(self, unit, amount): unit.hp = max(0,unit.hp-amount)
    def _execute(self, actor, skill, target, name):
        self.attacks.append((name,skill,target))
        return False
    def _state(self):
        d.before_state(self)
        if not any(x.alive for x in self.enemies): self.phase='win'
    def _advance(self): self.advances += 1


class DepthsBossTest(unittest.TestCase):
    def test_grail_heals_then_supply_line_special_disables_healing(self):
        battle = LaboratoryBattle(0)
        grail = battle.enemies[0]
        grail.hp -= 200
        self.assertIsNone(d.special(battle))
        d.enemy_step(battle,grail)
        self.assertEqual(grail.hp,grail.max_hp-115)
        self.assertEqual(d.special(battle)[1],'Cut Supply Lines')
        self.assertIsNone(d.use_special(battle))
        self.assertEqual(battle.advances,1)
        self.assertIsNone(d.special(battle))
        d.enemy_step(battle,grail)
        self.assertEqual(grail.hp,grail.max_hp-115)
        self.assertEqual(battle.attacks[-1][0],'Eternal Light')
        grail.hp=0
        battle._state()
        self.assertEqual(battle.phase,'win')

    def test_grail_cannot_be_burst_past_supply_line_phase(self):
        battle = LaboratoryBattle(0)
        grail = battle.enemies[0]
        grail.hp=0
        battle._state()
        self.assertGreater(grail.hp,0)
        self.assertEqual(battle.phase,'turn')
        self.assertEqual(d.special(battle)[1],'Cut Supply Lines')

    def test_arms_manifest_one_at_a_time_then_revive_once(self):
        battle = LaboratoryBattle(1)
        body,*arms=battle.enemies
        self.assertTrue(all(not arm.alive for arm in arms))
        self.assertEqual(d.hidden_enemies(battle),tuple(arms))
        for i in range(4):
            d.enemy_step(battle,body)
            self.assertEqual(sum(arm.alive for arm in arms),i+1)
            self.assertEqual(d.hidden_enemies(battle),tuple(arms[i+1:]))
            self.assertIs(battle.enemies[i+1],arms[i])
            battle.round+=1
        arms[0].hp=0
        d.enemy_step(battle,body)
        d.on_round(battle)
        self.assertFalse(arms[0].alive)
        self.assertIn('ARM RETURN',d.intent(battle))
        battle.round+=1
        d.on_round(battle)
        self.assertEqual(arms[0].hp,arms[0].max_hp//2)
        n=len(battle.attacks)
        d.enemy_step(battle,arms[0])
        self.assertEqual(len(battle.attacks),n)
        arms[0].hp=0
        d.enemy_step(battle,body)
        battle.round+=1
        d.on_round(battle)
        self.assertFalse(arms[0].alive)

    def test_apex_waits_and_rewards_arm_suppression(self):
        def power(suppress):
            battle=LaboratoryBattle(1)
            body,*arms=battle.enemies
            for _ in range(3):
                d.enemy_step(battle,body)
                battle.round+=1
            body.hp=body.max_hp//2
            d.enemy_step(battle,body)
            self.assertIn('DIVINE APEX',d.intent(battle))
            n=len(battle.attacks)
            d.enemy_step(battle,body)
            self.assertEqual(len(battle.attacks),n)
            if suppress: arms[1].hp=0
            battle.round+=1
            d.enemy_step(battle,body)
            name,spec,_=battle.attacks[-1]
            self.assertEqual(name,'Rays of Control')
            self.assertEqual(spec['target'],'enemies')
            return spec['power']
        self.assertEqual(power(False)-power(True),9)

    def test_finisher_cancels_all_remaining_enemy_actions(self):
        battle=LaboratoryBattle(1)
        body,*arms=battle.enemies
        d.enemy_step(battle,body)
        body.hp=0
        battle._state()
        self.assertEqual(battle.phase,'turn')
        self.assertTrue(all(not arm.alive for arm in arms))
        self.assertTrue(d.block_hit(battle,body,{}))
        n=len(battle.attacks)
        d.enemy_step(battle,body)
        self.assertEqual(len(battle.attacks),n)
        self.assertEqual(d.special(battle)[1],'Sinful Shell')
        self.assertIsNone(d.use_special(battle))
        self.assertEqual(battle.phase,'win')
        self.assertFalse(body.alive)
        self.assertIsNone(d.special(battle))

    def test_hooks_ignore_unrelated_waves(self):
        other=SimpleNamespace(enemies=[],_boss_state={},round=2,phase='turn',actor=None)
        d.on_spawn(other);d.on_round(other);d.before_state(other)
        self.assertEqual(d.intent(other),'')
        self.assertIsNone(d.special(other))
        self.assertIsNone(d.enemy_step(other,SimpleNamespace(behavior='misc')))


if __name__=='__main__': unittest.main()
