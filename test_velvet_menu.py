"""Keep the native entrance separate from actual Velvet menu input."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
import curses as C

from battle_ui import ENTER, ESC
from campaign import CampaignApp
from campaign_data import NODES
from campaign_state import Campaign
from velvet_entrance import DURATION
from velvet_menu import BLUE


class VelvetMenuTests(TestCase):
    def make_app(self,w=65,h=25):
        folder=TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path=Path(folder.name)/'fixture.json'
        c=Campaign(path)
        c.new_game()
        for node in NODES:
            c.clear(node['id'],'B')
            if node['id']=='museum-security':break
        app=CampaignApp(None,c)
        app.w,app.h=w,h
        cells=[]
        app.put=lambda y,x,text,color=None,*args:cells.append((y,x,str(text),color))
        return app,path,cells

    def test_all_outside_entries_and_consumed_skip_keys(self):
        for source,key in [('map',ESC),('brief',ENTER[0]),('result',' ')]:
            with self.subTest(source=source):
                app,path,cells=self.make_app()
                app.page=source
                if source=='result':app._b_battle=SimpleNamespace(phase='win')
                before=path.read_bytes()
                app.key('v')
                self.assertEqual(app.page,'velvet-entrance')
                app.key('1')  # Unrelated input is ignored during the scene.
                self.assertEqual((app.page,app.i),('velvet-entrance',0))
                app.key(key)
                self.assertEqual((app.page,app.i),('velvet',0))
                self.assertIsNone(app.velvet_started)
                self.assertEqual(app.tab,int(source=='result'))
                self.assertEqual(path.read_bytes(),before)
                app.key(ESC)
                self.assertEqual(app.page,source)

    def test_animation_renders_current_viewport_and_expires_without_input(self):
        app,path,cells=self.make_app(96,34)
        before=path.read_bytes()
        for w,h in [(96,34),(65,25)]:
            app.w,app.h=w,h
            with patch('campaign.time.monotonic',return_value=10):
                app.open_velvet('map')
            cells.clear()
            with patch('campaign.time.monotonic',return_value=11):
                app.draw_velvet_entrance()
            self.assertTrue(any(color==BLUE for _,_,_,color in cells))
            self.assertTrue(all(y<h and x+len(run)<w for y,x,run,_ in cells))
            self.assertEqual(app.page,'velvet-entrance')
            with patch('campaign.time.monotonic',return_value=10+DURATION+.02):
                app.draw_velvet_entrance()
            self.assertEqual(app.page,'velvet')
            self.assertTrue(any('VELVET ROOM' in run for _,_,run,_ in cells))
        self.assertEqual(path.read_bytes(),before)

    def test_responsive_chrome_on_live_submenus_and_footer_is_not_last_line(self):
        for w,h in [(65,25),(96,34)]:
            app,path,cells=self.make_app(w,h)
            raw=path.read_bytes()
            app.open_velvet('map')
            app.key(ESC)
            app.draw_velvet()
            self.assertTrue(any('High Pixie  135 cr' in run for _,_,run,_ in cells))
            self.assertTrue(any('ENTER PREVIEW' in run and y==h-2 for y,_,run,_ in cells))
            self.assertTrue(any('╔' in run and color==BLUE for _,_,run,color in cells))
            app.key('1')
            self.assertEqual(app.page,'fusion')
            cells.clear();app.draw_fusion()
            self.assertTrue(any('FUSION PREVIEW' in run for _,_,run,_ in cells))
            self.assertTrue(any('ESC BACK' in run and y==h-2 for y,_,run,_ in cells))
            app.key(ESC)
            self.assertEqual(app.page,'velvet')
            app.key(C.KEY_RIGHT)
            app.key('a')
            self.assertEqual(app.page,'cards')
            cells.clear();app.draw_cards()
            self.assertTrue(any('SKILL CARDS' in run for _,_,run,_ in cells))
            self.assertTrue(all(y<h-1 and x+len(run)<w for y,x,run,_ in cells))
            self.assertEqual(path.read_bytes(),raw)
