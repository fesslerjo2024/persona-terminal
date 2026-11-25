"""Exercise the lean and optional Adamah branches through the actual app."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from persona_terminal.persona3 import persona3_late as late
from persona_terminal.persona3.persona3_app import P3App
from persona_terminal.persona3.persona3_nyx_combat import FORMS
from persona_terminal.persona3.persona3_state import P3Store
from persona_terminal.persona3.persona3_summit import ADAMAH_PHASE, APPROACH, SEAL_PHASE, SUMMIT_LEVEL
from .test_persona3_arqa_combat import Surface
from .test_persona3_nyx_combat import _choice


class SummitTests(unittest.TestCase):
    def _draw(self,app,w,h):
        surface=Surface(w,h)
        app.w,app.h=w,h
        app.put=surface.put
        app.draw()
        return surface.text()

    def test_no_grind_and_optional_supply_runs_through_seal(self):
        for seed,optional in ((13,False),(41,True)):
            with self.subTest(optional=optional),TemporaryDirectory() as folder:
                path=Path(folder)/'p3.json'
                store=P3Store(path)
                store.new_game()
                store.commit(phase='finale',day=late.FINALE)
                app=P3App(None,store,seed=seed)
                self.assertEqual(app.record.level,1)
                self.assertEqual(tuple(app.record.stock),('Orpheus',))
                app.key('\n')
                if optional:
                    for k in '2347':app.key(k)  # Swap in Mitsuru and Ken.
                app.key('s')
                self.assertEqual(app.record.phase,ADAMAH_PHASE)
                for w,h in ((65,25),(96,34)):
                    frame=self._draw(app,w,h)
                    self.assertIn('257F',frame)
                    self.assertIn('battle level 17',frame)
                app.key('1')
                self.assertIn('258F',self._draw(app,65,25))
                raw=path.read_bytes()
                if optional:
                    app.key('2')
                    self.assertEqual(app.encounter,APPROACH)
                    self._win(app)
                    self.assertIn('cache adds two Medicines',self._draw(app,65,25))
                    self.assertEqual(path.read_bytes(),raw)  # Optional supplies, not durable farming.
                app.key('1')
                self.assertEqual(app.record.phase,'summit-jin')
                self.assertEqual(app.record.level,1)
                for encounter in late.SUMMIT_IDS:
                    app.key('\n')
                    self.assertEqual(app.encounter,encounter)
                    self.assertEqual(app.battle.level,SUMMIT_LEVEL)
                    if encounter==late.SUMMIT_IDS[0]:
                        self.assertEqual(app.battle.inventory['Medicine'],8 if optional else 6)
                        self.assertEqual(app.battle.inventory['Soul Drop'],7 if optional else 5)
                    phases=self._win(app)
                    if encounter==late.SUMMIT_IDS[-1]:
                        self.assertEqual(phases,[f.name for f in FORMS])
                self.assertEqual((app.page,app.record.phase,app.record.ending),(SEAL_PHASE,SEAL_PHASE,''))
                self.assertEqual(app.record.xp,0)
                self.assertIsNone(app.battle)
                app=P3App(None,P3Store(path))
                for w,h in ((65,25),(96,34)):
                    frame=self._draw(app,w,h)
                    self.assertIn('MAKOTO / THE GREAT SEAL',frame)
                    normalized=' '.join(frame.split())
                    self.assertIn('Nyx’s Avatar, not Nyx.',normalized)
                    self.assertIn('Your bonds unlock the Universe',normalized)
                    self.assertIn('Guard',frame)
                    self.assertNotIn('Attack',frame)
                    self.assertNotIn('Yukari',frame)
                app.key('1');app.key('2' if optional else '1')
                self.assertEqual(app.solo_seal.hp,20 if optional else 47)
                self.assertEqual(app.record.phase,SEAL_PHASE)
                frame=' '.join(self._draw(app,65,25).split())
                self.assertIn('1 Great Seal',frame)
                self.assertIn('keep Nyx from reaching humanity',frame)
                app.key('1')
                self.assertEqual((app.record.day,app.record.ending,app.record.xp),(late.RETURN,'true',1800))

    def _win(self,app):
        b=app.battle
        b.low_motion=True
        phases=[]
        for _ in range(150):
            if b.outcome:break
            if hasattr(b.late_cycle,'form') and (not phases or phases[-1]!=b.late_cycle.form.name):
                phases.append(b.late_cycle.form.name)
            act,target,persona=_choice(b)
            self.assertIsNone(b.act(act,target,persona=persona),(act,b.threat,b.log[-4:]))
        self.assertEqual(b.outcome,'win',(b.encounter,b.log))
        if b.reel is not None:app.key(' ')
        app.key('\n')
        self.assertNotEqual(app.page,'battle')
        return phases
