"""Showtime illustration uses native dots from combat and gallery entry paths."""
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

import cinema
import cutins
import native_showtime as showtime
from animation_gallery import AnimationGallery
from battle_engine import Battle
from campaign_state import Campaign
from test_animation_gallery import Surface


class NativeShowtimeTests(TestCase):
    def test_each_shot_has_its_own_moving_native_composition(self):
        motifs = {
            showtime.ROSE: ('Bouquet','Bomb','Flower burst'),
            showtime.ROAD: ('Handoff','Fist flurry','Crushed can'),
            showtime.BEEF: ('Chopsticks','Door breaks','Back to dinner'),
            showtime.DUEL: ('Draw','Parasol','Crossing blades'),
            showtime.DRIVE: ('Transformation','Launcher','Detonation'),
            showtime.RING: ('Tag','Dropkick','Body slam'),
            showtime.MASK: ('Berserk','Blade flurry','Gunshot'),
            showtime.DANCE: ('Echo','Dance','Final dip'),
        }
        for title, expected in motifs.items():
            with self.subTest(title=title):
                self.assertEqual(cinema.duration(title), cinema.get(title)[0])
                phases = showtime.REELS[title].stages
                self.assertEqual([label for _, label in phases if label in expected],list(expected))
                for w,h in ((64,25),(119,40)):
                    frames=set()
                    start=0.
                    for end,phase in phases:
                        t=(start+end)/2
                        cue,runs=cinema.paint(title,t,w,h)
                        self.assertEqual(cue,phase)
                        flat=''.join(run for row in runs for run,_ in row)
                        self.assertEqual(len(flat),w*h)
                        self.assertGreater(len(set(flat)&set(map(chr,range(0x2801,0x28ff)))),18)
                        self.assertIsNone(re.search(r'[^ \u2801-\u28ff]',flat))
                        frames.add(flat)
                        start=end
                    self.assertEqual(len(frames),len(phases))

    def test_gallery_and_live_battle_paint_the_same_native_shots(self):
        with TemporaryDirectory() as temp:
            save=Path(temp)/'disposable.json'
            app=Surface(Campaign(save))
            gallery=AnimationGallery()
            app.page='battle'
            app.battle_init()
            for i,(members, (title, _)) in enumerate(cutins.SHOWTIMES.items()):
                with self.subTest(title=title):
                    roster=tuple(n for n in cutins.ALL_OUT if n in members)
                    allies=tuple(n for n in roster if n!='Joker')
                    app.battle_init()
                    b=app._b_battle=Battle(allies,'Showtime rendering',seed=1,shuffle_turns=False,
                                         encounter_config={'waves':[['Bicorn']],'party_size':len(allies)+1,
                                                           'showtime_pairs':(roster,),
                                                           'available_thieves':roster})
                    app._b_screen='command'
                    gallery.index=i
                    gallery.started=0.
                    gallery.draw(app,now=1.5)
                    parts=list(app.out)
                    app.out.clear()
                    b.one_more=True   # Provide the combat condition that permits Baton Pass.
                    with patch.object(b._showtime_rng,'random',return_value=0.):
                        app._b_apply('pass:'+allies[0])
                    self.assertTrue(b.actions('showtime'))
                    target=b.targets('showtime')[0]
                    before=target.hp
                    with patch('battle_ui.time.monotonic',return_value=0.):
                        app._b_apply('showtime',target)
                    self.assertLess(target.hp,before)
                    self.assertEqual(app._b_cue.title,title)
                    with patch('battle_ui.time.monotonic',return_value=1.5):
                        app.battle_page()
                    self.assertEqual(app.out,parts)
                    self.assertGreater(sum('⠁'<=ch<='⣿' for run in app.out for ch in run),500)
                    app.out.clear()
            self.assertFalse(save.exists())
