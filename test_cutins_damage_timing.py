from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch

from battle_ui import DIM, HP_DRAIN, HP_FLASH, HP_SETTLE, RED
from campaign import CampaignApp
from campaign_state import Campaign, TestingCampaign


class CutInDamageTiming(TestCase):
    def test_finishing_cut_in_shows_damage_when_skipped_or_completed(self):
        for skip in ('\r','\x1b',None):
            with self.subTest(skip=skip), TemporaryDirectory() as d:
                path=Path(d)/'story.json'
                store=Campaign(path)
                store.new_game()
                opening_credits=store.data['credits']
                app=CampaignApp(None,store,seed=4)
                app.node=app.by_id['castle-gate']
                app.stage()
                app.put=Mock()
                app._b_arena=Mock()
                app.result=Mock()
                foe=app._b_battle.enemies[0]
                foe.down=True
                app._b_battle.one_more=True
                with patch('battle_ui.time.monotonic',return_value=10):
                    app._b_apply('allout')
                    app.record()
                    self.assertEqual(app._b_battle.phase,'win')
                    self.assertFalse(app._b_hp_trails)
                    self.assertIsNotNone(app._b_cut_damage)
                    app.key('7')
                    self.assertIsNotNone(app._b_cut_in)
                first_clear=path.read_bytes()
                start=10.12 if skip else 10.63
                with patch('battle_ui.time.monotonic',return_value=start):
                    if skip:app.key(skip)
                    else:app.battle_page()
                    self.assertIsNone(app._b_cut_in)
                    self.assertIsNone(app._b_cut_damage)
                    self.assertEqual(app._b_hp_trails[foe][1],start)
                    self.assertTrue(app._b_result_animation(start))
                    app._b_hp_draw(0,0,foe,5,start)
                    self.assertTrue(any(c.args[2]=='▓'*5 and c.args[3]==RED
                                        for c in app.put.call_args_list))
                with patch('battle_ui.time.monotonic',return_value=start+HP_FLASH+HP_DRAIN+.02):
                    self.assertEqual(app.page,'battle')
                    self.assertTrue(app._b_result_animation(start+HP_FLASH+HP_DRAIN+.02))
                    app._b_hp_draw(0,0,foe,5,start+HP_FLASH+HP_DRAIN+.02)
                    self.assertTrue(any(c.args[2]=='░'*5 and c.args[3]==DIM
                                        for c in app.put.call_args_list))
                with patch('battle_ui.time.monotonic',return_value=start+HP_FLASH+HP_DRAIN+HP_SETTLE+.02):
                    app.draw_combat()
                    self.assertEqual(app.page,'result')
                    self.assertTrue(app.result.called)
                    self.assertEqual(path.read_bytes(),first_clear)
                    self.assertEqual(store.data['credits'],opening_credits+app.node['reward']['credits'])

    def test_next_wave_waits_for_departing_foes_bar(self):
        store=TestingCampaign()
        app=CampaignApp(None,store,seed=4)
        app.node=app.by_id['treasure-route']
        app.testing=True
        app.stage()
        foes=tuple(app._b_battle.visible_enemies)
        for foe in foes:
            foe.down=True
            foe.hp=1
        app._b_battle.one_more=True
        with patch('battle_ui.time.monotonic',return_value=10):
            app._b_apply('allout')
            self.assertEqual(app._b_battle.wave,2)
            self.assertIsNone(app._b_outgoing)
        with patch('battle_ui.time.monotonic',return_value=10.15):
            app.key('\r')
            wave,former,until=app._b_outgoing
            self.assertEqual(wave,1)
            self.assertEqual(tuple(former),foes)
            self.assertAlmostEqual(until,10.15+HP_FLASH+HP_DRAIN+HP_SETTLE)
            self.assertTrue(all(app._b_hp_trails[u]==(1,10.15) for u in foes))
            self.assertTrue(app.key('4')) # Does not Guard on the incoming formation.
            self.assertFalse(any(u.guard for u in app._b_battle.allies))
