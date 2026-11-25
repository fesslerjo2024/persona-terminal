"""Verify selector controls, battle-floor cues and guided fusion at compact sizes."""
import curses as C
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from unittest import TestCase

from persona_terminal.persona5.battle_ui import ESC, RED
from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_combat import START_RESOURCES
from persona_terminal.persona3.persona3_state import P3Store
from persona_terminal.persona3.persona3_thebel import Hall


class ReadabilityTests(TestCase):
    def setUp(self):
        td=TemporaryDirectory();self.addCleanup(td.cleanup)
        self.path=Path(td.name)/'p3.json'
        store=P3Store(self.path);store.new_game()
        self.app=P3App(None,store)
        self.app.h,self.app.w=25,65
        self.rows=[]
        self.app.put=lambda y,x,text,color=None,*_:self.rows.append((y,x,str(text),color))

    def text(self):
        return '\n'.join(row[2] for row in self.rows)

    def test_horizontal_shuffle_wraps_and_only_enter_claims_selected_card(self):
        app=self.app
        from persona_terminal.persona3.persona3_state import TUTORIAL
        app.store.commit(phase='tartarus',day=TUTORIAL)
        app.hall=Hall(0)
        app.resources=app.caps=START_RESOURCES
        app.battle=SimpleNamespace(resources=dict(START_RESOURCES),inventory={})
        app._finish_hall_battle()
        self.assertEqual(app.page,'shuffle')
        yen=app.record.yen
        before=self.path.read_bytes()
        app.draw()
        self.assertIn('←→ SELECT  ENTER CLAIM',self.text())
        self.assertIn('Pixie',self.text())
        self.assertIn('¥90',self.text())
        self.assertIn('+30 HP / +12 SP',self.text())
        for low,high in ((5,22),(24,40),(42,60)):
            masks={ch for y,x,text,_ in self.rows if 8<=y<=14 and low<=x<high
                   for ch in text if 0x2801<=ord(ch)<0x28ff}
            self.assertGreater(len(masks),10)
        app.key(C.KEY_UP)
        self.assertEqual(app.i,0)
        app.key(C.KEY_LEFT)
        self.assertEqual(app.i,2)
        app.key(C.KEY_RIGHT)
        self.assertEqual(app.i,0)
        app.key(C.KEY_RIGHT)
        self.assertEqual(self.path.read_bytes(),before)
        app.key('\n')
        self.assertEqual((app.page,app.record.yen,app.record.masks),('hall',yen+90,('Orpheus',)))

    def test_gate_warning_is_persistent_but_fog_does_not_reveal_patrol(self):
        app=self.app;app.hall=Hall(1)
        app.resources=app.caps=START_RESOURCES
        app.draw_hall()
        text=self.text()
        self.assertIn('05F / GATEKEEPER FLOOR',text)
        self.assertIn('Ruthless Ice Ravens',text)
        self.assertIn('Step onto the sealed',text)
        self.assertIn('████████████████',text)
        self.assertFalse(any(t=='◆' and ink==RED for y,x,t,ink in self.rows))
        hall=app.hall
        self.assertEqual(hall.glyph(*hall.floor.stairs),' ')
        hall.seen.add(hall.floor.stairs)
        self.assertEqual(hall.glyph(*hall.floor.stairs),'⊗')
        hall.defeated=True
        self.assertEqual(hall.glyph(*hall.floor.stairs),'⇧')
        self.rows.clear();app.draw_hall()
        self.assertIn('STAIRS OPEN',self.text())
        self.assertNotIn('Step onto the sealed',self.text())

    def test_hall_party_names_hp_and_sp_share_the_same_columns(self):
        app=self.app;app.hall=Hall(1)
        app.caps=START_RESOURCES
        app.resources={'Protagonist':(71,23),'Yukari':(116,0),'Junpei':(0,39)}
        before=self.path.read_bytes()
        for w,h in ((65,25),(96,34)):
            app.w,app.h=w,h
            self.rows.clear();app.draw_hall()
            for i,(name,(hp,sp)) in enumerate(app.resources.items()):
                y=5+i*5
                room={(r,x):t for r,x,t,_ in self.rows if x>=34 and y<=r<=y+2}
                self.assertEqual(room[y,34],'Makoto' if i==0 else name)
                self.assertEqual(room[y+1,34],'HP')
                self.assertEqual(room[y+2,34],'SP')
                width=min(22,w-49)
                for shift,current,cap in ((1,hp,START_RESOURCES[name][0]),
                                          (2,sp,START_RESOURCES[name][1])):
                    bar=''.join(room[y+shift,j] for j in sorted(x for r,x in room
                                if r==y+shift and 37<=x<39+width))
                    self.assertEqual(len(bar),width)
                    self.assertEqual(bar.count('█')==0,current==0)
                    self.assertEqual(bar.count('█')==width,current==cap)
                    self.assertEqual(room[y+shift,39+width].strip(),f'{current:>3}/{cap}'.strip())
                if i<2:self.assertFalse(any(r in (y+3,y+4) and x>=34 for r,x,_,_ in self.rows))
            self.assertTrue(all(0<=y<h-1 and 0<=x<=x+len(t)<w for y,x,t,_ in self.rows))
        self.assertEqual(self.path.read_bytes(),before)

    def test_fusion_review_cancel_consumption_and_resummon(self):
        app=self.app;app.store.commit(masks=('Orpheus','Pixie'),yen=150)
        app.open_velvet('evening');app.key(' ')
        app.key('f');app.draw()
        self.assertIn('READY',self.text());self.assertIn('MISSING PARENTS',self.text())
        self.assertIn('Orpheus + Pixie',self.text())
        self.assertIn('Skills: Agi',self.text());self.assertIn('Defense: Ice weak',self.text())
        before=self.path.read_bytes()
        app.key('2')
        self.assertEqual(app.page,'fusion')
        self.assertIn('Need Angel in stock.',app.notice)
        app.key('1')
        self.assertEqual(app.page,'inherit')
        moves=app._inherit_rows()
        bash=next(i for i,(_,skill) in enumerate(moves,1) if skill=='Bash')
        app.key(str(bash))
        self.rows.clear();app.draw()
        self.assertIn('Parents leave stock, but stay registered.',self.text())
        self.assertIn('Inherit: Bash',self.text())
        self.assertIn('No yen cost.',self.text())
        app.key(ESC)
        self.assertEqual(self.path.read_bytes(),before)
        app.key('\n');app.key('\n')
        self.assertEqual((app.record.yen,app.record.masks,app.record.equipped),
                         (150,('Nekomata',),'Nekomata'))
        self.assertEqual(tuple(app.record.compendium),('Orpheus','Pixie','Nekomata'))
        app.key('c');app.key('r');self.assertEqual(app.page,'resummon')
        post_fuse=self.path.read_bytes()
        app.key(ESC)
        self.assertEqual(self.path.read_bytes(),post_fuse)
        app.key('r');app.key('\n')
        self.assertEqual(app.record.masks,('Nekomata','Orpheus'))
        self.assertEqual(app.record.equipped,'Nekomata')
        self.assertEqual(P3Store(self.path).state.yen,105)

    def test_all_registered_compact_list_explains_nothing_is_left(self):
        app=self.app
        app.store.commit(masks=('Orpheus','Nekomata','Apsaras',"Jack O'Lantern"))
        app.open_velvet('evening');app.key(' ');app.key('f');app.draw()
        self.assertIn('No recipe ready.',self.text())
        self.assertNotIn('ENTER REVIEW',self.text())
        self.assertNotIn('MISSING PARENTS',self.text())
        self.assertTrue(all(0<=y<24 and 0<=x<=x+len(t)<=64 for y,x,t,_ in self.rows))

    def test_long_event_date_and_entrance_shortcuts_fit_compact(self):
        from persona_terminal.persona3.persona3_upper import OPENS
        from persona_terminal.persona3.persona3_yabbashah import AFTER_AUGUST, AIGIS
        a=self.app
        a.store.commit(day=AFTER_AUGUST,phase='calendar')
        a.go('evening');a.draw()
        self.assertIn('08/08',self.text())
        self.assertTrue(all(x+len(t)<=64 for _,x,t,_ in self.rows))
        for day,shortcut in ((OPENS.replace(day=19),'R CASES'),(AIGIS,'C CLOCK')):
            a.store.commit(day=day,phase='calendar')
            a.deploy();a.key(' ')
            self.rows.clear();a.draw()
            footer=[t for y,x,t,_ in self.rows if y==23][0]
            self.assertIn(shortcut,footer)
            self.assertLessEqual(len(footer),64)

    def test_junpei_choices_are_dated_and_hospital_scene_does_not_repeat(self):
        from persona_terminal.persona3.persona3_junpei import INVITATION, FIRST_SHOP_DAY, PAYOFF_DAY
        a=self.app
        a.store.commit(day=INVITATION,phase='calendar',yen=400)
        a.resume()
        a.draw()
        self.assertIn('Talk with Junpei',self.text())
        self.assertNotIn('Hospital',self.text())
        a.key('5');a.key('4');a.key('\n')
        self.assertEqual(a.record.day,FIRST_SHOP_DAY)
        a.key('5')
        self.assertEqual(a.record.yen,150)
        self.assertEqual(a.page,'evening')
        self.assertIn('Give Junpei the flowers',a.evening_options())
        a.key('6')
        self.assertEqual(a.record.junpei_flowers,'given')
        a.store.commit(day=PAYOFF_DAY,activity='')
        a.resume()
        self.rows.clear();a.draw()
        self.assertIn('HOSPITAL VISIT',self.text())
        a.key('\n')
        self.assertEqual((a.page,a.record.junpei_flowers),('calendar','seen'))
        a.resume()
        self.assertEqual(a.page,'calendar')
