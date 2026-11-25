"""Do not enter a newer controller with an outdated process' save object."""
from dataclasses import fields,make_dataclass
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from persona3_app import P3App
from persona3_state import FieldRecord,P3Store,_encode


class Persona3LaunchBoundaryTests(TestCase):
    def test_suite_disallows_late_controller_import_from_its_selector(self):
        subprocess.run([sys.executable,'-B','-c',
                        'import sys,suite_menu; assert suite_menu.P3App is sys.modules["persona3_app"].P3App; '
                        'assert "persona3_state" in sys.modules'],
                       cwd=Path(__file__).resolve().parent,check=True)

    def test_old_cached_record_shows_restart_instead_of_deploy_crash(self):
        old=make_dataclass('FieldRecord',[(f.name,f.type,f) for f in fields(FieldRecord)
                                         if f.name not in ('upper','rescues')])
        previous=old(phase='calendar',day=date(2009,4,21),depth=1)
        with patch('persona3_app.state_runtime.VERSION',3):
            app=P3App(None,SimpleNamespace(state=previous))
        self.assertEqual(app.page,'restart-needed')
        app.w,app.h=65,25
        words=[]
        app.put=lambda y,x,label,*args:words.append(label)
        app.draw()
        self.assertIn('PERSONA 3 / RESTART NEEDED',words)
        app.key('4');app.key('1') # Original crash input, now inert.
        self.assertIsNone(app.exit)
        app.key('\n')
        self.assertTrue(app.exit)
        self.assertEqual(previous.depth,1)

    def test_fresh_launch_of_legacy_april_save_still_deploys_without_rewrite(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'p3.json'
            day=date(2009,4,21)
            blob=json.loads(_encode(FieldRecord(phase='calendar',day=day,depth=1,xp=100)))
            blob['version']=3
            for field in ('upper','rescues','yabba','monad','fragments','yabba_upper','tziah','tziah_upper','harabah','harabah_upper','adamah','ending','junpei_flowers','theurgy_drill_seen'):blob['state'].pop(field)
            before=json.dumps(blob,separators=(',',':')).encode()
            path.write_bytes(before)
            app=P3App(None,P3Store(path),seed=17)
            app.key('4');app.key('1');app.key(' ')
            self.assertEqual((app.page,app.record.day,app.record.depth,app.record.upper),('entrance',day,1,0))
            self.assertEqual(path.read_bytes(),before)
