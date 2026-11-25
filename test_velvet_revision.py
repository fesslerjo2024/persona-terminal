import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from battle_ui import ENTER, ESC
from campaign import CampaignApp
from campaign_data import NODES
from campaign_state import Campaign, CampaignError, TestingCampaign


class VelvetRevisionTests(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory(prefix='persona-revision-')
        self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/'disposable-story.json'
        self.story=Campaign(self.path)
        self.story.new_game()

    def prefix(self,through):
        for node in NODES:
            self.story.clear(node['id'],'B')
            if node['id']==through:break

    def reward_build(self):
        self.prefix('museum-security')
        self.story.apply_skill_card('High Pixie','Dia')
        self.story.equip_personas(('High Pixie','Arsène','Pixie'),primary='High Pixie')

    def app(self):
        app=CampaignApp(None,self.story,seed=3)
        app.w,app.h=65,25
        rows=[]
        app.put=lambda y,x,text,*args:rows.append((y,x,str(text)))
        return app,rows

    def choose_inheritance(self,app,skill):
        app.sub=next(i for i,(_,x) in enumerate(app.donor_options()) if x==skill)

    def test_reward_registered_lead_card_protected_cancel_then_confirm(self):
        self.reward_build()
        app,rows=self.app()
        raw=self.path.read_bytes()
        app.open_velvet('map')
        app.key(ESC)  # Dismiss the entrance, not the room.
        app.key('1')
        self.choose_inheritance(app,'Cleave')
        app.key('f')
        self.assertEqual(app.page,'refuse')
        app.draw_refuse()
        body=' '.join(row for _,_,row in rows)
        for text in ('CONFIRM RE-FUSION','135','Gain: Cleave','Lose: none','Keep learned skills: Dia'):
            self.assertIn(text,body)
        self.assertEqual(self.path.read_bytes(),raw)
        before=self.story.data
        app.key(ESC)
        self.assertEqual(app.page,'fusion')
        self.assertEqual(self.path.read_bytes(),raw)
        app.key('f')
        app.key(ENTER[0])
        self.assertEqual(app.page,'velvet')
        after=Campaign(self.path).data
        self.assertEqual(after['credits'],before['credits']-135)
        self.assertEqual(after['loadout'],before['loadout'])
        self.assertEqual(after['primary'],'High Pixie')
        self.assertEqual(after['personas']['High Pixie'],['Dia','Cleave'])
        self.assertEqual(after['fusion_skills'],{'High Pixie':'Cleave'})
        self.assertEqual(after['skill_cards'],before['skill_cards'])

    def test_revise_only_tracked_move_and_atomic_failure(self):
        self.reward_build()
        self.story.fuse('High Pixie','Cleave','Arsène',revise=True)
        preview=self.story.fusion_preview('High Pixie','Eiga','Arsène')
        self.assertEqual((preview['preserved'],preview['gains'],preview['losses']),
                         (['Dia'],['Eiga'],['Cleave']))
        raw=self.path.read_bytes();before=self.story.data
        with self.assertRaisesRegex(CampaignError,'Confirm re-fusion'):
            self.story.fuse('High Pixie','Eiga','Arsène')
        with patch('campaign_state._write',side_effect=OSError('witness disk-write failure')):
            with self.assertRaisesRegex(CampaignError,'witness disk-write failure'):
                self.story.fuse('High Pixie','Eiga','Arsène',revise=True)
        self.assertEqual(self.path.read_bytes(),raw)
        self.assertEqual(self.story.data,before)
        self.story.fuse('High Pixie','Eiga','Arsène',revise=True)
        reloaded=Campaign(self.path)
        self.assertEqual(reloaded.data['primary'],'High Pixie')
        self.assertEqual(reloaded.data['personas']['High Pixie'],['Dia','Eiga'])
        self.assertEqual(reloaded.data['fusion_skills'],{'High Pixie':'Eiga'})
        raw=self.path.read_bytes()
        with self.assertRaisesRegex(CampaignError,'No change'):
            reloaded.fuse('High Pixie','Eiga','Arsène',revise=True)
        self.assertEqual(self.path.read_bytes(),raw)

    def test_legacy_unclassified_full_protected(self):
        self.reward_build()
        payload=json.loads(self.path.read_bytes())
        self.assertNotIn('fusion_skills',payload)
        # Five base + three unclassified moves already fill the legacy cap.
        extras=['Dia','Cleave','Eiha']
        payload['personas']['High Pixie']=extras
        self.path.write_text(json.dumps(payload))
        raw=self.path.read_bytes()
        known=Campaign(self.path)
        self.assertEqual(known.status,'ready')
        self.assertEqual(known.fusion_preview('High Pixie','Eiga','Arsène')['preserved'],extras)
        with self.assertRaisesRegex(CampaignError,'No free skill slot'):
            known.fuse('High Pixie','Eiga','Arsène',revise=True)
        self.assertEqual(self.path.read_bytes(),raw)

    def test_new_fuse_and_testing_practice_keep_shared_state(self):
        app,_=self.app();story_before=self.path.read_bytes()
        app.start_testing()
        full=app.store;old_data=full.data
        self.assertIn('High Pixie',old_data['personas'])
        app.open_velvet('map')
        app.key(ESC)  # Dismiss the entrance, not the room.
        app.key('x')
        self.assertIsNot(app.store,full)
        self.assertNotIn('High Pixie',app.store.data['personas'])
        app.key('1');self.choose_inheritance(app,'Cleave');app.key('f')
        self.assertEqual(app.page,'registered')
        self.assertEqual(app.store.data['personas']['High Pixie'],['Cleave'])
        app.key(ESC);app.key(ESC)
        self.assertIs(app.store,full)
        self.assertEqual(app.store.data,old_data)
        self.assertEqual(self.path.read_bytes(),story_before)

    def test_escape_clears_failed_notice_and_view_does_not_write(self):
        app,_=self.app();before=self.path.read_bytes()
        app.open_velvet('map')
        app.key(ESC)  # Dismiss the entrance, not the room.
        app.key('1');app.key('f')
        self.assertIn('Insufficient credits',app.notice)
        app.key(ESC);app.key(ESC)
        self.assertEqual(app.page,'map');self.assertEqual(app.notice,'')
        self.assertEqual(self.path.read_bytes(),before)


if __name__=='__main__':unittest.main()
