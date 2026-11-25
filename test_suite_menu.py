"""Exercise the title boundaries without running any live campaign state."""
import curses as C
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from battle_ui import ESC, GOLD
from campaign_state import Campaign
from suite_menu import SuiteMenu, TITLES, cards, draw
from suite_art import PULSE_SECONDS, TUMBLE_SECONDS, emblem_runs
from test_animation_gallery import Surface
from test_startup import ScriptedScreen


class SuiteMenuTests(TestCase):
    def test_number_arrows_enter_and_p4_are_independent(self):
        app=SuiteMenu(None)
        self.assertEqual(app.choose('3'),3)
        self.assertIsNone(app.choose(C.KEY_RIGHT))
        self.assertIsNone(app.choose('\n'))
        self.assertIsNone(app.choose('4'))
        self.assertEqual(app.selection,1)
        self.assertEqual(app.choose('5'),5)
        self.assertIsNone(app.choose(C.KEY_RIGHT))
        self.assertEqual(app.choose('\n'),3)

    def test_geometry_and_click_hitboxes_in_both_sizes(self):
        for w,h in ((65,25),(96,34)):
            with self.subTest(size=(w,h)):
                app=SuiteMenu(None);app.w,app.h=w,h
                out=[];app.put=lambda y,x,t,*_:out.append((y,x,t))
                draw(app,0)
                self.assertTrue(all(0<=y<h-1 and 0<=x<=x+len(text)<w for y,x,text in out))
                self.assertTrue(all(any(f'PERSONA {i}' in t for _,_,t in out) for i in (3,4,5)))
                for caption in ('TITLE PREVIEW','UNAVAILABLE','PLAY CAMPAIGN','ICON DRAFTS'):
                    self.assertFalse(any(caption in t for _,_,t in out))
                for target,expected in zip(cards(w,h),(3,None,5)):
                    with patch('suite_menu.C.getmouse',return_value=(0,target.left+2,target.top+2,0,C.BUTTON1_CLICKED)):
                        self.assertEqual(app.choose(C.KEY_MOUSE),expected)
                with patch('suite_menu.C.getmouse',return_value=(0,0,0,0,C.BUTTON1_CLICKED)):
                    self.assertIsNone(app.choose(C.KEY_MOUSE))

    def test_emblems_are_distinct_and_p4_keeps_gold_when_unfocused(self):
        app=SuiteMenu(None);app.w,app.h=65,25
        out=[];app.put=lambda y,x,t,color,*_:out.append((y,x,t,color))
        boxes=cards(app.w,app.h)
        for selection in (0,1,2):
            out.clear();draw(app,selection)
            for box,detail in zip(boxes,('●','▒░▒','▄▄▄')):
                self.assertTrue(any(detail in t and box.contains(x,y) for y,x,t,_ in out))
            p4=boxes[1]
            painted=[(t,color) for y,x,t,color in out if p4.contains(x,y)]
            self.assertTrue(any('PERSONA 4' in t for t,_ in painted))
            self.assertTrue(all(color==GOLD for _,color in painted))

    def test_every_emblem_animates_and_settles_without_geometry_drift(self):
        for title in TITLES:
            with self.subTest(title=title.number):
                idle=emblem_runs(title.number,17,title.ink)
                first=emblem_runs(title.number,17,title.ink,.12)
                later=emblem_runs(title.number,17,title.ink,.36)
                self.assertNotEqual(first,later)
                self.assertNotEqual(first,idle)
                self.assertEqual(emblem_runs(title.number,17,title.ink,title.animation_seconds),idle)
                for all_rows in (idle,first,later):
                    self.assertEqual(len(all_rows),7)
                    for row in all_rows:
                        self.assertTrue(all(0<=x<=x+len(run)<=17 for x,run,_ in row))

    def test_retired_comparison_shortcuts_do_nothing(self):
        app=SuiteMenu(None)
        focus=app.selection
        for key in ('i','I','a','b','c','r'):
            self.assertIsNone(app.choose(key))
            self.assertEqual(app.selection,focus)
            self.assertIsNone(app.pulse_started)

    def test_animated_clock_hands_share_pivot_and_end_at_twelve(self):
        title=TITLES[0]
        def glyphs(rows):
            grid=[[' ']*17 for _ in range(7)]
            for y,row in enumerate(rows):
                for x,run,_ in row:grid[y][x:x+len(run)]=run
            return grid
        first=glyphs(emblem_runs(3,17,title.ink,.08))
        last=glyphs(emblem_runs(3,17,title.ink,PULSE_SECONDS*.87))
        self.assertIn('─',''.join(first[3][:8]))
        self.assertEqual(last[3][8],'●')
        self.assertEqual((last[1][8],last[2][8]),('│','│'))
        self.assertIn('12',''.join(last[0]))
        self.assertNotEqual(first,last)

    def test_p5_default_is_tumbling_card_and_launch_keeps_full_motion(self):
        from battle_ui import RED, WHITE
        title=TITLES[2]
        self.assertEqual(title.opening_seconds,TUMBLE_SECONDS)
        idle=emblem_runs(5,17,title.ink)
        white=''.join(text for row in idle for _,text,ink in row if ink==WHITE)
        self.assertIn('▄▄▄',white)
        self.assertIn('◥▴◤',white.replace(' ',''))
        self.assertTrue(any(ink==RED for row in idle for _,_,ink in row))
        # Mid-flight, some paper has rotated flat against the viewer, but
        # the crest isn't printed on the visible face of the sheet yet.
        preflip=emblem_runs(5,17,title.ink,TUMBLE_SECONDS*.33)
        self.assertFalse(any('◥' in text for row in preflip for _,text,_ in row))

        app=SuiteMenu(None)
        class Screen:
            now=0
            def getmaxyx(self):return 25,65
            def timeout(self,ms):pass
            def erase(self):pass
            def refresh(self):pass
            keys=iter(((.12,'5'),(.6,'i'),(.91,'\n'),(1.5,None)))
            def get_wch(self):
                self.now,key=next(self.keys)
                if key is None:raise C.error
                return key
        app.s=Screen()
        phases=[]
        with patch.object(app,'_mouse'), patch('suite_menu.time.monotonic',side_effect=lambda:app.s.now), \
             patch('suite_menu.draw',side_effect=lambda _app,selected,t:phases.append((selected,t))):
            self.assertEqual(app._selection(),5)
        self.assertEqual(len(phases),4)
        self.assertEqual(phases[0],(0,None))
        self.assertTrue(all(index==2 and t<TUMBLE_SECONDS for index,t in phases[1:]))
        self.assertGreater(phases[-1][1],.75)

    def test_preview_does_not_open_p5_and_returns_to_selector(self):
        menu=SuiteMenu(None)
        events=[]
        with patch.object(menu,'_selection',side_effect=[3,5,None]), \
             patch.object(menu,'_preview',side_effect=lambda:events.append('preview') or True):
            menu.run(lambda:events.append('campaign') or True)
        self.assertEqual(events,['preview','campaign'])

    def test_p3_intro_skip_does_not_start_new_game(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'unused-p3.json'
            menu=SuiteMenu(None,path)
            menu.put=lambda *args:None
            seen=[]
            class Screen:
                def getmaxyx(self):return 25,65
                def timeout(self,ms):pass
                def erase(self):pass
                def refresh(self):pass
                keys=iter(('\n','1','3'))
                def get_wch(self):return next(self.keys)
            menu.s=Screen()
            with patch.object(menu,'_mouse'), patch('suite_menu.time.monotonic',return_value=20), \
                 patch('persona3_title.draw_intro',side_effect=lambda app,t:seen.append('intro')), \
                 patch('persona3_title.draw_menu',side_effect=lambda app,i,*_:seen.append(i)):
                self.assertTrue(menu._preview())
            self.assertEqual(seen,['intro',1,0])
            self.assertFalse(path.exists())

    def test_p5_first_escape_skips_and_second_returns_to_selector(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'story.json';story=Campaign(path);story.new_game()
            before=path.read_bytes()
            app=Surface(story)
            screen=app.s=ScriptedScreen(app,[(.1,ESC),(.15,ESC)])
            with patch('campaign.time.monotonic',side_effect=lambda:screen.at):
                self.assertIs(app.run(back_to_suite=True),True)
            self.assertNotIn('CONTINUE',screen.frames[0][2])
            self.assertIn('CONTINUE',screen.frames[1][2])
            self.assertIn('ESC TITLES',screen.frames[1][2])
            self.assertEqual(path.read_bytes(),before)
