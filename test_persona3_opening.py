"""Original spring-demo story beats and the native Dark Hour transition."""
import re
import unittest

from persona3_opening import BEATS, BY_ID, TRANSITION_SECONDS, render


class OpeningTests(unittest.TestCase):
    def test_calendar_has_spoiler_bounded_checkpoints_and_a_pre_climb_brief(self):
        expected = [
            ('arrival','04/06'), ('awakening','04/09'), ('briefing','04/20'), ('tartarus','04/20'),
            ('relay','04/21'), ('monorail','05/09'), ('finale','05/10'),
        ]
        self.assertEqual([(b.id,b.date) for b in BEATS],expected)
        self.assertTrue(all(BY_ID[b.id] is b for b in BEATS))
        self.assertTrue(all(2 <= len(b.lines) <= 3 for b in BEATS))
        early=' '.join(' '.join(b.lines) for b in BEATS)
        self.assertIn('Orpheus',early)
        self.assertIn('Mitsuru takes the radio',early)
        for forbidden in ('Fuuka','Theurgy'):
            self.assertNotIn(forbidden,early)

    def test_every_scene_is_native_exact_at_compact_and_wide(self):
        art=tuple(dict.fromkeys((*(b.art for b in BEATS),'dark_hour','dorm','thebel','velvet')))
        for w,h in ((64,25),(95,34),(28,12)):
            sampled=[]
            for key in art:
                with self.subTest(size=(w,h),key=key):
                    frame=render(key,.81,w,h)
                    self.assertEqual(len(frame),h)
                    self.assertTrue(all(sum(len(text) for text,_ in row)==w for row in frame))
                    self.assertTrue(any(text.strip() for row in frame for text,_ in row))
                    rebuilt=key!='dark_hour'
                    if rebuilt:
                        dots=sum(0x2801<=ord(ch)<=0x28ff for row in frame for text,_ in row for ch in text)
                        self.assertGreater(dots,w*h//5)
                    self.assertTrue(all((text.isascii() or rebuilt and all(ch.isascii() or 0x2801<=ord(ch)<=0x28ff for ch in text))
                                        and not re.search('[A-Za-z]{2,}',text if key!='dark_hour' else re.sub('[IVX]','',text))
                                        for row in frame for text,_ in row))
                    sampled.append(frame)
            self.assertEqual(len(set(sampled)),len(art)-1)  # First climb uses Thebel's same stairs.

    def test_transition_paces_multiple_clocks_and_freezes_at_midnight(self):
        def inks(frame):
            return {ink for row in frame for text,ink in row if text.strip()}

        def picture(frame):
            return '\n'.join(''.join(text for text,_ in row) for row in frame)

        for w,h in ((64,25),(95,34)):
            frames=[render('dark_hour',i*TRANSITION_SECONDS/35,w,h) for i in range(36)]
            self.assertGreaterEqual(len(set(frames)),18)
            before=render('dark_hour',1.42,w,h)
            struck=render('dark_hour',1.86,w,h)
            frozen=render('dark_hour',2.08,w,h)
            self.assertIn('XII',picture(before))
            self.assertIn('23:59',picture(before))
            self.assertIn('00:00',picture(struck))
            self.assertIn('00:00',picture(frozen))
            self.assertIn('white',inks(struck))
            self.assertNotIn('forest',inks(struck))
            # Distinct overlapping dials move towards the viewer.
            self.assertGreater(sum(text.count('|') for row in before for text,_ in row),
                               sum(text.count('|') for row in frames[0] for text,_ in row))
            self.assertIn('III',picture(before))
            self.assertIn('VI',picture(before))
            self.assertEqual(inks(frozen),{'green','forest'})
            for t in (2.25,TRANSITION_SECONDS,10):
                self.assertEqual(frozen,render('dark_hour',t,w,h))
            self.assertEqual(picture(struck),picture(frozen))  # Color changes, clocks don't break.

    def test_dorm_deploy_timeout_and_each_skip_keep_exact_save_bytes(self):
        from datetime import date
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        from battle_ui import ESC
        from persona3_app import P3App
        from persona3_calendar_ui import NIGHT_SWEEP_SECONDS, departure
        from persona3_state import P3Store

        with TemporaryDirectory() as d:
            path=Path(d)/'disposable.json'
            store=P3Store(path)
            store.new_game()
            store.commit(phase='calendar',day=date(2009,4,22),depth=1)
            before=path.read_bytes()
            app=P3App(None,store,seed=3)
            app.w,app.h=65,25
            for key in ('\n',ESC,' '):
                app.go('evening');app.key('\n')
                self.assertEqual(app.page,'dark-hour')
                app.key(key)
                self.assertEqual(app.page,'entrance')
                self.assertEqual(app.entrance_targets()[app.i][1],'05F / Continue ascent')
            app.go('evening');app.key('\n')
            with patch('persona3_app.time.monotonic',return_value=app.started+.86), \
                 patch.object(app,'draw_scene_rows') as paint:
                app.draw()
                paint.assert_called_once_with(departure(.86,64,25))
                self.assertEqual(app.page,'dark-hour')
            with patch('persona3_app.time.monotonic',return_value=app.started+NIGHT_SWEEP_SECONDS+.1), \
                 patch.object(app,'draw_entrance') as entrance:
                app.draw()
                entrance.assert_called_once()
                self.assertEqual(app.page,'entrance')
            self.assertEqual(path.read_bytes(),before)
