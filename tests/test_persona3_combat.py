"""Deterministic checks for the standalone Persona 3 combat slice."""
import curses as C
import unittest

from persona_terminal.persona3.persona3_combat import ESC, P3Battle, hp_meter, party_caps, persona_skills


class Surface:
    h,w=25,65

    def __init__(self):
        self.drawn={}
        self.painted=[]

    def put(self,y,x,text,*_):
        assert 0<=y<self.h and 0<=x<self.w and x+len(text)<self.w
        self.drawn.setdefault(y,[]).append(text)
        self.painted.append((y,x,text))

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
        for w,h,first,left_step,right_step,ally_width,enemy_width in (
                (65,25,7,2,3,6,17),(96,34,8,4,4,18,32)):
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

                def half(y,enemy=False):
                    return ''.join(t for row,x,t in frame.painted if row==y and (x>=w//2)==enemy)

                team=[half(first+i*left_step) for i in range(3)]
                team_sp=[half(first+1+i*left_step) for i in range(3)]
                foes=[half(first+i*right_step,True) for i in range(3)]
                foe_hp=[half(first+1+i*right_step,True) for i in range(3)]
                self.assertIn('MakotoHP 65',team[0])
                self.assertIn('SP 0',team_sp[0])
                self.assertIn('▂'*ally_width,team_sp[0])
                self.assertIn('YukariHP 0',team[1])
                self.assertIn('KO',team_sp[1])
                self.assertIn('Barbaric Beast Wheel ↓',foes[0])
                self.assertIn('Magic Hand A',foes[1])
                self.assertTrue(foe_hp[1].endswith('▄'+'▂'*(enemy_width-1)))
                self.assertIn('Magic Hand B KO',foes[2])
                self.assertIn('HP 0/49',foe_hp[2])
                self.assertTrue(foe_hp[2].endswith('▂'*enemy_width))
                for row in team+team_sp:
                    self.assertEqual(row.count('▄')+row.count('▂'),ally_width)
                if left_step>2:
                    self.assertEqual(half(first+2),'')
                    self.assertEqual(half(first+3),'')
                    self.assertEqual(half(first+3,True),'')
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
        second.guard=False  # Isolate Shift and All-Out; the guard is tested separately.
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
        self.assertIn('is charging',b.threat)
        self.assertIsNone(b.act('skill:Zio',b.enemies[0]))
        self.assertTrue(b.enemies[0].down)
        self.assertTrue(b.one_more)
        self.assertIsNone(b.act('guard'))
        self.assertIsNone(b.act('guard'))
        self.assertIsNone(b.act('guard'))
        self.assertFalse(b.threat)
        self.assertIn('The knockdown interrupts Swift Axle’s charge.',b.log)

    def test_persona_preview_target_cancel_and_explicit_free_equip(self):
        for width,height in ((65,25),(100,40)):
            with self.subTest(width=width):
                b=P3Battle('priestess',stock={'Orpheus':(), 'Apsaras':('Agi',)},seed=2)
                resources=b.resources
                b.key('1')
                b.key(C.KEY_RIGHT)
                view=Surface();view.w,view.h=width,height
                b.draw(view)
                self.assertIn('Apsaras / PREVIEW',str(view))
                self.assertIn('Ice resist',str(view))
                self.assertIn('P EQUIP',str(view))
                self.assertIn('Agi',str(view))
                b.key('1');self.assertEqual(b.screen,'target')
                b.key(ESC)
                self.assertEqual((b.persona,b.screen,b.clock),('Orpheus','skills',30))
                b.key('p')
                self.assertEqual((b.persona,b.screen,b.clock),('Apsaras','skills',30))
                self.assertEqual(b.allies[0].affinity['Ice'],'resist')
                self.assertEqual(b.resources,resources)
                b.key(C.KEY_RIGHT)
                self.assertIsNone(b.mask_preview)
                self.assertTrue(b.act('persona:Orpheus'))

    def test_cast_validation_precedes_equip_and_normal_turn_resets_lock(self):
        b=P3Battle('venus-eagles',stock={'Orpheus':(), 'Apsaras':('Agi',)},seed=3)
        lead=b.actor
        first,second=b.enemies
        lead.sp=2
        problem=b.act('skill:Agi',first,persona='Apsaras')
        self.assertIn('needs 4 SP',problem)
        self.assertEqual((b.persona,lead.sp,b.persona_used),('Orpheus',2,False))
        lead.sp=20
        self.assertTrue(b.act('skill:Agi',lead,persona='Apsaras'))
        self.assertEqual((b.persona,lead.sp),('Orpheus',20))
        self.assertIsNone(b.act('skill:Agi',first,persona='Apsaras'))
        self.assertTrue(b.one_more and b.persona_used)
        self.assertEqual((b.persona,lead.sp),('Apsaras',16))
        self.assertIn('next normal turn',b.act('persona:Orpheus'))
        self.assertTrue(b.one_more)
        self.assertIsNone(b.act('shift',b.allies[2]))
        self.assertIn('Only Makoto',b.act('persona:Orpheus'))
        for _ in range(3):
            if b.actor is lead:break
            self.assertIsNone(b.act('guard'))
        self.assertIs(b.actor,lead)
        self.assertFalse(b.persona_used)
        self.assertIsNone(b.act('persona:Orpheus'))

    def test_level_caps_and_shared_persona_skill_source(self):
        self.assertEqual(party_caps(3)['Protagonist'],(138,58))
        self.assertIn('Sukukaja',persona_skills('Pixie',3,('Zio','Agi')))
        self.assertEqual(persona_skills('Pixie',3,('Zio','Agi')).count('Zio'),1)
        b=P3Battle('thebel-patrol',level=3,persona='Pixie',stock={'Pixie':('Agi',)},resources={'Yukari':(30,20)})
        self.assertEqual(b.resources['Yukari'],(30,20))
        self.assertEqual((b.actor.max_hp,b.actor.max_sp),(138,58))
        self.assertEqual(b.actor.skills,persona_skills('Pixie',3,('Agi',)))
        self.assertTrue(b.act('persona:Orpheus'))

    def test_gatekeeper_guards_and_braces_prevent_instant_sweeps(self):
        ravens=P3Battle('venus-eagles',seed=5)
        target=ravens.enemies[-1]
        self.assertIn('guarding',ravens.threat)
        self.assertIsNone(ravens.act('skill:Agi',target))
        self.assertFalse(target.down)
        self.assertIs(ravens.actor,ravens.allies[1])
        wheel=P3Battle('dancing-hand',seed=5)
        wheel.actor=wheel.allies[1]
        boss,*hands=wheel.enemies
        self.assertIn('Magic Hands brace',wheel.threat)
        self.assertIsNone(wheel.act('skill:Garu',boss))
        self.assertFalse(boss.down)
        self.assertLess(boss.hp,boss.max_hp)
        for hand in hands:hand.hp=0
        wheel.actor=wheel.allies[1]
        self.assertIsNone(wheel.act('skill:Garu',boss))
        self.assertTrue(boss.down)
        self.assertNotIn('Magic Hands brace',wheel.threat)

    def test_affinity_learning_only_from_hits_and_correct_each_target(self):
        for w,h in ((65,25),(100,40)):
            with self.subTest(width=w):
                b=P3Battle('venus-eagles',seed=3)
                one,two=b.enemies
                b.key('1')
                self.assertEqual(b._menu()[0][0],'Agi')
                initial=Surface();initial.w,initial.h=w,h;b.draw(initial)
                affinity_width=3 if w==65 else 5
                fire_x=w//2+2+3*affinity_width
                self.assertIn((10,fire_x,'?'),initial.painted)
                b.key('1')
                self.assertEqual([r[0] for r in b._menu()],[one.name,two.name])
                self.assertTrue(not b.seen)
                b.key(ESC);b.key(ESC)
                b.key('7');b.key('1')
                scan=Surface();scan.w,scan.h=w,h;b.draw(scan)
                self.assertIn('Fire  UNKNOWN',str(scan))
                self.assertEqual(b.seen,{})
                b.key(ESC)
                b.key('1');b.key('1');b.key('1')
                self.assertEqual(b.seen,{one.name:{'Fire':'weak'}})
                learned=Surface();learned.w,learned.h=w,h;b.draw(learned)
                self.assertIn((10,fire_x,'W' if w==65 else 'WEAK'),learned.painted)
                self.assertIn((13 if w==65 else 14,fire_x,'?'),learned.painted)
                b.key('1')
                self.assertIn('[WEAK]',b._menu()[0][0])
                b.key('1')
                self.assertEqual([r[0] for r in b._menu()],[one.name+' [WEAK]',two.name])
                one.hp=0;one.down=False
                b.key(ESC)
                self.assertNotIn('[WEAK]',b._menu()[0][0])

    def test_vulnerability_is_not_weakness_and_scan_stays_read_only(self):
        b=P3Battle('priestess',seed=2)
        foe=b.enemies[0]
        self.assertIsNone(b.act('skill:Agi',foe))
        self.assertFalse(b.one_more or foe.down)
        self.assertEqual(b.seen[foe.name]['Fire'],'vulnerable')
        self.assertEqual(b.clock,29)
        self.assertIsNone(b.act('analyze',foe))
        self.assertEqual(b.clock,29)
        self.assertEqual(b.seen[foe.name],{'Fire':'vulnerable'})
        b.overlay='intel'
        scan=Surface();b.draw(scan)
        self.assertIn('Fire  VULNERABLE',str(scan))
        self.assertIn('does not knock down',str(scan))
        b.overlay=None;b.actor=b.allies[-1]
        b.screen='skills'
        self.assertEqual(b._menu()[0][0],'Agi [VULN]')

    def test_all_affinity_symbols_and_short_names_have_unique_colors_and_cells(self):
        b=P3Battle('priestess')
        e=b.enemies[0]
        b.seen[e.name]={'Slash':'normal','Strike':'weak','Pierce':'resist','Fire':'vulnerable',
                        'Ice':'null','Electric':'repel','Wind':'drain'}
        for w,h,stride,marks in (
                (65,25,3,('·','W','R','V','N','P','D','?','?')),
                (100,40,5,('NORM','WEAK','RES','VULN','NULL','RPL','DRN','?','?'))):
            frame=Surface();frame.w,frame.h=w,h;b.draw(frame)
            x=w//2+2
            self.assertEqual(tuple(t for y,col,t in frame.painted if y==10 and col>=x),marks)
            self.assertTrue(all((10,x+i*stride,t) in frame.painted for i,t in enumerate(marks)))
            b.overlay='help'
            help_frame=Surface();help_frame.w,help_frame.h=w,h;b.draw(help_frame)
            self.assertIn('V Vulnerable (extra damage, no down)',str(help_frame))
            b.overlay=None
