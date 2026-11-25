"""The themed surfaces do not change mission selection, locks, or saves."""
import curses
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from battle_ui import ESC
from campaign_data import CHAPTERS, NODES
from campaign_state import Campaign
from palace_menu import SKINS, map_view, renderers, airlock
from test_animation_gallery import Surface
from test_casino_route import at_casino


class RecordedSurface(Surface):
    def __init__(self, store):
        super().__init__(store)
        self.calls=[]

    def put(self,y,x,text,color=None,b=False,reverse=False):
        super().put(y,x,text,color,b,reverse)
        self.calls.append((y,x,str(text),color,b,reverse))

    def reset(self):
        self.calls.clear()
        self.out.clear()


class PalaceMenuTests(unittest.TestCase):
    def setUp(self):
        temp=TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)/'fixture.json'

    def test_all_nine_map_and_brief_designs_fit_and_are_different(self):
        app=RecordedSurface(Campaign(self.path))
        app.key('3')
        self.assertEqual(set(renderers()),{c['id'] for c in CHAPTERS})
        for size in ((65,25),(71,27),(96,25),(96,34),(120,40)):
            app.w,app.h=size
            samples=set()
            for ch in range(len(CHAPTERS)):
                id=CHAPTERS[ch]['id']
                app.ch=ch
                for selected in range(len(app.nodes())):
                    with self.subTest(size=size,chapter=id,operation=selected+1):
                        app.pick=selected
                        app.reset()
                        app.draw_map()
                        self.assertTrue(any(app.nodes()[selected]['title'] in s for s in app.out))
                        self.assertTrue(all(0<=y<app.h and 0<=x<=x+len(s)<=app.w-1
                                            for y,x,s,*_ in app.calls))
                        self.assertEqual([y for y,x,s,*_ in app.calls if '↵ BRIEF' in s],[app.h-3])
                        self.assertEqual([y for y,x,s,*_ in app.calls if 'ESC TITLE' in s],[app.h-2])
                        self.assertFalse(any(y==app.h-1 for y,*_ in app.calls))
                        if selected==0:
                            samples.add(tuple((y,x,s) for y,x,s,*_ in app.calls if 6<=y<=app.h-8))
                            app.key('\n');app.reset()
                            self.assertEqual(app.page,'brief')
                            app.brief()
                            self.assertIn(SKINS[id].brief,app.out)
                            self.assertEqual(sum('ENTER DEPLOY' in s for s in app.out),1)
                            self.assertTrue(all(0<=y<app.h and 0<=x<=x+len(s)<=app.w-1
                                                for y,x,s,*_ in app.calls))
                            app.key(ESC)
                            self.assertEqual(app.page,'map')
            self.assertEqual(len(samples),len(CHAPTERS))
        self.assertFalse(self.path.exists())

    def test_story_unlocks_and_medals_remain_on_the_same_commands(self):
        c=Campaign(self.path);c.new_game();c.clear(NODES[0]['id'],'S')
        before=self.path.read_bytes()
        app=RecordedSurface(c)
        app.key('1');app.key(curses.KEY_RIGHT)
        self.assertEqual(app.label(),'CASTLE')
        status=map_view(app,0)
        self.assertEqual([r.status for r in status.rows],['clear','open','locked','locked','locked'])
        self.assertEqual(status.rows[0].medal,'S')
        app.key('3')
        self.assertEqual(app.page,'map')
        self.assertEqual(app.pick,2)
        app.draw_map()
        self.assertTrue(any('Clear Guardhouse' in s for s in app.out))
        app.key('1')
        self.assertEqual((app.page,app.node['id']),('brief','castle-gate'))
        self.assertEqual(self.path.read_bytes(),before)

    def test_casino_lift_rises_as_high_limit_unlocks(self):
        c=at_casino(self.path);c.clear('casino-service')
        app=RecordedSurface(c);app.key('1')
        before=self.path.read_bytes()
        app.draw_map()
        launch=next(y for y,x,s,*_ in app.calls if x==4 and s.startswith('┏'))
        floor_rows={s:y for y,x,s,*_ in app.calls if s in ('STAFF ONLY','MEMBERS FLOOR','HIGH LIMIT')}
        self.assertLess(floor_rows['HIGH LIMIT'],floor_rows['MEMBERS FLOOR'])
        self.assertLess(floor_rows['MEMBERS FLOOR'],floor_rows['STAFF ONLY'])
        self.assertEqual(floor_rows['MEMBERS FLOOR'],launch+1)
        self.assertEqual([y for y,x,s,*_ in app.calls if s=='╟─'],[floor_rows['MEMBERS FLOOR']])
        mission_rows=[y for y,x,s,*_ in app.calls
                      if any(row['title'] in s for row in app.nodes())]
        self.assertEqual(mission_rows,sorted(set(mission_rows)))
        self.assertEqual(len(mission_rows),len(app.nodes()))
        self.assertEqual(self.path.read_bytes(),before)
        # Highlighting a locked high-floor choice must not move the lift.
        app.pick=2
        locked=map_view(app,1)
        app.reset();renderers()['casino'](app,map_view(app,1.6))
        self.assertEqual(locked.rows[2].status,'locked')
        self.assertEqual(next(y for y,x,s,*_ in app.calls if x==4 and s.startswith('┏')),launch)
        app.pick=1;map_view(app,1.8)
        c.clear('casino-rigging')  # Simulate the completed operation on a disposable save.
        new_before=self.path.read_bytes()
        app.pick=app.near()
        view=map_view(app,2)
        self.assertEqual((view.selected,view.previous,view.motion),(2,1,0.))
        app.reset();renderers()['casino'](app,view)
        floor_immediate=next(y for y,x,s,*_ in app.calls if x==4 and s.startswith('┏'))
        app.reset();renderers()['casino'](app,map_view(app,2.3))
        middle=next(y for y,x,s,*_ in app.calls if x==4 and s.startswith('┏'))
        app.reset();renderers()['casino'](app,map_view(app,3))
        end=next(y for y,x,s,*_ in app.calls if x==4 and s.startswith('┏'))
        self.assertEqual(launch,floor_immediate)
        self.assertGreater(floor_immediate,middle);self.assertGreater(middle,end)
        self.assertEqual(floor_rows['HIGH LIMIT'],end+1)
        self.assertEqual([y for y,x,s,*_ in app.calls if s=='╟─'],[floor_rows['HIGH LIMIT']])
        self.assertEqual(self.path.read_bytes(),new_before)
        self.assertNotIn('COINS','\n'.join(app.out))

    def test_spaceport_airlock_does_not_replace_or_block_a_combat_turn(self):
        app=RecordedSurface(Campaign(self.path));app.key('3')
        app.ch=next(i for i,c in enumerate(CHAPTERS) if c['id']=='spaceport')
        app.key('\n');app.key('\n')
        self.assertEqual(app.page,'battle')
        self.assertIsNotNone(app.airlock_started)
        app.reset();airlock(app,.4)
        self.assertTrue(app.calls)
        self.assertTrue(all(y==2 for y,*_ in app.calls))
        app.key('?')
        self.assertEqual(app._b_overlay,'help')
        self.assertFalse(self.path.exists())
