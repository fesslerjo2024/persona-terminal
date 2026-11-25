"""Dated optional flags and byte-safe migration for the November errand."""
import json
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from persona_terminal.persona3 import persona3_junpei as content
from persona_terminal.persona3 import persona3_late as late
from persona_terminal.persona3.persona3_state import FieldRecord,P3SaveError,P3Store,V8_FIELDS,_encode,next_story_date


class JunpeiErrandTests(TestCase):
    def setUp(self):
        tmp=TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/'persona3.json'
        self.store=P3Store(self.path)
        self.store.new_game()

    def test_skip_anchors_invitation_but_not_shop_if_declined(self):
        self.store.commit(phase='calendar',day=date(2009,11,6))
        self.store.advance_night(skip=True)
        self.assertEqual(self.store.state.day,content.INVITATION)
        self.assertEqual(content.option(self.store.state)[0],'talk')
        self.store.advance_night(skip=True)
        self.assertEqual(self.store.state.day,late.RYOJI)
        self.assertIsNone(content.option(self.store.state))
        with self.assertRaises(P3SaveError):self.store.junpei('talk')

    def test_steps_consume_correct_slots_and_january_payoff_once(self):
        self.store.commit(phase='calendar',day=content.INVITATION,yen=260,xp=500)
        self.store.junpei('talk')
        self.assertEqual((self.store.state.activity,self.store.state.yen),('junpei',260))
        self.store.advance_night(skip=True)
        self.assertEqual(self.store.state.day,content.FIRST_SHOP_DAY)
        self.assertEqual(content.option(self.store.state)[0],'buy')
        self.store.junpei('buy')
        self.assertEqual((self.store.state.activity,self.store.state.yen),('flower-shop',10))
        self.assertEqual(content.option(self.store.state,evening=True)[0],'give')
        self.store=P3Store(self.path)
        self.store.junpei('give')
        self.assertIsNone(content.option(self.store.state,evening=True))
        self.store.commit(day=date(2010,1,20),activity='')
        self.store.advance_night(skip=True)
        self.assertTrue(content.payoff_due(self.store.state))
        now=P3Store(self.path)
        now.finish_junpei()
        self.assertEqual((now.state.day,now.state.junpei_flowers,now.state.activity,now.state.xp),
                         (content.PAYOFF_DAY,'seen','hospital',500))
        with self.assertRaises(P3SaveError):now.finish_junpei()
        self.assertFalse(content.payoff_due(P3Store(self.path).state))
        self.assertEqual(next_story_date(content.PAYOFF_DAY,flower='seen'),late.FINALE)

    def test_expired_and_broke_paths_are_nonmutating(self):
        self.store.commit(phase='calendar',day=content.FIRST_SHOP_DAY,yen=5,junpei_flowers='spoken')
        before=self.path.read_bytes()
        with self.assertRaisesRegex(P3SaveError,'need ¥245'):
            self.store.junpei('buy')
        self.assertEqual(self.path.read_bytes(),before)
        self.store.commit(day=content.LAST_GIFT_DAY+timedelta(days=1),phase='chidori',junpei_flowers='bought')
        before=self.path.read_bytes()
        with self.assertRaises(P3SaveError):self.store.junpei('give')
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual(next_story_date(date(2010,1,20),flower='bought'),late.FINALE)

    def test_v7_migration_is_lazy_and_flags_are_validated(self):
        state=FieldRecord(phase='calendar',day=content.PAYOFF_DAY,xp=3500,harabah=2)
        data=json.loads(_encode(state))
        data['version']=7
        for field in V8_FIELDS:data['state'].pop(field)
        original=json.dumps(data).encode()
        self.path.write_bytes(original)
        self.store.reload()
        self.assertEqual((self.store.state.junpei_flowers,self.store.state.theurgy_drill_seen,
                          self.store.state.xp,self.store.state.harabah),('',False,3500,2))
        self.assertEqual(self.path.read_bytes(),original)
        self.assertFalse(content.payoff_due(self.store.state))
        with self.assertRaises(P3SaveError):self.store.commit(theurgy_drill_seen=1)
        with self.assertRaises(P3SaveError):self.store.commit(junpei_flowers='forged')
        self.assertEqual(self.path.read_bytes(),original)
        self.store.commit(theurgy_drill_seen=True)
        self.assertEqual(json.loads(self.path.read_bytes())['version'],11)
        self.assertTrue(P3Store(self.path).state.theurgy_drill_seen)
