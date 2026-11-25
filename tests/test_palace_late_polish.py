"""Packed-dot focus cues on the late Palace maps."""
from types import SimpleNamespace
from unittest import TestCase

from persona_terminal.persona5.palace_design import Design
from persona_terminal.persona5.palace_late_themes import _bridge, _fracture, _prism
from persona_terminal.persona5.palace_menu import MapView, Operation
from persona_terminal.persona5.palace_middle_themes import _cruiser_broadside


def design(key,selected,width,height):
    ids={
        'cruiser':('cruiser-guests','cruiser-industry','cruiser-cleaner',
                   'cruiser-akechi','cruiser-sacrifice','cruiser-duel'),
        'depths':('depths-prison','depths-floor','depths-grail',
                  'depths-rebellion','depths-guardians','depths-yaldabaoth'),
        'laboratory':('laboratory-reality','laboratory-daat','laboratory-records',
                      'laboratory-counseling','laboratory-colors','laboratory-choice'),
    }[key]
    rows=tuple(Operation(id,id,'','open','',i==selected) for i,id in enumerate(ids))
    return Design(SimpleNamespace(w=width,h=height),MapView(rows,selected,False,''),'cyan')


def pigments(p,colors,bounds=(0,0,100,60)):
    lx,ly,rx,ry=bounds
    x,y=map(round,p.art.xy((lx,ly)))
    u,v=map(round,p.art.xy((rx,ry)))
    return {(col,row) for row in range(y,v+1) for col in range(x,u+1)
            if p.art.c.rows[row][col] in colors}


class LatePalacePolish(TestCase):
    def test_deck_glow_is_local_to_the_selected_deck(self):
        for w,h in ((65,25),(96,35)):
            selected=[]
            for focus in (None,0,2):
                p=design('cruiser',0,w,h)
                _cruiser_broadside(p,68,4,98,40,focus)
                selected.append(pigments(p,{'ochre','amber','gold','white'}))
            first, second=(dots-selected[0] for dots in selected[1:])
            self.assertGreater(len(first),12)
            self.assertGreater(len(second),12)
            self.assertFalse(first&second)

    def test_only_the_active_light_route_adds_a_white_beam(self):
        for w,h in ((65,25),(96,35)):
            count=[]
            for focus in (4,5):
                p=design('laboratory',focus,w,h)
                _prism(p,0,0,99,59)
                count.append(len(pigments(p,{'white'},(64,8,99,25))))
            self.assertGreater(count[0],count[1]+10)

    def test_depths_connects_the_gap_with_isolated_dots(self):
        p=design('depths',3,96,35)
        scene=design('depths',3,96,35)
        _bridge(p)
        _fracture(scene,2,2,98,58)
        guide=pigments(p,{'violet','slate'},(44,13,53,44))-pigments(scene,{'violet','slate'},(44,13,53,44))
        # The central region stays mostly empty, but the little guide spans
        # several rows. Converting it into a chunky bridge would fail.
        self.assertGreater(len(guide),4)
        self.assertLess(len(guide),15)
        self.assertGreater(len({y for _,y in guide}),4)
        debris=(45,31),(50,37),(55,45),(57,51)
        for x,y in debris:
            col,row=map(round,scene.art.xy((2+.96*x,2+56*y/60)))
            self.assertIn(scene.art.c.rows[row][col],{'plum','indigo'})
