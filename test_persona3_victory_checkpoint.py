"""Durable victory receipts: card choices, expeditions and dated aftermath."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase

from battle_ui import ESC
from persona3_app import P3App
from persona3_combat import LEAD_ID, party_caps
import persona3_field_recovery as recovery
from persona3_state import BOSS_AFTERMATH, MOON, MOON_XP, P3Store, P3SaveError
from persona3_thebel import Hall


class VictoryCheckpointTests(TestCase):
    def setUp(self):
        temp=TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)/'field.json'
        self.store=P3Store(self.path)
        self.store.new_game()

    def reopen(self):
        self.store=P3Store(self.path)
        return P3App(None,self.store,seed=13)

    def field_victory(self,index,depth,*,xp=180,lounge=False,replay=False):
        self.store.commit(phase='calendar',day=date(2009,4,24),field_checkpoint=None,
                          depth=depth,xp=xp,activity='lounge' if lounge else '')
        app=self.reopen()
        app.caps=party_caps(app.record.level)
        app.hall=Hall(index,replay=replay)
        app.hall.step('up')
        app.sp_bonus=lounge
        app.battle=SimpleNamespace(resources={n:(min(28,hp),min(8,sp)) for n,(hp,sp) in app.caps.items()},
            inventory={'Medicine':1,'Soul Drop':1,'Revival Bead':0},charge={LEAD_ID:20},
            affinity_updates={'maya':{'Slash':'weak'}})
        app._finish_hall_battle()
        self.assertEqual(app.page,'shuffle')
        return app

    def test_continue_restores_two_first_clear_cards_and_heal_without_awarding_twice(self):
        for index,depth,reward,mask in ((0,0,65,'Pixie'),(1,1,100,'Angel')):
            with self.subTest(index=index):
                before_yen=self.store.state.yen
                app=self.field_victory(index,depth,lounge=True)
                recorded=app.record.xp
                original=app.resources
                if index==0:
                    options=recovery.options(app.resources,app.inventory,app.field_kits,app.record)
                    soul_drop=next(a for a in options if a.name=='Soul Drop')
                    self.assertTrue(app._use_aid(soul_drop,LEAD_ID))
                    self.assertGreater(app.resources[LEAD_ID][1],original[LEAD_ID][1])
                saved=app.resources
                tile=app.hall.pos
                app=self.reopen()
                self.assertEqual((app.page,app.hall.index,app.hall.pos,app.record.depth),('shuffle',index,tile,index+1))
                self.assertEqual((recorded,app.shuffle_yen()),(180+reward,90))
                self.assertEqual(app.resources,saved)
                self.assertFalse(app.sp_bonus)
                self.assertEqual(app.charge,{LEAD_ID:20})
                self.assertEqual(app.record.affinity_index,{'maya':{'Slash':'weak'}})
                self.assertEqual(app.inventory['Soul Drop'],0 if index==0 else 1)
                self.assertEqual(app.record.yen,before_yen+25)
                with self.assertRaises(P3SaveError):self.store.advance_night()
                app.key('1')
                self.assertIn(mask,app.record.masks)
                self.assertEqual(app.resources,saved)
                self.assertEqual(app.record.xp,recorded)
                app=self.reopen()
                self.assertEqual((app.page,app.record.xp,app.hall.pos),('hall',recorded,tile))
                self.assertEqual(app.resources,saved)
                with self.assertRaises(P3SaveError):self.store.claim_field_card(1,mask,90)

    def test_cup_replay_and_extraction_remain_exactly_once(self):
        app=self.field_victory(0,1,replay=True)
        self.assertEqual((app.record.xp,app.shuffle_yen()),(205,30))
        old=app.resources
        expected=app._recover_at(old,app.caps,30,12)
        app.key('3')
        self.assertEqual(app.resources,expected)
        app=self.reopen()
        self.assertEqual((app.page,app.resources,app.record.xp),('hall',expected,205))
        app.key('x');app.key('\n')
        self.assertIsNone(app.record.field_checkpoint)
        self.assertEqual(self.reopen().page,'calendar')

    def test_mid_brake_and_first_light_survive_restart_without_boss_or_extra_xp(self):
        self.store.commit(phase='monorail',day=MOON)
        self.store.clear_operation('priestess')
        for phase,scene in (('monorail-brake','train-brake'),('monorail-stopped','train-brake'),('finale','story')):
            app=self.reopen()
            self.assertEqual((app.page,app.record.aftermath,app.record.xp),(scene,phase,MOON_XP))
            if phase=='monorail-brake':
                self.assertIsNone(app.train_stopped)
                app.key(ESC)
                self.assertTrue(app.exit)
                app=self.reopen()
                self.assertIsNone(app.train_stopped)
            if phase=='monorail-stopped':self.assertIsNotNone(app.train_stopped)
            app.key('\n')
        self.assertEqual((app.page,app.record.aftermath,app.record.xp),('calendar','',MOON_XP))
        self.assertEqual(self.reopen().page,'calendar')

    def test_other_early_victories_resume_each_mandatory_aftermath(self):
        import persona3_arqa as arqa
        import persona3_upper as upper
        import persona3_yabbashah as yabba
        import persona3_yabbashah_upper as high
        starts=(('emperor-empress',arqa.RESCUE_DAY),('hotel-lovers',upper.HOTEL_DAY),
                ('chariot-justice',yabba.AUGUST_MOON),('hermit',high.HERMIT_DAY))
        for operation,start in starts:
            with self.subTest(operation=operation):
                phase,day,award,scene=BOSS_AFTERMATH[operation]
                self.store.commit(phase=phase,day=start,xp=400,aftermath='')
                self.store.clear_operation(operation)
                app=self.reopen()
                self.assertEqual((app.page,app.scene,app.record.day,app.record.xp),('story',scene,day,400+award))
                app.key('\n')
                self.assertEqual((app.page,app.record.aftermath),('calendar',''))
                app=self.reopen()
                self.assertEqual(app.page,'calendar')
                app.go('evening')
                app.deploy()
                self.assertFalse(app.free_expedition)
