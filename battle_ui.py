"""Velvet Room battle interface. Simulation rules live in battle.py."""
import curses as C
import textwrap
import time
from cutins import duration as cutin_duration
import cinema
from wrestling_scene import HEIGHT as SCENE_ROWS, WIDTH as SCENE_COLUMNS

RED,GOLD,CYAN,WHITE,DIM,GREEN=range(1,7)
ENTER=(C.KEY_ENTER,'\r','\n')
ESC='\x1b'
ELEMENTS=(
    ('Physical','Ph',GOLD),('Gun','Gu',GOLD),('Fire','Fi',RED),
    ('Ice','Ic',CYAN),('Electric','El',GOLD),('Wind','Wi',GREEN),
    ('Psy','Ps',RED),('Nuclear','Nu',CYAN),('Bless','Bl',WHITE),
    ('Curse','Cu',RED),('Almighty','Al',DIM),
)
AFFINITY={
    'unknown':('?',DIM),'normal':('·',WHITE),'weak':('W',GOLD),
    'resist':('R',CYAN),'null':('N',CYAN),'repel':('P',RED),'drain':('D',GREEN),
}
HP_FLASH=0.24
HP_DRAIN=0.42
HP_SETTLE=0.12
MODIFIERS=(('attack','ATK'),('defense','DEF'),('agility','AGI'))


