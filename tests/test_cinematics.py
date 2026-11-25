"""Coverage of all actual gallery art, timing and restoration of control."""
import curses
import re
from pathlib import Path
import tempfile
import unittest

from persona_terminal.persona5 import cinema
from persona_terminal.persona5 import cutins
from persona_terminal.persona5.animation_gallery import AnimationGallery
from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona5.campaign_state import Campaign
from persona_terminal.persona5.wrestling_scene import HEIGHT, WIDTH
from .test_animation_gallery import Surface


def plain(rows):
    return '\n'.join(''.join(run for run,_ in row) for row in rows)


class BoundedSurface(Surface):
    def put(self, y, x, text, *attributes):
        assert 0 <= y < self.h and 0 <= x < self.w
        assert x+len(text) <= self.w, (y,x,text)
        self.out.append(text)


class CinematicTests(unittest.TestCase):
    def test_one_authored_animation_per_showtime_and_allout(self):
        cards = (*cutins.SHOWTIMES.values(), *cutins.ALL_OUT.values(), cutins.ORACLE,
                 cutins.ORACLE_SUPPORT, cutins.FINAL_GUARD)
        self.assertEqual(len(cards),20)
        last_frames = set()
        inks = {'queen','noir','foe','rope','rail','face','dim','flash',
                'red','gold','cyan','green','white'}
        with tempfile.TemporaryDirectory() as d:
            app = BoundedSurface(Campaign(Path(d)/'absent.json'))
            for title,subtitle in cards:
                with self.subTest(title=title):
                    seconds, render = cinema.get(title)
                    self.assertEqual(seconds, cutins.duration(title))
                    self.assertGreater(seconds,cutins.CUTIN_SECONDS)
                    frames = set()
                    for n in range(31):
                        t = seconds*n/31
                        beat,rows = render(t)
                        frame = plain(rows)
                        frames.add(frame)
                        self.assertTrue(frame.isascii())
                        self.assertIsNone(re.search(r'[A-Za-z]{3,}', frame), frame)
                        self.assertEqual(len(rows),HEIGHT)
                        self.assertTrue(all(sum(len(run) for run,_ in row) == WIDTH for row in rows))
                        self.assertTrue(all(ink in inks for row in rows for _,ink in row))
                        for w,h in ((65,25),(100,34),(120,40)):
                            app.w,app.h=w,h
                            app.out.clear()
                            app.draw_cutin(title,t,finishing=False)
                            self.assertTrue(app.out)
                            self.assertNotIn(title,app.out)
                            if beat:
                                self.assertNotIn(beat,app.out)
                            self.assertIsNone(re.search(r'[A-Z]{3,}', ' '.join(app.out)))
                    self.assertGreaterEqual(len(frames),7)
                    final = plain(render(seconds-.12)[1])
                    self.assertNotIn(final,last_frames)
                    last_frames.add(final)
        self.assertEqual(len(last_frames),20)

    def test_allout_replay_and_old_preview_no_save_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            save = Path(d)/'slot.json'
            app = Surface(Campaign(save))
            app.story.new_game()
            before=save.read_bytes()
            g=AnimationGallery()
            g.key(app,curses.KEY_RIGHT,now=0)
            g.key(app,'9',now=1)
            self.assertEqual(g.clip.title,cutins.ALL_OUT['Violet'][0])
            g.key(app,'r',now=2)
            g.draw(app,now=3.23)
            self.assertEqual(g.started,2)
            g.key(app,ESC,now=3.24)
            self.assertIsNone(g.started)
            g.key(app,curses.KEY_RIGHT,now=3.25)
            g.key(app,'3',now=4)
            self.assertEqual(g.clip.title,cutins.ORACLE[0])
            app.out.clear()
            g.draw(app,now=6.1)
            self.assertTrue(app.out)
            self.assertNotIn(cutins.ORACLE[0],app.out)
            g.draw(app,now=9)
            self.assertIsNone(g.started)
            self.assertEqual(save.read_bytes(),before)

    def test_live_allout_uses_actor_cut_and_ufo_keeps_existing_impact(self):
        from persona_terminal.persona5.battle_engine import Battle
        for oracle,actor,title in ((False,'Queen',cutins.ALL_OUT['Queen'][0]),
                                  (True,'Queen',cutins.ORACLE[0])):
            with self.subTest(oracle=oracle), tempfile.TemporaryDirectory() as d:
                b=Battle(('Queen','Noir'),'All-Out test',seed=1,shuffle_turns=False,
                         encounter_config={'waves':[['Bicorn','Silky']], 'party_size':3,
                                           'oracle_features':('ufo',) if oracle else ()})
                self.assertIsNone(b.act('guard'))
                self.assertEqual(b.actor.name,actor)
                foes=list(b.enemies)
                for foe in foes:foe.hp=5;foe.down=True
                b.one_more=True
                app=Surface(Campaign(Path(d)/'slot.json'))
                app.battle_init()
                app._b_battle=b
                app._b_apply('allout')
                self.assertEqual(app._b_cut_in[0],title)
                self.assertEqual(b.phase,'win')
                self.assertTrue(all(foe.hp==0 for foe in foes))
                self.assertEqual(sum('All-Out Attack!' in log for log in b.log),1)
                app.battle_key(' ')
                self.assertIsNone(app._b_cut_in)
                self.assertEqual(sum('All-Out Attack!' in log for log in b.log),1)
                self.assertTrue(all(app._b_hp_trails[foe][0] == 5 for foe in foes))

    def test_live_moral_support_cut_uses_new_art_once(self):
        from persona_terminal.persona5.battle_engine import Battle
        b=Battle(('Mona','Panther'),'Support test',seed=4,shuffle_turns=False,
                 encounter_config={'waves':[['Bicorn','Silky']], 'party_size':3,
                                   'oracle_features':('support',)})
        b.allies[1].hp=48
        with tempfile.TemporaryDirectory() as d:
            app=Surface(Campaign(Path(d)/'slot.json'))
            app.battle_init()
            app._b_battle=b
            for _ in range(10):
                app._b_apply('guard')
                if app._b_cut_in:
                    break
            self.assertEqual(app._b_cut_in[0],cutins.ORACLE_SUPPORT[0])
            self.assertTrue(b._support_used)
            app.draw_cutin(app._b_cut_in[0],1.1)
            self.assertTrue(app.out)
            self.assertNotIn(cutins.ORACLE_SUPPORT[0],app.out)
            app.battle_key(' ')
            self.assertIsNone(app._b_cut_in)
            self.assertEqual(sum('MORAL SUPPORT' in log for log in b.log),1)
