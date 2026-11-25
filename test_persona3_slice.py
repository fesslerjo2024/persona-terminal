"""Campaign boundary checks for the independent Persona 3 field chapter."""
from collections import deque
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
        app.key('\n')
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
        app.key('\n')
        self.assertEqual(app.battle.resources,original_resources)
        self.assertEqual(app.battle.inventory,bag)

    def test_fusion_keeps_parents_debits_once_and_survives_reload(self):
        self.store.new_game()
        self.store.commit(masks=('Orpheus','Pixie'),yen=130)
        enriched=self.store.fuse('Nekomata')
        self.assertEqual((enriched.masks,enriched.yen),(('Orpheus','Pixie','Nekomata'),20))
        self.store.commit(equipped='Nekomata')
        reloaded=P3Store(self.path)
        self.assertEqual(reloaded.state.equipped,'Nekomata')
        with self.assertRaises(P3SaveError):reloaded.fuse('Nekomata')
        self.assertEqual(reloaded.state.yen,20)
