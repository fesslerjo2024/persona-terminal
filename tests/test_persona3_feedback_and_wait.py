"""Battle HUD and calendar shortcuts exercised through their real controllers."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_autumn_operations import BRIDGE
from persona_terminal.persona3.persona3_combat import P3Battle
from persona_terminal.persona3.persona3_state import MOON, P3Store
from persona_terminal.persona3.persona3_upper import RESCUE_DEADLINE
from .test_persona3_arqa_combat import Surface


class FeedbackAndWaitTests(TestCase):
    sizes=((65,25),(96,35))

    def battle_screen(self,b,size,time=25.):
        with patch('persona_terminal.persona3.persona3_combat.monotonic',return_value=time):
            screen=Surface(*size)
            b.draw(screen)
            return screen.text()

    def test_spell_cost_and_weak_down_cue_expire_without_erasing_log(self):
        b=P3Battle('thebel-patrol',seed=2)
        target=b.enemies[0]
        target.hp=target.max_hp=120
        target.affinity['Fire']='weak'
        self.assertEqual(b.next_actor.label,'Yukari')
        before=target.hp
        with patch('persona_terminal.persona3.persona3_combat.monotonic',return_value=25.):
            for key in '111':
                b.key(key)
        self.assertTrue(target.down)
        self.assertTrue(b.one_more)
        amount=before-target.hp
        for size in self.sizes:
            with self.subTest(size=size):
                frame=self.battle_screen(b,size)
                self.assertIn('NEXT Yukari',frame)
                self.assertIn('−4 SP',frame)
                self.assertIn('−'+str(amount),frame)
                self.assertIn('WEAK',frame)
                self.assertIn('DOWN',frame)
                self.assertIn('earns One More',frame)
                after=self.battle_screen(b,size,25.7)
                self.assertNotIn('−4 SP',after)
                self.assertNotIn('−'+str(amount),after)
        self.assertTrue(any('takes' in entry and 'WEAK' in entry for entry in b.log))

    def test_next_skips_ko_and_shows_enemy_after_last_ally(self):
        b=P3Battle('priestess',seed=2)
        b.allies[1].hp=0
        self.assertEqual(b.next_actor.label,'Junpei')
        b.key('3')
        self.assertEqual(b.actor.label,'Junpei')
        self.assertEqual(b.next_actor.label,'Priestess')
        self.assertIn('NEXT Priestess',self.battle_screen(b,self.sizes[0]))
        b._finish('win')
        self.assertIsNone(b.next_actor)

    def test_seal_break_exposes_without_down_then_actual_knockdown_allows_all_out(self):
        b=P3Battle(BRIDGE,seed=2)
        boss,*seals=b.enemies
        self.assertNotIn(boss,b.targetable_enemies)
        for seal in seals[:-1]:seal.hp=0
        seals[-1].hp=1
        self.assertIsNone(b.act('attack',seals[-1]))
        self.assertIn(boss,b.targetable_enemies)
        self.assertTrue(b.is_exposed(boss))
        self.assertFalse(boss.down)
        self.assertFalse(b.all_out)
        b.key('6')
        for size in self.sizes:
            frame=self.battle_screen(b,size)
            self.assertIn('Hanged Man EXPOSED',frame)
            self.assertIn('Exposed is not Down.',frame)
            self.assertNotIn('Hanged Man ↓',frame)
        b.actor.crit_boost=6
        self.assertIsNone(b.act('attack',boss))
        self.assertTrue(boss.down)
        self.assertTrue(b.all_out)
        for size in self.sizes:
            self.assertIn('Hanged Man ↓',self.battle_screen(b,size))
        prev=boss.hp
        self.assertIsNone(b.act('allout'))
        self.assertLess(boss.hp,prev)

    def calendar(self,day):
        directory=TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path=Path(directory.name)/'disposable-p3.json'
        store=P3Store(path);store.new_game()
        store.commit(day=day,phase='calendar')
        return path,P3App(None,store,seed=2)

    def app_screen(self,app,size):
        screen=Surface(*size)
        app.w,app.h,app.put=screen.w,screen.h,screen.put
        app.draw()
        return screen.text()

    def test_select_wait_without_going_to_dorm_keeps_warnings_and_story(self):
        path,app=self.calendar(date(2009,4,21))
        before=path.read_bytes()
        for size in self.sizes:
            self.assertIn('5 Wait for next event',self.app_screen(app,size))
        app.key('5')
        for size in self.sizes:
            frame=self.app_screen(app,size)
            self.assertIn('WAIT FOR FULL MOON?',frame)
            self.assertIn('02F survey is unfinished',frame)
        self.assertEqual(path.read_bytes(),before)
        app.key(ESC)
        self.assertEqual(app.page,'calendar')
        self.assertEqual(path.read_bytes(),before)
        app.key('5');app.key('\n')
        self.assertEqual((app.record.day,app.record.phase,app.page),(MOON,'monorail','operation'))

    def test_direct_wait_still_warns_about_optional_case_deadlines(self):
        path,app=self.calendar(RESCUE_DEADLINE)
        before=path.read_bytes()
        app.key(str(len(app.options())))
        frame=' '.join(self.app_screen(app,self.sizes[0]).split())
        self.assertIn('remaining missing-person cases will expire',frame)
        self.assertEqual(path.read_bytes(),before)
