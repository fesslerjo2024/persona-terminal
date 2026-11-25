"""Progression and save compatibility for the July Persona 3 chapter."""
from collections import deque
from datetime import date,timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import curses as C
import json

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_arqa import BRIDGE
from persona_terminal.persona3.persona3_combat import LEAD_ID
from persona_terminal.persona3.persona3_state import P3SaveError,P3Store,_encode
from persona_terminal.persona3.persona3_thebel import DIRECTIONS,Hall,_blocks
from persona_terminal.persona3.persona3_combat import ENCOUNTERS
from persona_terminal.persona3.persona3_mirror_art import observation
from persona_terminal.persona3 import persona3_upper as upper


class UpperArqaTests(TestCase):
    def setUp(self):
        td=TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.path=Path(td.name)/'p3.json'
        self.store=P3Store(self.path)
        self.store.new_game()

    def fixture(self,*args,**kwargs):
        self.store.commit(*args,**kwargs)
        return P3App(None,self.store,seed=2)

    def paint(self,app,w=65,h=25):
        app.w,app.h=w,h
        captured=[]
        app.put=lambda y,x,t,*_:captured.append((y,x,str(t)))
        app.draw()
        self.assertTrue(all(0<=y<h-1 and 0<=x<=x+len(t)<w for y,x,t in captured),
                        [(y,x,t) for y,x,t in captured if x+len(t)>=w or y>=h-1])
        return ' '.join(t for _,__,t in captured)

    def test_old_june13_continues_same_day_and_all_existing_progress(self):
        app=self.fixture(phase='calendar',day=BRIDGE,arqa=5,depth=4,xp=1420,
                         masks=('Orpheus','Apsaras'),equipped='Apsaras',
                         archive=(('Orpheus',''),('Apsaras','Agi')))
        old=json.loads(_encode(app.record))
        old['version']=3
        for key in ('upper','rescues','yabba','monad','fragments','yabba_upper','tziah','tziah_upper','harabah','harabah_upper','adamah','ending','junpei_flowers','theurgy_drill_seen'):old['state'].pop(key)
        old['state']['phase']='complete'
        prior=json.dumps(old,separators=(',',':')).encode()
        self.path.write_bytes(prior)
        self.store.reload()
        migrated=P3App(None,self.store)
        self.assertEqual(self.path.read_bytes(),prior)
        self.assertEqual((migrated.page,migrated.record.day,migrated.record.arqa,migrated.record.upper,
                          migrated.record.depth,migrated.record.xp),('calendar',BRIDGE,5,0,4,1420))
        self.assertEqual(migrated.record.stock['Apsaras'],('Agi',))
        migrated.next_night()
        self.assertEqual(json.loads(self.path.read_bytes())['version'],11)
        self.assertEqual(self.store.state.day,BRIDGE+timedelta(days=1))

    def test_rescue_needs_valid_date_floor_distance_and_never_repeats_reward(self):
        early=upper.RESCUES[0].day-timedelta(days=1)
        app=self.fixture(phase='calendar',day=early,upper=2,yen=15,aid=0)
        self.assertEqual(app.active_rescues(),())
        with self.assertRaises(P3SaveError):self.store.rescue_civilian('ayako',50)
        self.store.advance_night()
        self.assertEqual([c.id for c in app.active_rescues()],['ayako'])
        app.deploy();app.key(' ');app.key('r')
        self.assertIn('50F  Ayako',self.paint(app))
        app.key(ESC);app.key('\n');app.key(' ')
        self.assertEqual(app.hall.floor.number,50)
        self.assertIn('R RESCUE',self.paint(app))
        original=self.path.read_bytes()
        app.key('r')
        self.assertIn('Move closer',app.notice)
        self.assertEqual(self.path.read_bytes(),original)
        app.hall.pos=(5,5)
        app.key('r');app.key('r')
        self.assertEqual((app.record.rescues,app.record.yen,app.record.aid,app.hall.steps),
                         (('ayako',),135,1,0))
        with self.assertRaises(P3SaveError):self.store.rescue_civilian('ayako',50)
        app.next_night(skip=True)
        self.assertEqual((app.record.day,app.page),(upper.RESCUES[1].day,'calendar'))
        self.assertEqual([case.id for case in app.active_rescues()],['kenjiro','yoshimi'])
        app.next_night(skip=True)
        self.assertEqual((app.record.day,app.page),(upper.HOTEL_DAY,'hotel'))
        self.assertFalse(app.active_rescues())

    def test_upper_warps_full_list_and_crossings(self):
        app=self.fixture(phase='calendar',day=upper.OPENS,depth=5,arqa=5,upper=7)
        app.deploy();app.key(' ')
        app.key('2');app.key(' ');app.key('t')
        self.assertIn('○ 64F',self.paint(app))
        app.key(C.KEY_LEFT)
        self.assertEqual(app.block,'arqa')
        app.key('1');app.key(' ')
        self.assertEqual(app.block,'upper')
        app.key('t');app.key(C.KEY_LEFT);app.key('\t');app.key('\n');app.key(' ')
        self.assertIn('43F / LOWER ARQA BORDER',self.paint(app,96,34))
        app.key('\n')
        self.assertIn('69F / UPPER ARQA BORDER',self.paint(app))

    def test_hotel_carry_heal_mirror_selection_retry_and_success(self):
        app=self.fixture(phase='hotel',day=upper.HOTEL_DAY,xp=700,
                         masks=('Orpheus','Apsaras'),equipped='Apsaras')
        original=self.path.read_bytes()
        self.assertIn('Yukari  /  Healing / Wind  [LOCKED]',self.paint(app))
        app.key('3');app.key('5');app.key('s');app.key(' ')
        self.assertEqual([u.name for u in app.battle.allies],[LEAD_ID,'Yukari','Akihiko','Mitsuru'])
        makoto=app.battle.allies[0]
        makoto.hp=38;makoto.sp=7
        app.battle.inventory['Medicine']=1
        app.battle.inventory['Dis-Charm']=1
        app.battle.charge[LEAD_ID]=67
        app.battle.outcome='win'
        app.key('\n')
        self.assertEqual(app.page,'hotel-hall')
        self.assertIn('H HEAL',self.paint(app))
        app.key('h');app.key('1');app.key('1');app.key(ESC)
        self.assertEqual(app.resources[LEAD_ID],(88,7))
        self.assertEqual(app.inventory['Medicine'],0)
        app.key('3')
        base=self.paint(app)
        self.assertIn('Mirror by the curtains',base)
        self.assertNotIn(observation(False),base)
        app.key('i')
        self.assertIn(observation(True).split()[0],self.paint(app))
        app.key(C.KEY_DOWN)
        self.assertIn(observation(False).split()[0],self.paint(app))
        self.assertEqual(app.mirror_index,0)
        app.key('i')
        app.key('1')
        self.assertIn('reflection looks back',app.notice)
        self.assertEqual(app.mirror_index,0)
        app.key('2')
        self.assertEqual(app.page,'hotel-hall')
        app.key('4');app.key('2')
        self.assertIn('ROOM 304',self.paint(app))
        app.key(ESC);app.key('2');app.key('1');app.key('4')
        self.assertEqual([u.name for u in app.battle.allies],[LEAD_ID,'Yukari','Akihiko','Mitsuru'])
        self.assertEqual((app.battle.resources[LEAD_ID],app.battle.inventory['Medicine'],
                          app.battle.inventory['Dis-Charm'],app.battle.charge[LEAD_ID]),
                         ((88,7),0,1,67))
        self.assertEqual(self.path.read_bytes(),original)
        app.battle.outcome='loss'
        app.key('\n')
        self.assertEqual(app.page,'hotel')
        self.assertEqual(self.path.read_bytes(),original)
        app.key('s');app.key(' ')
        self.assertEqual(app.battle.inventory['Medicine'],3)
        app.battle.outcome='win';app.key('\n')
        for k in '324214':app.key(k)
        app.battle.outcome='win';app.key('\n')
        self.assertIn('AFTER THE HOTEL',self.paint(app))
        self.assertEqual((app.record.day,app.record.xp),(upper.AFTER_HOTEL,700+upper.HOTEL_XP))
        with self.assertRaises(P3SaveError):self.store.clear_operation('hotel-lovers')

    def test_hotel_toggles_individual_members_with_fixed_pair_and_slot_limit(self):
        app=self.fixture(phase='hotel',day=upper.HOTEL_DAY,xp=700)
        original=self.path.read_bytes()
        for w,h in ((65,25),(120,40)):
            text=self.paint(app,w,h)
            for label in ('● Makoto','● Yukari','● Junpei','● Akihiko','○ Mitsuru',
                          '↵ TOGGLE','S DEPLOY','ESC TITLE','two Shadows inside the hotel',
                          'Yukari is assigned to keep you healed','Choose up to two more allies'):
                self.assertIn(label,text)
        app.key(C.KEY_DOWN);app.key('\n')
        self.assertEqual(app.notice,'Yukari is always active.')
        app.key('1')
        self.assertEqual(app.notice,'Makoto is always active.')
        app.key('5')
        self.assertEqual(app.notice,'Remove an active ally first.')
        self.assertEqual(app.hotel_edit,['Junpei','Akihiko'])
        app.key('3');app.key('4')
        text=self.paint(app)
        self.assertIn('2/4 ACTIVE',text)
        self.assertIn('○ Junpei',text)
        self.assertIn('○ Akihiko',text)
        app.key('s')
        self.assertEqual(app.page,'hotel-intro')
        app.key(' ')
        self.assertEqual([u.name for u in app.battle.allies],[LEAD_ID,'Yukari'])
        self.assertEqual(self.path.read_bytes(),original)

    def test_authored_floor_and_rescue_tiles_are_reachable(self):
        by_floor={f.number:f for f in upper.FLOORS}
        for f in upper.FLOORS:
            with self.subTest(floor=f.number):
                blocked=_blocks(f)
                self.assertFalse(blocked.intersection(f.patrol))
                self.assertNotIn(f.start,blocked)
                seen={f.start};queue=deque([f.start])
                while queue:
                    x,y=queue.popleft()
                    for dx,dy in DIRECTIONS.values():
                        p=(x+dx,y+dy)
                        if p not in blocked and p not in seen:seen.add(p);queue.append(p)
                self.assertIn(f.stairs,seen)
                if f.number in upper.BY_FLOOR:self.assertIn(upper.BY_FLOOR[f.number].pos,seen)
        self.assertTrue(all(x.floor in by_floor for x in upper.RESCUES))

    def test_wait_with_incomplete_rescues_requires_visible_confirmation(self):
        app=self.fixture(phase='calendar',day=date(2009,6,26))
        before=self.path.read_bytes()
        app.key('4');app.key('4')
        self.assertIn('cases will expire',self.paint(app))
        app.key(ESC)
        self.assertEqual(self.path.read_bytes(),before)

    def test_distinct_patrols_choose_floor_encounter_even_on_replay(self):
        self.assertEqual([Hall(i,floors=upper.FLOORS,block='upper',replay=True).encounter
                          for i in (0,2,4,6)],
                         ['upper-patrol','upper-patrol-50','upper-patrol-56','upper-patrol-56'])
        self.assertEqual(len({ENCOUNTERS[n][1] for n in
                              ('upper-patrol','upper-patrol-50','upper-patrol-56')}),3)
        self.assertEqual(Hall(1,floors=upper.FLOORS,block='upper',replay=True).encounter,'upper-patrol')
