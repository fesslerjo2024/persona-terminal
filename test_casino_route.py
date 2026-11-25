"""Sae's Casino route gates must run before advancing or saving."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from battle_ui import ESC
from campaign_combat import build_stage
from campaign_data import NODES
from campaign_state import Campaign, TestingCampaign
from casino_route import CasinoRoute, REGISTRATION_COINS, SLOT_COST, JACKPOT, CARD_COST
from test_animation_gallery import Surface
from weekend_bosses import enemy_step


def at_casino(path):
    c=Campaign(path)
    c.new_game()
    for node in NODES:
        if node['id']=='casino-service':
            break
        c.clear(node['id'])
    return c


class CasinoRouteTests(TestCase):
    def test_slot_controls_can_be_done_either_order_and_payout_is_one_time(self):
        for order in (('green','red'),('red','green')):
            with self.subTest(order=order):
                c=CasinoRoute()
                c.open('dice')
                self.assertFalse(c.choose('play_dice'))
                self.assertEqual(c.coins,REGISTRATION_COINS)
                self.assertFalse(c.choose('leave_dice'))
                c.choose('override_dice');c.choose('play_dice')
                opening=c.coins
                self.assertGreaterEqual(opening,SLOT_COST)
                c.choose('play_dice')
                self.assertEqual(c.coins,opening)
                self.assertTrue(c.choose('leave_dice'))
                c.open('slots')
                for blocked in ('red','green','spin','exchange'):
                    self.assertFalse(c.choose(blocked))
                c.choose('scan');c.choose(order[0]);c.choose('spin')
                self.assertFalse(c.jackpot)
                self.assertEqual(c.coins,opening)
                c.choose(order[1]);c.choose('spin');c.choose('spin')
                self.assertTrue(c.jackpot)
                self.assertEqual(c.coins,opening+JACKPOT-SLOT_COST)
                self.assertTrue(c.choose('exchange'))
                self.assertFalse(c.choose('exchange'))
                self.assertEqual(c.coins,opening+JACKPOT-SLOT_COST-CARD_COST)

    def test_through_story_title_map_battle_and_card_only_then_clear(self):
        with TemporaryDirectory() as d:
            path=Path(d)/'fixture.json'
            c=at_casino(path)
            c.clear('casino-service')
            app=Surface(c)
            before=c.data
            app.key('1')
            self.assertEqual(app.label(),'CASINO')
            app.key('2');app.key('\n')
            b=app._b_battle
            self.assertEqual((b.phase,b.wave),('turn',1))
            # Isolate resource preservation from a possible random enemy
            # opener on wave two. The production battle still shuffles.
            b.shuffle_turns=False
            joker=b.allies[0]
            joker.hp-=20;joker.sp-=10
            tracked_stats=(joker.hp,joker.sp)
            b.items['Medicine']-=1
            original=path.read_bytes()

            def knock_out_foes_and_open_route():
                for foe in b.enemies:b._hurt(foe,foe.hp)
                b._state()
                self.assertIsNotNone(b.act('guard'))  # no actions inside breaks
                with patch.object(app,'_b_result_animation',return_value=False):
                    app.draw_combat()
                self.assertEqual(app.page,'casino-route')
                self.assertEqual(path.read_bytes(),original)

            knock_out_foes_and_open_route()
            self.assertEqual(app.casino_route.stage,'dice')
            app.key('2');app.key('3')
            self.assertEqual(b.wave,1)
            app.key(ESC);app.key(ESC)
            self.assertFalse(app.casino_route.leaving)
            for key in ('1','2','3'):app.key(key)
            self.assertEqual((b.phase,b.wave),('turn',2))
            self.assertEqual((joker.hp,joker.sp),tracked_stats)
            self.assertEqual(b.items['Medicine'],2)
            with self.assertRaises(ValueError):b.resume_wave()
            knock_out_foes_and_open_route()
            self.assertEqual(app.casino_route.stage,'slots')
            for key in ('1','2','4','5'):app.key(key)
            self.assertEqual((b.phase,b.wave),('interlude',2))
            self.assertFalse(c.can_play('casino-darkness'))
            self.assertEqual(path.read_bytes(),original)
            app.key('3');app.key('4')
            app.out.clear();app.draw_casino_route()
            self.assertIn('[ 7 ]   [ 7 ]   [ 7 ]',app.out)
            self.assertEqual(path.read_bytes(),original)
            app.key('5')
            self.assertEqual(b.phase,'win')
            loaded=Campaign(path)
            self.assertIn('casino-rigging',loaded.data['cleared'])
            self.assertEqual(loaded.next_node,'casino-darkness')
            self.assertEqual(loaded.data['credits']-before['credits'],400)
            self.assertEqual(set(loaded.data),set(before))

    def test_confirming_escape_abandons_without_writing_or_unlocking(self):
        with TemporaryDirectory() as d:
            path=Path(d)/'fixture.json'
            c=at_casino(path)
            c.clear('casino-service');c.clear('casino-rigging')
            original=path.read_bytes()
            a=Surface(c);a.key('1');a.key('3');a.key('\n')
            b=a._b_battle
            for foe in b.enemies:b._hurt(foe,foe.hp)
            b._state()
            a.draw_combat()
            a.key('2');a.key('3')
            self.assertFalse(a.casino_route.through_vent)
            a.key('1');a.key('2');a.key(ESC);a.key('\n')
            self.assertEqual(a.page,'map')
            self.assertIsNone(a.casino_route)
            self.assertEqual(path.read_bytes(),original)
            self.assertFalse(c.can_play('casino-arena'))

    def test_darkness_exit_and_snake_king_charge(self):
        c=CasinoRoute();c.open('darkness')
        self.assertFalse(c.choose('exit'));self.assertFalse(c.choose('vent'))
        self.assertFalse(c.choose('door'));self.assertFalse(c.choose('vent'))
        self.assertTrue(c.choose('exit'))
        b=build_stage(TestingCampaign(),'casino-darkness',seed=1)
        for foe in b.enemies:foe.hp=0
        b._state();b.resume_wave()
        snake=b.enemies[0]
        self.assertEqual(snake.name,'Snake King')
        self.assertFalse(any(v=='weak' for v in snake.affinity.values()))
        snake.hp=snake.max_hp//2
        b._boss_state['snake_turn']=2
        enemy_step(b,snake)
        self.assertIn('CONCENTRATE',b.story_intent)
        self.assertIn('MAZIONGA',b.story_intent)
        for ally in b.allies:ally.guard=True
        b._boss_state['pending'].clear()
        enemy_step(b,snake)
        self.assertNotIn('CONCENTRATE',b.story_intent)
        self.assertTrue(any('Charged Mazionga' in line for line in b.log))
