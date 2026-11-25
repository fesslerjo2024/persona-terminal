import unittest
from functools import partial
from curses import KEY_LEFT, KEY_RIGHT
from battle_engine import Battle, TEAM, ENCOUNTERS, SKILLS, DEFAULT_ATTACK
from battle_ui import BattleUI, RED, HP_FLASH, HP_DRAIN
class CombatChecks(unittest.TestCase):
 def battle(self, name='Castle Downfall',seed=3):
  return Battle(['Mona','Skull','Panther'],name,seed=seed,shuffle_turns=False)
 def test_rosters(self):
  for name,data in ENCOUNTERS.items():
   team=[] if data.get('party_size')==1 else ['Crow','Violet','Noir']
   b=Battle(team,name,seed=6,shuffle_turns=False)
   self.assertEqual(len(b.allies),len(team)+1)
   self.assertEqual(b.actor.name,'Joker')
   self.assertEqual(b.wave_count,len(data['waves']))
 def test_one_more_and_baton(self):
  b=self.battle(); joker=b.actor; foe=b.enemies[1]
  b.enemies[0].hp=b.enemies[2].hp=250
  self.assertIsNone(b.act('skill:Eiha',foe))
  self.assertTrue(b.one_more and foe.down)
  self.assertEqual(b.seen[foe.name]['Curse'],'weak')
  self.assertIsNone(b.act('pass:Mona'));self.assertEqual(b.chain,1)
  self.assertIsNotNone(b.act('pass:Joker'))
  self.assertIsNone(b.act('skill:Garula',b.enemies[0]))
  self.assertTrue(b.one_more)
  self.assertIsNone(b.act('pass:Skull'))
  self.assertIsNone(b.act('skill:Zionga',b.enemies[2]))
  self.assertTrue(b.one_more)
  self.assertIsNone(b.act('pass:Panther'));before=b.actor.sp
  self.assertEqual(b.chain,3)
  self.assertIsNone(b.act('skill:Agilao',foe))
  self.assertEqual(b.allies[3].sp,before)
  self.assertEqual(b.wave,1)
 def test_hold_up(self):
  b=self.battle()
  for u in b.enemies:u.down=True;u.hp=20
  b.one_more=True
  self.assertTrue(b.hold_up)
  self.assertIsNone(b.act('allout'))
  self.assertEqual(b.wave,2)
  self.assertEqual(b.actor.name,'Joker')
 def test_allout_scales_with_standing_squad(self):
  for downed,expected in ((0,128),(1,96),(2,64)):
   b=self.battle()
   for u in b.enemies:u.down=True;u.hp=200
   b.one_more=True
   if downed:b.allies[1].down=True
   if downed==2:b.allies[2].hp=0
   self.assertTrue(b.hold_up)
   self.assertEqual(b.allout_damage,expected)
   self.assertIsNone(b.act('allout'))
   self.assertTrue(all(u.hp==200-expected for u in b.enemies))
 def test_weakness_ko_grants_one_more_for_a_standing_shadow(self):
  b=self.battle();foe=b.enemies[1];foe.hp=1
  self.assertIsNone(b.act('skill:Eiha',foe))
  self.assertFalse(foe.alive)
  self.assertTrue(b.one_more)
  self.assertEqual(b.actor.name,'Joker')
 def test_ko_does_not_grant_one_more_if_down_or_not_weak(self):
  for already_down,weak in ((True,True),(False,False)):
   b=self.battle();foe=b.enemies[1];foe.hp=1;foe.down=already_down
   if not weak:foe.affinity['Curse']='normal'
   self.assertIsNone(b.act('skill:Eiha',foe))
   self.assertFalse(foe.alive)
   self.assertFalse(b.one_more)
   self.assertEqual(b.actor.name,'Mona')
 def test_allout_requires_joker_standing_even_on_an_ally_turn(self):
  b=self.battle();joker=b.allies[0]
  b.actor=b.allies[1];b.cursor=1;b.one_more=True
  for u in b.enemies:u.down=True;u.hp=200
  joker.down=True
  self.assertEqual(b.allout_fighters,3)
  self.assertEqual(b.actions('allout'),[])
  self.assertIn('Joker is knocked down',b.act('allout'))
  self.assertTrue(b.one_more)
  self.assertTrue(all(u.hp==200 for u in b.enemies))
  joker.down=False
  self.assertTrue(b.hold_up)
  self.assertTrue(b.actions('allout'))
 def test_guard_and_enemy(self):
  b=self.battle()
  for i in range(4):self.assertIsNone(b.act('guard'))
  self.assertEqual(b.round,2)
  self.assertTrue(any('takes ' in m and 'GUARD' in m for m in b.log))
  self.assertFalse(b.allies[0].guard)
  self.assertEqual(b.actor.name,'Joker')
 def test_cannot_repeatedly_down_same_shadow(self):
  b=self.battle();foe=b.enemies[1];foe.hp=foe.max_hp=500
  self.assertIsNone(b.act('skill:Eiha',foe));self.assertTrue(foe.down)
  self.assertEqual(b.actor.name,'Joker');b.rng.seed(3)
  self.assertIsNone(b.act('skill:Eiha',foe));self.assertEqual(b.actor.name,'Mona')
 def test_sp_and_items(self):
  b=self.battle(); a=b.actor; t=b.allies[1]; a.sp=0
  self.assertIsNotNone(b.act('skill:Eiha',b.enemies[0]))
  self.assertEqual(b.actor,a);self.assertEqual(a.sp,0)
  count=b.items['Soul Drop'];t.sp=0
  self.assertIsNone(b.act('item:Soul Drop',t))
  self.assertEqual(t.sp,10);self.assertEqual(b.items['Soul Drop'],count-1)
 def test_technical_and_ailment_guard(self):
  b=self.battle(seed=3);t=b.enemies[0];t.hp=t.max_hp=300;t.status='burn'
  self.assertTrue(b._strike(b.actor,t,SKILLS['Garula']))
  self.assertTrue(t.down);self.assertTrue(any('TECHNICAL' in x for x in b.log))
  t.status='';t.guard=True;b._ail(t,'sleep',100);self.assertEqual(t.status,'')
 def test_joker_falls(self):
  b=self.battle();b.allies[0].hp=0;b._state()
  self.assertEqual(b.phase,'loss')
 def test_burn_ko_skips_fighter_before_their_action(self):
  b=self.battle();mona=b.allies[1]
  mona.hp=1;mona.status='burn';mona.status_turns=2
  self.assertNotIn(mona,b.upcoming_turns())
  self.assertIsNone(b.act('guard'))
  self.assertEqual(mona.hp,0)
  self.assertIs(b.actor,b.allies[2])
