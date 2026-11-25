"""Offline Velvet Room combat rules. Scenario numbers are tuned for this simulation."""
from dataclasses import dataclass,field
import random, math
from cutins import ORACLE_SUPPORT, all_out as all_out_cut, showtime as showtime_cut
from battle_data import SKILLS, TEAM, PERSONAS, ITEMS, ENEMIES, ENCOUNTERS

DEFAULT_ATTACK=dict(kind='damage',element='Physical',power=29,target='enemy',accuracy=96)
DEFAULT_GUN=dict(kind='damage',element='Gun',power=24,target='enemy',accuracy=96)
TECH={
 'burn':{'Wind','Nuclear'},'freeze':{'Physical','Nuclear'},
 'shock':{'Physical','Gun','Nuclear'},'sleep':{'Physical','Gun','Fire','Ice','Electric','Wind','Psy','Nuclear','Bless','Curse','Almighty'},
 'dizzy':{'Physical','Gun','Fire','Ice','Electric','Wind','Psy','Nuclear','Bless','Curse','Almighty'},
 'fear':{'Psy'},'forget':{'Psy'},'brainwash':{'Psy'},'rage':{'Psy'},'confuse':{'Psy'},'despair':{'Psy'}
}
AFF={'weak':1.5,'resist':.5,'normal':1,'null':0,'repel':0,'drain':0}
STATS=('attack','defense','agility')
STAT_TURNS=3
@dataclass(eq=False)
class Unit:
 name:str
 hp:int
 sp:int
 skills:list
 affinity:dict
 enemy:bool=False
 behavior:str=''
 no_knockdown:bool=False
 max_ammo:int=4
 max_hp:int=field(init=False)
 max_sp:int=field(init=False)
 ammo:int=field(init=False)
 down:bool=False
 guard:bool=False
 status:str=''
 status_turns:int=0
 buffs:dict=field(default_factory=dict)
 def __post_init__(self):self.max_hp=self.hp;self.max_sp=self.sp;self.ammo=self.max_ammo
 @property
 def alive(self):return self.hp>0
def _unit(name,d,enemy=False):
 return Unit(name,int(d['hp']),int(d.get('sp',0)),list(d.get('skills',[])),dict(d.get('affinity',{})),enemy,
             d.get('behavior',''),d.get('no_knockdown',False) or d.get('behavior')=='boss',int(d.get('ammo',d.get('rounds',0 if enemy else 4))))
