"""Composed battle frames and risky departure choices, with disposable saves."""
import curses as C
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from battle_ui import BattleUI,ESC
from campaign import CampaignApp
from campaign_combat import build_stage
from campaign_state import Campaign,CampaignError,TestingCampaign


class Surface(CampaignApp):
    def __init__(self,store,w=65,h=25):
        super().__init__(None,store,4)
        self.w,self.h=w,h
        self.blank()

    def blank(self):
        self.rows=[[' ']*self.w for _ in range(self.h)]

    def put(self,y,x,text,*_,**__):
        if 0<=y<self.h and 0<=x<self.w-1:
            self.rows[y][x:min(self.w-1,x+len(text))]=text[:self.w-1-x]

    def capture(self,draw):
        self.blank()
        draw()
        return '\n'.join(''.join(row) for row in self.rows)


def museum(app):
    app.start_testing()
    app.key(C.KEY_RIGHT)
    app.key('6')
    app.key('\n')
    b=app._b_battle
    assert b.config['id']=='museum-throne'
    for u in b.enemies:u.hp=0
    assert b._state() and b.wave==2
    b._advance()
    b.actor=next(u for u in b.allies if u.name=='Mona')
    return b


class BattleAuditTests(TestCase):
    def test_five_foes_leave_a_real_command_skill_and_target_row(self):
        with TemporaryDirectory() as directory:
            save=Campaign(Path(directory)/'disposable.json')
            for w,h in ((65,25),(100,40)):
                app=Surface(save,w,h)
                b=museum(app)
                frame=app.capture(app.battle_page)
                self.assertIn('Persona',frame)
                self.assertIn('Verdant Copy',frame)
                b.log.append('Older context stays separate from the command row.')
                app.key('1')
                frame=app.capture(app.battle_page)
                self.assertIn('Garula',frame)
                self.assertIn('Zorro',frame)
                self.assertNotIn('ZorroNDS',frame)
                b.seen['Golden Copy']={'Wind':'weak'}
                b.seen['Verdant Copy']={'Wind':'drain'}
                app.key('1')
                frame=app.capture(app.battle_page)
                self.assertIn('1 Madarame',frame)
                app.key('5')
                self.assertTrue(any('drains Wind' in entry for entry in b.log))

    def test_learned_affinity_badges_never_disclose_hidden_affinity(self):
        with TemporaryDirectory() as directory:
            app=Surface(Campaign(Path(directory)/'disposable.json'))
            b=museum(app)
            app.key('1')
            frame=app.capture(app.battle_page)
            self.assertIn('Garula',frame)
            self.assertNotIn('[DRAIN]',frame)
            b.seen.update({
                'Verdant Copy':{'Wind':'drain'},
                'Golden Copy':{'Wind':'weak'},
                'Cerulean Copy':{'Wind':'repel'},
                'Scarlet Copy':{'Wind':'null'},
            })
            app.key(C.KEY_DOWN)
            frame=app.capture(app.battle_page)
            self.assertIn('Drain: Verdant Copy',frame)
            self.assertIn('[DRAIN]',frame)
            self.assertIn('[REPEL]',frame)
            self.assertIn('[NULL]',frame)
            self.assertIn('[WEAK]',frame)
            app.key(C.KEY_UP)
            app.key('1')
            app.key(C.KEY_END)
            frame=app.capture(app.battle_page)
            self.assertIn('[DRAIN] Verdant Copy',frame)
            b.enemies[-1].hp=0
            app.key(C.KEY_HOME)
            self.assertNotIn('[DRAIN]',app.capture(app.battle_page))

    def test_persona_preview_is_defensive_and_tenth_item_has_no_fake_key(self):
        with TemporaryDirectory() as directory:
            store=Campaign(Path(directory)/'disposable.json')
            store.new_game()
            app=Surface(store)
            app.key('1');app.key('1');app.key('\n')
            b=app._b_battle
            app.key('1');app.key(C.KEY_RIGHT)
            frame=app.capture(app.battle_page)
            self.assertIn('Pixie / PREVIEW',frame)
            self.assertIn('GuW IcW ElR',frame)
            self.assertEqual(b.persona,'Arsène')
            app.key('i')
            self.assertIn('DEF: IcW BlW CuR',app.capture(app.battle_page))
            app.key(ESC);app.key(ESC)
            app.key('5');app.key(C.KEY_END)
            frame=app.capture(app.battle_page)
            self.assertIn('Air Cannon',frame)
            self.assertNotIn('10 Air Cannon',frame)
            app.key('1')
            self.assertIn('Medicine',app.capture(app.battle_page))

    def test_combat_presentation_has_no_honest_actions_until_ready(self):
        with TemporaryDirectory() as directory:
            app=Surface(Campaign(Path(directory)/'disposable.json'))
            b=museum(app)
            app._b_outgoing=(1,b.enemies,float('inf'))
            frame=app.capture(app.battle_page)
            self.assertIn('NEXT FORMATION',frame)
            self.assertNotIn('I STATUS',frame)
            self.assertNotIn('Persona',frame)
            app._b_outgoing=None
            b.phase='win'
            frame=app.capture(app.battle_page)
            self.assertNotIn('REMATCH',frame)
            self.assertNotIn('TRIAL CLEARED',frame)
            app.page='trials'
            self.assertIn('REMATCH',app.capture(app.battle_page))

    def test_quit_cancels_without_writes_and_win_can_retry_save(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'disposable.json'
            store=Campaign(path)
            store.new_game()
            app=Surface(store)
            app.key('1');app.key('1');app.key('\n')
            before=path.read_bytes()
            self.assertTrue(app.key('q'))
            self.assertIn('QUIT THIS ATTEMPT?',app.capture(app.draw_departure))
            app.key(ESC)
            self.assertEqual(app.page,'battle')
            self.assertEqual(path.read_bytes(),before)
            app._b_battle.phase='win'
            with patch.object(store,'clear',side_effect=CampaignError('Injected save failure.')):
                app.record()
                self.assertTrue(app.key('q'))
            self.assertEqual(app.page,'result')
            self.assertIn('DISCARD UNSAVED WIN?',app.capture(app.draw_departure))
            app.key(ESC)
            self.assertIn('RETRY SAVE',app.capture(app.result))
            app.key(ESC)
            self.assertEqual(app.departure,('map',True))
            app.key(ESC)
            app.key('\n')
            self.assertIsNone(app.error)
            self.assertEqual(Campaign(path).data['cleared'],{'castle-gate':'S'})
            self.assertFalse(app.key('q'))

    def test_explicitly_confirm_quit_or_waive_unsaved_result(self):
        for key,destination in (('q','quit'),(ESC,'map')):
            with self.subTest(destination=destination), TemporaryDirectory() as directory:
                path=Path(directory)/'disposable.json'
                store=Campaign(path)
                store.new_game()
                app=Surface(store)
                app.key('1');app.key('1');app.key('\n')
                before=path.read_bytes()
                app._b_battle.phase='win'
                with patch.object(store,'clear',side_effect=CampaignError('Injected save failure.')):
                    app.record()
                app.page='result'
                self.assertTrue(app.key(key))
                self.assertEqual(app.departure,(destination,True))
                self.assertEqual(app.key('\n'),destination=='map')
                if destination=='map':self.assertEqual(app.page,'map')
                self.assertEqual(path.read_bytes(),before)
