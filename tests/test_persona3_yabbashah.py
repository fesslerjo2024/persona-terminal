"""Lower Yabbashah field routing, optional roguelike rooms, and new-date continuity."""
from collections import deque
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
import json

from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_combat import ENCOUNTERS, LEAD_ID, PERSONAS
from persona_terminal.persona3.persona3_state import FieldRecord,P3Store,_encode
from persona_terminal.persona3.persona3_thebel import DIRECTIONS,_blocks
from persona_terminal.persona3.persona3_upper import AFTER_HOTEL
from persona_terminal.persona3.persona3_yabbashah import (AFTER_AUGUST, AIGIS, AUGUST_MOON, BEACH, DOOR,
                               FLOORS, OPENS, PASSAGE, YAKUSHIMA)


class YabbashahTests(TestCase):
    def setUp(self):
        td=TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.path=Path(td.name)/'p3.json'
        self.store=P3Store(self.path)
        self.store.new_game()

    def app(self,**kw):
        self.store.commit(**kw)
        return P3App(None,self.store,seed=9)

    def paint(self,app):
        app.w,app.h=65,25
        events=[]
        app.put=lambda y,x,t,*_:events.append((y,x,str(t)))
        app.draw()
        self.assertTrue(all(0<=y<24 and 0<=x<=x+len(t)<65 for y,x,t in events),events)
        return ' '.join(t for _,__,t in events)

    def test_old_closed_july8_reopens_without_rewriting_and_preserves_progress(self):
        older=json.loads(_encode(FieldRecord(phase='calendar',day=AFTER_HOTEL,
                                             depth=5,arqa=4,upper=3,xp=2200,yen=450)))
        older['version']=4;older['state']['phase']='complete'
        names=('phase','day','depth','yen','aid','academics','courage','charm','activity',
               'masks','equipped','xp','archive','arqa','upper','rescues')
        older['state']={key:older['state'][key] for key in names}
        saved=json.dumps(older,indent=1).encode()
        self.path.write_bytes(saved)
        self.store.reload()
        app=P3App(None,self.store)
        self.assertEqual((app.page,app.record.day,app.record.upper,app.record.xp),
                         ('calendar',AFTER_HOTEL,3,2200))
        self.assertEqual(self.path.read_bytes(),saved)
        app.next_night(skip=True)
        self.assertEqual((app.record.day,app.open_blocks[-1]),(OPENS,'yabba'))

    def test_trip_reloads_and_aigis_not_assignable_before_24(self):
        app=self.app(phase='calendar',day=OPENS)
        self.assertFalse(app.aigis_active)
        app.next_night(skip=True)
        self.assertEqual(app.record.day,YAKUSHIMA)
        self.assertIn('KIRIJO VILLA',self.paint(app))
        app.key('1');app.key('2')
        self.assertEqual(app.record.day,BEACH)
        app=P3App(None,P3Store(self.path))
        app.key('2');app.key('1')
        self.assertIn('AIGIS',self.paint(app))
        self.assertFalse(app.aigis_active)
        app.key('1');app.key('\n')
        self.assertEqual((app.record.day,app.page),(AIGIS,'calendar'))
        app.open_field_party()
        app.key('1');app.key('5');app.key('s')
        self.assertIn('Aigis',app.resources)
        self.assertNotIn('Yukari',app.resources)
        self.assertEqual(len(app.resources),4)

    def test_monad_passage_carries_and_commits_once_after_second_battle(self):
        app=self.app(phase='calendar',day=AIGIS,yabba=5,fragments=6)
        app.deploy();app.key(' ');app.key('\n');app.key(' ')
        old=self.path.read_bytes()
        app.key('g');app.key('\n')
        self.assertEqual(app.encounter,'monad-passage-maya')
        app.battle.allies[0].hp=81
        app.battle.inventory['Medicine']=1
        app.battle.charge[LEAD_ID]=49
        app.battle.outcome='win';app.key('\n')
        self.assertEqual(self.path.read_bytes(),old)
        self.assertIn('Encounter 2/2',self.paint(app))
        app.key('\n')
        self.assertEqual((app.battle.allies[0].hp,app.battle.inventory['Medicine'],
                          app.battle.charge[LEAD_ID]),(81,1,49))
        app.battle.outcome='win';app.key('\n')
        self.assertEqual((app.page,app.record.monad,app.record.fragments,app.record.yabba),
                         ('hall',(PASSAGE,),11,5))
        app.key('g')
        self.assertEqual(app.page,'hall')

    def test_clock_is_opt_in_cost_and_does_not_spend_when_full(self):
        app=self.app(phase='calendar',day=AIGIS,yabba=1,fragments=7)
        app.deploy();app.key(' ')
        old=self.path.read_bytes()
        app.key('c');app.key('\n')
        self.assertEqual(self.path.read_bytes(),old)
        app.resources[LEAD_ID]=(75,3)
        app.key('c');app.key('\n')
        self.assertEqual((app.resources,app.record.fragments),(app.caps,0))
        self.assertEqual(app.inventory['Medicine'],3)

    def test_floor_tiles_and_canon_group_sequence(self):
        self.assertEqual([f.number for f in FLOORS],[70,77,80,82,90,91])
        for f in FLOORS:
            self.assertIn(f.mask,PERSONAS)
            self.assertIn(f.encounter,ENCOUNTERS)
            blocked=_blocks(f)
            self.assertTrue(not blocked.intersection({f.start,f.stairs,*f.patrol}),f)
            seen={f.start};queue=deque(seen)
            while queue:
                x,y=queue.popleft()
                for dx,dy in DIRECTIONS.values():
                    pos=x+dx,y+dy
                    if pos not in seen and pos not in blocked:seen.add(pos);queue.append(pos)
            self.assertIn(f.stairs,seen)

    def test_august_pick_and_retry_are_independent_of_tower_depth(self):
        app=self.app(phase='calendar',day=AIGIS)
        app.next_night(skip=True)
        self.assertEqual((app.discovery_key,app.record.day),('bunker',AUGUST_MOON))
        app.key('1');app.key('1');app.key('1')
        self.assertEqual(app.page,'august')
        now=self.path.read_bytes()
        app.key('\n');app.key('1');app.key('5');app.key('s')
        self.assertEqual(app.encounter,'chariot-justice')
        self.assertNotIn('Yukari',[x.name for x in app.battle.allies])
        self.assertIn('Aigis',[x.name for x in app.battle.allies])
        app.battle.outcome='loss';app.key('\n')
        self.assertEqual(app.page,'august')
        self.assertEqual(self.path.read_bytes(),now)
