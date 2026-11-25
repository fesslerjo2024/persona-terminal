"""Native reel timing and render routing never depend on compact cels."""
import unittest
from unittest.mock import patch

from persona_terminal.persona5 import cinema
from persona_terminal.persona5 import cutins
from persona_terminal.persona5 import satanael_scene


class NativeRegistryTests(unittest.TestCase):
    def test_native_catalog_matches_emitted_cards_and_known_durations(self):
        titles = {card[0] for card in (*cutins.ALL_OUT.values(), *cutins.SHOWTIMES.values(),
                                     cutins.ORACLE, cutins.ORACLE_SUPPORT, cutins.FINAL_GUARD)}
        self.assertEqual(titles|{satanael_scene.TITLE}, cinema._native_catalog().keys())
        self.assertEqual(cutins.duration(satanael_scene.TITLE), satanael_scene.SECONDS)
        for title in titles:
            with self.subTest(title=title):
                self.assertTrue(cinema.has(title))
                self.assertEqual(cutins.duration(title), cinema.get(title)[0])

    def test_native_paths_ignore_legacy_and_do_not_guess_missing_time(self):
        with patch('persona_terminal.persona5.cinema._legacy_catalog',side_effect=AssertionError('legacy lookup')):
            title=cutins.SHOWTIMES[frozenset(('Fox','Skull'))][0]
            self.assertTrue(cinema.has(title))
            self.assertEqual(cutins.duration(title),7.92)
            beat,frame=cinema.paint(title,2,72,25)
            self.assertTrue(beat)
            self.assertEqual(len(frame),25)
            self.assertEqual({sum(len(run) for run,_ in row) for row in frame},{72})
            self.assertFalse(cinema.has('unknown clip'))
            self.assertEqual(cutins.duration('unknown clip'),0)


if __name__=='__main__':
    unittest.main()
