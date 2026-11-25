"""Velvet Room battle interface. Simulation rules live in battle.py."""
import curses as C
import textwrap
import time
from cutins import CutCue, duration as cutin_duration
import cinema
from reel_palette import IDS as SCENE_PIGMENTS
from combat_palette import P5_MARKS

RED,GOLD,CYAN,WHITE,DIM,GREEN=range(1,7)
ENTER=(C.KEY_ENTER,'\r','\n')
ESC='\x1b'
ELEMENTS=tuple((element,element[:2],ink) for element,(_,ink) in P5_MARKS.items())
AFFINITY={
    'unknown':('?',DIM),'normal':('·',WHITE),'weak':('W',GOLD),
    'resist':('R',CYAN),'null':('N',CYAN),'repel':('P',RED),'drain':('D',GREEN),
}
HP_FLASH=0.24
HP_DRAIN=0.42
HP_SETTLE=0.12
FEEDBACK_HOLD=1.16
SHORT_REPEAT_RATE=1.8
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

    def _b_list(self,rows,y,x,w,h,idx,shortcut=True,details=True,marks=()):
        """Rows are (title, detail, enabled); return selected row."""
        if not rows:
            self._b_put(y,x,'Nothing available.',DIM,width=w)
            return
        i=max(0,min(idx,len(rows)-1))
        step=2 if details and h>=len(rows)*2 and self.w>=78 else 1
        visible=max(1,h//step)
        start=min(max(0,i-visible//2),max(0,len(rows)-visible))
        for n,row in enumerate(rows[start:start+visible],start):
            title,detail,enabled=row
            a=n==i
            p=('▶' if a else ' ')+' '+((f'{n+1:>2} ' if n<9 else '   ') if shortcut else '')
            color=CYAN if a else WHITE if enabled else DIM
            row_y=y+(n-start)*step
            mark=marks[n] if marks else None
            if mark:
                glyph,ink=mark
                room=max(0,w-len(p)-2)
                name,sep,badges=title.partition(' [')
                badge=(sep+badges)[:room]
                name=name[:max(0,room-len(badge))]
                self._b_put(row_y,x,p,color,a,a,width=w)
                self._b_put(row_y,x+len(p),name,ink,a)
                self._b_put(row_y,x+len(p)+len(name),badge,WHITE if enabled else DIM)
                self._b_put(row_y,x+len(p)+len(name)+len(badge)+1,glyph,ink,a)
            elif not enabled:
                self._b_put(row_y,x,p,color,a,a,width=w)
                self._b_put(row_y,x+len(p),title,DIM,width=w-len(p))
            else:
                line=(p+title)[:w].ljust(w)
                self._b_put(row_y,x,line,color,a,a,width=w)
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
        self._b_feedback={}
        self._b_feedback_until=0.0
        self._b_outgoing=None
        self._b_cut_in=None
        self._b_cut_damage=None
        self._b_cut_queue=[]
        self._b_battle_cuts=set()
        self._b_intermediate_wave=False
        self._b_final_action=False
        self._b_offer_short_repeats=False
        # Playback preferences and completed first views are app-session
        # presentation only, not combat state or a save field.
        if not hasattr(self,'_b_finished_cuts'):
            self._b_finished_cuts=set()
            self._b_short_repeats=False

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
        a,x=3,self.w//2+1
        left=x-a-2 if wide else self.w-6
        right=self.w-x-3
        meta=self._b_trial_names[self._b_trial]
        trial=self._b_trials[meta]
        needed=trial.get('party_size',4)-1
        footer='←→ TRIAL  D DIFFICULTY  S DEPLOY  ESC MAP'
        if needed:footer='↑↓ ALLY  ↵ TOGGLE  '+footer
        self.frame('VELVET ROOM / SQUAD',footer)
        count=trial.get('wave_count',len(trial.get('waves') or []))
        waves='Waves vary' if not count else '1 wave' if count==1 else f'{count} waves'
        if trial.get('shuffle_count'):
            waves+=f' · {trial["shuffle_count"]} random Shadows'
        overview=f'{self._b_levels[self._b_diff]} · {waves}'
        self._b_heading(4,a,f'TEAM  {len(self._b_selected)}/{needed}  +  JOKER' if needed else 'JOKER ONLY',left)
        if needed:
            rows=[]
            for name in self._b_roster:
                record=self._b_team[name]
                health=f'  HP {record["hp"]} / SP {record["sp"]}' if wide else ''
                rows.append((f'{"●" if name in self._b_selected else "○"} {name:<8} {record.get("persona","")}{health}',record.get('role',''),True))
            picked=self._b_list(rows,6,a,left,max(1,(self.h-12 if wide else min(8,self.h-17))),self._b_index,details=False)
            if picked and picked[1]:
                self._b_par(self.h-7 if wide else 14,a,picked[1],left,2 if wide else 1,GOLD)
        else:
            self._b_par(6,a,'No allies or Baton Pass in this trial.',left,1,WHITE)
        ty,tx,tw=(4,x,right) if wide else (16 if needed else 9,a,left)
        self._b_heading(ty,tx,meta,tw)
        self._b_put(ty+2,tx,overview,WHITE,width=tw)
        self._b_par(ty+3,tx,trial.get('hint',''),tw,3 if wide or not needed else min(2,max(1,self.h-ty-8)))
        if self._b_message:self._b_put(self.h-4,3,self._b_message,GOLD,width=self.w-6)

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

    def _b_feedback_parts(self,u):
        return self._b_feedback.get(u,())

    def _b_feedback_draw(self,y,x,w,u):
        parts=self._b_feedback_parts(u)
        if not parts or w<=0:return
        label=' · '.join(parts)
        if len(label)>w:
            short={'CRITICAL':'CRIT','TECHNICAL':'TECH','RESIST':'RES','REVIVED':'REV'}
            label=' '.join(short.get(part,part) for part in parts)
        if len(label)>w:
            visible=[]
            for token in label.split():
                if len(' '.join((*visible,token)))>w:break
                visible.append(token)
            label=' '.join(visible)
        if label:self._b_put(y,x,label,GOLD,True,width=w)

    def _b_sp_draw(self,y,x,u,w):
        fill=max(int(u.sp>0),min(w,round(w*u.sp/max(1,u.max_sp))))
        if fill:self._b_put(y,x,'█'*fill,GOLD if u.sp<=u.max_sp*.2 else CYAN)
        if fill<w:self._b_put(y,x+fill,'░'*(w-fill),DIM)

    def _b_unit_draw(self,y,x,w,u,active=False,now=0,tall=False):
        states=[]
        if u.hp<=0:states.append('KO')
        if u.down and u.hp>0:states.append('DOWN')
        if u.guard and u.hp>0:states.append('GUARD')
        if u.status and u.hp>0:states.append(str(u.status).upper())
        name=f'{"▶" if active else " "} {u.name}'
        text=name+('  ['+' / '.join(states)+']' if states else '')
        color=RED if u.hp<=0 else GOLD if u.down or u.status else CYAN if active else WHITE
        hp=f'{max(0,u.hp):g}/{u.max_hp:g}'
        sp=f'{max(0,u.sp):g}/{u.max_sp:g}'
        low_hp=u.hp<=u.max_hp*.3
        low_sp=u.sp<=u.max_sp*.2
        parts=self._b_feedback_parts(u)
        side_at=max(14,len(text)+2) if tall else len(text)+2
        if parts and side_at+6>w:
            text=name+(' KO' if not u.alive else ' ↓' if u.down else '')
            side_at=len(text)+2
        self._b_put(y,x,text,color,active,width=w)
        if tall:
            run=min(17,max(5,w//3))
            hp_color=RED if low_hp else WHITE
            self._b_put(y+1,x+2,'HP '+hp,hp_color,width=11)
            self._b_hp_draw(y+1,x+13,u,run,now)
            self._b_put(y+2,x+2,'SP '+sp,GOLD if low_sp else WHITE,width=11)
            self._b_sp_draw(y+2,x+13,u,run)
            readout=13+run+2
            if parts:
                self._b_feedback_draw(y,x+side_at,w-side_at,u)
                self._b_mod_draw(y+1,x+readout,w-readout,u)
            else:self._b_mod_draw(y,x+side_at,w-side_at,u)
            if u.max_ammo and w-readout>=5:self._b_put(y+2,x+readout,f'▪ {u.ammo}/{u.max_ammo}',DIM,width=w-readout)
        else:
            half=(w-1)//2
            digits=11 if half>=15 else 10
            self._b_put(y+1,x,('HP ' if digits==11 else 'HP')+hp,RED if low_hp else WHITE,width=digits)
            self._b_hp_draw(y+1,x+digits,u,half-digits,now)
            self._b_put(y+1,x+half+1,('SP ' if digits==11 else 'SP')+sp,GOLD if low_sp else WHITE,width=digits)
            self._b_sp_draw(y+1,x+half+1+digits,u,w-half-1-digits)
            if parts:self._b_feedback_draw(y,x+side_at,w-side_at,u)
            else:self._b_mod_draw(y,x+side_at,w-side_at,u)

    def _b_action_menu(self):
        b=self._b_battle
        caps=[
            ('skills','Persona','Spend HP or SP on skills.'),
            ('attack','Attack',''),
            ('gun','Gun',f'{b.actor.ammo}/{b.actor.max_ammo} rounds left.'),
            ('guard','Guard','Brace until this fighter’s next turn.'),
            ('items','Items',''),
            ('baton','Baton Pass','Pass One More, then hit an opening on another Shadow.'),
            ('allout','All-Out Attack',''),
            ('analyze','Analyze','Inspect a Shadow without spending this turn.'),
        ]
        rows=[]
        for cat,label,desc in caps:
            options=b.actions(cat)
            ok=bool(options)
            if cat=='allout' and ok:desc=options[0][2]
            reason=b.action_block(cat,pick_target=True) if cat in ('attack','gun') and ok else None
            rows.append((cat,label,reason or (desc if ok else b.command_block(cat)),ok and not reason))
        extra=b.actions('story-special')
        if extra:
            cat,label,desc=extra[0]
            rows.append((cat,label,desc,True))
        shows=b.actions('showtime')
        if shows:
            cat,label,desc=shows[0]
            rows.append((cat,label,desc,True))
        contracts=b.actions('contract')
        if contracts:
            cat,label,desc=contracts[0]
            rows.append((cat,label,desc,True))
        return rows

    def _b_action_rows(self):
        return self._b_battle.actions(self._b_category,self._b_persona_view)

    def _b_attack_element(self,aid):
        if aid=='allout':return 'Almighty'
        spec=self._b_battle._spec(aid)
        return spec.get('element') if spec and spec['kind']=='damage' else None

    _B_EFFECTS=('drain','repel','null','weak')

    def _b_known_targets(self,aid):
        """Affinities already learned by resolving hits; never enemy internals."""
        b=self._b_battle
        spec=b._spec(aid) if aid else None
        if not spec or spec['kind']!='damage' or spec['target'] not in ('enemy','enemies'):
            return {}
        units=b.targets(aid) if spec['target']=='enemy' else getattr(b,'visible_enemies',b.enemies)
        return {u:b.seen.get(u.name,{}).get(spec['element']) for u in units if u.alive}

    @staticmethod
    def _b_defense(affinity,width):
        values=' '.join(abbr+AFFINITY[affinity[element]][0]
            for element,abbr,_ in ELEMENTS if affinity.get(element) not in (None,'normal')
            and affinity[element] in AFFINITY) or 'Normal'
        # Seven tags fit in 27 columns if the optional heading is omitted.
        return 'DEF: '+values if len(values)+5<=width else values

    def _b_label_effects(self,label,effects,width):
        tags=[]
        for effect in self._B_EFFECTS:
            if effect in effects:
                tag=f'[{effect.upper()}]'
                if len(' '.join([*tags,tag]))<=width-min(12,len(label))-1:tags.append(tag)
        markers=' '.join(tags)
        if markers:return label[:width-1-len(markers)]+' '+markers
        return label

    def _b_turn_strip(self,y):
        b=self._b_battle
        if b.phase!='turn':return
        queue=list(b.upcoming_turns())
        following='NEXT REGULAR' if b.one_more and queue and queue[0] is b.actor else 'NEXT'
        label=f'NOW {b.actor.name}'+(' +1' if b.one_more else '')+f'   {following} '
        self._b_put(y,3,label,CYAN,True)
        x=3+len(label)
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
        if now>=self._b_feedback_until:self._b_feedback.clear()
        shown_wave,foes=(self._b_outgoing[:2] if self._b_outgoing else (b.wave,getattr(b,'visible_enemies',b.enemies)))
        active=b.actor
        wide=self.w>=91
        split=max(32,(self.w-1)//2)
        nav='↑↓ SELECT  ↵ CONFIRM'
        trial=getattr(self,'page',None)=='trials'
        if self._b_outgoing or b.phase=='interlude' or b.phase!='turn' and not trial:
            footer=''
        elif b.phase!='turn':
            footer='↵ REMATCH  S SQUAD  L LOG  ESC MAP'
        elif self._b_screen=='command':
            restart='R RESET' if trial else 'R RETRY'
            if self._b_offer_short_repeats:
                footer='↑↓ PICK  ↵ USE  I STATUS  L LOG  C SHORT REPEATS  ESC MAP'
            else:
                footer=f'↑↓ SELECT  ↵ USE  I STATUS  L LOG  ? HELP  {restart}  ESC MAP'
        else:
            switch='←→ PERSONA  ' if self._b_screen=='actions' and self._b_category=='skills' and active.name=='Joker' and not b.shifted and len(self._b_personas)>1 else ''
            footer=f'{switch}{nav}  I STATUS  ESC BACK'
        self.frame('VELVET ROOM / SHADOW TRIAL' if trial else 'PALACE / COMBAT',footer)
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
        skill_view=(self._b_screen=='actions' and self._b_category=='skills'
                    or self._b_screen=='targets' and (self._b_id or '').startswith('skill:'))
        preview=self._b_persona_view if skill_view and active.name=='Joker' else None
        roster=(preview+(' / PREVIEW' if preview!=b.persona else ' / EQUIPPED')
                if preview else 'PHANTOM THIEVES • '+b.persona)
        self._b_heading(6,3,roster,split-5)
        if preview:
            # The paired preview heading and DEF stay on screen until confirming
            # a skill. Status still shows the unit's actual equipped defenses.
            affinity=self._b_personas[preview]['affinity']
            self._b_put(7,3,self._b_defense(affinity,split-5).ljust(split-5),CYAN,width=split-5)
        right=self.w-split-3
        stale=in_play and any(u.alive and u in b.stale_readings for u in foes)
        self._b_put(6,split,'AFFINITIES • READINGS CHANGED' if stale else 'SHADOW AFFINITIES',
                    GOLD if stale else CYAN,True,width=right)
        self._b_affinity_row(7,split,right)
        tall=self.h>=29
        ally_step=3 if tall else 2
        enemy_step=3 if self.h>=29 and 8+3*len(foes)<=self.h-9 else 2
        for i,u in enumerate(b.allies):
            y=8+i*ally_step
            self._b_unit_draw(y,3,split-5,u,u is active,now,tall)
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
            if enemy_step==3:
                self._b_affinity_row(y+1,split,right,u)
                if self._b_feedback_parts(u):
                    self._b_feedback_draw(y+2,split+2,right-2,u)
                else:self._b_mod_draw(y+2,split+2,right-2,u)
            elif self._b_feedback_parts(u):
                self._b_feedback_draw(y+1,split+2,right-2,u)
            else:
                self._b_affinity_row(y+1,split,right,u)
                affinity_width=(4 if right>=44 else 2)*len(ELEMENTS)
                self._b_mod_draw(y+1,split+affinity_width+1,right-affinity_width-1,u)
        after_rosters=8+max(len(b.allies)*ally_step,len(foes)*enemy_step)
        # Protect one menu row plus log/detail at the supported minimum height.
        # The optional blank spacer may vanish, never a command or a foe.
        tight=not tall or after_rosters+1>=self.h-6
        top=after_rosters+(not tight)
        if self._b_outgoing:
            self._b_put(top,3,'WAVE CLEARED  /  NEXT FORMATION INCOMING',GOLD,True,width=self.w-6)
            return
        if b.phase=='interlude':
            self._b_put(top,3,'WAVE CLEARED',GOLD,True,width=self.w-6)
            if b.log:self._b_log_draw(self.h-5,3,self.w-6,1)
            return
        if b.phase in ('win','loss'):
            if trial:self._b_result(top)
            return
        if boss_intent:
            limit=self.w-6
            text=('!  ' if len(boss_intent)+3<=limit else '')+boss_intent
            if len(text)>limit:text=text[:limit-1]+'…'
            self._b_put(3 if tight else top-1,3,text,RED,True,width=limit)
        bonus='HOLD UP!' if b.hold_up else (f'ONE MORE! · CHAIN {b.chain}' if b.one_more else '')
        start=top+1
        end=self.h-6
        h=max(1,end-start+1)
        w=split-5 if wide else self.w-6
        reaction='';marks=[];aimed=None
        if self._b_screen=='command':
            heading=bonus or 'COMMANDS'
            commands=self._b_action_menu()
            menu=[(label,help,ok) for cat,label,help,ok in commands]
            marks=[P5_MARKS.get(self._b_attack_element(cat)) if allowed else None for cat,_,_,allowed in commands]
        elif self._b_screen=='actions':
            menu=[]
            reactions=[]
            for aid,action_label,detail in self._b_action_rows():
                reason=b.action_block(aid,persona=self._b_persona_view,pick_target=True) if aid.startswith(('skill:','item:')) else None
                spec=b._spec(aid)
                known=self._b_known_targets(aid)
                mark=P5_MARKS.get(self._b_attack_element(aid))
                marks.append(mark)
                action_label=self._b_label_effects(action_label,known.values(),w-5-(2 if mark else 0))
                ui_effects=[]
                if spec and spec['target']=='enemies':
                    for effect in self._B_EFFECTS:
                        names=[u.name for u,affinity in known.items() if affinity==effect]
                        if names:
                            number=f' (+{len(names)-1})' if len(names)>1 else ''
                            ui_effects.append(f'{effect.title()}: {names[0]}{number}')
                reactions.append('  •  '.join(ui_effects))
                menu.append((action_label,reason or detail,not reason))
            if reactions:reaction=reactions[min(self._b_index,len(reactions)-1)]
            heading=self._b_category.upper()
            if self._b_category=='skills':
                name=(self._b_persona_view or b.persona) if active.name=='Joker' else self._b_team[active.name]['persona']
                if active.name=='Joker':heading='SKILLS'
                else:
                    heading=name
                    self._b_put(7,3,self._b_defense(active.affinity,split-5).ljust(split-5),CYAN,width=split-5)
        else:
            targets=b.targets(self._b_id)
            known=self._b_known_targets(self._b_id)
            menu=[]
            for u in targets:
                reason=None if self._b_id in ('analyze','contract') else b.action_block(self._b_id,u,self._b_persona_view)
                effect=known.get(u)
                title=(f'[{effect.upper()}] ' if effect in self._B_EFFECTS else '')+u.name
                menu.append((title,reason or '',not reason))
            heading=self._b_action_title+' → TARGET'
            aimed=self._b_attack_element(self._b_id)
        if bonus and self._b_screen!='command':heading+='  /  '+bonus
        more=f'{min(self._b_index+1,len(menu))}/{len(menu)}' if len(menu)>h else ''
        heading_width=w-(len(more)+1 if more else 0)
        if aimed in P5_MARKS:
            glyph,ink=P5_MARKS[aimed]
            self._b_put(top,3,f'{glyph} {heading}',ink,True,width=heading_width)
        else:
            self._b_put(top,3,heading,RED if b.hold_up else GOLD if b.one_more else CYAN,True,width=heading_width)
        if more:self._b_put(top,3+w-len(more),more,DIM)
        picked=self._b_list(menu,start,3,w,h,self._b_index,details=False,marks=marks)
        if wide:
            self._b_heading(top,split,getattr(b,'navigator','Oracle').upper()+' / BATTLE LOG',self.w-split-3)
            for y in range(top+2,self.h-4):
                self._b_put(y,split-3,'│',DIM)
            self._b_log_draw(top+2,split,self.w-split-3,max(0,h-1))
        reason=self._b_message or (picked[1] if picked and not picked[2] else '')
        if reason:
            self._b_par(self.h-5 if len(reason)>self.w-6 else self.h-4,3,reason,self.w-6,2,GOLD)
        else:
            if reaction:
                self._b_put(self.h-5,3,reaction,GOLD,width=self.w-6)
            elif not wide and b.log:
                self._b_put(self.h-5,3,str(b.log[-1]),WHITE,width=self.w-6)
            hint=picked[1] if picked else ''
            if hint:self._b_put(self.h-4,3,hint,DIM,width=self.w-6)

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
        if not win:
            summary=b.defeat_diagnosis()
            for i,line in enumerate(summary):
                if top+1+i<self.h-4:self._b_put(top+1+i,3,line,WHITE,width=self.w-6)
        elif b.log and top+3<self.h-4:self._b_put(top+3,3,str(b.log[-1]),DIM,width=self.w-6)

    def _b_over(self):
        b=self._b_battle
        if self._b_overlay=='log':
            self.frame(getattr(b,'navigator','Oracle').upper()+' / BATTLE LOG','↑↓ SCROLL  ESC BACK')
            self._b_log_draw(4,3,self.w-6,self.h-8,self._b_log_scroll)
        elif self._b_overlay=='status':
            self.frame(getattr(b,'navigator','Oracle').upper()+' / FIELD STATUS','ESC BACK')
            cols=(self.w-6)//2
            foes=getattr(b,'visible_enemies',b.enemies)
            self._b_put(3,3,'DEF: W Weak · R Resist · N Null · P Repel · D Drain',DIM,width=self.w-6)
            for title,roster,x,color in (('PHANTOM THIEVES',b.allies,3,CYAN),('SHADOWS',foes,5+cols,RED)):
                self._b_put(4,x,title,color,True,width=cols-2)
                for i,u in enumerate(roster):
                    y=5+i*(4 if roster is b.allies else 3)
                    state='KO' if not u.alive else ' '.join(item for item in (
                        'DOWN' if u.down else '', 'GUARD' if u.guard else '', str(u.status).upper()) if item)
                    self._b_put(y,x,u.name+(f' [{state}]' if state else ''),WHITE,True,width=cols-2)
                    flags=f'HP {u.hp}/{u.max_hp}  SP {u.sp}/{u.max_sp}'
                    if getattr(u,'max_ammo',0):flags+=f'  GUN {u.ammo}'
                    self._b_put(y+1,x,flags,DIM,width=cols-2)
                    self._b_mod_draw(y+2,x,cols-2,u)
                    if roster is b.allies:
                        self._b_put(y+3,x,self._b_defense(u.affinity,cols-2),CYAN,width=cols-2)
            if any(self._b_modifiers(u) for u in (*b.allies,*foes)):
                self._b_put(self.h-4,3,'↑ Buff   ↓ Debuff   Number = turns left',DIM,width=self.w-6)
        elif self._b_overlay=='intel':
            self.frame(getattr(b,'navigator','Oracle').upper()+' / AFFINITY SCAN','ESC BACK')
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
        elif self._b_overlay=='elements':
            self.frame('ELEMENT COLORS','ESC TACTICS')
            col=(self.w-6)//3
            for idx,(element,(glyph,ink)) in enumerate(P5_MARKS.items()):
                row,x=divmod(idx,3)
                self._b_put(5+row*2,3+x*col,f'{glyph} {element}',ink,True,width=col)
        elif self._b_overlay=='help':
            controls='E ELEMENTS  ESC BACK'
            if getattr(b,'story',False):
                controls='C REPEATS: '+('SHORT' if self._b_short_repeats else 'FULL')+'  '+controls
            self.frame(getattr(b,'navigator','Oracle').upper()+' / TACTICS',controls)
            if getattr(b,'story',False):
                self._b_put(3,3,'Short speeds up seen clips. Final blows stay at full speed.',DIM,width=self.w-6)
            topics=[
                ('AFFINITIES','? Unknown · Normal W Weak R Resist N Null P Repel D Drain'),
                ('PERSONA SWITCH','Joker can preview skills without changing masks. Using one equips the new Persona.'),
                ('ONE MORE','A fresh knockdown or weakness KO on a standing Shadow earns One More. Hits on already-downed targets don’t.'),
                ('BATON PASS','Hand an extra action to an eligible ally. Chain different teammates to boost damage.'),
                ('HOLD UP','Down every living Shadow. Joker must be standing for an All-Out Attack; more allies standing means more damage.'),
                (('SHOWTIME','An eligible reserve partner can join. An incapacitated active partner cannot.')
                 if b.config.get('showtime_pairs') else
                 ('ANALYZE','Read known affinities without spending your turn. Try an element to learn its effect.')),
            ]
            line=4
            for title,detail in topics:
                self._b_put(line,3,title,GOLD,True)
                self._b_par(line+1,3,detail,self.w-6,2,WHITE)
                line+=4 if self.h>=30 else 3
        else:
            abandon=self._b_overlay=='abandon'
            title='END THIS TRIAL?' if abandon else 'RETURN TO SAFE ROOM?'
            self.frame('VELVET ROOM / PAUSED','↵ YES  ESC BACK')
            self.mid(7,title,GOLD,True)
            self._b_par(10,3,'Current trial progress will be lost.' if abandon else
                 'The current fight can be resumed.',
                 self.w-6,3,WHITE)

    def draw_cutin(self,title,elapsed=0.0,*,finishing=True,cast=(),targets=0):
        """Only paint the animation. Names and controls belong to the menu."""
        if not cinema.has(title):
            from battle_impact_art import draw_impact
            self.draw_scene_rows(draw_impact(elapsed,self.w-1,self.h))
            return
        _,rows=cinema.paint(title,elapsed,self.w-1,self.h,finishing=finishing,cast=cast,targets=targets)
        self.draw_scene_rows(rows)

    def draw_scene_rows(self,rows):
        """Paint to the current terminal bounds, not a fixed picture box."""
        inks={'queen':CYAN,'noir':GOLD,'foe':RED,'rope':DIM,
              'rail':RED,'face':WHITE,'dim':DIM,'flash':GOLD,
              'red':RED,'gold':GOLD,'cyan':CYAN,'green':GREEN,'white':WHITE,
              **SCENE_PIGMENTS}
        shade={'dim','rope','slate','navy','forest','ochre','wine','ink','indigo','plum','umber','moss'}
        for y,row in enumerate(rows):
            x=0
            for run,ink in row:
                if run.strip():self._b_put(y,x,run,inks[ink],ink not in shade)
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
            cue=self._b_cue
            elapsed=(now-started)*self._b_cut_rate
            self.draw_cutin(title,elapsed,finishing=cue.finishing,cast=cue.cast,targets=cue.targets)
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
        self._b_feedback.clear()
        self._b_feedback_until=0.0
        self._b_outgoing=None
        self._b_cut_in=None
        self._b_cut_damage=None
        self._b_cut_queue=[]
        self._b_battle_cuts=set()
        self._b_intermediate_wave=False
        self._b_final_action=False
        self._b_offer_short_repeats=False
        self._b_present_action(b,b.wave,b.enemies,now)

    def _b_show_damage(self,events,old_wave,old_foes,now,feedback=()):
        self._b_record_damage(events,now)
        if feedback:
            grouped={}
            for event in feedback:
                values,tags=grouped.setdefault(event.target,({},{}))
                if event.resource and event.delta:
                    # Damage and recovery can both occur during an automatic
                    # enemy chain. Retain both instead of showing a net gain.
                    key=event.resource,event.delta>0,'COST' in event.tags
                    values[key]=values.get(key,0)+event.delta
                tags.update(dict.fromkeys(tag for tag in event.tags if tag!='COST'))
            self._b_feedback={u:tuple(f'{n:+g} {r}'+(' cost' if paid else '') for (r,_,paid),n in values.items())+tuple(tags)
                              for u,(values,tags) in grouped.items()}
            self._b_feedback={u:tuple(part.replace('-', '−') for part in parts)
                              for u,parts in self._b_feedback.items()}
            self._b_feedback_until=now+FEEDBACK_HOLD

        if self._b_battle.wave!=old_wave and any(foe in self._b_hp_trails for foe in old_foes):
            self._b_outgoing=(old_wave,old_foes,now+max(FEEDBACK_HOLD,HP_FLASH+HP_DRAIN+HP_SETTLE))

    def _b_start_cut(self,card,now):
        cue=card if isinstance(card,CutCue) else CutCue(*card)
        self._b_cue=cue
        mode='testing' if getattr(self,'testing',False) else 'trials' if getattr(self,'page',None)=='trials' else 'story'
        self._b_cut_key=(mode,cue.title,cue.finishing)
        self._b_cut_shortenable=not self._b_final_action and (not cue.finishing or self._b_intermediate_wave)
        if (self._b_cut_shortenable and self._b_cut_key in self._b_battle_cuts
                and mode=='story' and not self._b_short_repeats):
            self._b_offer_short_repeats=True
        self._b_cut_rate=(SHORT_REPEAT_RATE if self._b_cut_shortenable and self._b_short_repeats
                          and self._b_cut_key in self._b_finished_cuts else 1.0)
        self._b_cut_in=(cue.title,cue.description,now,now+cutin_duration(cue.title)/self._b_cut_rate)

    def _b_present_action(self,b,old_wave,old_foes,now):
        cut=getattr(b,'cut_in',None)
        if cut:
            # The CutCue finisher flag controls the artwork. A wave ending
            # within ordinary combat is not the final blow of a battle.
            phase=getattr(b,'phase',None)
            self._b_intermediate_wave=phase=='turn' and b.wave!=old_wave
            self._b_final_action=phase in ('win','loss','interlude')
            self._b_cut_queue=list(getattr(b,'cut_in_queue',()))
            self._b_cut_damage=(tuple(b.damage_events),old_wave,old_foes,tuple(getattr(b,'feedback',())))
            self._b_start_cut(cut,now)
        else:
            self._b_show_damage(b.damage_events,old_wave,old_foes,now,getattr(b,'feedback',()))

    def _b_release_cut(self,now):
        if self._b_cut_in and now>=self._b_cut_in[3]:
            if self._b_cut_shortenable:
                self._b_finished_cuts.add(self._b_cut_key)
                self._b_battle_cuts.add(self._b_cut_key)
        if self._b_cut_queue:
            self._b_start_cut(self._b_cut_queue.pop(0),now)
            return
        self._b_cut_in=None
        if self._b_cut_damage:
            events,wave,foes,feedback=self._b_cut_damage
            self._b_cut_damage=None
            self._b_show_damage(events,wave,foes,now,feedback)

    def _b_result_animation(self,now):
        return (self._b_cut_in is not None
                or bool(self._b_feedback) and now<self._b_feedback_until
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
        self._b_offer_short_repeats=False
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
            if overlay=='help' and kl=='e':
                self._b_overlay='elements'
                return True
            if overlay=='elements' and k==ESC:
                self._b_overlay='help'
                return True
            if overlay=='help' and kl=='c' and getattr(b,'story',False):
                self._b_short_repeats=not self._b_short_repeats
                self._b_offer_short_repeats=False
                return True
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
        if kl=='c' and self._b_screen=='command' and self._b_offer_short_repeats and b.phase=='turn':
            self._b_short_repeats=True
            self._b_offer_short_repeats=False
            self._b_message='Short Repeats on. Final blows stay full.'
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
                if getattr(self,'page',None)=='trials':
                    # Classic Trials can be resumed. Returning to the map
                    # needs no destructive-action confirmation.
                    self.page=-1
                else:
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
            cat,label,detail,ok=rows[choose]
            self._b_index=self._b_saved_index=choose
            if not ok:
                self._b_message=detail
                return True
            self._b_message=''
            if cat in ('attack','gun','guard','analyze','allout','story-special','showtime','contract') and len(b.actions(cat))==1:
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