class Battle:
 def __init__(self,teammates,encounter,difficulty='Normal',seed=None,*,shuffle_turns=True,
              encounter_config=None,team_data=None,persona_pool=None,enemy_data=None,joker_stats=None):
  if encounter_config is None and encounter not in ENCOUNTERS:raise ValueError('Unknown trial.')
  self.config=ENCOUNTERS[encounter] if encounter_config is None else encounter_config
  self.story=encounter_config is not None
  self.navigator=self.config.get('navigator','Mona' if self.story else 'Oracle')
  self.team_data=TEAM if team_data is None else team_data
  need=self.config.get('party_size',4)-1
  if len(teammates)!=need or len(set(teammates))!=need or any(n not in self.team_data for n in teammates):raise ValueError(f'Select {need} different teammates.')
  if difficulty not in ('Normal','Hard','Merciless'):raise ValueError('Unknown difficulty.')
  self.rng=random.Random(seed);self.encounter=encounter;self.difficulty=difficulty;self.phase='turn'
  self.initiative_rng=random.Random(None if seed is None else seed ^ 0x5A17)
  self.shuffle_turns=shuffle_turns
  self._showtime_rng=random.Random(None if seed is None else seed ^ 0x57071)
  self._showtime=None;self._showtime_spent=False
  self._slot_actor=None;self._slot_effects={}
  self.personas=PERSONAS if persona_pool is None else persona_pool;self.persona=next(iter(self.personas));self.shifted=False
  p=self.personas[self.persona]
  stats={'hp':180,'sp':55,'ammo':5,**(joker_stats or {})}
  self.allies=[_unit('Joker',dict(**stats,skills=p['skills'],affinity=p['affinity']))]+[_unit(n,self.team_data[n]) for n in teammates]
  self.items={k:v['count'] for k,v in ITEMS.items()}
  if not teammates and not self.story:
   self.allies[0].hp=self.allies[0].max_hp=205
   self.allies[0].sp=self.allies[0].max_sp=72
   self.items['Medicine']+=1
  self.log=[];self.seen={};self.last_error=None;self.chain=0;self.one_more=False;self.passed=set()
  self.damage_events=[]
  self.reaper_turn=0;self._reaper_charge=None;self._reaper_last_phase=''
  config=self.config
  self.waves=config['waves']
  self.enemy_data=ENEMIES if enemy_data is None else enemy_data
  self._story_intent='';self._boss_state={}
  self._support_used=False
  # Presentation state is separate from damage, initiative and the save.
  self.cut_in=None;self.cut_in_queue=[];self._ufo_cut_seen=False
  if config.get('shuffle_count'):
   from shuffle_data import SHUFFLE_ENEMIES
   self.enemy_data=SHUFFLE_ENEMIES
   draw=random.Random(None if seed is None else seed ^ 0x5A40)
   self.waves=[draw.sample(sorted(self.enemy_data),config['shuffle_count'])]
  self.wave_count=len(self.waves);self.wave=1
  self.round=1;self.cursor=-1;self.actor=None
  self.interlude=None
  self._say(f'Trial entered: {encounter} // {difficulty}.')
  self._spawn();self._advance()
  if self._support_used:self._queue_cutin(ORACLE_SUPPORT)
 @property
 def story_intent(self):
  if not self.story:return ''
  from weekend_bosses import intent
  return intent(self)
 def _offer_showtime(self,baton=False):
  self._showtime=None
  if not self.story or self._showtime_spent or len(self.allies)<2:return
  roster=set(self.config.get('available_thieves',()))
  active={u.name:u for u in self.allies}
  a=self.actor
  options=[]
  for pair in self.config.get('showtime_pairs',()):
   if a.name not in pair or not roster.issuperset(pair):continue
   partner=active.get(next(n for n in pair if n!=a.name))
   if partner and (not partner.alive or partner.down or partner.status in ('sleep','freeze','fear')):continue
   options.append(pair)
  if not options:return
  danger=any(u.alive and 3*u.hp<=u.max_hp for u in self.allies)
  finisher=any(u.alive and 4*u.hp<=u.max_hp for u in self.enemies)
  if (baton or danger or finisher) and self._showtime_rng.random()<(.48 if baton else .16):
   self._showtime=self._showtime_rng.choice(options)
 def _say(self,msg):
  self.log.append(msg)
  if len(self.log)>160:del self.log[:-160]
 def upcoming_turns(self):
  """Scheduled movers after the current action, including across a round boundary."""
  if self.phase!='turn':return []
  return [u for u in (self.order[self.cursor+1:]+self.next_order)
          if u.alive and u.status not in ('sleep','freeze')
          and not (u.status=='burn' and u.hp<=max(1,u.max_hp//12))][:len(self.order)]
 def _roll_order(self):
  roster=self.allies+self.enemies
  if not self.shuffle_turns:return roster
  live=[u for u in roster if u.alive]
  for _ in range(16):
   self.initiative_rng.shuffle(live)
   sides=[u.enemy for u in live]
   if len(live)<3 or len(set(sides))<2 or sum(a!=b for a,b in zip(sides,sides[1:]))>=2:break
  # Keep KO'd slots available in case a fighter is revived before their turn.
  absent=[u for u in roster if not u.alive]
  for u in absent:live.insert(self.initiative_rng.randrange(len(live)+1),u)
  return live
 def _spawn(self):
  names=self.waves[self.wave-1]; totals={n:names.count(n) for n in names};counts={}
  self.enemies=[]
  for n in names:
   counts[n]=counts.get(n,0)+1
   u=_unit(n,self.enemy_data[n],True)
   if totals[n]>1:u.name=f'{n} {chr(64+counts[n])}'
   self.enemies.append(u)
  if self.story and self.config.get('party_size')==1:
   for u in self.enemies:u.hp=u.max_hp=max(1,round(u.max_hp*.72))
  if self.story and self.config.get('id','').startswith(('cruiser-','depths-','laboratory-')) and self.wave>1:
   for u in self.allies:
    if u.alive:
     u.hp=min(u.max_hp,u.hp+round(u.max_hp*.26));u.sp=min(u.max_sp,u.sp+8)
   self._say('Between waves: standing allies catch their breath and recover some HP/SP.')
  self.order=self._roll_order()
  if self.story and self.wave==1:
   opener=next(u for u in self.order if not u.enemy and u.alive)
   self.order.remove(opener);self.order.insert(0,opener)
  self.next_order=self.order[:] if self.story else self._roll_order();self.cursor=-1
  self._boss_state={};self._story_intent='';self._showtime=None
  for u in self.allies:
   u.ammo=u.max_ammo;u.down=False;u.guard=False
  self._say(f'Wave {self.wave}/{self.wave_count}: '+', '.join(u.name for u in self.enemies)+'. Ammo refilled.')
 @property
 def allout_fighters(self):
  return sum(u.alive and not u.down for u in self.allies)
 @property
 def allout_damage(self):
  return 32*self.allout_fighters
 @property
 def hold_up(self):
  foes=[t for t in self.enemies if t.alive]
  joker=self.allies[0]
  return bool(self.phase=='turn' and self.one_more and self.actor and not self.actor.enemy and joker.alive and not joker.down and self.allout_fighters>=2 and foes and all(u.down for u in foes))
 def _next_wave(self):
  if self.wave==self.wave_count:
   self.phase='win';self._say('Trial cleared. The Velvet Room awaits.')
  else:
   self.wave+=1;self.round=1;self._spawn()
 def _state(self):
  if self.phase!='turn':return True
  if not self.allies[0].alive:
   self.phase='loss';self._say('Joker fell. Trial failed.');return True
  if not any(u.alive for u in self.enemies):
   self.interlude=self.config.get('wave_breaks',{}).get(self.wave)
   if self.interlude:
    self.phase='interlude';self._finish_slot()
    self.one_more=False;self.chain=0;self.passed=set();self._showtime=None
   else:self._next_wave()
   return True
  return False
 def resume_wave(self):
  """Resume a configured story break without resetting the squad's state."""
  if self.phase!='interlude' or not self.interlude:
   raise ValueError('There is no paused wave to resume.')
  self.interlude=None;self.phase='turn'
  self.damage_events.clear();self.cut_in=None;self.cut_in_queue.clear()
  had_support=self._support_used
  self._next_wave()
  if self.phase=='turn':self._advance()
  if not had_support and self._support_used:self._queue_cutin(ORACLE_SUPPORT)
 def _advance(self):
  self.one_more=False;self.chain=0;self.passed=set();self._showtime=None
  while self.phase=='turn':
   self._finish_slot()
   self.cursor+=1
   if self.cursor>=len(self.order):
    self.order=self.next_order;self.next_order=self.order[:] if self.story else self._roll_order()
    self.cursor=0;self.round+=1;self._say(f'Round {self.round}.')
    if self.story:
     from weekend_bosses import on_round
     on_round(self)
   u=self.order[self.cursor]
   if not u.alive:continue
   self.actor=u;self.shifted=False;u.guard=False
   self._slot_actor=u;self._slot_effects=dict(u.buffs)
   if self._reaper_charge is not None and not u.enemy:self._reaper_charge.discard(u)
   if u.down:u.down=False;self._say(f'{u.name} gets back up.')
   if u.status:
    status=u.status
    if status=='burn':
     d=self._hurt(u,max(1,u.max_hp//12));self._say(f'{u.name} takes {d} burn damage.')
    if status=='sleep':
     heal=min(u.max_hp-u.hp,max(1,u.max_hp//12));u.hp+=heal;u.sp=min(u.max_sp,u.sp+3)
    u.status_turns-=1
    if u.status_turns<=0:u.status='';self._say(f'{u.name} shakes off {status}.')
    if self._state():
     if self.phase!='turn':return
     continue
    if not u.alive:continue
    if status in ('sleep','freeze') or status in ('shock','fear','confuse') and self.rng.random()<.45:
     self._say(f'{u.name} loses the turn to {status}.');continue
   if not u.enemy:
    pending=self._boss_state.get('pending')
    if pending is not None:pending.discard(u)
    self._offer_showtime()
    return
   bonus=self._enemy_step(u)
   if self._state():
    if self.phase!='turn':return
    continue
   if bonus and u.alive:
    self._say(f'{u.name} gets One More!')
    self._enemy_step(u)
    if self._state():
     if self.phase!='turn':return
     continue
 def _finish_slot(self):
  u=self._slot_actor
  if u is None:return
  for k,original in self._slot_effects.items():
   if u.buffs.get(k) is not original:continue
   sign,left=original
   if left<=1:
    del u.buffs[k]
    self._say(f'{u.name}: {k} effect wore off.')
   else:u.buffs[k]=(sign,left-1)
  self._slot_actor=None;self._slot_effects={}
 def _spec(self,id):
  if id=='attack':return DEFAULT_ATTACK
  if id=='gun':return DEFAULT_GUN
  if id=='showtime':return dict(kind='damage',element='Almighty',power=111,target='enemy',accuracy=100)
  if id.startswith('skill:'):return SKILLS.get(id[6:])
  if id.startswith('item:'):
   item=ITEMS.get(id[5:]);return SKILLS[item['skill']] if item else None
  return None
 def _cash(self,u,s):
  sp=int(s.get('sp',0));hp=math.ceil(u.max_hp*s.get('hp',0)/100)
  if self.chain>=3 and not u.enemy and self.one_more:sp=hp=0
  return sp,hp
 def _afford(self,u,s):
  return not self._cost_block(u,s)
 def _cost_block(self,u,s):
  sp,hp=self._cash(u,s)
  if u.status=='forget' and (s.get('sp',0) or s.get('hp',0)):
   return f'{u.name} has Forget and can’t use Persona skills.'
  if u.sp<sp:return f'{u.name} needs {sp} SP but has {u.sp} SP.'
  if u.hp<=hp:return f'{u.name} needs more than {hp} HP to survive the skill ({u.hp} HP left).'
 def command_block(self,cat):
  if cat=='gun':return 'Out of ammo. Guns reload at the next wave.'
  if cat=='items':return 'No usable items remain in the squad’s bag.'
  if cat=='baton':return 'No eligible ally to receive the Baton Pass.' if self.one_more else 'Earn One More before using Baton Pass.'
  if cat=='allout':
   if self.allies[0].down:return 'Joker is knocked down. He must be standing for an All-Out Attack.'
   return 'All-Out Attack requires a Hold Up (all living Shadows down and two squad members standing).'
  if cat=='skills':return 'This fighter has no Persona skills available.'
  return 'No eligible moves for this command.'
 def action_block(self,id,target=None,persona=None,*,pick_target=False):
  """Explain an invalid standard action without changing combat state."""
  a=self.actor;s=self._spec(id)
  if s is None:return 'Unknown action.'
  switching=id.startswith('skill:') and persona is not None and persona!=self.persona
  if switching and (a.name!='Joker' or self.shifted or persona not in self.personas):
   return 'Joker can switch Personas only once per action.'
  skills=self.personas[persona]['skills'] if switching else a.skills
  if id.startswith('skill:') and id[6:] not in skills:return 'That skill is not on the selected Persona.'
  if id.startswith('item:') and not self.items.get(id[5:],0):return f'No {id[5:]} left in the bag.'
  if id=='gun' and not a.ammo:return self.command_block('gun')
  reason=self._cost_block(a,s)
  if reason:return reason
  kind=s['kind'];mode=s['target'];candidates=self.targets(id)
  if mode in ('enemy','ally'):
   if not candidates:
    if kind=='revive':return 'No ally is knocked out. Use an HP heal for a living ally.'
    return 'No living ally to target.' if mode=='ally' else 'No living Shadow to target.'
   if target not in candidates:
    if pick_target and target is None:return None
    if kind=='revive':return 'Revival only works on a knocked-out ally.'
    if kind in ('heal','restore') and target in self.allies and not target.alive:
     return f'{target.name} is knocked out. Use a revival skill or item first.'
    return 'Choose a living ally.' if mode=='ally' else 'Choose a living Shadow.'
  recipients=([target] if target is not None else [a] if mode=='self' else
              [u for u in self.allies if u.alive] if mode=='allies' else [])
  if recipients and kind in ('heal','restore'):
   resource='HP' if kind=='heal' else 'SP'
   if all(getattr(u,resource.lower())==getattr(u,'max_'+resource.lower()) for u in recipients):
    who=recipients[0].name if len(recipients)==1 else 'Every living ally'
    return f'{who} already has full {resource}.'
 def targets(self,id):
  if self.phase!='turn':return []
  if id=='analyze':return [t for t in self.enemies if t.alive]
  s=self._spec(id)
  if not s:return []
  dest=s.get('target','enemy')
  if dest=='enemy':return [t for t in self.enemies if t.alive]
  if dest=='ally':return [t for t in self.allies if (t.alive != (s['kind']=='revive'))]
  return []
 def _baton(self):
  return [t for t in self.allies if t.alive and not t.down and t is not self.actor and t not in self.passed and t.status not in ('sleep','freeze')]
 def actions(self,cat,persona=None):
  if self.phase!='turn' or self.actor is None or self.actor.enemy:return []
  a=self.actor
  if cat=='showtime' and self._showtime:
   return [('showtime','Showtime [T]',' × '.join(self._showtime)+' • Almighty • free, once per battle.')]
  if cat=='story-special' and self.story:
   from weekend_bosses import special
   row=special(self)
   return [row] if row else []
  if cat=='attack':return [('attack','Melee attack','Physical damage. No resource cost.')]
  if cat=='gun':return [('gun','Fire one shot',f'{a.ammo}/{a.max_ammo} rounds. Reloads between waves.')] if a.ammo else []
  if cat=='guard':return [('guard','Guard','Reduce incoming damage and prevent knockdowns until your next turn.')]
  if cat=='analyze':return [('analyze','Analyze','Review only affinities already observed. Does not spend your turn.')]
  if cat=='allout':return [('allout','All-Out Attack',f'{self.allout_fighters} standing • {self.allout_damage} damage to each Shadow.')] if self.hold_up else []
  if cat=='baton':
   return [(f'pass:{t.name}',f'Pass to {t.name}','Give your extra action to an ally and boost damage.') for t in self._baton()] if self.one_more else []
  if cat=='persona':
   return [(f'persona:{n}',n,p.get('role','Change Joker’s skills and affinities.')) for n,p in self.personas.items() if n!=self.persona] if a.name=='Joker' and not self.shifted else []
  if cat=='items':
   return [(f'item:{n}',f'{n} ×{count}',self._describe(SKILLS[ITEMS[n]['skill']])) for n,count in self.items.items() if count>0]
  if cat=='skills':
   names=self.personas[persona]['skills'] if a.name=='Joker' and not self.shifted and persona in self.personas else a.skills
   return [(f'skill:{n}',n,self._describe(SKILLS[n],a)) for n in names]
  return []
 def _describe(self,s,a=None):
  sp,hp=self._cash(a,s) if a else (0,0)
  cost=f'{sp} SP' if sp else f'{s.get("hp",0)}% HP' if hp else 'No cost'
  p=s.get('power',0);k=s['kind']; elem=s.get('element','')
  tp=('all enemies' if s['target']=='enemies' else 'all allies' if s['target']=='allies' else s['target'])
  label=(f'{elem} damage' if k=='damage' else f'{s.get("status","status").title()} ailment' if k=='ailment' else
         f'{("Accuracy/Evasion" if s.get("stat")=="agility" else "ATK/DEF/AGI" if s.get("stat")=="all" else s["stat"].title())} {"↑" if k=="buff" else "↓"} ({STAT_TURNS} turns)'
         if k in ('buff','debuff') else 'Restore SP' if k=='restore' else
         'Remove stat buffs' if k=='dekaja' else 'Remove stat debuffs' if k=='dekunda' else k.title())
  return ' • '.join([cost,label,tp]+([f'power {p}'] if p else []))
 def _queue_cutin(self,card):
  if self.cut_in is None:self.cut_in=card
  else:self.cut_in_queue.append(card)
 def act(self,id,target=None,*,persona=None):
  self.damage_events.clear();self.cut_in=None;self.cut_in_queue.clear()
  supported=self._support_used
  error=self._act(id,target,persona)
  if not supported and self._support_used:self._queue_cutin(ORACLE_SUPPORT)
  self.last_error=error
  return error
 def _equip_persona(self,n):
  a=self.actor;p=self.personas[n]
  self.persona=n;a.skills=list(p['skills']);a.affinity=dict(p['affinity']);self.shifted=True
  self._say(f'Joker switches to {n}.')
 def _act(self,id,target,persona=None):
  if self.phase!='turn' or not self.actor or self.actor.enemy:return 'No active party turn.'
  a=self.actor
  if id=='story-special' and self.story:
   from weekend_bosses import use_special
   return use_special(self)
  if id=='showtime':
   if not self._showtime or target not in self.targets(id):return 'No Showtime is available for that target.'
   title='SHOWTIME / '+' × '.join(self._showtime)
   self._queue_cutin(showtime_cut(self._showtime))
   self._showtime_spent=True;self._showtime=None
   self._execute(a,self._spec(id),target,title)
   if not self._state() or self.phase=='turn':self._advance()
   return None
  if id=='analyze':
   if target not in self.targets(id):return 'Select a living Shadow.'
   seen=self.seen.get(target.name,{})
   intel=', '.join(f'{k}: {v}' for k,v in seen.items()) or 'unknown affinities'
   self._say(f'Analyze {target.name}: {intel}.');return None
  if id.startswith('persona:'):
   n=id[8:]
   if a.name!='Joker' or self.shifted or n not in self.personas or n==self.persona:return 'Joker can switch once per action.'
   self._equip_persona(n);return None
  if id.startswith('pass:'):
   t=next((t for t in self._baton() if t.name==id[5:]),None)
   if not self.one_more:return self.command_block('baton')
   if t is None:return 'That ally is down, unable to act, or already chained.'
   self.passed.add(a);self.actor=t;self.chain+=1;self.shifted=False
   t.hp=min(t.max_hp,t.hp+4*self.chain);t.sp=min(t.max_sp,t.sp+self.chain)
   self._say(f'Baton Pass! {a.name} → {t.name}. Chain ×{self.chain}.');self._offer_showtime(baton=True);return None
  if id=='allout':
   if not self.hold_up:return self.command_block('allout')
   damage=self.allout_damage
   if self.story:
    foes=[t for t in self.enemies if t.alive]
    oracle_drop=('ufo' in self.config.get('oracle_features',()) and not self._ufo_cut_seen
                 and len(foes)>=2 and all(t.hp<=damage for t in foes))
    if oracle_drop:self._ufo_cut_seen=True
    self._queue_cutin(all_out_cut(a.name,oracle_drop))
   self._say(f'All-Out Attack! {self.allout_fighters} standing • {damage} damage per Shadow.')
   for t in self.enemies:
    if t.alive:self._hurt(t,damage)
   if self._state():
    if self.phase=='turn':self._advance()
   else:self._advance()
   return None
  if id=='guard':
   a.guard=True;self._say(f'{a.name} guards.');self._advance();return None
  s=self._spec(id)
  switching=id.startswith('skill:') and persona is not None and persona!=self.persona
  reason=self.action_block(id,target,persona)
  if reason:return reason
  if switching:self._equip_persona(persona)
  if id=='gun':a.ammo-=1
  if id.startswith('item:'):self.items[id[5:]]-=1
  sp,hp=self._cash(a,s);a.sp-=sp;a.hp-=hp
  extra=self._execute(a,s,target,id.split(':',1)[-1])
  if self._state():
   if self.phase=='turn':self._advance()
  elif extra:
   self.one_more=True;self.shifted=False
   self._offer_showtime()
   self._say('Hold Up! All-Out Attack available.' if self.hold_up else f'{a.name} gets One More!')
  else:self._advance()
  return None
 def _hurt(self,t,num):
  before=t.hp
  d=max(0,int(num));t.hp=max(0,t.hp-d)
  if t.hp<before:self.damage_events.append((t,before,t.hp))
  if not t.alive:t.down=False;t.status=''
  return d
 def _execute(self,a,s,target,name):
  if self.story and not a.enemy and target is not None and target.enemy and s['kind']=='damage':
   from weekend_bosses import intercept
   target=intercept(self,target,s)
  ours=self.enemies if a.enemy else self.allies
  theirs=self.allies if a.enemy else self.enemies
  mode=s['target'];kind=s['kind']
  targets=[a] if mode=='self' else ([t for t in ours if t.alive] if mode=='allies' else [t for t in theirs if t.alive]) if mode in ('allies','enemies') else [target]
  self._say(f'{a.name} → {name.title() if name in ("attack","gun") else name}.')
  bonus=False
  for t in targets:
   if t is None:continue
   if kind=='damage':bonus=self._strike(a,t,s) or bonus
   elif kind=='heal':
    old=t.hp;t.hp=min(t.max_hp,t.hp+int(s.get('power',0)*(1+.2*self.chain if not a.enemy else 1)));self._say(f'{t.name} recovers {t.hp-old} HP.')
   elif kind=='restore':
    old=t.sp;t.sp=min(t.max_sp,t.sp+int(s.get('power',0)));self._say(f'{t.name} recovers {t.sp-old} SP.')
   elif kind=='revive':
    t.hp=max(1,min(t.max_hp,round(t.max_hp*int(s.get('power',50))/100)));t.down=False;self._say(f'{t.name} returns with {t.hp} HP.')
   elif kind=='cure':
    self._say(f'{t.name} clears {t.status or "no ailment"}.');t.status='';t.status_turns=0
   elif kind in ('buff','debuff'):
    stat=s.get('stat','attack'); sign=1 if kind=='buff' else -1
    for key in STATS if stat=='all' else (stat,):
     prior=t.buffs.get(key,(0,0))[0]
     if prior==-sign:
      del t.buffs[key]
      self._say(f'{t.name}: {key} returned to normal.')
     else:
      t.buffs[key]=(sign,STAT_TURNS)
      state='up' if sign==1 else 'down'
      self._say(f'{t.name}: {key} {state} ({STAT_TURNS} turns'+(', refreshed).' if prior else ').'))
   elif kind in ('dekaja','dekunda'):
    remove_sign=1 if kind=='dekaja' else -1
    removed=[key for key,(sign,_) in t.buffs.items() if sign==remove_sign]
    for key in removed:del t.buffs[key]
    self._say(f'{t.name}: '+('cleared '+', '.join(removed)+'.' if removed else 'no stat effects to clear.'))
   elif kind=='ailment':self._ail(t,s.get('status',''),s.get('chance',0.9))
  return bonus
 def _ail(self,t,status,chance):
  chance=chance/100 if chance>1 else chance
  if not status or not t.alive:return
  if t.guard:self._say(f'{t.name} guards against {status}.');return
  if t.no_knockdown: self._say(f'{t.name} shook off the ailment.');return
  if not t.status and self.rng.random()<chance:
   t.status=status;t.status_turns=2;self._say(f'{t.name} is afflicted with {status}.')
  else:self._say(f'{t.name} resisted {status}.')
 def _strike(self,a,t,s):
  if self.story and not a.enemy and t.enemy:
   from weekend_bosses import block_hit
   if block_hit(self,t,s):return False
  e=s.get('element','Physical'); f=t.affinity.get(e,'normal')
  if e=='Almighty':f='normal'
  accuracy=s.get('accuracy',96)
  accuracy-=8*t.buffs.get('agility',(0,0))[0];accuracy+=8*a.buffs.get('agility',(0,0))[0]
  if a.status=='dizzy':accuracy-=18
  if self.rng.randrange(100)>=accuracy:self._say(f'{t.name} dodged.');return False
  marked=t.status in TECH and e in TECH[t.status]
  # Physical hits shatter frozen targets' ordinary physical defenses.
  frozen_override=t.status=='freeze' and e in ('Physical','Gun')
  if not a.enemy and t.enemy and not frozen_override:self.seen.setdefault(t.name,{})[e]=f
  if frozen_override and f in ('null','repel','drain','resist'):f='normal'
  crit=e in ('Physical','Gun') and f not in ('null','repel','drain','resist') and self.rng.randrange(100)<s.get('crit',14)
  amount=s['power']*self.rng.uniform(.91,1.09)
  amount*=1+0.25*a.buffs.get('attack',(0,0))[0]
  amount*=1-0.25*t.buffs.get('defense',(0,0))[0]
  if self.difficulty=='Hard':amount*=1.27 if a.enemy else .84
  if self.difficulty=='Merciless':amount*=1.34 if a.enemy else .80
  if self.difficulty=='Merciless' and (f=='weak' or marked or crit):amount*=2.0
  if not a.enemy and self.chain:amount*=1+.2*self.chain
  if f in ('null','repel','drain'):
   if f=='repel':self._hurt(a,max(1,round(amount)));self._say(f'{t.name} repels {e}!')
   elif f=='drain':t.hp=min(t.max_hp,t.hp+max(1,round(amount)));self._say(f'{t.name} drains {e}!')
   else:self._say(f'{t.name} blocks {e}.')
   return False
  amount*=AFF.get(f,1)
  if marked:amount*=1.42
  if crit:amount*=1.45
  if t.guard:amount*=.48
  was_down=t.down
  dmg=self._hurt(t,max(1,round(amount)))
  tags=[name for cond,name in [(f=='weak','WEAK'),(f=='resist','RESIST'),(crit,'CRITICAL'),(marked,'TECHNICAL'),(t.guard,'GUARD')] if cond]
  self._say(f'{t.name} takes {dmg} damage'+(' ['+' · '.join(tags)+']' if tags else '')+('.' if t.alive else ' — down for the count!'))
  if t.status in ('freeze','sleep') and marked:t.status='';t.status_turns=0
  if s.get('status'):self._ail(t,s['status'],s.get('chance',.24))
  # A weakness KO counts only if the target was standing before the hit.
  # _hurt clears Down on KO, so test the pre-hit state.
  if not t.alive:return f=='weak' and not was_down
  if (f=='weak' or crit or marked) and not t.guard and not t.no_knockdown and not was_down:
   t.down=True
   return True
  return False
 @property
 def reaper_phase(self):
  if self.encounter!='Reaper Alert' or not self.enemies:return ''
  u=self.enemies[0]
  return 'Last Toll' if u.hp*100<=32*u.max_hp else 'Judgment' if u.hp*100<=68*u.max_hp else 'Pursuit'
 @property
 def reaper_intent(self):
  if not self.reaper_phase or self.phase!='turn':return ''
  if self._reaper_charge is not None:return 'Concentrate → Megidolaon. Guard before the blast.'
  if self.reaper_phase=='Pursuit':return 'The Reaper hunts weaknesses. Watch Joker’s current Persona.'
  if self.reaper_phase=='Judgment':return 'Expect stat pressure and charged Almighty damage.'
  return 'Final phase. Save enough HP to survive the next charge.'
 def _reaper_step(self,a):
  self.reaper_turn+=1
  phase=self.reaper_phase
  tier={'Pursuit':0,'Judgment':1,'Last Toll':2}[phase]
  if phase!=self._reaper_last_phase:
   self._reaper_last_phase=phase;self._say(f'The Reaper / {phase.upper()}.')
  live=[u for u in self.allies if u.alive]
  if self._reaper_charge is not None:
   if any(u.alive for u in self._reaper_charge):
    self._say('The Reaper holds its charge. Megidolaon is still coming.')
    return False
   self._reaper_charge=None
   spell=dict(kind='damage',power=61+7*tier,element='Almighty',target='enemies',accuracy=100)
   self._execute(a,spell,None,'Megidolaon')
   return False
  cycle=self.reaper_turn
  if (tier==0 and cycle%5==0) or (tier==1 and cycle%4==0) or (tier==2 and cycle%3==0):
   self._reaper_charge=set(live)
   self._say('The Reaper → Concentrate. Megidolaon is coming. Guard!')
   return False
  if tier and cycle%5==2 and sum(sign>0 for u in live for sign,_ in u.buffs.values())>=3:
   self._execute(a,SKILLS['Dekaja'],None,'Dekaja')
   return False
  if tier and cycle%4==1 and cycle>2:
   chosen=max(live,key=lambda u:u.hp/u.max_hp)
   self._execute(a,SKILLS['Debilitate'],chosen,'Debilitate')
   return False
  if cycle%3==0:
   spells=('Maragion','Mabufula','Mazionga','Magarula','Mapsio','Mafreila','Makouga','Maeiga')
   def pressure(name):
    elem=SKILLS[name]['element']
    return sum(1 if u.affinity.get(elem)=='weak' else -1 if u.affinity.get(elem) in ('repel','drain','null') else 0 for u in live)+self.rng.random()*1.8
   name=max(spells,key=pressure)
   self._execute(a,dict(SKILLS[name],power=26+3*tier,chance=8),None,name)
   return False
  elements=('Agilao','Bufula','Zionga','Garula','Psio','Freila','Kouga','Eiga')
  def threat(pair):
   name,u=pair;aff=u.affinity.get(SKILLS[name]['element'],'normal')
   return {'weak':19,'resist':-16,'null':-90,'repel':-90,'drain':-90}.get(aff,0)+self.rng.random()*26-17*u.guard-9*u.down
  name,target=max(((name,u) for name in elements for u in live),key=threat)
  self._execute(a,dict(SKILLS[name],power=33+3*tier,chance=10),target,name)
  if self.allies[0].alive and cycle%3==2:
   targets=[u for u in live if u.alive and u.affinity.get('Gun') not in ('null','repel','drain')]
   if targets:
    target=self.rng.choice(targets)
    self._execute(a,dict(DEFAULT_GUN,power=25+2*tier,crit=4),target,'Gun')
   else:
    target=self.rng.choice([u for u in live if u.alive])
    self._execute(a,dict(DEFAULT_ATTACK,power=22+2*tier,crit=4),target,'Attack')
  return False
 def _enemy_step(self,a):
  if self.story:
   from weekend_bosses import enemy_step
   result=enemy_step(self,a)
   if result is not None:return result
  if a.behavior=='reaper':return self._reaper_step(a)
  living=[u for u in self.allies if u.alive]
  friends=[u for u in self.enemies if u.alive]
  if not living:return False
  options=[]
  for name,s in [('Attack',DEFAULT_ATTACK)]+[(n,SKILLS[n]) for n in a.skills if n in SKILLS]:
   if not self._afford(a,s):continue
   kind=s['kind']; mode=s['target']
   if kind=='damage':
    def score(u):
     af=u.affinity.get(s.get('element','Physical'),'normal')
     return s['power']*(0.08 if af in ('null','repel','drain') else 1.50 if af=='weak' else .55 if af=='resist' else 1)*(.55 if u.guard else 1)+ (12 if u.hp<35 else 0)
    if mode=='enemies':options.append((sum(score(u) for u in living)*.56,name,s,None))
    else:options.extend((score(u),name,s,u) for u in living)
   elif kind=='heal':
    wounded=[u for u in friends if u.hp/u.max_hp<.54]
    if wounded:
     t=min(wounded,key=lambda t:t.hp/t.max_hp)
     options.append((62+(1-t.hp/t.max_hp)*26+(13 if a.behavior=='support' else 0),name,s,t))
   elif kind=='ailment':
    clean=[u for u in living if not u.status]
    if clean:options.append((57+(14 if a.behavior=='ailment' else 0),name,s,self.rng.choice(clean)))
   elif kind in ('buff','debuff','dekaja','dekunda'):
    friendly=kind in ('buff','dekunda')
    sign=1 if kind in ('buff','dekaja') else -1
    stat=s.get('stat','all')
    keys=STATS if stat=='all' else (stat,)
    def utility(u):
     if kind in ('dekaja','dekunda'):
      return 23*sum(u.buffs.get(k,(0,0))[0]==sign for k in keys)
     return sum(18 if u.buffs.get(k,(0,0))[0]!=sign else 6 if u.buffs[k][1]==1 else 0 for k in keys)
    pool=friends if friendly else living
    if mode in ('allies','enemies'):
     score=sum(utility(u) for u in pool)
     if score:options.append((30+min(46,score*.55),name,s,None))
    else:
     for t in ([a] if mode=='self' else pool):
      score=utility(t)
      if score:options.append((35+min(37,score),name,s,t))
  if not options:return False
  _,name,s,t=max(options,key=lambda x:x[0]+self.rng.uniform(-20,20))
  sp,hp=self._cash(a,s);a.sp-=sp;a.hp-=hp
  return self._execute(a,s,t,name)
