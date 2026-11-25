"""Element colors are keyed from move data, not display names or highlights."""
import curses as C
import unittest

from persona3_combat import DIM, ELEMENT_MARKS, ESC, P3Battle, WHITE


class Surface:
    def __init__(self,w,h):
        self.w,self.h=w,h
        self.cells={}

    def put(self,y,x,text,ink,_,reverse):
        if not (0<=y<self.h and x+len(text)<self.w):
            raise AssertionError((y,x,text))
        for i,char in enumerate(text,x):
            self.cells[y,i]=(char,ink,reverse)

    def row(self,y):
        return ''.join(self.cells.get((y,x),(' ',None,None))[0] for x in range(self.w))

    def find(self,token):
        for y in range(self.h):
            x=self.row(y).find(token)
            if x>=0:return y,x
        raise AssertionError((token, '\n'.join(self.row(y) for y in range(self.h))))

    def ink(self,token):
        return self.cells[self.find(token)][1:]

    def element_row(self,token,element):
        y,x=self.find(token)
        symbol,ink=ELEMENT_MARKS[element]
        assert self.cells[y,x][1:]==(ink,False)
        assert any(v==(symbol,ink,False) for (row,_),v in self.cells.items() if row==y)


class ElementPresentation(unittest.TestCase):
    def frame(self,b,w,h):
        frame=Surface(w,h)
        b.draw(frame)
        return frame

    def test_damage_colors_are_distinct_and_cover_all_damage_moves(self):
        self.assertEqual(len(ELEMENT_MARKS),10)
        for slot in (0,1):
            self.assertEqual(len({i[slot] for i in ELEMENT_MARKS.values()}),10)
        b=P3Battle('arqa-ravens',theurgy=True,fuuka=True)
        self.assertEqual(b._attack_element('allout'),'Almighty')
        self.assertIsNone(b._attack_element('skill:Dia'))
        self.assertIsNone(b._attack_element('theurgy:cadenza'))
        self.assertEqual(b._attack_element('theurgy:cyclone'),'Wind')
        self.assertEqual(b._attack_element('theurgy:blizzard'),'Ice')

    def test_compact_and_wide_selection_keep_element_color_and_target_badge(self):
        for w,h in ((65,25),(120,40)):
            with self.subTest(width=w):
                b=P3Battle('arqa-ravens',seed=4,stock={'Orpheus':(), 'Apsaras':()})
                self.frame(b,w,h).element_row('Attack','Slash')
                b.key('1')
                b.seen[b.enemies[0].name]={'Fire':'drain'}
                frame=self.frame(b,w,h)
                frame.element_row('Agi','Fire')
                frame.element_row('Bash','Strike')
                self.assertEqual(frame.ink('[DRAIN]'),(WHITE,False))
                self.assertNotEqual(frame.ink('Tarunda')[0],ELEMENT_MARKS['Fire'][1])
                b.key('1')
                frame=self.frame(b,w,h)
                frame.element_row('FIRE','Fire')
                self.assertNotEqual(frame.ink('[DRAIN]')[0],ELEMENT_MARKS['Fire'][1])
                b.key(ESC);b.key(C.KEY_RIGHT)
                frame=self.frame(b,w,h)
                frame.element_row('Bufu','Ice')
                self.assertEqual(frame.ink('Dia')[0],WHITE)
                self.assertEqual(b.persona,'Orpheus')
                self.assertEqual(len(b.seen),1)

    def test_guide_teaches_palette_without_changing_other_keys(self):
        b=P3Battle('arqa-ravens')
        b.key('?')
        frame=self.frame(b,65,25)
        frame.find('ELEMENT COLORS')
        frame.find('AFFINITY KEY')
        frame.find('ESC BACK')
        for element,(symbol,ink) in ELEMENT_MARKS.items():
            frame.find(f'{symbol} {element}')
            self.assertEqual(frame.ink(f'{symbol} {element}'),(ink,False))