class PersonaTabChecks(unittest.TestCase):
 def setUp(self):
  self.ui=BattleUI();self.ui.battle_init();self.ui._b_class=partial(Battle,shuffle_turns=False);self.ui._b_launch()
  self.b=self.ui._b_battle;self.order=list(self.ui._b_personas)
 def test_single_tab_cycles_live_skill_list_and_wraps(self):
  self.assertEqual([row[1] for row in self.ui._b_action_menu()].count('Persona'),1)
  self.ui.battle_key(KEY_RIGHT)
  self.assertEqual(self.ui._b_screen,'command')
  self.ui.battle_key('1')
  self.assertEqual(self.ui._b_action_rows()[0][1],'Eiha')
  for name in self.order[1:]+self.order[:1]:
   self.ui.battle_key(KEY_RIGHT)
   self.assertEqual(self.ui._b_screen,'actions')
   self.assertEqual(self.ui._b_persona_view,name)
   self.assertEqual([r[1] for r in self.ui._b_action_rows()],self.ui._b_personas[name]['skills'])
  self.ui.battle_key(KEY_LEFT)
  self.assertEqual(self.ui._b_persona_view,self.order[-1])
  self.assertEqual(self.b.persona,self.order[0])
  self.ui.battle_key('\x1b')
  self.assertEqual(self.ui._b_screen,'command')
  self.assertFalse(self.b.shifted)
 def test_cancel_target_and_cast_from_new_persona(self):
  self.b.rng.seed(3)
  self.ui.battle_key('1')
  self.ui.battle_key(KEY_RIGHT)
  self.ui.battle_key('1')
  self.assertEqual(self.ui._b_screen,'targets')
  self.ui.battle_key('\x1b')
  self.assertEqual(self.ui._b_action_rows()[0][1],'Bufula')
  self.assertEqual(self.b.persona,self.order[0])
  self.ui.battle_key('1')
  self.ui.battle_key('1')
  self.assertEqual(self.b.persona,'Jack Frost')
  self.assertTrue(any('Joker → Bufula' in s for s in self.b.log))
 def test_unaffordable_skill_does_not_switch(self):
  self.b.actor.sp=0
  self.ui.battle_key('1')
  self.ui.battle_key(KEY_RIGHT)
  self.ui.battle_key('1')
  self.ui.battle_key('1')
  self.assertEqual(self.ui._b_message,'Joker needs 8 SP but has 0 SP.')
  self.assertEqual(self.b.persona,self.order[0])
  self.assertFalse(self.b.shifted)
 def test_teammates_cannot_cycle(self):
  self.ui.battle_key('4')
  self.assertEqual(self.b.actor.name,'Mona')
  self.ui.battle_key('1')
  before=self.ui._b_action_rows()
  self.ui.battle_key(KEY_RIGHT)
  self.ui.battle_key(KEY_LEFT)
  self.assertEqual(self.ui._b_screen,'actions')
  self.assertEqual(self.ui._b_action_rows(),before)
  self.assertEqual(self.b.persona,self.order[0])

