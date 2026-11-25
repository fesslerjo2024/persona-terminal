"""Checks for the rebuilt single-pair scene, not the unrecovered original."""
import tempfile
from pathlib import Path
import unittest

from animation_gallery import AnimationGallery
from battle_engine import Battle
from battle_ui import ESC
from cutins import CUTIN_SECONDS, duration, showtime
from campaign_state import Campaign
from test_animation_gallery import Surface
from wrestling_scene import BEATS, HEIGHT, SECONDS, TITLE, WIDTH, render


def flatten(frame):
    return '\n'.join(''.join(run for run,_ in row) for row in frame)


class WrestlingSceneTests(unittest.TestCase):
    def test_storyboard_bounds_motion_and_count(self):
        t = 0
        for end, label in BEATS:
            with self.subTest(label=label):
                beat, rows = render((t + end) / 2)
                self.assertEqual(beat, label)
                self.assertEqual(len(rows), HEIGHT)
                self.assertTrue(all(sum(len(run) for run,_ in row) == WIDTH for row in rows))
                self.assertTrue(flatten(rows).isascii())
            t = end
        self.assertNotEqual(render(1.9)[1], render(2.47)[1])
        self.assertNotEqual(render(4.57)[1], render(5.42)[1])
        for when, number in ((5.95,1), (6.62,2), (7.22,3)):
            s = flatten(render(when)[1])
            for n in range(1,4):
                self.assertEqual(f'[ {n} ]' in s,n <= number)

    def test_gallery_uses_scene_duration_without_touching_save(self):
        with tempfile.TemporaryDirectory() as folder:
            save = Path(folder) / 'story.json'
            app = Surface(Campaign(save))
            app.story.new_game()
            before = save.read_bytes()
            g = AnimationGallery()
            g.key(app,'6',now=0)
            self.assertEqual(g.clip.title,TITLE)
            g.draw(app,now=2.2)
            self.assertIn('03 / QUEEN: LARIAT',app.out)
            g.draw(app,now=SECONDS-.01)
            self.assertIn('09 / MATCH OVER',app.out)
            g.draw(app,now=SECONDS+.01)
            self.assertIsNone(g.started)
            self.assertEqual(save.read_bytes(),before)
            self.assertEqual(duration(showtime(('Mona','Panther'))[0]),CUTIN_SECONDS)

    def test_real_showtime_skip_preserves_single_impact(self):
        pair = ('Queen','Noir')
        for seed in range(25):
            b = Battle(pair,'Wrestling test',seed=seed,shuffle_turns=False,
                encounter_config={'waves':[['Bicorn','Silky']],
                    'party_size':3, 'available_thieves':('Joker',*pair),
                    'showtime_pairs':[pair]})
            self.assertIsNone(b.act('guard'))
            self.assertEqual(b.actor.name,'Queen')
            b._offer_showtime(baton=True)
            if b.actions('showtime'):
                break
        else:
            self.fail('No eligible Queen/Noir Showtime roll in seed set')
        with tempfile.TemporaryDirectory() as folder:
            app = Surface(Campaign(Path(folder)/'story.json'))
            app.battle_init()
            app._b_battle = b
            target = b.targets('showtime')[0]
            before = target.hp
            app._b_apply('showtime',target)
            self.assertEqual(app._b_cut_in[0],TITLE)
            self.assertAlmostEqual(app._b_cut_in[3]-app._b_cut_in[2],SECONDS)
            self.assertEqual(sum('Queen → SHOWTIME' in line for line in b.log),1)
            after = target.hp
            self.assertLess(after,before)
            self.assertNotIn(target,app._b_hp_trails)
            app.battle_key(ESC)
            self.assertIsNone(app._b_cut_in)
            self.assertEqual(target.hp,after)
            self.assertEqual(app._b_hp_trails[target][0],before)
