"""Source-bound late Tartarus topology and real compact combat checks."""
from collections import deque
from datetime import date
from types import SimpleNamespace
from unittest import TestCase

import persona3_combat as combat
import persona3_winter as field
import persona3_winter_combat as data
from persona3_thebel import DIRECTIONS, Hall


class WinterTartarusTests(TestCase):
    def test_story_gates_use_actual_floors_and_connected_halls(self):
        self.assertEqual(field.OPENS,{'harabah_upper':date(2009,12,10),'adamah':date(2010,1,1)})
        self.assertEqual(field.BORDERS,{'harabah_upper':226,'adamah':256})
        bosses={'harabah_upper':(203,212,218,225),'adamah':(230,236,241,246,247,253,254,255)}
        for key,(floors,border,xp) in field.BLOCKS.items():
            self.assertEqual(tuple(x.number for x in floors if x.guardian),bosses[key])
            self.assertEqual(len(floors),len(xp))
            self.assertEqual(len({x.number for x in floors}),len(floors))
            self.assertTrue(floors[-1].number<border)
            for i,f in enumerate(floors):
                with self.subTest(floor=f.number):
                    hall=Hall(i,floors=floors,block=key)
                    reached={hall.pos}
                    queue=deque(reached)
                    while queue:
                        x,y=queue.popleft()
                        for dx,dy in DIRECTIONS.values():
                            point=x+dx,y+dy
                            if point not in hall.blocked and point not in reached:
                                reached.add(point)
                                queue.append(point)
                    self.assertIn(f.stairs,reached)
                    self.assertTrue(set(f.patrol)<=reached)
                    self.assertIn(f.mask,combat.PERSONAS)
                    self.assertEqual(hall.encounter,f.encounter)
                    # Narrow UI has room for three foes and usable actions.
                    self.assertLessEqual(len(combat.ENCOUNTERS[f.encounter][1]),3)
        block,no,stages,reward=field.PASSAGES[field.HARABAH_PASSAGE]
        self.assertEqual((block,no),('harabah_upper',225))
        self.assertTrue(all(name in combat.ENCOUNTERS for name in stages))
        self.assertTrue(all(n>0 for n in reward))

    def test_new_masks_have_known_skill_and_distinct_era_paths(self):
        self.assertEqual(set(data.PERSONAS),{name for name,_ in data.FUSIONS})
        self.assertEqual(set(data.SUMMON_PRICE),set(data.PERSONAS))
        for name,parents in data.FUSIONS:
            self.assertNotIn(name,parents)
            self.assertTrue(all(parent in combat.PERSONAS for parent in parents))
            self.assertEqual(combat.persona_skills(name),data.PERSONAS[name][0])
            self.assertIn(data.FUSION_DATES[name],field.OPENS.values())
        self.assertEqual(set(data.FUSION_DATES.values()),set(field.OPENS.values()))

    def test_guarded_telegraphed_almighty_works_in_real_battle(self):
        battle=combat.P3Battle('winter-cultist',level=24,seed=5,persona='Seiryu',
                               party=(combat.LEAD_ID,'Yukari','Akihiko','Mitsuru'))
        for w,h in ((65,25),(96,34)):
            rows=[]
            app=SimpleNamespace(w=w,h=h,put=lambda y,x,msg,*_:rows.append((y,x,msg)))
            battle.draw(app)
            self.assertIn((4,3,'MEGIDOLAON / Guard against Almighty.'),rows)
            self.assertTrue(all(0<=y<h and 0<=x<x+len(msg)<w for y,x,msg in rows if msg))
        self.assertIsNone(battle.act('guard'))
        for _ in range(3):
            self.assertIsNone(battle.act('attack',battle.enemies[0]))
        self.assertEqual(battle.round,2)
        hit=next(line for line in battle.log if line.startswith('Makoto takes'))
        guarded=int(hit.split()[2])
        self.assertIn('[GUARD]',hit)
        self.assertLess(guarded,25)
        self.assertGreater(battle.allies[1].max_hp-battle.allies[1].hp,39)
        self.assertNotIn('MEGIDOLAON',battle.threat)

    def test_castle_reserves_do_not_extend_formation_or_repeat(self):
        battle=combat.P3Battle('winter-comeback',level=24,seed=17,persona='Suzaku')
        castle,foot,mage=battle.enemies
        self.assertIn('REINFORCEMENTS',battle.threat)
        foot.hp=mage.hp=0 # Simulate killing the two opening soldiers.
        for _ in range(3):
            self.assertIsNone(battle.act('guard'))
        self.assertEqual((foot.hp,mage.hp),(foot.max_hp//2,mage.max_hp//2))
        self.assertEqual(battle.enemies,[castle,foot,mage])
        self.assertNotIn('REINFORCEMENTS',battle.threat)
        foot.hp=mage.hp=0
        for _ in range(3):
            self.assertIsNone(battle.act('guard'))
        self.assertEqual((foot.hp,mage.hp),(0,0))
        self.assertEqual(sum('calls in reserve' in line for line in battle.log),1)
