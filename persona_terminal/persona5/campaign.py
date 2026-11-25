"""Persona 5 Terminal: independent, reconstructed offline curses campaign."""
import curses as C
import textwrap
import time
from .animation_gallery import AnimationGallery
from .cutins import ACTIVE_ORACLE_FEATURES
from .title_scene import PRODUCT_TITLE, STARTUP_SECONDS, draw_startup, draw_title
from . import velvet_entrance
from . import velvet_menu
from . import bank_vault
from . import campaign_story
from . import first_escape
from .spaceport_press import PressConsole
from .lab_infiltration import LabInfiltration, entry_label as lab_entry_label
from .bank_vault import VAULT_WORDS
from .battle_data import TEAM
from .battle_ui import BattleUI, RED, GOLD, CYAN, WHITE, DIM, GREEN, ENTER, ESC
from ..shared.terminal_surface import TerminalSurface
from . import campaign_data as content
from .campaign_combat import build_stage, stage_grade, stage_party, solo_readiness, operation_unavailable
from .casino_route import CasinoRoute, draw_route_art
from .palace_menu import Timeline, map_screen, brief_frame, transition_frame, airlock
from .campaign_state import TestingCampaign, CampaignError

STORY=(
 ('A NEW SCHOOL','You tried to help a woman on the street. A powerful stranger blamed you, and now you’re in Tokyo on probation, living above Café Leblanc. On your way to Shujin with a new classmate, Ryuji, a strange app picks up the volleyball coach’s name: Kamoshida. A drawbridge rises where the school gate should be.'),
)

COMMANDS=('Persona','Attack','Gun','Guard','Items','Baton Pass','All-Out Attack','Analyze')
DRILL=(
    ('FIND THE WEAKNESS','The Bicorn is weak to Electric. Start by opening Persona.',COMMANDS,1),
    ('SWITCH TO PIXIE','Left and Right cycle masks. Pick Pixie and use Zio.',(),1),
    ('PICK A SHADOW','The W is a known matching weakness. Aim at the Bicorn.',('Lantern   Wind W','Bicorn   Electric W'),2),
    ('ONE MORE!','A new knockdown gives an extra action. Use Baton Pass to extend it.',COMMANDS,6),
    ('PASS TO MONA','Pass to a teammate who can knock down a different standing enemy. Mona has Wind.',('Mona  /  Wind','Skull  /  Electric'),1),
    ('OPEN MONA’S SKILLS','Open Mona’s Persona list to use Wind.',COMMANDS,1),
    ('USE GARULA','Garula is a single-target Wind skill.',('Garula   Wind','Magarula   Wind all','Diarama   Heal'),1),
    ('FINISH THE SETUP','Aim at the standing lantern. The Bicorn is already down.',('Lantern   Wind W','Bicorn   DOWN'),1),
    ('HOLD UP','Both Shadows are down and Joker is standing. Use All-Out Attack.',COMMANDS,7),
    ('BRACE FOR THE HIT','The King is winding up Royal Smash. Guard to reduce the damage.',COMMANDS,4),
)

