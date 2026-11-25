"""Playable Persona 3 field chapter, isolated from every Persona 5 route."""
import curses as C
import random
import textwrap
import time
from datetime import timedelta

from battle_ui import CYAN, DIM, ENTER, ESC, GOLD, GREEN, RED, WHITE
from reel_palette import IDS
from terminal_surface import TerminalSurface
import persona3_opening as opening
import persona3_state as state_runtime
import persona3_late as late
import persona3_junpei as junpei
from persona3_operation_route import OperationRoute, OPERATION_ROUTE_PAGES
from persona3_summit import APPROACH, SUMMIT_LEVEL
import persona3_late_registry as registry
from persona3_late_route import LateRoute,LATE_BATTLES,LATE_DATED
import persona3_arqa as arqa
import persona3_upper as upper
import persona3_yabbashah as yabba
import persona3_yabbashah_upper as high
import persona3_combat as combat
import persona3_cards as reward_cards
import persona3_calendar_ui as calendar_ui
import persona3_field_recovery as field_recovery
import persona3_field_clues as field_clues
from persona3_field_checkpoint import FieldCheckpoint
from dataclasses import replace
import persona3_velvet_ui as velvet_ui
import persona3_briefing_ui as briefing_ui
import persona3_discovery_schedule as discovery
from persona3_dorm_notice import note_for as dorm_note_for, lounge_line as dorm_lounge_line
from persona3_state import (AWAKENING_XP, FLOOR_XP, MOON,
                            REPLAY_XP, SUMMON_PRICE, TUTORIAL, AWAKENING, P3SaveError, available_fusions, next_story_date)
from persona3_thebel import FLOORS, H, W, Hall

BLUE=IDS['navy']
TEAL=IDS['teal']
MOVES={C.KEY_UP:'up',C.KEY_DOWN:'down',C.KEY_LEFT:'left',C.KEY_RIGHT:'right',
       'w':'up','s':'down','a':'left','d':'right'}
ACTIVITIES=(
    ('library','Library','Academics +1 and ¥60 for Compendium summons.'),
    ('track','Track practice','Courage +1, one field kit and an extra Medicine tonight.'),
    ('lounge','Dorm lounge','Charm +1; +15 HP and +8 SP after the first victory tonight.'),
)
PARTY=(combat.LEAD_ID,'Yukari','Junpei')
BLOCKS={'thebel':(FLOORS,22,FLOOR_XP),'arqa':(arqa.FLOORS,arqa.BORDER,arqa.FLOOR_XP),
        'upper':(upper.FLOORS,upper.BORDER,upper.FLOOR_XP),
        'yabba':(yabba.FLOORS,yabba.BORDER,yabba.FLOOR_XP),
        high.BLOCK:(high.FLOORS,high.BORDER,high.FLOOR_XP),**registry.BLOCKS}
BLOCK_OPENS=dict((('thebel',None),('arqa',arqa.OPENS),('upper',upper.OPENS),
                  ('yabba',yabba.OPENS),(high.BLOCK,high.OPENS),*registry.OPENS.items()))
BLOCK_NAMES={'thebel':'Thebel','arqa':'Lower Arqa','upper':'Upper Arqa','yabba':'Lower Yabbashah',high.BLOCK:'Upper Yabbashah',**registry.NAMES}
MONAD_STAGES={**yabba.MONAD_STAGES,high.PASSAGE:high.PASSAGE_STAGES,
              **{row[0]:row[1] for row in registry.PASSAGES.values()}}
HOTEL_BATTLES=('hotel-hierophant','hotel-lovers')
HOTEL_LOCKED=(combat.LEAD_ID,'Yukari')
HOTEL_RESERVES=('Junpei','Akihiko','Mitsuru')
HOTEL_CAPACITY=2
HOTEL_ROLES=('Wild Card lead','Healing / Wind','Slash / Fire','Strike / Electric','Ice / Support')
FOOT='↑↓ CHOOSE  ENTER OPEN  ESC TITLE'
FULL_MOONS=frozenset((AWAKENING,MOON,arqa.RESCUE_DAY,upper.HOTEL_DAY,
                     yabba.AUGUST_MOON,high.HERMIT_DAY,late.OCT,late.NOV,late.FINALE))


