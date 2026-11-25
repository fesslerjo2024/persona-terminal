"""Exercise startup input isolation and the live Calling Card landing."""
import curses
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona5.campaign_state import Campaign
from persona_terminal.persona5 import intro_calling_card as card
from .test_animation_gallery import Surface
from persona_terminal.persona5.title_scene import PRODUCT_TITLE, STARTUP_SECONDS


class ScriptedScreen:
    def timeout(self,ms):
        pass
    def __init__(self, app, inputs):
        self.app = app
        self.inputs = iter(inputs)
        self.frames = []
        self.at = 0
        self.app.out = []

    def erase(self):
        self.app.out.clear()

    def getmaxyx(self):
        return self.app.h, self.app.w

    def refresh(self):
        self.frames.append((self.app.page, self.app.i, '\n'.join(self.app.out)))

    def get_wch(self):
        self.at, key = next(self.inputs)
        if key is None:
            raise curses.error
        return key


class StartupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)/'disposable.json'

    def run_app(self, *inputs, ready=False, width=65, height=25):
        story = Campaign(self.path)
        if ready:
            story.new_game()
        before = self.path.read_bytes() if ready else None
        app = Surface(story)
        app.w, app.h = width, height
        screen = app.s = ScriptedScreen(app, inputs)
        with patch('persona_terminal.persona5.campaign.time.monotonic', side_effect=lambda: screen.at):
            app.run()
        if ready:
            self.assertEqual(self.path.read_bytes(), before)
        else:
            self.assertFalse(self.path.exists())
        return screen.frames

    def test_playing_startup_lands_once_on_working_title(self):
        frames = self.run_app((2, None), (card.DURATION+.2, None),
                              (STARTUP_SECONDS+.1, None), (7, '1'), (8, ESC), (9, 'q'),
                              ready=True, width=96, height=34)
        self.assertTrue(all(PRODUCT_TITLE not in frame for _,_,frame in frames[:3]))
        self.assertIn(PRODUCT_TITLE, frames[3][2])
        self.assertTrue(any(page == 'map' and 'CAMPAIGN SAVE LOADED' in frame
                            for page,_,frame in frames[4:]))
        self.assertFalse(any('ANIMATION GALLERY' in frame or 'TESTING MODE' in frame
                             or 'CLASSIC TRIALS' in frame for _,_,frame in frames))
        self.assertEqual(frames[-1][0],'title')
        self.assertIn(PRODUCT_TITLE, frames[-1][2])

    def test_enter_escape_or_space_skip_without_selecting_the_default(self):
        for skip in ('\n', ESC, ' '):
            with self.subTest(skip=skip):
                frames = self.run_app((.1, skip), (.22, 'q'))
                self.assertEqual(len(frames), 2)
                self.assertNotIn(PRODUCT_TITLE, frames[0][2])
                self.assertEqual(frames[1][:2], ('title',1))
                self.assertIn(PRODUCT_TITLE, frames[1][2])

    def test_second_enter_continues_existing_save_and_esc_returns_to_title(self):
        frames = self.run_app((.1, '\n'), (.3, '\n'), (.5, ESC), (.6, 'q'), ready=True)
        self.assertEqual([(page,index) for page,index,_ in frames],
                         [('title',0),('title',0),('map',0),('title',0)])
        self.assertIn('CAMPAIGN SAVE LOADED', frames[2][2])

    def test_geometry_at_minimum_and_wide_terminal(self):
        for w,h in ((65,25),(96,34),(120,40)):
            with self.subTest(size=(w,h)):
                app=Surface(Campaign(self.path))
                app.w,app.h=w,h
                with patch.object(app,'put',wraps=app.put) as put:
                    app.title()
                calls=[args for args,_ in put.call_args_list]
                self.assertEqual(sum(text == PRODUCT_TITLE for _,_,text,*_ in calls),1)
                self.assertEqual([y for y,x,text,*_ in calls if '↵ OPEN' in text],[h-2])
                self.assertTrue(all(0<=y<h and 0<=x<=x+len(text)<=w-1 for y,x,text,*_ in calls))
                art=card.render(card.DURATION,w-1,h)
                for row in art:
                    self.assertEqual(sum(len(run) for run,_ in row),w-1)
                flat='\n'.join(''.join(run for run,_ in row) for row in art)
                self.assertTrue(all(ch.isspace() or 0x2801<=ord(ch)<=0x28ff for ch in flat))
                self.assertIsNone(re.search(r'[A-Z]{3,}',flat))
                self.assertTrue(any(ink=='white' and any(0x2801<=ord(ch)<=0x28ff for ch in run)
                                    for row in art for run,ink in row))
