"""Chapter briefings, summit checkpoints, and ending screens for P3App."""
from time import monotonic
from dataclasses import replace
from textwrap import wrap

from persona_terminal.shared.terminal_constants import ENTER,ESC,DIM,CYAN,GOLD,WHITE
from . import persona3_late as late
from . import persona3_discovery as discovery
from .persona3_discovery_schedule import CHECKPOINTS
from .persona3_summit import (ADAMAH_PHASE,SEAL_PHASE,APPROACH,Ascent,SoloSeal,
                             SUMMIT_LEVEL,SUMMIT_SUPPLIES,ascent_art,seal_art)
from .persona3_summit_checkpoint import SummitCarry

LATE_DATED=('discovery','late-aftermath','late-interlude','late-brief','late-between','decision','summit',SEAL_PHASE,'epilogue','ending','credits')
LATE_BATTLES=('fortune-strength','takaya-jin','hanged-man','chidori',APPROACH,*late.SUMMIT_IDS)


class LateRoute(discovery.DiscoveryRoute):
    def late_route_init(self):
        self.late_party=None
        self.ascent=Ascent()
        self.solo_seal=SoloSeal()
        self.late_story=None
        self.aftermath_step=None
        self.aftermath_started=0.
        self.ending_index=0
        self.credit_started=0.

    def resume_late(self):
        phase=self.record.phase
        day=self.record.day
        if phase in CHECKPOINTS:
            self.discover(CHECKPOINTS[phase][1])
        elif phase=='bridge-aftermath':
            self.discover('pharos-farewell')
        elif phase in late.AFTERMATH_PHASES:
            self.start_aftermath()
        elif phase=='epilogue' and day==late.ENDING:
            self.discover('roof')
        elif phase in ('epilogue','ending','decision',SEAL_PHASE):
            self.go(phase)
        elif phase in (*late.SUMMIT_PHASES,ADAMAH_PHASE):
            carry=getattr(self.record,'summit_carry',None)
            if carry:self.late_party=carry.roster
            self.go('summit')
        elif phase in late.OPERATION:self.go('late-brief')
        elif day in (*late.STORY_DAYS,*late.INTERLUDES):
            self.late_story=late.STORY_DAYS.get(day) or late.INTERLUDES[day]
            self.go('late-interlude')
        else:return False
        return True

    def ending_art(self,kind,y=5,height=8,seconds=None):
        if kind in ('dorm','tartarus'):
            from .persona3_opening import TRANSITION_SECONDS
            self.art(kind,TRANSITION_SECONDS,y,height)
        else:
            from .persona3_ending_art import DURATIONS,render
            self.draw_scene_rows(render(kind,DURATIONS[kind]*.50 if seconds is None else seconds,self.w-5,height),top=y,left=2)

    def start_aftermath(self):
        self.aftermath_step,self.aftermath_nodes=discovery.scene(self.record.phase)
        self.aftermath_started=monotonic()
        self.go('late-aftermath')

    def draw_late_aftermath(self):
        day=self.record.day
        if self.record.phase=='station-aftermath':
            from .persona3_station_scene import AFTER_MIDNIGHT
            if self.aftermath_step not in AFTER_MIDNIGHT:day=late.OCT
        discovery.draw(self,self.aftermath_nodes[self.aftermath_step],
                       monotonic()-self.aftermath_started,day=day)

    def _late_aftermath_key(self,k):
        if k==ESC:self.exit=True;return
        choices=self.aftermath_nodes[self.aftermath_step][3]
        pick=self.choose(k,len(choices))
        if pick is None:return
        _,target=choices[pick]
        if target is None:
            if self.write(self.store.finish_aftermath):
                self.aftermath_step=None
                self.go('calendar')
        else:
            self.aftermath_step=target
            self.i=0

    def draw_late_interlude(self):
        title,art,lines=self.late_story
        self.frame(title,'ENTER CONTINUE  ESC TITLE')
        self.ending_art(art)
        top=14
        for line in lines:
            for piece in wrap(line,self.w-8):
                if top>self.h-5:break
                self.put(top,4,piece,WHITE)
                top+=1

    def _late_interlude_key(self,k):
        if k in ENTER:self.go('calendar')
        elif k==ESC:self.exit=True

    def draw_late_brief(self):
        phase=self.record.phase
        title,_,art,lines=late.OPERATION[phase]
        self.frame(title,'ENTER SQUAD  V VELVET  T PRACTICE  ESC TITLE')
        self.ending_art(art)
        self.lines(15,4,lines[0],count=3)

    def _late_brief_key(self,k):
        phase=self.record.phase
        if k==ESC:self.exit=True
        elif k in ('v','V'):self.open_velvet('late-brief')
        elif k in ('t','T'):self.open_field_party()
        elif k in ENTER:self.open_roster(phase,'late-brief')

    def start_late_roster(self,purpose,roster):
        carry=getattr(self.record,'summit_carry',None)
        if purpose=='summit' and carry and carry.roster!=roster:
            if not self.write(self.store.commit,summit_carry=replace(carry,roster=roster)):return
        self.late_party=roster
        if purpose=='finale':
            self.ascent=Ascent()
            if self.write(self.store.begin_summit):
                self.go('summit')
            return
        if purpose=='summit':
            self.go('summit')
            return
        if purpose=='hanged':
            self.open_battle('hanged-man')
            return
        self.open_battle(late.OPERATION[purpose][1])

    def draw_late_between(self):
        self.frame('MOONLIGHT BRIDGE / THE LAST SHADOW','ENTER SQUAD  ESC TITLE')
        self.ending_art('stars')
        self.lines(15,4,'Strega retreats. The Shadow is suspended above the bridge.',count=2)

    def _late_between_key(self,k):
        if k==ESC:self.exit=True
        elif k in ENTER:self.open_roster('hanged','late-between')

    def draw_decision(self):
        self.frame('DECEMBER 31 / RYOJI','↑↓ SELECT  ENTER CHOOSE  ESC TITLE')
        self.ending_art('bridge',height=7)
        self.lines(12,4,'Ryoji offers to erase your memory of the Dark Hour. That will not stop Nyx.',count=2)
        self.choices(('Spare Ryoji','Kill Ryoji'),15,4,step=2)

    def _decision_key(self,k):
        if k==ESC:self.exit=True;return
        pick=self.choose(k,2)
        if pick==0:
            if self.write(self.store.ryoji_choice,True):self.resume()
        elif pick==1:self.overlay='ryoji'

    def confirm_ryoji(self):
        if self.write(self.store.ryoji_choice,False):
            self.ending_index=0
            self.resume()

    def summit_index(self):
        return late.SUMMIT_PHASES.index(self.record.phase)

    def summit_inventory(self,encounter):
        if encounter==late.SUMMIT_IDS[0]:return self.ascent.supplies()
        return dict(SUMMIT_SUPPLIES)

    def _draw_ascent(self):
        a=self.ascent
        self.frame(f'{a.floor}F / ADAMAH','↑↓ SELECT  ENTER CONFIRM  P SQUAD  V VELVET  ESC TITLE')
        self.draw_scene_rows(ascent_art(a.step,self.w-5,8),top=5,left=2)
        if a.step==0:
            self.lines(13,4,'Fuuka finds the last staircase. The squad is ready for the climb.',count=2)
            self.choices(('Take the staircase',),16,4)
        else:
            body=('The patrol is gone. Its cache adds two Medicines and two Soul Drops for Jin.'
                  if a.cache else 'Jin is one floor up. A patrol guards extra supplies, but you can go around it.')
            self.lines(13,4,body,count=2)
            self.choices(('Climb to 259F',) if a.cache else
                         ('Climb to 259F','Intercept the patrol for supplies'),16,4)
        if self.record.level<SUMMIT_LEVEL:
            self.put(20,4,f'Summit readiness: battle level {SUMMIT_LEVEL}.',CYAN)

    def _ascent_key(self,k):
        if k==ESC:self.exit=True;return
        if k in ('v','V'):self.open_velvet('summit');return
        if k in ('p','P'):self.open_roster('summit','summit');return
        a=self.ascent
        pick=self.choose(k,1 if a.step==0 or a.cache else 2)
        if pick is None:return
        if a.step==0:
            a.step=1
            self.go('summit')
        elif pick==1:
            self.open_battle(APPROACH)
        elif self.write(self.store.reach_summit):
            self.resume()

    def draw_summit(self):
        if self.record.phase==ADAMAH_PHASE:self._draw_ascent();return
        i=self.summit_index()
        title,desc=late.SUMMIT_HEADS[i]
        carry=getattr(self.record,'summit_carry',None)
        can_restock=carry and carry.resources is not None
        self.frame(title,('ENTER FIGHT  P SQUAD  ' if self.late_party else 'ENTER SQUAD  ')+('R RESTOCK  ' if can_restock else '')+'V VELVET  ESC TITLE')
        self.ending_art('stars',height=9)
        self.lines(15,4,desc,count=3)
        if self.late_party:self.put(18,4,'  •  '.join(self.late_party[1:]) or 'Makoto alone',CYAN)
        if can_restock:self.lines(19,4,'Restock keeps Theurgy charge.',count=1)

    def _summit_key(self,k):
        if self.record.phase==ADAMAH_PHASE:self._ascent_key(k);return
        if k==ESC:self.exit=True;return
        if k in ('v','V'):self.open_velvet('summit');return
        carry=getattr(self.record,'summit_carry',None)
        if k in ('r','R') and carry and carry.resources is not None:
            if self.write(self.store.commit,summit_carry=carry.restocked()):
                self.notice='Restocked HP, SP and items. Theurgy kept.'
            return
        if k in ('p','P') or k in ENTER and self.late_party is None:
            self.open_roster('summit','summit');return
        if k in ENTER:self.open_battle(late.SUMMIT_IDS[self.summit_index()])

    def complete_late_battle(self,encounter):
        if encounter not in LATE_BATTLES:return False
        if encounter==APPROACH:
            self.ascent.cache=self.battle.outcome=='win'
            if not self.ascent.cache:self.retries+=1
            self.go('summit')
            if not self.ascent.cache:self.notice='Regrouped. You can still bypass the patrol.'
            return True
        if self.battle.outcome!='win':
            self.retries+=1
            self.go('summit' if encounter in late.SUMMIT_IDS else 'late-brief')
            carry=getattr(self.record,'summit_carry',None)
            if encounter in late.SUMMIT_IDS and carry and carry.resources is not None:
                self.notice='Back at the saved checkpoint. Restock before retrying.'
            return True
        if encounter=='takaya-jin':
            self.go('late-between')
            return True
        carry=SummitCarry.from_battle(self.battle) if encounter in late.SUMMIT_IDS[:-1] else None
        if self.write(self.store.clear_operation,encounter,summit_carry=carry,
                      affinity_updates=getattr(self.battle,'affinity_updates',{})):
            if encounter==late.SUMMIT_IDS[-1]:
                self.battle=None
                self.encounter=''
                self.solo_seal=SoloSeal()
            self.ending_index=0
            self.resume()
        return True

    def draw_great_seal(self):
        s=self.solo_seal
        self.frame('MAKOTO / THE GREAT SEAL','↑↓ SELECT  ENTER CONFIRM  ESC TITLE')
        self.draw_scene_rows(seal_art(s.beat,self.w-5,8,s.outcome=='loss'),top=5,left=2)
        self.lines(13,4,s.copy,count=3)
        self.choices(s.choices,17,4)
        self.put(20,4,f'Makoto   HP {s.hp}/100',CYAN if s.hp>30 else GOLD)

    def _great_seal_key(self,k):
        if k==ESC:self.exit=True;return
        s=self.solo_seal
        pick=self.choose(k,len(s.choices))
        if pick is None:return
        if s.outcome=='loss':
            self.solo_seal=SoloSeal()
        else:
            s.choose(pick)
            if s.outcome=='win' and self.write(self.store.clear_operation,SEAL_PHASE):
                self.resume()
                return
        self.i=0

    def draw_epilogue(self):
        index=(late.RETURN,late.REMEMBER,late.ENDING).index(self.record.day)
        title,art,body=late.TRUE_END[index]
        self.frame(title,'ENTER CONTINUE  ESC TITLE')
        self.ending_art(art,height=11)
        self.lines(17,4,body,count=3)

    def _epilogue_key(self,k):
        if k==ESC:self.exit=True
        elif k in ENTER and self.write(self.store.ending_next):
            self.ending_index=0
            self.resume()

    def draw_ending(self):
        bad=self.record.ending=='bad'
        if bad:title,art,body=late.BAD_END[self.ending_index]
        else:title,art,body='THE GREAT SEAL','roof',''
        self.frame(title,'ENTER CONTINUE  ESC TITLE')
        self.ending_art(art,height=11)
        self.lines(17,4,body,count=3)

    def _ending_key(self,k):
        if k==ESC:self.exit=True
        elif k in ENTER:
            if self.record.ending=='bad' and self.ending_index==0:self.ending_index=1
            else:
                self.credit_started=monotonic()
                self.ending_index=0
                self.go('credits')

    def draw_credits(self):
        elapsed=monotonic()-self.credit_started
        self.frame('PERSONA 3 TERMINAL','ENTER TITLE  ESC TITLE' if self.ending_index else 'ENTER CONTINUE  ESC TITLE')
        art=('karaoke' if self.record.ending=='bad' else 'reunion') if self.ending_index else 'credits'
        self.ending_art(art,height=10,seconds=min(elapsed,1.9) if self.ending_index else elapsed)
        if not self.ending_index:
            self.mid(16,'Inspired by Persona 3 Reload',CYAN)
            self.mid(18,'ATLUS / P-STUDIO',DIM)

    def _credits_key(self,k):
        if k==ESC:self.exit=True
        elif k in ENTER:
            if self.ending_index:self.exit=True
            else:self.ending_index=1;self.credit_started=monotonic()

    def late_draw(self):
        {'discovery':self.draw_discovery,'late-aftermath':self.draw_late_aftermath,'late-interlude':self.draw_late_interlude,'late-brief':self.draw_late_brief,
         'late-between':self.draw_late_between,'decision':self.draw_decision,'summit':self.draw_summit,SEAL_PHASE:self.draw_great_seal,
         'epilogue':self.draw_epilogue,'ending':self.draw_ending,'credits':self.draw_credits}[self.page]()

    def late_key(self,k):
        {'discovery':self._discovery_key,'late-aftermath':self._late_aftermath_key,'late-interlude':self._late_interlude_key,'late-brief':self._late_brief_key,
         'late-between':self._late_between_key,'decision':self._decision_key,'summit':self._summit_key,SEAL_PHASE:self._great_seal_key,
         'epilogue':self._epilogue_key,'ending':self._ending_key,'credits':self._credits_key}[self.page](k)
