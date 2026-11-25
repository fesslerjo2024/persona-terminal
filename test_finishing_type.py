from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import cinema
import cutins
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

    def test_combat_checks_knockout_before_showing_finishing_text(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as d:
            app=Surface(Campaign(Path(d)/'slot.json'))
            app.battle_init()
            title=cutins.ALL_OUT['Joker'][0]
            app._b_start_cut(cutins.ALL_OUT['Joker'],1)
            for alive in (True,False):
                app._b_cut_damage=((),1,(SimpleNamespace(alive=alive),))
                with patch('battle_ui.time.monotonic',return_value=3),patch.object(app,'draw_cutin') as draw:
                    app.battle_page()
                draw.assert_called_once_with(title,2,finishing=not alive)
