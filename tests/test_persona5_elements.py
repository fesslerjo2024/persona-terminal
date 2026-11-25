"""Persona 5 attack pigments and symbols survive selection and viewport changes."""
import unittest

from persona_terminal.persona5.battle_data import ELEMENTS, ITEMS, SKILLS
from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.shared.combat_palette import P3_MARKS, P5_MARKS
from .test_battle_information import Recorder


class ColorRecorder(Recorder):
    def __init__(self, w, h):
        self.colors = []
        super().__init__(w, h)

    def put(self, y, x, value, ink=None, bold=False, reverse=False):
        super().put(y, x, value)
        if len(value):
            self.colors.append((y, x, value, ink, reverse))

    def render(self):
        self.colors.clear()
        return super().render()

    def assert_attack(self, name, element):
        glyph, ink = P5_MARKS[element]
        y, _, _, _, _ = next(row for row in self.colors if row[2].strip() == name and row[3] == ink)
        if not any(row[0] == y and row[2] == glyph and row[3] == ink for row in self.colors):
            raise AssertionError(f'Missing {element} marker on {name}')


class Persona5AttackColors(unittest.TestCase):
    def test_palette_is_complete_distinct_and_matches_persona3(self):
        self.assertEqual(tuple(P5_MARKS), ELEMENTS)
        self.assertEqual(len({marker for marker, _ in P5_MARKS.values()}), len(ELEMENTS))
        self.assertEqual(len({ink for _, ink in P5_MARKS.values()}), len(ELEMENTS))
        for element in ('Fire', 'Ice', 'Electric', 'Wind', 'Almighty'):
            self.assertEqual(P5_MARKS[element], P3_MARKS[element])
        self.assertEqual(P5_MARKS['Bless'], P3_MARKS['Light'])
        self.assertEqual(P5_MARKS['Curse'], P3_MARKS['Dark'])

    def test_actions_keep_their_color_on_focus_and_in_targeting(self):
        for w, h in ((65,25), (100,35)):
            with self.subTest(width=w):
                ui = ColorRecorder(w,h)
                ui._b_launch()
                ui.render()
                ui.assert_attack('Attack', 'Physical')
                ui.assert_attack('Gun', 'Gun')
                ui.battle_key('1')
                ui.render()
                ui.assert_attack('Eiha', 'Curse')
                self.assertIsNone(ui._b_attack_element('skill:Dia'))
                b=ui._b_battle
                foe=b.enemies[0]
                b.seen[foe.name]={'Curse':'weak'}
                ui.render()
                ui.assert_attack('Eiha', 'Curse')
                self.assertIn('[WEAK]', ui.render())
                ui.battle_key('1')
                ui.render()
                self.assertTrue(any('● Eiha → TARGET' in text and ink==P5_MARKS['Curse'][1]
                                    for _,_,text,ink,_ in ui.colors))
                self.assertEqual(b.persona,'Arsène')
                self.assertEqual(b.seen[foe.name],{'Curse':'weak'})

    def test_item_mapping_and_help_legend(self):
        ui=ColorRecorder(65,25)
        ui._b_launch()
        for name, item in ITEMS.items():
            spec=SKILLS[item['skill']]
            expected=spec.get('element') if spec['kind']=='damage' else None
            self.assertEqual(ui._b_attack_element('item:'+name),expected)
        ui.battle_key('?');ui.battle_key('e')
        self.assertIn('ESC TACTICS',ui.render())
        for element,(glyph,ink) in P5_MARKS.items():
            self.assertTrue(any(text==f'{glyph} {element}' and color==ink
                                for _,_,text,color,_ in ui.colors),element)
        ui.battle_key(ESC)
        self.assertEqual(ui._b_overlay,'help')
        ui.battle_key(ESC)
        self.assertIsNone(ui._b_overlay)
