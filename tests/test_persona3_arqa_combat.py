"""Lower Arqa, Fuuka reconnaissance, and character-specific Theurgy."""
from unittest import TestCase
from unittest.mock import patch

from persona_terminal.persona3 import persona3_arqa_combat as arqa
from persona_terminal.persona3.persona3_combat import DEFAULT_PARTY, LEAD_ID, P3Battle, party_caps, persona_skills

FOUR=(*DEFAULT_PARTY,'Akihiko')


class Surface:
    def __init__(self,w,h):
        self.w,self.h=w,h
        self.grid=[list(' '*w) for _ in range(h)]

    def put(self,y,x,text,*_):
        assert 0<=y<self.h and 0<=x and x+len(text)<self.w,(y,x,text)
        self.grid[y][x:x+len(text)]=text

    def text(self):
        return '\n'.join(''.join(row) for row in self.grid)


class LowerArqaCombat(TestCase):
    def test_default_and_rescue_rosters_and_true_arqa_formations(self):
        self.assertEqual(tuple(party_caps()),DEFAULT_PARTY)
        self.assertEqual(tuple(party_caps(4,FOUR)),FOUR)
        rescue=P3Battle('emperor-empress',seed=2)
        self.assertEqual(tuple(u.name for u in rescue.allies),(LEAD_ID,'Junpei','Akihiko'))
        self.assertTrue(rescue.fuuka)
        self.assertFalse(rescue.theurgy)
        self.assertIn('Skewer',persona_skills('Forneus'))
        self.assertIn('Kouha',persona_skills('Omoikane'))
        self.assertIn('Maragi',persona_skills('Inugami',6))
        self.assertEqual([u.label for u in P3Battle('arqa-magus').enemies],
                         ['Heretic Magus','Grievous Table A','Grievous Table B'])
        self.assertEqual([u.label for u in P3Battle('arqa-dice').enemies],
                         ['Disturbing Dice','Slaughter Twins A','Slaughter Twins B'])
        birds=P3Battle('arqa-ravens')
        self.assertEqual([u.affinity.get('Ice') for u in birds.enemies],['weak','resist','resist'])
        self.assertEqual(birds.seen,{})

    def test_relic_warns_before_each_element(self):
        b=P3Battle('arqa-relic',party=FOUR,level=4,seed=2)
        for element in arqa.RELIC_SEQUENCE:
            self.assertIn(f'{element} incoming',b.threat)
            for _ in b.allies:self.assertIsNone(b.act('guard'))
            self.assertIn(f'Clairvoyant Relic casts {element}.',b.log)

    def test_fuuka_scan_queued_and_old_boss_readings_removed_per_phase(self):
        b=P3Battle('emperor-empress',seed=6)
        empress,emperor=b.enemies
        opener=b.actor
        self.assertIsNone(b.act('full-analysis'))
        self.assertTrue(b.scan_pending)
        self.assertEqual((b.actor,b.seen,b.scan_left),(opener,{},2))
        self.assertIsNone(b.act('analyze',emperor))
        self.assertFalse(b.seen)
        self.assertIsNone(b.act('guard'))
        self.assertFalse(b.scan_pending)
        self.assertEqual(b.seen[empress.name]['Pierce'],'weak')
        self.assertEqual(b.seen[emperor.name]['Electric'],'weak')
        self.assertIn('already scanned',b.act('full-analysis'))
        empress.hp=100
        b.act('guard');b.act('guard')
        self.assertNotIn(empress.name,b.seen)
        self.assertEqual(b.seen[emperor.name]['Electric'],'weak')
        self.assertIn('PARADIGM SHIFT',b.threat)
        b.act('full-analysis');b.act('guard')
        self.assertEqual(b.seen[empress.name]['Pierce'],'null')
        self.assertEqual(b.seen[empress.name]['Strike'],'weak')
        b.act('guard');b.act('guard')
        self.assertNotIn(emperor.name,b.seen)
        self.assertEqual(b.seen[empress.name]['Strike'],'weak')
        b.act('full-analysis');b.act('guard')
        self.assertEqual(b.seen[emperor.name]['Electric'],'null')
        self.assertEqual(b.seen[emperor.name]['Fire'],'weak')
        self.assertEqual(b.scan_left,0)

    def test_theurgy_tutorial_keyboard_affinity_bypass_no_extra_cost_single_cast(self):
        for width,height in ((65,25),(120,40)):
            with self.subTest(width=width):
                b=P3Battle('theurgy-drill',party=FOUR,seed=3)
                self.assertEqual(b.actor.label,'Yukari')
                self.assertEqual(b.charge['Yukari'],100)
                screen=Surface(width,height);b.draw(screen)
                for label in ('9 Theurgy','8 Fuuka','TG 100%','Black Raven'):self.assertIn(label,screen.text())
                before=b.resources
                for k in '911':b.key(k)
                self.assertEqual(b.outcome,'win')
                self.assertEqual(b.resources,before)
                self.assertEqual(b.charge['Yukari'],0)
                self.assertEqual(b.seen,{})
                self.assertEqual(b.reel[0],'Cyclone Arrow')
                b.key('\n')
                self.assertIsNone(b.reel)
                self.assertFalse(b.key('\n'))
                self.assertEqual(sum('uses Cyclone Arrow' in row for row in b.log),1)

    def test_fusion_theurgy_uses_registry_not_active_stock_and_knows_ailment_block(self):
        locked=P3Battle('arqa-patrol')
        self.assertNotIn('Theurgy',[r[0] for r in locked._menu()])
        self.assertIn('not unlocked',locked.act('theurgy:cadenza'))
        b=P3Battle('arqa-relic',theurgy=True,stock={'Orpheus':()},
                   registered={'Orpheus','Apsaras'},charge={LEAD_ID:100},seed=2)
        self.assertNotIn('Apsaras',b.stock)
        b.actor.status='distress'
        self.assertIn('ailment',b.act('theurgy:cadenza'))
        self.assertEqual(b.charge[LEAD_ID],100)
        b.actor.status=''
        b.actor.hp=30
        self.assertIsNone(b.act('theurgy:cadenza'))
        self.assertEqual(b.allies[0].hp,95)
        self.assertEqual(b.charge[LEAD_ID],0)
        self.assertEqual(b.allies[0].agility,1)

    def test_character_charge_is_separate_and_roles_match(self):
        b=P3Battle('arqa-patrol',party=FOUR,theurgy=True,seed=6)
        lead,yukari,junpei,aki=b.allies
        lead.hp=75
        self.assertIsNone(b.act('skill:Agi',b.enemies[0]))
        self.assertEqual(b.charge[LEAD_ID],28)
        self.assertIs(b.actor,yukari)
        self.assertIsNone(b.act('skill:Dia',lead))
        self.assertEqual(b.charge['Yukari'],35)
        self.assertIs(b.actor,junpei)
        aki.attack=1
        with patch.object(b.rng,'random',return_value=0.):
            self.assertIsNone(b.act('attack',b.enemies[0]))
        self.assertEqual(b.charge['Junpei'],54)
        self.assertEqual(b.charge['Akihiko'],0)
        self.assertIsNone(b.act('guard'))
        self.assertEqual(b.charge['Akihiko'],16)
        self.assertEqual(b.charge['Yukari'],35)

    def test_fuuka_oracle_is_separate_and_not_unlocked_at_rescue(self):
        rescue=P3Battle('emperor-empress')
        rescue.key('8')
        self.assertNotIn('Oracle',[r[0] for r in rescue._menu()])
        b=P3Battle('arqa-patrol',party=FOUR,fuuka=True,theurgy=True,
                   charge={'Fuuka':54,'Yukari':19},seed=4)
        actor=b.actor
        b.act('full-analysis')
        self.assertEqual(b.charge['Fuuka'],54)
        b.act('guard')
        self.assertEqual(b.charge['Fuuka'],100)
        self.assertEqual(b.charge['Yukari'],19)
        actor=b.actor;actor.hp=13
        b.key('8')
        view=Surface(65,25);b.draw(view)
        self.assertIn('ORACLE 100%',view.text())
        b.key('2')
        self.assertIs(b.actor,actor)
        self.assertGreater(actor.hp,13)
        self.assertEqual(b.charge['Fuuka'],0)
        self.assertEqual(b.charge['Yukari'],19)
        self.assertIn('Oracle restores squad HP',b.log[-1])

    def test_first_key_at_cut_in_expiry_cannot_fall_through(self):
        b=P3Battle('theurgy-drill',party=FOUR)
        with patch('persona_terminal.persona3.persona3_combat.monotonic',return_value=100.):
            for k in '911':b.key(k)
        with patch('persona_terminal.persona3.persona3_combat.monotonic',return_value=b.reel[2]+.001):
            self.assertTrue(b.key('\n'))
            self.assertIsNone(b.reel)
            self.assertFalse(b.key('\n'))

    def test_mitsuru_uses_independent_ice_theurgy(self):
        b=P3Battle('arqa-patrol',party=(LEAD_ID,'Yukari','Akihiko','Mitsuru'),
                   fuuka=True,theurgy=True,charge={'Mitsuru':100},seed=4)
        b.actor=b.allies[-1]
        self.assertEqual(b._theurgy_ids(),['blizzard'])
        foe=b.enemies[1]
        self.assertEqual(foe.affinity['Ice'],'resist')
        self.assertIsNone(b.act('theurgy:blizzard',foe))
        self.assertEqual(foe.hp,0)
        self.assertEqual(b.charge['Mitsuru'],0)
        self.assertNotIn(foe.name,b.seen)
        self.assertEqual(b.reel[0],'Blizzard Edge')
