"""Campaign boundary checks for the independent Persona 3 field chapter."""
from collections import deque
from datetime import date
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from battle_ui import ESC
from campaign_state import Campaign
from persona3_app import P3App
from persona3_state import AWAKENING, END, MOON, TUTORIAL, P3SaveError, P3Store, distinct_slots
from persona3_thebel import DIRECTIONS, FLOORS, Hall


class FieldSliceTests(TestCase):
    def setUp(self):
        folder=TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path=Path(folder.name)/'persona3.json'
        self.store=P3Store(self.path)

    def test_reading_missing_save_never_initializes_a_file(self):
        self.assertEqual(self.store.status,'missing')
        self.assertFalse(self.path.exists())
        P3Store(self.path)
        self.assertFalse(self.path.exists())

    def test_separate_slots_reject_symlink_hardlink_and_foreign_record(self):
        p5=self.path.with_name('p5.json')
        Campaign(p5).new_game()
        raw=p5.read_bytes()
        self.assertFalse(distinct_slots(p5,p5))
        self.path.symlink_to(p5)
        self.assertFalse(distinct_slots(p5,self.path))
        self.path.unlink()
        self.path.hardlink_to(p5)
        self.assertFalse(distinct_slots(p5,self.path))
        self.store.reload()
        self.assertEqual(self.store.status,'foreign')
        with self.assertRaisesRegex(P3SaveError,'another game'):
            self.store.new_game(confirm=True)
        self.assertEqual(p5.read_bytes(),raw)
        self.assertEqual(self.path.read_bytes(),raw)

    def test_confirmed_new_game_makes_exact_backup_and_reloads(self):
        self.store.new_game()
        self.store.commit(phase='awakening',day=AWAKENING)
        before=self.path.read_bytes()
        with self.assertRaises(P3SaveError):self.store.new_game()
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual(P3Store(self.path).state.phase,'awakening')
        self.store.new_game(confirm=True)
        self.assertEqual(P3Store(self.path).state.phase,'arrival')
        backup,=self.path.parent.glob('persona3.backup-*.json')
        self.assertEqual(backup.read_bytes(),before)

    def test_calendar_persists_once_daily_activity_and_boss_unlocks_without_climb(self):
        self.store.new_game();self.store.commit(phase='tartarus',day=TUTORIAL)
        self.store.advance_night()
        first=self.store.activity('track')
        self.assertEqual((first.courage,first.aid),(1,2))
        reloaded=P3Store(self.path)
        with self.assertRaises(P3SaveError):reloaded.activity('track')
        while reloaded.state.day<MOON:reloaded.advance_night()
        self.assertEqual((reloaded.state.phase,reloaded.state.depth),('monorail',0))

    def test_maps_are_distinct_and_stairs_require_then_retain_fight_state(self):
        routes=set()
        for i,floor in enumerate(FLOORS):
            hall=Hall(i)
            first=hall.shadow
            self.assertTrue(all(p not in hall.blocked for p in floor.patrol))
            queue=deque([(hall.pos,())]);seen={hall.pos}
            while queue:
                (x,y),path=queue.popleft()
                if (x,y)==floor.stairs:break
                for d,(a,b) in DIRECTIONS.items():
                    n=x+a,y+b
                    if n not in seen and n not in hall.blocked:
                        queue.append((n,path+(d,)));seen.add(n)
            else:self.fail('Unreachable staircase.')
            routes.add(path)
            for d in path[:2]:hall.step(d)
            self.assertNotEqual(hall.shadow,first)
            for d in path[2:-1]:hall.step(d)
            self.assertEqual(hall.step(path[-1]),'battle')
            hall.defeated=True
            inverse={'up':'down','down':'up','left':'right','right':'left'}
            hall.step(inverse[path[-1]])
            self.assertEqual(hall.step(path[-1]),'stairs')
        self.assertEqual(len(routes),len(FLOORS))

    def test_timeout_returns_to_exact_preboarding_save_and_bag(self):
        self.store.new_game()
        self.store.commit(phase='monorail',day=MOON)
        app=P3App(None,self.store,seed=3)
        before=self.path.read_bytes()
        from test_persona3_operation_route import OperationRouteTests
        def board():
            app.key('\n')
            for _ in range(2):
                OperationRouteTests.walk(self,app,(8,1));app.key('\n')
            OperationRouteTests.walk(self,app,(2,1));app.key('\n')
            OperationRouteTests.walk(self,app,(8,1));app.key('\n')
        board()
        first=app.battle
        original_resources,bag=first.resources,dict(first.inventory)
        first.clock=1
        self.assertIsNone(first.act('guard'))
        self.assertEqual(first.outcome,'timeout')
        app.key('l')
        self.assertEqual(app.page,'battle')
        self.assertEqual(first.overlay,'log')
        app.key(ESC)
        app.key('\n')
        self.assertEqual(app.page,'operation')
        self.assertEqual(before,self.path.read_bytes())
        board()
        self.assertEqual(app.battle.resources,original_resources)
        self.assertEqual(app.battle.inventory,bag)

    def test_fusion_consumes_stock_and_inheritance_survives_resummoning(self):
        self.store.new_game()
        self.store.commit(masks=('Orpheus','Pixie'),yen=130)
        self.assertIn(('Orpheus','Bash'),self.store.inheritance_options('Nekomata'))
        enriched=self.store.fuse('Nekomata','Bash')
        self.assertEqual((enriched.masks,enriched.yen),(('Nekomata',),130))
        self.assertEqual(enriched.stock,{'Nekomata':('Bash',)})
        self.assertEqual(enriched.equipped,'Nekomata')
        reload=P3Store(self.path)
        self.assertEqual(reload.state.stock,enriched.stock)
        self.assertIn('Orpheus',reload.state.compendium)
        with self.assertRaises(P3SaveError):reload.fuse('Nekomata')
        reload.resummon('Orpheus')
        self.assertEqual((reload.state.masks,reload.state.yen),(('Nekomata','Orpheus'),85))
        self.assertEqual(reload.state.equipped,'Nekomata')

    def test_v1_load_preserves_exact_bytes_and_progress_until_next_upgrade_write(self):
        v1={'game':'persona-3-terminal','version':1,'state':{
            'phase':'calendar','day':'2009-04-25','depth':3,'yen':340,'aid':1,
            'academics':1,'courage':2,'charm':3,'activity':'library',
            'masks':['Orpheus','Pixie','Angel'],'equipped':'Angel',
        }}
        raw=json.dumps(v1).encode()
        self.path.write_bytes(raw)
        self.store.reload()
        s=self.store.state
        self.assertEqual((s.day,s.depth,s.yen,s.equipped),(date(2009,4,25),3,340,'Angel'))
        self.assertEqual(tuple(s.compendium),tuple(v1['state']['masks']))
        self.assertEqual((s.xp,s.level),(280,3))
        self.assertEqual(self.path.read_bytes(),raw)
        self.store.grant_xp(25)
        self.assertEqual(json.loads(self.path.read_bytes())['version'],11)
        self.assertEqual(P3Store(self.path).state.depth,3)

    def test_wait_for_moon_is_available_underleveled_and_keeps_partial_progress(self):
        self.store.new_game();self.store.commit(phase='calendar',day=date(2009,4,21),depth=1,
                                                   xp=100,masks=('Orpheus','Pixie'))
        app=P3App(None,self.store);before=self.path.read_bytes()
        app.key('4');app.key('4')
        self.assertEqual(app.overlay,'wait')
        app.key(ESC)
        self.assertEqual(self.path.read_bytes(),before)
        app.key('4');app.key('\n')
        self.assertEqual((app.page,app.record.day,app.record.depth,app.record.xp),('operation',MOON,1,100))
        self.assertEqual(app.record.masks,('Orpheus','Pixie'))
        self.assertIsNone(app.battle)
