"""Combat readouts and the Spaceport uninterrupted wave transition at two supported terminal sizes."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from persona_terminal.persona5.battle_data import SKILLS
from persona_terminal.persona5.battle_ui import CYAN, DIM, ESC, FEEDBACK_HOLD
from persona_terminal.persona5.campaign_data import NODES
from persona_terminal.persona5.campaign_state import Campaign
from .test_animation_gallery import Surface
from .test_persona5_elements import ColorRecorder


class Persona5Feedback(unittest.TestCase):
    def test_exact_cost_and_weak_knockdown_beside_units_then_expire(self):
        for width,height in ((65,25),(96,35)):
            with self.subTest(width=width):
                ui=ColorRecorder(width,height)
                ui._b_launch()
                b=ui._b_battle
                caster=b.actor
                target=b.enemies[0]
                target.hp=target.max_hp=200
                target.affinity['Curse']='weak'
                b.rng.seed(1)
                before=caster.sp
                with patch('persona_terminal.persona5.battle_ui.time.monotonic',return_value=20):
                    ui.battle_key('1')
                    ui.battle_key('1')
                    ui.battle_key('1')
                    screen=ui.render()
                    self.assertLess(target.hp,200)
                    self.assertTrue(target.down)
                    self.assertEqual(before-caster.sp,SKILLS['Eiha']['sp'])
                    attack=next((y,x,text) for y,x,text,_,_ in ui.colors if 'WEAK' in text and f'−{200-target.hp} HP' in text)
                    self.assertIn('DOWN',attack[2])
                    self.assertGreaterEqual(attack[1],(width-1)//2)
                    caster_note=next((y,x,text) for y,x,text,_,_ in ui.colors if f'−{before-caster.sp} SP' in text)
                    self.assertLess(caster_note[1],(width-1)//2)
                    self.assertTrue(any(x<(width-1)//2 and '█' in text and ink==CYAN
                                        for _,x,text,ink,_ in ui.colors))
                    self.assertTrue(any('HP' in text and '/' in text for _,_,text,_,_ in ui.colors))
                    self.assertTrue(any('SP' in text and '/' in text for _,_,text,_,_ in ui.colors))
                    self.assertIn('L LOG',ui.last_footer)
                    self.assertTrue(any('takes' in line and 'WEAK' in line for line in b.log))
                    for y,x,value in ui.written:
                        self.assertGreaterEqual(y,0)
                        self.assertLess(y,height)
                        self.assertLessEqual(x+len(value),width)
                with patch('persona_terminal.persona5.battle_ui.time.monotonic',return_value=20+FEEDBACK_HOLD+.01):
                    ui.render()
                    self.assertFalse(ui._b_feedback)
                    self.assertIn('L LOG',ui.last_footer)

    def test_final_ko_cue_is_held_until_readable(self):
        ui=ColorRecorder(96,35)
        ui._b_launch()
        b=ui._b_battle
        b.story=False
        b.wave=b.wave_count
        for f in b.enemies[1:]:f.hp=0
        target=b.enemies[0]
        target.hp=5
        b.rng.seed(1)
        ui.page='battle'
        with patch('persona_terminal.persona5.battle_ui.time.monotonic',return_value=42):
            ui._b_apply('attack',target)
            self.assertEqual(b.phase,'win')
            self.assertIn('−5 HP · KO',ui.render())
            self.assertTrue(ui._b_result_animation(42.9))

    def test_unavailable_all_out_stays_dim_even_when_focused(self):
        ui=ColorRecorder(96,35)
        ui._b_launch()
        ui._b_index=6
        ui.render()
        self.assertTrue(any(text=='All-Out Attack' and color==DIM and not reverse
                            for _,_,text,color,reverse in ui.colors))

    def test_spaceport_advances_automatically_and_keeps_resources_and_save(self):
        for width,height in ((65,25),(96,35)):
            with self.subTest(width=width), TemporaryDirectory() as d:
                path=Path(d)/'disposable.json'
                slot=Campaign(path)
                slot.new_game()
                for node in NODES:
                    if node['id']=='spaceport-boss':break
                    slot.clear(node['id'])
                byte_state=path.read_bytes()
                app=Surface(slot)
                app.w,app.h=width,height
                app.key('1')  # Continue through the actual app's title and map.
                self.assertEqual(app.label(),'SPACEPORT')
                app.key('6'); app.key('\n')
                b=app._b_battle
                self.assertEqual(b.config['id'],'spaceport-boss')
                b.shuffle_turns=False
                b.allies[0].hp-=15
                b.allies[0].sp-=14
                b.items['Medicine']-=1
                tracked=[(u.hp,u.sp) for u in b.allies],dict(b.items)
                for wave in range(1,6):
                    self.assertEqual(b.wave,wave)
                    for foe in b.enemies:foe.hp=0
                    b._state()
                self.assertEqual((b.phase,b.wave,b.interlude),('turn',6,None))
                self.assertIsNone(app.casino_route)
                app.out.clear()
                app.draw_combat()
                self.assertNotIn('SPACEPORT / RESOURCE CHECK',app.out)
                self.assertEqual(app.page,'battle')
                self.assertIn('Execurobo MDL-ED',(enemy.name for enemy in b.enemies))
                self.assertEqual(([(u.hp,u.sp) for u in b.allies],dict(b.items)),tracked)
                self.assertEqual(path.read_bytes(),byte_state)
