"""Regression coverage for calendar, readiness and recovery audit fixes."""
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_arqa import BRIDGE
from persona_terminal.persona3.persona3_combat import LEAD_ID, P3Battle
from persona_terminal.persona3.persona3_junpei import LAST_GIFT_DAY
from persona_terminal.persona3.persona3_late import FINALE, when
from persona_terminal.persona3.persona3_state import END, P3SaveError, P3Store
from persona_terminal.persona3.persona3_summit_checkpoint import SummitCarry
from persona_terminal.persona3.persona3_upper import RESCUE_DEADLINE
from .test_persona3_arqa_combat import Surface


class AuditFollowups(TestCase):
    def setUp(self):
        td=TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.path=Path(td.name)/'disposable.json'
        self.store=P3Store(self.path)
        self.store.new_game()

    def app(self,day,**state):
        self.store.commit(day=day,**{'phase':'calendar',**state})
        return P3App(None,self.store,seed=4)

    def paint(self,app,w=65,h=25):
        surface=Surface(w,h)
        app.w,app.h,app.put=w,h,surface.put
        app.draw()
        return ' '.join(surface.text().split())

    def test_last_day_rest_wait_and_extract_warn_without_mutation(self):
        cases=((RESCUE_DEADLINE,{},'missing-person cases will expire'),
               (LAST_GIFT_DAY,{'junpei_flowers':'bought'},'miss your chance to bring Junpei'))
        for day,state,warning in cases:
            app=self.app(day,**state)
            before=self.path.read_bytes()
            for k in ('3','4'):
                app.go('evening')
                app.key(k)
                self.assertIn(warning,self.paint(app))
                app.key(ESC)
                self.assertEqual(self.path.read_bytes(),before)
            app.deploy();app.key(' ');app.key('x')
            self.assertIn(warning,self.paint(app))
            app.key(ESC)
            self.assertEqual(self.path.read_bytes(),before)
            app.go('evening');app.key('3');app.key('\n')
            self.assertEqual(app.record.day,day+timedelta(days=1))

    def test_early_skip_is_informed_not_gated_and_elevator_mentions_old_block(self):
        app=self.app(date(2009,4,21))
        for k in ('4','4'):app.key(k)
        self.assertIn('02F survey is unfinished',self.paint(app))
        app.key('\n')
        self.assertEqual(app.page,'operation')
        app=self.app(END,depth=1)
        self.assertIn('MAY / DAYTIME',self.paint(app))
        app.key('4')
        self.assertIn('Thebel still open',self.paint(app))
        app.key('1');app.key(' ')
        self.assertIn('Return to Thebel',self.paint(app))

    def test_lounge_has_dated_character_flavor_and_keeps_recovery_perk(self):
        app=self.app(date(2009,4,23),depth=1)
        app.key('3')
        self.assertIn('Yukari puts the kettle on',self.paint(app))
        self.assertEqual((app.record.activity,app.record.charm),('lounge',1))
        app.key('1')
        self.assertTrue(app.sp_bonus)

    def test_full_charge_without_registered_pair_stays_on_commands(self):
        for stock,registered,locked in (
            ({'Orpheus':()},('Orpheus',),True),
            ({'Pixie':()},('Orpheus','Apsaras','Pixie'),False),
        ):
            b=P3Battle('thebel-patrol',stock=stock,persona=next(iter(stock)),registered=registered,
                       theurgy=True,charge={LEAD_ID:100})
            opts=b._menu()
            self.assertEqual('LOCKED' in opts[-1][0],locked)
            b.key('9')
            if locked:
                self.assertEqual(b.screen,'command')
                self.assertIn('Orpheus and Apsaras',b.notice)
            else:
                self.assertEqual(b.screen,'theurgies')
                self.assertTrue(any(r[0]=='Cadenza' for r in b._menu()))
        app=self.app(BRIDGE)
        app.open_theurgy_training(deploy=True)
        self.assertIn('Orpheus and Apsaras for Cadenza',self.paint(app))
        app.go('compendium')
        panel=self.paint(app)
        self.assertIn('Cadenza: register',panel)
        self.assertIn('Orpheus +',panel)
        self.assertIn('Apsaras.',panel)

    def test_evolved_team_heal_spends_sp_once_and_never_revives(self):
        app=self.app(when(11,9),xp=3500)
        app.deploy();app.key(' ')
        app.resources.update({LEAD_ID:(10,16),'Yukari':(98,32),'Junpei':(0,12)})
        original=app.resources.copy()
        before=self.path.read_bytes()
        app.key('h')
        app.i=next(i for i,aid in enumerate(app._recovery_options()) if aid.name=='Mediarama')
        self.assertIn('Yukari • Mediarama',self.paint(app))
        app.key('\n')
        self.assertEqual(app.resources[LEAD_ID],(10+61,16))
        self.assertEqual(app.resources['Yukari'],(min(app.caps['Yukari'][0],98+61),20))
        self.assertEqual(app.resources['Junpei'],original['Junpei'])
        self.assertEqual(self.path.read_bytes(),before)

    def test_summit_restock_keeps_charge_and_resets_resources_and_supplies(self):
        roster=(LEAD_ID,'Yukari','Akihiko','Aigis')
        carry={LEAD_ID:100,'Yukari':20,'Aigis':85,'Fuuka':73}
        checkpoint=SummitCarry(roster,((LEAD_ID,10,1),),(('Medicine',0),('Soul Drop',7)),tuple(carry.items()))
        self.app(FINALE,phase='summit-nyx',xp=3800,summit_carry=checkpoint)
        before=self.path.read_bytes()
        app=P3App(None,P3Store(self.path))
        self.assertEqual(app.late_party,roster)
        self.assertIn('Restock keeps Theurgy charge',self.paint(app))
        self.assertEqual(self.path.read_bytes(),before)
        app.key('\n')
        self.assertEqual(app.battle.resources[LEAD_ID],(10,1))
        app=P3App(None,P3Store(self.path))
        app.key('r')
        self.assertIn('Theurgy kept',self.paint(app))
        self.assertNotEqual(self.path.read_bytes(),before)
        updated=self.path.read_bytes()
        app=P3App(None,P3Store(self.path))
        self.assertNotIn('R RESTOCK',self.paint(app))
        app.key('\n')
        self.assertEqual(app.battle.resources[LEAD_ID],app.battle.caps[LEAD_ID])
        self.assertGreater(app.battle.inventory['Medicine'],0)
        self.assertEqual(app.battle.inventory['Soul Drop'],7)
        for name,n in carry.items():self.assertEqual(app.battle.charge[name],n)
        self.assertEqual(self.path.read_bytes(),updated)
        with self.assertRaisesRegex(P3SaveError,'Invalid summit checkpoint'):
            self.store.commit(day=when(4,22),phase='calendar',summit_carry=checkpoint)

    def test_late_boss_cues_reflect_usable_actions(self):
        b=P3Battle('strega-jin',day=FINALE,theurgy=True)
        cycle=b.late_cycle
        cycle.signal='grenade'
        for ally,phrase in ((b.allies[0],'Guard or switch Persona.'),(b.allies[1],'Guard.')):
            cycle.aim=('Shock Grenade','Electric',30,ally)
            self.assertTrue(cycle.threat().endswith(phrase))
        c=P3Battle('chidori',day=when(11,22),theurgy=True)
        c.late_cycle.chidori.hp=5
        c.late_cycle.settle(c)
        self.assertIn('spring of life spent',c.late_cycle.threat().lower())
