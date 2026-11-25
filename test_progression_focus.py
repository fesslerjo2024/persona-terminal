"""Debrief prompts select earned options without modifying progress."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase

from battle_data import TEAM
from campaign import CampaignApp
from campaign_state import Campaign


class DebriefFocus(TestCase):
    def test_recruit_and_registration_focus_only(self):
        with TemporaryDirectory() as d:
            path = Path(d) / 'fresh.json'
            store = Campaign(path)
            store.new_game()
            app = CampaignApp(None,store,seed=4)
            app._b_battle = SimpleNamespace(phase='win')
            app.reward = store.clear('castle-gate','S')
            app.page = 'result'
            before = path.read_bytes()
            self.assertTrue(app.key('s'))
            self.assertEqual(app.page,'squad')
            self.assertEqual(['Joker',*TEAM][app.i],'Panther')
            self.assertNotIn('Panther',app.edit)
            app.key('\x1b')
            self.assertEqual(before,path.read_bytes())

            app.reward = store.clear('guardhouse','S')
            before = path.read_bytes()
            self.assertTrue(app.key('v'))
            self.assertEqual(app.page,'velvet')
            self.assertEqual(app.velvet_names()[app.i],'Bicorn')
            self.assertNotIn('Bicorn',app.mask_edit)
            app.key('\x1b')
            self.assertEqual(app.page,'result')
            self.assertEqual(before,path.read_bytes())
