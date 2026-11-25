"""The arena keeps Joker solo; the bridge interlude alone grants passage."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona5.campaign_combat import build_stage
from persona_terminal.persona5.campaign_state import Campaign, TestingCampaign
from persona_terminal.persona5.casino_route import CasinoRoute
from .test_casino_route import at_casino
from .test_animation_gallery import Surface


class ArenaAndBridgeTests(TestCase):
    def test_arena_roster_and_configured_recovery_do_not_reset_the_stock(self):
        b=build_stage(TestingCampaign(),'casino-arena',seed=8)
        self.assertEqual([u.name for u in b.allies],['Joker'])
        self.assertEqual(b.config['showtime_pairs'],())
        self.assertEqual(b.items['Stun Gun'],2)
        b.shuffle_turns=False
        j=b.allies[0]
        for species,count in (('Ganesha',2),('Rangda',3),('Thor',1)):
            self.assertEqual(len(b.enemies),count)
            self.assertTrue(all(u.name.startswith(f'Arena {species}') for u in b.enemies))
            j.hp-=125;j.sp-=12
            hp,sp=j.hp,j.sp
            for foe in b.enemies:foe.hp=0
            b.items['Medicine']-=1
            b._state()
            if species!='Thor':
                self.assertEqual(j.hp,min(j.max_hp,hp+round(j.max_hp*.26)))
                self.assertEqual(j.sp,min(j.max_sp,sp+8))
                self.assertEqual(b.phase,'turn')
        self.assertEqual(b.phase,'win')
        self.assertEqual(b.items['Medicine'],2)

    def test_bridge_order_must_be_followed_and_coins_cannot_be_duplicated(self):
        route=CasinoRoute()
        route.open('bridge')
        self.assertEqual(route.bridge_toll,100_000)
        self.assertFalse(route.choose('cross'))
        self.assertFalse(route.choose('spare'))
        self.assertFalse(route.choose('payout'))
        self.assertEqual(route.bridge_deposit,0)
        self.assertFalse(route.choose('prize'))
        self.assertEqual((route.bridge_deposit,route.bridge_toll),(100_000,1_000_000))
        self.assertFalse(route.choose('prize'))
        self.assertFalse(route.choose('spare'))
        self.assertFalse(route.choose('payout'))
        self.assertFalse(route.choose('payout'))
        self.assertEqual(route.bridge_deposit,550_000)
        self.assertFalse(route.choose('cross'))
        self.assertFalse(route.choose('spare'))
        self.assertFalse(route.choose('spare'))
        self.assertEqual(route.bridge_deposit,1_001_000)
        self.assertTrue(route.choose('cross'))

    def test_bridge_cancellation_and_completion_in_campaign_menu(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'fixture.json'
            c=at_casino(path)
            for id in ('casino-service','casino-rigging','casino-darkness','casino-arena'):
                c.clear(id)
            data=c.data
            before=path.read_bytes()
            app=Surface(c)
            app.key('1')
            def enter_bridge():
                app.key('5');app.key('\n')
                self.assertEqual(app.page,'battle')
                b=app._b_battle
                for foe in b.enemies:foe.hp=0
                b._state()
                with patch.object(app,'_b_result_animation',return_value=False):
                    app.draw_combat()
                self.assertEqual(app.page,'casino-route')
                return b
            enter_bridge()
            app.key('4')
            self.assertFalse(c.can_play('casino-heist'))
            app.key('1')
            app.key(ESC);app.key(ESC)
            self.assertEqual(app.casino_route.bridge_deposit,100_000)
            app.key(ESC);app.key('\n')
            self.assertEqual(app.page,'map')
            self.assertEqual(path.read_bytes(),before)
            b=enter_bridge()
            self.assertEqual(app.casino_route.bridge_deposit,0)
            for key in ('1','2','3'):app.key(key)
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(b.phase,'interlude')
            app.out.clear();app.draw_casino_route()
            self.assertTrue(any('1,001,000 / 1,000,000' in line for line in app.out))
            app.key('4')
            self.assertEqual(b.phase,'win')
            after=Campaign(path)
            self.assertTrue(after.can_play('casino-heist'))
            self.assertEqual(after.data['credits'],data['credits']+400)
            self.assertEqual(set(after.data),set(data))