class P3App(LateRoute,OperationRoute,TerminalSurface):
    def __init__(self,screen,store,seed=None):
        self.s=screen;self.store=store;self.seed=seed
        self.late_route_init()
        self.page='';self.i=0;self.notice='';self.exit=None
        self.scene='';self.started=0.;self.back='';self.overlay=''
        self.hall=None;self.resources={};self.caps={};self.inventory={};self.battle=None
        self.retries=0;self.sp_bonus=False;self.practice=False
        self.resume_hall=None;self.free_expedition=False;self.practice_depth=0;self.practice_aid=0
        self.guided_expedition=False;self.expedition_back=''
        self.block='thebel';self.practice_arqa=0;self.charge={}
        self.recovery_seen=False;self.teleport_target=None;self.warp_start=1
        self.search_step=0;self.practice_party=None;self.expedition_store=None
        self.heal_back=None;self.aid_index=0;self.velvet_return_index=0
        self.practice_upper=0;self.hotel_party=None;self.mirror_index=0
        self.hotel_edit=list(HOTEL_RESERVES[:HOTEL_CAPACITY])
        self.rescue_return=None;self.mirror_observation=False
        self.practice_yabba=0;self.practice_yabba_upper=0;self.monad_route=None;self.monad_index=0
        self.temperance_bonus=0;self.practice_monad=set();self.roster_pick=set();self.roster_for='field'
        self.recipe_i=0;self.inherit_i=0;self.fuse_skill='';self.summon_name=''
        self.theurgy_back='evening';self.theurgy_deploy=False
        self.patrol_rng=random.Random(seed)
        if (getattr(state_runtime,'VERSION',0)<11 or
                not all(hasattr(store.state,field) for field in ('upper','rescues','yabba','monad','fragments','yabba_upper','adamah','ending','junpei_flowers','theurgy_drill_seen','arqa_tag_seen','aftermath','field_checkpoint'))):
            self.go('restart-needed')
        else:self.resume()

    def draw_restart_needed(self):
        # This screen must not read the older record or attempt a write.
        self.mid(7,'PERSONA 3 / RESTART NEEDED',CYAN,True)
        self.mid(10,'This terminal is still running the previous version.',WHITE)
        self.mid(12,'Close it and reopen Persona Terminal.',WHITE)
        self.mid(14,'Reopening does not reset your save.',TEAL)
        self.mid(self.h-2,'ENTER BACK  Q QUIT',DIM)

    @property
    def record(self):
        return self.loadout_store.state

    @property
    def loadout_store(self):
        return self.expedition_store if self.expedition_store is not None else self.store

    def go(self,page):
        self.page=page;self.i=0;self.notice=''
        if page=='entrance':self.i=self.entrance_default()

    def beat(self,scene):
        self.scene=scene
        self.go('story')

    def resume(self):
        phase=self.record.phase
        if self.record.field_checkpoint:
            self.resume_field_checkpoint()
            return
        if self.record.aftermath:
            key=self.record.aftermath
            if key.startswith('monorail-'):self.start_train_brake(stopped=key=='monorail-stopped')
            else:self.beat(key)
            return
        if junpei.payoff_due(self.record):
            self.late_story=junpei.PAYOFF;self.go('late-interlude');return
        if self.resume_late():return
        if phase=='arrival':self.discover('arrival')
        elif phase in ('awakening','tartarus','complete'):
            scene={'complete':'august-after','tartarus':'briefing' if not self.record.depth else 'tartarus'}
            self.beat(scene.get(phase,phase))
        elif phase in ('monorail','rescue'):self.go('operation')
        elif phase=='hotel':self.go('hotel')
        elif phase=='yakushima':
            if self.record.day in (yabba.YAKUSHIMA,yabba.BEACH):
                self.discover('villa' if self.record.day==yabba.YAKUSHIMA else 'shore')
            else:self.go('yakushima')
        elif phase in ('august','hermit'):self.go(phase)
        elif self.record.day==high.OPENS:self.beat('koromaru')
        elif phase=='calendar' and self.record.activity in (row[0] for row in ACTIVITIES):self.go('evening')
        else:self.go('calendar')

    def write(self,fn,*args,**kw):
        try:fn(*args,**kw)
        except (OSError,P3SaveError) as err:
            self.notice=str(err)
            return False
        return True

    def frame(self,title,footer,status=''):
        self.put(1,2,'◆ SEES / FIELD TERMINAL',CYAN,True)
        tag=status or self.record.day.strftime('%m/%d  %a').upper()
        self.put(1,self.w-3-len(tag),tag,TEAL,True)
        self.put(2,2,'━'*(self.w-4),BLUE)
        self.put(4,3,title,CYAN,True)
        self.put(self.h-3,2,'━'*(self.w-4),BLUE)
        self.mid(self.h-2,footer,TEAL)
        if self.notice:self.put(self.h-4,3,self.notice[:self.w-6],GOLD,True)

    def lines(self,y,x,text,width=None,count=4,color=WHITE):
        for n,line in enumerate(textwrap.wrap(text,width or self.w-6)[:count]):
            self.put(y+n,x,line,color)

    def choices(self,items,y=8,x=3,width=None,step=2):
        width=width or self.w-x-3
        for index,item in enumerate(items):
            text=item[0] if isinstance(item,tuple) else item
            color=item[1] if isinstance(item,tuple) else WHITE
            prefix='◆' if index==self.i else ' '
            line=f'{prefix} {index+1} {text}'[:width].ljust(width)
            self.put(y+index*step,x,line,CYAN if index==self.i else color,
                     index==self.i,index==self.i)

    def choose(self,k,length):
        self.i=self._b_nav(k,self.i,length)
        pick=self._b_commit(k,self.i,length)
        if pick is not None:self.i=pick
        return pick

    def draw_scene_rows(self,rows,*,top=0,left=0):
        for y,row in enumerate(rows,top):
            x=left
            for run,ink in row:
                if run.strip():self.put(y,x,run,{'white':WHITE,'gold':GOLD,'green':GREEN,
                    'cyan':CYAN,'red':RED}.get(ink,IDS.get(ink,DIM)))
                x+=len(run)

    def art(self,key,t,y=5,height=9):
        self.draw_scene_rows(opening.render(key,t,self.w-5,height),top=y,left=2)

    def draw_story(self):
        beat={'finale':opening.BY_ID['finale'],'signal':arqa.SIGNAL,'bridge':arqa.BRIDGE_BEAT,
              'hotel-after':upper.AFTER,'august-after':yabba.AFTER_BEAT,
              'koromaru':opening.Beat('koromaru','08/08','A NEW MEMBER',high.KOROMARU_INTRO,'dorm'),
              'hermit-after':opening.Beat('hermit-after','09/06','AFTER ESCAPADE',high.HERMIT_AFTER,'dorm')}.get(self.scene)
        if beat is None:beat=opening.BY_ID[self.scene]
        primary={'awakening':'Call on Orpheus','briefing':'Go with S.E.E.S.',
                 'tartarus':'Enter Tartarus'}.get(self.scene)
        story_choices=(primary,) if primary else ()
        if self.scene=='bridge':
            story_choices=('Continue to squad' if self.theurgy_deploy else 'Return to the dorm',
                           'Replay the drill' if self.record.theurgy_drill_seen else 'Try the drill')
        footer={'hotel-after':'ENTER CALENDAR  ESC TITLE','august-after':'ENTER CALENDAR  T PRACTICE  V VELVET  ESC TITLE', 'hermit-after':'ENTER CALENDAR  T PRACTICE  V VELVET  ESC TITLE'}.get(self.scene,'ENTER NEXT  ESC TITLE')
        if primary:footer='ENTER SELECT  ESC TITLE'
        if self.scene=='bridge':footer='↑↓ SELECT  ENTER CHOOSE  ESC BACK'
        self.frame(beat.heading,footer)
        art_height=min(9,self.h-19) if story_choices else 9
        if self.scene=='hotel-after':self.hotel_art('exit')
        else:self.art(beat.art,opening.TRANSITION_SECONDS,height=art_height)
        top=6+art_height
        for line in beat.lines:
            wrapped=textwrap.wrap(line,self.w-8)
            for item in wrapped:
                if top>=self.h-(4+len(story_choices)):break
                self.put(top,4,item)
                top+=1
        if story_choices:self.choices(story_choices,min(self.h-4-len(story_choices),max(top+1,19)),4,step=1)

    def _story_key(self,k):
        if k==ESC:
            if self.scene=='bridge':self.go(self.theurgy_back)
            else:self.exit=True
            return
        if self.scene in ('august-after','hermit-after'):
            if k in ('t','T'):
                self.open_field_party();return
            if k in ('v','V'):
                self.open_velvet('story');return
        if self.scene=='bridge':
            pick=self.choose(k,2)
            if pick==1:self.open_battle('theurgy-drill')
            elif pick==0:
                if not self.theurgy_intro_seen and not self.write(self.store.commit,theurgy_intro_seen=True):
                    return
                if self.theurgy_deploy:self.open_roster('field',self.theurgy_back)
                else:self.go(self.theurgy_back)
            return
        if k not in ENTER and not (k=='1' and self.scene in ('awakening','briefing','tartarus')):return
        if self.scene in ('finale','signal','hotel-after','august-after','koromaru','hermit-after'):
            if self.record.aftermath==self.scene and not self.write(self.store.advance_boss_aftermath):return
            self.go('calendar')
        elif self.scene=='awakening':self.open_battle('awakening')
        elif self.scene=='briefing':self.beat('tartarus')
        elif self.scene=='tartarus':self.deploy()

    @property
    def next_operation(self):
        return next_story_date(self.record.day,flower=self.record.junpei_flowers) or late.FINALE

    @property
    def event_label(self):
        day=self.next_operation
        names={arqa.BRIDGE:'THEURGY TRAINING',yabba.OPENS:'YABBASHAH OPENS',
               yabba.YAKUSHIMA:'YAKUSHIMA TRIP',high.OPENS:'UPPER YABBASHAH OPENS',
               late.DECISION:'RYOJI RETURNS',junpei.INVITATION:'JUNPEI',
               junpei.FIRST_SHOP_DAY:'AFTER SCHOOL',junpei.PAYOFF_DAY:'HOSPITAL VISIT',
               late.CHIDORI:'EVENING OPERATION',
               **{day:'MISSING-PERSON REPORT' for day in upper.REPORT_DAYS},
               **discovery.EVENT_NAMES,
               **{d:registry.NAMES[k].upper()+' OPENS' for k,d in registry.OPENS.items()},
               **{d:('DORM BRIEFING' if d in (late.BRIDGE,late.AIGIS) else title.split(' / ')[-1])
                  for d,title in late.STORY_NAMES.items()}}
        return names.get(day,'FULL MOON' if day in FULL_MOONS else 'NEXT EVENT')

    @property
    def arqa_open(self):
        return self.record.day>=arqa.OPENS

    @property
    def upper_open(self):
        return self.record.day>=upper.OPENS

    @property
    def open_blocks(self):
        return tuple(name for name,day in BLOCK_OPENS.items() if day is None or day<=self.record.day)

    def active_rescues(self):
        s=self.record
        return tuple(x for x in upper.RESCUES if x.day<=s.day<=upper.RESCUE_DEADLINE and x.id not in s.rescues)

    @property
    def fuuka_active(self):
        return self.record.day>=arqa.AFTER_RESCUE

    @property
    def theurgy_active(self):
        return self.record.day>=arqa.BRIDGE

    @property
    def theurgy_intro_seen(self):
        return self.record.theurgy_intro_seen or self.record.theurgy_drill_seen

    @property
    def current_party(self):
        if self.theurgy_active and self.practice_party:
            return tuple(n for n in self.practice_party if n!='Shinjiro' or self.record.day<=late.SHINJIRO_THROUGH)
        return (*PARTY,'Akihiko') if self.record.day>=arqa.AKIHIKO_JOINS else PARTY

    @property
    def aigis_active(self):
        return self.record.day>=yabba.AIGIS

    @property
    def roster_choices(self):
        names=('Yukari','Junpei','Akihiko','Mitsuru')
        if self.aigis_active:names=(*names,'Aigis')
        if self.record.day>=high.OPENS:names=(*names,'Koromaru')
        if self.record.day>=late.KEN:names=(*names,'Ken')
        if late.SHINJIRO<=self.record.day<=late.SHINJIRO_THROUGH:names=(*names,'Shinjiro')
        blocked={'hermit':('Junpei',),'october':('Ken','Shinjiro'),'chidori':('Junpei',)}
        names=tuple(n for n in names if n not in blocked.get(self.roster_for,()))
        return names

    def open_field_party(self):
        if self.page=='evening' and self.theurgy_active and not self.theurgy_intro_seen:
            self.open_theurgy_training(deploy=True)
        else:self.open_roster('field',self.page)

    def open_theurgy_training(self,*,deploy=False):
        self.theurgy_back,self.theurgy_deploy=self.page,deploy
        self.beat('bridge')

    def open_roster(self,purpose,back):
        self.roster_for=purpose
        self.roster_back=back
        self.roster_pick=set((self.late_party if purpose=='summit' and self.late_party else self.current_party)[1:]) & set(self.roster_choices)
        if purpose in ('hermit','october','chidori') and len(self.roster_pick)<3:
            for name in self.roster_choices:
                self.roster_pick.add(name)
                if len(self.roster_pick)==3:break
        self.go('roster')
        self._roster_started=time.monotonic()

    def draw_roster(self):
        title={'august':'AUGUST 6 / SQUAD','hermit':'SEPTEMBER 5 / SQUAD','october':'OCTOBER 4 / SQUAD',
               'november':'NOVEMBER 3 / SQUAD','hanged':'MOONLIGHT BRIDGE / SQUAD','chidori':'NOVEMBER 22 / SQUAD','finale':'JANUARY 31 / SQUAD','summit':'SUMMIT / SQUAD'}.get(self.roster_for,'TARTARUS / SQUAD')
        choices=self.roster_choices
        absence={'hermit':'Junpei is absent.','chidori':'Junpei is absent.',
                 'october':'Ken and Shinjiro are absent.'}.get(self.roster_for,'')
        summit=self.roster_for in ('finale','summit')
        resources=combat.party_caps(self.deployment_level(summit),party=choices)[choices[self.i]]
        now=time.monotonic()
        elapsed=now-getattr(self,'_roster_started',now-briefing_ui.ROSTER_SECONDS)
        briefing_ui.draw_roster(self,briefing_ui.Roster(title,choices,frozenset(self.roster_pick),
                                                       resources,absence),elapsed)

    def _roster_key(self,k):
        if k==ESC:self.go(self.roster_back);return
        if k in ('s','S'):
            self.practice_party=(combat.LEAD_ID,*(n for n in self.roster_choices if n in self.roster_pick))
            if self.roster_for=='august':self.open_battle('chariot-justice')
            elif self.roster_for=='hermit':self.open_battle('hermit')
            elif self.roster_for in (*late.OPERATION,'summit','hanged'):
                self.start_late_roster(self.roster_for,self.practice_party)
            else:self.deploy()
            return
        pick=self.choose(k,len(self.roster_choices))
        if pick is None:return
        name=self.roster_choices[pick]
        if name in self.roster_pick:self.roster_pick.remove(name)
        elif len(self.roster_pick)==3:self.notice='Remove an active ally first.';return
        else:self.roster_pick.add(name)
        self.notice=''

    def draw_hermit(self):
        from persona3_club_art import render
        self.frame('SEPTEMBER 5 / CLUB ESCAPADE','ENTER SQUAD  V VELVET  T PRACTICE  ESC TITLE')
        self.draw_scene_rows(render(self.w-5,9),top=5,left=2)
        self.lines(15,4,high.HERMIT_BRIEF[0],count=3)

    def _hermit_key(self,k):
        if k==ESC:self.exit=True
        elif k in ('v','V'):self.open_velvet('hermit')
        elif k in ('t','T'):self.open_field_party()
        elif k in ENTER:self.open_roster('hermit','hermit')

    def draw_yakushima(self):
        part=0 if self.record.day==yabba.YAKUSHIMA else 1 if self.record.day==yabba.BEACH else 2
        title,_,lines=yabba.TRIP[part]
        self.frame(title,'ENTER CONTINUE  ESC TITLE')
        self.draw_scene_rows(yabba.shore(part,self.w-5,9),top=5,left=2)
        self.lines(15,4,lines[0],count=4)

    def _yakushima_key(self,k):
        if k==ESC:self.exit=True
        elif k in ENTER and self.write(self.store.trip_next):self.resume()

    def draw_august(self):
        self.frame('AUGUST 6 / UNDERGROUND PASSAGE','ENTER SQUAD  V VELVET  T PRACTICE  ESC TITLE')
        self.art('tartarus',opening.TRANSITION_SECONDS,height=8)
        self.lines(15,4,'Strega sealed the way out. Fuuka has a Shadow reading deeper in the bunker.',count=2)

    def _august_key(self,k):
        if k==ESC:self.exit=True
        elif k in ('v','V'):self.open_velvet('august')
        elif k in ('t','T'):self.open_field_party()
        elif k in ENTER:self.open_roster('august','august')

    def options(self):
        s=self.record
        if not s.activity:
            extra=junpei.option(s)
            return ([row[1] for row in ACTIVITIES]+['Head to the dorm']
                    +([extra[1]] if extra else [])
                    +(['Wait for next event'] if self.calendar_wait_available else []))
        return self.evening_options()

    @property
    def calendar_wait_available(self):
        s=self.record
        return (s.phase=='calendar' and not s.activity and not s.aftermath
                and not s.field_checkpoint
                and next_story_date(s.day,flower=s.junpei_flowers) is not None)

    def draw_calendar(self):
        s=self.record
        stage='EVENING' if s.activity else 'DAYTIME' if s.day.weekday()==6 else 'AFTER SCHOOL'
        cases=self.active_rescues()
        footer=FOOT+('  R CASES' if cases else '')
        self.frame(f'{s.day.strftime("%B").upper()} / {stage}',footer)
        if any(case.day==s.day for case in cases) and not self.notice:
            self.put(self.h-4,3,'Elizabeth filed a missing-person report.',GOLD,True)
        new_reports={person.day for person in upper.RESCUES
                     if person.id not in s.rescues and s.day<=person.day}
        if cases:new_reports.add(s.day)
        events={arqa.BRIDGE,yabba.OPENS,yabba.YAKUSHIMA,high.OPENS,*late.MAJOR_DAYS}
        if s.day<=junpei.INVITATION and not s.junpei_flowers:events.add(junpei.INVITATION)
        if s.junpei_flowers=='spoken':events.add(junpei.FIRST_SHOP_DAY)
        if s.junpei_flowers=='given':events.add(junpei.PAYOFF_DAY)
        block=self.open_blocks[-1]
        field='depth' if block=='thebel' else block
        stats=((self.level_text(),CYAN),
               ('02F / FIRST SURVEY' if self.first_survey_due else
                f'{BLOCK_NAMES[block]} {getattr(s,field)}/{len(BLOCKS[block][0])}',TEAL),
               (f'¥{s.yen}   FIELD KITS {s.aid}',WHITE),
               (f'ACA {s.academics}  COU {s.courage}  CHA {s.charm}',DIM))
        detail=''
        if not s.activity and self.i<3:detail=ACTIVITIES[self.i][2]
        extra=junpei.option(s)
        if extra and self.i==4:detail=extra[2]
        choices=self.options()
        wait_selected=self.calendar_wait_available and self.i==len(choices)-1
        upcoming=(self.event_label,self.next_operation) if s.activity or wait_selected else ()
        calendar_ui.draw(self,calendar_ui.CalendarView(
            s.day, FULL_MOONS,frozenset(new_reports),frozenset(events),stats,
            tuple(choices),detail,upcoming))

    def _calendar_key(self,k):
        if k in ('r','R') and self.active_rescues():self.open_rescues();return
        if k==ESC:self.exit=True;return
        options=self.options()
        pick=self.choose(k,len(options))
        if pick is None:return
        if self.calendar_wait_available and pick==len(options)-1:
            self.overlay='wait'
            return
        if not self.record.activity and not self.practice:
            extra=junpei.option(self.record)
            if pick==4 and extra:
                if self.write(self.store.junpei,extra[0]):
                    self.go('evening');self.notice=junpei.CONFIRMATION[extra[0]]
                return
            if pick<3:
                if self.write(self.store.activity,ACTIVITIES[pick][0]):
                    self.go('evening')
                    if pick==2:self.notice=dorm_lounge_line(self.record.day)
            else:
                # Going straight to the dorm leaves this day's stat unchanged.
                self.practice=True
                self.go('evening')
            return
        self._evening_action(pick)

    def draw_evening(self):
        s=self.record
        moon=min((day for day in FULL_MOONS if day>s.day),default=None)
        rescues=self.active_rescues()
        deadlines=[]
        if rescues:
            cases='CASE' if len(rescues)==1 else 'CASES'
            deadlines.append(f'{len(rescues)} {cases}  /  UNTIL {upper.RESCUE_DEADLINE:%m/%d}')
        if junpei.option(s,evening=True):deadlines.append(f'FLOWERS  /  UNTIL {junpei.LAST_GIFT_DAY:%m/%d}')
        block=self.open_blocks[-1]
        floors,border,_=BLOCKS[block]
        depth=getattr(s,'depth' if block=='thebel' else block)
        if depth<len(floors):
            checkpoint=floors[depth]
            field_next=f'NEXT: {checkpoint.number:02d}F'+(' • GATEKEEPER' if checkpoint.guardian else '')
        elif block=='adamah':
            field_next=f'{border}F • SUMMIT {late.FINALE:%m/%d}'
        else:
            field_next=f'{border:02d}F BORDER • SEALED'
        if self.first_survey_due:field_next='02F / FIRST SURVEY'
        briefing_ui.draw_evening(self,briefing_ui.Briefing(s.day,self.next_operation,self.event_label,
            moon,tuple(self.evening_options()),BLOCK_NAMES[block].upper(),f'{depth}/{len(floors)}',
            field_next,tuple(deadlines),bool(rescues),dorm_note_for(s.day),
            self.thebel_hint))

    @property
    def thebel_hint(self):
        if MOON<self.record.day<arqa.RESCUE_DAY and self.record.depth<len(FLOORS):
            return 'Thebel still open'
        return ''

    def level_text(self):
        s=self.record
        remaining=s.next_level_at
        return f'LV {s.level}  XP {s.xp}'+(f'/{remaining}' if remaining is not None else '  MAX')

    def evening_options(self):
        wait={arqa.BRIDGE:'Wait for the training day',yabba.OPENS:'Wait for Yabbashah',
              late.CHIDORI:'Wait for the evening operation',
              yabba.YAKUSHIMA:'Wait for Yakushima',high.OPENS:'Wait for Upper Yabbashah',
              late.DECISION:'Wait for Ryoji',late.FINALE:'Wait for January 31',
              junpei.INVITATION:'Wait for November 7',junpei.FIRST_SHOP_DAY:'Wait until tomorrow',
              junpei.PAYOFF_DAY:'Wait for January 21',
              **{day:'Wait for the next case report' for day in upper.REPORT_DAYS},
              **{d:'Wait for '+registry.NAMES[k] for k,d in registry.OPENS.items()},
              **{d:'Wait for '+n.title() for d,n in late.STORY_NAMES.items()}}.get(self.next_operation,'Wait for the full moon' if self.next_operation in FULL_MOONS else 'Wait for the next event')
        extra=junpei.option(self.record,evening=True)
        return (['Enter Tartarus','Velvet Room','Rest until tomorrow',wait]
                +(['Replay Theurgy drill' if self.record.theurgy_drill_seen else 'Theurgy field test']
                  if self.theurgy_active else [])+([extra[1]] if extra else []))

    def _evening_action(self,pick):
        if pick==0:
            if self.theurgy_active:self.open_field_party()
            else:self.deploy()
        elif pick==1:self.open_velvet(self.page)
        elif pick==2:
            if self.deadline_warnings(self.record.day+timedelta(days=1)):self.overlay='rest'
            else:self.next_night()
        elif pick==3:self.overlay='wait'
        elif pick==4 and self.theurgy_active:self.open_theurgy_training()
        else:
            extra=junpei.option(self.record,evening=True)
            if extra and self.write(self.store.junpei,extra[0]):
                self.go('evening');self.notice=junpei.CONFIRMATION[extra[0]]

    def _evening_key(self,k):
        if k in ('r','R') and self.active_rescues():self.open_rescues();return
        if k==ESC:self.practice=False;self.go('calendar');return
        pick=self.choose(k,len(self.evening_options()))
        if pick is not None:self._evening_action(pick)

    def deadline_warnings(self,target):
        s=self.record
        warnings=[]
        if s.day<=upper.RESCUE_DEADLINE<target and len(s.rescues)<len(upper.RESCUES):
            warnings.append('Any remaining missing-person cases will expire.')
        if s.junpei_flowers in ('spoken','bought') and s.day<=junpei.LAST_GIFT_DAY<target:
            warnings.append('You’ll miss your chance to bring Junpei the flowers.')
        return tuple(warnings)

    def next_night(self,skip=False):
        if self.write(self.store.advance_night,skip=skip):
            self.hall=None
            self.resume_hall=None
            self.practice=False
            if self.record.phase in ('monorail','rescue'):
                self.recovery_seen=False
                self.go('operation')
            elif self.record.phase=='hotel':self.go('hotel')
            elif self.record.phase in ('yakushima','august','hermit',*late.PHASE_DAYS,*discovery.CHECKPOINTS) or self.record.day in (high.OPENS,high.AFTER_HERMIT,junpei.PAYOFF_DAY,*late.STORY_DAYS,*late.INTERLUDES):self.resume()
            else:self.go('calendar')

    @property
    def floors(self):
        return BLOCKS[self.block][0]

    @property
    def field_depth(self):
        if self.block in registry.BLOCKS:return self.practice_late[self.block] if self.free_expedition else getattr(self.record,self.block)
        if self.block==high.BLOCK:return self.practice_yabba_upper if self.free_expedition else self.record.yabba_upper
        if self.block=='yabba':return self.practice_yabba if self.free_expedition else self.record.yabba
        if self.block=='upper':return self.practice_upper if self.free_expedition else self.record.upper
        if self.block=='arqa':return self.practice_arqa if self.free_expedition else self.record.arqa
        return self.practice_depth if self.free_expedition else self.record.depth

    @property
    def field_kits(self):
        return self.practice_aid if self.free_expedition else self.record.aid

    @property
    def first_survey_due(self):
        return self.record.day<MOON and self.record.depth==0

    def deploy(self):
        self.started=time.monotonic()
        story_practice=(self.scene in ('august-after','hermit-after') and
                        (self.page=='story' or self.page=='roster' and self.roster_back=='story'))
        self.free_expedition=(story_practice or
                              self.record.phase in ('complete','monorail','rescue','hotel','august','hermit',*late.OPERATION))
        self.expedition_store=self.store.practice_copy() if self.free_expedition else None
        self.expedition_back='story' if story_practice or self.record.phase=='complete' else 'late-brief' if self.record.phase in late.OPERATION else self.record.phase if self.record.phase in ('hotel','august','hermit') else 'operation'
        self.block=self.open_blocks[-1]
        self.practice_depth=self.record.depth
        self.practice_arqa=self.record.arqa
        self.practice_upper=self.record.upper
        self.practice_yabba=self.record.yabba
        self.practice_yabba_upper=self.record.yabba_upper
        self.practice_late={name:getattr(self.record,name) for name in registry.BLOCKS}
        self.temperance_bonus=2 if any(x in self.record.monad for x in (yabba.PASSAGE,high.PASSAGE)) else 0
        self.monad_route=None;self.practice_monad=set()
        self.charge={}
        self.warp_start=1
        self.practice_aid=self.record.aid
        patrol_seed=None if self.seed is None else self.seed ^ self.record.day.toordinal()
        self.patrol_rng=random.Random(patrol_seed)
        self.guided_expedition=not self.free_expedition and self.first_survey_due
        self.sp_bonus=self.record.activity=='lounge' and not self.free_expedition
        self.caps=combat.party_caps(self.record.level) if self.current_party==PARTY else combat.party_caps(self.record.level,party=self.current_party)
        self.resources=dict(self.caps)
        self.inventory=dict(combat.BAG)
        if self.record.activity=='track' and not self.free_expedition:self.inventory['Medicine']+=1
        self.resume_hall=None
        self.hall=Hall(0) if self.guided_expedition else None
        self.go('dark-hour')

    def draw_dark_hour(self):
        elapsed=time.monotonic()-self.started
        first=self.guided_expedition
        if elapsed>=calendar_ui.departure_length(first):
            self.go('hall' if first else 'entrance');self.draw();return
        self.draw_scene_rows(calendar_ui.departure(elapsed,self.w-1,self.h,first=first))

    def entrance_targets(self):
        depth=self.field_depth
        targets=[]
        if self.resume_hall is not None:
            targets.append(('resume',f'Resume {self.resume_hall.floor.number:02d}F'))
        if self.guided_expedition:
            if not depth:targets.append((0,'02F / Entry Hall'))
            return tuple(targets)
        targets.extend((i,f'{self.floors[i].number:02d}F / Revisit') for i in range(depth))
        if depth<len(self.floors):
            targets.append((depth,f'{self.floors[depth].number:02d}F / Continue ascent'))
        else:
            boundary=BLOCKS[self.block][1]
            status='Block Crossing' if self.next_block else 'Sealed Border'
            targets.append(('border',f'{boundary:02d}F / {status}'))
        return tuple(targets)

    def entrance_default(self):
        targets=self.entrance_targets()
        return 0 if self.resume_hall is not None else max(0,len(targets)-1)

    def border_detail(self):
        following=self.next_block
        if following:return f'Cross into {BLOCK_NAMES[following]}.'
        if self.block=='adamah':
            if self.record.day>=late.FINALE:return 'Enter the summit from the January 31 briefing.'
            return f'Summit opens {late.FINALE:%B} {late.FINALE.day}.'
        blocks=tuple(BLOCK_OPENS)
        next_block=blocks[blocks.index(self.block)+1]
        opens=BLOCK_OPENS[next_block]
        return f'{BLOCK_NAMES[next_block]} opens {opens:%B} {opens.day}. Return on or after that date.'

    def draw_entrance(self):
        from persona3_elevator_ui import LiftView, Stop, draw

        footer=('←→ BLOCK  ' if self.arqa_open else '')+'↑↓ FLOOR  ↵ GO  H HEAL  V VELVET  X '+('END' if self.free_expedition else 'EXIT')
        if self.active_rescues() and not self.free_expedition:footer+='  R CASES'
        if self.record.day>=yabba.OPENS:footer+='  C CLOCK'
        self.frame('TARTARUS / ELEVATOR',footer)
        boundary=BLOCKS[self.block][1]
        stops=[]
        for target,label in self.entrance_targets():
            mapped=True
            if target=='border':
                floor=boundary
                next_block=self.next_block
                kind='crossing' if next_block else 'border'
                detail=self.border_detail()
            elif target=='resume':
                floor=self.resume_hall.floor.number
                kind='resume'
                mapped=self.resume_hall.block==self.block
                detail=('Return to your place on this floor.' if mapped else
                        f'Resume in {BLOCK_NAMES[self.resume_hall.block]}.')
            else:
                checkpoint=self.floors[target]
                floor=checkpoint.number
                kind='revisit' if target<self.field_depth else 'ascent'
                label=f'{floor:02d}F'
                named=checkpoint.guardian or checkpoint.label in ('ENTRY HALL','MONAD LANDING')
                if floor in registry.PASSAGES or yabba.MONAD_FLOOR.get(floor)==yabba.PASSAGE:
                    label+=' Monad Passage'
                elif named:
                    label+=' '+' '.join(word.capitalize() for word in checkpoint.label.split())
                if kind=='revisit':
                    detail=(f'{checkpoint.guardian} defeated. Patrols only.' if checkpoint.guardian
                            else f'{checkpoint.label.title()}. Fresh patrols.')
                else:
                    detail=(f'Gatekeeper: {checkpoint.guardian}' if checkpoint.guardian
                            else checkpoint.label.title())
            stops.append(Stop(label,floor,detail,kind,mapped))
        blocks=self.open_blocks
        index=blocks.index(self.block)
        previous=BLOCK_NAMES[blocks[index-1]] if len(blocks)>1 else ''
        following=BLOCK_NAMES[blocks[(index+1)%len(blocks)]] if len(blocks)>1 else ''
        draw(self,LiftView(self.block,BLOCK_NAMES[self.block],
                          'practice' if self.free_expedition else 'story',
                          tuple(stops),self.i,self.floors[0].number,boundary,
                          self.field_depth,len(self.floors),self.field_kits,
                          self.record.fragments if self.record.day>=yabba.OPENS else None,
                          f'LV {self.record.level}',tuple(BLOCKS).index(self.block)+1,len(BLOCKS),previous,following))
        if self.thebel_hint and self.block=='arqa':
            self.put(self.h-5,4,'← Return to Thebel',TEAL)

    def go_entrance(self,*,resume=False):
        self.resume_hall=self.hall if resume else None
        self.warp_start=self.hall.floor.number if self.hall is not None else BLOCKS[self.block][1]
        self.hall=None
        self.go('entrance')

    def _select_floor(self,index):
        if not 0<=index<=min(self.field_depth,len(self.floors)):
            self.notice='That floor has not been reached.'
            return
        self.resume_hall=None
        if index==len(self.floors):
            self.hall=None
            self.go('border')
            return
        replay=index<self.field_depth
        offset=self.patrol_rng.randrange(len(self.floors[index].patrol)) if replay else 0
        self.hall=Hall(index,replay=replay,patrol_offset=offset,floors=self.floors,block=self.block)
        self.go('hall')

    def _entrance_key(self,k):
        if k in ('c','C') and self.record.day>=yabba.OPENS:
            self.overlay='clock';return
        if k in ('r','R') and self.active_rescues() and not self.free_expedition:
            self.open_rescues();return
        if k in ('v','V'):
            self.open_velvet('entrance')
            return
        if k in ('x','X',ESC):
            self.overlay='extract'
            return
        if self.arqa_open and k in (C.KEY_LEFT,C.KEY_RIGHT):
            blocks=self.open_blocks
            self.block=blocks[(blocks.index(self.block)+(1 if k==C.KEY_RIGHT else -1))%len(blocks)]
            self.i=self.entrance_default()
            return
        entries=self.entrance_targets()
        if k=='\t':
            self.i=next((i for i,(target,_) in enumerate(entries) if target=='border'),self.entrance_default())
            return
        pick=self.choose(k,len(entries))
        if pick is None:return
        target,_=entries[pick]
        if self.arqa_open:
            if target=='resume':destination=self.resume_hall.floor.number
            elif target=='border':destination=BLOCKS[self.block][1]
            else:destination=self.floors[target].number
            self.teleport_target=(target,destination)
            self.started=time.monotonic()
            self.go('teleport')
        else:self._finish_teleport(target)

    def _finish_teleport(self,target):
        if target=='resume':
            self.hall,self.resume_hall=self.resume_hall,None
            self.block=self.hall.block
            self.go('hall')
        elif target=='border':self._select_floor(len(self.floors))
        else:self._select_floor(target)

    def draw_teleport(self):
        from persona3_menu_motion import ELEVATOR_SECONDS,render_elevator
        elapsed=time.monotonic()-self.started
        target,destination=self.teleport_target
        if elapsed>=ELEVATOR_SECONDS:
            self._finish_teleport(target);self.draw();return
        self.draw_scene_rows(render_elevator(elapsed,self.w-1,self.h,self.warp_start,destination))

    def end_expedition(self):
        if self.free_expedition:
            self.hall=None
            self.resume_hall=None
            self.free_expedition=False
            self.expedition_store=None
            if self.expedition_back=='story':self.beat('hermit-after' if self.record.day==high.AFTER_HERMIT else 'august-after')
            else:self.go(self.expedition_back)
        else:
            guided=self.guided_expedition
            self.next_night()
            if guided:
                self.notice=('02F mapped. The first Tartarus survey is complete.' if self.record.depth
                             else 'Survey unfinished. Return to 02F next evening.')

    def draw_hall(self):
        hall=self.hall
        floor=hall.floor
        sealed=not hall.stairs_open
        floor_type=(('GATEKEEPER FLOOR' if floor.guardian else 'SHADOW FLOOR') if sealed
                    else 'REVISIT / PATROL' if hall.replay and not hall.defeated else 'FLOOR CLEARED')
        footer=('ARROWS MOVE' if self.guided_expedition else 'MOVE')+'  H HEAL  T ENTRANCE  X EXTRACT'
        contact=self.floor_rescue
        if contact:footer+='  R RESCUE'
        if self.active_monad:footer+='  G MONAD'
        landmark=self.hall_landmark
        close=self.near_landmark
        if close:footer+='  E LOOK'
        if not sealed and hall.pos==floor.stairs:footer+='  ↵ STAIRS'
        self.frame(f'{floor.number:02d}F / {floor_type}',footer)
        ox,oy=4,7
        outline=RED if sealed and floor.guardian else IDS['violet'] if self.block!='thebel' else BLUE
        self.put(6,ox-1,'╔'+'═'*W+'╗',outline)
        self.put(oy+H,ox-1,'╚'+'═'*W+'╝',outline)
        for y in range(H):
            self.put(oy+y,ox-1,'║',outline);self.put(oy+y,ox+W,'║',outline)
            for x in range(W):
                ch=hall.glyph(x,y)
                if contact and (x,y)==contact.pos and (x,y) in hall.seen and (x,y)!=hall.pos:ch='!'
                if landmark==(x,y) and (x,y) in hall.seen and ch=='·':ch='¤'
                color={'¤':GOLD,'@':CYAN,'▒':IDS['violet'] if self.block!='thebel' else BLUE,'·':DIM,'⇧':CYAN,'◆':RED,'⊗':RED,'!':GOLD}.get(ch,WHITE)
                if ch!=' ':self.put(oy+y,ox+x,ch,color,ch in '@◆⇧⊗!¤')
        self.draw_hall_party(34)
        detail_y=19 if len(self.resources)>3 else 18
        if sealed:
            label=floor.guardian or ('SHADOW CLOSE' if hall.alert else floor.label)
            self.lines(detail_y,34,label,self.w-37,1,RED if floor.guardian or hall.alert else GOLD)
            goal='Reach the sealed stairs. Clear the Shadow.' if self.guided_expedition else 'Step onto the sealed stairs to fight.'
            self.lines(detail_y+1,34,goal,self.w-37,2,GOLD)
            legend='@ You   ◆ Shadow   ⊗ Battle'
        else:
            self.put(detail_y,34,'STAIRS OPEN',CYAN,True)
            if hall.replay and not hall.defeated:
                self.lines(detail_y+1,34,'Shadows still patrol here.',self.w-37,1,TEAL)
                legend='@ You   ◆ Shadow   ⇧ Stairs'
            else:legend='@ You   ⇧ Stairs'
        self.put(19,4,legend,DIM)
        if contact:
            x,y=contact.pos;hx,hy=hall.pos
            clue='! Survivor nearby' if abs(hx-x)+abs(hy-y)<=1 else 'Survivor: '+(
                ('N' if y<hy else 'S' if y>hy else '')+('W' if x<hx else 'E' if x>hx else ''))
            self.put(18,4,clue,GOLD)
        self.put(20,4,f'KITS {self.field_kits}   '+self.level_text(),TEAL)
        if close and not contact:self.put(18,4,'¤ Something on the rail' if floor.number==23 else '¤ A chalk mark',GOLD)
        if self.active_monad:self.put(18,4,'◆ Monad Door' if self.active_monad==yabba.DOOR else '◆ Monad Passage',GOLD)

    def draw_hall_party(self,x):
        width=min(22,self.w-x-15)
        count=len(self.resources)
        for i,name in enumerate(self.resources):
            y=5+i*(3 if count>3 else 5)
            hp,sp=self.resources[name]
            max_hp,max_sp=self.caps[name]
            self.put(y,x,combat.display_name(name),WHITE if hp else RED,True)
            tracks=(('HP',hp,max_hp,GREEN if hp*4>=max_hp else RED),
                    ('SP',sp,max_sp,CYAN))
            for row,(label,current,cap,ink) in enumerate(tracks,y+1):
                fill,empty=combat.hp_meter(current,cap,width)
                self.put(row,x,label,ink)
                self.put(row,x+3,fill,ink)
                self.put(row,x+3+len(fill),empty,DIM)
                self.put(row,x+width+5,f'{current:>3}/{cap:<3}',WHITE)

    def _stairs(self):
        if self.guided_expedition:
            self.end_expedition()
        else:self._select_floor(self.hall.index+1)

    @property
    def floor_rescue(self):
        if self.hall is None or self.free_expedition:return None
        person=upper.BY_FLOOR.get(self.hall.floor.number)
        return person if person in self.active_rescues() else None

    def open_rescues(self):
        self.rescue_return=(self.page,self.i)
        self.go('rescue-board')

    def draw_rescue_board(self):
        self.frame('ELIZABETH / MISSING PERSONS','ESC BACK')
        for y,person in enumerate(self.active_rescues(),8):
            self.put(y,4,f'{person.floor}F  {person.name}',WHITE)
        self.put(13,4,'Last search night: July 6.',GOLD)

    def _rescue_board_key(self,k):
        if k==ESC:
            where,index=self.rescue_return
            self.go(where)
            self.i=index

    @property
    def hall_landmark(self):
        hall=self.hall
        return field_clues.LOWER_ARQA_CLUES.get(hall.floor.number) if hall and hall.replay and hall.block=='arqa' else None

    @property
    def near_landmark(self):
        point=self.hall_landmark
        return bool(point and point in self.hall.seen and
                    sum(abs(a-b) for a,b in zip(point,self.hall.pos))<=1)

    def draw_field_clue(self):
        floor=self.hall.floor.number
        self.frame(f'{floor:02d}F / STAIR RAIL','ENTER/ESC BACK')
        rows=list(field_clues.DESCRIPTIONS[floor])
        if floor==35 and self.record.arqa_tag_seen:rows.insert(1,field_clues.CALLBACK)
        for i,line in enumerate(rows):self.lines(8+i*3,4,line,count=2)

    def _hall_key(self,k):
        if k in ('e','E') and self.near_landmark:
            if (self.hall.floor.number==23 and not self.record.arqa_tag_seen and
                    not self.write(self.loadout_store.commit,arqa_tag_seen=True)):
                return
            self.go('field-clue')
            return
        if k in ('g','G') and self.active_monad:
            self.monad_route=self.active_monad
            self.monad_index=0
            self.go('monad')
            return
        if k in ('r','R') and self.floor_rescue:
            person=self.floor_rescue
            x,y=self.hall.pos
            if abs(x-person.pos[0])+abs(y-person.pos[1])>1:
                self.notice='Move closer to the survivor.'
                return
            if self.write(self.store.rescue_civilian,person.id,self.hall.floor.number):
                reward=f'¥{person.yen}'+(' + Field Kit' if person.kits else '')
                self.notice=f'{person.name} escorted to safety. {reward}'
            return
        if k in ('t','T',ESC):self.go_entrance(resume=True);return
        if k in ('x','X'):self.overlay='extract';return
        if k in ('m','M'):
            if self._use_aid(self._recovery_options()[0]):
                self.notice=f'First aid restored up to {field_recovery.KIT_HP} HP.'
            return
        if k in ENTER and self.hall.pos==self.hall.floor.stairs and self.hall.stairs_open:self._stairs()
        elif k in MOVES:
            nextstep=self.hall.step(MOVES[k])
            if nextstep=='battle':self.open_battle(self.hall.encounter)
            elif nextstep=='stairs':self._stairs()

    @property
    def next_block(self):
        blocks=self.open_blocks
        n=blocks.index(self.block)+1
        return blocks[n] if n<len(blocks) else None

    def draw_border(self):
        cross=self.next_block
        boundary=BLOCKS[self.block][1]
        footer='↵ CROSS  T ENTRANCE  H HEAL  X EXTRACT' if cross else 'ENTER ENTRANCE  H HEAL  X EXTRACT'
        self.frame(f'{boundary:02d}F / {BLOCK_NAMES[self.block].upper()} BORDER',footer)
        self.art('thebel',opening.TRANSITION_SECONDS,height=10)
        self.lines(17,4,f'The stairs into {BLOCK_NAMES[cross]} are open.' if cross else
                   self.border_detail(),count=2)

    def draw_operation(self):
        rescue=self.record.phase=='rescue'
        if rescue:
            beat=arqa.FOUND if self.recovery_seen else arqa.RESCUE
            footer='ENTER FIGHT' if self.recovery_seen else 'ENTER SEARCH'
        else:
            beat=opening.BY_ID['monorail']
            footer='ENTER BOARD'
        self.frame(beat.heading,footer+'  V VELVET  T PRACTICE  ESC TITLE')
        if rescue:
            from persona3_menu_motion import render_signal
            self.draw_scene_rows(render_signal(1.2,self.w-5,8),top=5,left=2)
        else:self.art(beat.art,opening.TRANSITION_SECONDS,height=9)
        top=14 if rescue else 15
        for line in beat.lines:
            for item in textwrap.wrap(line,self.w-8):
                if top>=self.h-5:break
                self.put(top,4,item);top+=1
        if not rescue:
            details=combat.PERSONAS[self.record.equipped]
            warning=f'{self.record.equipped} is weak to Ice. Change in Velvet Room.' if details['affinity'].get('Ice')=='weak' else 'Action countdown starts in battle.'
            self.put(self.h-6,4,f'LV {self.record.level}   Lead: {self.record.equipped}',TEAL)
            self.put(self.h-5,4,warning,GOLD)

    def _operation_key(self,k):
        if k==ESC:
            if self.recovery_seen:self.recovery_seen=False
            else:self.exit=True
        elif k in ('v','V'):self.open_velvet('operation')
        elif k in ('t','T'):self.deploy()
        elif k in ENTER:
            if self.record.phase!='rescue':self.start_train_route()
            elif self.recovery_seen:self.open_battle('emperor-empress')
            else:
                self.search_step=0
                self.go('rescue-search')

    def draw_rescue_search(self):
        hint, choices, _ = arqa.SEARCH[self.search_step]
        self.frame('TARTARUS / SEARCH','↑↓ ROUTE  ENTER SEARCH  ESC BRIEFING')
        self.art('thebel',opening.TRANSITION_SECONDS,height=8)
        self.lines(14,3,hint,count=2,color=TEAL)
        self.choices(choices,17,3,step=1)

    def _rescue_search_key(self,k):
        if k==ESC:self.go('operation');return
        _,choices,route=arqa.SEARCH[self.search_step]
        pick=self.choose(k,len(choices))
        if pick is None:return
        if pick!=route:
            self.notice='The signal fades. Try another route.'
            return
        self.search_step+=1
        if self.search_step==len(arqa.SEARCH):
            self.discover('fuuka')
        else:self.go('rescue-search')

    def hotel_art(self,scene):
        from persona3_hotel_art import DURATION,render
        self.draw_scene_rows(render(scene,DURATION,self.w-5,7),top=5,left=2)

    def draw_hotel(self):
        self.frame(upper.HOTEL.heading,'↑↓ SELECT  ↵ TOGGLE  S DEPLOY  V VELVET  T PRACTICE  ESC TITLE')
        from persona3_hotel_art import DURATION,render
        art_height=7 if self.h>=30 else 4
        self.draw_scene_rows(render('arrival',DURATION,self.w-5,art_height),top=5,left=2)
        brief_y=5+art_height
        squad_y=max(13,brief_y+3)
        self.lines(brief_y,4,upper.HOTEL.lines[0],width=self.w-8,count=3)
        active_count=len(self.hotel_edit)+len(HOTEL_LOCKED)
        self.put(squad_y,4,f'SQUAD  /  {active_count}/{len(HOTEL_LOCKED)+HOTEL_CAPACITY} ACTIVE',TEAL,True)
        roster=(*HOTEL_LOCKED,*HOTEL_RESERVES)
        rows=[]
        for name,role in zip(roster,HOTEL_ROLES):
            active=name in HOTEL_LOCKED or name in self.hotel_edit
            marker='●' if active else '○'
            lock='  [LOCKED]' if name in HOTEL_LOCKED else ''
            rows.append((f'{marker} {combat.display_name(name)}  /  {role}{lock}','',active))
        self._b_list(rows,squad_y+1,4,self.w-8,len(rows),self.i)
        hp,sp=combat.party_caps(self.record.level,party=roster)[roster[self.i]]
        self.put(squad_y+7,4,f'{hp} HP  /  {sp} SP',TEAL)

    def _hotel_key(self,k):
        if k==ESC:self.exit=True;return
        if k in ('v','V'):self.open_velvet('hotel');return
        if k in ('t','T'):self.open_field_party();return
        if k in ('s','S'):
            self._enter_hotel()
            return
        roster=(*HOTEL_LOCKED,*HOTEL_RESERVES)
        previous=self.i
        pick=self.choose(k,len(roster))
        if pick is None:
            if self.i!=previous:self.notice=''
            return
        name=roster[pick]
        if name in HOTEL_LOCKED:
            self.notice=f'{combat.display_name(name)} is always active.'
        elif name in self.hotel_edit:
            self.hotel_edit.remove(name)
            self.notice=f'{name} moved to standby.'
        elif len(self.hotel_edit)>=HOTEL_CAPACITY:
            self.notice='Remove an active ally first.'
        else:
            self.hotel_edit.append(name)
            self.notice=f'{name} selected.'

    def _enter_hotel(self):
        self.hotel_party=(*HOTEL_LOCKED,*self.hotel_edit)
        self.mirror_index=0
        self.mirror_observation=False
        self.caps=combat.party_caps(self.record.level,party=self.hotel_party)
        self.resources=dict(self.caps)
        self.inventory=dict(combat.BAG)
        self.charge={}
        self.started=time.monotonic()
        self.go('hotel-intro')

    def draw_hotel_intro(self):
        from persona3_hotel_art import DURATION,render
        elapsed=time.monotonic()-self.started
        if elapsed>=DURATION:
            self.open_battle(HOTEL_BATTLES[0]);self.draw();return
        self.draw_scene_rows(render('intro',elapsed,self.w-1,self.h))

    def deployment_level(self,summit=False):
        return max(SUMMIT_LEVEL,self.record.level) if summit else self.record.level

    def open_battle(self,encounter):
        self.encounter=encounter
        state=self.record
        seed=None if self.seed is None else self.seed ^ state.day.toordinal() ^ self.retries
        summit=encounter in (*late.SUMMIT_IDS,APPROACH)
        operation=encounter in ('awakening','priestess','emperor-empress','theurgy-drill','chariot-justice','hermit',*LATE_BATTLES)
        kwargs={}
        carry=getattr(state,'summit_carry',None) if summit else None
        if encounter in (*LATE_BATTLES,APPROACH):
            roster=self.late_party or self.current_party
            start_charge={n:35 for n in roster} if summit else {}
            if carry:start_charge.update(carry.charge)
            kwargs.update(party=roster,fuuka=True,theurgy=True,registered=state.compendium,
                          charge=start_charge)
        elif encounter in HOTEL_BATTLES:
            kwargs.update(party=self.hotel_party,fuuka=True,theurgy=True,charge=self.charge,registered=state.compendium)
        elif encounter in ('chariot-justice','hermit'):
            kwargs.update(party=self.current_party,fuuka=True,theurgy=True,registered=state.compendium)
        elif encounter=='emperor-empress':
            kwargs.update(party=(combat.LEAD_ID,'Junpei','Akihiko'),fuuka=True)
        elif encounter=='theurgy-drill':
            kwargs.update(party=(combat.LEAD_ID,'Yukari','Akihiko','Mitsuru'),fuuka=True,theurgy=True,charge={'Yukari':100},
                          registered=state.compendium)
        elif not operation and (self.current_party!=PARTY or self.fuuka_active):
            kwargs.update(party=self.current_party,fuuka=self.fuuka_active,
                          theurgy=self.theurgy_active,charge=self.charge,registered=state.compendium)
        self.battle=combat.P3Battle(encounter,
            resources=carry.vitals if carry else None if operation else self.resources,
            inventory=(dict(carry.supplies) if carry else self.summit_inventory(encounter) if summit else
                       None if operation or encounter==HOTEL_BATTLES[0] else self.inventory),
            persona='Orpheus' if encounter=='awakening' else state.equipped,
            stock={'Orpheus':()} if encounter=='awakening' else state.stock,
            level=self.deployment_level(summit),seed=seed,day=state.day,
            affinity_memory=getattr(state,'affinity_index',{}),**kwargs)
        self.battle.adjust_lead=encounter!='awakening' and len(state.masks)>1
        self.go('battle')

    def draw_lead_recovery(self):
        masks=self.record.masks
        self.frame('ADJUST STARTING PERSONA','↑↓ SELECT  ENTER EQUIP  ESC CANCEL')
        self.put(7,4,'Current: '+self.record.equipped,CYAN,True)
        count=max(1,self.h-16)
        start=max(0,min(self.i-count+1,len(masks)-count))
        for idx,name in enumerate(masks[start:start+count],start):
            self.put(9+idx-start,4,('◆ ' if idx==self.i else '  ')+name,
                     CYAN if idx==self.i else WHITE,idx==self.i)
        selected=masks[self.i]
        affinities=', '.join(f'{element} {effect}' for element,effect in combat.PERSONAS[selected]['affinity'].items())
        self.lines(self.h-6,4,'Defense: '+(affinities or 'Normal'),count=2)

    def _lead_recovery_key(self,k):
        if k==ESC:self.go('battle');return
        pick=self.choose(k,len(self.record.masks))
        if pick is None:return
        name=self.record.masks[pick]
        if name!=self.record.equipped and not self.write(self.loadout_store.commit,equipped=name):return
        self.go('battle')
        self.notice=f'{name} will lead the next attempt.'

    def _battle_key(self,k):
        if (k in ('a','A') and self.battle.outcome in ('loss','timeout') and
                self.battle.adjust_lead and not self.battle.overlay and not self.battle.reel):
            self.go('lead-recovery')
            self.i=self.record.masks.index(self.record.equipped)
            return
        if self.battle.key(k):return
        if self.complete_late_battle(self.encounter):return
        if self.encounter=='theurgy-drill':
            if (self.battle.outcome=='win' and not self.record.theurgy_drill_seen
                    and not self.write(self.store.commit,theurgy_drill_seen=True)):
                return
            self.beat('bridge');return
        if self.encounter in ('chariot-justice','hermit'):
            arc='hermit' if self.encounter=='hermit' else 'august'
            if self.battle.outcome!='win':
                self.retries+=1
                self.go(arc)
            elif self.write(self.store.clear_operation,self.encounter,affinity_updates=getattr(self.battle,'affinity_updates',{})):self.beat(arc+'-after')
            return
        if self.monad_route and self.encounter in MONAD_STAGES[self.monad_route]:
            self._finish_monad()
            return
        if self.encounter in HOTEL_BATTLES:
            if self.battle.outcome!='win':
                self.retries+=1
                self.go('hotel')
            elif self.encounter==HOTEL_BATTLES[0]:
                self.resources=self.battle.resources
                self.inventory=dict(self.battle.inventory)
                self.charge=self.battle.charge
                self.start_hotel_route()
            elif self.write(self.store.clear_operation,self.encounter,affinity_updates=getattr(self.battle,'affinity_updates',{})):
                self.beat('hotel-after')
            return
        if self.battle.outcome!='win':
            self.retries+=1
            if self.encounter in ('priestess','emperor-empress'):self.go('operation')
            elif self.encounter=='awakening':self.beat('awakening')
            else:self.end_expedition()
            return
        if self.encounter=='awakening':
            if self.write(self.store.grant_xp,AWAKENING_XP,phase='tartarus',day=TUTORIAL,affinity_updates=getattr(self.battle,'affinity_updates',{})):self.beat('briefing')
        elif self.encounter in ('priestess','emperor-empress'):
            if self.write(self.store.clear_operation,self.encounter,affinity_updates=getattr(self.battle,'affinity_updates',{})):
                if self.encounter=='priestess':self.start_train_brake()
                else:self.beat('signal')
        else:self._finish_hall_battle()

    def resume_field_checkpoint(self):
        checkpoint=self.record.field_checkpoint
        self.block=checkpoint.block
        self.hall=checkpoint.restore(self.floors)
        self.resources=dict(checkpoint.resources)
        self.practice_party=tuple(self.resources)
        self.caps=combat.party_caps(self.record.level,party=self.practice_party)
        self.inventory=dict(checkpoint.items)
        self.charge=dict(checkpoint.charge)
        self.temperance_bonus=checkpoint.temperance
        self.sp_bonus=checkpoint.lounge
        self.guided_expedition=checkpoint.guided
        self.go('shuffle' if checkpoint.pending else 'hall')

    def _finish_hall_battle(self):
        cleared=self.hall.index+1
        first=cleared>self.field_depth
        old=self.record
        resources=dict(self.battle.resources)
        inventory=dict(self.battle.inventory)
        charge=dict(getattr(self.battle,'charge',{}))
        supply=first and self.hall.floor.encounter=='arqa-magus'
        if supply:inventory['Soul Drop']=inventory.get('Soul Drop',0)+1
        if self.free_expedition:
            if first:
                if self.block in registry.BLOCKS:self.practice_late[self.block]=cleared
                elif self.block==high.BLOCK:self.practice_yabba_upper=cleared
                elif self.block=='yabba':self.practice_yabba=cleared
                elif self.block=='upper':self.practice_upper=cleared
                elif self.block=='arqa':self.practice_arqa=cleared
                else:self.practice_depth=cleared
            self.resources=resources
            if self.sp_bonus:self.recover(15,8)
        else:
            award=BLOCKS[self.block][2][self.hall.index] if first else REPLAY_XP
            earned={('depth' if self.block=='thebel' else self.block):cleared,'yen':min(999999,old.yen+25)} if first else {}
            if first and self.block in ('yabba',high.BLOCK,*registry.BLOCKS):
                earned['fragments']=min(99,old.fragments+2)
            if self.temperance_bonus:award=award*5//4
            temperance=max(0,self.temperance_bonus-1)
            level=state_runtime.level_for(min(999999,old.xp+award))
            caps=combat.party_caps(level,party=tuple(resources))
            resources=self._resize_resources(resources,self.caps,caps)
            if self.sp_bonus:resources=self._recover_at(resources,caps,15,8)
            checkpoint=FieldCheckpoint.capture(self.hall,resources,inventory,charge,temperance,
                                               False,self.guided_expedition,True)
            if not self.write(self.store.grant_xp,award,field_checkpoint=checkpoint,
                              affinity_updates=getattr(self.battle,'affinity_updates',{}),**earned):return
            self.temperance_bonus=temperance
            self.resources,self.caps=resources,caps
        self.sp_bonus=False
        self.hall.defeated=True
        self.hall.alert=False
        self.inventory,self.charge=inventory,charge
        if not self.free_expedition:
            self.go('shuffle')
            self.notice=f'+{award} XP'+('  /  Soul Drop found' if supply else '')
            if self.record.level>old.level:
                new=[x for x in combat.persona_skills(old.equipped,self.record.level,old.stock[old.equipped])
                     if x not in combat.persona_skills(old.equipped,old.level,old.stock[old.equipped])]
                self.notice+=f'  /  Level {self.record.level}'
                if new:self.notice+='  /  '+', '.join(new)+' unlocked'
        elif self.hall.pos==self.hall.floor.stairs:self._stairs()
        else:self.go('hall')

    @staticmethod
    def _resize_resources(resources,caps,next_caps):
        return {n:(min(next_caps[n][0],hp+next_caps[n][0]-caps.get(n,next_caps[n])[0]) if hp else 0,
                   min(next_caps[n][1],sp+next_caps[n][1]-caps.get(n,next_caps[n])[1]) if hp else sp)
                for n,(hp,sp) in resources.items()}

    def adjust_caps(self,old_level):
        if self.record.level>old_level:
            next_caps=combat.party_caps(self.record.level) if self.current_party==PARTY else combat.party_caps(self.record.level,party=self.current_party)
            self.resources=self._resize_resources(self.resources,self.caps,next_caps)
            self.caps=next_caps

    @property
    def active_monad(self):
        if not self.hall:return None
        route=(high.PASSAGE if self.hall.floor.number==117 else None) if self.block==high.BLOCK else (yabba.MONAD_FLOOR.get(self.hall.floor.number) if self.block=='yabba' else None)
        if self.hall.floor.number in registry.PASSAGES and self.hall.stairs_open:route=registry.PASSAGES[self.hall.floor.number][0]
        if route in self.record.monad or route in self.practice_monad:return None
        return route

    def draw_monad(self):
        name='MONAD DOOR' if self.monad_route==yabba.DOOR else 'MONAD PASSAGE'
        self.frame(name,'ENTER CHALLENGE  H HEAL  ESC FLOOR')
        self.art('dark_hour',opening.TRANSITION_SECONDS,height=8)
        n=len(MONAD_STAGES[self.monad_route])
        self.put(14,4,f'Encounter {self.monad_index+1}/{n}',TEAL)
        if self.monad_index:
            self.lines(16,4,'The next guard is deeper inside. HP, SP, and supplies carry forward.',count=2)
        else:
            self.lines(16,4,'Optional challenge. Defeat ends this expedition. You can leave the door alone.',count=2)

    def _monad_key(self,k):
        if k==ESC:
            self.monad_route=None;self.go('hall');return
        if k in ENTER:self.open_battle(MONAD_STAGES[self.monad_route][self.monad_index])

    def _finish_monad(self):
        if self.battle.outcome!='win':
            self.monad_route=None
            self.end_expedition()
            return
        route=self.monad_route
        last=self.monad_index+1==len(MONAD_STAGES[route])
        old_level=self.record.level
        if last:
            if self.free_expedition:self.practice_monad.add(route)
            elif not self.write(self.store.clear_monad,route,affinity_updates=getattr(self.battle,'affinity_updates',{})):return
        self.resources=dict(self.battle.resources)
        self.inventory=dict(self.battle.inventory)
        self.charge=self.battle.charge
        self.adjust_caps(old_level)
        if last:
            self.hall.seen.update((x,y) for y in range(H) for x in range(W))
            self.monad_route=None
            self.go('hall')
            if route in (yabba.PASSAGE,high.PASSAGE):
                self.temperance_bonus=2
                self.notice='Temperance unlocked. First two fights each night earn 25% more XP.'
            elif route==yabba.DOOR:
                self.inventory['Soul Drop']=self.inventory.get('Soul Drop',0)+1
                self.notice='Door cleared. Floor mapped and Soul Drop added.'
            else:self.notice='Passage cleared. Twilight Fragments awarded.'
            return
        self.monad_index+=1
        self.go('monad')

    def use_clock(self):
        if self.resources==self.caps:
            self.notice='The squad is already at full HP and SP.'
            return
        if not self.write(self.loadout_store.spend_fragments,yabba.CLOCK_COST):return
        self.resources=dict(self.caps)
        self.notice='HP and SP fully restored.'

    @staticmethod
    def _recover_at(resources,caps,hp,sp):
        return {n:(min(caps[n][0],left+hp),min(caps[n][1],mana+sp)) if left else (left,mana)
                for n,(left,mana) in resources.items()}

    def recover(self,hp,sp):
        self.resources=self._recover_at(self.resources,self.caps,hp,sp)

    def draw_battle(self):
        self.battle.draw(self)
        if self.notice:self.put(self.h-4,3,self.notice[:self.w-6],GOLD,True)

    def draw_shuffle(self):
        self.frame('SHUFFLE TIME','←→ SELECT  ENTER CLAIM  H HEAL')
        mask=self.hall.floor.mask
        unregistered=mask not in self.record.masks
        reward_cards.draw(self,(('PERSONA',mask if unregistered else 'Registered',unregistered),
                                ('COINS',f'¥{self.shuffle_yen()}',True),('CUP','+30 HP / +12 SP',True)),self.i)

    def shuffle_yen(self):
        return 30 if self.hall.replay else 90

    def _shuffle_key(self,k):
        if k in (C.KEY_LEFT,C.KEY_RIGHT):
            self.i=(self.i+(-1 if k==C.KEY_LEFT else 1))%3
            self.notice=''
            return
        pick=self._b_commit(k,self.i,3)
        if pick is None:return
        self.i=pick
        restored=self._recover_at(self.resources,self.caps,30,12) if pick==2 else None
        if not self.write(self.store.claim_field_card,pick,self.hall.floor.mask,self.shuffle_yen(),restored):return
        if restored is not None:self.resources=restored
        self.go('hall')
        if self.hall.pos==self.hall.floor.stairs and not self.active_monad:self._stairs()

    def _recovery_options(self):
        hotel=self.heal_back and self.heal_back[0]=='hotel-hall'
        aids=field_recovery.options(self.resources,self.inventory,self.field_kits,self.record)
        return aids[1:] if hotel else aids

    def _open_heal(self):
        self.heal_back=(self.page,self.i,self.notice)
        self.go('field-heal')

    def _leave_heal(self):
        page,index,notice=self.heal_back
        self.heal_back=None
        self.go(page)
        self.i=index
        self.notice=notice

    def _use_aid(self,aid,target=None):
        reason=aid.blocked(self.resources,self.caps)
        if reason:
            self.notice=reason
            return False
        updated=aid.apply(self.resources,self.caps,target)
        inventory=dict(self.inventory)
        if aid.kind!='kit' and not aid.caster:inventory[aid.name]-=1
        changes={}
        if not self.free_expedition and self.record.field_checkpoint:
            checkpoint=self.record.field_checkpoint
            changes['field_checkpoint']=replace(checkpoint,resources=tuple(updated.items()),items=tuple(inventory.items()))
        if aid.kind=='kit':
            if self.free_expedition:self.practice_aid-=1
            else:changes['aid']=self.record.aid-1
        if changes and not self.write(self.store.commit,**changes):return False
        self.resources,self.inventory=updated,inventory
        return True

    def draw_field_heal(self):
        aids=self._recovery_options()
        selecting=self.page=='field-target'
        in_hotel=self.heal_back and self.heal_back[0]=='hotel-hall'
        self.frame('RECOVERY / TARGET' if selecting else 'HOTEL / RECOVERY' if in_hotel else 'TARTARUS / RECOVERY',
                   ('↑↓ ALLY  ENTER USE' if selecting else '↑↓ PICK  ENTER OPEN')+'  ESC BACK')
        aid=aids[self.aid_index if selecting else self.i]
        if selecting:
            rows=[(combat.display_name(n),WHITE if aid.eligible(n,self.resources,self.caps) else DIM)
                  for n in self.resources]
        else:
            rows=[(item.label,WHITE if not item.blocked(self.resources,self.caps) else DIM)
                  for item in aids]
        self.choices(rows,6,3,29,step=1)
        self.lines(15,3,aid.detail,27,2,TEAL)
        reason=aid.blocked(self.resources,self.caps)
        if selecting:
            name=tuple(self.resources)[self.i]
            if not aid.eligible(name,self.resources,self.caps):
                reason='Cannot use on '+combat.display_name(name)+'.'
        if reason:self.lines(18,3,reason,27,2,GOLD)
        self.draw_hall_party(34)

    def _field_heal_key(self,k):
        options=self._recovery_options()
        if self.page=='field-target':
            aid=options[self.aid_index]
            if k==ESC:
                self.go('field-heal');self.i=self.aid_index
                return
            names=tuple(self.resources)
            pick=self.choose(k,len(names))
            if pick is None:return
            target=names[pick]
            if not aid.eligible(target,self.resources,self.caps):
                self.notice='Choose an ally who needs that recovery.'
                return
            if self._use_aid(aid,target):
                self.go('field-heal')
                self.i=self.aid_index
                self.notice=f'{aid.name} used on {combat.display_name(target)}.'
            return
        if k==ESC:
            self._leave_heal()
            return
        pick=self.choose(k,len(options))
        if pick is None:return
        aid=options[pick]
        reason=aid.blocked(self.resources,self.caps)
        if reason:self.notice=reason;return
        if aid.kind=='kit':
            if self._use_aid(aid):self.notice='Field Kit used on the party.'
        elif aid.team:
            if self._use_aid(aid):self.notice=f'{aid.name} used on the party.'
        else:
            self.aid_index=pick
            self.go('field-target')
            self.i=next(i for i,n in enumerate(self.resources) if aid.eligible(n,self.resources,self.caps))

    def open_velvet(self,back):
        self.back=back
        self.velvet_return_index=self.i
        self.started=time.monotonic()
        self.go('velvet-intro')

    def _enter_velvet(self):
        self.go('velvet')
        self.i=self.record.masks.index(self.record.equipped)

    def draw_velvet_intro(self):
        from persona3_cinematics import VELVET_SECONDS,render_velvet
        elapsed=time.monotonic()-self.started
        if elapsed>=VELVET_SECONDS:
            self._enter_velvet();self.draw();return
        self.draw_scene_rows(render_velvet(elapsed,self.w-1,self.h))

    def recipes(self):
        return tuple(self.loadout_store.fusion_preview(name) for name,_ in available_fusions(self.record.day))

    def _persona_details(self,name,extra=()):
        spec=combat.PERSONAS[name]
        skills=combat.persona_skills(name,self.record.level,extra)
        defense=', '.join(f'{e} {v}' for e,v in spec['affinity'].items()) or 'Normal'
        return ('Skills: '+', '.join(skills),'Defense: '+defense)

    def _inherit_rows(self):
        name=self.recipes()[self.recipe_i].result
        return (('', ''),*self.loadout_store.inheritance_options(name))

    def draw_velvet(self):
        s=self.record
        rows=()
        page=self.page
        detail=()
        review_elapsed=None
        i=self.i
        if page=='velvet':
            screen='stock'
            name=s.masks[i]
            rows=tuple(velvet_ui.Row(n,'Equipped' if n==s.equipped else '') for n in s.masks)
            detail=(f'LV {s.level} • {len(s.masks)} in stock',*self._persona_details(name,s.stock[name]))
            if self.expedition_store is not None:detail+=('Practice changes do not save.',)
            inherited=s.compendium[name]
            if inherited:detail+=(f'Inherited: {inherited}',)
            footer='↑↓ PICK  ENTER EQUIP  F FUSE  C COMPENDIUM  ESC BACK'
        elif page=='compendium':
            screen='compendium'
            name=tuple(s.compendium)[i]
            rows=tuple(velvet_ui.Row(n,'In stock' if n in s.masks else f'Resummon ¥{SUMMON_PRICE[n]}')
                       for n in s.compendium)
            extra=s.compendium[name]
            detail=(*self._persona_details(name,(extra,) if extra else ()),
                    'In stock' if name in s.masks else f'Resummon for ¥{SUMMON_PRICE[name]}')
            if self.theurgy_active and not {'Orpheus','Apsaras'}<=s.compendium.keys():
                detail+=('Cadenza: register Orpheus + Apsaras.',)
            footer='↑↓ PICK  R RESUMMON  S STOCK  F FUSE  ESC BACK' if name not in s.masks else '↑↓ PICK  S STOCK  F FUSE  ESC BACK'
        elif page=='fusion':
            screen='fusion'
            recipes=self.recipes()
            item=recipes[i]
            rows=tuple(velvet_ui.Row(r.result,r.status,r.ready) for r in recipes)
            parents=' + '.join(item.parents)
            detail=(parents,'Needs: '+', '.join(item.missing) if item.missing and not item.registered else item.status,
                    *self._persona_details(item.result))
            if not any(r.ready for r in recipes):detail+=('No recipe ready.',)
            footer='↑↓ RECIPE  ENTER REVIEW  ESC BACK' if item.ready else '↑↓ RECIPE  ESC BACK'
        elif page=='inherit':
            screen='inherit'
            item=self.recipes()[self.recipe_i]
            rows=tuple(velvet_ui.Row(skill or 'No inheritance',parent) for parent,skill in self._inherit_rows())
            skill=self._inherit_rows()[i][1]
            detail=(item.result,*self._persona_details(item.result,(skill,) if skill else ()),
                    'Choose up to one parent skill.')
            footer='↑↓ SKILL  ENTER REVIEW  ESC BACK'
        elif page=='fuse-confirm':
            screen='confirm'
            review_elapsed=time.monotonic()-self.fusion_review_started
            item=self.recipes()[self.recipe_i]
            lead=item.result if s.equipped in item.parents else s.equipped
            detail=(f'{item.parents[0]} + {item.parents[1]} → {item.result}',
                    ('Parents leave stock, but stay registered.',TEAL),
                    'Inherit: '+(self.fuse_skill or 'none'),
                    *self._persona_details(item.result,(self.fuse_skill,) if self.fuse_skill else ()),
                    'Equip after fusion: '+lead,
                    'No yen cost.')
            footer='ENTER FUSE  ESC CANCEL'
        else:
            screen='resummon'
            name=self.summon_name
            price=SUMMON_PRICE[name]
            extra=s.compendium[name]
            detail=(name,f'Pay ¥{price}   /   ¥{s.yen} → ¥{s.yen-price}',
                    *self._persona_details(name,(extra,) if extra else ()),
                    f'{s.equipped} stays equipped.')
            footer='ENTER RESUMMON  ESC CANCEL'
        velvet_ui.draw(self,velvet_ui.View(screen,i,s.yen,rows,detail,footer,review_elapsed))

    def _open_fusion(self):
        self.go('fusion')
        self.i=next((i for i,v in enumerate(self.recipes()) if v.ready),0)

    def _velvet_key(self,k):
        if k==ESC:
            self.go(self.back)
            if self.back in ('entrance','hotel'):self.i=self.velvet_return_index
        elif k in ('f','F'):self._open_fusion()
        elif k in ('c','C'):self.go('compendium')
        else:
            pick=self.choose(k,len(self.record.masks))
            if pick is not None and self.write(self.loadout_store.commit,equipped=self.record.masks[pick]):
                self.notice='Equipped '+self.record.equipped+'.'

    def _compendium_key(self,k):
        if k in (ESC,'s','S'):
            self.go('velvet');self.i=self.record.masks.index(self.record.equipped)
        elif k in ('f','F'):self._open_fusion()
        elif k in ('r','R'):
            name=tuple(self.record.compendium)[self.i]
            if name in self.record.masks:self.notice='Already in your stock.'
            elif self.record.yen<SUMMON_PRICE[name]:
                self.notice=f'Need ¥{SUMMON_PRICE[name]-self.record.yen} more.'
            else:
                self.summon_name=name
                self.page='resummon';self.notice=''
        else:self.choose(k,len(self.record.compendium))

    def _fusion_key(self,k):
        if k==ESC:
            self.go('velvet');self.i=self.record.masks.index(self.record.equipped);return
        old=self.i
        pick=self.choose(k,len(self.recipes()))
        if old!=self.i:self.notice=''
        if pick is None:return
        item=self.recipes()[pick]
        if not item.ready:self.notice=item.reason;return
        self.recipe_i=self.i
        self.go('inherit')

    def _inherit_key(self,k):
        if k==ESC:self.go('fusion');self.i=self.recipe_i;return
        rows=self._inherit_rows()
        pick=self.choose(k,len(rows))
        if pick is not None:
            self.inherit_i=pick
            self.fuse_skill=rows[pick][1]
            self.fusion_review_started=time.monotonic()
            self.page='fuse-confirm';self.notice=''

    def _fuse_confirm_key(self,k):
        if k==ESC:
            self.go('inherit');self.i=self.inherit_i
        elif k in ENTER:
            item=self.recipes()[self.recipe_i]
            if self.write(self.loadout_store.fuse,item.result,self.fuse_skill):
                self.go('velvet')
                self.i=self.record.masks.index(item.result)
                self.notice=f'Fused {item.result}  /  Parents archived.'

    def _resummon_key(self,k):
        if k==ESC:self.page='compendium';self.notice=''
        elif k in ENTER and self.write(self.loadout_store.resummon,self.summon_name):
            self.go('velvet')
            self.i=self.record.masks.index(self.summon_name)
            self.notice='Resummoned '+self.summon_name+'.'

    def draw_overlay(self):
        if self.overlay=='extract':
            self.frame('END PRACTICE?' if self.free_expedition else 'END EXPEDITION?','ENTER CONFIRM  ESC STAY')
            detail=('End practice and return without advancing the date.' if self.free_expedition else
                    'Survey unfinished. You can return to 02F next evening.' if self.guided_expedition and self.first_survey_due else
                    'The night ends. Cleared checkpoints and claimed cards are saved.')
            self.lines(9,4,detail,count=3)
            if not self.free_expedition:
                for i,line in enumerate(self.deadline_warnings(self.record.day+timedelta(days=1))):
                    self.lines(13+i*2,4,line,count=2,color=GOLD)
        elif self.overlay=='clock':
            self.frame('TARTARUS / RECOVERY CLOCK','ENTER USE  ESC BACK')
            self.lines(8,4,f'{self.record.fragments} Twilight Fragments on hand. The Clock costs {yabba.CLOCK_COST}.',count=2)
            self.lines(11,4,'Restore the squad’s HP and SP. Supplies are unchanged.',count=2)
        elif self.overlay=='hotel-retreat':
            self.frame('LEAVE THE HOTEL?','ENTER RETRY  ESC STAY')
            self.lines(9,4,'You will start this operation again from the briefing.',count=2)
        elif self.overlay in ('wait','rest'):
            wait=self.overlay=='wait'
            target=self.next_operation if wait else self.record.day+timedelta(days=1)
            days=(target-self.record.day).days
            destination=f'{target:%B} {target.day}'
            if wait:
                self.frame(f'WAIT FOR {self.event_label}?','ENTER WAIT  ESC STAY')
                self.lines(8,4,f'Skip {days} day{"s" if days!=1 else ""} to {destination}. No activities are earned.',count=3)
            else:
                self.frame('REST UNTIL TOMORROW?','ENTER REST  ESC STAY')
                self.lines(8,4,f'End the evening and advance to {destination}.')
            warnings=self.deadline_warnings(target)
            if wait and self.first_survey_due and target>=MOON:
                warnings+=('The 02F survey is unfinished. Skip it and face the full moon without training.',)
            if warnings:
                for i,line in enumerate(warnings):self.lines(11+i*3,4,line,count=3,color=GOLD)
            elif target in upper.REPORT_DAYS:self.lines(11,4,'Elizabeth will have new cases to review.',count=2)
            elif wait:self.lines(11,4,'Your checkpoints and Persona stock stay as they are.',count=3)
        elif self.overlay=='ryoji':
            self.frame('FORGET THE DARK HOUR?','ENTER CONFIRM  ESC BACK')
            self.lines(9,4,'Choosing this ends the campaign at graduation. January and Tartarus will be skipped.',count=3)
        elif self.overlay=='quit':
            self.frame('LEAVE PERSONA 3?','ENTER QUIT  ESC STAY')
            self.lines(9,4,'Only recorded checkpoints and time slots carry forward.',count=3)

    def draw(self):
        if self.overlay:self.draw_overlay();return
        if self.page in OPERATION_ROUTE_PAGES:self.draw_operation_route();return
        if self.page in LATE_DATED:self.late_draw();return
        {'restart-needed':self.draw_restart_needed,'story':self.draw_story,
         'yakushima':self.draw_yakushima,'august':self.draw_august,'hermit':self.draw_hermit,'roster':self.draw_roster,'monad':self.draw_monad,'hotel':self.draw_hotel,
         'hotel-intro':self.draw_hotel_intro,
         'rescue-board':self.draw_rescue_board,'calendar':self.draw_calendar,'evening':self.draw_evening,
         'dark-hour':self.draw_dark_hour,'teleport':self.draw_teleport,
         'field-heal':self.draw_field_heal,'field-target':self.draw_field_heal,'entrance':self.draw_entrance,'hall':self.draw_hall,'border':self.draw_border,
         'operation':self.draw_operation,'rescue-search':self.draw_rescue_search,'velvet-intro':self.draw_velvet_intro,'battle':self.draw_battle,'lead-recovery':self.draw_lead_recovery,'field-clue':self.draw_field_clue,'shuffle':self.draw_shuffle,
         'velvet':self.draw_velvet,'compendium':self.draw_velvet,'fusion':self.draw_velvet,
         'inherit':self.draw_velvet,'fuse-confirm':self.draw_velvet,'resummon':self.draw_velvet}[self.page]()

    def key(self,k):
        if self.page=='restart-needed':
            if k in ('q','Q'):self.exit=False
            elif k in (*ENTER,ESC):self.exit=True
            return
        if self.overlay:
            if k==ESC:self.overlay=''
            elif k in ENTER:
                if self.overlay=='quit':self.exit=False
                elif self.overlay=='hotel-retreat':self.go('hotel')
                elif self.overlay=='clock':self.use_clock()
                elif self.overlay=='ryoji':self.confirm_ryoji()
                elif self.overlay=='wait':self.next_night(skip=True)
                elif self.overlay=='rest':self.next_night()
                else:self.end_expedition()
                self.overlay=''
            return
        if k in ('h','H') and self.page in ('entrance','hall','border','shuffle','hotel-hall','monad'):
            self._open_heal()
            return
        if k in ('q','Q'):
            if self.page in ('field-heal','field-target','field-clue','lead-recovery','hotel-intro','hotel-hall','hotel-mirror','train-cars','train-brake','dark-hour','teleport','entrance','hall','border','battle','shuffle'):
                self.overlay='quit'
            else:self.exit=False
            return
        if self.page in OPERATION_ROUTE_PAGES:self.operation_route_key(k);return
        if self.page=='late-interlude' and junpei.payoff_due(self.record):
            if k in ENTER and self.write(self.store.finish_junpei):self.go('calendar')
            elif k==ESC:self.exit=True
            return
        if self.page in LATE_DATED:self.late_key(k);return
        if self.page=='dark-hour':
            if k in (*ENTER,ESC,' '):self.go('hall' if self.guided_expedition else 'entrance')
            return
        if self.page=='hotel-intro':
            if k in (*ENTER,ESC,' '):self.open_battle(HOTEL_BATTLES[0])
            return
        if self.page=='velvet-intro':
            if k in (*ENTER,ESC,' '):self._enter_velvet()
            return
        if self.page=='teleport':
            if k in (*ENTER,ESC,' '):self._finish_teleport(self.teleport_target[0])
            return
        if self.page=='field-clue':
            if k in (*ENTER,ESC):self.go('hall')
            return
        if self.page=='border':
            if k in ENTER and self.next_block:
                self.block=self.next_block;self._select_floor(self.field_depth)
            elif k in (*ENTER,ESC,'t','T'):self.go_entrance()
            elif k in ('x','X'):self.overlay='extract'
            return
        {'story':self._story_key,'yakushima':self._yakushima_key,'august':self._august_key,'hermit':self._hermit_key,
         'roster':self._roster_key,'monad':self._monad_key,'hotel':self._hotel_key,
         'rescue-board':self._rescue_board_key,'calendar':self._calendar_key,'evening':self._evening_key,
         'entrance':self._entrance_key,'hall':self._hall_key,
         'field-heal':self._field_heal_key,'field-target':self._field_heal_key,'operation':self._operation_key,'rescue-search':self._rescue_search_key,'battle':self._battle_key,'lead-recovery':self._lead_recovery_key,
         'shuffle':self._shuffle_key,'velvet':self._velvet_key,'compendium':self._compendium_key,
         'fusion':self._fusion_key,'inherit':self._inherit_key,
         'fuse-confirm':self._fuse_confirm_key,'resummon':self._resummon_key}[self.page](k)

    def run(self):
        self.s.timeout(48)
        while self.exit is None:
            self.s.erase();self.h,self.w=self.s.getmaxyx()
            small=self.h<25 or self.w<65
            if small:self.mid(self.h//2,'Widen the terminal to 65 × 25.',GOLD)
            else:self.draw()
            self.s.refresh()
            try:k=self.s.get_wch()
            except C.error:continue
            if not small or k in ('q','Q'):self.key(k)
        return self.exit
