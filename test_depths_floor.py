from collections import deque
import curses as C
import unittest

from depths_floor import DepthsLightFloor, DIRECTIONS, EXIT, INITIAL_BLUE, SIZE, START


SOLUTION = (C.KEY_DOWN, C.KEY_DOWN, C.KEY_RIGHT, C.KEY_UP, C.KEY_RIGHT,
            C.KEY_UP, C.KEY_DOWN, C.KEY_DOWN)


class DepthsLightFloorTests(unittest.TestCase):
    def test_entry_wall_and_reset(self):
        floor = DepthsLightFloor()
        initial = set(INITIAL_BLUE) | {START}
        self.assertEqual(floor.blue, initial)
        self.assertEqual(floor.moves, 0)
        for direction in (C.KEY_UP, C.KEY_LEFT):
            self.assertIsNone(floor.key(direction))
            self.assertEqual(floor.blue, initial)
            self.assertEqual(floor.position, START)
            self.assertEqual(floor.moves, 0)
        floor.key(C.KEY_DOWN)
        self.assertEqual(floor.blue, initial | {(1, 0)})
        floor.key(C.KEY_UP)
        self.assertEqual(floor.blue, initial ^ {(1, 0), START})
        floor.key('X')
        self.assertEqual(floor.blue, initial)
        self.assertEqual(floor.position, START)
        self.assertEqual(floor.moves, 0)

    def test_early_exit_requires_light_and_early_submit_keeps_state(self):
        floor = DepthsLightFloor()
        for direction in SOLUTION[:3] + (C.KEY_RIGHT,):
            floor.key(direction)
        self.assertEqual(floor.position, EXIT)
        old = set(floor.blue)
        self.assertIsNone(floor.key('\n'))
        self.assertEqual(floor.blue, old)
        self.assertEqual(floor.moves, 4)
        self.assertIn('still yellow', floor.message)
        floor.blue = {(y, x) for y in range(SIZE) for x in range(SIZE)}
        floor.position = START
        self.assertFalse(floor.ready)
        self.assertIsNone(floor.key(13))
        self.assertIn('Submit from EXIT',floor.message)

    def test_revisit_flips_and_solve_requires_enter(self):
        floor = DepthsLightFloor()
        for move, key in enumerate(SOLUTION, start=1):
            self.assertIsNone(floor.key(key))
            if move in (5, 7):
                self.assertEqual((1,2) in floor.blue, move==7)
        self.assertTrue(floor.ready)
        self.assertEqual(floor.moves, 8)
        self.assertEqual(floor.key(C.KEY_ENTER),'solved')
        self.assertEqual(floor.key(C.KEY_LEFT),'solved')

    def test_back_and_bypass_are_distinct_and_restart_fresh(self):
        for key, expected in ((27,'back'), ('s','bypass')):
            floor = DepthsLightFloor()
            floor.key(C.KEY_RIGHT)
            self.assertEqual(floor.key(key),expected)
            self.assertEqual(floor.key('x'),expected)
            reopened = DepthsLightFloor()
            self.assertEqual(reopened.blue,set(INITIAL_BLUE)|{START})
            self.assertEqual(reopened.moves,0)

    def test_original_board_has_eight_move_minimum(self):
        floor = DepthsLightFloor()
        start = (floor.position, frozenset(floor.blue))
        seen = {start}
        queue = deque([(start, 0)])
        while queue:
            (position, blue), steps = queue.popleft()
            if position == EXIT and len(blue) == SIZE * SIZE:
                self.assertEqual(steps, len(SOLUTION))
                return
            for dy, dx in DIRECTIONS.values():
                tile = (position[0]+dy, position[1]+dx)
                state = (tile,blue ^ {tile})
                if state in seen or any(not 0<=n<SIZE for n in tile):
                    continue
                seen.add(state)
                queue.append((state,steps+1))
        self.fail('The original floor has no route to its exit.')


if __name__ == '__main__':
    unittest.main()
