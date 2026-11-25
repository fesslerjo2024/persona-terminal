"""Persona 3 Extras reuses live visuals and combat without opening a save."""
from collections import deque
import curses as C
import unittest
from unittest.mock import patch

from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona3.persona3_extras import GALLERY, PRACTICE, Persona3Extras, run_persona3_extra


class Screen:
    def __init__(self, keys, w, h):
        self.keys=deque(keys)
        self.w,self.h=w,h
        self.frames=[]
        self.delay=48

    def timeout(self, value):self.delay=value
    def getdelay(self):return self.delay
    def erase(self):self.parts=[]
    def getmaxyx(self):return self.h,self.w
    def get_wch(self):return self.keys.popleft()

    def addnstr(self,y,x,value,limit,style):
        assert 0<=y<self.h and 0<=x<x+limit<=self.w-1
        assert len(value)<=limit, (y,x,value,limit)
        self.parts.append((y,x,value))

    def refresh(self):self.frames.append(self.parts)


def lines(frame):
    return ' '.join(value for _,_,value in frame)


class Persona3ExtrasTests(unittest.TestCase):
    def scripted(self,kind,keys,size):
        screen=Screen(keys,*size)
        with patch('persona_terminal.shared.terminal_surface.C.color_pair',return_value=0), patch('persona_terminal.persona3.persona3_extras.monotonic',return_value=10):
            with patch('persona_terminal.persona3.persona3_state.P3Store.__init__',side_effect=AssertionError('attempted disk access')):
                run_persona3_extra(screen,kind,seed=4)
        self.assertEqual(screen.delay,48)
        self.assertFalse(screen.keys)
        return screen.frames

    def test_gallery_plays_without_chrome_and_esc_returns_to_same_row(self):
        for size in ((65,25),(96,35)):
            frames=self.scripted('gallery',(C.KEY_DOWN,'\n',ESC,ESC),size)
            self.assertIn('▶ Dark Hour',lines(frames[1]))
            self.assertNotIn('ANIMATION GALLERY',lines(frames[2]))
            self.assertTrue(frames[2])
            self.assertIn('▶ Dark Hour',lines(frames[3]))

    def test_practice_loadout_restarts_and_escape_is_one_level_at_a_time(self):
        for size in ((65,25),(96,35)):
            frames=self.scripted('practice',(C.KEY_DOWN,'\n','1',ESC,ESC,ESC,ESC,'\n',ESC),size)
            self.assertIn('▶ Thebel Patrol',lines(frames[1]))
            self.assertIn('THEBEL PATROL',lines(frames[2]))
            self.assertIn('ORPHEUS / SKILLS',lines(frames[3]).upper())
            self.assertIn('Leave this practice battle?',lines(frames[5]))
            self.assertIn('THEBEL PATROL',lines(frames[6]))
            self.assertIn('▶ Thebel Patrol',lines(frames[8]))
        meta=PRACTICE[-1]
        battle=meta.start(1)
        self.assertEqual(battle.encounter,'nyx-avatar')
        battle.allies[0].hp-=10
        self.assertGreater(meta.start(1).allies[0].hp,battle.allies[0].hp)

    def test_catalog_uses_valid_battles_and_unique_animation_labels(self):
        self.assertEqual(len(GALLERY),len({row[0] for row in GALLERY}))
        for _,seconds,render in GALLERY:
            self.assertTrue(render(seconds*.75,64,25))
        for entry in PRACTICE:
            self.assertEqual(entry.key,entry.start(1).encounter)

    def test_group_navigation_wraps_and_remembers_each_selection(self):
        for size in ((65,25),(96,35)):
            for kind,groups in (('gallery',('STORY & EXPLORATION','VELVET ROOM','THEURGY & ORACLE',
                                           'ALL-OUT ATTACKS')),
                                ('practice',('SPRING OPERATIONS','SUMMER OPERATIONS',
                                             'AUTUMN & WINTER','TARTARUS SUMMIT'))):
                keys=(C.KEY_DOWN,*(C.KEY_RIGHT,)*len(groups),C.KEY_LEFT,ESC)
                frames=self.scripted(kind,keys,size)
                for frame,name in zip(frames[1:],(*groups,groups[0],groups[-1])):
                    self.assertIn(f'‹ {name} ›',lines(frame))
                    self.assertIn('←→ GROUP',lines(frame))
                selected=lambda frame: next(value for _,_,value in frame if value.startswith('▶ '))
                self.assertEqual(selected(frames[1]), selected(frames[-2]))
