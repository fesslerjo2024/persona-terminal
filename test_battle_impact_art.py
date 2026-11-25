from unittest import TestCase
from unittest.mock import patch

from battle_impact_art import draw_impact
import cinema
from cutins import ALL_OUT
from test_battle_information import Recorder


class BattleImpactArtTests(TestCase):
    def test_generic_impact_moves_and_keeps_exact_dimensions(self):
        for w,h in ((64,25),(95,34)):
            frames=[draw_impact(t,w,h) for t in (.0,.25,.69)]
            self.assertEqual(len(set(frames)),3)
            for frame in frames:
                self.assertEqual(len(frame),h)
                self.assertTrue(all(sum(len(run) for run,_ in row)==w for row in frame))
                self.assertTrue(all(ch==' ' or '⠁'<=ch<='⣿' for row in frame for run,_ in row for ch in run))

    def test_existing_cues_still_use_their_authored_renderer(self):
        ui=Recorder(65,25)
        with patch.object(ui,'draw_scene_rows') as rows:
            ui.draw_cutin('unknown placeholder',.25)
            rows.assert_called_once_with(draw_impact(.25,64,25))
            rows.reset_mock()
            title=ALL_OUT['Joker'][0]
            ui.draw_cutin(title,.75)
            rows.assert_called_once_with(cinema.paint(title,.75,64,25)[1])
