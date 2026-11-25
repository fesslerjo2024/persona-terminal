"""The themed surfaces do not change mission selection, locks, or saves."""
import curses
from statistics import median
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona5.campaign_data import CHAPTERS, NODES
from persona_terminal.persona5.campaign_state import Campaign
from persona_terminal.persona5.palace_menu import SKINS, map_view, renderers, airlock
from persona_terminal.shared.reel_palette import IDS
from .test_animation_gallery import Surface
from .test_casino_route import at_casino


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
        app.begin_extra('practice')
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
                        self.assertEqual([y for y,x,s,*_ in app.calls if 'ESC EXTRAS' in s],[app.h-2])
                        self.assertFalse(any(y==app.h-1 for y,*_ in app.calls))
                        if selected==0:
                            body=[(y,x,s) for y,x,s,*_ in app.calls if 6<=y<=app.h-8]
                            samples.add(tuple(body))
                            dots={c for _,_,run in body for c in run if '⠁'<=c<='⣿'}
                            self.assertGreater(len(dots),14)
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
        self.assertIn('Locked. Clear the previous operation to reveal it.',app.out)
        app.key('1')
        self.assertEqual((app.page,app.node['id']),('brief','castle-gate'))
        self.assertEqual(self.path.read_bytes(),before)

    def test_every_story_palace_hides_future_names_and_briefs_until_unlocked(self):
        c=Campaign(self.path)
        c.new_game()
        for ch,chapter in enumerate(CHAPTERS):
            with self.subTest(chapter=chapter['id']):
                app=RecordedSurface(c)
                app.key('1')
                self.assertEqual(app.ch,ch)
                open_node, next_node, *future = app.nodes()
                before=self.path.read_bytes()
                for w,h in ((65,25),(100,35)):
                    app.w,app.h=w,h
                    for i,node in enumerate(app.nodes()[1:],1):
                        app.key(str(i+1))
                        self.assertEqual(app.page,'map')
                        self.assertEqual(app.pick,i)
                        view=map_view(app,0)
                        self.assertEqual(view.rows[0].title,open_node['title'])
                        self.assertEqual(view.rows[i].title,'???')
                        self.assertEqual(view.rows[i].mark,'')
                        app.reset();app.draw_map()
                        self.assertIn('???','\n'.join(app.out))
                        for hidden in (next_node,*future):
                            self.assertNotIn(hidden['title'],'\n'.join(app.out))
                        if chapter['id']=='cruiser' and i==1:
                            self.assertNotIn('Outer Deck','\n'.join(app.out))
                    self.assertEqual(self.path.read_bytes(),before)
                c.clear(open_node['id'],'B')
                app.pick=1
                view=map_view(app,1)
                self.assertEqual((view.rows[0].title,view.rows[0].medal),(open_node['title'],'B'))
                self.assertEqual(view.rows[1].title,next_node['title'])
                self.assertEqual(view.detail,next_node.get('brief',''))
                self.assertTrue(all(r.title=='???' for r in view.rows[2:]))
                app.key('\n')
                self.assertEqual((app.page,app.node['id']),('brief',next_node['id']))
                for node in (next_node,*future):
                    c.clear(node['id'],'B')

    def test_late_map_art_cannot_preview_a_locked_room(self):
        from unittest.mock import patch
        from persona_terminal.persona5 import palace_late_themes as themes

        gates={
            'depths':('depths-rebellion','_platform','_bridge'),
            'laboratory':('laboratory-colors','_intake','_color_route'),
        }
        c=Campaign(self.path)
        c.new_game()
        for chapter in CHAPTERS:
            key=chapter['id']
            if key not in gates:
                for node in chapter['nodes']:c.clear(node['id'],'B')
                continue
            app=RecordedSurface(c)
            app.key('1')
            self.assertEqual(CHAPTERS[app.ch]['id'],key)
            gate,base,late=gates[key]
            idx=next(i for i,node in enumerate(app.nodes()) if node['id']==gate)

            def render(expected,pick):
                before=self.path.read_bytes()
                for w,h in ((65,25),(112,38)):
                    app.w,app.h=w,h
                    app.pick=pick
                    app.reset()
                    view=map_view(app,10.)
                    with patch.object(themes,base,wraps=getattr(themes,base)) as early:
                        with patch.object(themes,late,wraps=getattr(themes,late)) as later:
                            renderers()[key](app,view)
                    self.assertEqual((early.call_count,later.call_count),
                                     (0,1) if expected else (1,0))
                    self.assertTrue(any('⠁'<=ch<='⣿' for _,_,run,*_ in app.calls for ch in run))
                self.assertEqual(self.path.read_bytes(),before)

            render(False,0)
            render(False,idx)
            render(False,len(app.nodes())-1)

            for node in app.nodes()[:idx]:c.clear(node['id'],'B')
            self.assertTrue(c.can_play(gate))
            render(True,idx)
            render(False,idx-1)
            render(False,len(app.nodes())-1)
            for node in app.nodes()[idx:]:c.clear(node['id'],'B')

    def test_casino_lift_rises_as_high_limit_unlocks(self):
        c=at_casino(self.path);c.clear('casino-service')
        app=RecordedSurface(c);app.key('1')
        before=self.path.read_bytes()

        def cabin_y():
            # At the compact viewport the right lip of the packed cabin
            # is column 7, the only place with this amber lift outline.
            amber=IDS['amber']
            return median(y for y,x,s,color,*_ in app.calls
                          if x==7 and color==amber and all('⠁'<=c<='⣿' for c in s))

        app.draw_map()
        launch=cabin_y()
        floor_rows={s:y for y,x,s,*_ in app.calls if s in ('STAFF ONLY','MEMBERS FLOOR','FLOOR 03')}
        self.assertLess(floor_rows['FLOOR 03'],floor_rows['MEMBERS FLOOR'])
        self.assertNotIn('HIGH LIMIT',app.out)
        self.assertLess(floor_rows['MEMBERS FLOOR'],floor_rows['STAFF ONLY'])
        self.assertEqual(floor_rows['MEMBERS FLOOR'],launch)
        self.assertEqual([y for y,x,s,*_ in app.calls if s=='╟─'],[floor_rows['MEMBERS FLOOR']])
        mission_rows=[y for y,x,s,*_ in app.calls
                      if '???' in s or any(row['title'] in s for row in app.nodes())]
        self.assertEqual(mission_rows,sorted(set(mission_rows)))
        self.assertEqual(len(mission_rows),len(app.nodes()))
        self.assertEqual(self.path.read_bytes(),before)
        # Highlighting a locked high-floor choice must not move the lift.
        app.pick=2
        locked=map_view(app,1)
        app.reset();renderers()['casino'](app,map_view(app,1.6))
        self.assertEqual(locked.rows[2].status,'locked')
        self.assertEqual(cabin_y(),launch)
        app.pick=1;map_view(app,1.8)
        c.clear('casino-rigging')  # Simulate the completed operation on a disposable save.
        new_before=self.path.read_bytes()
        app.pick=app.near()
        view=map_view(app,2)
        self.assertEqual((view.selected,view.previous,view.motion),(2,1,0.))
        app.reset();renderers()['casino'](app,view)
        floor_immediate=cabin_y()
        app.reset();renderers()['casino'](app,map_view(app,2.3))
        middle=cabin_y()
        app.reset();renderers()['casino'](app,map_view(app,3))
        end=cabin_y()
        self.assertEqual(launch,floor_immediate)
        self.assertGreater(floor_immediate,middle);self.assertGreater(middle,end)
        self.assertIn((end,'HIGH LIMIT'),[(y,s) for y,_,s,*_ in app.calls])
        self.assertEqual(floor_rows['FLOOR 03'],end)
        self.assertEqual([y for y,x,s,*_ in app.calls if s=='╟─'],[floor_rows['FLOOR 03']])
        self.assertEqual(self.path.read_bytes(),new_before)
        self.assertNotIn('COINS','\n'.join(app.out))

    def test_spaceport_airlock_does_not_replace_or_block_a_combat_turn(self):
        app=RecordedSurface(Campaign(self.path));app.begin_extra('practice')
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
