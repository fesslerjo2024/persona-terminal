"""Live cue repeat preference never changes a battle, save or gallery playback."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

import cutins
from animation_gallery import AnimationGallery
from battle_engine import Battle
from battle_ui import ESC,SHORT_REPEAT_RATE
from campaign_state import Campaign
from test_animation_gallery import Surface


class CutinPacingTests(TestCase):
    def setUp(self):
        temp=TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)/'test-slot.json'
        self.app=Surface(Campaign(self.path))
        self.app.page='battle'
        self.app.battle_init()
        self.app._b_battle=Battle(('Mona','Skull'),'Test',seed=1,shuffle_turns=False,
                                  encounter_config={'waves':[['Bicorn']],'party_size':3})
        self.app._b_screen='command'
        self.title=cutins.ALL_OUT['Joker'][0]
        self.cue=cutins.CutCue(*cutins.ALL_OUT['Joker'],False,('Joker','Mona'),1)
        self.seconds=cutins.duration(self.title)

    def option(self,state):
        self.app.out.clear()
        self.assertTrue(self.app.battle_key('?'))
        self.app._b_over()
        self.assertTrue(any('C REPEATS: '+state in row for row in self.app.out))
        self.assertTrue(self.app.battle_key('c'))
        self.assertTrue(self.app.battle_key(ESC))

    def start(self,now,cue=None):
        self.app._b_start_cut(cue or self.cue,now)
        return self.app._b_cut_in[3]-now

    def test_skip_first_no_shortening_then_completion_allows_opt_in(self):
        app=self.app
        self.option('FULL')
        self.assertAlmostEqual(self.start(1),self.seconds)
        with patch('battle_ui.time.monotonic',return_value=1.25):
            self.assertTrue(app.battle_key(' '))
        self.assertIsNone(app._b_cut_in)
        self.assertAlmostEqual(self.start(2),self.seconds)
        app._b_release_cut(2+self.seconds+.01)
        self.assertAlmostEqual(self.start(5),self.seconds/SHORT_REPEAT_RATE)
        with patch('battle_ui.time.monotonic',return_value=5.5),patch.object(app,'draw_cutin') as draw:
            app.battle_page()
        draw.assert_called_once_with(self.title,.5*SHORT_REPEAT_RATE,finishing=False,
                                     cast=('Joker','Mona'),targets=1)
        app._b_release_cut(5.51)
        self.option('SHORT')
        self.assertAlmostEqual(self.start(10),self.seconds)
        self.assertFalse(self.path.exists())

    def test_completed_full_clip_repeats_default_full_and_gallery_independent(self):
        app=self.app
        self.start(0)
        app._b_release_cut(self.seconds)
        self.assertAlmostEqual(self.start(4),self.seconds)
        app._b_release_cut(4.25)
        self.option('FULL')
        # Full finishers are never shortened, even if already viewed. An
        # ordinary practice view cannot collapse a first story view either.
        finishing=cutins.CutCue(*cutins.ALL_OUT['Joker'],True)
        self.assertAlmostEqual(self.start(8,finishing),self.seconds)
        app._b_release_cut(8+self.seconds+.01)
        self.assertAlmostEqual(self.start(9,finishing),self.seconds)
        app._b_release_cut(9.25)
        app.testing=True
        self.assertAlmostEqual(self.start(9),self.seconds)
        app._b_release_cut(9.25)
        app.testing=False
        app.battle_init()  # New mission: preference still applies in-session.
        self.assertAlmostEqual(self.start(10),self.seconds/SHORT_REPEAT_RATE)
        gallery=AnimationGallery()
        gallery.group=1
        self.assertEqual(gallery.clip.title,self.title)
        self.assertAlmostEqual(gallery.clip.duration,self.seconds)
        self.assertFalse(self.path.exists())

    def test_duplicate_nonfinishing_clip_surfaces_short_setting_without_using_turn(self):
        app=self.app
        self.start(0)
        app._b_release_cut(self.seconds+.01)
        app._b_arena()
        self.assertFalse(any('C SHORT REPEATS' in msg for msg in app.out))
        app.out.clear()
        self.start(10)
        app._b_release_cut(10+self.seconds+.01)
        app._b_arena()
        self.assertTrue(any('C SHORT REPEATS' in msg for msg in app.out))
        b=app._b_battle
        before=(b.log[:],b.actor,b.round,dict(b.items))
        app.key('c')
        self.assertTrue(app._b_short_repeats)
        self.assertEqual((b.log,b.actor,b.round,b.items),before)
        self.assertAlmostEqual(self.start(20),self.seconds/SHORT_REPEAT_RATE)

    def test_seen_wave_ending_is_short_but_true_final_blow_is_full(self):
        app=self.app
        cue=cutins.CutCue(*cutins.ALL_OUT['Joker'],True,('Joker','Mona'),1)
        b=app._b_battle
        def wave_cue(now,phase):
            b.cut_in=cue;b.wave+=1;b.phase=phase
            app._b_present_action(b,b.wave-1,b.enemies,now)
            return app._b_cut_in[3]-now
        self.assertAlmostEqual(wave_cue(0,'turn'),self.seconds)
        app._b_release_cut(self.seconds+.01)
        app._b_short_repeats=True
        self.assertAlmostEqual(wave_cue(10,'turn'),self.seconds/SHORT_REPEAT_RATE)
        app._b_release_cut(10+self.seconds+.01)
        self.assertAlmostEqual(wave_cue(20,'win'),self.seconds)

    def test_release_starts_next_cue_once_without_action(self):
        app=self.app
        self.option('FULL')
        self.start(0)
        app._b_release_cut(self.seconds+.01)
        self.assertAlmostEqual(self.start(4),self.seconds/SHORT_REPEAT_RATE)
        app._b_cut_queue=[cutins.CutCue(*cutins.ORACLE_SUPPORT)]
        before=app._b_battle.log[:]
        with patch('battle_ui.time.monotonic',return_value=4.2):
            self.assertTrue(app.battle_key('\n'))
            self.assertEqual(app._b_cut_in[0],cutins.ORACLE_SUPPORT[0])
            self.assertFalse(app._b_cut_queue)
            self.assertAlmostEqual(app._b_cut_in[3]-4.2,cutins.duration(cutins.ORACLE_SUPPORT[0]))
            self.assertTrue(app.battle_key(ESC))
        self.assertIsNone(app._b_cut_in)
        self.assertEqual(app._b_battle.log,before)
