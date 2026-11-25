import unittest

from cruiser_route import CruiserMouseRoute


class TestCruiserRoute(unittest.TestCase):
    def test_form_and_location_both_matter(self):
        r = CruiserMouseRoute()
        self.assertTrue(r.mouse)
        for key in "DET":
            self.assertIsNone(r.key(key))
            self.assertEqual(r.room, "hall")
            self.assertTrue(r.statue)
        self.assertIsNone(r.key("v"))
        self.assertEqual(r.room, "service")
        self.assertFalse(r.mouse)
        self.assertIsNone(r.key("E"))
        r.key("D")
        self.assertTrue(r.mouse)
        self.assertIsNone(r.key("E"))
        for key in "VTD":
            self.assertIsNone(r.key(key))
        self.assertEqual(r.room, "hall")
        self.assertFalse(r.mouse)
        self.assertIsNone(r.key("V"))
        self.assertEqual(r.room, "hall")
        self.assertEqual(r.key("E"), "solved")

    def test_reversible_and_optional(self):
        r = CruiserMouseRoute()
        for key in "VTT":
            r.key(key)
        self.assertTrue(r.statue)
        r.key("X")
        self.assertEqual(r.room, "hall")
        self.assertTrue(r.mouse)
        self.assertEqual(r.key(27), "back")
        self.assertEqual(CruiserMouseRoute().key("S"), "bypass")
