"""Progression, migration and combat handoffs for Persona 3's June slice."""
import curses as C
from collections import deque
from datetime import timedelta
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_arqa import AFTER_RESCUE, AKIHIKO_JOINS, BRIDGE, FLOORS, OPENS, RESCUE_DAY
from persona_terminal.persona3.persona3_combat import ENCOUNTERS, PERSONAS
from persona_terminal.persona3.persona3_state import MOON, MOON_XP, P3SaveError, P3Store, _encode, available_fusions
from persona_terminal.persona3.persona3_thebel import DIRECTIONS, _blocks


class ArqaTests(TestCase):
    def setUp(self):
        tmp=TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/'p3.json'
        self.store=P3Store(self.path)
        self.store.new_game()

    def fixture(self,day,phase='calendar',**kw):
        self.store.commit(phase=phase,day=day,**kw)
        return P3App(None,self.store,seed=22)

    def paint(self,app,w=65,h=25):
        events=[]
        app.w,app.h=w,h
        app.put=lambda y,x,value,*args:events.append((y,x,str(value)))
        app.draw()
        self.assertTrue(all(0<=y<h-1 and 0<=x<w-1 and x+len(value)<=w-1
                            for y,x,value in events),
                        [(y,x,value) for y,x,value in events if x+len(value)>w-1 or y>=h-1])
        return '\n'.join(value for _,_,value in events)

    def test_v2_may10_is_an_open_calendar_without_replayed_rewards_or_writes(self):
        existing=self.fixture(OPENS,depth=2,yen=134,xp=624,equipped='Nekomata',
                              masks=('Nekomata','Apsaras'),
                              archive=(('Nekomata','Bash'),('Apsaras',''),('Orpheus','')))
        old=json.loads(_encode(existing.record))
        old['version']=2
        for key in ('arqa','upper','rescues','yabba','monad','fragments','yabba_upper','tziah','tziah_upper','harabah','harabah_upper','adamah','ending','junpei_flowers','theurgy_drill_seen'):old['state'].pop(key)
        old['state']['phase']='complete'
        prior=json.dumps(old,indent=1).encode()
        self.path.write_bytes(prior)
        self.store.reload()
        app=P3App(None,self.store)
        s=app.record
        self.assertEqual((app.page,s.day,s.depth,s.arqa,s.xp,s.yen),('calendar',OPENS,2,0,624,134))
        self.assertEqual((s.equipped,s.stock['Nekomata'],s.compendium['Orpheus']),('Nekomata',('Bash',),''))
        self.assertEqual(self.path.read_bytes(),prior)
        with self.assertRaises(P3SaveError):self.store.clear_operation('priestess')
        self.assertEqual(self.path.read_bytes(),prior)
        self.store.advance_night()
        self.assertEqual(json.loads(self.path.read_bytes())['version'],11)
        self.assertEqual(P3Store(self.path).state.xp,624)

    def test_preserves_old_preboard_and_clear_is_one_transaction(self):
        app=self.fixture(MOON,'monorail',depth=1,xp=100)
        before=self.path.read_bytes()
        self.assertEqual(app.page,'operation')
        app.key('t');app.key(' ')
        app.key('x');app.key('\n')
        self.assertEqual(self.path.read_bytes(),before)
        self.store.clear_operation('priestess')
        s=P3Store(self.path).state
        self.assertEqual((s.phase,s.day,s.xp,s.depth,s.arqa),('calendar',OPENS,100+MOON_XP,1,0))
        with self.assertRaises(P3SaveError):self.store.clear_operation('priestess')

    def test_replay_uses_correct_block_and_resume_keeps_supplies(self):
        app=self.fixture(OPENS,depth=2,arqa=3)
        unused=self.path.read_bytes()
        app.deploy();app.key(' ')
        self.assertIn('36F Dice Gate',self.paint(app))
        self.assertIn('←→ BLOCK',self.paint(app,96,34))
        app.key(C.KEY_LEFT);app.key('\n')
        self.assertEqual(app.page,'teleport')
        app.key(ESC)
        self.assertEqual((app.page,app.hall.floor.number),('hall',8))
        hall=app.hall
        app.resources['Protagonist']=(54,12)
        app.key('t');app.key(C.KEY_RIGHT);app.key('\n');app.key(' ')
        self.assertIs(app.hall,hall)
        self.assertEqual(app.block,'thebel')
        self.assertEqual(app.resources['Protagonist'],(54,12))
        self.assertEqual(self.path.read_bytes(),unused)

    def test_arqa_rewards_independent_of_thebel_and_35_to_36_carries_items(self):
        app=self.fixture(OPENS,depth=1,arqa=2,xp=700)
        app.deploy();app.key(' ');app.key('\n');app.key(' ')
        self.assertEqual(app.hall.floor.number,35)
        app.hall.pos=app.hall.floor.stairs
        app.battle=SimpleNamespace(resources=app.resources,inventory={'Soul Drop':0})
        app._finish_hall_battle()
        self.assertIn('Soul Drop',app.notice)
        self.assertEqual((app.record.depth,app.record.arqa),(1,3))
        app.key('3') # Cup, then directly to next floor.
        self.assertEqual(app.hall.floor.number,36)
        self.assertEqual(app.inventory['Soul Drop'],1)
        self.assertEqual(P3Store(self.path).state.arqa,3)

    def test_rescue_navigation_retries_and_june13_no_disk_writes(self):
        app=self.fixture(AKIHIKO_JOINS-timedelta(days=1),depth=2,xp=395)
        self.assertNotIn('Akihiko',app.current_party)
        app.next_night()
        self.assertIn('Akihiko',app.current_party)
        app.next_night(skip=True)
        self.assertEqual(app.record.day,RESCUE_DAY)
        self.assertIn('THE SEARCH FOR FUUKA',self.paint(app))
        before=self.path.read_bytes()
        app.key('\n');app.key('1')
        self.assertEqual(app.search_step,0)
        app.key('2');app.key('1')
        self.assertIn('AT THE ENTRANCE',self.paint(app))
        app.key('1')
        self.assertIn('LUCIA',self.paint(app))
        app.key('1')
        self.assertIn('A VOICE IN TARTARUS',self.paint(app))
        app.key('1')
        self.assertEqual([x.label for x in app.battle.allies],['Makoto','Junpei','Akihiko'])
        self.assertEqual(self.path.read_bytes(),before)
        app.battle.outcome='loss';app.key('\n')
        self.assertEqual(app.page,'operation')
        self.assertEqual(self.path.read_bytes(),before)
        app.key('\n');app.battle.outcome='win';app.key('\n')
        self.assertEqual(app.record.day,AFTER_RESCUE)
        self.assertTrue(app.fuuka_active)
        app.key('\n');app.next_night(skip=True)
        self.assertEqual(app.discovery_key,'pharos-visit')
        for _ in range(3):app.key('1')
        app.next_night(skip=True)
        self.assertEqual((app.record.day,app.page),(BRIDGE,'calendar'))
        app.key('4');app.key('5');app.key('2')
        self.assertTrue(app.battle.theurgy)
        self.assertEqual(app.battle.charge['Yukari'],100)
        self.assertEqual([u.label for u in app.battle.allies],['Makoto','Yukari','Akihiko','Mitsuru'])
        before=self.path.read_bytes()
        app.battle.outcome='win';app.key('\n')
        self.assertEqual((app.page,app.scene),('story','bridge'))
        self.assertTrue(app.record.theurgy_drill_seen)
        self.assertNotEqual(self.path.read_bytes(),before)
        seen=self.path.read_bytes()
        app.key('\n')
        self.assertEqual(app.page,'evening')
        app.key('5');app.key('2')
        self.assertEqual((app.page,app.battle.encounter),('battle','theurgy-drill'))
        app.battle.outcome='win';app.key('\n')
        self.assertEqual(self.path.read_bytes(),seen)
        app.key('\n');app.key('1')
        self.assertIn('TARTARUS / SQUAD',self.paint(app))
        app.key('1');app.key('4');app.key('s')
        self.assertEqual(tuple(app.resources),('Protagonist','Junpei','Akihiko','Mitsuru'))
        app.key(' ');app.key('x');app.key(ESC)
        self.assertEqual(app.page,'entrance')
        app.key('x');app.key('\n')
        self.assertEqual((app.page,app.record.day),('calendar',BRIDGE+timedelta(days=1)))
        self.assertNotEqual(self.path.read_bytes(),before)

    def test_four_ally_floor_and_early_recipes_fit_and_are_unlocked_in_date(self):
        app=self.fixture(AKIHIKO_JOINS)
        app.deploy();app.key(' ');app.key('\n');app.key(' ')
        for size in [(65,25),(96,34)]:
            text=self.paint(app,*size)
            self.assertIn('Akihiko',text)
        self.assertEqual(len(available_fusions(MOON)),3)
        self.assertTrue(all(result in PERSONAS for result,_ in available_fusions(OPENS)))

    def test_arqa_map_targets_and_patrol_tiles_accessible(self):
        self.assertEqual(tuple(x.number for x in FLOORS),(23,28,35,36,42))
        for floor in FLOORS:
            with self.subTest(floor=floor.number):
                self.assertIn(floor.encounter,ENCOUNTERS)
                self.assertIn(floor.mask,PERSONAS)
                blocked=_blocks(floor)
                self.assertFalse(set(floor.patrol)&blocked)
                seen={floor.start}
                queue=deque([floor.start])
                while queue:
                    x,y=queue.popleft()
                    for dx,dy in DIRECTIONS.values():
                        pos=(x+dx,y+dy)
                        if pos not in seen|blocked:seen.add(pos);queue.append(pos)
                self.assertIn(floor.stairs,seen)
