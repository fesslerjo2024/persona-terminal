"""Discovery choices reveal context without changing combat or save rules."""
from datetime import date, timedelta
from pathlib import Path
import json
from tempfile import TemporaryDirectory
from unittest import TestCase

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona3 import persona3_discovery as discovery
from persona_terminal.persona3.persona3_discovery_schedule import CHECKPOINTS
from persona_terminal.persona3 import persona3_late as late
from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_state import P3Store
from .test_persona3_arqa_combat import Surface


class DiscoveryTests(TestCase):
    def setUp(self):
        folder=TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.save=Path(folder.name)/'p3.json'
        self.store=P3Store(self.save)
        self.store.new_game()

    def app(self,**state):
        if state:self.store.commit(**state)
        return P3App(None,self.store,seed=5)

    def draw(self,a,w=65,h=25):
        s=Surface(w,h)
        a.w,a.h,a.put=w,h,s.put
        a.draw()
        return ' '.join(s.text().split())

    def choose(self,a,keys):
        for key in keys:a.key(key)

    def test_all_discoveries_render_at_both_widths_and_every_choice_leads_out(self):
        a=self.app()
        before=self.save.read_bytes()
        keys=(*discovery.MODULE_FOR,'promise')
        self.assertEqual(len(keys),14)
        for key in keys:
            with self.subTest(key=key):
                a.discover(key)
                start,nodes=discovery.scene(key)
                leaves=set()
                def walk(node,ancestors):
                    self.assertNotIn(node,ancestors)
                    leaves.add(node)
                    a.discovery_step=node
                    title,_,body,choices=nodes[node]
                    for size in ((65,25),(120,40)):
                        layout=self.draw(a,*size)
                        for part in (title,*body,*(label for label,_ in choices)):
                            self.assertIn(part,layout)
                    for _,following in choices:
                        if following:walk(following,ancestors|{node})
                walk(start,set())
                self.assertEqual(leaves,set(nodes))
        self.assertEqual(self.save.read_bytes(),before)

    def test_new_game_contract_is_optional_and_ends_before_rooftop_awakening(self):
        a=self.app()
        raw=self.save.read_bytes()
        self.assertIn('LAST TRAIN TO IWATODAI',self.draw(a))
        self.assertIn('You’re Makoto, a new student',self.draw(a))
        self.choose(a,'11')
        self.assertIn('THE CONTRACT',self.draw(a))
        self.assertNotIn('Pharos',self.draw(a))
        self.assertEqual(self.save.read_bytes(),raw)
        self.choose(a,'11')
        self.assertEqual((a.page,a.record.phase),('story','awakening'))
        self.assertIn('THE ROOFTOP',self.draw(a))

    def test_rooftop_and_post_awakening_explain_actions_at_both_widths(self):
        a=self.app(day=date(2009,4,9),phase='awakening')
        for w,h in ((65,25),(100,35)):
            screen=self.draw(a,w,h)
            self.assertIn('Orpheus is your Persona.',screen)
            self.assertIn('Call on Orpheus',screen)
        a.key('1')
        self.assertEqual(a.encounter,'awakening')
        a.battle.outcome='win';a.key('\n')
        self.assertEqual(a.scene,'briefing')
        for w,h in ((65,25),(100,35)):
            screen=self.draw(a,w,h)
            self.assertIn('Most people turn into coffins',screen)
            self.assertIn('Ikutsuki, the adviser to S.E.E.S.',screen)
            self.assertIn('Go with S.E.E.S.',screen)
        a.key('\n')
        for w,h in ((65,25),(100,35)):
            screen=self.draw(a,w,h)
            self.assertIn('mapping the first floor',screen)
            self.assertIn('Enter Tartarus',screen)
        a.key('\n')
        self.assertEqual(a.page,'dark-hour')

    def test_chidori_setup_and_flower_skip_only_warn_when_an_errand_is_open(self):
        a=self.app(day=date(2009,9,5),phase='club-setup')
        a.key('2')
        self.assertIn('Junpei knows Chidori from their talks after school.',self.draw(a))
        a=self.app(day=date(2009,9,6),phase='calendar',aftermath='hermit-after')
        self.assertIn('into custody at the hospital',self.draw(a))
        a.key('\n')
        a=self.app(day=late.CHIDORI,phase='chidori')
        self.assertIn('S.E.E.S. took to the hospital after Escapade',self.draw(a))
        for flag in ('','spoken','bought','given'):
            a=self.app(day=date(2009,11,21),phase='calendar',junpei_flowers=flag)
            before=self.save.read_bytes()
            a.go('evening');a.key('4')
            self.assertEqual(a.overlay,'wait')
            self.assertEqual('miss your chance to bring Junpei the flowers' in self.draw(a),
                             flag in ('spoken','bought'))
            self.assertEqual(self.save.read_bytes(),before)

    def test_approach_scenes_checkpoint_then_unlock_existing_briefs(self):
        for key,phase,nextpage in (('bunker','bunker-setup','august'),('club','club-setup','hermit')):
            d,_,_=CHECKPOINTS[phase]
            a=self.app(phase='calendar',day=d-timedelta(days=1))
            a.next_night(skip=True)
            self.assertEqual((a.page,a.discovery_key,a.record.phase),('discovery',key,phase))
            a.key('1')
            a.key(ESC)
            self.assertTrue(a.exit)
            a=P3App(None,P3Store(self.save))
            self.assertEqual(a.discovery_step,discovery.scene(key)[0])
            for _ in range(6):
                if a.page!='discovery':break
                a.key('1')
            self.assertEqual((a.page,a.record.day),(nextpage,d))
            self.store.reload()

    def test_shinjiro_discovery_does_not_repeat_in_same_day(self):
        a=self.app(phase='calendar',day=late.SHINJIRO-timedelta(days=1))
        a.next_night(skip=True)
        self.assertEqual((a.discovery_key,a.record.day),('shinjiro',late.SHINJIRO))
        a.key('2')
        self.assertIn('Is he upstairs?',self.draw(a))
        self.choose(a,'11')
        self.assertEqual(a.page,'calendar')
        self.assertEqual(P3App(None,P3Store(self.save)).page,'calendar')

    def test_medea_never_checks_or_reveals_the_optional_flower_payoff(self):
        for flag in ('','given'):
            with self.subTest(flag=flag):
                a=self.app(phase='chidori',day=late.CHIDORI,xp=3000,junpei_flowers=flag)
                a.store.clear_operation('chidori')
                a.resume()
                self.assertEqual(a.discovery_key,'medea')
                raw=self.save.read_bytes()
                for _ in range(4):
                    text=self.draw(a).lower()
                    self.assertIn('11/22',text)
                    self.assertNotIn('flower',text)
                    a.key('1')
                text=self.draw(a)
                self.assertIn('11/23',text)
                self.assertIn('Trismegistus',text)
                self.assertEqual(self.save.read_bytes(),raw)
                a.key('1')
                self.assertEqual((a.page,a.record.day,a.record.xp,a.record.junpei_flowers),
                                 ('calendar',late.CHIDORI_AFTER,3490,flag))

    def test_bridge_reveals_identity_but_does_not_make_the_new_year_decision(self):
        a=self.app(phase='calendar',day=late.BRIDGE-timedelta(days=1))
        a.next_night(skip=True)
        raw=self.save.read_bytes()
        self.assertEqual(a.discovery_key,'bridge')
        self.choose(a,'11111')
        self.assertIn('The boy at your bedside called himself Pharos.',self.draw(a))
        a.key('1')
        self.assertIn('12/03',self.draw(a))
        self.assertIn('human life will end. That’s the Fall.',self.draw(a))
        a.key('1')
        self.assertIn('December 31',self.draw(a))
        self.assertNotIn('Kill Ryoji',self.draw(a))
        self.assertEqual(self.save.read_bytes(),raw)
        a.key('1')
        self.assertEqual((a.page,a.record.day,a.record.ending),('calendar',date(2009,12,3),''))
        a.next_night(skip=True)
        self.assertEqual(a.record.day,date(2009,12,10))

    def test_v9_normal_in_progress_operation_stays_readable_and_starts_at_brief(self):
        self.store.commit(phase='august',day=date(2009,8,6))
        blob=json.loads(self.save.read_bytes())
        blob['version']=9
        raw=json.dumps(blob).encode()
        self.save.write_bytes(raw)
        self.store.reload()
        self.assertEqual(self.app().page,'august')
        self.assertEqual(self.save.read_bytes(),raw)
