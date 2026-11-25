#!/usr/bin/env python3
"""Phantom Campaign: independent, reconstructed offline curses campaign."""
import argparse
import curses as C
import os
from pathlib import Path
import textwrap
import time
from animation_gallery import AnimationGallery
from battle_data import TEAM
from battle_ui import BattleUI, RED, GOLD, CYAN, WHITE, DIM, GREEN, ENTER, ESC
import campaign_data as content
from campaign_combat import build_stage, stage_grade
from campaign_state import Campaign, TestingCampaign, CampaignError

VAULT_WORDS=('RICH','REAP','HUGE','GOLD')
VAULT_MAP=dict(zip('RICHEAPUGOLD','010293131841'))
STORY=(
 ('SHUJIN AFTER CLASS','At Shujin, a celebrated coach has made the gym his kingdom. You and Ryuji follow the strange app through the school gate. The tracks vanish behind you.'),
 ('A CASTLE WITH NO EXIT','The school gives way to castle walls. Mona points to a side gate. Take the Treasure at the heart of the distortion and the real Kamoshida may have to answer for what he has done.'),
 ('THE FIRST OPENING','A lantern swings over the patrol. Mona watches the flame bend and points into the wind. Ryuji rolls up his sleeves. Start there, and do not let the sentries call for help.'),
)

COMMANDS=('Persona','Attack','Gun','Guard','Items','Baton Pass','All-Out Attack','Analyze')
DRILL=(
    ('FIND THE WEAKNESS','The Bicorn is weak to Electric. Start by opening Persona.',COMMANDS,1),
    ('SWITCH TO PIXIE','Left and Right cycle masks. Pick Pixie and use Zio.',(),1),
    ('PICK A SHADOW','The W is a known matching weakness. Aim at the Bicorn.',('Lantern   Wind W','Bicorn   Electric W'),2),
    ('ONE MORE!','A new knockdown gives an extra action. Use Baton Pass to extend it.',COMMANDS,6),
    ('PASS TO MONA','Mona brings Wind to the chain.',('Mona  /  Wind','Skull  /  Electric'),1),
    ('OPEN MONA’S SKILLS','Open Mona’s Persona list to use Wind.',COMMANDS,1),
    ('USE GARULA','Garula is a single-target Wind skill.',('Garula   Wind','Magarula   Wind all','Diarama   Heal'),1),
    ('FINISH THE SETUP','Aim at the standing lantern. The Bicorn is already down.',('Lantern   Wind W','Bicorn   DOWN'),1),
    ('HOLD UP','Both Shadows are down and Joker is standing. Use All-Out Attack.',COMMANDS,7),
    ('BRACE FOR THE HIT','The King is winding up Royal Smash. Guard to reduce the damage.',COMMANDS,4),
)