class BattleIntelChecks(unittest.TestCase):
 def setUp(self):
  self.ui=BattleUI();self.ui.battle_init();self.ui._b_class=partial(Battle,shuffle_turns=False);self.ui._b_launch()
  self.b=self.ui._b_battle;self.b.rng.seed(3)
 def test_queue_uses_scheduled_slots_even_after_baton(self):
  b=self.b
  self.assertEqual(b.upcoming_turns()[:4],b.allies[1:]+b.enemies[:1])
  foe=b.enemies[1];foe.hp=500
  self.assertIsNone(b.act('skill:Eiha',foe))
  self.assertIsNone(b.act('pass:Skull'))
  self.assertEqual(b.actor.name,'Skull')
  self.assertEqual(b.upcoming_turns()[0].name,'Mona')
  for u in b.allies[1:3]:u.hp=0
  b.allies[3].status='sleep'
  self.assertIs(b.upcoming_turns()[0],b.enemies[0])
 def test_only_resolved_elements_reveal(self):
  b=self.b;a=b.actor;target=b.enemies[0];other=b.enemies[1]
  self.assertFalse(b._strike(a,target,dict(SKILLS['Bufula'],accuracy=0)))
  self.assertNotIn(target.name,b.seen)
  b._strike(a,target,dict(SKILLS['Bufula'],accuracy=100))
  self.assertEqual(b.seen[target.name],{'Ice':'weak'})
  self.assertNotIn(other.name,b.seen)
  b._strike(a,target,dict(SKILLS['Agilao'],accuracy=100))
  self.assertEqual(b.seen[target.name],{'Ice':'weak','Fire':'drain'})
 def test_one_more_strip_and_defeated_shadow(self):
  b=self.b;foe=b.enemies[0];foe.hp=0
  self.assertIsNone(b.act('skill:Eiha',b.enemies[1]))
  self.assertTrue(b.one_more)
  self.assertNotIn(foe,b.upcoming_turns())
  self.ui.w=126;written=[]
  self.ui.put=lambda y,x,value,*args:written.append(value)
  self.ui._b_turn_strip(5)
  self.assertIn('NOW Joker +1   NEXT ',written)
  self.assertNotIn(foe.name,written)
 def test_affinity_and_queue_fit_small_and_large_arena(self):
  self.b.seen[self.b.enemies[0].name]={'Ice':'weak'}
  for w,h in ((65,25),(85,28),(126,46)):
   screen={}
   self.ui.w=w;self.ui.h=h
   def put(y,x,value,*args):
    self.assertTrue(0<=y<h and 0<=x<w,(y,x,value))
    for i,c in enumerate(value):
     if x+i<w-1:screen[y,x+i]=c
   self.ui.put=put
   self.ui.frame=lambda *_:None
   self.ui._b_arena()
   line=lambda y:''.join(screen.get((y,x),' ') for x in range(w))
   self.assertIn('NOW Joker   NEXT Mona',line(5))
   self.assertIn('Ph',line(7));self.assertIn('Al',line(7))
   self.assertIn('█',line(8))
   self.assertIn('W',line(9));self.assertEqual(line(9).count('?'),10)
   self.assertEqual(line(12 if w>=91 and h>=37 else 11).count('?'),11)

