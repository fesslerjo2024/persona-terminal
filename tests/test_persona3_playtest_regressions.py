"""Playtest regressions through Persona 3's player-facing commands."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_combat import P3Battle
from persona_terminal.persona3.persona3_field_clues import CALLBACK
from persona_terminal.persona3.persona3_recording_discoveries import VILLA_FRAGMENT
from persona_terminal.persona3.persona3_state import MOON, P3Store
from .test_persona3_arqa_combat import Surface


def render(app, width, height):
    surface=Surface(width,height)
    app.w,app.h,app.put=width,height,surface.put
    app.draw()
    return ' '.join(surface.text().split())


class PlaytestRegressions(TestCase):
    def setUp(self):
        folder=TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path=Path(folder.name)/'practice.json'
        self.store=P3Store(self.path)
        self.store.new_game()

    def test_supply_bindings_hold_after_depletion(self):
        for size in ((65,25),(100,35)):
            b=P3Battle('thebel-patrol',seed=2,inventory={'Medicine':1,'Soul Drop':1,'Revival Bead':1})
            b.allies[0].hp=1
            b.key('4');b.key('1');b.key('1')
            actor=b.actor
            b.key('4');b.key('1')
            screen=Surface(*size);b.draw(screen)
            self.assertIn('1 Medicine ×0',screen.text())
            self.assertIn('2 Soul Drop ×1',screen.text())
            self.assertIn('3 Revival Bead ×1',screen.text())
            self.assertIn('Out of Medicine.',screen.text())
            self.assertEqual(b.inventory,{'Medicine':0,'Soul Drop':1,'Revival Bead':1})
            self.assertIs(b.actor,actor)

    def test_shift_tells_apart_the_three_blocked_states(self):
        b=P3Battle('thebel-patrol',seed=2)
        actor=b.actor
        b.key('5')
        self.assertIn('Earn a One More',b.notice)
        b.one_more=True
        b.key('5');b.key('1')
        receiver=b.actor
        self.assertIsNot(receiver,actor)
        b.key('5')
        self.assertIn('Already shifted',b.notice)
        self.assertIs(receiver,b.actor)
        b.shifted=False
        for u in b.allies:
            if u is not receiver:u.down=True
        b.key('5')
        self.assertIn('No teammate can receive',b.notice)
        self.assertIs(receiver,b.actor)

    def test_loss_link_changes_only_confirmed_lead_and_uses_it_on_retry(self):
        self.store.commit(phase='monorail',day=MOON,masks=('Nekomata','Angel'),equipped='Nekomata')
        a=P3App(None,self.store,seed=2)
        a.key('1')
        a.open_battle('priestess')
        b=a.battle
        b.allies[0].hp=1
        b._enemy_bonus=True
        b._hit(b.enemies[0],b.allies[0],'Ice',100,False)
        b._ended()
        for size in ((65,25),(100,35)):
            defeat=render(a,*size)
            self.assertIn('Ice hit a weakness.',defeat)
            self.assertIn('One More follow-up.',defeat)
            self.assertIn('A ADJUST LEAD',defeat)
        before=self.path.read_bytes()
        resources=b.resources
        a.key('a')
        self.assertEqual(a.page,'lead-recovery')
        self.assertIn('Nekomata',render(a,65,25))
        a.key(ESC)
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual(b.resources,resources)
        a.key('a');a.key('2')
        self.assertEqual(a.record.equipped,'Angel')
        self.assertEqual(a.page,'battle')
        self.assertEqual(b.resources,resources)
        a.key('1')
        self.assertEqual(a.page,'battle')
        a.key('\n')
        self.assertEqual(a.page,'operation')
        a.open_battle('priestess')
        self.assertEqual(a.battle.persona,'Angel')

    def test_recording_comparison_replays_exact_cue_but_can_be_skipped(self):
        for compare in (False,True):
            with self.subTest(compare=compare):
                self.store.commit(phase='recovered-recording',day=date(2009,11,5))
                a=P3App(None,self.store)
                a.discover('recording')
                before=self.path.read_bytes()
                a.key('1')
                for size in ((65,25),(100,35)):
                    self.assertIn('Replay the July fragment',render(a,*size))
                a.key('2' if compare else '1')
                if compare:
                    for size in ((65,25),(100,35)):
                        self.assertIn(VILLA_FRAGMENT,render(a,*size))
                    a.key('2')
                    self.assertIn('before Eiichiro said he was shutting down',render(a,65,25))
                    a.key('1')
                self.assertIn('YUKARI / ISIS',render(a,65,25))
                self.assertEqual(self.path.read_bytes(),before)

    def test_border_gives_actual_date_and_never_bypasses_gate(self):
        self.store.commit(phase='calendar',day=date(2009,5,2),depth=5)
        a=P3App(None,self.store)
        a.deploy();a.key('\n');a.key('\n')
        self.assertEqual(a.page,'border')
        for size in ((65,25),(100,35)):
            self.assertIn('Lower Arqa opens May 10.',render(a,*size))
        a.key('\n')
        self.assertEqual((a.page,a.block),('entrance','thebel'))
        self.assertIn('Keep HP / SP / items.',render(a,65,25))

    def test_landmark_is_optional_and_echo_survives_real_reload(self):
        self.store.commit(phase='calendar',day=date(2009,5,11),arqa=3,depth=5)
        before=self.path.read_bytes()
        a=P3App(None,self.store)
        a.deploy();a.key('\n')
        a.key('1');a.key('\n')
        self.assertEqual(a.hall.floor.number,23)
        self.assertNotIn('E LOOK',render(a,65,25))
        a.key('d')
        for size in ((65,25),(100,35)):
            self.assertIn('E LOOK',render(a,*size))
        self.assertEqual(self.path.read_bytes(),before)
        a.key('t');a.key('4');a.key('\n');a.key('s');a.key('e')
        self.assertNotIn(CALLBACK,render(a,65,25))
        self.assertEqual(self.path.read_bytes(),before)
        a=P3App(None,P3Store(self.path))
        a.deploy();a.key('\n');a.key('1');a.key('\n');a.key('d')
        resources,inventory=a.resources.copy(),a.inventory.copy()
        a.key('e')
        self.assertIn('A torn SEES tag',render(a,65,25))
        self.assertEqual((a.resources,a.inventory),(resources,inventory))
        a.key(ESC)
        self.assertEqual(a.page,'hall')
        a=P3App(None,P3Store(self.path))
        self.assertTrue(a.record.arqa_tag_seen)
        self.assertEqual((a.record.xp,a.record.yen),(0,50))
        a.deploy();a.key('\n');a.key('3');a.key('\n');a.key('s');a.key('e')
        for size in ((65,25),(100,35)):
            self.assertIn(CALLBACK,render(a,*size))

    def test_cracking_cue_shares_real_shell_threshold_and_names_revivor(self):
        b=P3Battle('chariot-justice',seed=42)
        cycle=b.tank_cycle
        self.assertNotIn('CRACKING',b.threat)
        cycle.tank.hp=cycle.split_hp+1
        self.assertIn('SHELL CRACKING',b.threat)
        cycle.count=1
        self.assertIn('CANNON AIMED',b.threat)
        self.assertIn('Shell cracking',b.threat)
        cycle.tank.hp=cycle.split_hp
        cycle.settle(b)
        chariot,justice=cycle.visible
        justice.hp=0
        self.assertIn('Defeat Chariot before it acts.',b.threat)
        justice.hp=1
        chariot.hp=0
        self.assertIn('Defeat Justice before it acts.',b.threat)
