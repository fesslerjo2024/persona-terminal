"""Upper-block navigation, Koromaru, and September calendar continuity."""
from datetime import date
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from persona3_app import P3App
from persona3_combat import ENCOUNTERS, LEAD_ID, P3Battle
from persona3_state import FieldRecord, P3Store, _encode
from persona3_thebel import _blocks
from persona3_yabbashah import AFTER_AUGUST
from persona3_yabbashah_upper import AFTER_HERMIT, FLOORS, HERMIT_DAY, OPENS, PASSAGE, PASSAGE_STAGES
from test_persona3_arqa_combat import Surface


class UpperYabbashah(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/'p3.json'
        self.store=P3Store(self.path)
        self.store.new_game()

    def app(self,**kw):
        self.store.commit(**kw)
        return P3App(None,self.store,seed=4)

    def view(self,app,w,h):
        surface=Surface(w,h)
        app.w,app.h=w,h;app.put=surface.put
        app.draw()
        return surface.text()

    def test_v5_august7_keeps_contents_and_can_reach_august8(self):
        blob=json.loads(_encode(FieldRecord(phase='calendar',day=AFTER_AUGUST,xp=3900,
                                             yabba=4,monad=('door',),fragments=6)))
        blob['version']=5
        [blob['state'].pop(key) for key in ('yabba_upper','tziah','tziah_upper','harabah','harabah_upper','adamah','ending','junpei_flowers','theurgy_drill_seen')]
        raw=json.dumps(blob).encode()
        self.path.write_bytes(raw);self.store.reload()
        app=P3App(None,self.store,seed=4)
        self.assertEqual((app.scene,app.record.yabba,app.record.fragments),('august-after',4,6))
        self.assertEqual(self.path.read_bytes(),raw)
        app.key('\n');app.key('4');app.key('3')
        self.assertEqual((app.record.day,app.scene),(OPENS,'koromaru'))
        self.assertEqual(app.open_blocks[-1],'yabba_upper')
        app.key('\n');app.key('4');app.key('1')
        self.assertIn('Continue to squad',self.view(app,65,25))
        app.key('\n')
        self.assertIn('Koromaru',self.view(app,65,25))
        app.key('1');app.key('6');app.key('s');app.key(' ')
        self.assertEqual((app.page,app.block),('entrance','yabba_upper'))
        self.assertIn('Koromaru',app.resources)
        self.assertNotIn('Yukari',app.resources)

    def test_august7_closed_legacy_phase_does_not_softlock(self):
        blob=json.loads(_encode(FieldRecord(phase='complete',day=AFTER_AUGUST)))
        blob['version']=5;[blob['state'].pop(key) for key in ('yabba_upper','tziah','tziah_upper','harabah','harabah_upper','adamah','ending','junpei_flowers','theurgy_drill_seen')]
        self.path.write_text(json.dumps(blob));self.store.reload()
        app=P3App(None,self.store,seed=2)
        self.assertEqual(app.page,'story')
        app.key('\n');app.key('4');app.key('3')
        self.assertEqual((app.record.day,app.scene),(OPENS,'koromaru'))

    def test_hermit_has_no_junpei_and_yukari_optional(self):
        app=self.app(phase='hermit',day=HERMIT_DAY)
        self.assertIn('CLUB ESCAPADE',self.view(app,65,25))
        app.key('\n')
        self.assertNotIn('Junpei',app.roster_choices)
        app.key('1');app.key('5');app.key('s')
        self.assertEqual((app.encounter,app.battle.allies[-1].name),('hermit','Koromaru'))
        self.assertNotIn('Yukari',[u.name for u in app.battle.allies])
        app.battle.outcome='win';app.key('\n')
        self.assertEqual((app.scene,app.record.day),('hermit-after',AFTER_HERMIT))
        app.key('t');app.key('s');app.key(' ')
        self.assertTrue(app.free_expedition)

    def test_upper_maps_boss_list_and_optional_passage(self):
        self.assertEqual([f.number for f in FLOORS if f.guardian],[99,105,112])
        self.assertEqual(len(PASSAGE_STAGES),3)
        for f in FLOORS:
            self.assertFalse(_blocks(f)&{f.start,f.stairs,*f.patrol})
            self.assertIn(f.encounter,ENCOUNTERS)
        app=self.app(phase='calendar',day=date(2009,8,9),yabba_upper=5)
        app.deploy();app.key(' ');app.key('\n');app.key(' ')
        self.assertEqual(app.active_monad,PASSAGE)
        app.key('g')
        for stage in PASSAGE_STAGES:
            app.key('\n')
            self.assertEqual(app.encounter,stage)
            app.battle.outcome='win';app.key('\n')
        self.assertEqual(app.record.monad,(PASSAGE,))
        self.assertEqual(app.temperance_bonus,2)
        self.assertIsNone(app.active_monad)

    def test_venom_fear_and_team_counters(self):
        squad=(LEAD_ID,'Yukari','Aigis','Koromaru')
        b=P3Battle('upper-yabba-magus',party=squad,seed=3)
        for _ in squad:b.act('guard')
        self.assertFalse(any(u.status=='poison' for u in b.allies))
        m=P3Battle('upper-yabba-maria',party=squad,seed=4)
        m.allies[0].hp-=30
        m.act('skill:Agi',m.enemies[0])
        for _ in squad[1:]:m.act('guard')
        self.assertIn('GHASTLY WAIL',m.threat)
        self.assertEqual(m.allies[0].status,'fear')
        m.act('guard')
        self.assertIsNone(m.act('skill:Patra',m.allies[0]))
        self.assertNotIn('GHASTLY WAIL',m.threat)
        n=P3Battle('upper-yabba-tower',party=squad,seed=2,charge={'Koromaru':100},theurgy=True)
        for _ in squad[:-1]:n.act('guard')
        self.assertEqual(n.actor.name,'Koromaru')
        self.assertIsNone(n.act('theurgy:hound',n.enemies[0]))
        self.assertEqual(n.reel[0],'Hound of Hades')