class BattleUI:
    """Curses rendering and navigation for the Velvet Room."""

    def _b_put(self,y,x,msg,color=WHITE,bold=False,reverse=False,width=None):
        if width is not None:msg=msg[:max(0,width)]
        self.put(y,x,msg,color,bold,reverse)

    def _b_rule(self,y,x,w,c=RED):
        self._b_put(y,x,'─'*max(0,w),c)

    def _b_par(self,y,x,msg,w,maxlines=2,color=DIM):
        for i,line in enumerate(textwrap.wrap(str(msg),max(8,w),break_long_words=False)[:maxlines]):
            self._b_put(y+i,x,line,color,width=w)

    def _b_hp_draw(self,y,x,u,w,now):
        def cells(hp):
            return max(int(hp>0),min(w,round(w*hp/max(1,u.max_hp))))
        filled=cells(u.hp)
        stable=filled
        trailing=0
        anim=self._b_hp_trails.get(u)
        if anim:
            before,started=anim
            elapsed=now-started
            if before>u.hp and elapsed<HP_FLASH+HP_DRAIN:
                fraction=max(0.0,min(1.0,1-(elapsed-HP_FLASH)/HP_DRAIN))
                lost=max(1,cells(before)-filled)
                # A sub-cell hit briefly recolors one cell without shortening
                # the final bar below the actual displayed HP.
                if cells(before)==filled:stable=max(0,filled-1)
                trailing=min(w-stable,int(lost*fraction+0.999999))
        if stable:self._b_put(y,x,'█'*stable,GREEN if u.hp>u.max_hp*.3 else GOLD)
        if trailing:self._b_put(y,x+stable,'▓'*trailing,RED,True)
        empty=w-stable-trailing
        if empty:self._b_put(y,x+stable+trailing,'░'*empty,DIM)

    def _b_heading(self,y,x,text,w):
        self._b_put(y,x,text,CYAN,True,width=w)
        self._b_rule(y+1,x,w,DIM)

    def _b_list(self,rows,y,x,w,h,idx,shortcut=True):
        """Rows are (title, detail, enabled); return selected row."""
        if not rows:
            self._b_put(y,x,'Nothing available.',DIM,width=w)
            return
        i=max(0,min(idx,len(rows)-1))
        step=2 if h>=len(rows)*2 and self.w>=78 else 1
        visible=max(1,h//step)
        start=min(max(0,i-visible//2),max(0,len(rows)-visible))
        for n,row in enumerate(rows[start:start+visible],start):
            title,detail,enabled=row
            a=n==i
            p=('▶' if a else ' ')+' '+(f'{n+1:>2} ' if shortcut else '')
            color=CYAN if a else WHITE if enabled else DIM
            line=(p+title)[:w].ljust(w)
            self._b_put(y+(n-start)*step,x,line,color,a,a,width=w)
            if step==2:self._b_put(y+(n-start)*step+1,x+len(p),detail,DIM,width=w-len(p))
        return rows[i]

    @staticmethod
    def _b_nav(k,i,n):
        if k in (C.KEY_UP,'k','K'):return (i-1)%max(1,n)
        if k in (C.KEY_DOWN,'j','J'):return (i+1)%max(1,n)
        if k==C.KEY_HOME:return 0
        if k==C.KEY_END:return max(0,n-1)
        if k==C.KEY_PPAGE:return max(0,i-5)
        if k==C.KEY_NPAGE:return min(max(0,n-1),i+5)
        return i

    @staticmethod
    def _b_commit(k,i,n):
        if k in ENTER:return i
        if isinstance(k,str) and k in '123456789' and int(k)<=n:return int(k)-1
        return None

    def battle_init(self):
        from battle_engine import Battle, TEAM, PERSONAS, ENCOUNTERS
        self._b_class=Battle
        self._b_team=TEAM
        self._b_personas=PERSONAS
        self._b_trials=ENCOUNTERS
        self._b_trial_names=list(ENCOUNTERS)
        self._b_roster=list(TEAM)
        self._b_selected=[n for n in ('Mona','Skull','Panther') if n in TEAM]
        if len(self._b_selected)<3:
            self._b_selected=self._b_roster[:3]
        self._b_trial=0
        self._b_diff=0
        self._b_levels=['Normal','Hard','Merciless']
        self._b_screen='setup'
        self._b_index=0
        self._b_saved_index=0
        self._b_category='skills'
        self._b_persona_view=None
        self._b_id=None
        self._b_action_title=''
        self._b_message=''
        self._b_battle=None
        self._b_overlay=None
        self._b_log_scroll=0
        self._b_hp_trails={}
        self._b_outgoing=None
        self._b_cut_in=None
        self._b_cut_damage=None
        self._b_cut_queue=[]

    def _b_ensure(self):
        if not hasattr(self,'_b_battle'):
            self.battle_init()

    def _b_launch(self):
        trial=self._b_trial_names[self._b_trial]
        needed=self._b_trials[trial].get('party_size',4)-1
        selected=self._b_selected if needed else []
        if len(selected)!=needed:
            self._b_message=f'Choose exactly {needed} teammates alongside Joker.'
            return
        try:
            new=self._b_class(list(selected),trial,self._b_levels[self._b_diff])
        except ValueError as exc:
            self._b_message=str(exc)
            return
        self._b_battle=new
        self._b_prepare_presentation(new,time.monotonic())
        self._b_screen='command'
        self._b_persona_view=None
        self._b_index=0
        self._b_id=None
        self._b_message=''
        self._b_overlay=None
        self._b_log_scroll=0

    def _b_setup_draw(self):
        wide=self.w>=85
        title='VELVET ROOM / SQUAD'
        self.frame(title,'↑ ↓ SELECT   ENTER TOGGLE   ← → TRIAL   D LEVEL   S DEPLOY   ESC BACK')
        a,x=3, self.w//2+1
        left=(x-a-2) if wide else self.w-6
        right=self.w-x-3
        meta=self._b_trial_names[self._b_trial]
        trial=self._b_trials[meta]
        needed=trial.get('party_size',4)-1
        count=trial.get('wave_count',len(trial.get('waves') or []))
        waves='WAVES VARY' if not count else '1 WAVE' if count==1 else f'{count} WAVES'
        if trial.get('shuffle_count'):
            waves+=f' / {trial["shuffle_count"]} SHUFFLED SHADOWS'
        self._b_heading(4,a,f'TEAM  {len(self._b_selected)}/{needed}  +  JOKER' if needed else 'WILD CARD  /  JOKER ONLY',left)
        if wide:
            self._b_heading(4,x,'TRIAL DOSSIER',right)
            self._b_put(6,x,f'{self._b_trial+1:02}/{len(self._b_trial_names):02}  {meta}',GOLD,True,width=right)
            self._b_put(8,x,f'LEVEL  {self._b_levels[self._b_diff].upper()}',CYAN,True,width=right)
            self._b_put(9,x,waves,CYAN,True,width=right)
            self._b_par(11,x,trial.get('description',''),right,3,WHITE)
            if trial.get('hint'):
                self._b_heading(14,x,'ORACLE INTEL',right)
                self._b_par(16,x,trial['hint'],right,3)
            self._b_par(20,x,'Joker can change Persona. Build a squad with distinct elements and someone who can keep it standing.',right,3)
        rows=[]
        for name in self._b_roster:
            record=self._b_team[name]
            selected=needed and name in self._b_selected
            role=record.get('role','')
            persona=record.get('persona','')
            health='  '+f'HP {record["hp"]} / SP {record["sp"]}' if wide else ''
            rows.append((f'{"●" if selected else "○"} {name:<8} {persona}{health}',role,bool(needed)))
        if self._b_roster:
            self._b_list(rows,6,a,left,max(1,(self.h-12 if wide else min(8,self.h-17))),self._b_index)
            tip=self._b_team[self._b_roster[self._b_index]].get('role','')
        else:tip=''
        if wide:
            self._b_par(self.h-8,a,tip,left,2,GOLD)
        else:
            self._b_heading(15,a,f'TRIAL  {meta}  /  {self._b_levels[self._b_diff].upper()}',left)
            self._b_put(17,a,waves,CYAN,True,width=left)
            self._b_par(18,a,trial.get('description',''),left,2,WHITE)
        self._b_put(self.h-5,3,self._b_message or ('Select three allies, then deploy.' if needed else 'Solo trial: your selected squad stays on standby.'),GOLD,width=self.w-6)

    @staticmethod
    def _b_modifiers(u):
        if not u.alive:return []
        mods=[]
        for key,label in MODIFIERS:
            value=u.buffs.get(key)
            if value:
                direction,remaining=value
                if direction and remaining>0:
                    mods.append((f'{label}{"↑" if direction>0 else "↓"}{remaining}',GREEN if direction>0 else RED))
        return mods

    def _b_mod_draw(self,y,x,w,u):
        mods=self._b_modifiers(u)
        for token,color in mods:
            if len(token)>w:break
            self._b_put(y,x,token,color,True)
            x+=len(token)+2
            w-=len(token)+2

    def _b_unit_draw(self,y,x,w,u,active=False,now=0,tall=False):
        states=[]
        if u.hp<=0:states.append('KO')
        if u.down and u.hp>0:states.append('DOWN')
        if u.guard and u.hp>0:states.append('GUARD')
        if u.status and u.hp>0:states.append(str(u.status).upper())
        text=f'{"▶" if active else " "} {u.name}'
        if states:text+='  ['+' / '.join(states)+']'
        color=RED if u.hp<=0 else GOLD if u.down or u.status else CYAN if active else WHITE
        mods=self._b_modifiers(u)
        if not tall and mods and len(text)+2+len(mods[0][0])>w:
            text=text[:max(2,w-2-len(mods[0][0]))]
        self._b_put(y,x,text,color,active,width=w)
        if tall:self._b_mod_draw(y+2,x+2,w-2,u)
        elif mods:self._b_mod_draw(y,x+len(text)+2,w-len(text)-2,u)
        hp=f'HP {max(0,u.hp):g}/{u.max_hp:g}'
        sp=f'SP {max(0,u.sp):g}/{u.max_sp:g}'
        gun=f'  •{u.ammo}' if getattr(u,'max_ammo',0) else ''
        if w>=45:
            self._b_put(y+1,x+2,hp,RED if u.hp<=u.max_hp*.3 else DIM)
            self._b_hp_draw(y+1,x+15,u,10,now)
            self._b_put(y+1,x+28,sp+gun,DIM,width=w-28)
        else:
            self._b_put(y+1,x+2,f'{hp}   {sp}',RED if u.hp<=u.max_hp*.3 else DIM,width=w-8)
            self._b_hp_draw(y+1,x+w-5,u,5,now)

    def _b_action_menu(self):
        b=self._b_battle
        caps=[
            ('skills','Persona','Open skills; Joker can cycle Personas with ←/→.'),
            ('attack','Attack','Strike one Shadow without spending SP.'),
            ('gun','Gun','Use ammunition to exploit gun affinity.'),
            ('guard','Guard','Brace until this fighter’s next turn.'),
            ('items','Items','Use the squad’s shared supplies.'),
            ('baton','Baton Pass','Hand your extra action to another teammate.'),
            ('allout','All-Out Attack','Finish a Hold Up with a team strike.'),
            ('analyze','Analyze','Inspect a Shadow without spending this turn.'),
        ]
        rows=[]
        for cat,label,desc in caps:
            options=b.actions(cat)
            ok=bool(options)
            if cat=='allout' and ok:desc=options[0][2]
            rows.append((cat,label,desc if ok else b.command_block(cat),ok))
        extra=b.actions('story-special')
        if extra:
            cat,label,desc=extra[0]
            rows.append((cat,label,desc,True))
        shows=b.actions('showtime')
        if shows:
            cat,label,desc=shows[0]
            rows.append((cat,label,desc,True))
        return rows

    def _b_action_rows(self):
        return self._b_battle.actions(self._b_category,self._b_persona_view)

    def _b_weak_targets(self,aid):
        b=self._b_battle
        if not aid:return ()
        spec=b._spec(aid)
        if not spec or spec['kind']!='damage' or spec['target'] not in ('enemy','enemies'):return ()
        targets=b.targets(aid) if spec['target']=='enemy' else b.enemies
        return tuple(u for u in targets if u.alive and b.seen.get(u.name,{}).get(spec['element'])=='weak')

    def _b_turn_strip(self,y):
        b=self._b_battle
        if b.phase!='turn':return
        label=f'NOW {b.actor.name}'+(' +1' if b.one_more else '')+'   NEXT '
        self._b_put(y,3,label,CYAN,True)
        x=3+len(label)
        queue=list(b.upcoming_turns())
        for i,u in enumerate(queue):
            name=u.name
            if x+len(name)+(3 if i else 0)>self.w-3:break
            if i:self._b_put(y,x,' › ',DIM);x+=3
            self._b_put(y,x,name,RED if u.enemy else CYAN,i==0)
            x+=len(name)
        if not queue:self._b_put(y,x,'—',DIM)

    def _b_affinity_row(self,y,x,w,enemy=None):
        step=4 if w>=44 else 2
        info={} if enemy is None else self._b_battle.seen.get(enemy.name,{})
        for i,(element,abbr,color) in enumerate(ELEMENTS):
            if enemy is None:value=abbr
            else:value,color=AFFINITY[info.get(element,'unknown')]
            self._b_put(y,x+i*step,value,color,enemy is None or value in ('W','P','D'))

    def _b_arena(self):
        b=self._b_battle
        now=time.monotonic()
        self._b_hp_trails={u:a for u,a in self._b_hp_trails.items() if now-a[1]<HP_FLASH+HP_DRAIN+HP_SETTLE}
        if self._b_outgoing and now>=self._b_outgoing[2]:self._b_outgoing=None
        shown_wave,foes=(self._b_outgoing[:2] if self._b_outgoing else (b.wave,b.enemies))
        active=b.actor
        wide=self.w>=91
        split=max(32,(self.w-1)//2)
        footer='↑ ↓ SELECT   ENTER CONFIRM   ESC BACK   I STATUS   L LOG   ? HELP'
        if b.phase=='turn' and self._b_screen=='actions' and self._b_category=='skills':
            footer='↑ ↓ SKILL   ENTER SELECT   I STATUS   ESC BACK'
            if active.name=='Joker' and not b.shifted:
                footer='← → PERSONA   ↑ ↓ SKILL   ENTER SELECT   I STATUS   ESC BACK'
        self.frame('VELVET ROOM / SHADOW TRIAL',footer)
        self._b_put(3,3,'? Unknown · Normal W Weak R Resist N Null P Repel D Drain',DIM,width=self.w-6)
        wave_line=f'WAVE {shown_wave}/{b.wave_count}  •  '+('CLEARED' if self._b_outgoing else f'ROUND {b.round}   /   {b.difficulty.upper()}')
        if len(wave_line)>split-4 and not self._b_outgoing:
            wave_line=f'{shown_wave}/{b.wave_count}  ROUND {b.round}  {b.difficulty.upper()}'
        self._b_put(4,3,wave_line,GOLD,True,width=split-4)
        in_play=b.phase=='turn' and not self._b_outgoing
        boss_phase=getattr(b,'reaper_phase','') if in_play else ''
        boss_intent=(getattr(b,'story_intent','') or getattr(b,'reaper_intent','')) if in_play else ''
        encounter_width=self.w-split-3
        if boss_phase:
            label=f'{b.encounter}  /  {boss_phase}'
            if len(label)>encounter_width:label=boss_phase
            self._b_put(4,split,label,GOLD,True,width=encounter_width)
        else:
            self._b_put(4,split,b.encounter,CYAN,True,width=encounter_width)
        if not self._b_outgoing:self._b_turn_strip(5)
        self._b_heading(6,3,'PHANTOM THIEVES • '+b.persona,split-5)
        right=self.w-split-3
        self._b_put(6,split,'SHADOW FORMATION / AFFINITIES',CYAN,True,width=right)
        self._b_affinity_row(7,split,right)
        double=self.h>=31
        tall=wide and self.h>=37
        ally_step=3 if tall else 2 if double else 1
        enemy_step=3 if tall else 2
        for i,u in enumerate(b.allies):
            y=8+i*ally_step
            if double:self._b_unit_draw(y,3,split-5,u,u is active,now,tall)
            else:
                state=' KO' if not u.alive else ' ↓' if u.down else ' G' if u.guard else ''
                label=f'{"▶" if u is active else " "} {u.name:<8} {u.hp:g}H/{u.sp:g}S'+state
                mods=self._b_modifiers(u)
                if mods and len(label)+1+len(mods[0][0])>split-11:
                    label=f'{"▶" if u is active else " "} {u.name[:6]} {u.hp:g}H/{u.sp:g}S'+state
                self._b_put(y,3,label,RED if not u.alive else GOLD if u.down else CYAN if u is active else WHITE,u is active,width=split-11)
                self._b_mod_draw(y,4+len(label),split-12-len(label),u)
                self._b_hp_draw(y,split-7,u,5,now)
        picked_target=None
        if self._b_screen=='targets':
            targets=b.targets(self._b_id)
            if targets:picked_target=targets[min(self._b_index,len(targets)-1)]
        for i,u in enumerate(foes):
            y=8+enemy_step*i
            state=' KO' if not u.alive else ' ↓' if u.down else ' G' if u.guard else ''
            if u.status and right>=43:state+=' '+u.status.upper()
            prefix='▶ ' if u is picked_target else '  '
            hp=(f'  HP {u.hp}/{u.max_hp}' if right>=44 else f' {u.hp}H')+state
            bars=10 if right>=44 else 5
            bar_x=split+right-bars
            name=u.name[:max(1,right-bars-1-len(hp)-len(prefix))]
            self._b_put(y,split,prefix+name+hp,RED if not u.alive else GOLD if u.down else CYAN if u is picked_target else WHITE,u is picked_target,width=right)
            self._b_hp_draw(y,bar_x,u,bars,now)
            self._b_affinity_row(y+1,split,right,u)
            if tall:self._b_mod_draw(y+2,split+2,right-2,u)
            else:
                affinity_width=(4 if right>=44 else 2)*len(ELEMENTS)
                self._b_mod_draw(y+1,split+affinity_width+1,right-affinity_width-1,u)
        top=9+max(len(b.allies)*ally_step,len(foes)*enemy_step)
        if self._b_outgoing:
            self._b_put(top,3,'WAVE CLEARED  /  NEXT FORMATION INCOMING',GOLD,True,width=self.w-6)
            return
        if b.phase in ('win','loss'):
            self._b_result(top)
            return
        if boss_intent:
            limit=self.w-6
            text=('!  ' if len(boss_intent)+3<=limit else '')+boss_intent
            if len(text)>limit:text=text[:limit-1]+'…'
            self._b_put(top-1,3,text,RED,True,width=limit)
        label=f'{active.name.upper()}  /  COMMAND'
        if b.hold_up:label=f'HOLD UP!  /  ALL-OUT ATTACK: {b.allout_damage} DAMAGE'
        elif b.one_more:label=f'{active.name.upper()}  /  ONE MORE!   CHAIN {b.chain}'
        self._b_put(top,3,label,RED if b.hold_up else GOLD if b.one_more else CYAN,True,width=(split-5 if wide else self.w-6))
        if wide:
            self._b_heading(top,split,getattr(b,'navigator','Oracle').upper()+' / BATTLE LOG',self.w-split-3)
        start=top+2
        end=self.h-6
        h=max(1,end-start+1)
        commands=self._b_action_menu()
        if self._b_screen=='command':
            menu=[(label,help,ok) for cat,label,help,ok in commands]
        elif self._b_screen=='actions':
            menu=[]
            for aid,action_label,detail in self._b_action_rows():
                reason=b.action_block(aid,persona=self._b_persona_view,pick_target=True) if aid.startswith(('skill:','item:')) else None
                weak=self._b_weak_targets(aid)
                if weak:action_label+=' [WEAK]'
                spec=b._spec(aid)
                if weak and spec and spec['target']=='enemies':detail='Weak: '+', '.join(u.name for u in weak)
                menu.append((action_label,reason or detail,not reason))
            category=self._b_category.upper()
            if self._b_category=='skills':
                name=(self._b_persona_view or b.persona) if active.name=='Joker' else self._b_team[active.name]['persona']
                category='PERSONA: '+name
                if active.name=='Joker' and name!=b.persona:
                    self._b_put(top+1,3,'Equips when you use a skill.',DIM,width=(split-5 if wide else self.w-6))
            self._b_put(top,3,active.name.upper()+' / '+category+(' / ONE MORE!' if b.one_more else ''),GOLD if b.one_more else CYAN,True,width=split-5 if wide else self.w-6)
        else:
            targets=b.targets(self._b_id)
            menu=[]
            for u in targets:
                reason=None if self._b_id=='analyze' else b.action_block(self._b_id,u,self._b_persona_view)
                detail=f'HP {u.hp:g}/{u.max_hp:g}   SP {u.sp:g}/{u.max_sp:g}'+('   DOWN' if u.down else '')
                title=('[WEAK] ' if u in self._b_weak_targets(self._b_id) else '')+u.name
                menu.append((title,reason or detail,not reason))
            self._b_put(top,3,'TARGET  /  '+self._b_action_title+(' / ONE MORE!' if b.one_more else ''),GOLD,True,width=(split-5 if wide else self.w-6))
        context=picked_target if self._b_screen=='targets' else active
        if not tall and context and self._b_modifiers(context) and not (
           self._b_screen=='actions' and self._b_category=='skills' and self._b_persona_view not in (None,b.persona)
        ):
            self._b_mod_draw(top+1,3,split-5 if wide else self.w-6,context)
        w=split-5 if wide else self.w-6
        picked=self._b_list(menu,start,3,w,h,self._b_index)
        if wide:
            for y in range(top+2,self.h-4):
                self._b_put(y,split-3,'│',DIM)
            self._b_log_draw(start,split,self.w-split-3,h+1)
        if self._b_message or (picked and not picked[2]):
            self._b_par(self.h-5,3,'BLOCKED: '+(self._b_message or picked[1]),self.w-6,2,GOLD)
        else:
            if not wide and b.log and self.h-5>end:
                self._b_put(self.h-5,3,str(b.log[-1]),WHITE,width=self.w-6)
            self._b_put(self.h-4,3,picked[1] if picked else '',DIM,width=self.w-6)

    def _b_log_draw(self,y,x,w,count,offset=0):
        lines=[]
        for msg in self._b_battle.log:
            segments=textwrap.wrap(str(msg),max(8,w-2)) or ['']
            color=GOLD if any(p in str(msg).casefold() for p in ('weak','critical','technical','one more','hold up','baton')) else DIM
            lines.extend((('· ' if i==0 else '  ')+v,color) for i,v in enumerate(segments))
        top=min(max(0,len(lines)-count-offset),max(0,len(lines)-count))
        for i,(msg,col) in enumerate(lines[top:top+count]):
            self._b_put(y+i,x,msg,col,width=w)

    def _b_result(self,top):
        b=self._b_battle
        win=b.phase=='win'
        self._b_put(top,3,'◆  TRIAL CLEARED' if win else '◆  SQUAD DEFEATED',GREEN if win else RED,True,width=self.w-6)
        self._b_par(top+2,3,
            'The Shadows are down. The Velvet Room records your victory.' if win else
            'Joker can’t continue. Try another squad, guard against weaknesses, or change your Persona.',
            self.w-6,2,WHITE)
        self._b_put(top+5,3,'ENTER  REMATCH      S  SQUAD SETUP      L  BATTLE LOG',GOLD,True,width=self.w-6)
        if b.log and top+7<self.h-4:self._b_put(top+7,3,str(b.log[-1]),DIM,width=self.w-6)

    def _b_over(self):
        b=self._b_battle
        if self._b_overlay=='log':
            self.frame(getattr(b,'navigator','Oracle').upper()+' / BATTLE LOG','↑ ↓ / PGUP PGDN SCROLL   ESC BACK')
            self._b_log_draw(4,3,self.w-6,self.h-8,self._b_log_scroll)
        elif self._b_overlay=='status':
            self.frame(getattr(b,'navigator','Oracle').upper()+' / FIELD STATUS','ESC OR I BACK   •   ↑ BUFF / ↓ DEBUFF   •   NUMBER = OWN TURNS LEFT')
            self._b_put(4,3,'PHANTOM THIEVES',CYAN,True)
            y=5
            for roster in (b.allies,b.enemies):
                if roster is b.enemies:
                    y+=1
                    self._b_put(y,3,'SHADOW FORMATION',RED,True)
                    y+=1
                for u in roster:
                    state='KO' if not u.alive else '  '.join(
                        item for item in ('DOWN' if u.down else '', 'GUARD' if u.guard else '',str(u.status).upper()) if item
                    )
                    x=3
                    name=f'{u.name:<18}'
                    self._b_put(y,x,name,WHITE,True,width=18)
                    flags=f'HP {u.hp}/{u.max_hp}  SP {u.sp}/{u.max_sp}'
                    self._b_put(y,22,flags,DIM,width=self.w-25)
                    if state:self._b_put(y+1,3,state,GOLD,width=18)
                    if self._b_modifiers(u):self._b_mod_draw(y+1,22,self.w-25,u)
                    y+=2
            if y<self.h-4:
                p=getattr(b,'reaper_phase','')
                q=getattr(b,'reaper_intent','')
                if b.phase=='turn' and (p or q):
                    self._b_par(y+1,3,'  /  '.join(i for i in (p,q) if i),self.w-6,2,GOLD)
                else:
                    self._b_par(y+1,3,'One More and Baton Pass are bonus actions, not additional turns on the clock.',self.w-6,2)
        elif self._b_overlay=='intel':
            self.frame(getattr(b,'navigator','Oracle').upper()+' / AFFINITY SCAN','ESC BACK   •   ANALYZE DOES NOT CONSUME YOUR TURN')
            target=self._b_analyzed
            self._b_heading(4,3,target.name.upper(),self.w-6)
            self._b_put(6,3,f'HP {target.hp}/{target.max_hp}   SP {target.sp}/{target.max_sp}',WHITE)
            self._b_mod_draw(7,3,self.w-6,target)
            info=b.seen.get(target.name,{})
            spacing=max(17,(self.w-8)//3)
            for i,(e,_,_) in enumerate(ELEMENTS):
                v=info.get(e,'unknown')
                color=GOLD if v=='weak' else DIM if v=='unknown' else CYAN
                self._b_put(9+i//3*2,3+(i%3)*spacing,f'{e.upper():<9} {v.upper()}',color,width=spacing-1)
            self._b_par(19,3,'Unobserved affinities remain unknown. Test elements carefully: a Shadow can block, repel or drain them.',self.w-6,2)
        elif self._b_overlay=='help':
            self.frame(getattr(b,'navigator','Oracle').upper()+' / TACTICS','ESC BACK')
            topics=[
                ('PERSONA SWITCH','Open Persona on Joker’s turn. Use ←/→ to cycle Personas and see their skills. Using a skill equips that Persona. Esc cancels.'),
                ('ONE MORE','A fresh knockdown or weakness KO on a standing Shadow earns One More. Hits on already-downed targets don’t.'),
                ('BATON PASS','Hand an extra action to an eligible ally. Chain different teammates to boost damage.'),
                ('HOLD UP','Down every living Shadow. Joker must be standing for an All-Out Attack; more allies standing means more damage.'),
                ('SURVIVE','Watch your own affinities. Guard before enemy pressure, heal early, and save SP for openings.'),
                ('ANALYZE','Inspect a Shadow’s known affinities without spending your turn. Discover the rest by trying elements.'),
            ]
            line=5
            for title,detail in topics:
                self._b_put(line,3,title,GOLD,True)
                self._b_par(line+1,3,detail,self.w-6,2,WHITE)
                line+=4 if self.h>=30 else 3
        else:
            abandon=self._b_overlay=='abandon'
            title='END THIS TRIAL?' if abandon else 'RETURN TO SAFE ROOM?'
            self.frame('VELVET ROOM / PAUSED','ENTER CONFIRM   ESC STAY')
            self.mid(7,title,GOLD,True)
            self._b_par(10,3,'The current fight ends. Choose a new squad or deploy again.' if abandon else
                 'Your current fight stays paused. Open Velvet Room again to pick up where you left off.',
                 self.w-6,3,WHITE)

    def draw_cutin(self,title,elapsed=0.0):
        """Only paint the animation. Names and controls belong to the menu."""
        scene=cinema.get(title)
        if not scene:
            # Defensive fallback for unknown future events, with no captions.
            size=max(1,min(18,int(elapsed*18)+1))
            for dy in (-2,-1,0,1,2):
                self._b_put(self.h//2+dy,self.w//2-size-1,'*',GOLD)
                self._b_put(self.h//2+dy,self.w//2+size+1,'*',GOLD)
            return
        _,rows=scene[1](elapsed)
        inks={'queen':CYAN,'noir':GOLD,'foe':RED,'rope':DIM,
              'rail':RED,'face':WHITE,'dim':DIM,'flash':GOLD,
              'red':RED,'gold':GOLD,'cyan':CYAN,'green':GREEN,'white':WHITE}
        left=(self.w-SCENE_COLUMNS)//2
        top=(self.h-SCENE_ROWS)//2
        for y,row in enumerate(rows,top):
            x=left
            for run,ink in row:
                if run.strip():self._b_put(y,x,run,inks[ink],ink not in ('dim','rope'))
                x+=len(run)

    def battle_page(self):
        self._b_ensure()
        now=time.monotonic()
        if self._b_cut_in and now>=self._b_cut_in[3]:
            self._b_release_cut(now)
        if self._b_overlay:
            self._b_over()
        elif self._b_cut_in:
            title,_,started,_=self._b_cut_in
            self.draw_cutin(title,now-started)
        elif self._b_screen=='setup':
            self._b_setup_draw()
        else:
            self._b_arena()

    def _b_record_damage(self,events,now):
        for unit,before,_ in events:
            prior,start=self._b_hp_trails.get(unit,(before,-1))
            if now-start>=HP_FLASH+HP_DRAIN:prior=before
            self._b_hp_trails[unit]=(max(prior,before),now)

    def _b_prepare_presentation(self,b,now):
        self._b_hp_trails.clear()
        self._b_outgoing=None
        self._b_cut_in=None
        self._b_cut_damage=None
        self._b_cut_queue=[]
        self._b_present_action(b,b.wave,b.enemies,now)

    def _b_show_damage(self,events,old_wave,old_foes,now):
        self._b_record_damage(events,now)
        if self._b_battle.wave!=old_wave and any(foe in self._b_hp_trails for foe in old_foes):
            self._b_outgoing=(old_wave,old_foes,now+HP_FLASH+HP_DRAIN+HP_SETTLE)

    def _b_start_cut(self,card,now):
        self._b_cut_in=(*card,now,now+cutin_duration(card[0]))

    def _b_present_action(self,b,old_wave,old_foes,now):
        cut=getattr(b,'cut_in',None)
        if cut:
            self._b_cut_queue=list(getattr(b,'cut_in_queue',()))
            self._b_cut_damage=(tuple(b.damage_events),old_wave,old_foes)
            self._b_start_cut(cut,now)
        else:
            self._b_show_damage(b.damage_events,old_wave,old_foes,now)

    def _b_release_cut(self,now):
        if self._b_cut_queue:
            self._b_start_cut(self._b_cut_queue.pop(0),now)
            return
        self._b_cut_in=None
        if self._b_cut_damage:
            events,wave,foes=self._b_cut_damage
            self._b_cut_damage=None
            self._b_show_damage(events,wave,foes,now)

    def _b_result_animation(self,now):
        return (self._b_cut_in is not None
                or self._b_outgoing is not None and now<self._b_outgoing[2]
                or any(u.hp<before and now-start<HP_FLASH+HP_DRAIN+HP_SETTLE
                       for u,(before,start) in self._b_hp_trails.items()))

    def _b_apply(self,aid,target=None):
        b=self._b_battle
        old=b.actor
        old_wave,old_foes=b.wave,b.enemies
        error=b.act(aid,target,persona=self._b_persona_view if self._b_category=='skills' else None)
        if error:
            self._b_message=error
            return
        now=time.monotonic()
        self._b_present_action(b,old_wave,old_foes,now)
        self._b_screen='command'
        self._b_persona_view=None
        self._b_index=0 if self._b_battle.actor is not old else self._b_saved_index
        self._b_id=None
        self._b_message=''
        if aid=='analyze' and target is not None:
            self._b_analyzed=target;self._b_overlay='intel'

    def _b_chosen(self,category,aid,label):
        b=self._b_battle
        if aid.startswith(('skill:','item:')) or aid in ('attack','gun'):
            reason=b.action_block(aid,persona=self._b_persona_view,pick_target=True)
            if reason:
                self._b_message=reason
                return
        targets=b.targets(aid)
        if targets:
            self._b_category=category
            self._b_id=aid
            self._b_action_title=label
            self._b_screen='targets'
            self._b_index=0
        else:
            self._b_apply(aid)

    def battle_key(self,k):
        self._b_ensure()
        if self._b_cut_in:
            now=time.monotonic()
            if now>=self._b_cut_in[3] or k in ENTER or k==ESC or k==' ':
                self._b_release_cut(now)
            return True  # Skip presentation only; never process a second action.
        if self._b_outgoing and time.monotonic()<self._b_outgoing[2]:return True
        b=self._b_battle
        kl=k.lower() if isinstance(k,str) else k
        if self._b_overlay:
            overlay=self._b_overlay
            if k==ESC or overlay=='intel' and k in ENTER or overlay=='status' and kl=='i' or overlay=='log' and kl=='l' or overlay=='help' and k in ('?','h','H'):
                self._b_overlay=None
                return True
            if overlay=='log':
                if k in (C.KEY_UP,C.KEY_DOWN,C.KEY_PPAGE,C.KEY_NPAGE):
                    step={C.KEY_UP:1,C.KEY_DOWN:-1,C.KEY_PPAGE:8,C.KEY_NPAGE:-8}[k]
                    self._b_log_scroll=max(0,min(max(0,len(b.log)*2-1),self._b_log_scroll+step))
            elif overlay in ('resume','abandon') and k in ENTER:
                self._b_overlay=None
                if overlay=='resume':
                    self.page=-1
                else:
                    self._b_screen='setup'
                    self._b_battle=None
                    self._b_index=0
                    self._b_message=''
            return True
        if self._b_screen=='setup':
            if k==ESC:
                self.page=-1
                return True
            if k in (C.KEY_LEFT,C.KEY_RIGHT):
                self._b_trial=(self._b_trial+(1 if k==C.KEY_RIGHT else -1))%len(self._b_trial_names)
                self._b_message=''
            elif kl=='d':
                self._b_diff=(self._b_diff+1)%len(self._b_levels)
            elif kl=='s':
                self._b_launch()
            else:
                self._b_index=self._b_nav(k,self._b_index,len(self._b_roster))
                choose=self._b_commit(k,self._b_index,len(self._b_roster))
                if choose is not None:
                    self._b_index=choose
                    name=self._b_roster[choose]
                    if self._b_trials[self._b_trial_names[self._b_trial]].get('party_size',4)==1:
                        self._b_message='This trial is solo. Your selected squad is unchanged.'
                    elif name in self._b_selected:
                        self._b_selected.remove(name)
                        self._b_message=f'{name} moved to standby.'
                    elif len(self._b_selected)<3:
                        self._b_selected.append(name)
                        self._b_message=f'{name} joins the active squad.'
                    else:
                        self._b_message='Squad full. Toggle an active ally off first.'
            return True
        if kl=='i':
            self._b_overlay='status'
            return True
        if kl=='l':
            self._b_overlay='log'
            self._b_log_scroll=0
            return True
        if kl in ('h','?'):
            self._b_overlay='help'
            return True
        if b.phase in ('win','loss'):
            if k in ENTER or kl=='r':self._b_launch()
            elif k==ESC:
                self._b_battle=None;self._b_screen='setup';self._b_index=0;self.page=-1
            elif kl=='s':
                self._b_battle=None;self._b_screen='setup';self._b_index=0;self._b_message=''
            return True
        if kl=='r':
            self._b_overlay='abandon'
            return True
        if k in (C.KEY_LEFT,C.KEY_RIGHT) and self._b_screen=='actions' and self._b_category=='skills':
            if b.actor.name=='Joker' and not b.shifted:
                order=list(self._b_personas)
                direction=1 if k==C.KEY_RIGHT else -1
                self._b_persona_view=order[(order.index(self._b_persona_view or b.persona)+direction)%len(order)]
                self._b_index=0
                self._b_message=''
            return True
        if k==ESC or k==C.KEY_LEFT:
            if self._b_screen=='targets':
                self._b_screen=self._b_target_back
                self._b_index=self._b_target_back_index
            elif self._b_screen=='actions':
                self._b_screen='command'; self._b_index=self._b_saved_index
                self._b_persona_view=None
            elif k==ESC:
                self._b_overlay='resume'
            self._b_message=''
            return True
        if self._b_screen=='command':
            rows=self._b_action_menu()
            old_index=self._b_index
            self._b_index=self._b_nav(k,self._b_index,len(rows))
            if old_index!=self._b_index:self._b_message=''
            choose=next((i for i,row in enumerate(rows) if row[0]=='showtime'),None) if kl=='t' else self._b_commit(k,self._b_index,len(rows))
            if choose is None:return True
            cat,label,_,ok=rows[choose]
            self._b_index=self._b_saved_index=choose
            if not ok:
                self._b_message=b.command_block(cat)
                return True
            self._b_message=''
            if cat in ('attack','gun','guard','analyze','allout','story-special','showtime') and len(b.actions(cat))==1:
                aid,atitle,_=b.actions(cat)[0]
                self._b_target_back='command'
                self._b_target_back_index=choose
                self._b_chosen(cat,aid,atitle)
            else:
                self._b_category=cat
                self._b_persona_view=b.persona if cat=='skills' and b.actor.name=='Joker' else None
                self._b_screen='actions'
                self._b_index=0
        elif self._b_screen=='actions':
            rows=self._b_action_rows()
            old_index=self._b_index
            self._b_index=self._b_nav(k,self._b_index,len(rows))
            if old_index!=self._b_index:self._b_message=''
            choose=self._b_commit(k,self._b_index,len(rows))
            if choose is not None and rows:
                self._b_index=choose
                self._b_target_back='actions'
                self._b_target_back_index=choose
                aid,title,_=rows[choose]
                self._b_chosen(self._b_category,aid,title)
        else:
            rows=b.targets(self._b_id)
            old_index=self._b_index
            self._b_index=self._b_nav(k,self._b_index,len(rows))
            if old_index!=self._b_index:self._b_message=''
            choose=self._b_commit(k,self._b_index,len(rows))
            if choose is not None and rows:
                self._b_index=choose
                self._b_apply(self._b_id,rows[choose])
        return True
