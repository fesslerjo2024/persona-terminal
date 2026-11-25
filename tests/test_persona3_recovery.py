"""Verify recovery and Velvet menu changes against a disposable expedition."""
import curses as C
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_combat import LEAD_ID
from persona_terminal.persona3.persona3_field_recovery import KIT_HP
from persona_terminal.persona3.persona3_state import MOON,P3Store


class P3RecoveryTests(TestCase):
    def setUp(self):
        td=TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.path=Path(td.name)/'persona3.json'
        self.store=P3Store(self.path)
        self.store.new_game()
        self.store.commit(day=date(2009,4,23),phase='calendar',depth=2,
                          masks=('Orpheus','Pixie'),aid=2)
        self.app=P3App(None,self.store,seed=1)

    def open_field(self):
        app=self.app
        app.deploy();app.key(' ')
        return app

    def has(self,text,w=65,h=25):
        self.app.w,self.app.h=w,h
        painted=[]
        self.app.put=lambda y,x,t,*_:painted.append((y,x,str(t)))
        self.app.draw()
        self.assertIn(text,' '.join(t for _,__,t in painted))
        self.assertTrue(all(0<=y<h-1 and 0<=x<=x+len(t)<w for y,x,t in painted))

    def test_heal_during_expedition_consumes_real_supplies_and_caster_sp(self):
        app=self.open_field()
        app.key('2')
        hall=app.hall
        origin=hall.pos,hall.steps,hall.shadow
        app.resources.update({LEAD_ID:(24,16),'Yukari':(98,32),'Junpei':(0,12)})
        self.has('H HEAL')
        app.key('h')
        self.has('Yukari • Dia')
        self.has('Revival Bead',96,34)
        saved=self.path.read_bytes()
        app.key('2');app.key(ESC)
        self.assertEqual(app.inventory['Medicine'],3)
        self.assertEqual(app.page,'field-heal')
        app.key('2');app.key('1')
        self.assertEqual(app.resources[LEAD_ID],(74,16))
        self.assertEqual(app.inventory['Medicine'],2)
        app.key('3');app.key('1')
        self.assertEqual(app.resources[LEAD_ID],(74,28))
        self.assertEqual(app.inventory['Soul Drop'],0)
        app.key('4');app.key('3')
        self.assertEqual(app.resources['Junpei'],(40,12))
        self.assertEqual(app.inventory['Revival Bead'],0)
        app.key('5');app.key('2') # Yukari spends her own SP while healing herself.
        self.assertEqual(app.resources['Yukari'],(116,28))
        self.assertEqual(self.path.read_bytes(),saved)
        app.key('1')
        self.assertEqual(app.resources['Junpei'],(40+KIT_HP,12))
        self.assertEqual(self.store.state.aid,1)
        app.key(ESC)
        self.assertIs(app.hall,hall)
        self.assertEqual((hall.pos,hall.steps,hall.shadow),origin)
        app.open_battle(hall.encounter)
        self.assertEqual(app.battle.resources,app.resources)
        self.assertEqual(app.battle.inventory,app.inventory)

    def test_entrance_border_and_shuffle_restore_selection_without_advancing(self):
        app=self.open_field()
        prior=self.path.read_bytes()
        app.key(C.KEY_DOWN)
        selected=app.i
        app.key('h');app.key('1') # Everyone already full.
        self.assertIn('No injured',app.notice)
        self.assertEqual(self.store.state.aid,2)
        app.key(ESC)
        self.assertEqual((app.page,app.i),('entrance',selected))
        for page in ('border','shuffle'):
            app.go(page);app.i=2
            app.key('H');app.key(ESC)
            self.assertEqual((app.page,app.i),(page,2))
        self.assertEqual(self.path.read_bytes(),prior)

    def test_velvet_animates_on_each_april_visit_but_not_return_from_compendium(self):
        app=self.open_field()
        app.key('2');hall=app.hall
        app.key('t')
        app.key(C.KEY_DOWN)
        saved=self.path.read_bytes()
        self.has('V VELVET')
        app.key('v')
        self.assertEqual(app.page,'velvet-intro')
        app.key(ESC) # Does not cancel the visit.
        self.assertEqual(app.page,'velvet')
        self.assertEqual(self.path.read_bytes(),saved)
        app.key('c');app.key(ESC)
        self.assertEqual(app.page,'velvet')
        app.key('2')
        self.assertEqual(self.store.state.equipped,'Pixie')
        app.key(ESC)
        self.assertEqual((app.page,app.i),('entrance',1))
        app.key('v')
        self.assertEqual(app.page,'velvet-intro')
        with patch('persona_terminal.persona3.persona3_app.time.monotonic',return_value=app.started+2):
            self.has('ACTIVE STOCK')
        app.key(ESC);app.key('1')
        self.assertIs(app.hall,hall)
        self.assertEqual(app.record.equipped,'Pixie')

    def test_practice_can_equip_and_fuse_temporarily_without_touching_disk(self):
        self.store.commit(day=MOON,phase='monorail')
        app=P3App(None,self.store)
        self.app=app
        original=self.path.read_bytes()
        app.key('t');app.key(' ');app.key('v');app.key(' ')
        self.has('Practice changes do not save.')
        app.key('f');app.key('1');app.key('1');app.key('\n')
        self.assertEqual(app.record.equipped,'Nekomata')
        self.assertEqual(self.store.state.equipped,'Orpheus')
        app.key(ESC);app.key('x');app.key('\n')
        self.assertEqual((app.page,app.record.equipped),('operation','Orpheus'))
        self.assertEqual(self.path.read_bytes(),original)

    def test_no_cost_when_healer_cannot_cast_or_target_cannot_receive_it(self):
        app=self.open_field()
        app.resources.update({LEAD_ID:(5,3),'Yukari':(13,2),'Junpei':(0,0)})
        app.key('h');app.key('5')
        self.assertEqual(app.notice,'Needs 4 SP.')
        initial=dict(app.inventory),dict(app.resources),self.path.read_bytes()
        app.key('2');app.key('3')
        self.assertIn('Choose an ally',app.notice)
        self.assertEqual((app.inventory,app.resources,self.path.read_bytes()),initial)
