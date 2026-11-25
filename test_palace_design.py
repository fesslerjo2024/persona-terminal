"""The production concept adapter separates art, controls, and hidden data."""
from types import SimpleNamespace
from unittest import TestCase
from palace_design import Design,draw_design
from palace_menu import MapView,Operation


def view(selected):
    titles=('Castle Gate','A Very Long Tower and Treasure Route','UNREVEALED SCENE')
    return MapView(tuple(Operation(f'castle-{i}',t,'','locked' if i==2 else ('clear' if i==0 else 'open'),
                                   'B' if i==0 else '',selected==i)
                         for i,t in enumerate(titles)),selected,False,'')


class PalaceDesignTests(TestCase):
    def test_art_precedes_legible_active_operation_and_locked_focus_is_neutral(self):
        for w,h in ((65,25),(96,35),(119,40)):
            writes=[]
            app=SimpleNamespace(w=w,h=h,put=lambda *args:writes.append(args))
            for selected in (1,2):
                writes.clear()
                def layout(p):
                    p.art.line('amber',(0,10),(100,10))
                    for i in range(p.count):
                        p.mission(i,70,13,40,short='Stairs')
                    p.note('background note',70,13)
                p=draw_design(app,view(selected),'amber',layout)
                self.assertTrue(any('⠁'<=c<='⣿' for c in writes[0][2]))
                self.assertTrue(all(6<=y<=h-8 and 0<=x<x+len(s)<w for y,x,s,*_ in writes))
                self.assertNotIn('UNREVEALED SCENE',' '.join(s for _,_,s,*_ in writes))
                self.assertTrue(any('???' in q.text for q in p.labels()))
                reverse=[q for q in p.labels() if q.reverse]
                if selected==1:
                    self.assertEqual(len(reverse),1)
                    self.assertIn('A Very Long Tower and Treasure Route',reverse[0].text)
                else:
                    self.assertFalse(reverse)
                    self.assertTrue(any(q.bold and '???' in q.text for q in p.labels()))

    def test_adapter_does_not_silently_drop_missions(self):
        p=Design(SimpleNamespace(w=65,h=25),view(1),'amber')
        p.mission(0,0,3)
        with self.assertRaisesRegex(ValueError,'Duplicate operation'):
            p.mission(0,0,4)
        with self.assertRaisesRegex(ValueError,'every operation'):
            p.labels()
