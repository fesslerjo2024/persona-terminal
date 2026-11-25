"""Deterministic checks for the standalone Persona 3 combat slice."""
import curses as C
import unittest

from persona3_combat import ESC, P3Battle, hp_meter


class Surface:
    h,w=25,65

    def __init__(self):
        self.drawn={}

    def put(self,y,x,text,*_):
        assert 0<=y<self.h and 0<=x<self.w and x+len(text)<self.w
        self.drawn.setdefault(y,[]).append(text)

    def __str__(self):
        return '\n'.join(''.join(self.drawn[y]) for y in sorted(self.drawn))


class Persona3CombatTests(unittest.TestCase):
    def test_makoto_is_used_in_status_targets_logs_guide_and_defeat(self):
        b=P3Battle('thebel-patrol',seed=2)
        self.assertIn('Protagonist',b.resources)
        self.assertNotIn('Makoto',b.resources)
        for key,phrase in (('i','Makoto / Orpheus'),('?','keep Makoto standing')):
            b.key(key)
            app=Surface();b.draw(app)
            self.assertIn(phrase,str(app))
            self.assertNotIn('protagonist',str(app).casefold())
            b.key(ESC)
        b.allies[0].hp=40
        b.key('4');b.key('1')
        app=Surface();b.draw(app)
        self.assertIn('Makoto',str(app))
        self.assertNotIn('protagonist',str(app).casefold())
        b.key('1')
        self.assertTrue(any('Makoto recovers' in line for line in b.log))
        b._finish('loss')
        app=Surface();b.draw(app)
        self.assertIn('Makoto falls.',str(app))
        self.assertFalse(any('protagonist' in line.casefold() for line in b.log))

    def test_hp_meter_preserves_full_empty_and_low_at_compact_width(self):
        self.assertEqual(hp_meter(0,382,4),('','░░░░'))
        self.assertEqual(hp_meter(1,382,4),('█','░░░'))
        self.assertEqual(hp_meter(191,382,4),('██','░░'))
        self.assertEqual(hp_meter(381,382,4),('███','░'))
        self.assertEqual(hp_meter(382,382,4),('████',''))

    def test_hp_sp_rows_show_every_unit_and_keep_long_names_and_ko(self):
        for w,h,spacing,ally_width,enemy_width in ((65,25,2,6,17),(96,34,4,18,32)):
            with self.subTest(width=w):
                b=P3Battle('dancing-hand',seed=6)
                b.allies[0].hp=b.allies[0].max_hp//2
                b.allies[0].sp=0
                b.allies[1].hp=0
                b.enemies[0].hp=108
                b.enemies[0].down=True
                b.enemies[1].hp=1
                b.enemies[2].hp=0
                frame=Surface();frame.w,frame.h=w,h
                before=b.resources
                b.draw(frame)
                self.assertEqual(b.resources,before)
                team=[''.join(frame.drawn[8+i*spacing]) for i in range(3)]
                meters=[''.join(frame.drawn[9+i*spacing]) for i in range(3)]
                self.assertIn('MakotoHP 65',team[0])
                self.assertIn('Barbaric Beast Wheel ↓',team[0])
                self.assertIn('SP 0',meters[0])
                self.assertIn('▂'*ally_width,meters[0])
                self.assertIn('YukariHP 0',team[1])
                self.assertIn('KO',meters[1])
                self.assertIn('Magic Hand A',team[1])
                self.assertTrue(meters[1].endswith('▄'+'▂'*(enemy_width-1)))
                self.assertIn('Magic Hand B KO',team[2])
                self.assertIn('HP 0/49',meters[2])
                self.assertTrue(meters[2].endswith('▂'*enemy_width))
                self.assertTrue(all(row.count('▄')+row.count('▂')==ally_width for row in team))
                self.assertTrue(all(row.count('▄')+row.count('▂')==ally_width+enemy_width for row in meters))
                if spacing>2:
                    self.assertFalse(any(y in frame.drawn for y in (10,11)))
                for name in b.COMMANDS:self.assertIn(name,str(frame))

    def test_early_roster_and_carry(self):
        stock={'Protagonist':(86,29),'Yukari':(45,13),'Junpei':(30,10)}
        solo=P3Battle('awakening',resources=stock,seed=5)
        self.assertEqual([x.name for x in solo.allies],['Protagonist'])
        self.assertEqual(solo.resources,stock)
        b=P3Battle('thebel-patrol',resources=stock,seed=5)
        self.assertEqual([x.name for x in b.allies],list(stock))
        self.assertIsNone(b.act('skill:Agi',b.enemies[0]))
        self.assertEqual(b.resources['Protagonist'],(86,25))
        self.assertEqual(P3Battle('venus-eagles',resources=b.resources).resources,b.resources)

    def test_one_more_shift_handoff_no_boost_and_all_out(self):
        b=P3Battle('venus-eagles',seed=4)
        first,second=b.enemies
        self.assertEqual(len(b.enemies),2)
        self.assertIsNone(b.act('skill:Agi',first))
        self.assertTrue(first.down and b.one_more and not b.all_out)
        junpei=b.allies[2]
        junpei.hp-=10
        before=b.resources
        self.assertIsNone(b.act('shift',junpei))
        self.assertIs(b.actor,junpei)
        self.assertEqual(before,b.resources)
        self.assertTrue(b.act('shift',b.allies[1]))
        self.assertIsNone(b.act('skill:Agi',second))
        self.assertTrue(second.down and b.all_out)
        self.assertIsNone(b.act('allout'))
        self.assertEqual(b.outcome,'win')

    def test_three_physical_types_different_defenses(self):
        for actor_index,action,element in (
                (0,'attack','Slash'),(0,'skill:Bash','Strike'),(1,'attack','Pierce')):
            with self.subTest(element=element):
                b=P3Battle('rampage-drive',seed=1)
                b.actor=b.allies[actor_index]
                foe=b.enemies[0]
                self.assertIsNone(b.act(action,foe))
                self.assertEqual(b.seen[foe.name][element],'normal' if element=='Pierce' else 'resist')
                self.assertNotIn('Physical',b.seen[foe.name])

    def test_enemy_earns_one_more_on_a_fresh_down(self):
        b=P3Battle('thebel-patrol',seed=6)
        hero=b.allies[0]
        for ally in b.allies[1:]:ally.hp=0
        b.enemies[0].hp=0
        hero.affinity['Fire']='weak'
        b._advance()
        self.assertIn('Muttering Tiara earns One More!',b.log)
        self.assertEqual(b.log.count('Muttering Tiara attacks.'),2)
        self.assertLess(hero.hp,hero.max_hp)

    def test_countdown_ignores_presentation_and_rejects_spend_on_invalid(self):
        b=P3Battle('priestess',seed=2)
        b.clock=1
        for key in ('?','\r',ESC,'1','1',ESC,ESC,'8'):
            b.key(key)
            frame=Surface();b.draw(frame)
            self.assertEqual(b.clock,1)
        self.assertIsNone(b.act('analyze',b.enemies[0]))
        self.assertEqual(b.clock,1)
        self.assertTrue(b.act('item:Medicine',b.actor))
        self.assertEqual(b.clock,1)
        self.assertIsNone(b.act('guard'))
        self.assertEqual(b.outcome,'timeout')
        frame=Surface();b.draw(frame)
        self.assertIn('TIME EXPIRED',str(frame))
        self.assertFalse(b.key('\r'))

    def test_invitation_shaves_budget_and_final_action_can_win(self):
        b=P3Battle('priestess',seed=4)
        boss=b.enemies[0]
        boss.hp=300
        self.assertIsNone(b.act('skill:Agi',boss))
        self.assertEqual(b.clock,26)
        self.assertIn('Despairing Tiara',[u.name for u in b.enemies])
        self.assertIsNone(b.act('attack',boss))
        self.assertEqual(b.clock,25)  # Threshold only triggers once.
        b.clock=1;boss.hp=1
        self.assertIsNone(b.act('attack',boss))
        self.assertEqual((b.clock,b.outcome),(0,'win'))

    def test_compact_keyboard_highlights_then_shifts(self):
        b=P3Battle('thebel-patrol',seed=3)
        b.key('2')
        frame=Surface();b.draw(frame)
        self.assertIn('TARGET',str(frame))
        self.assertIn('Cowardly Maya',str(frame))
        self.assertEqual((b.actor.name,b.screen),('Protagonist','target'))
        b.key('1')  # Slash defeats the Maya and earns an extra action.
        b.key('5')
        b.key('\r')  # Shift to the first available ally, Yukari.
        self.assertEqual(b.actor.name,'Yukari')
        b.key('1')
        b.key('1')
        b.key('\r')  # Garu finishes the remaining Wind-weak Tiara.
        self.assertEqual(b.outcome,'win')
        b.key('l')
        self.assertEqual(b.overlay,'log')
        b.key(ESC)
        self.assertFalse(b.key('\r'))

    def test_swift_axle_charge_warning_is_actionable(self):
        b=P3Battle('rampage-drive',persona='Pixie',seed=6)
        for _ in b.allies: self.assertIsNone(b.act('guard'))
        self.assertIn('is charging',b.threat)
        self.assertIsNone(b.act('skill:Zio',b.enemies[0]))
        self.assertTrue(b.enemies[0].down)
        self.assertTrue(b.one_more)
        self.assertIsNone(b.act('guard'))
        self.assertIsNone(b.act('guard'))
        self.assertIsNone(b.act('guard'))
        self.assertFalse(b.threat)
        self.assertIn('The knockdown interrupts Swift Axle’s charge.',b.log)
