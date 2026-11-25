"""May/July route regressions through P3App, with disposable save fixtures."""
from collections import deque
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import curses as C

from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_combat import LEAD_ID
from persona_terminal.persona3.persona3_operation_route import TrainRoute, _HATCH, _JUNPEI
from persona_terminal.persona3.persona3_state import P3Store, MOON
from persona_terminal.persona3.persona3_upper import HOTEL_DAY

ENTER='\n'
ESC='\x1b'


class OperationRouteTests(TestCase):
    def make_app(self,phase,day):
        tmp=TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/'p3.json'
        store=P3Store(self.path);store.new_game()
        store.commit(phase=phase,day=day,xp=1190)
        app=P3App(None,store,seed=17)
        app.w,app.h=65,25
        return app

    def view(self,app):
        writes=[]
        app.put=lambda y,x,text,*_:writes.append((y,x,str(text)))
        app.draw()
        for y,x,text in writes:
            if text.strip():
                self.assertTrue(0<=y<app.h,(y,text))
                self.assertTrue(0<=x and x+len(text)<app.w,(x,text))
        return '\n'.join(t for _,_,t in writes)

    def walk(self,app,target):
        r=app.train_route
        q=deque(((r.position,()),))
        seen={r.position}
        while q:
            p,keys=q.popleft()
            if p==target:break
            for key in (C.KEY_LEFT,C.KEY_RIGHT,C.KEY_UP,C.KEY_DOWN):
                probe=TrainRoute(r.car,p,r.reunited)
                if probe.move(key) and probe.position not in seen:
                    seen.add(probe.position)
                    q.append((probe.position,keys+(key,)))
        else:self.fail(f'Unreachable in car {r.car}: {target}')
        for k in keys:app.key(k)
        self.assertEqual(r.position,target)

    def test_train_real_inputs_before_clock_and_brake_payoff(self):
        app=self.make_app('monorail',MOON)
        before=self.path.read_bytes()
        app.key(ENTER)
        self.assertEqual(app.page,'train-cars')
        self.assertIn('Junpei breaks into a run',self.view(app))
        self.assertIsNone(app.battle)
        app.key(ENTER)
        self.assertEqual(app.train_route.car,0)
        app.key(C.KEY_RIGHT);app.key(C.KEY_UP)
        self.assertEqual(app.train_route.position,(1,1))  # seat blocks you
        for car in range(3):
            self.assertEqual(app.train_route.car,car)
            if car==2:break
            self.walk(app,_HATCH);app.key(ENTER)
        self.walk(app,_HATCH);app.key(ENTER)
        self.assertIn('Regroup with Junpei',app.notice)
        self.assertIsNone(app.battle)
        self.walk(app,(_JUNPEI[0]-1,1))
        self.assertIn('ENTER REGROUP',self.view(app))
        app.key(ENTER)
        self.assertTrue(app.train_route.reunited)
        self.walk(app,_HATCH)
        self.assertEqual(self.path.read_bytes(),before)
        app.key(ENTER)
        self.assertEqual((app.battle.encounter,app.battle.clock),('priestess',30))
        self.assertEqual(tuple(u.name for u in app.battle.allies),(LEAD_ID,'Yukari','Junpei'))
        self.assertEqual(self.path.read_bytes(),before)
        # Cover the transition and clock isolation, without turning this into a
        # combat-balance fixture: the independent playthrough wins normally.
        app.battle.outcome='win'
        app.key(ENTER)
        self.assertEqual((app.page,app.record.day),('train-brake',date(2009,5,10)))
        saved=self.path.read_bytes()
        self.assertIn('ENTER PULL BRAKE',self.view(app))
        app.key(ENTER)
        self.assertIn('The brakes catch',self.view(app))
        self.assertNotEqual(self.path.read_bytes(),saved)
        self.assertEqual(app.record.aftermath,'monorail-stopped')
        app.key(ENTER)
        self.assertEqual((app.page,app.scene,app.record.aftermath),('story','finale','finale'))

    def test_hotel_decoys_reverse_floor_order_and_real_resources_preserved(self):
        app=self.make_app('hotel',HOTEL_DAY)
        app.key('s');app.key(' ')
        self.assertEqual(app.battle.encounter,'hotel-hierophant')
        app.battle.allies[0].hp-=17
        app.battle.allies[0].sp-=13
        app.battle.inventory['Medicine']-=1
        resources=app.battle.resources
        inventory=dict(app.battle.inventory)
        initial_party=tuple(u.name for u in app.battle.allies)
        app.battle.outcome='win';app.key(ENTER)
        before=self.path.read_bytes()
        self.assertEqual(app.page,'hotel-hall')
        self.assertIn('Room 204',self.view(app))
        self.assertEqual((app.resources,app.inventory),(resources,inventory))
        app.key('2')  # Room 204 is an actual decoy, not a hidden route alias.
        self.assertIn('ROOM 204',self.view(app))
        app.key('i');self.assertIn('the room and your squad.',' '.join(self.view(app).split()))
        app.key(ENTER);self.assertEqual(app.hotel_cleared,set())
        app.key(ESC);self.assertEqual(app.i,1)
        app.key('4')  # Take the stairs first; 304 may be solved before 205.
        self.assertIn('3F HALL',self.view(app))
        app.key('4');self.assertIn('suite still won',app.notice)  # no Lovers yet
        app.key('2')
        self.assertIn('nobody is in it.',self.view(app))
        app.key(ENTER)
        self.assertEqual(app.hotel_cleared,{'304'})
        app.key('4');self.assertIn('suite still won',app.notice)
        app.key('5');app.key('3')  # Go back to 2F, enter Room 205.
        self.assertIn('ROOM 205',self.view(app))
        app.key(C.KEY_DOWN)
        self.assertIn('nobody is in it.',self.view(app))
        app.key(ENTER)
        self.assertEqual(app.hotel_cleared,{'205','304'})
        app.key('4')
        app.w,app.h=96,34
        self.assertIn('second Shadow is waiting',self.view(app))
        self.assertEqual(self.path.read_bytes(),before)
        app.key('4')
        self.assertEqual(app.battle.encounter,'hotel-lovers')
        self.assertEqual(tuple(u.name for u in app.battle.allies),initial_party)
        self.assertIn('Yukari',initial_party)
        self.assertEqual((app.battle.resources,app.battle.inventory),(resources,inventory))
        self.assertEqual(self.path.read_bytes(),before)


class MonorailArtTests(TestCase):
    def test_train_motion_and_stopped_cab_are_native_at_both_terminal_sizes(self):
        from persona_terminal.persona3.persona3_operation_art import train
        for width,height in ((60,7),(91,12)):
            enter=train(width,height,1,0)
            moving=train(width,height,1,.42)
            cab=train(width,height,3,.42,braking=True)
            stop=train(width,height,3,.42,braking=True,stopped=True)
            self.assertEqual(len({enter,moving,cab,stop}),4)
            self.assertEqual(stop,train(width,height,3,4.0,braking=True,stopped=True))
            for frame in (enter,moving,cab,stop):
                self.assertEqual(len(frame),height)
                self.assertTrue(all(sum(len(run) for run,_ in row)==width for row in frame))
                self.assertGreater(sum(0x2801<=ord(ch)<=0x28ff
                    for row in frame for run,_ in row for ch in run),width*height//4)
