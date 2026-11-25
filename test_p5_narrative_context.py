"""Essential story handoffs are registered on the ordinary Persona 5 route."""
import curses as C
import unittest
from unittest.mock import patch

from campaign_data import CHAPTERS
from campaign_story import (CASINO_ARREST, CASINO_WINDOW, COLD_OPEN,
                            ESCAPE_FIGHT, REQUIRED_AFTER, SCENES, StoryScene,
                            story_offer)


class Persona5NarrativeContextTests(unittest.TestCase):
    def test_first_palace_and_late_setups_have_real_before_scenes(self):
        intended = {
            'throne-room': 'castle-card',
            'museum-entry': 'museum-purpose', 'bank-entry': 'bank-purpose',
            'pyramid-desert': 'pyramid-request', 'spaceport-entry': 'spaceport-purpose',
            'casino-service': 'casino-purpose', 'casino-heist': 'casino-phone-setup',
            'cruiser-guests': 'cruiser-purpose', 'cruiser-akechi': 'akechi-glove',
            'depths-prison': 'depths-purpose', 'laboratory-reality': 'january-contradiction',
            'laboratory-daat': 'daat-purpose',
        }
        nodes = {node['id'] for chapter in CHAPTERS for node in chapter['nodes']}
        for operation, name in intended.items():
            with self.subTest(operation=operation):
                self.assertIn(operation, nodes)
                self.assertEqual(story_offer(operation, 'before'), name)
                self.assertTrue(SCENES[name].before)
                self.assertFalse(SCENES[name].optional)

    def test_story_choices_resolve_and_required_scenes_are_registered(self):
        expected = {'castle-gate', 'throne-room', 'museum-security', 'bank-entry',
                    'pyramid-boss', 'casino-heist', 'cruiser-akechi', 'depths-grail',
                    'laboratory-reality', 'laboratory-choice'}
        self.assertLessEqual(expected, REQUIRED_AFTER)
        for operation in REQUIRED_AFTER:
            with self.subTest(operation=operation):
                scene = SCENES[story_offer(operation, 'after')]
                self.assertFalse(scene.before or scene.optional)
                for beat in scene.beats.values():
                    targets = [target for _, _, target in beat.choices]
                    if beat.enter:
                        targets.append(beat.enter)
                    self.assertTrue(targets)
                    self.assertLessEqual(set(targets), set(scene.beats) | {'done'})

    def test_casino_reprise_repeats_the_window_and_capture(self):
        opening = SCENES[COLD_OPEN].beats
        reprise = SCENES['casino-payoff'].beats
        self.assertEqual(opening['balcony'].body, CASINO_WINDOW)
        self.assertEqual(reprise['window'].body, CASINO_WINDOW)
        self.assertEqual(opening['arrest'].body, CASINO_ARREST)
        self.assertTrue(reprise['capture'].body.startswith(CASINO_ARREST))
        self.assertIn('across the table from Sae', reprise['table'].body)
        self.assertIn('trigger the Metaverse app', reprise['change'].body)
        self.assertNotIn('Akechi', SCENES['casino-phone-setup'].beats['start'].body)

    def test_optional_pyramid_flavor_is_not_the_only_oracle_context(self):
        scene = SCENES[story_offer('pyramid-boss', 'after')]
        start = scene.beats['start']
        self.assertIn('Oracle', start.body)
        self.assertEqual(start.enter, 'done')
        self.assertEqual(start.choices[0][2], 'quiet')

    def test_morgana_chooses_a_battle_transition_not_an_unknown_story_beat(self):
        self.assertIsNone(story_offer('castle-gate', 'before'))
        scene = StoryScene(story_offer('april-infiltration', 'before'))
        self.assertTrue(scene.mouse_enabled())
        self.assertIn('FOLLOW MORGANA', scene.primary_button()[2])
        self.assertTrue(scene.key('\n'))
        self.assertEqual(scene.requested_transition, ESCAPE_FIGHT)
        self.assertNotIn(ESCAPE_FIGHT, scene.scene.beats)
        self.assertEqual(scene.beat, 'start')
        self.assertIn('return', scene.scene.beats)

    def test_maruki_enter_by_default_listens_and_refusing_is_deliberate(self):
        view = StoryScene('maruki-offer')
        self.assertTrue(view.mouse_enabled())
        self.assertEqual([key for _, _, _, key in view.choice_buttons()], ['1', '2', '3'])
        for expected in ('hear', 'sumire', 'hear', 'sumire'):
            self.assertFalse(view.key('\n'))
            self.assertEqual(view.beat, expected)
        self.assertFalse(view.key(C.KEY_DOWN))
        self.assertFalse(view.key('\n'))
        self.assertEqual(view.beat, 'reject')
        self.assertIn('FACE MARUKI', view.primary_button()[2])
        self.assertTrue(view.key('\n'))

    def test_maruki_targeted_mouse_choice_opens_the_selected_conversation(self):
        view = StoryScene('maruki-offer')
        y, x, _, _ = view.choice_buttons()[1]
        with patch('campaign_story.C.getmouse', return_value=(0, x+2, y, 0, C.BUTTON1_CLICKED)):
            self.assertFalse(view.key(C.KEY_MOUSE))
        self.assertEqual(view.beat, 'sumire')
        self.assertFalse(view.key('3'))
        self.assertEqual(view.beat, 'reject')


if __name__ == '__main__':
    unittest.main()
