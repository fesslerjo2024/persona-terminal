import curses as C
from pathlib import Path
import re
import tempfile
import unittest

from animation_gallery import AnimationGallery
from battle_ui import ESC
from campaign import CampaignApp
from campaign_state import Campaign


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

    def test_extras_gallery_playback_returns_and_leaves_save_untouched(self):
        from unittest.mock import patch
        self.app.story.new_game()
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}

        def exercise(*,startup):
            self.assertFalse(startup)
            self.assertEqual(self.app.page, 'gallery')
            self.app.gallery.key(self.app, '\n', now=0)
            self.app.gallery.draw(self.app, now=0.2)
            self.assertTrue(self.app.out)
            self.assertNotIn('ROSE & REVOLVER', ' '.join(self.app.out))
            self.assertTrue(self.app.key(ESC))  # Leave the preview first.
            self.assertEqual(self.app.page, 'gallery')
            self.assertFalse(self.app.key(ESC))  # Return to the Extras caller.

        with patch.object(self.app, 'run', side_effect=exercise):
            self.app.run_extra('gallery')
        self.assertEqual(self.app.page, 'title')
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
            now += c.duration+0.03
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
        self.assertGreater(sum('⠁'<=ch<='⣿' for run in self.app.out for ch in run),100)
        self.assertNotIn('WAVE CLEARED', ' '.join(self.app.out))
        self.assertTrue(g.key(self.app, ESC, now=3.3))
        self.assertIsNone(g.started)
        self.assertFalse(g.key(self.app, ESC, now=3.3))

    def test_loop_replays_only_selected_clip_and_clears_on_leave(self):
        g = AnimationGallery()
        g.key(self.app,C.KEY_RIGHT,now=0)
        g.key(self.app,C.KEY_DOWN,now=0)
        chosen=g.clip
        g.key(self.app,'l',now=1)
        self.assertTrue(g.loop)
        self.assertFalse(g.reel)
        g.draw(self.app,now=chosen.duration+1.01)
        self.assertIs(g.clip,chosen)
        self.assertAlmostEqual(g.started,chosen.duration+1.01)
        g.key(self.app,'r',now=chosen.duration+1.11)
        self.assertAlmostEqual(g.started,chosen.duration+1.11)
        g.key(self.app,' ',now=chosen.duration+1.21)
        self.assertIsNone(g.started)
        self.assertFalse(g.loop)
        self.assertIs(g.clip,chosen)
        g.key(self.app,'L',now=20)
        self.assertTrue(g.key(self.app,ESC,now=20.1))
        self.assertFalse(g.loop)
        self.assertFalse(g.key(self.app,ESC,now=20.2))
        self.assertFalse(self.save.exists())

    def test_practice_and_gallery_remember_selections_without_touching_story(self):
        from unittest.mock import patch
        self.app.story.new_game()
        before=self.save.read_bytes()
        def move_map(*,startup):
            self.assertFalse(startup)
            self.assertTrue(self.app.testing)
            self.app.key(C.KEY_RIGHT)
            self.app.key(C.KEY_DOWN)
            self.assertEqual((self.app.ch,self.app.pick),(1,1))
            self.app.draw_map()
            self.assertNotIn('ANIMATION GALLERY', ' '.join(self.app.out))
            self.app.key('g')
            self.assertEqual(self.app.page,'map')
            self.assertFalse(self.app.key(ESC))
        def move_gallery(*,startup):
            self.app.key(C.KEY_RIGHT)
            self.app.key(C.KEY_DOWN)
            self.assertEqual((self.app.gallery.group,self.app.gallery.index),(1,1))
            self.assertFalse(self.app.key(ESC))
        def check_map(*,startup):
            self.assertEqual((self.app.ch,self.app.pick),(1,1))
            self.assertFalse(self.app.key(ESC))
        def check_gallery(*,startup):
            self.assertEqual((self.app.gallery.group,self.app.gallery.index),(1,1))
            self.assertFalse(self.app.key(ESC))
        for kind, action in (('practice',move_map),('gallery',move_gallery),
                             ('practice',check_map),('gallery',check_gallery)):
            with patch.object(self.app, 'run', side_effect=action):
                self.app.run_extra(kind)
            self.assertIs(self.app.store,self.app.story)
            self.assertFalse(self.app.testing)
        self.assertEqual(self.save.read_bytes(),before)

    def test_story_map_does_not_take_testing_gallery_shortcut(self):
        self.app.story.new_game()
        self.app.key('1')
        self.assertEqual(self.app.page,'map')
        self.app.key('g')
        self.assertEqual(self.app.page,'map')
        self.assertIsNone(self.app.gallery)

    def test_map_footer_and_classic_trials_escape_are_unambiguous(self):
        from unittest.mock import patch
        self.app.begin_extra('practice')
        with patch.object(self.app, 'put', wraps=self.app.put) as draw:
            self.app.draw_map()
        shortcuts=[args for args,_ in draw.call_args_list
                   if 'T CLASSIC TRIALS' in str(args[2])]
        self.assertEqual(len(shortcuts),1)
        self.assertEqual(shortcuts[0][0],self.app.h-2)
        self.assertIn('ESC EXTRAS',shortcuts[0][2])
        self.app.key('t')
        self.assertEqual(self.app.page,'trials')
        self.app.key('t')
        self.assertEqual(self.app.page,'trials')
        self.app.key(ESC)
        self.assertEqual(self.app.page,'map')
        self.app.key('t')
        self.app.key('s')
        battle=self.app._b_battle
        self.assertIsNotNone(battle)
        self.app.key(ESC)
        self.assertEqual(self.app.page,'map')
        self.app.key('t')
        self.assertEqual(self.app.page,'trials')
        self.assertIs(self.app._b_battle,battle)
        self.app.key(ESC)
        self.assertEqual(self.app.page,'map')
        self.assertFalse(self.app.key(ESC))
        self.assertFalse(self.save.exists())
