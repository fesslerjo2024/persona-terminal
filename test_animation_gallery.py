import curses as C
from pathlib import Path
import re
import tempfile
import unittest

from animation_gallery import AnimationGallery
from battle_ui import ESC
from campaign import CampaignApp
from campaign_state import Campaign
from cutins import duration


class Surface(CampaignApp):
    w, h = 65, 25

    def __init__(self, story):
        super().__init__(None, story)
        self.out = []

    def put(self, y, x, text, color=None, b=False, reverse=False):
        self.out.append(str(text))


class GalleryTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.save = self.root / 'slot.json'
        self.app = Surface(Campaign(self.save))

    def test_title_shortcuts_back_and_save_untouched(self):
        self.app.story.new_game()
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        self.assertTrue(self.app.key('4'))
        self.assertEqual((self.app.page,self.app.i), ('gallery',3))
        self.app.gallery.key(self.app, '\n', now=0)
        self.app.gallery.draw(self.app, now=0.2)
        self.assertTrue(self.app.out)
        self.assertNotIn('ROSE & REVOLVER', ' '.join(self.app.out))
        self.assertTrue(self.app.key(ESC))  # Leave the preview first.
        self.assertEqual(self.app.page, 'gallery')
        self.assertTrue(self.app.key(ESC))
        self.assertEqual(self.app.page, 'title')
        self.assertFalse(self.app.key('5'))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_reel_renders_every_unique_clip_at_minimum_terminal_size(self):
        g = AnimationGallery()
        self.assertEqual([len(group) for _,group in g.groups], [8,9,3,2])
        self.assertEqual(len({c.title for _, group in g.groups for c in group}),22)
        self.assertTrue(g.key(self.app, 'p', now=0))
        titles = []
        now = 0
        while g.started is not None:
            c = g.clip
            titles.append(c.title)
            self.app.out.clear()
            g.draw(self.app, now=now+0.6)
            self.assertTrue(self.app.out)
            self.assertFalse(re.search(r'[A-Z]{3,}', ' '.join(self.app.out)))
            if c.hp:self.assertTrue(any('▓' in s for s in self.app.out))
            now += 2.1 if c.hp else duration(c.title)+0.03
            g.draw(self.app, now=now)
        self.assertEqual(titles, [c.title for _,group in g.groups for c in group])
        self.assertFalse(g.reel)
        self.assertFalse(self.save.exists())

    def test_navigation_replay_and_skip(self):
        g = AnimationGallery()
        g.key(self.app,C.KEY_LEFT,now=0)
        g.key(self.app,C.KEY_DOWN,now=0)
        self.assertEqual(g.clip.title, 'FINAL HIT / WAVE CLEAR')
        g.key(self.app,'\n',now=1)
        g.key(self.app,'r',now=1.6)
        self.assertEqual(g.started,1.6)
        self.app.out.clear()
        g.draw(self.app,now=3.28)
        self.assertEqual(sum(' ( * * ) ' == row for row in self.app.out),3)
        self.assertNotIn('WAVE CLEARED', ' '.join(self.app.out))
        self.assertTrue(g.key(self.app, ESC, now=3.3))
        self.assertIsNone(g.started)
        self.assertFalse(g.key(self.app, ESC, now=3.3))
