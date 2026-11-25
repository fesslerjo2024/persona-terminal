"""The final debrief and reloaded map show completion without a new save flag."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase

from campaign import CampaignApp
from campaign_data import NODES
from campaign_state import Campaign, TestingCampaign


class CampaignCompletion(TestCase):
    def app(self, store):
        app=CampaignApp(None,store,seed=7)
        app.w,app.h=65,25
        rows=[]
        app.put=lambda y,x,text,*_args:rows.append((y,x,str(text)))
        app.ch=len(app.chapters)-1
        app.pick=len(app.nodes())-1
        app.node=app.nodes()[-1]
        return app,rows

    def test_completion_from_verified_clears_no_new_save_flag(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'isolated.json'
            saved=Campaign(path)
            saved.new_game()
            for node in NODES[:-1]:
                saved.clear(node['id'],'B')
            app,rows=self.app(saved)
            app.draw_map()
            self.assertIsNone(app.completed_operations())
            self.assertFalse(any('CAMPAIGN COMPLETE' in text for _,_,text in rows))
            app.reward=saved.clear(NODES[-1]['id'],'S')
            before=path.read_bytes()
            app.first=True
            app.grade='S'
            app._b_battle=SimpleNamespace(phase='win')
            app.result()
            self.assertTrue(any('LABORATORY SECURED' in text for _,_,text in rows))
            self.assertIn((6,3,'CAMPAIGN COMPLETE  /  53/53 OPERATIONS'),rows)
            reopened,lines=self.app(Campaign(path))
            reopened.draw_map()
            self.assertTrue(any('CAMPAIGN COMPLETE • 53/53' in text for _,_,text in lines))
            self.assertEqual(before,path.read_bytes())

    def test_testing_never_claims_story_complete(self):
        app,rows=self.app(TestingCampaign())
        app.start_testing()
        app.ch=len(app.chapters)-1
        self.assertTrue(app.testing)
        app.draw_map()
        self.assertIsNone(app.completed_operations())
        self.assertFalse(any('CAMPAIGN COMPLETE' in text for _,_,text in rows))
        self.assertTrue(any('ALL 6 BATTLES OPEN' in text for _,_,text in rows))
