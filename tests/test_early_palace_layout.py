"""Approved Castle, Museum and Bank art remains tied to actual route state."""
import curses
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from persona_terminal.persona5.campaign_data import CHAPTERS
from persona_terminal.persona5.campaign_state import Campaign
from persona_terminal.persona5.palace_menu import map_view, renderers
from .test_palace_menu import RecordedSurface


class EarlyPalaceLayoutTests(TestCase):
    def setUp(self):
        td=TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.save=Path(td.name)/'disposable.json'

    def test_all_named_operations_stay_readable_at_both_sizes_in_practice(self):
        app=RecordedSurface(Campaign(self.save))
        app.begin_extra('practice')
        for app.w,app.h in ((65,25),(96,35)):
            for ch in range(3):
                app.ch=ch
                for app.pick in range(len(app.nodes())):
                    with self.subTest(size=(app.w,app.h),palace=ch,operation=app.pick):
                        app.reset()
                        app.draw_map()
                        for node in app.nodes():
                            self.assertTrue(any(6<=y<=app.h-8 and node['title'] in line
                                                for y,_,line,*_ in app.calls))
                        self.assertTrue(any(any('⠁'<=c<='⣿' for c in line)
                                            for y,_,line,*_ in app.calls if 6<=y<=app.h-8))
                    app.key('\n')
                    self.assertEqual(app.node['id'],app.nodes()[app.pick]['id'])
                    app.key('\x1b')
                    self.assertEqual(app.page,'map')
        self.assertFalse(self.save.exists())

    def test_locked_museum_frames_do_not_show_future_pictures(self):
        from persona_terminal.persona5.palace_early_themes import _painting
        store=Campaign(self.save)
        store.new_game()
        for node in CHAPTERS[0]['nodes']:
            store.clear(node['id'],'B')
        app=RecordedSurface(store)
        app.key('1')
        self.assertEqual(CHAPTERS[app.ch]['id'],'museum')
        app.pick=2
        save=self.save.read_bytes()
        with patch('persona_terminal.persona5.palace_early_themes._painting',wraps=_painting) as art:
            app.draw_map()
        self.assertEqual(art.call_count,1)  # One unlocked painting; five identical draped mounts.
        text='\n'.join(app.out)
        self.assertIn('???',text)
        self.assertNotIn(app.nodes()[2]['title'],text)
        self.assertEqual(self.save.read_bytes(),save)

    def test_bank_select_moves_brass_needle_without_writing_progress(self):
        app=RecordedSurface(Campaign(self.save))
        app.begin_extra('practice')
        app.ch,app.pick=2,0

        def dial(now):
            app.reset()
            view=map_view(app,now)
            renderers()['bank'](app,view)
            pane=tuple((y,x,run,c) for y,x,run,c,*_ in app.calls
                       if x+len(run)<app.w*.42 and all('⠁'<=ch<='⣿' for ch in run))
            self.assertTrue(pane)
            return pane

        start=dial(1.)
        app.key(curses.KEY_DOWN)
        first=dial(2.)
        self.assertEqual((app.pick,map_view(app,2.).previous),(1,0))
        sweep=dial(2.16)
        settled=dial(3.)
        self.assertNotEqual(start,settled)
        self.assertNotEqual(first,sweep)
        self.assertNotEqual(sweep,settled)
        self.assertFalse(self.save.exists())
