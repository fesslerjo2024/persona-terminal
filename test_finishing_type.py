from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import cinema
import cutins
from battle_ui import ESC
from campaign_state import Campaign
from finishing_type import MARKS
from test_animation_gallery import Surface


class FinishingTypeTests(unittest.TestCase):
    def test_wording_at_end_and_not_before_attack_or_on_nonlethal_hits(self):
        cards={actor:card[0] for actor,card in cutins.ALL_OUT.items()}
        cards['Oracle']=cutins.ORACLE[0]
        self.assertEqual(cards.keys(),MARKS.keys())
        for actor,title in cards.items():
            word,_,_,_,start=MARKS[actor]
            for w,h in ((64,25),(95,34),(119,40)):
                with self.subTest(actor=actor,w=w,h=h):
                    end=cutins.duration(title)-.08
                    for t,enabled,expected in ((start-.001,True,False),(end,True,True),(end,False,False)):
                        _,frame=cinema.paint(title,t,w,h,finishing=enabled)
                        lines=[''.join(text for text,_ in row) for row in frame]
                        self.assertEqual(list(map(len,lines)),[w]*h)
                        self.assertEqual(any(word in row for row in lines),expected)

    def test_gallery_text_never_leaks_into_showtimes_or_oracle_support(self):
        cards=(*cutins.SHOWTIMES.values(),cutins.ORACLE_SUPPORT,cutins.FINAL_GUARD)
        for title,_ in cards:
            for t in (.1,2.0,cutins.duration(title)-.1):
                self.assertEqual(cinema.paint(title,t,95,34),cinema.paint(title,t,95,34,finishing=False))

    def test_direct_outcome_is_not_changed_by_following_burn_or_skip(self):
        from battle_engine import Battle
        for direct in (True,False):
            with self.subTest(direct=direct), tempfile.TemporaryDirectory() as d:
                slot=Path(d)/'slot.json'
                app=Surface(Campaign(slot))
                app.battle_init()
                b=Battle(('Violet','Noir'),'Finisher fixture',seed=7,shuffle_turns=False,
                         encounter_config={'waves':[['Bicorn']], 'party_size':3})
                app._b_battle=b
                foe=b.enemies[0]
                b.allies[1].down=True
                foe.max_hp=200
                foe.hp=b.allout_damage+(0 if direct else 2)
                foe.status='burn'
                foe.status_turns=2
                foe.down=True
                b.one_more=True
                b.order=[b.allies[0],foe,*b.allies[1:]]
                b.cursor=0
                with patch('battle_ui.time.monotonic',return_value=1.0):
                    app._b_apply('allout')
                self.assertEqual(b.phase,'win')
                self.assertEqual(tuple(e[2] for e in b.damage_events),(0,) if direct else (2,0))
                self.assertIs(b.cut_in.finishing,direct)
                self.assertEqual(b.cut_in.cast,('Joker','Noir'))
                self.assertEqual(b.cut_in.targets,1)
                with patch('battle_ui.time.monotonic',return_value=3.0), patch.object(app,'draw_cutin',wraps=app.draw_cutin) as draw:
                    app.battle_page()
                draw.assert_called_once_with(cutins.ALL_OUT['Joker'][0],2.,finishing=direct,
                                             cast=('Joker','Noir'),targets=1)
                self.assertEqual(any(MARKS['Joker'][0] in row for row in app.out),direct)
                before=b.log[:]
                with patch('battle_ui.time.monotonic',return_value=3.01):
                    self.assertTrue(app.battle_key(ESC))
                self.assertIsNone(app._b_cut_in)
                self.assertEqual(b.log,before)
                self.assertFalse(slot.exists())

    def test_authored_charge_draws_live_cast_and_impact_outcome(self):
        title=cutins.ALL_OUT['Joker'][0]
        for w,h in ((64,25),(95,34)):
            with self.subTest(w=w,h=h):
                dry=cinema.paint(title,.22,w,h,cast=('Joker','Mona'),targets=1)
                royal=cinema.paint(title,.22,w,h,cast=('Joker','Noir','Violet'),targets=3)
                self.assertNotEqual(dry,royal)
                # The typography begins much later, so a change here
                # demonstrates real motion specific to the impact outcome.
                lethal=cinema.paint(title,.75,w,h,cast=('Joker','Noir'),targets=2,finishing=True)
                survives=cinema.paint(title,.75,w,h,cast=('Joker','Noir'),targets=2,finishing=False)
                self.assertNotEqual(lethal,survives)
