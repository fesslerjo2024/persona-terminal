"""Calendar branching, old end-saves, finale checkpoint routing, and epilogue UI."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_state import P3Store, LATE_FIELDS
from persona_terminal.persona3 import persona3_late as late
from .test_persona3_arqa_combat import Surface
from persona_terminal.persona3.persona3_combat import LEAD_ID


class LateRouteTests(unittest.TestCase):
    def setUp(self):
        folder=TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path=Path(folder.name)/'p3.json'
        self.store=P3Store(self.path)
        self.store.new_game()

    def app(self,**commit):
        self.store.commit(**commit)
        return P3App(None,self.store,seed=12)

    def draw(self,app,dimensions=(65,25)):
        w,h=dimensions
        s=Surface(w,h);app.w,app.h=w,h;app.put=s.put;app.draw()
        return s.text()

    def test_prior_endpoint_migrates_without_write_and_reaches_tziah(self):
        self.store.commit(day=late.when(9,6),phase='calendar',xp=5100,yabba_upper=6)
        data=json.loads(self.path.read_bytes())
        data['version']=6
        for f in (*LATE_FIELDS,'ending','junpei_flowers','theurgy_drill_seen'):data['state'].pop(f)
        raw=json.dumps(data).encode();self.path.write_bytes(raw)
        self.store.reload();app=P3App(None,self.store)
        self.assertEqual(self.path.read_bytes(),raw)
        self.assertEqual(app.record.yabba_upper,6)
        app.key('\n');app.key('4');app.key('4')
        self.assertIn('LOWER TZIAH',self.draw(app))
        app.key('\n')
        self.assertEqual(app.open_blocks[-1],'tziah')
        self.assertEqual(app.record.day,late.when(9,10))

    def test_hanged_man_gets_second_team_selection(self):
        app=self.app(day=late.NOV,phase='november')
        app.key('\n');app.key('s')
        self.assertEqual(app.encounter,'takaya-jin')
        app.battle.outcome='win';app.key('\n')
        self.assertIn('ENTER SQUAD',self.draw(app))
        app.key('\n');app.key('s')
        self.assertEqual(app.encounter,'hanged-man')
        app.battle.outcome='win';app.key('\n')
        self.assertEqual((app.page,app.discovery_key,app.record.day),('discovery','pharos-farewell',late.NOV_AFTER))

    def test_roster_gates_and_awakened_moves(self):
        app=self.app(day=late.OCT,phase='october',theurgy_intro_seen=True)
        app.key('\n')
        self.assertNotIn('Ken',app.roster_choices)
        self.assertNotIn('Shinjiro',app.roster_choices)
        app.key('s');app.battle.outcome='win';app.key('\n')
        while app.page=='late-aftermath':app.key('1')
        app.key('4');app.key('1')
        self.assertIn('Ken',app.roster_choices)
        self.assertNotIn('Shinjiro',app.roster_choices)
        app.key('s');app.key(' ');app.key('\n');app.key(' ')
        app.open_battle('tziah-patrol')
        self.assertIn('Ziodyne',next(u for u in app.battle.allies if u.name=='Akihiko').skills)

    def test_station_witness_and_both_quiet_responses(self):
        self.app(day=late.OCT,phase='october',xp=1300)
        self.store.clear_operation('fortune-strength')
        opening_bytes=self.path.read_bytes()
        for response,copy in (('1','Makoto waits with him'),('2','Makoto sits down beside him')):
            self.path.write_bytes(opening_bytes)
            a=P3App(None,P3Store(self.path))
            self.assertIn('10/04  SUN',self.draw(a))
            a.key(response)
            if response=='1':
                self.assertIn('THE RADIO',self.draw(a))
                a.key('1')
            self.assertIn('you lost control of your Persona. My mother died.', ' '.join(self.draw(a).split()))
            for _ in range(3):a.key('1')
            self.assertEqual(a.aftermath_step,'last_words')
            a.key(response)
            for dims in ((65,25),(120,40)):
                layout=self.draw(a,dims)
                self.assertIn('10/05  MON',layout)
                self.assertIn(copy,' '.join(layout.split()))
            self.assertEqual(self.path.read_bytes(),opening_bytes)
            a.key('1')
            self.assertEqual((a.page,a.record.day,a.record.xp),('calendar',late.OCT_AFTER,1950))
            self.assertEqual(P3App(None,P3Store(self.path)).page,'calendar')

    def test_betrayal_optional_clue_restarts_and_releases_into_calendar(self):
        a=self.app(day=late.NOV,phase='november',xp=2400)
        self.assertIn('all twelve must fall to end the Dark Hour', ' '.join(self.draw(a).split()))
        self.store.clear_operation('hanged-man')
        a.resume()
        before=self.path.read_bytes()
        for _ in range(3):a.key('1')
        self.assertIn('the dorm clock stops at midnight', ' '.join(self.draw(a).split()))
        self.assertNotIn('controller',self.draw(a))
        a.key('2')
        self.assertIn('THE MISSING FACES',self.draw(a))
        a.key('1')
        self.assertIn('A BELL IN THE DARK',self.draw(a))
        a.key('\x1b')
        self.assertTrue(a.exit)
        self.assertEqual(self.path.read_bytes(),before)
        a=P3App(None,P3Store(self.path))
        self.assertIn('AT THE BEDSIDE',self.draw(a))
        for _ in range(3):a.key('1')
        self.assertIn('THE CELEBRATION',self.draw(a))
        for step in ('bell','reveal','observatory','refuse','release','aftermath'):
            a.key('1')
            self.assertEqual(a.aftermath_step,step)
            self.draw(a,(65,25));self.draw(a,(96,34))
        a.key('1')
        self.assertEqual((a.page,a.record.day,a.record.xp),('calendar',late.NOV_AFTER,3250))
        self.assertEqual(P3App(None,P3Store(self.path)).page,'calendar')
        a.key('4');a.key('3')
        self.assertIn('THE RECOVERED FILE',self.draw(a))
        for _ in range(2):a.key('1')
        self.assertIn('ISIS',self.draw(a))

    def test_previous_v8_aftermath_dates_open_without_replay_or_write(self):
        for day in (late.OCT_AFTER,late.NOV_AFTER):
            self.store.reload()
            self.store.commit(day=day,phase='calendar')
            payload=json.loads(self.path.read_bytes())
            payload['version']=8
            before=json.dumps(payload).encode()
            self.path.write_bytes(before)
            a=P3App(None,P3Store(self.path))
            self.assertEqual((a.page,a.record.day),('calendar',day))
            self.assertEqual(self.path.read_bytes(),before)

    def test_bad_path_confirm_and_reopen(self):
        app=self.app(day=late.DECISION,phase='decision')
        raw=self.path.read_bytes()
        app.key('2');app.key('\x1b')
        self.assertEqual(self.path.read_bytes(),raw)
        app.key('2');app.key('\n')
        self.assertEqual((app.record.day,app.page,app.record.ending),(late.ENDING,'ending','bad'))
        self.assertEqual(P3App(None,P3Store(self.path)).page,'ending')
        self.assertIn('GRADUATION',self.draw(app))
        app.key('\n');app.key('\n');app.key('\n');app.key('\n')
        self.assertTrue(app.exit)

    def test_true_checkpoints_retry_and_rooftop_reopen(self):
        app=self.app(day=late.DECISION,phase='decision')
        app.key('1')
        self.assertEqual(app.record.day,late.JANUARY)
        app.key('\n');app.key('4');app.key('4');app.key('\n')
        self.assertEqual(app.discovery_key,'promise')
        app.key('1');app.key('1')
        app.key('\n');app.key('s')
        self.assertEqual(app.record.phase,'summit-adamah')
        for floor in ('257F','258F'):
            self.assertIn(floor,self.draw(app))
            app.key('\n')
        self.assertEqual(app.record.phase,'summit-jin')
        app.key('\n');app.battle.allies[0].hp=47
        app.battle.charge[LEAD_ID]=86
        app.battle.outcome='win';app.key('\n');app.key('\n')
        self.assertEqual(app.battle.resources[LEAD_ID][0],47)
        app.battle.outcome='loss';app.key('\n')
        self.assertEqual(app.record.phase,'summit-takaya')
        app=P3App(None,P3Store(self.path))
        app.key('\n')
        self.assertEqual(app.battle.resources[LEAD_ID][0],47)
        self.assertEqual(app.battle.charge[LEAD_ID],86)
        app=P3App(None,P3Store(self.path))
        app.key('r')
        app.key('\n')
        self.assertGreater(app.battle.resources[LEAD_ID][0],47)
        self.assertEqual(app.battle.charge[LEAD_ID],86)
        app.battle.outcome='win';app.key('\n')
        app=P3App(None,P3Store(self.path))
        app.key('\n')
        self.assertEqual(app.encounter,'nyx-avatar')
        app.battle.outcome='win';app.key('\n')
        self.assertEqual((app.page,app.record.phase,app.record.day),('great-seal','great-seal',late.FINALE))
        app=P3App(None,P3Store(self.path))
        self.assertEqual(app.page,'great-seal')
        self.assertIn('MAKOTO / THE GREAT SEAL',self.draw(app))
        raw=self.path.read_bytes()
        app.key('2');app.key('2')
        self.assertIn('Retry at the threshold',self.draw(app))
        self.assertEqual(self.path.read_bytes(),raw)
        app.key('1');app.key('1');app.key('1')
        self.assertIn('Great Seal',self.draw(app))
        self.assertEqual(self.path.read_bytes(),raw)
        app.key('1')
        self.assertEqual(app.record.day,late.RETURN)
        for day in (late.RETURN,late.REMEMBER):
            self.assertEqual(app.record.day,day)
            self.assertIn('MARCH',self.draw(app))
            app.key('\n')
        self.assertEqual((app.page,app.discovery_key,app.record.day),('discovery','roof',late.ENDING))
        for _ in range(6):app.key('1')
        self.assertEqual((app.page,app.record.ending),('ending','true'))
        app.key('\n')
        self.assertIn('ATLUS',self.draw(app,(120,40)))