class CampaignApp(BattleUI):
    def __init__(self,screen,store,seed=None):
        self.s=screen;self.store=self.story=store;self.seed=seed
        self.chapters=tuple(content.CHAPTERS)
        self.by_id={n['id']:n for n in content.NODES}
        self.page='title';self.testing=False
        self.i=0 if store.status=='ready' else 1
        self.ch=0;self.pick=0;self.node=None;self.marks={}
        self.notice='';self.cached_trials=None;self.story_view=None
        self.prologue=0;self.dial=0;self.code='';self.dial_notice=''
        self.grade=None;self.reward=None;self.error=None;self.finished=None
        self.story_visited=False;self.restore_focus=False
        self.gallery=None

    def put(self,y,x,t,color=WHITE,b=False,reverse=False):
        if 0<=y<self.h and 0<=x<self.w-1:
            try:self.s.addnstr(y,x,str(t),self.w-1-x,C.color_pair(color)|(C.A_BOLD if b else 0)|(C.A_REVERSE if reverse else 0))
            except C.error:pass
    def mid(self,y,t,color=WHITE,b=False):
        self.put(y,max(0,(self.w-len(t))//2),t,color,b)
    def frame(self,title,footer):
        if self.testing:
            self.put(0,2,'SESSION ONLY  /  STORY SAVE UNCHANGED',DIM)
        self.put(1,2,'◆ TESTING MODE' if self.testing else '◆ PHANTOM CAMPAIGN',GOLD if self.testing else RED,True)
        self.put(1,max(21,self.w-len(title)-3),title,CYAN,True)
        for y in (2,self.h-3):self.put(y,2,'━'*(self.w-4),RED)
        self.mid(self.h-2,footer,DIM)
    def lines(self,y,x,text,width=None,limit=4,color=WHITE):
        for j,line in enumerate(textwrap.wrap(str(text),width or self.w-6)[:limit]):self.put(y+j,x,line,color)
    def panel(self,title,heading,footer):
        self.frame(title,footer);self.put(4,3,heading,GOLD,True)
        if self.notice:self.put(self.h-4,3,self.notice[:self.w-6],GOLD,True)
    def nodes(self,ch=None):
        return tuple(self.by_id[n] if isinstance(n,str) else n for n in self.chapters[self.ch if ch is None else ch]['nodes'])
    def label(self,ch=None):return self.chapters[self.ch if ch is None else ch]['id'].upper()
    def opened(self):
        if self.testing:return len(self.chapters)
        known=self.store.data['cleared']
        return min(len(self.chapters),1+sum(all(n['id'] in known for n in self.nodes(i)) for i in range(len(self.chapters))))
    def near(self):
        cleared=self.store.data['cleared']
        return next((i for i,n in enumerate(self.nodes()) if n['id'] not in cleared),len(self.nodes())-1)
    def switch(self,d):
        self.marks[self.ch]=self.pick;self.ch=(self.ch+d)%self.opened()
        self.pick=self.marks.get(self.ch,self.near());self.notice=''
    def nav(self,k,i,n):return self._b_nav(k,i,n)
    def commit(self,k,i,n):return self._b_commit(k,i,n)
    def transact(self,fn,description):
        try:result=fn()
        except (CampaignError,ValueError,OSError) as exc:
            self.notice='BLOCKED • '+str(exc);return False,None
        self.notice=('TEST SESSION' if self.testing else 'AUTOSAVED')+'  /  '+description
        return True,result

    def title(self):
        self.frame('TOKYO / OFFLINE LINK','↑↓ SELECT  ENTER OPEN  1–5 JUMP')
        self.mid(5,'—  M E T A V E R S E   L I N K  —',RED,True)
        self.mid(7,'P H A N T O M   C A M P A I G N',WHITE,True)
        self.mid(9,'◆  PALACE INFILTRATION  /  FIGHT-ONLY  ◆',GOLD)
        ready=self.story.status=='ready'
        self._b_list([('CONTINUE','',ready),('NEW GAME','',True),('TESTING MODE','',True),('ANIMATION GALLERY','',True),('QUIT','',True)],11,5,self.w-10,5,self.i)
        tips=('Continue from the campaign autosave.' if ready else 'No readable story save in this slot.',
              'Begin at the Castle; existing saves are backed up.',
              'All built battles, no story progress or save changes.',
              'Preview every cut-in and battle effect without a fight.','Close the terminal.')
        self.mid(17,tips[self.i],DIM)
        if self.notice:self.put(self.h-4,3,self.notice[:self.w-6],GOLD)

    def confirm(self):
        self.panel('SYSTEM / NEW GAME','START A NEW CAMPAIGN?','N CONFIRM NEW GAME  ESC KEEP CURRENT SAVE')
        self.lines(8,3,'Your old save will be copied to a separate backup before the new one replaces it. Escape leaves the current file untouched.')

    def story_panel(self):
        title,body=STORY[self.prologue]
        self.panel('PROLOGUE / CASTLE',f'{self.prologue+1}/3  ◆  {title}','← BACK  ENTER NEXT  ESC SKIP')
        self.lines(8,3,body,limit=8)

    def start_drill(self):
        self.drill=0;self.drill_pick=0;self.drill_mask=0;self.drill_feedback='';self.page='drill'
    def drill_rows(self):
        if self.drill==2:
            return (('Eiha  Curse','Cleave  Physical','Rakunda  DEF down'),
                    ('Zio  Electric','Garu  Wind','Dia  Heal'),
                    ('Agi  Fire','Dazzler  Ailment','Rakunda  DEF down'))[self.drill_mask]
        return DRILL[self.drill-1][2]
    def draw_drill(self):
        self.frame('MONA / FIELD DRILL','↑↓ PICK  ENTER CONFIRM  ESC SKIP')
        if self.drill in (0,len(DRILL)+1):
            start=self.drill==0
            self.mid(6,'◈ TRAINING LINK ◈' if start else '◈ FIELD DRILL CLEARED ◈',GREEN,True)
            self.lines(9,3,'Try a short simulation. No progress, supplies or SP can be lost here.' if start else
                       'A weakness gave One More. Baton Pass chained into an All-Out Attack. Guard reduced the practice hit.')
            self.lines(14,3,'Enter to begin. These keys match the real battle menu.' if start else
                       'Enter to open the map. H from the map reruns training. I checks status and L opens the battle log.',color=DIM)
            return
        name,hint,_,_=DRILL[self.drill-1]
        self.put(4,3,f'{self.drill:02}/{len(DRILL)}  /  {name}',GOLD,True)
        self.lines(6,3,hint,limit=2)
        if self.drill==2:self.put(9,3,'←→ MASK  [ '+('Arsène','Pixie',"Jack-o’-Lantern")[self.drill_mask]+' ]',CYAN,True)
        for i,name in enumerate(self.drill_rows()):
            x=3+(i//4)*((self.w-6)//2);y=11+i%4
            self.put(y,x,f'{"▶" if i==self.drill_pick else " "} {i+1} {name}',CYAN if i==self.drill_pick else WHITE)
        self.lines(19,3,self.drill_feedback,limit=2,color=GOLD)
    def drill_key(self,k):
        if k==ESC or (self.drill==len(DRILL)+1 and k in (*ENTER,' ')):
            self.page='map';self.notice='FIELD DRILL SKIPPED' if k==ESC else 'FIELD DRILL COMPLETE';return
        if self.drill==0:
            if k in (*ENTER,' '):self.drill=1
            return
        if self.drill==len(DRILL)+1:return
        if self.drill==2 and k in (C.KEY_LEFT,C.KEY_RIGHT):
            self.drill_mask=(self.drill_mask+(1 if k==C.KEY_RIGHT else -1))%3
            self.drill_pick=0;self.drill_feedback='';return
        rows=self.drill_rows()
        self.drill_pick=self.nav(k,self.drill_pick,len(rows))
        item=self.commit(k,self.drill_pick,len(rows))
        if item is None:return
        correct=DRILL[self.drill-1][3]-1
        if item==correct and (self.drill!=2 or self.drill_mask==1):
            self.drill+=1;self.drill_pick=0;self.drill_feedback=''
        else:
            self.drill_feedback=('Switch to Pixie, then choose Zio.' if self.drill==2 else
                                 f'Try {correct+1} {rows[correct]}.')

    def transition(self):
        next_ch=self.chapters[self.ch+1]
        self.panel('CASE FILE / '+next_ch['id'].upper(),'◆ A NEW CASE  /  '+next_ch['title'].upper(),'ENTER OPEN MAP  ESC SKIP')
        self.lines(8,3,next_ch.get('brief','A new Palace is open. Pick an operation from the map.'),limit=9)

    def draw_map(self):
        nodes=self.nodes();d=self.store.data;known=d['cleared']
        complete=sum(n['id'] in known for n in nodes)
        title=f'ALL {len(nodes)} BATTLES OPEN' if self.testing else f'{complete}/{len(nodes)} CLEARED'
        self.panel(f'PALACE / {self.label()} MAP',f'◆ {self.chapters[self.ch]["title"].upper()}  /  {title}',
                   '←→ PALACE  ↑↓ PICK  ↵ BRIEF  S SQUAD  V VELVET  T  ESC')
        tabs='  /  '.join(f'[ {self.label(i)} ]' if i==self.ch else self.label(i) for i in range(self.opened()))
        if len(tabs)>self.w-6:
            count=self.opened()
            tabs=f'‹ {self.label((self.ch-1)%count)}  [ {self.label()} ]  {self.label((self.ch+1)%count)} ›  {self.ch+1}/{count}'
        self.put(5,3,tabs,CYAN,True)
        self.put(6,3,'◆ Available  •  T Classic Trials' if self.testing else '✓ Clear  ◆ Available  ▣ Locked  •  H Help  T Trials',DIM)
        wide=self.w>=92;split=self.w//2
        for idx,n in enumerate(nodes):
            ok=self.store.can_play(n['id']);done=not self.testing and n['id'] in known
            mark='✓' if done else '◆' if ok else '▣'
            rank=f'  [{known[n["id"]]}]' if done and known.get(n['id']) else ''
            y=8+idx*(2 if wide else 1);width=split-5 if wide else self.w-6
            row=f'{"▶" if idx==self.pick else " "}  {idx+1:02}  {mark}  {n["title"]}{rank}'
            self.put(y,3,row[:width].ljust(width),GREEN if done else CYAN if ok else DIM,idx==self.pick,idx==self.pick)
            if wide:self.put(y+1,11,n.get('map_mark',''),DIM)
        x,y=(split+2,8) if wide else (3,15);n=nodes[self.pick];width=self.w-x-3
        self.put(y,x,n['title'].upper()[:width],CYAN,True)
        self.lines(y+2,x,n.get('brief',''),width,3)
        if self.store.can_play(n['id']):
            self.put(y+5,x,f'{len(n["waves"])} wave(s)  /  Enter for briefing.',DIM)
        else:
            prior=nodes[max(0,self.pick-1)]['title']
            self.put(y+5,x,('LOCKED • Clear '+prior+' first.')[:width],GOLD)

    def brief(self):
        n=self.node;d=self.store.data
        self.panel(self.label()+' / OPERATION BRIEF','◆ '+n['title'].upper(),
                   ('ENTER DIALS' if self.dials_required() else 'ENTER DEPLOY')+'  ESC MAP  S SQUAD  V VELVET')
        self.lines(6,3,(not self.testing and n.get('story_before')) or n.get('brief',''),limit=4)
        self.put(10,3,(f'WAVES: {len(n["waves"])}   /   SQUAD: '+', '.join(['Joker',*d['squad']]))[:self.w-6],CYAN,True)
        self.lines(12,3,n.get('preview') or 'Opening formation: '+', '.join(n['waves'][0]),limit=3,color=DIM)
        self.put(15,3,n.get('navigator','Mona').upper()+' INTEL  /  '+n.get('tactic',''),GOLD,True)
        self.lines(16,3,n.get('hint',''),limit=self.h-20,color=WHITE)

    def dials_required(self):
        return (not self.testing and self.node['id']=='bank-vault' and self.dial<len(VAULT_WORDS)
                and 'bank-vault' not in self.store.data['cleared'])
    def draw_dials(self):
        word=VAULT_WORDS[self.dial]
        self.panel('BANK / VAULT DIALS',f'◆ LOCK {self.dial+1}/4  /  {word}',
                   '0–9 SET DIALS  BACKSPACE EDIT  ENTER TURN  ESC BACK')
        self.lines(6,3,'Translate the lock word from left to right using Kaneshiro’s journal.')
        pairs=tuple(VAULT_MAP.items())
        for j in range(2):self.put(10+j,3,'   '.join(a+'='+b for a,b in pairs[j*6:(j+1)*6]),CYAN)
        self.mid(14,'     '.join(word),GOLD,True)
        self.mid(15,'   '.join('['+x+']' for x in self.code.ljust(4,'_')),WHITE,True)
        if self.dial:self.put(18,3,'OPENED: '+', '.join(VAULT_WORDS[:self.dial]),GREEN)
        self.lines(19,3,self.dial_notice,limit=2,color=GOLD)
    def key_dials(self,k):
        if k==ESC:self.code='';self.dial_notice='';self.page='brief'
        elif k in (C.KEY_BACKSPACE,chr(127),chr(8)):self.code=self.code[:-1];self.dial_notice=''
        elif isinstance(k,str) and len(k)==1 and k in '0123456789':
            self.code=(self.code+k)[:4];self.dial_notice=''
        elif k in ENTER:
            code=''.join(VAULT_MAP[x] for x in VAULT_WORDS[self.dial])
            if len(self.code)<4:self.dial_notice='Set all four digits before turning the lock.'
            elif self.code!=code:self.code='';self.dial_notice='That lock did not turn. Check the notebook.'
            else:
                self.dial+=1;self.code='';self.dial_notice=''
                if self.dial==4:self.page='brief';self.notice='DIALS OPEN  /  ENTER TO DEPLOY'

    def open_squad(self,back):
        self.back=back;self.edit=list(self.store.data['squad']);self.i=0;self.page='squad';self.notice=''
    def draw_squad(self):
        d=self.store.data;names=['Joker',*TEAM]
        self.panel('PALACE / SQUAD',f'◆ TEAM CONFIG  /  {len(self.edit)}/{d["squad_slots"]} ALLIES + JOKER',
                   '↑↓ SELECT  ENTER TOGGLE  S APPLY SQUAD  ESC BACK')
        rows=[]
        for n in names:
            own=n=='Joker' or n in d['teammates']
            mark='●' if n=='Joker' or n in self.edit else '○' if own else '▣'
            rows.append((f'{mark} {n}  /  '+('Wild Card lead' if n=='Joker' else TEAM[n]['role']),'',own))
        self._b_list(rows,6,3,self.w-6,9,self.i)
        n=names[self.i]
        if n=='Joker':self.put(17,3,f'Joker upgrades: +{d["joker_hp"]} HP  /  +{d["joker_sp"]} SP',CYAN)
        elif n in d['teammates']:
            self.put(17,3,f'{n}  /  {TEAM[n]["hp"]} HP  {TEAM[n]["sp"]} SP',CYAN)
            self.lines(18,3,'Upgrades: '+(', '.join(d['team_skills'].get(n,[])) or 'none'),limit=2,color=DIM)
        else:self.put(17,3,'This Thief has not joined the campaign.',DIM)

    def stage(self):
        try:b=build_stage(self.store,self.node['id'],self.seed)
        except (CampaignError,ValueError) as exc:self.notice='BLOCKED • '+str(exc);self.page='brief';return
        self.battle_init();self._b_battle=b
        self._b_personas=getattr(b,'personas',self._b_personas);self._b_screen='command'
        self._b_prepare_presentation(b,time.monotonic())
        self.finished=None;self.reward=None;self.error=None;self.grade=None;self.first=False
        self.notice='';self.page='battle'
    def record(self,retry=False):
        b=self._b_battle
        if b.phase not in ('win','loss') or (self.finished is not None and not retry):return
        self.finished=time.monotonic()
        if b.phase=='loss':self.notice='NO CAMPAIGN PROGRESS CHANGED';return
        self.grade=stage_grade(b)
        if self.testing:self.notice='PRACTICE ONLY  /  STORY SAVE UNCHANGED';return
        self.first=self.node['id'] not in self.store.data['cleared']
        try:
            self.reward=self.store.clear(self.node['id'],self.grade);self.error=None
            self.notice='AUTOSAVED  /  '+('FIRST CLEAR' if self.first else 'BEST MEDAL KEPT')
        except (CampaignError,ValueError,OSError) as exc:
            self.error=str(exc);self.notice='BLOCKED • Progress has not been saved.'
    def draw_combat(self):
        if self._b_overlay in ('resume','abandon'):
            self.panel('PALACE / PAUSED','RESTART THIS FIGHT?' if self._b_overlay=='abandon' else 'RETURN TO THE PALACE MAP?',
                       'ENTER CONFIRM  ESC STAY')
            self.lines(9,3,'This attempt ends. An unfinished fight does not change campaign progress.')
            return
        self.record()
        now=time.monotonic()
        if (self.finished is not None and self._b_overlay is None and now-self.finished>=.68
                and not self._b_result_animation(now)):
            self.page='result';self.result();return
        self.battle_page()
        self.record()
    def chapter_final(self):
        return self.node['id']==self.nodes()[-1]['id'] and all(n['id'] in self.store.data['cleared'] for n in self.nodes())
    def new_chapter(self):
        return not self.testing and self.first and not self.error and self.chapter_final() and self.ch+1<self.opened()
    def result(self):
        win=self._b_battle.phase=='win'
        if self.testing:title='PRACTICE WIN' if win else 'PRACTICE DEFEAT'
        else:title=(self.label()+' SECURED' if self.chapter_final() else 'OPERATION CLEARED') if win else 'SQUAD DEFEATED'
        footer=('ENTER RETRY SAVE  ESC MAP' if self.error else
                'ENTER RETRY  L LOG  ESC MAP' if not win else
                (f'↵ {self.label(self.ch+1)}' if self.new_chapter() else '↵ MAP')+'  R REPLAY  L LOG  S SQUAD  V CARDS  ESC MAP')
        self.panel('PALACE / DEBRIEF','◆ '+title+'  //  '+self.node['title'].upper(),footer)
        if win:
            self.put(7,3,('PRACTICE MEDAL  ' if self.testing else 'MEDAL  ')+str(self.grade),GOLD,True)
            self.put(8,3,'S: all standing at 50%+ HP  A: ¾+ standing  B: otherwise',DIM)
        if self.error:self.lines(10,3,self.error,limit=4,color=RED);return
        if self.testing:self.lines(11,3,'No campaign rewards or progress. All built battles remain available.');return
        if not win:self.lines(10,3,'Joker cannot continue. Retry with fresh supplies, or return to the map to adjust the team.');return
        y=10
        if self.reward:
            self.put(y,3,'FIRST-CLEAR REWARDS',CYAN,True);y+=1
            for field,label in (('credits','Credits'),('joker_hp','Joker HP'),('joker_sp','Joker SP'),('slots','Mask slots'),('squad_slots','Ally slots'),
                                ('teammates','Recruited'),('personas','Registered'),('skill_cards','Skill cards'),('oracle','Support')):
                v=self.reward.get(field)
                if v:
                    self.put(y,3,f'◆ {label}: '+(', '.join(v) if isinstance(v,(list,tuple)) else '+'+str(v)),WHITE);y+=1
            for name,moves in self.reward.get('team_skills',{}).items():
                self.put(y,3,f'◆ {name} learned '+', '.join(moves),WHITE);y+=1
        else:self.put(y,3,'Replay complete. First-clear rewards cannot repeat.',DIM);y+=1
        if self.first and self.node.get('story_after') and y+1<self.h-5:
            self.lines(y+1,3,self.node['story_after'],limit=min(4,self.h-6-y),color=DIM)
        if self.new_chapter():self.put(self.h-5,3,'NEW PALACE UNLOCKED  /  '+self.label(self.ch+1),GREEN,True)
        elif self.chapter_final():self.lines(self.h-5,3,self.chapters[self.ch].get('completion','Palace secured.'),limit=1,color=GREEN)
        else:self.put(self.h-5,3,'NEXT ROUTE  /  '+self.nodes()[self.near()]['title'].upper(),GREEN,True)

    def open_velvet(self,back,compendium=False):
        d=self.store.data
        self.back=back;self.mask_edit=list(d['loadout']);self.primary=d['primary']
        self.tab=int(compendium or not hasattr(self.store,'fusion_options'))
        self.i=0;self.notice='';self.page='velvet'
    def velvet_names(self):
        if self.tab:return list(self.store.data['personas'])
        return [r['result'] for r in getattr(content,'FUSIONS',())]
    def draw_velvet(self):
        d=self.store.data;names=self.velvet_names();y=15
        self.panel('VELVET ROOM',f'◆ {"FUSION  /  [ COMPENDIUM ]" if self.tab else "[ FUSION ]  /  COMPENDIUM"}  •  {d["credits"]} cr',
                   '←→ TAB  ↑↓ PICK  E EQUIP  P LEAD  A CARD  S APPLY  ESC' if self.tab else '←→ TAB  ↑↓ PICK  ENTER PREVIEW  ESC BACK')
        if not names:self.put(6,3,'No entries.',DIM);return
        rows=[]
        for name in names:
            if self.tab:
                mark='★' if name==self.primary else '●' if name in self.mask_edit else '○'
                rows.append((f'{mark} {name}','',True))
            else:
                f=self.store.fusion_options(name);r=f['recipe']
                rows.append((f'{"◆" if f.get("available",f.get("allowed",False)) else "▣"} {name}   {r["cost"]} cr','',True))
        self._b_list(rows,6,3,self.w-6,8,self.i)
        name=names[self.i]
        self.put(y,3,name.upper(),CYAN,True)
        if self.tab:
            spec=self.store.persona_spec(name) if hasattr(self.store,'persona_spec') else content.PERSONA_DATA[name]
            self.put(y+1,3,f'{len(self.mask_edit)}/{d["slots"]} active  •  ★ starting Persona',DIM)
            self.lines(y+2,3,', '.join(spec['skills']),limit=2)
            self.lines(y+4,3,'Defense: '+(', '.join(f'{a} {v}' for a,v in spec['affinity'].items()) or 'Normal'),limit=2,color=DIM)
        else:
            f=self.store.fusion_options(name)
            self.lines(y+1,3,' + '.join(f['recipe']['parents'])+'  →  '+name,limit=2)
            self.lines(y+3,3,f.get('reason') or 'Preview first. Registered parents stay in the Compendium.',limit=2,color=DIM)
    def donor_options(self):
        return [(None,None)]+[(n,k) for n,skills in self.fusion['donors'].items() for k in skills]
    def draw_fusion(self):
        f=self.fusion;r=f['recipe'];d=self.store.data
        self.panel('VELVET ROOM / FUSION PREVIEW','◆ '+' + '.join(r['parents'])+'  →  '+r['result'],
                   '↑↓ INHERIT ONE SKILL  F FUSE  ESC CANCEL')
        self.put(6,3,f'PRICE {r["cost"]}  /  {d["credits"]} ON HAND  /  {d["credits"]-r["cost"]} AFTER',CYAN)
        spec=content.PERSONA_DATA[r['result']]
        self.lines(7,3,'Base skills: '+', '.join(spec['skills']),limit=2,color=DIM)
        self.put(9,3,'SELECT INHERITANCE  /  PARENTS ARE RETAINED',GOLD,True)
        self._b_list([((k+' ← '+n) if k else 'No inherited skill','',True) for n,k in self.donor_options()],10,3,self.w-6,8,self.sub)
        if f.get('reason'):self.lines(self.h-6,3,f['reason'],limit=2,color=GOLD)
    def draw_registered(self):
        d=self.store.data
        self.panel('VELVET ROOM / REGISTERED','◆ '+self.fused.upper()+' IS REGISTERED','E EQUIP NOW  ESC KEEP REGISTERED')
        self.lines(7,3,'The equipped Personas have not changed yet.')
        self.lines(10,3,'Choose which mask to replace.' if len(d['loadout'])>=d['slots'] else 'An open slot is ready.')
    def draw_replace(self):
        d=self.store.data;n=d['loadout'][self.sub]
        self.panel('VELVET ROOM / EQUIP SWAP','◆ EQUIP '+self.fused.upper(),'↑↓ SELECT  ENTER CONFIRM REPLACEMENT  ESC CANCEL')
        self._b_list([(a,'',True) for a in d['loadout']],7,3,self.w-6,8,self.sub)
        self.lines(16,3,f'Replace {n} with {self.fused}. All masks remain registered.')
        if n==d['primary']:self.lines(19,3,self.fused+' becomes the starting Persona.',limit=1,color=GOLD)
    def equip_fusion(self,old=None):
        d=self.store.data;names=list(d['loadout']);primary=d['primary']
        if old is None:names.append(self.fused)
        else:
            names[names.index(old)]=self.fused
            if primary==old:primary=self.fused
        if self.transact(lambda:self.store.equip_personas(names,primary),'EQUIPPED '+self.fused)[0]:
            self.mask_edit=names;self.primary=primary;self.tab=1
            self.i=self.velvet_names().index(self.fused);self.page='velvet'
    def draw_cards(self):
        name=self.velvet_names()[self.i]
        self.panel('VELVET ROOM / SKILL CARDS','◆ APPLY A CARD TO '+name.upper(),'↑↓ SELECT  ENTER APPLY ONE CARD  ESC CANCEL')
        cards=self.store.data['skill_cards']
        if not cards:self.put(7,3,'No skill cards found.',DIM)
        else:self._b_list([(f'{k} ×{v}','',True) for k,v in cards.items()],6,3,self.w-6,self.h-12,self.sub)

    def start_story(self):
        ok,backup=self.transact(self.story.new_game,'NEW CAMPAIGN')
        if not ok:return
        if backup:self.notice+='  •  Previous save backed up.'
        self.ch=self.pick=self.prologue=self.dial=0;self.code=self.dial_notice='';self.marks={}
        self.cached_trials=None;self.story_visited=True;self.restore_focus=False;self.page='prologue'
    def start_testing(self):
        try:new=TestingCampaign()
        except (CampaignError,ValueError) as exc:self.notice='BLOCKED • '+str(exc);return
        self.story_view=(self.ch,self.pick,self.marks,self.node,self.cached_trials)
        self.testing=True;self.store=new;self.ch=self.pick=0
        self.marks={};self.node=None;self.cached_trials=None
        self.notice='ALL BUILT BATTLES OPEN  /  NO STORY SAVES';self.page='map'
    def leave_map(self):
        if self.testing:
            self.ch,self.pick,self.marks,self.node,self.cached_trials=self.story_view
            self.store=self.story;self.testing=False;self.story_view=None
            self.notice='TESTING MODE CLOSED  /  STORY SAVE UNCHANGED'
            self.restore_focus=self.story_visited
        else:self.notice=''
        self.i=0 if self.story.status=='ready' else 1;self.page='title'
    def leave_result(self):
        self.page='map'
        if not self.testing:self.pick=self.near()

    def key(self,k):
        kl=k.lower() if isinstance(k,str) else k
        if kl=='q':
            if self.page=='battle' and self._b_battle.phase=='win':
                self.record()
                if self.error:self.page='result';return True
            return False
        page=self.page
        if page=='title':
            self.i=self.nav(k,self.i,5);choose=self.commit(k,self.i,5)
            if choose==0:
                status=self.story.reload()
                if self.story.status=='ready':
                    if not self.restore_focus or self.ch>=self.opened():self.ch=self.opened()-1;self.pick=self.near()
                    self.restore_focus=False;self.story_visited=True
                    self.dial=0;self.code=self.dial_notice=''
                    self.notice='CAMPAIGN SAVE LOADED';self.page='map'
                else:self.notice='BLOCKED • No readable campaign save.'
            elif choose==1:
                self.story.reload()
                if self.story.status=='missing':self.start_story()
                else:self.page='confirm';self.notice=''
            elif choose==2:self.start_testing()
            elif choose==3:
                self.i=3
                if self.gallery is None:self.gallery=AnimationGallery()
                self.notice='';self.page='gallery'
            elif choose==4:return False
        elif page=='gallery':
            if not self.gallery.key(self,k):self.page='title'
        elif page=='confirm':
            if k==ESC:self.page='title';self.notice='CURRENT SAVE KEPT'
            elif kl=='n':self.start_story()
        elif page=='prologue':
            if k==ESC:self.start_drill()
            elif k==C.KEY_LEFT:self.prologue=max(0,self.prologue-1)
            elif k in (*ENTER,' ',C.KEY_RIGHT):
                if self.prologue==len(STORY)-1:self.start_drill()
                else:self.prologue+=1
        elif page=='drill':self.drill_key(k)
        elif page=='transition':
            if k in (*ENTER,ESC,' ',C.KEY_RIGHT):
                self.switch(1);self.page='map';self.notice=self.label()+' ROUTE OPEN  /  AUTOSAVED'
        elif page=='map':
            old=self.pick
            self.pick=self.nav(k,self.pick,len(self.nodes()))
            if k==ESC:self.leave_map()
            elif k in (C.KEY_LEFT,C.KEY_RIGHT) and self.opened()>1:self.switch(1 if k==C.KEY_RIGHT else -1)
            elif kl in ('h','?') and not self.testing:self.start_drill()
            elif kl=='s':self.open_squad('map')
            elif kl=='v':self.open_velvet('map')
            elif kl=='t':
                if self.cached_trials is None:self.battle_init()
                else:self.__dict__.update(self.cached_trials)
                self.page='trials'
            else:
                choose=self.commit(k,self.pick,len(self.nodes()))
                if choose is not None:
                    self.pick=choose;n=self.nodes()[choose]
                    if self.store.can_play(n['id']):self.node=n;self.page='brief';self.notice=''
                    else:self.notice='LOCKED • Finish the previous operation.'
                elif old!=self.pick:self.notice=''
        elif page=='brief':
            if k==ESC:self.page='map';self.notice=''
            elif kl=='s':self.open_squad('brief')
            elif kl=='v':self.open_velvet('brief')
            elif k in ENTER:
                if self.dials_required():self.page='dials';self.notice=''
                else:self.stage()
        elif page=='dials':self.key_dials(k)
        elif page=='squad':
            names=['Joker',*TEAM];d=self.store.data
            if k==ESC:self.page=self.back;self.notice=''
            elif kl=='s':
                if self.transact(lambda:self.store.equip_squad(self.edit),'SQUAD EQUIPPED')[0]:self.page=self.back
            else:
                self.i=self.nav(k,self.i,len(names));choose=self.commit(k,self.i,len(names))
                if choose is not None:
                    self.i=choose;n=names[choose]
                    if n=='Joker':self.notice='Joker is always active.'
                    elif n not in d['teammates']:self.notice='LOCKED • This Thief has not joined.'
                    elif n in self.edit:self.edit.remove(n);self.notice=n+' moved to standby.'
                    elif len(self.edit)>=d['squad_slots']:self.notice='BLOCKED • Remove an active ally first.'
                    else:self.edit.append(n);self.notice=n+' selected. Press S to apply.'
        elif page=='velvet':
            if k==ESC:self.page=self.back;self.notice=''
            elif k in (C.KEY_LEFT,C.KEY_RIGHT) and hasattr(self.store,'fusion_options'):
                self.tab=1-self.tab;self.i=0;self.notice=''
            else:
                names=self.velvet_names()
                if not names:return True
                self.i=self.nav(k,self.i,len(names));choose=self.commit(k,self.i,len(names));name=names[self.i]
                if not self.tab and choose is not None:
                    self.i=choose;self.fusion=self.store.fusion_options(names[choose]);self.sub=0;self.page='fusion';self.notice=''
                elif self.tab:
                    if choose is not None:self.i=choose
                    elif kl in ('e','p'):
                        if name in self.mask_edit:
                            if kl=='p':self.primary=name
                            elif len(self.mask_edit)>1:
                                self.mask_edit.remove(name)
                                if self.primary==name:self.primary=self.mask_edit[0]
                            else:self.notice='BLOCKED • Keep one Persona equipped.';return True
                        elif len(self.mask_edit)>=self.store.data['slots']:self.notice='BLOCKED • Unequip one mask first.';return True
                        else:
                            self.mask_edit.append(name)
                            if kl=='p':self.primary=name
                        self.notice='Draft updated. Press S to apply.'
                    elif kl=='s':self.transact(lambda:self.store.equip_personas(self.mask_edit,self.primary),'PERSONA LOADOUT')
                    elif kl=='a' and hasattr(self.store,'apply_skill_card'):self.sub=0;self.page='cards';self.notice=''
        elif page=='fusion':
            opts=self.donor_options()
            if k==ESC:self.page='velvet';self.notice=''
            elif kl=='f':
                donor,skill=opts[self.sub];name=self.fusion['recipe']['result']
                if self.transact(lambda:self.store.fuse(name,skill,donor),'REGISTERED '+name+(f' WITH {skill}' if skill else ''))[0]:
                    self.fused=name;self.page='registered'
            else:
                self.sub=self.nav(k,self.sub,len(opts));choose=self.commit(k,self.sub,len(opts))
                if choose is not None:self.sub=choose
        elif page=='registered':
            if k==ESC:self.page='velvet'
            elif kl=='e':
                d=self.store.data
                if len(d['loadout'])>=d['slots']:self.sub=0;self.page='replace'
                else:self.equip_fusion()
        elif page=='replace':
            ns=self.store.data['loadout']
            if k==ESC:self.page='registered'
            elif k in ENTER:self.equip_fusion(ns[self.sub])
            else:
                self.sub=self.nav(k,self.sub,len(ns));choose=self.commit(k,self.sub,len(ns))
                if choose is not None:self.sub=choose
        elif page=='cards':
            cards=list(self.store.data['skill_cards'])
            if k==ESC:self.page='velvet';self.notice=''
            elif cards:
                self.sub=self.nav(k,self.sub,len(cards));choose=self.commit(k,self.sub,len(cards))
                if choose is not None:
                    name=self.velvet_names()[self.i];skill=cards[choose]
                    if self.transact(lambda:self.store.apply_skill_card(name,skill),name+' LEARNED '+skill)[0]:self.page='velvet'
        elif page=='battle':
            if self._b_overlay in ('resume','abandon') and k in ENTER:
                if self._b_overlay=='abandon':self.stage()
                else:self.page='map';self.notice='ATTEMPT ENDED  /  Campaign save unchanged'
            elif self._b_battle.phase=='turn' or self._b_overlay is not None or self._b_cut_in:
                self.battle_key(k);self.record()
        elif page=='result':
            win=self._b_battle.phase=='win'
            if k==ESC:self.leave_result()
            elif k in ENTER and self.error:self.record(retry=True)
            elif k in ENTER and win:
                if self.new_chapter():self.page='transition'
                else:self.leave_result()
            elif k in ENTER or (kl=='r' and not self.error):self.stage()
            elif kl=='l' and not self.error:self._b_overlay='log';self._b_log_scroll=0;self.page='result-log'
            elif win and not self.error and kl=='s':self.open_squad('result')
            elif win and not self.error and kl=='v':self.open_velvet('result',True)
        elif page=='result-log':
            self.battle_key(k)
            if self._b_overlay is None:self.page='result'
        elif page=='trials':
            self.battle_key(k)
            if self.page==-1:
                self.cached_trials={k:v for k,v in vars(self).items() if k.startswith('_b_')}
                self.page='map';self.notice='TRAINING ONLY  /  Campaign save unchanged'
        return True

    def run(self):
        draw={'title':self.title,'confirm':self.confirm,'prologue':self.story_panel,'transition':self.transition,
              'map':self.draw_map,'drill':self.draw_drill,'brief':self.brief,'dials':self.draw_dials,'squad':self.draw_squad,
              'velvet':self.draw_velvet,'fusion':self.draw_fusion,'registered':self.draw_registered,
              'replace':self.draw_replace,'cards':self.draw_cards,'battle':self.draw_combat,'result':self.result,
              'result-log':self.battle_page,'trials':self.battle_page,
              'gallery':lambda:self.gallery.draw(self)}
        while True:
            self.s.erase();self.h,self.w=self.s.getmaxyx()
            small=self.h<25 or self.w<65
            if small:self.mid(self.h//2,'Widen the terminal to at least 65 × 25. Q quits.',GOLD)
            else:draw[self.page]()
            self.s.refresh()
            try:k=self.s.get_wch()
            except C.error:continue
            if (not small or k in ('q','Q')) and not self.key(k):return

def run_curses(s,store,seed):
    try:C.curs_set(0)
    except C.error:pass
    C.start_color()
    try:C.use_default_colors();bg=-1
    except C.error:bg=C.COLOR_BLACK
    colors=[203,221,51,255,246,84] if C.COLORS>=256 else [
        C.COLOR_RED,C.COLOR_YELLOW,C.COLOR_CYAN,C.COLOR_WHITE,C.COLOR_WHITE,C.COLOR_GREEN]
    for i,color in enumerate(colors,1):C.init_pair(i,color,bg)
    s.keypad(True);s.timeout(80)
    CampaignApp(s,store,seed).run()

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Play the reconstructed Phantom Campaign offline.')
    default=Path(__file__).with_name('campaign-save.json')
    p.add_argument('--save',type=Path,default=Path(os.environ.get('PHANTOM_CAMPAIGN_SAVE',str(default))))
    p.add_argument('--seed',type=int,default=None,help=argparse.SUPPRESS)
    args=p.parse_args()
    try:C.wrapper(run_curses,Campaign(args.save),args.seed)
    except KeyboardInterrupt:pass
