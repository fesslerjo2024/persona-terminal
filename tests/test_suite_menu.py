"""Exercise the title boundaries without running any live campaign state."""
import curses as C
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from persona_terminal.persona5.battle_ui import ESC, GOLD
from persona_terminal.persona5.campaign_state import Campaign
from persona_terminal.shared.suite_menu import EXTRAS_BUTTON, SuiteMenu, TITLES, cards, draw
from persona_terminal.shared.suite_art import INKS, PIN_SECONDS, emblem_runs
from .test_animation_gallery import Surface
from .test_startup import ScriptedScreen


class SuiteMenuTests(TestCase):
    def test_extras_button_is_clickable_and_keyboard_accessible(self):
        for w,h in ((65,25),(96,35)):
            app=SuiteMenu(None);app.w,app.h=w,h
            app.choose('5')
            self.assertIsNone(app.choose(C.KEY_DOWN))
            self.assertEqual(app.choose('\n'),'extras')
            self.assertEqual(app.selection,2)
            app.choose(C.KEY_UP)
            self.assertEqual(app.choose('\n'),5)
            x=(w-len(EXTRAS_BUTTON))//2
            with patch('persona_terminal.shared.suite_menu.C.getmouse',return_value=(0,x,h-5,0,C.BUTTON1_CLICKED)):
                self.assertEqual(app.choose(C.KEY_MOUSE),'extras')
            self.assertEqual(app.choose('X'),'extras')

    def test_extras_esc_and_remembered_selection(self):
        for w,h in ((65,25),(96,35)):
            class Screen:
                keys=iter(('2','2',ESC,'1','1',ESC,'\n','\n',ESC,ESC))
                def getmaxyx(self):return h,w
                def timeout(self,ms):pass
                def erase(self):pass
                def refresh(self):pass
                def get_wch(self):return next(self.keys)
            app=SuiteMenu(Screen())
            written=[]
            app.put=lambda y,x,label,*_:written.append((y,x,label))
            seen=[]
            with patch.object(app,'_mouse'):
                self.assertTrue(app._extras(lambda leaf:seen.append((3,leaf)),
                                             lambda leaf:seen.append((5,leaf))))
            self.assertEqual(seen,[(5,'practice'),(3,'gallery'),(3,'gallery')])
            self.assertEqual(app.extras_leaves,{3:0,5:1})
            self.assertFalse(any('Persona 4' in text for _,_,text in written))
            self.assertTrue(all(0<=y<h-1 and 0<=x<=x+len(text)<w for y,x,text in written))

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
                    with patch('persona_terminal.shared.suite_menu.C.getmouse',return_value=(0,target.left+2,target.top+2,0,C.BUTTON1_CLICKED)):
                        self.assertEqual(app.choose(C.KEY_MOUSE),expected)
                with patch('persona_terminal.shared.suite_menu.C.getmouse',return_value=(0,0,0,0,C.BUTTON1_CLICKED)):
                    self.assertIsNone(app.choose(C.KEY_MOUSE))

    def test_emblems_are_distinct_and_p4_keeps_gold_when_unfocused(self):
        app=SuiteMenu(None);app.w,app.h=65,25
        out=[];app.put=lambda y,x,t,color,*_:out.append((y,x,t,color))
        boxes=cards(app.w,app.h)
        for selection in (0,1,2):
            out.clear();draw(app,selection)
            for box in boxes:
                self.assertTrue(any(any('⠁'<=ch<='⣿' for ch in t) and box.contains(x,y)
                                    for y,x,t,_ in out))
            p4=boxes[1]
            painted=[(t,color) for y,x,t,color in out if p4.contains(x,y)]
            self.assertTrue(any('PERSONA 4' in t for t,_ in painted))
            self.assertTrue(all(color==GOLD for text,color in painted if 'PERSONA 4' in text or '═' in text))
            self.assertTrue(any(color==INKS['amber'] for _,color in painted))

    def test_every_emblem_animates_and_settles_without_geometry_drift(self):
        for title in TITLES:
            with self.subTest(title=title.number):
                idle=emblem_runs(title.number,17,9)
                first=emblem_runs(title.number,17,9,.12)
                later=emblem_runs(title.number,17,9,.36)
                self.assertNotEqual(first,later)
                self.assertNotEqual(first,idle)
                self.assertEqual(emblem_runs(title.number,17,9,title.animation_seconds),idle)
                for all_rows in (idle,first,later):
                    self.assertEqual(len(all_rows),9)
                    for row in all_rows:
                        self.assertTrue(all(0<=x<=x+len(run)<=17 for x,run,_ in row))

    def test_retired_comparison_shortcuts_do_nothing(self):
        app=SuiteMenu(None)
        focus=app.selection
        for key in ('i','I','a','b','c','r'):
            self.assertIsNone(app.choose(key))
            self.assertEqual(app.selection,focus)
            self.assertIsNone(app.pulse_started)

    def test_selector_matches_the_approved_previews_at_rest_and_during_playback(self):
        from persona_terminal.shared.selector_draft_gallery import candidates, picture
        for title,name in zip(TITLES,('Dark Hour Clock','Golden Tube TV','Pinned Calling Card')):
            with self.subTest(title=title.number):
                self.assertEqual(candidates(title.number)[0][0],name)
                for phase,elapsed in ((0,0),(18,title.animation_seconds/2),(36,None)):
                    rows=picture(title.number,0,26,11,phase)
                    expected=[]
                    for row in rows:
                        x=1
                        expected_row=[]
                        for run,pigment in row:
                            if run.strip():expected_row.append((x,run,INKS[pigment]))
                            x+=len(run)
                        expected.append(tuple(expected_row))
                    self.assertEqual(emblem_runs(title.number,28,11,elapsed),tuple(expected))

    def test_pinned_card_launch_keeps_full_motion(self):
        self.assertEqual(TITLES[2].opening_seconds,PIN_SECONDS)
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
        with patch.object(app,'_mouse'), patch('persona_terminal.shared.suite_menu.time.monotonic',side_effect=lambda:app.s.now), \
             patch('persona_terminal.shared.suite_menu.draw',side_effect=lambda _app,selected,t:phases.append((selected,t))):
            self.assertEqual(app._selection(),5)
        self.assertEqual(len(phases),4)
        self.assertEqual(phases[0],(0,None))
        self.assertTrue(all(index==2 and t<PIN_SECONDS for index,t in phases[1:]))
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
            with patch.object(menu,'_mouse'), patch('persona_terminal.shared.suite_menu.time.monotonic',return_value=20), \
                 patch('persona_terminal.persona3.persona3_title.draw_intro',side_effect=lambda app,t:seen.append('intro')), \
                 patch('persona_terminal.persona3.persona3_title.draw_menu',side_effect=lambda app,i,*_:seen.append(i)):
                self.assertTrue(menu._preview())
            self.assertEqual(seen,['intro',1,0])
            self.assertFalse(path.exists())

    def test_p5_first_escape_skips_and_second_returns_to_selector(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'story.json';story=Campaign(path);story.new_game()
            before=path.read_bytes()
            app=Surface(story)
            screen=app.s=ScriptedScreen(app,[(.1,ESC),(.15,ESC)])
            with patch('persona_terminal.persona5.campaign.time.monotonic',side_effect=lambda:screen.at):
                self.assertIs(app.run(back_to_suite=True),True)
            self.assertNotIn('CONTINUE',screen.frames[0][2])
            self.assertIn('CONTINUE',screen.frames[1][2])
            self.assertIn('ESC TITLES',screen.frames[1][2])
            self.assertEqual(path.read_bytes(),before)
