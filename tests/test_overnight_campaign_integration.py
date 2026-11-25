"""Check the audited Royal routes at the real campaign key dispatcher."""
import curses as C
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from persona_terminal.persona5.battle_data import TEAM
from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona5.campaign_state import Campaign
from .test_battle_audit import Surface


class OvernightCampaignIntegration(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'playtest.json'
        self.save = Campaign(self.path)
        self.save.new_game()

    def before(self, node):
        while self.save.next_node != node:
            self.assertIsNotNone(self.save.next_node)
            self.save.clear(self.save.next_node, 'B')

    @staticmethod
    def locate(app, node):
        app.ch = next(i for i, ch in enumerate(app.chapters) if node in [
            entry['id'] if isinstance(entry, dict) else entry for entry in ch['nodes']])
        app.pick = next(i for i, entry in enumerate(app.nodes()) if entry['id'] == node)
        app.page = 'map'
        app.key('\n')

    def test_defeat_lead_change_swaps_only_on_commit_and_retry_uses_it(self):
        self.before('museum-security')
        data = self.save.data
        data['slots'] = len(data['loadout'])
        data['personas']['Jack Frost'] = []
        self.save._commit(data)
        app = Surface(self.save)
        self.locate(app, 'museum-security')
        app.stage()
        app._b_battle.phase = 'loss'
        app.record()
        app.page = 'result'
        self.assertIn('A ADJUST LEAD', app.capture(app.result))
        initial_bytes = self.path.read_bytes()
        initial = self.save.data
        app.key('a')
        app.lead_pick = app.lead_choices().index('Jack Frost')
        self.assertIn('will take',app.capture(app.draw_adjust_lead))
        app.key(ESC)
        self.assertEqual(self.path.read_bytes(),initial_bytes)
        app.key('a')
        app.lead_pick = app.lead_choices().index('Jack Frost')
        app.key('\n')
        self.assertEqual(self.save.data['primary'],'Jack Frost')
        self.assertEqual(set(initial['loadout'])-{initial['primary']},
                         set(self.save.data['loadout'])-{'Jack Frost'})
        self.assertEqual(initial['credits'], self.save.data['credits'])
        app.key('\n')
        self.assertEqual(app.page,'battle')
        self.assertEqual(app._b_battle.persona,'Jack Frost')

    def test_blocked_story_roster_is_explicit_and_not_edited_on_inspect(self):
        self.before('cruiser-guests')
        data=self.save.data
        data['teammates']=list(dict.fromkeys([*data['teammates'],'Crow']))
        data['squad']=['Mona','Queen','Crow']
        self.save._commit(data)
        app=Surface(self.save)
        self.locate(app,'cruiser-guests')
        app.key('s')
        snapshot=self.path.read_bytes()
        for _ in range(len(data['teammates'])+1):
            view=app.capture(app.draw_squad)
            if 'Crow  /  Not on this operation' in view:break
            app.key(C.KEY_DOWN)
        self.assertIn('Crow  /  Not on this operation',view)
        self.assertIn('2/3 DEPLOY',view)
        app.i=['Joker',*TEAM].index('Crow')
        app.key('\n')
        self.assertIn('Crow',app.edit)
        app.key(ESC)
        self.assertEqual(snapshot,self.path.read_bytes())

    def test_optional_mural_persistence_and_review(self):
        self.before('pyramid-murals')
        app=Surface(self.save)
        self.locate(app,'pyramid-murals')
        original=self.path.read_bytes()
        app.key('\n')
        app.key('1')
        self.assertEqual(original,self.path.read_bytes())
        app.key(ESC)
        self.assertEqual(app.page,'brief')
        app.key('\n')
        app.key('1');app.key('2')
        self.assertEqual(Campaign(self.path).data['story_clues'],['pyramid-motif'])
        app.key(ESC)
        self.assertEqual(app.page,'brief')
        self.assertIn('C REVIEW CLUE',app.capture(app.brief))
        app.key('c')
        self.assertIn('A child holds a receiver',app.capture(lambda:app.story_scene.draw(app)))
        app.key('\n')
        self.assertIn('adult hand lays a statement',app.capture(lambda:app.story_scene.draw(app)))
        app.key(ESC)
        self.assertEqual(app.page,'brief')

    def test_castle_join_beat_first_clear_and_revisit_without_save(self):
        self.before('castle-gate')
        app=Surface(self.save)
        self.locate(app,'castle-gate')
        app.stage()
        app._b_battle.phase='win'
        app.record()
        app.page='result'
        self.assertNotIn('Panther',app.capture(app.result))
        after=Campaign(self.path).data
        self.assertEqual(after.pop('pending_story_after'),'castle-gate')
        self.assertNotIn('Panther',after['teammates'])
        app.key('\n')
        self.assertEqual(app.page,'story-scene')
        app.key('1');app.key('\n')
        self.assertEqual(app.page,'result')
        self.assertIn('Panther joined your roster • Standby',app.capture(app.result))
        after['teammates'].append('Panther')
        after['roster'].append('Panther')
        self.assertEqual(after,Campaign(self.path).data)
        after_bytes=self.path.read_bytes()
        self.locate(app,'castle-gate')
        self.assertIn('C REVISIT STORY',app.capture(app.brief))
        app.key('c')
        self.assertEqual(app.page,'story-scene')
        app.key(ESC)
        self.assertEqual(app.page,'brief')
        self.assertEqual(after_bytes,self.path.read_bytes())