class CampaignApp(TerminalSurface, BattleUI):
    def __init__(self,screen,store,seed=None):
        self.s=screen;self.store=self.story=store;self.seed=seed
        self.chapters=tuple(content.CHAPTERS)
        self.by_id={n['id']:n for n in content.NODES}
        self.page='title';self.testing=False
        self.i=0 if store.status=='ready' else 1
        self.ch=0;self.pick=0;self.node=None;self.marks={}
        self.notice='';self.cached_trials=None;self.story_view=None;self.practice_view=None
        self.prologue=0;bank_vault.reset_dials(self)
        self.grade=None;self.reward=None;self.error=None;self.finished=None
        self.story_visited=False;self.restore_focus=False
        self.gallery=None
        self.casino_route=None
        self.velvet_started=None
        self.departure=None
        self.back_to_suite=False
        self.palace_timeline=Timeline();self.airlock_started=None
        self.drill_back='map';self.played_after=False
        self.story_scene=None;self.scene_destination=None
        self.scene_checkpoint=None
        self.escape_fight=None;self.press_console=None;self.lab_route=None;self.field_lessons=set()

    def frame(self,title,footer,*,accent=None):
        self.put(1,2,'◆ BATTLE PRACTICE' if self.testing else f'◆ {PRODUCT_TITLE}',GOLD if self.testing else RED,True)
        self.put(1,max(21,self.w-len(title)-3),title,accent or CYAN,True)
        self.put(2,2,'━'*(self.w-4),accent or RED)
        if isinstance(footer,tuple):
            # Two-line map controls stay completely inside the last visible
            # cells. Leave the last terminal row unused; shorter window crops
            # cannot erase the testing shortcuts.
            for off,line in enumerate(footer):
                self.mid(self.h-2-(len(footer)-1)+off,line,DIM)
        else:
            self.put(self.h-3,2,'━'*(self.w-4),accent or RED)
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

    def title_options(self):
        ready=self.story.status=='ready'
        return [('CONTINUE','',ready),('NEW GAME','',True),('QUIT','',True)]

    def title(self):
        draw_title(self,self.title_options(),self.i,self.notice,back=self.back_to_suite)

    def confirm(self):
        self.panel('SYSTEM / NEW GAME','START A NEW CAMPAIGN?','N CONFIRM NEW GAME  ESC KEEP CURRENT SAVE')
        self.lines(8,3,'Your old save will be copied to a separate backup before the new one replaces it.')

    def story_panel(self):
        title,body=STORY[self.prologue]
        self.panel('APRIL / SHUJIN',title,'ENTER SELECT  ESC TITLE')
        self.lines(8,3,body,limit=8)
        row,col,button,_=self.prologue_button()
        self.put(row,col,button,CYAN,True,True)

    def prologue_button(self):
        return 16,3,' ▶  CROSS THE DRAWBRIDGE  ','\n'

    def start_drill(self, back='map'):
        self.drill_back=back
        self.drill=0;self.drill_pick=0;self.drill_mask=0;self.drill_feedback='';self.page='drill'
    def drill_rows(self):
        if self.drill==2:
            return (('Eiha  Curse','Cleave  Physical','Rakunda  DEF down'),
                    ('Zio  Electric','Garu  Wind','Dia  Heal'),
                    ('Agi  Fire','Dazzler  Ailment','Rakunda  DEF down'))[self.drill_mask]
        return DRILL[self.drill-1][2]
    def draw_drill(self):
        if self.drill in (0,len(DRILL)+1):
            start=self.drill==0
            self.frame('FIELD DRILL','↵ BEGIN  ESC SKIP' if start else ('↵ BRIEF' if self.drill_back=='brief' else '↵ MAP'))
            self.mid(6,'PRACTICE BATTLE' if start else 'DRILL COMPLETE',GREEN,True)
            if start:self.lines(9,3,'Learn weaknesses, Baton Pass, and All-Out Attacks without risking your squad.')
            return
        guide='←→ PERSONA  ' if self.drill==2 else ''
        self.frame('FIELD DRILL',guide+'↑↓ PICK  ↵ CONFIRM  ESC SKIP')
        name,hint,_,_=DRILL[self.drill-1]
        self.put(4,3,f'{self.drill:02}/{len(DRILL)}  /  {name}',GOLD,True)
        self.lines(6,3,hint,limit=2)
        if self.drill==2:self.put(9,3,'[ '+('Arsène','Pixie',"Jack-o’-Lantern")[self.drill_mask]+' ]',CYAN,True)
        for i,name in enumerate(self.drill_rows()):
            x=3+(i//4)*((self.w-6)//2);y=11+i%4
            self.put(y,x,f'{"▶" if i==self.drill_pick else " "} {i+1} {name}',CYAN if i==self.drill_pick else WHITE)
        self.lines(19,3,self.drill_feedback,limit=2,color=GOLD)
    def drill_key(self,k):
        if k==ESC or (self.drill==len(DRILL)+1 and k in (*ENTER,' ')):
            self.page=self.drill_back;self.notice='';return
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
        transition_frame(self,self.chapters[self.ch+1],'ENTER OPEN MAP  ESC SKIP')

    def draw_map(self):
        map_screen(self,time.monotonic())

    def pass_practice(self):
        return not self.testing and self.node['id'] in ('spaceport-entry','spaceport-ranks')

    def story_offer(self,phase,node_id=None):
        if self.testing:return None
        return campaign_story.story_offer(node_id or self.node['id'],phase,
                           seen_clues=self.store.data.get('story_clues',()))

    def open_story_scene(self,scene,destination,*,checkpoint=None,beat=None):
        self.story_scene=campaign_story.StoryScene(scene,seen_clues=self.store.data.get('story_clues',()),
                                                   suspendable=checkpoint is not None)
        if beat is not None:self.story_scene.beat=beat
        self.scene_destination=destination
        self.scene_checkpoint=checkpoint
        self.notice='';self.page='story-scene'

    def key_story_scene(self,k):
        scene=self.story_scene
        previous=scene.beat
        close=scene.key(k)
        if getattr(scene,'requested_transition',None)==first_escape.FIGHT:
            scene.requested_transition=None
            if self.save_opening('infiltration:fight'):self.start_escape_fight()
            return
        clues=scene.clues.difference(self.store.data.get('story_clues',()))
        if clues:
            try:self.store.remember_clues(clues)
            except (CampaignError,ValueError,OSError) as exc:
                self.notice='Clue not saved: '+str(exc)
        checkpoint=self.scene_checkpoint
        if checkpoint=='opening' and not scene.suspended and (scene.beat!=previous or close):
            phase='casino' if scene.scene_id==campaign_story.COLD_OPEN else 'infiltration'
            step=('april:0' if phase=='casino' else None) if close else phase+':'+scene.beat
            if not self.save_opening(step):
                scene.beat=previous
                return
        if not close:return
        destination=self.scene_destination
        recruit=None
        if checkpoint not in (None,'opening') and not scene.suspended:
            try:self.store.finish_pending_story(checkpoint)
            except (CampaignError,ValueError,OSError) as exc:
                self.notice='Story checkpoint not saved: '+str(exc);return
            recruit=campaign_story.RECRUIT_HANDOFFS.get(checkpoint)
        self.scene_destination=None;self.story_scene=None;self.scene_checkpoint=None
        if scene.suspended:
            self.leave_map();return
        if checkpoint=='laboratory-choice' and self.campaign_complete():
            self.page='campaign-complete';self.i=0
        elif destination=='deploy':
            if scene.cancelled:self.page='brief'
            else:self.enter_operation()
        else:
            if destination=='result':self.played_after=True
            if destination=='resume-map':self.focus_campaign_map()
            else:self.page=destination
        if recruit:
            active=recruit in self.store.data['squad']
            self.notice=f'{recruit} joined your roster • '+('Active' if active else 'Standby')
        elif checkpoint=='pyramid-boss':
            self.notice='Oracle available • Moral Support, UFO Finisher'

    def start_escape_fight(self):
        self.story_scene=None;self.scene_destination=None;self.scene_checkpoint=None
        self.escape_fight=first_escape.EscapeFight(self.seed)
        self.notice='';self.page='escape-fight'

    def key_escape_fight(self,k):
        fight=self.escape_fight
        if k==C.KEY_MOUSE:
            k=campaign_story.clicked_story_button(fight.buttons(self.w))
            if k is None:return
        if k==ESC:self.leave_map();return
        if fight.battle.phase=='win':
            if k in ENTER and self.save_opening('infiltration:'+first_escape.RETURN_BEAT):
                self.open_story_scene(first_escape.SCENE_ID,'map',checkpoint='opening',beat=first_escape.RETURN_BEAT)
            return
        if fight.battle.phase=='loss':
            if k in ENTER:self.start_escape_fight()
            return
        fight.pick=self.nav(k,fight.pick,2)
        choose=self.commit(k,fight.pick,2)
        if choose is not None:
            fight.pick=choose
            if fight.act(('attack','guard')[choose])=='win':
                self.save_opening('infiltration:'+first_escape.RETURN_BEAT)

    def save_opening(self,step):
        try:return self.store.checkpoint_opening(step)
        except (CampaignError,ValueError,OSError) as exc:
            self.notice='Opening checkpoint not saved: '+str(exc);return False

    def focus_campaign_map(self):
        if not self.restore_focus or self.ch>=self.opened():self.ch=self.opened()-1;self.pick=self.near()
        self.restore_focus=False;self.story_visited=True
        bank_vault.reset_dials(self)
        self.notice='CAMPAIGN SAVE LOADED';self.page='map'

    def resume_campaign_story(self):
        data=self.store.data
        if step:=data.get('story_opening'):
            phase, beat=step.split(':',1)
            if phase=='casino':
                self.prologue=0
                self.open_story_scene(campaign_story.COLD_OPEN,'prologue',checkpoint='opening',beat=beat)
            elif phase=='infiltration':
                if beat=='fight':self.start_escape_fight()
                else:self.open_story_scene(first_escape.SCENE_ID,'map',checkpoint='opening',beat=beat)
            else:
                self.prologue=0;self.page='prologue';self.notice=''
            return True
        if (pending:=data.get('pending_story_after')) and (offer:=self.story_offer('after',pending)):
            self.open_story_scene(offer,'resume-map',checkpoint=pending)
            return True
        if self.campaign_complete():
            self.page='campaign-complete';self.i=0;self.notice=''
            return True
        return False

    def campaign_complete(self):
        data=self.store.data
        return not self.testing and len(data['cleared'])==len(self.by_id) and not data.get('pending_story_after')

    def draw_campaign_complete(self):
        self.panel('STORY','CAMPAIGN COMPLETE','↑↓ SELECT  ENTER SELECT  ESC TITLE')
        self.lines(8,3,f'All {len(self.by_id)} operations are clear. Your roster and medals are saved.',limit=2)
        self._b_list((('Return to Title','',True),('Replay Operations','',True)),
                     13,3,self.w-6,2,self.i,details=False)

    def open_trials(self):
        if self.cached_trials is None:self.battle_init()
        else:self.__dict__.update(self.cached_trials)
        self.page='trials'

    def pending_after(self):
        if self.testing or self.node is None:return None
        pending=self.store.data.get('pending_story_after')
        return pending if pending==self.node['id'] else None

    def open_after(self,offer):
        self.open_story_scene(offer,'result',checkpoint=self.pending_after())

    def after_scene(self):
        if (not self.first or self.error or self.played_after):return None
        return self.story_offer('after')

    def deploy(self):
        self.lab_route=None
        offer=(None if self.node['id'] in self.store.data['cleared'] else self.story_offer('before'))
        if offer:self.open_story_scene(offer,'deploy')
        else:self.enter_operation()

    def enter_operation(self):
        if self.node.get('press_console'):
            self.press_console=PressConsole();self.page='spaceport-press';self.notice=''
        elif room:=self.node.get('lab_room'):
            self.lab_route=LabInfiltration(self.node['id'],room);self.page='lab-route';self.notice=''
        else:self.stage()

    def deployment_label(self):
        if self.dials_required():return 'DIALS'
        if self.node.get('press_console'):return 'CONSOLE'
        if room:=self.node.get('lab_room'):return lab_entry_label(room)
        return 'DEPLOY'

    def briefing_story(self):
        review=self.story_offer('review')
        if review:return review,'REVIEW CLUE'
        if not self.testing and self.node['id'] in self.store.data['cleared']:
            if self.node['id']=='pyramid-murals':
                return self.story_offer('before'),'REVISIT MURAL'
            if story:=self.story_offer('after'):
                return story,'REVISIT STORY'
        return None,''

    def brief(self):
        n=self.node
        scene,caption=self.briefing_story()
        skin=brief_frame(self,self.chapters[self.ch]['id'],'◆ '+n['title'].upper(),
                   'ENTER '+self.deployment_label()+'  ESC MAP  S SQUAD  V VELVET'+('  H BATON DRILL' if self.pass_practice() else '')+
                   ('  C '+caption if scene else ''))
        self.lines(6,3,(not self.testing and n.get('story_before')) or n.get('brief',''),limit=4)
        self.put(10,3,(f'WAVES: {len(n["waves"])}   /   SQUAD: '+', '.join(['Joker',*stage_party(self.store,n)]))[:self.w-6],
                 skin.accent,True)
        self.lines(12,3,n.get('preview') or 'Opening formation: '+', '.join(n['waves'][0]),limit=3,color=DIM)
        self.put(15,3,'TACTICS',skin.accent,True)
        readiness=solo_readiness(self.store,n)
        self.lines(16,3,n.get('hint',''),limit=self.h-22 if readiness else self.h-20,color=WHITE)
        if readiness:self.lines(self.h-6,3,readiness,limit=2,color=GOLD)

    def dials_required(self):
        return (not self.testing and self.node['id']=='bank-vault' and self.dial<len(VAULT_WORDS)
                and 'bank-vault' not in self.store.data['cleared'])
    def draw_dials(self):
        bank_vault.draw_dials(self)
    def key_dials(self,k):
        bank_vault.key_dials(self,k)

    def open_squad(self,back):
        self.back=back;self.edit=list(self.store.data['squad']);self.i=0;self.page='squad';self.notice=''
    def squad_operation(self):
        return self.node if self.back in ('brief','result') else None

    def squad_names(self):
        data=self.store.data
        pending=campaign_story.RECRUIT_HANDOFFS.get(data.get('pending_story_after'))
        return ['Joker',*(n for n in TEAM if n!='Joker' and
                          (self.testing or (n in data['teammates'] and n!=pending)))]

    def draw_squad(self):
        d=self.store.data;names=self.squad_names()
        op=self.squad_operation()
        deployed=sum(name in names and not operation_unavailable(op,name) for name in self.edit)
        label='DEPLOY' if op else 'ALLIES'
        self.panel('PALACE / SQUAD',f'◆ {deployed}/{d["squad_slots"]} {label} + JOKER',
                   '↑↓ SELECT  ENTER TOGGLE  S APPLY SQUAD  ESC BACK')
        rows=[]
        for n in names:
            own=n=='Joker' or n in d['teammates']
            restricted=own and operation_unavailable(op,n)
            mark='⊘' if restricted else '●' if n=='Joker' or n in self.edit else '○' if own else '▣'
            role='Not on this operation' if restricted else 'Wild Card lead' if n=='Joker' else TEAM[n]['role']
            rows.append((f'{mark} {n}  /  '+role,'',own and not restricted))
        self._b_list(rows,6,3,self.w-6,9,self.i)
        n=names[self.i]
        if n=='Joker':
            if d['joker_hp'] or d['joker_sp']:
                self.put(17,3,f'+{d["joker_hp"]} HP  /  +{d["joker_sp"]} SP',CYAN)
        elif n in d['teammates']:
            if operation_unavailable(op,n):
                self.put(17,3,'Saved roster: '+('selected' if n in self.edit else 'standby')+'.',DIM)
                return
            self.put(17,3,f'{TEAM[n]["hp"]} HP  /  {TEAM[n]["sp"]} SP',CYAN)
            if d['team_skills'].get(n):
                self.lines(18,3,'Learned: '+', '.join(d['team_skills'][n]),limit=2,color=DIM)
        else:self.put(17,3,'This Thief has not joined the campaign.',DIM)

    def stage(self):
        try:b=build_stage(self.store,self.node['id'],self.seed)
        except (CampaignError,ValueError) as exc:self.notice='BLOCKED • '+str(exc);self.page='brief';return
        if self.lab_route is not None and self.lab_route.node_id==self.node['id']:self.lab_route.prepare(b)
        self.battle_init();self._b_battle=b
        self.casino_route=CasinoRoute() if self.node.get('wave_breaks') else None
        self._b_personas=getattr(b,'personas',self._b_personas);self._b_screen='command'
        self._b_prepare_presentation(b,time.monotonic())
        self.finished=None;self.reward=None;self.error=None;self.grade=None;self.first=False
        self.notice='';self.page='battle';self.played_after=False
        self.airlock_started=time.monotonic() if self.node['id'].startswith('spaceport-') else None

    def draw_casino_route(self):
        route=self.casino_route
        if route.leaving:
            self.panel('CASINO / PAUSED','RETURN TO THE PALACE MAP?','ENTER CONFIRM  ESC STAY')
            self.lines(8,3,'This attempt ends. Unfinished fights do not change campaign progress.')
            return
        heading={'dice':'DICE CONTROL ROOM','slots':'GIANT SLOT',
                 'darkness':'HOUSE OF DARKNESS','bridge':'BRIDGE OF JUDGMENT'}[route.stage]
        self.panel('CASINO / INFILTRATION',heading,'↑↓ SELECT  ↵ ACT  ESC LEAVE ATTEMPT')
        draw_route_art(self,route)
        if route.stage in ('dice','slots'):
            self.put(6,3,f'COINS  {route.coins:,}',GOLD,True)
        if route.stage=='bridge':
            self.put(6,3,f'DEPOSIT  {route.bridge_deposit:,} / {route.bridge_toll:,}',GOLD,True)
        if route.stage=='slots':
            self.mid(7,'[ 7 ]   [ 7 ]   [ 7 ]' if route.jackpot else '[   ]   [   ]   [   ]',
                     GOLD if route.jackpot else DIM,True)
        rows=route.rows()
        self._b_list([(r.label,'',not r.block) for r in rows],9,3,self.w-6,len(rows),route.pick)
        detail=route.notice or rows[route.pick].block
        if detail:self.lines(16,3,detail,limit=3,color=GOLD if route.notice else DIM)

    def key_casino_route(self,k):
        route=self.casino_route
        if route.leaving:
            if k==ESC:route.leaving=False
            elif k in ENTER:
                self.casino_route=None;self._b_battle=None;self.page='map'
                self.notice='ATTEMPT ENDED  /  Campaign save unchanged'
            return
        if k==ESC:route.leaving=True;return
        rows=route.rows()
        new_pick=self.nav(k,route.pick,len(rows))
        if new_pick!=route.pick:
            route.pick=new_pick;route.notice=''
        choose=self.commit(k,route.pick,len(rows))
        if choose is None:return
        route.pick=choose
        if not route.choose(rows[choose].id):return
        b=self._b_battle
        if route.stage=='slots':b._say('High Limit card acquired.')
        b.resume_wave()
        self._b_index=0
        self._b_prepare_presentation(b,time.monotonic())
        self.page='battle'
        self.record()

    def record(self,retry=False):
        b=self._b_battle
        if b.phase not in ('win','loss') or (self.finished is not None and not retry):return
        self.finished=time.monotonic()
        if b.phase=='loss':self.notice='';return
        self.grade=stage_grade(b)
        if self.testing:self.notice='';return
        self.first=self.node['id'] not in self.store.data['cleared']
        try:
            contract={'contract': b.contract} if getattr(b,'contract',None) is not None else {}
            if self.node['id'] in campaign_story.REQUIRED_AFTER:contract['queue_story']=True
            if updates:=getattr(b,'affinity_updates',None):contract['affinity_updates']=updates
            prior=self.store.data['squad']
            self.reward=self.store.clear(self.node['id'],self.grade,**contract);self.error=None
            self.activated=[name for name in self.store.data['squad'] if name not in prior]
            self.notice='AUTOSAVED  /  '+('FIRST CLEAR' if self.first else 'PERSONA REGISTERED' if self.reward else 'BEST MEDAL KEPT')
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
        if (self._b_battle.phase=='interlude'
                and not self._b_result_animation(now)):
            self.casino_route.open(self._b_battle.interlude)
            self.page='casino-route';self.draw_casino_route();return
        if (self.finished is not None and self._b_overlay is None and now-self.finished>=.68
                and not self._b_result_animation(now)):
            self.page='result';self.result();return
        self.battle_page()
        if self.airlock_started is not None and self._b_overlay is None and not self._b_cut_in:
            airlock(self,now-self.airlock_started)
        self.record()

    def field_lesson(self):
        if self.testing or self.ch!=0:return
        b=self._b_battle
        if b.phase!='turn' or not b.one_more:return
        if b.hold_up and 'allout' not in self.field_lessons:
            b._say('All Shadows are down. Try an All-Out Attack.')
            self.field_lessons.add('allout')
        elif not b.hold_up and 'baton' not in self.field_lessons and b.actions('baton'):
            b._say('Baton Pass hands this extra action to an ally.')
            self.field_lessons.add('baton')

    def chapter_final(self):
        return self.node['id']==self.nodes()[-1]['id'] and all(n['id'] in self.store.data['cleared'] for n in self.nodes())
    def new_chapter(self):
        return not self.testing and self.first and not self.error and self.chapter_final() and self.ch+1<self.opened()
    def result(self):
        win=self._b_battle.phase=='win'
        if self.testing:title='PRACTICE WIN' if win else 'PRACTICE DEFEAT'
        else:title=(self.label()+' SECURED' if self.chapter_final() else 'OPERATION CLEARED') if win else 'SQUAD DEFEATED'
        footer=('ENTER RETRY SAVE  ESC LEAVE' if self.error else
                'ENTER RETRY  A ADJUST LEAD  L LOG  ESC MAP' if not win else
                ('↵ STORY  ' if self.after_scene() else f'↵ {self.label(self.ch+1)}  ' if self.new_chapter() else '↵ MAP  ')+
                ('L LOG  S SQUAD  V CARDS  ESC TITLE' if self.pending_after() else 'R REPLAY  L LOG  S SQUAD  V CARDS  ESC MAP'))
        self.panel('PALACE / DEBRIEF','◆ '+title+'  //  '+self.node['title'].upper(),footer)
        if win:
            self.put(7,3,('PRACTICE MEDAL  ' if self.testing else 'MEDAL  ')+str(self.grade),GOLD,True)
            self.put(8,3,'S: all standing at 50%+ HP  A: ¾+ standing  B: otherwise',DIM)
        if self.error:self.lines(10,3,self.error,limit=4,color=RED);return
        if not win:
            diagnose=getattr(self._b_battle,'defeat_diagnosis',None)
            summary=diagnose() if diagnose else ()
            if not summary:
                fallback=getattr(self._b_battle,'loss_summary',lambda:'')()
                summary=(fallback,) if fallback else ()
            for i,detail in enumerate(summary[:2]):
                self.lines(8+i*3,3,detail,limit=2,color=GOLD if i==0 else DIM)
            return
        if self.testing:return
        y=10
        if self.reward:
            self.put(y,3,'FIRST-CLEAR REWARDS' if self.first else 'REPLAY REWARDS',CYAN,True);y+=1
            for field,label in (('credits','Credits'),('joker_hp','Joker HP'),('joker_sp','Joker SP'),('slots','Mask slots'),('squad_slots','Ally slots'),
                                ('teammates','Recruited'),('personas','Registered'),('skill_cards','Skill cards'),('oracle','Support')):
                v=self.reward.get(field)
                if field=='oracle' and v:
                    names={'support':'Moral Support','ufo':'UFO Finisher'}
                    v=tuple(names[item] for item in v if item in ACTIVE_ORACLE_FEATURES)
                if v:
                    if field=='teammates':
                        for name in v:
                            state='active' if name in self.store.data['squad'] else 'standby'
                            self.put(y,3,f'◆ {label}: {name} • {state}',WHITE);y+=1
                        continue
                    if field=='squad_slots':
                        added=[n for n in getattr(self,'activated',()) if n not in self.reward.get('teammates',())]
                        if added: label+=' (active: '+', '.join(added)+')'
                    self.put(y,3,f'◆ {label}: '+(', '.join(v) if isinstance(v,(list,tuple)) else '+'+str(v)),WHITE);y+=1
            for name,moves in self.reward.get('team_skills',{}).items():
                self.put(y,3,f'◆ {name} learned '+', '.join(moves),WHITE);y+=1
        if self.first and self.node.get('story_after') and y+1<self.h-5:
            self.lines(y+1,3,self.node['story_after'],limit=min(4,self.h-6-y),color=DIM)
        if not self.pending_after():
            if self.new_chapter():self.put(self.h-5,3,'NEW PALACE UNLOCKED  /  '+self.label(self.ch+1),GREEN,True)
            elif self.chapter_final():self.lines(self.h-5,3,self.chapters[self.ch].get('completion','Palace secured.'),limit=1,color=GREEN)

    def lead_choices(self):
        d=self.store.data
        return [d['primary'],*(name for name in d['stock'] if name!=d['primary'])]

    def draw_adjust_lead(self):
        d=self.store.data; choices=self.lead_choices(); name=choices[self.lead_pick]
        self.panel('PALACE / ADJUST LEAD','◆ STARTING PERSONA',
                   '↑↓ SELECT  ENTER APPLY  ESC CANCEL')
        self._b_list([(n,'Current' if n==d['primary'] else 'Carried' if n in d['loadout'] else 'In stock',
                       True) for n in choices],6,3,self.w-6,8,self.lead_pick,shortcut=False)
        spec=self.store.persona_spec(name)
        weak=', '.join(e for e,a in spec['affinity'].items() if a=='weak') or 'none'
        self.lines(16,3,f'{name} weaknesses: {weak}',limit=2,color=CYAN)
        availability=('Current lead' if name==d['primary'] else 'Already carried'
                      if name in d['loadout'] else 'In stock • not equipped')
        self.put(15,3,availability,DIM)
        if name not in d['loadout'] and len(d['loadout'])>=d['slots']:
            self.lines(19,3,f'{name} will take {d["primary"]}’s slot.',limit=2,color=GOLD)

    def key_adjust_lead(self,k):
        if k==ESC:self.page='result';self.notice='';return
        choices=self.lead_choices()
        self.lead_pick=self.nav(k,self.lead_pick,len(choices))
        if k not in ENTER:return
        d=self.store.data; name=choices[self.lead_pick]
        if name==d['primary']:self.page='result';return
        loadout=list(d['loadout'])
        if name not in loadout:
            if len(loadout)>=d['slots']:loadout[loadout.index(d['primary'])]=name
            else:loadout.append(name)
        if self.transact(lambda:self.store.equip_personas(loadout,name),'LEAD: '+name)[0]:
            self.page='result'

    def open_velvet(self,back,compendium=False):
        self.back=back;self.velvet_parent=None
        self._velvet_panel(compendium)
        self.velvet_started=time.monotonic();self.page='velvet-entrance'
    def draw_velvet_entrance(self):
        elapsed=time.monotonic()-self.velvet_started
        if elapsed>=velvet_entrance.DURATION:
            self.velvet_started=None;self.page='velvet'
            self.draw_velvet()
        else:self.draw_scene_rows(velvet_entrance.render(elapsed,self.w-1,self.h))
    def _velvet_panel(self,compendium=False):
        d=self.store.data
        self.mask_edit=list(d['loadout']);self.primary=d['primary']
        self.tab=int(compendium);self.i=0;self.notice='';self.page='velvet'
    def velvet_names(self):
        if self.tab:return list(self.store.data['personas'])
        return [r['result'] for r in getattr(content,'FUSIONS',())]
    def _velvet_chrome(self,room,heading,footer):
        velvet_menu.panel(self,room,heading,footer,practice=self.velvet_parent is not None)
    def draw_velvet(self):
        d=self.store.data;names=self.velvet_names()
        name=names[self.i] if names else None
        archived=self.tab and name not in d['stock']
        footer=(('←→ TAB  ↑↓ PICK  ENTER RESUMMON  ESC BACK' if archived
                 else '←→ TAB  ↑↓ PICK  E EQUIP  P LEAD  A CARD  S APPLY  ESC')
                if self.tab else '←→ TAB  ↑↓ PICK  ENTER PREVIEW  X PRACTICE  ESC BACK'
                if self.testing and self.velvet_parent is None
                else '←→ TAB  ↑↓ PICK  ENTER PREVIEW  ESC BACK')
        self._velvet_chrome('','',footer)
        velvet_menu.tabs(self,self.tab,d['credits'])
        x,width=velvet_menu.detail_split(self)
        if not names:self.put(6,3,'No entries.',DIM);return
        rows=[]
        for name in names:
            if self.tab:
                in_stock=name in d['stock']
                mark='★' if name==self.primary else '●' if name in self.mask_edit else '○' if in_stock else '·'
                rows.append((f'{mark} {name}',in_stock))
            else:
                f=self.store.fusion_options(name);r=f['recipe']
                mark='▣' if not f['available'] else '↻' if f['registered'] else '◆'
                rows.append((f'{mark} {name}  {r["cost"]} cr',f['available']))
        velvet_menu.selector(self,rows,6,3,x-7,self.h-12,self.i)
        name=names[self.i]
        self.put(6,x,name[:width],CYAN,True)
        if self.tab:
            spec=self.store.persona_spec(name)
            status=(f'Archived • {self.store.summon_preview(name)["cost"]} cr to summon' if archived
                    else f'{len(self.mask_edit)}/{d["slots"]} equipped  •  ★ lead')
            self.lines(8,x,status,width=width,limit=2,color=velvet_menu.STEEL)
            self.lines(10,x,', '.join(spec['skills']),width=width,limit=4)
            affinities=', '.join(f'{a} {v}' for a,v in spec['affinity'].items()) or 'Normal'
            self.lines(15,x,'Defense: '+affinities,width=width,limit=4,color=DIM)
        else:
            f=self.store.fusion_options(name)
            self.lines(8,x,' + '.join(f['recipe']['parents']),width=width,limit=2)
            if f['reason']:self.lines(11,x,f['reason'],width=width,limit=4,color=DIM)
            elif f['registered']:self.lines(11,x,'Already registered. Re-fusion can change its inherited skill.',width=width,limit=4,color=DIM)
    def donor_options(self):
        return [(None,None)]+[(n,k) for n,skills in self.fusion['donors'].items() for k in skills]
    def _fusion_selection(self):
        donor,skill=self.donor_options()[self.sub]
        return self.fusion['recipe']['result'],skill,donor
    def _fusion_price(self,r):
        cash=self.store.data['credits'];cost=r['cost']
        outcome=f'{cash-cost} AFTER' if cash>=cost else f'{cost-cash} SHORT'
        return f'PRICE {cost}  /  {cash} ON HAND  /  '+outcome
    def draw_fusion(self):
        name,skill,donor=self._fusion_selection()
        f=self.store.fusion_preview(name,skill,donor);r=f['recipe']
        footer=('↑↓ INHERITANCE  ENTER REVIEW  ESC BACK' if f['available']
                else '↑↓ INHERITANCE  ESC BACK')
        self._velvet_chrome('FUSION PREVIEW',' + '.join(r['parents'])+'  →  '+name,footer)
        self.put(6,3,self._fusion_price(r),CYAN)
        self.put(8,3,'Both parents leave stock but stay in the Compendium.',GOLD)
        velvet_menu.selector(self,[((k+' ← '+n) if k else 'No inherited skill',True)
                                   for n,k in self.donor_options()],10,3,self.w-7,7,self.sub)
        self.lines(18,3,f['reason'] or 'Result skills: '+', '.join(f['after']),
                   limit=2,color=GOLD if f['reason'] else DIM)
    def draw_fusion_confirm(self):
        name,skill,donor=self._fusion_selection()
        f=self.store.fusion_preview(name,skill,donor)
        verb='RE-FUSE ' if f['registered'] else 'FUSE '
        self._velvet_chrome('CONFIRM FUSION','◆ '+verb+name.upper(),
                           'ENTER CONFIRM FUSION  ESC CANCEL')
        self.put(6,3,self._fusion_price(f['recipe']),CYAN)
        self.lines(8,3,'Consume: '+', '.join(f['consumed']),limit=2,color=GOLD)
        self.put(10,3,'Parents stay in the Compendium.',DIM)
        self.lines(12,3,'Result skills: '+', '.join(f['after']),limit=2)
        if f['losses']:
            self.lines(14,3,'Replaces: '+', '.join(f['losses']),limit=1,color=GOLD)
        self.lines(15,3,'Equipped after fusion: '+', '.join(f['loadout']),limit=3,color=CYAN)
        self.put(18,3,'Lead: '+f['lead'],CYAN)
        if f['lead']!=self.store.data['primary'] or f['lead']==name:
            defenses=content.PERSONA_DATA[name]['affinity']
            weak=', '.join(e for e,effect in defenses.items() if effect=='weak') or 'none'
            self.lines(19,3,'Lead weaknesses: '+weak,limit=2,color=GOLD)
    def draw_summon(self):
        name=self.velvet_names()[self.i];preview=self.store.summon_preview(name)
        self._velvet_chrome('COMPENDIUM','◆ RESUMMON '+name.upper(),
                           'ENTER CONFIRM  ESC CANCEL' if preview['available'] else 'ESC BACK')
        self.put(6,3,self._fusion_price(preview),CYAN)
        self.lines(8,3,'Return to stock with: '+', '.join(self.store.persona_spec(name)['skills']),limit=3)
        if preview['reason']:self.put(12,3,preview['reason'],GOLD)
    def draw_cards(self):
        name=self.velvet_names()[self.i]
        cards=self.store.data['skill_cards']
        skill=list(cards)[self.sub] if cards else None
        reason=self.store.skill_card_block(name,skill) if skill else ''
        footer='↑↓ SELECT  ENTER APPLY ONE CARD  ESC CANCEL' if skill and not reason else '↑↓ SELECT  ESC BACK'
        self._velvet_chrome('SKILL CARDS','◆ APPLY A CARD TO '+name.upper(),footer)
        if not cards:self.put(7,3,'No skill cards found.',DIM)
        else:
            rows=[]
            for card,count in cards.items():
                blocked=bool(self.store.skill_card_block(name,card))
                rows.append((f'{card} ×{count}'+(' [UNAVAILABLE]' if blocked else ''),not blocked))
            velvet_menu.selector(self,rows,6,3,self.w-7,self.h-13,self.sub)
            self.lines(self.h-7,3,velvet_menu.card_description(skill),limit=1,color=CYAN)
            if reason:self.lines(self.h-6,3,reason,limit=2,color=GOLD)

    def start_story(self):
        ok,backup=self.transact(lambda:self.story.new_game(opening=True),'NEW CAMPAIGN')
        if not ok:return
        if backup:self.notice+='  •  Previous save backed up.'
        self.ch=self.pick=self.prologue=0;bank_vault.reset_dials(self);self.marks={}
        self.cached_trials=None;self.story_visited=True;self.restore_focus=False;self.page='prologue';self.field_lessons.clear()
        self.resume_campaign_story()
    def start_testing(self):
        self.story_view=(self.ch,self.pick,self.marks,self.node,self.cached_trials)
        if self.practice_view is None:
            self.store=TestingCampaign()
            self.ch=self.pick=0
            self.marks={};self.cached_trials=None
        else:
            self.store,self.ch,self.pick,self.marks,self.cached_trials=self.practice_view
        self.testing=True;self.node=None;self.notice='';self.page='map'

    def leave_map(self):
        if self.testing:
            self.practice_view=(self.store,self.ch,self.pick,self.marks,self.cached_trials)
            self.ch,self.pick,self.marks,self.node,self.cached_trials=self.story_view
            self.store=self.story;self.testing=False;self.story_view=None
            self.restore_focus=self.story_visited
        self.notice=''
        self.i=0 if self.story.status=='ready' else 1;self.page='title'

    def leave_result(self):
        self.page='map'
        if not self.testing:self.pick=self.near()

    def begin_extra(self,kind):
        if kind=='practice':
            self.start_testing()
        elif kind=='gallery':
            if self.gallery is None:self.gallery=AnimationGallery()
            self.notice='';self.page='gallery'
        else:raise ValueError(f'Unknown Persona 5 extra: {kind!r}')

    def run_extra(self,kind):
        """Open an Extras leaf without startup or a writable practice save."""
        self.begin_extra(kind)
        try:
            self.run(startup=False)
        finally:
            if self.testing:self.leave_map()
            elif self.page=='gallery':
                self.gallery.stop()
                self.page='title'

    def draw_departure(self):
        destination,unsaved=self.departure
        heading='DISCARD UNSAVED WIN?' if unsaved else 'QUIT THIS ATTEMPT?'
        self.frame('SYSTEM / CONFIRM','ENTER DISCARD  ESC CANCEL' if unsaved else 'ENTER QUIT  ESC STAY')
        self.put(4,3,heading,GOLD,True)
        if unsaved:
            self.lines(7,3,'The victory did not save. Cancelling lets you retry the save.')
        else:
            self.lines(7,3,'This attempt ends. Your existing campaign save is unchanged.')

    def key(self,k):
        kl=k.lower() if isinstance(k,str) else k
        if self.departure is not None:
            if k==ESC:self.departure=None
            elif k in ENTER:
                destination,unsaved=self.departure
                self.departure=None
                if destination=='quit':return False
                self.leave_result()
                if unsaved:self.notice='UNSAVED VICTORY DISCARDED'
            return True
        if kl=='q':
            b=getattr(self,'_b_battle',None)
            if self.page=='battle' and b.phase=='win':
                # An already committed win can exit immediately.
                self.record()
                if not self.error:return False
                self.page='result'
            if self.page=='result' and self.error:
                self.departure=('quit',True)
                return True
            active_trial=self.page=='trials' and b is not None and b.phase=='turn'
            if (self.page=='battle' and b.phase in ('turn','interlude')
                    or self.page=='casino-route' or active_trial):
                self.departure=('quit',False)
                return True
            return False
        page=self.page
        if page=='title':
            count=len(self.title_options())
            self.i=self.nav(k,self.i,count);choose=self.commit(k,self.i,count)
            if choose==0:
                status=self.story.reload()
                if self.story.status=='ready':
                    if not self.resume_campaign_story():self.focus_campaign_map()
                else:self.notice='BLOCKED • No readable campaign save.'
            elif choose==1:
                self.story.reload()
                if self.story.status=='missing':self.start_story()
                else:self.page='confirm';self.notice=''
            elif choose==2:return False
        elif page=='gallery':
            if not self.gallery.key(self,k):return False
        elif page=='confirm':
            if k==ESC:self.page='title';self.notice='CURRENT SAVE KEPT'
            elif kl=='n':self.start_story()
        elif page=='campaign-complete':
            self.i=self.nav(k,self.i,2)
            choose=self.commit(k,self.i,2)
            if k==ESC or choose==0:self.leave_map()
            elif choose==1:self.focus_campaign_map()
        elif page=='story-scene':self.key_story_scene(k)
        elif page=='escape-fight':self.key_escape_fight(k)
        elif page=='spaceport-press':
            press=self.press_console.key(self,k)
            if press=='back':self.press_console=None;self.page='brief'
            elif press=='cross':self.press_console=None;self.stage()
        elif page=='lab-route':
            route=self.lab_route.key(self,k)
            if route=='back':self.lab_route=None;self.page='brief'
            elif route=='deploy':self.stage()
        elif page=='prologue':
            if k==C.KEY_MOUSE and campaign_story.button_clicked(self.prologue_button()):k='\n'
            if k==ESC:self.leave_map()
            elif k in (*ENTER,' ',C.KEY_RIGHT):
                if self.save_opening('infiltration:start'):
                    self.open_story_scene(self.story_offer('before',first_escape.SCENE_KEY),'map',checkpoint='opening')
        elif page=='drill':self.drill_key(k)
        elif page=='transition':
            if k in (*ENTER,ESC,' ',C.KEY_RIGHT):
                self.switch(1);self.page='map';self.notice=self.label()+' ROUTE OPEN  /  AUTOSAVED'
        elif page=='map':
            old=self.pick
            self.pick=self.nav(k,self.pick,len(self.nodes()))
            if k==ESC:
                if self.testing:return False
                self.leave_map()
            elif k in (C.KEY_LEFT,C.KEY_RIGHT) and self.opened()>1:self.switch(1 if k==C.KEY_RIGHT else -1)
            elif kl in ('h','?') and not self.testing:self.start_drill()
            elif kl=='s':self.open_squad('map')
            elif kl=='v':self.open_velvet('map')
            elif kl=='t' and self.testing:self.open_trials()
            else:
                choose=self.commit(k,self.pick,len(self.nodes()))
                if choose is not None:
                    self.pick=choose;n=self.nodes()[choose]
                    if self.store.can_play(n['id']):
                        self.palace_timeline.cue(self.chapters[self.ch]['id'],choose,time.monotonic())
                        self.node=n;self.page='brief';self.notice=''
                    else:self.notice=''  # The selected map row already explains the lock.
                elif old!=self.pick:self.notice=''
        elif page=='brief':
            if k==ESC:self.page='map';self.notice=''
            elif kl=='s':self.open_squad('brief')
            elif kl=='v':self.open_velvet('brief')
            elif kl=='h' and self.pass_practice():self.start_drill('brief')
            elif kl=='c' and (offer:=self.briefing_story()[0]):self.open_story_scene(offer,'brief')
            elif k in ENTER:
                if self.dials_required():self.page='dials';self.notice=''
                else:self.deploy()
        elif page=='dials':self.key_dials(k)
        elif page=='casino-route':self.key_casino_route(k)
        elif page=='squad':
            names=self.squad_names();d=self.store.data
            if k==ESC:self.page=self.back;self.notice=''
            elif kl=='s':
                if self.transact(lambda:self.store.equip_squad(self.edit),'SQUAD EQUIPPED')[0]:self.page=self.back
            else:
                self.i=self.nav(k,self.i,len(names));choose=self.commit(k,self.i,len(names))
                if choose is not None:
                    self.i=choose;n=names[choose]
                    if n=='Joker':self.notice='Joker is always active.'
                    elif n not in d['teammates']:self.notice='LOCKED • This Thief has not joined.'
                    elif operation_unavailable(self.squad_operation(),n):self.notice=n+' is not on this operation.'
                    elif n in self.edit:self.edit.remove(n);self.notice=n+' moved to standby.'
                    elif len(self.edit)>=d['squad_slots']:
                        locked=[name for name in self.edit if operation_unavailable(self.squad_operation(),name)]
                        self.notice=(f'{locked[0]} holds a saved slot. Edit from the map.' if locked
                                     else 'BLOCKED • Remove an active ally first.')
                    else:self.edit.append(n);self.notice=n+' selected. Press S to apply.'
        elif page=='velvet-entrance':
            if k in (*ENTER,ESC,' '):
                self.velvet_started=None;self.page='velvet'
        elif page=='velvet':
            if k==ESC:
                self.notice=''
                if self.velvet_parent is not None:
                    self.store=self.velvet_parent;self.velvet_parent=None
                    self._velvet_panel()
                else:self.page=self.back
            elif kl=='x' and self.testing and self.velvet_parent is None and not self.tab:
                self.velvet_parent=self.store
                self.store=TestingCampaign(fusion_practice=True)
                self._velvet_panel()
            elif k in (C.KEY_LEFT,C.KEY_RIGHT) and hasattr(self.store,'fusion_options'):
                self.tab=1-self.tab;self.i=0;self.notice=''
            else:
                names=self.velvet_names()
                if not names:return True
                self.i=self.nav(k,self.i,len(names));choose=self.commit(k,self.i,len(names));name=names[self.i]
                if not self.tab and choose is not None:
                    self.i=choose;self.fusion=self.store.fusion_options(names[choose]);self.sub=0;self.page='fusion';self.notice=''
                elif self.tab:
                    if choose is not None:
                        self.i=choose
                        if k in ENTER and names[choose] not in self.store.data['stock']:
                            self.page='summon';self.notice=''
                    elif kl in ('e','p','a') and name not in self.store.data['stock']:
                        self.notice='Resummon this Persona first.'
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
            elif k in ENTER or kl=='f':
                name,skill,donor=self._fusion_selection()
                preview=self.store.fusion_preview(name,skill,donor)
                if not preview['available']:self.notice='BLOCKED • '+preview['reason']
                else:self.page='fusion-confirm';self.notice=''
            else:
                old=self.sub
                self.sub=self.nav(k,self.sub,len(opts));choose=self.commit(k,self.sub,len(opts))
                if choose is not None:self.sub=choose
                if old!=self.sub:self.notice=''
        elif page=='fusion-confirm':
            if k==ESC:self.page='fusion';self.notice=''
            elif k in ENTER:
                name,skill,donor=self._fusion_selection()
                ok,_=self.transact(lambda:self.store.fuse(name,skill,donor,revise=self.fusion['registered']),
                                   'FUSED '+name)
                if ok:
                    done=self.notice;self._velvet_panel(True)
                    self.i=self.velvet_names().index(name);self.notice=done
        elif page=='summon':
            if k==ESC:self.page='velvet';self.notice=''
            elif k in ENTER:
                name=self.velvet_names()[self.i]
                if self.transact(lambda:self.store.summon(name),'RESUMMONED '+name)[0]:
                    self.page='velvet'
        elif page=='cards':
            cards=list(self.store.data['skill_cards'])
            if k==ESC:self.page='velvet';self.notice=''
            elif cards:
                self.sub=self.nav(k,self.sub,len(cards));choose=self.commit(k,self.sub,len(cards))
                if choose is not None:
                    self.sub=choose
                    name=self.velvet_names()[self.i];skill=cards[choose]
                    if not self.store.skill_card_block(name,skill):
                        if self.transact(lambda:self.store.apply_skill_card(name,skill),name+' LEARNED '+skill)[0]:self.page='velvet'
        elif page=='battle':
            if self._b_overlay in ('resume','abandon') and k in ENTER:
                if self._b_overlay=='abandon':self.stage()
                else:self.page='map';self.notice='ATTEMPT ENDED  /  Campaign save unchanged'
            elif (self._b_battle.phase=='turn'
                  or self._b_overlay is not None or self._b_cut_in):
                self.battle_key(k);self.field_lesson();self.record()
        elif page=='result':
            win=self._b_battle.phase=='win'
            if k==ESC:
                if self.error:self.departure=('map',True)
                elif win and self.pending_after():self.leave_map()
                else:self.leave_result()
            elif k in ENTER and self.error:self.record(retry=True)
            elif k in ENTER and win:
                if offer:=self.after_scene():self.open_after(offer)
                elif self.new_chapter():self.page='transition'
                else:self.leave_result()
            elif k in ENTER or (kl=='r' and not self.error and not self.pending_after()):self.stage()
            elif kl=='l' and not self.error:self._b_overlay='log';self._b_log_scroll=0;self.page='result-log'
            elif not win and kl=='a':self.lead_pick=0;self.page='adjust-lead';self.notice=''
            elif win and not self.error and kl=='s':self.open_squad('result')
            elif win and not self.error and kl=='v':self.open_velvet('result',True)
        elif page=='adjust-lead':self.key_adjust_lead(k)
        elif page=='result-log':
            self.battle_key(k)
            if self._b_overlay is None:self.page='result'
        elif page=='trials':
            self.battle_key(k)
            if self.page==-1:
                self.cached_trials={k:v for k,v in vars(self).items() if k.startswith('_b_')}
                self.page='map';self.notice=''
        return True

    def run(self,*,back_to_suite=False,startup=True):
        self.back_to_suite=back_to_suite
        draw={'title':self.title,'confirm':self.confirm,'prologue':self.story_panel,'transition':self.transition,
              'campaign-complete':self.draw_campaign_complete,
              'escape-fight':lambda:self.escape_fight.draw(self),'spaceport-press':lambda:self.press_console.draw(self),
              'casino-route':self.draw_casino_route,'story-scene':lambda:self.story_scene.draw(self),
              'lab-route':lambda:self.lab_route.draw(self),
              'map':self.draw_map,'drill':self.draw_drill,'brief':self.brief,'dials':self.draw_dials,'squad':self.draw_squad,
              'velvet-entrance':self.draw_velvet_entrance,
              'velvet':self.draw_velvet,'fusion':self.draw_fusion,'fusion-confirm':self.draw_fusion_confirm,
              'summon':self.draw_summon,'cards':self.draw_cards,'battle':self.draw_combat,'result':self.result,
              'result-log':self.battle_page,'adjust-lead':self.draw_adjust_lead,'trials':self.battle_page,
              'gallery':lambda:self.gallery.draw(self)}
        started=None
        fast=False
        opener_mouse=False
        while True:
            self.s.erase();self.h,self.w=self.s.getmaxyx()
            small=self.h<25 or self.w<65
            if small:
                if self.departure is not None:
                    self.mid(max(0,self.h//2-1),'Discard unsaved win?' if self.departure[1] else 'Quit this attempt?',GOLD)
                    self.mid(self.h//2,'ENTER YES  ESC CANCEL',WHITE)
                else:self.mid(self.h//2,'Widen the terminal to at least 65 × 25. Q quits.',GOLD)
            else:
                if startup:
                    now=time.monotonic()
                    if started is None:started=now
                    if now-started>=STARTUP_SECONDS:startup=False
                    else:draw_startup(self,now-started)
                if not startup:
                    if self.departure is not None:self.draw_departure()
                    else:draw[self.page]()
            wants_mouse=(not startup and not small and (self.page in ('prologue','escape-fight') or
                         (self.page=='story-scene' and self.story_scene.mouse_enabled())))
            if wants_mouse!=opener_mouse:
                self._mouse(C.BUTTON1_CLICKED if wants_mouse else 0)
                opener_mouse=wants_mouse
            self.s.refresh()
            animate=not small and (startup or self.page=='velvet-entrance'
                or (self.page=='gallery' and self.gallery.started is not None)
                or (self.page in ('battle','trials','result-log') and self._b_cut_in is not None))
            if animate!=fast:
                self.s.timeout(32 if animate else 80)
                fast=animate
            try:k=self.s.get_wch()
            except C.error:continue
            if startup:
                if k in ('q','Q'):return
                if not small and k in (*ENTER,ESC,' '):startup=False
                continue  # A skip is never sent to the live menu.
            if not small and back_to_suite and k==ESC and self.page=='title':return True
            if (not small or self.departure is not None or k in ('q','Q')) and not self.key(k):
                if opener_mouse:self._mouse(0)
                return False