class BattleBlockChecks(unittest.TestCase):
 def setUp(self):
  self.ui=BattleUI();self.ui.battle_init();self.ui._b_class=partial(Battle,shuffle_turns=False);self.ui._b_launch()
  self.b=self.ui._b_battle
 def test_healing_reports_full_hp_and_does_not_cost_turn_or_sp(self):
  b=self.b;joker=b.actor
  self.ui.battle_key('4')
  mona=b.actor;sp=mona.sp
  self.ui.battle_key('1');self.ui.battle_key('3');self.ui.battle_key('1')
  self.assertEqual(self.ui._b_message,'Joker already has full HP.')
  self.assertIs(b.actor,mona);self.assertEqual(mona.sp,sp)
  joker.hp-=30;self.ui.battle_key('1')
  self.assertEqual(joker.hp,joker.max_hp);self.assertLess(mona.sp,sp)
 def test_revive_and_forget_have_distinct_reasons(self):
  b=self.b;joker=b.actor
  self.assertIn('No ally is knocked out',b.act('item:Revival Bead'))
  b.allies[1].hp=0
  self.assertEqual(b.act('item:Medicine',b.allies[1]),'Mona is knocked out. Use a revival skill or item first.')
  self.assertIn('Revival only works',b.act('item:Revival Bead',joker))
  joker.status='forget'
  self.assertIn('Forget',b.act('skill:Eiha',b.enemies[0]))
 def test_command_and_hp_block_reasons(self):
  joker=self.b.actor
  joker.ammo=0;self.ui.battle_key('3')
  self.assertIn('Out of ammo',self.ui._b_message)
  self.ui.battle_key('6');self.assertIn('One More',self.ui._b_message)
  self.ui.battle_key('7');self.assertIn('Hold Up',self.ui._b_message)
  joker.hp=1
  self.assertIn('HP to survive',self.b.act('skill:Cleave',self.b.enemies[0]))

class HealthAnimationChecks(unittest.TestCase):
 def setUp(self):
  self.ui=BattleUI();self.ui.battle_init();self.ui._b_class=partial(Battle,shuffle_turns=False);self.ui._b_launch()
  self.b=self.ui._b_battle
 def test_red_segment_holds_drains_and_settles(self):
  shots=[]
  self.ui.put=lambda y,x,value,color,*args:shots.append((value,color))
  ally=self.b.allies[0];ally.hp=90
  self.ui._b_hp_trails[ally]=(180,5)
  for t,expected in ((5,5),(5+HP_FLASH/2,5),(5+HP_FLASH+HP_DRAIN/2,3),(5+HP_FLASH+HP_DRAIN+0.01,0)):
   shots.clear();self.ui._b_hp_draw(0,0,ally,10,t)
   self.assertEqual(sum(len(s) for s,c in shots if c==RED),expected)
   self.assertEqual(sum(len(s) for s,_ in shots),10)
  self.assertEqual(shots[0][0],'█'*5)
 def test_attack_and_burn_record_different_bars(self):
  ally=self.b.allies[1];ally.status='burn';ally.status_turns=2
  enemy=self.b.enemies[0];enemy.hp=enemy.max_hp=300
  self.b.rng.seed(3)
  self.ui._b_apply('attack',enemy)
  self.assertEqual(self.ui._b_hp_trails[ally][0],ally.max_hp)
  self.assertEqual(self.ui._b_hp_trails[enemy][0],300)
 def test_previous_wave_stays_visible_for_finishing_hit(self):
  outgoing=self.b.enemies
  for enemy in outgoing:enemy.hp=20;enemy.down=True
  self.b.one_more=True
  self.ui._b_apply('allout')
  self.assertEqual(self.b.wave,2)
  self.assertIs(self.ui._b_outgoing[1],outgoing)
  self.assertTrue(all(self.ui._b_hp_trails[u][0]==20 for u in outgoing))

