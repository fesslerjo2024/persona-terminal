"""The packaged layout does not relocate save slots or change the entry command."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from persona_terminal.persona3.persona3_state import DEFAULT_SAVE as P3_DEFAULT
from persona_terminal.persona3 import persona3_title
from persona_terminal.persona5.campaign_state import DEFAULT_SAVE as P5_DEFAULT
from persona_terminal.shared import launcher
from persona_terminal.shared.suite_menu import SuiteMenu


class LauncherLayoutTests(TestCase):
    def test_selector_paints_persona3_title_with_shared_surface(self):
        selector = SuiteMenu(None)
        selector.w, selector.h = 65, 25
        with patch.object(selector, 'put') as paint:
            persona3_title.draw_intro(selector, persona3_title.DURATION * .65)
        self.assertTrue(paint.called)
        self.assertTrue(any(any('\u2801' <= ch <= '\u28ff' for ch in call.args[2])
                            for call in paint.call_args_list))

    def test_default_slots_are_still_next_to_public_launcher(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / 'campaign.py').is_file())
        self.assertEqual(P5_DEFAULT, root / 'campaign-save.json')
        self.assertEqual(P3_DEFAULT, root / 'persona3-save.json')
        with patch.dict(os.environ, {}, clear=True), \
             patch('sys.argv', ['campaign.py']), \
             patch.object(launcher.C, 'wrapper') as curses_entry:
            launcher.main()
        curses_entry.assert_called_once_with(launcher.run_curses, P5_DEFAULT,
                                             None, False, P3_DEFAULT)

    def test_save_environment_and_direct_switch_still_use_separate_paths(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            env = {'PHANTOM_CAMPAIGN_SAVE': str(root / 'p5 slot.json'),
                   'PERSONA3_TERMINAL_SAVE': str(root / 'p3 slot.json')}
            with patch.dict(os.environ, env, clear=True), \
                 patch('sys.argv', ['campaign.py', '--persona5', '--seed', '7']), \
                 patch.object(launcher.C, 'wrapper') as curses_entry:
                launcher.main()
            curses_entry.assert_called_once_with(launcher.run_curses,
                                                 root / 'p5 slot.json', 7, True,
                                                 root / 'p3 slot.json')
            self.assertEqual(list(root.iterdir()), [])

    def test_relative_cli_paths_stay_relative_and_take_precedence(self):
        env = {'PHANTOM_CAMPAIGN_SAVE': '/unused/five.json',
               'PERSONA3_TERMINAL_SAVE': '/unused/three.json'}
        with patch.dict(os.environ, env, clear=True), \
             patch('sys.argv', ['campaign.py', '--save', 'five.json', '--p3-save', 'three.json']), \
             patch.object(launcher.C, 'wrapper') as curses_entry:
            launcher.main()
        curses_entry.assert_called_once_with(launcher.run_curses,
                                             Path('five.json'), None, False,
                                             Path('three.json'))
