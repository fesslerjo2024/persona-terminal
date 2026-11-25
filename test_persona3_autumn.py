"""Authored Autumn blocks, formations and bounded tactical tells."""
from collections import deque
from datetime import date
from types import SimpleNamespace
from unittest import TestCase

import persona3_autumn as content
import persona3_autumn_combat as tactics
from persona3_thebel import DIRECTIONS, _blocks


class AutumnContentTests(TestCase):
    def test_dates_and_actual_gatekeeper_floors(self):
        self.assertEqual(content.OPENS,{'tziah':date(2009,9,10),
                                      'tziah_upper':date(2009,10,6),
                                      'harabah':date(2009,11,6)})
        self.assertEqual({k:(tuple(f.number for f in floors if f.guardian),end)
                          for k,(floors,end,_) in content.BLOCKS.items()},
                         {'tziah':((125,126,132,136,143),144),
                          'tziah_upper':((151,155,161,170,171),172),
                          'harabah':((179,184,188,193),198)})
        self.assertEqual(len(tactics.ENCOUNTERS['tziah-125'][1]),3)
        self.assertEqual(len(tactics.ENCOUNTERS['tziah-136'][1]),3)
        self.assertEqual(len(tactics.ENCOUNTERS['harabah-188'][1]),3)

    def test_floor_tactical_data_and_map_reachability(self):
        for group, (floors,end,xp) in content.BLOCKS.items():
            self.assertIn(group,tactics.REPLAY_ENCOUNTERS)
            self.assertEqual(len(floors),len(xp))
            for floor in floors:
                with self.subTest(floor=floor.number):
                    self.assertIn(floor.mask,tactics.PERSONAS)
                    self.assertTrue(all(k in tactics.FOES for k in tactics.ENCOUNTERS[floor.encounter][1]))
                    self.assertLess(floor.number,end)
                    walls=_blocks(floor)
                    self.assertFalse(set(floor.patrol)&walls)
                    seen={floor.start}
                    q=deque(seen)
                    while q:
                        x,y=q.popleft()
                        for dx,dy in DIRECTIONS.values():
                            p=(x+dx,y+dy)
                            if p not in walls and p not in seen:seen.add(p);q.append(p)
                    self.assertIn(floor.stairs,seen)

    def test_burst_threat_matches_actual_round_and_does_not_double_trigger_bonus(self):
        enemy=SimpleNamespace(alive=True,down=False,role='fall-necro-charge',label='Necromachinery')
        allies=[SimpleNamespace(alive=True)]
        log=[];damage=[]
        b=SimpleNamespace(round=1,enemies=[enemy],allies=allies,_say=log.append,
                          _hit=lambda _a,t,k,p,crit,**kw:damage.append((t,k,p,crit,kw)) or False)
        self.assertEqual(tactics.threat(b),'')
        self.assertIsNone(tactics.enemy_turn(b,enemy,False))
        self.assertFalse(log)
        b.round=2
        self.assertIn('MEGIDOLAON',tactics.threat(b))
        allies[0].hp=100;allies[0].max_hp=150;allies[0].label='Makoto'
        self.assertIs(tactics.enemy_turn(b,enemy,True),False)
        self.assertEqual(damage.pop()[1], 'Strike')
        self.assertIs(tactics.enemy_turn(b,enemy,False),False)
        self.assertEqual(damage[0][1::],('Almighty',62,False,{'ignore_affinity':True}))
        enemy.alive=False
        self.assertFalse(tactics.threat(b))

    def test_support_goes_away_if_no_ally_to_support(self):
        main=SimpleNamespace(alive=True,hp=70,max_hp=200,defense=0,label='Jotun')
        hand=SimpleNamespace(alive=True,down=False,role='fall-left',label='Hand')
        log=[]
        b=SimpleNamespace(round=2,enemies=[main,hand],allies=[SimpleNamespace(alive=True)],_say=log.append)
        main.down=False;main.role=''
        self.assertIs(tactics.enemy_turn(b,hand,False),False)
        self.assertEqual(main.hp,118)
        main.alive=False
        self.assertIsNone(tactics.enemy_turn(b,hand,False))
        self.assertEqual(main.hp,118)

    def test_judge_replaces_repeat_ice_with_a_told_verdict_and_pierce_follow_up(self):
        judge=SimpleNamespace(alive=True,down=False,label='Merciless Judge',role='fall-judge')
        victim=SimpleNamespace(alive=True,hp=110,max_hp=150,label='Makoto')
        actions=[]
        b=SimpleNamespace(round=2,enemies=[judge],allies=[victim],_say=lambda _s:None,
                          _hit=lambda a,t,k,p,*args: actions.append((k,p)) or True)
        self.assertIn('ICE VERDICT',tactics.threat(b))
        tactics.enemy_turn(b,judge,False)
        tactics.enemy_turn(b,judge,True)
        self.assertEqual(actions,[('Ice',42),('Pierce',33)])
