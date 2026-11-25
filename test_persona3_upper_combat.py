"""Upper Arqa roles, defensive cues and hotel carry-through regressions."""
import unittest
from unittest.mock import patch

from persona3_combat import DEFAULT_PARTY, LEAD_ID, P3Battle
from persona3_upper_combat import PERSONAS
from test_persona3_arqa_combat import Surface

PARTY=(*DEFAULT_PARTY,'Akihiko')


def cycle(b,last='guard'):
    for i,_ in enumerate(b.allies):
        action=last if i==len(b.allies)-1 else 'guard'
        target=b.enemies[0] if action=='attack' else None
        assert b.act(action,target) is None,(action,b.actor,b.log[-4:])


class UpperCombat(unittest.TestCase):
    def test_accurate_floor_formations_and_stock(self):
        patrol=P3Battle('upper-patrol',party=PARTY)
        self.assertEqual([u.name for u in patrol.enemies],['Bronze Dice','Vicious Raven'])
        t=P3Battle('upper-servant',party=PARTY,persona='Inugami')
        self.assertEqual([u.name for u in t.enemies],['Servant Tower','Enslaved Cupid A','Enslaved Cupid B'])
        self.assertEqual(t.enemies[0].affinity['Dark'],'weak')
        self.assertEqual(t.enemies[0].affinity['Electric'],'repel')
        self.assertTrue(all(u.affinity['Electric']=='weak' for u in t.enemies[1:]))
        self.assertEqual(t.seen,{})
        self.assertIsNone(t.act('skill:Eiha',t.enemies[0]))
        self.assertTrue(t.one_more)
        self.assertEqual(t.seen,{'Servant Tower':{'Dark':'weak'}})
        for name in PERSONAS:
            b=P3Battle('upper-patrol',persona=name)
            self.assertGreaterEqual(len(b.actor.skills),3)

    def test_lady_affinities_and_gigas_friendly_fire(self):
        b=P3Battle('upper-lady',party=PARTY,persona='Sati',seed=3)
        lady,first,second=b.enemies
        self.assertEqual([u.name for u in b.enemies],['Lascivious Lady','Profligate Gigas A','Profligate Gigas B'])
        self.assertEqual(lady.affinity['Fire'],'null')
        self.assertEqual(lady.affinity['Strike'],'vulnerable')
        self.assertEqual(first.affinity['Wind'],'weak')
        with patch.object(b.rng,'random',return_value=0.):
            self.assertIsNone(b.act('skill:Marin Karin',first))
        self.assertEqual(first.status,'charm')
        for _ in range(3):self.assertIsNone(b.act('guard'))
        self.assertTrue(any('Profligate Gigas A turns on' in x for x in b.log))
        self.assertLess(second.hp,second.max_hp)

    def test_cavalry_visible_gale_and_ordinary_wind_drains(self):
        b=P3Battle('upper-cavalry',party=PARTY,persona='Angel',seed=7)
        foe=b.enemies[0]
        foe.hp-=37
        self.assertIn('GALE CHARGE',b.threat)
        self.assertIsNone(b.act('skill:Garu',foe))
        self.assertGreater(foe.hp,foe.max_hp-37)
        for _ in range(3):self.assertIsNone(b.act('guard'))
        self.assertIn('Fleetfooted Cavalry releases the charged Gale Slash.',b.log)
        self.assertNotIn('GALE CHARGE',b.threat)

    def test_hierophant_guard_prevents_doomsday_fear(self):
        for guarded in (True,False):
            b=P3Battle('hotel-hierophant',party=PARTY,seed=5)
            cycle(b)
            self.assertIn('DOOMSDAY DOCTRINE',b.threat)
            cycle(b,last='guard' if guarded else 'attack')
            self.assertEqual(b.allies[-1].status,'' if guarded else 'fear')
            self.assertTrue(all(not u.status for u in b.allies[:-1]))
            self.assertIn('Hierophant pronounces Doomsday Doctrine.',b.log)

    def test_hotel_reuses_party_resources_inventory_charge_and_registry(self):
        a=P3Battle('hotel-hierophant',party=PARTY,fuuka=True,theurgy=True,
                   charge={LEAD_ID:61,'Fuuka':42},registered={'Orpheus','Apsaras'},level=7)
        a.allies[1].hp=64;a.allies[1].sp=17
        a.inventory['Medicine']=1;a.inventory['Dis-Charm']=1
        b=P3Battle('hotel-lovers',party=PARTY,fuuka=True,theurgy=True,
                   charge=a.charge,registered=a.registered,resources=a.resources,
                   inventory=a.inventory,level=7)
        self.assertEqual(b.resources,a.resources)
        self.assertEqual(b.inventory,a.inventory)
        self.assertEqual(b.charge,a.charge)
        self.assertEqual(b.registered,a.registered)
        self.assertEqual([u.name for u in b.allies],[u.name for u in a.allies])
        b.inventory['Dis-Charm']=0
        self.assertEqual(a.inventory['Dis-Charm'],1)
        with self.assertRaisesRegex(ValueError,'Yukari'):
            P3Battle('hotel-lovers',party=(LEAD_ID,'Junpei','Akihiko'))

    def test_lovers_cure_or_heartbreaker_exactly_once(self):
        for cure in (False,True):
            b=P3Battle('hotel-lovers',party=PARTY,fuuka=True,theurgy=True,
                       inventory={'Medicine':2,'Dis-Charm':1},seed=8)
            self.assertIn('Akihiko should Guard',b.threat)
            cycle(b,last='attack')
            target=b.allies[-1]
            self.assertEqual(target.status,'charm')
            self.assertIn('HEARTBREAKER',b.threat)
            before=target.hp
            for w,h in ((65,25),(120,40)):
                view=Surface(w,h);b.draw(view)
                self.assertIn('CHARM SP',view.text())
                self.assertNotIn('AkihikoCHARM',view.text())
                self.assertIn('HEARTBREAKER',view.text())
            if cure:
                self.assertTrue(b.act('item:Dis-Charm',b.actor))
                self.assertEqual(b.inventory['Dis-Charm'],1)
                self.assertIsNone(b.act('item:Dis-Charm',target))
                self.assertEqual(b.inventory['Dis-Charm'],0)
                for _ in range(3):b.act('guard')
                self.assertFalse(any('targets charmed allies' in x for x in b.log))
                self.assertEqual(target.hp,before)
            else:
                for _ in range(3):b.act('guard')
                self.assertIn('has Charm',b.act('attack',b.enemies[0]))
                self.assertIsNone(b.act('guard'))
                self.assertEqual(sum('targets charmed allies' in x for x in b.log),1)
                self.assertEqual(target.status,'')
                self.assertLess(target.hp,before)

    def test_representative_patrol_pairs_use_distinct_counterplay(self):
        routes={
            'upper-patrol':(['Bronze Dice','Vicious Raven'],('Electric','Ice')),
            'upper-patrol-50':(['Maniacal Book','Steel Gigas'],('Fire','Electric')),
            'upper-patrol-56':(['Jealous Cupid','Dark Eagle'],('Ice','Wind')),
        }
        for encounter,(names,weaknesses) in routes.items():
            with self.subTest(encounter=encounter):
                b=P3Battle(encounter,party=PARTY,seed=5)
                self.assertEqual([u.name for u in b.enemies],names)
                self.assertEqual([u.affinity.get(e) for u,e in zip(b.enemies,weaknesses)],['weak','weak'])
                self.assertFalse(b.seen)

    def test_hierophant_marks_exact_slots_and_leaves_others_free(self):
        b=P3Battle('hotel-hierophant',party=PARTY,seed=5)
        cycle(b)  # Makouga; next is a two-target Doctrine.
        self.assertIn('Guard: Makoto, Akihiko.',b.threat)
        # Only Makoto of the two marks guards. The other two unmarked
        # allies can attack freely and don't need to spend Guard charges.
        self.assertIsNone(b.act('guard'))
        for _ in range(3):self.assertIsNone(b.act('attack',b.enemies[0]))
        self.assertEqual([u.label for u in b.allies if u.status=='fear'],['Akihiko'])
        for _ in range(3):
            self.assertFalse('DOOMSDAY' in b.threat)
            cycle(b)
        self.assertIn('Guard: Yukari.',b.threat)
        cycle(b)
        self.assertFalse(any(u.status for u in b.allies))
        self.assertEqual(sum('uses Assault Dive' in row for row in b.log),2)

    def test_knocked_out_mark_does_not_silently_retarget(self):
        b=P3Battle('hotel-hierophant',party=PARTY,seed=5)
        cycle(b)
        b.allies[-1].hp=0
        self.assertIn('Guard: Makoto.',b.threat)
        for _ in range(3):self.assertIsNone(b.act('attack',b.enemies[0]))
        self.assertEqual([u.label for u in b.allies if u.status=='fear'],['Makoto'])
