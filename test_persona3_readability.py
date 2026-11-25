"""Verify selector controls, battle-floor cues and guided fusion at compact sizes."""
import curses as C
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from battle_ui import ESC, RED
from persona3_app import P3App
from persona3_combat import START_RESOURCES
from persona3_state import P3Store
from persona3_thebel import Hall


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
        app=self.app;app.hall=Hall(0);app.hall.defeated=True
        app.go('shuffle')
        before=self.path.read_bytes()
        app.draw()
        self.assertIn('←→ SELECT  ENTER CLAIM',self.text())
        self.assertIn('Pixie',self.text())
        self.assertIn('¥90',self.text())
        self.assertIn('+30 HP / +12 SP',self.text())
        self.assertTrue(any('◈' in text for _,_,text,_ in self.rows))
        app.key(C.KEY_UP)
        self.assertEqual(app.i,0)
        app.key(C.KEY_LEFT)
        self.assertEqual(app.i,2)
        app.key(C.KEY_RIGHT)
        self.assertEqual(app.i,0)
        app.key(C.KEY_RIGHT)
        self.assertEqual(self.path.read_bytes(),before)
        app.key('\n')
        self.assertEqual((app.page,app.record.yen,app.record.masks),('hall',140,('Orpheus',)))

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

    def test_fusion_review_cancel_debit_and_explicit_equip(self):
        app=self.app;app.store.commit(masks=('Orpheus','Pixie'),yen=150)
        app.open_velvet('evening')
        app.key('f');app.draw()
        self.assertIn('READY',self.text());self.assertIn('MISSING PARENTS',self.text())
        self.assertIn('✓ Orpheus',self.text());self.assertIn('✓ Pixie',self.text())
        self.assertIn('¥110  /  ¥40 after',self.text())
        self.assertIn('Skills: Agi',self.text());self.assertIn('Defense: Ice weak',self.text())
        before=self.path.read_bytes()
        app.key('2')
        self.assertEqual(app.page,'fusion')
        self.assertIn('Register Angel first.',app.notice)
        app.key('1')
        self.rows.clear();app.draw()
        self.assertIn('Both parents stay registered.',self.text())
        self.assertIn('Orpheus stays equipped.',self.text())
        self.assertIn('Pay ¥110   /   ¥150 → ¥40',self.text())
        app.key(ESC)
        self.assertEqual(self.path.read_bytes(),before)
        app.key('1');app.key('\n')
        self.assertEqual((app.record.yen,app.record.masks,app.record.equipped),
                         (40,('Orpheus','Pixie','Nekomata'),'Orpheus'))
        self.assertEqual(app.record.masks[app.i],'Nekomata')
        app.key('\n')
        self.assertEqual(app.record.equipped,'Nekomata')
        self.assertEqual(P3Store(self.path).state.yen,40)

    def test_all_registered_compact_list_explains_nothing_is_left(self):
        app=self.app
        app.store.commit(masks=('Orpheus','Nekomata','Apsaras',"Jack O'Lantern"))
        app.open_velvet('evening');app.key('f');app.draw()
        self.assertIn('All recipes registered',self.text())
        self.assertNotIn('ENTER REVIEW',self.text())
        self.assertNotIn('MISSING PARENTS',self.text())
        self.assertTrue(all(0<=y<24 and 0<=x<=x+len(t)<=64 for y,x,t,_ in self.rows))