class StatInitiativeChecks(unittest.TestCase):
 def battle(self,seed=3,shuffle=False):
  return Battle(['Mona','Queen','Panther'],'Castle Downfall',seed=seed,shuffle_turns=shuffle)
 def test_initiative_varies_and_interleaves_both_sides(self):
  orders=set()
  for seed in range(16):
   b=self.battle(seed,True)
   for order in (b.order,b.next_order):
    self.assertEqual(set(order),set(b.allies+b.enemies))
    self.assertGreaterEqual(sum(a.enemy!=z.enemy for a,z in zip(order,order[1:])),2)
   orders.add(tuple(u.name for u in b.order))
  self.assertGreater(len(orders),8)
 def test_next_round_uses_exact_forecast(self):
  b=self.battle(9,True);forecast=list(b.next_order)
  b._enemy_step=lambda _:False
  first_expected=next(u for u in forecast if not u.enemy)
  while b.round==1:self.assertIsNone(b.act('guard'))
  self.assertEqual(b.order,forecast)
  self.assertIs(b.actor,first_expected)
 def test_party_wide_buffs_and_enemy_wide_debuffs(self):
  b=self.battle()
  queen,panther=b.allies[2:4]
  b._execute(queen,SKILLS['Marakukaja'],None,'Marakukaja')
  self.assertTrue(all(u.buffs['defense']==(1,3) for u in b.allies))
  b._execute(panther,SKILLS['Matarunda'],None,'Matarunda')
  self.assertTrue(all(u.buffs['attack']==(-1,3) for u in b.enemies))
  shadow=b.enemies[0]
  b._execute(shadow,SKILLS['Marakukaja'],None,'Marakukaja')
  self.assertTrue(all(u.buffs['defense']==(1,3) for u in b.enemies))
  b._execute(queen,SKILLS['Dekaja'],None,'Dekaja')
  self.assertTrue(all(u.buffs=={'attack':(-1,3)} for u in b.enemies))
  b._execute(shadow,SKILLS['Dekunda'],None,'Dekunda')
  self.assertTrue(all(not u.buffs for u in b.enemies))
 def test_opposites_cancel_and_reapply_refreshes(self):
  b=self.battle();ally=b.allies[1];shadow=b.enemies[0]
  ally.buffs['attack']=(1,1)
  b._execute(b.actor,SKILLS['Tarukaja'],ally,'Tarukaja')
  self.assertEqual(ally.buffs['attack'],(1,3))
  b._execute(shadow,SKILLS['Tarunda'],ally,'Tarunda')
  self.assertNotIn('attack',ally.buffs)
 def test_stat_expires_after_three_regular_turns_not_free_actions(self):
  b=self.battle();joker=b.actor
  b._enemy_step=lambda _:False
  b._execute(joker,SKILLS['Tarukaja'],joker,'Tarukaja')
  b.act('analyze',b.enemies[0])
  self.assertEqual(joker.buffs['attack'],(1,3))
  b.act('guard')  # casting turn does not consume the newly applied effect
  self.assertEqual(joker.buffs['attack'],(1,3))
  for remaining in (2,1,0):
   while b.actor is not joker:b.act('guard')
   b.act('guard')
   self.assertEqual(joker.buffs.get('attack',(0,0))[1],remaining)
 def test_attack_and_defense_change_damage(self):
  def damage(attack,defense):
   b=self.battle();u=b.actor;foe=b.enemies[1]
   foe.hp=foe.max_hp=500;u.buffs['attack']=(attack,3)
   foe.buffs['defense']=(defense,3)
   b._strike(u,foe,dict(SKILLS['Eiha'],accuracy=100))
   return 500-foe.hp
  base=damage(0,0)
  self.assertGreater(damage(1,0),base)
  self.assertLess(damage(0,1),base)
  self.assertGreater(damage(0,-1),base)
  self.assertLess(damage(-1,0),base)

class SpecialTrialChecks(unittest.TestCase):
 def reaper(self):
  return Battle(['Mona','Violet','Queen'],'Reaper Alert',seed=4,shuffle_turns=False)
 def test_reaper_is_one_enemy_and_same_hp_pool_across_phases(self):
  b=self.reaper();foe=b.enemies[0]
  self.assertEqual(b.wave_count,1)
  self.assertEqual([u.name for u in b.enemies],['The Reaper'])
  self.assertGreater(foe.max_hp,1000)
  self.assertEqual(b.reaper_phase,'Pursuit')
  foe.hp=600;self.assertEqual(b.reaper_phase,'Judgment')
  foe.hp=300;self.assertEqual(b.reaper_phase,'Last Toll')
  self.assertFalse(b._state());self.assertIs(b.enemies[0],foe)
 def test_reaper_charge_waits_and_guard_reduces_the_blast(self):
  def resolve(guard):
   b=self.reaper();boss=b.enemies[0];joker=b.allies[0]
   b.reaper_turn=4
   self.assertFalse(b._enemy_step(boss))
   self.assertIn('Megidolaon',b.reaper_intent)
   before=joker.hp
   b._enemy_step(boss)
   self.assertEqual(joker.hp,before)
   b._reaper_charge.clear()
   joker.guard=guard
   b._enemy_step(boss)
   self.assertIsNone(b._reaper_charge)
   self.assertTrue(any('→ Megidolaon' in m for m in b.log))
   return before-joker.hp
  self.assertGreater(resolve(False),2*resolve(True)-2)
 def test_shuffle_is_three_distinct_boss_free_shadows(self):
  from shuffle_data import SHUFFLE_ENEMIES
  self.assertGreaterEqual(len(SHUFFLE_ENEMIES),100)
  draws=set()
  for seed in range(18):
   b=Battle(['Mona','Violet','Queen'],'Mementos Shuffle',seed=seed,shuffle_turns=False)
   names=tuple(u.name for u in b.enemies)
   self.assertEqual(b.wave_count,1)
   self.assertEqual(len(set(names)),3)
   self.assertLessEqual(set(names),set(SHUFFLE_ENEMIES))
   self.assertTrue(all(not u.no_knockdown and all(s in SKILLS for s in u.skills) for u in b.enemies))
   draws.add(names)
  self.assertGreaterEqual(len(draws),17)

if __name__=='__main__':unittest.main()
