"""Render and keyboard regressions for the Pyramid cutaway route."""
import curses
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from battle_ui import ESC
from campaign_data import CHAPTERS, NODES
from campaign_state import Campaign
from palace_menu import map_view, renderers
from test_palace_menu import RecordedSurface


class PyramidMapTests(unittest.TestCase):
    def setUp(self):
        directory=TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path=Path(directory.name)/'fixture.json'
        self.chapter=next(i for i,c in enumerate(CHAPTERS) if c['id']=='pyramid')

    def text(self, app):
        rows=[list(' '*app.w) for _ in range(app.h)]
        for y,x,s,*_ in app.calls:
            self.assertGreaterEqual(y,6)
            self.assertLessEqual(y,app.h-8)
            self.assertLessEqual(x+len(s),app.w-1)
            rows[y][x:x+len(s)]=s
        return '\n'.join(''.join(row) for row in rows)

    def draw(self, app, now):
        app.reset()
        renderers()['pyramid'](app,map_view(app,now))
        return self.text(app)

    def test_testing_focus_traces_the_tunnel_and_moves_projection(self):
        app=RecordedSurface(Campaign(self.path))
        app.begin_extra('practice')
        app.ch=self.chapter
        for w,h in ((65,25),(96,34)):
            app.w,app.h=w,h
            app.pick=0
            start=self.draw(app,10.)
            self.assertIn('PREVIEW',start)
            self.assertIn('‹/\\›',start)
            app.key(curses.KEY_DOWN)
            self.assertEqual(app.pick,1)
            self.draw(app,11.)
            early=self.draw(app,11.05)
            finished=self.draw(app,12.)
            self.assertNotIn('‹/\\›',finished)
            self.assertIn('‹<>›',finished)
            self.assertLess(early.count('•'), finished.count('•'))
            self.assertIn('✦',finished)
            highlights=[s for _,_,s,_,_,reverse in app.calls if reverse]
            self.assertIn('Light Across the Chasm',highlights)
            self.assertEqual(len(highlights),2)  # title and doorway only
            title_rows={}
            for node in app.nodes():
                hits=[y for y,_,s,*_ in app.calls if node['title'] in s]
                self.assertEqual(len(hits),1)
                title_rows[node['id']]=hits[0]
            self.assertEqual(len(set(title_rows.values())),4)
            self.assertLess(title_rows['pyramid-boss'],title_rows['pyramid-desert'])
            app.key('6')
            self.assertEqual(app.node['id'],'pyramid-boss')
            app.key(ESC)
            self.assertEqual(app.page,'map')
        self.assertFalse(self.path.exists())

    def test_story_progress_restores_real_fragments_and_lights_next_open_route(self):
        store=Campaign(self.path)
        store.new_game()
        for node in NODES:
            if node['id']=='pyramid-desert':
                break
            store.clear(node['id'],'B')
        app=RecordedSurface(store)
        app.key('1')
        app.ch=self.chapter
        app.pick=1
        before_bytes=self.path.read_bytes()
        before=self.draw(app,1.)
        self.assertNotIn('PREVIEW',before)
        self.assertNotIn('[/\\]',before)
        self.assertIn('×',before)
        self.assertEqual(self.path.read_bytes(),before_bytes)

        # Only the real clear changes projection-independent route state.
        store.clear('pyramid-desert','S')
        app.pick=2  # Selection stays locked, but the next open route is lit.
        save=self.path.read_bytes()
        after=self.draw(app,2.)
        after=self.draw(app,3.)
        self.assertIn('[/\\]',after)
        self.assertIn('[S]',after)
        self.assertIn('◦',after)
        self.assertIn('×',after)
        self.assertNotIn('[<>]',after)
        self.assertEqual(save,self.path.read_bytes())
