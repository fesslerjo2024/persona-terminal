"""Keep the gallery menu compact without touching authored frames or saves."""
import curses
import unittest

from animation_gallery import AnimationGallery
from battle_ui import BattleUI, ESC


class Surface(BattleUI):
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.calls = []

    def frame(self, title, controls):
        self.calls.append((1, 0, title))
        self.calls.append((self.h-2, 0, controls))

    def put(self, y, x, text, *args):
        self.calls.append((y, x, text))

    def nav(self, key, index, count):
        return self._b_nav(key, index, count)

    def commit(self, key, index, count):
        return self._b_commit(key, index, count)


class GalleryBaselineTests(unittest.TestCase):
    def test_every_group_fits_at_minimum_with_one_label_control_row_and_no_copy(self):
        for w, h in ((65, 25), (96, 34)):
            app = Surface(w, h)
            gallery = AnimationGallery()
            for group in range(len(gallery.groups)):
                app.calls.clear()
                gallery.draw(app, now=0)
                strings = [line for _,_,line in app.calls]
                self.assertEqual(sum('ANIMATION GALLERY' in line for line in strings), 1)
                self.assertEqual(sum('ESC BACK' in line for line in strings), 1)
                self.assertNotIn('R REPLAY', ' '.join(strings))
                for y,x,line in app.calls:
                    self.assertLessEqual(x+len(line), w-1)
                    self.assertLess(y,h)
                for clip in gallery.clips:
                    row, = [line for line in strings if clip.title in line]
                    if clip.duo:
                        self.assertIn(' + '.join(clip.duo), row)
                    self.assertEqual('Preview only' in row, clip.title == 'ORACLE // FINAL GUARD')
                gallery.key(app, curses.KEY_RIGHT, now=0)
            self.assertFalse(gallery.key(app, ESC, now=0))
