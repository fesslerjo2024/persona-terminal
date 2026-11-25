"""Compact, read-only Persona 3 Velvet Room render surfaces."""
from dataclasses import replace
import unittest

from battle_ui import CYAN, GOLD, WHITE
from persona3_velvet_ui import Row, View, draw
from reel_palette import IDS


class Surface:
    def __init__(self,w,h):
        self.w,self.h=w,h
        self.frames=[]
        self.calls=[]

    def frame(self,title,footer):
        self.frames.append((title,footer))

    def put(self,y,x,text,*style):
        assert 0<=y<self.h-4 and 0<=x<=x+len(text)<=self.w-2
        self.calls.append((x,y,text,style))

    @property
    def text(self):
        return '\n'.join(call[2] for call in self.calls)


class VelvetUITests(unittest.TestCase):
    def test_active_and_compendium_perform_no_storage_calls(self):
        # The surface deliberately has no store, record, or key dispatch.
        views=(
            View('stock',1,780,(Row('Orpheus','Equipped'),Row('Pixie','Unregistered')),
                 ('Stock 2/6','Skills: Zio, Dia','Defense: Electric resist'),
                 '↑↓ PICK  ENTER EQUIP  R REGISTER  F FUSE  ESC BACK'),
            View('compendium',0,780,(Row('Orpheus','In stock',False),Row('Angel','Resummon ¥160')),
                 ('Registered copy','In active stock'), '↑↓ PICK  ESC BACK'),
        )
        for w,h in ((65,25),(96,34)):
            for v in views:
                with self.subTest(size=(w,h),screen=v.screen):
                    app=Surface(w,h);draw(app,v)
                    self.assertEqual(app.frames,[('VELVET ROOM / '+('ACTIVE STOCK' if v.screen=='stock' else 'COMPENDIUM'),v.footer)])
                    self.assertEqual(app.text.count('¥780'),1)
                    self.assertIn(v.rows[v.index].label,app.text)
                    self.assertIn(v.rows[v.index].detail,app.text)
                    line=next(row for row in app.calls if '◆' in row[2])
                    self.assertEqual(line[3][-1],v.rows[v.index].enabled)

    def test_inheritance_window_follows_last_item_and_no_false_shortcut(self):
        rows=tuple(Row(f'Skill {i+1}',f'From parent {i+1}') for i in range(10))
        view=View('inherit',0,1000,rows,
                  ('Nekomata',('Choose one additional skill',GOLD)),'↑↓ PICK  ENTER REVIEW  ESC BACK')
        app=Surface(65,25);draw(app,view)
        self.assertIn('◆ 1 Skill 1',app.text)
        self.assertIn('1–6/10 ↓',app.text)
        self.assertNotIn('Skill 10',app.text)
        app=Surface(65,25);draw(app,replace(view,index=9))
        self.assertIn('↑ 5–10/10',app.text)
        selected=next(row[2] for row in app.calls if row[2].startswith('◆'))
        self.assertEqual(selected.strip(),'◆   Skill 10')
        self.assertIn('From parent 10',app.text)
        self.assertNotIn('Skill 1 ',app.text)
        app=Surface(96,34);draw(app,replace(view,index=9))
        self.assertIn('1 Skill 1',app.text)
        self.assertNotIn('–10/10',app.text)

    def test_fusion_consequences_and_resummon_cost_fit_at_minimum(self):
        templates={
            'confirm':('Nekomata', 'Inherit: Dia', ('Consumed: Orpheus and Pixie',GOLD),
                       'Registered snapshots remain in the Compendium.', 'Nekomata will be equipped.'),
            'resummon':('Angel', ('Fee: ¥160   •   Remaining: ¥620',GOLD),
                        'Skills: Kouha, Dia', 'Adds to stock without equipping.'),
        }
        for screen,detail in templates.items():
            with self.subTest(screen=screen):
                app=Surface(65,25)
                draw(app,View(screen,0,780,(),detail,'ENTER CONFIRM  ESC CANCEL'))
                self.assertEqual(len(app.frames),1)
                self.assertNotIn('│',app.text)
                for item in detail:
                    self.assertIn(item if isinstance(item,str) else item[0],app.text)


class VelvetReviewSurfaceTests(unittest.TestCase):
    def test_moving_review_does_not_cover_consequences_or_controls(self):
        for w,h in ((65,25),(96,34)):
            view=View('confirm',0,150,(),('Orpheus + Pixie → Nekomata',
                     ('Parents leave stock, but stay registered.',GOLD),
                     'Inherit: Bash','Skills: Agi, Bash, Maragi','Defense: Ice weak',
                     'Equip after fusion: Nekomata','No yen cost.'),
                     'ENTER FUSE  ESC CANCEL',0)
            columns=[]
            for t in (0,.25,.72):
                app=Surface(w,h)
                draw(app,replace(view,review_elapsed=t))
                cards={}
                for x,y,run,style in app.calls:
                    ink=style[0] if style else None
                    if y==5 and ink in (CYAN,IDS['rose']) and any(0x2801<=ord(ch)<=0x28ff for ch in run):
                        cards.setdefault(ink,x)
                columns.append(sorted(cards.values()))
                self.assertEqual(app.frames,[('VELVET ROOM / CONFIRM FUSION',view.footer)])
                for item in (view.detail[0],view.detail[1][0],view.detail[-1]):
                    self.assertIn(item,app.text)
            self.assertEqual([len(c) for c in columns],[2,2,2])
            self.assertLess(columns[0][0],columns[-1][0])
            self.assertGreater(columns[0][1],columns[-1][1])
