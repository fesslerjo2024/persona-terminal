"""Playable Persona 3 field chapter, isolated from every Persona 5 route."""
from calendar import Calendar
import curses as C
import random
import textwrap
import time

from battle_ui import CYAN, DIM, ENTER, ESC, GOLD, GREEN, RED, WHITE
from reel_palette import IDS
from terminal_surface import TerminalSurface
import persona3_opening as opening
import persona3_combat as combat
import persona3_cards as reward_cards
from persona3_state import END, FUSIONS, MOON, TUTORIAL, P3SaveError
from persona3_thebel import FLOORS, H, W, Hall

BLUE=IDS['navy']
TEAL=IDS['teal']
MOVES={C.KEY_UP:'up',C.KEY_DOWN:'down',C.KEY_LEFT:'left',C.KEY_RIGHT:'right',
       'w':'up','s':'down','a':'left','d':'right'}
ACTIVITIES=(
    ('library','Library','Study  /  Academics +1, ¥40'),
    ('track','Track practice','Courage +1, one field kit'),
    ('lounge','Dorm lounge','Charm +1, +6 SP on first clear tonight'),
)
PARTY=tuple(combat.PARTY)
FOOT='↑↓ CHOOSE  ENTER OPEN  ESC TITLE'


class P3App(TerminalSurface):
    def __init__(self,screen,store,seed=None):
        self.s=screen;self.store=store;self.seed=seed
        self.page='';self.i=0;self.notice='';self.exit=None
        self.scene='';self.started=0.;self.back='';self.overlay=''
        self.hall=None;self.resources={};self.caps={};self.inventory={};self.battle=None
        self.retries=0;self.sp_bonus=False;self.practice=False
        self.resume_hall=None;self.free_expedition=False;self.practice_depth=0;self.practice_aid=0
        self.guided_expedition=False;self.expedition_back=''
        self.patrol_rng=random.Random(seed)
        self.resume()

    @property
    def record(self):
        return self.store.state

    def go(self,page):
        self.page=page;self.i=0;self.notice=''

    def beat(self,scene):
        self.scene=scene
        self.go('story')

    def resume(self):
        phase=self.record.phase
        if phase in ('arrival','awakening','tartarus','complete'):
            self.beat('finale' if phase=='complete' else phase)
        elif phase=='monorail':self.go('operation')
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

    def art(self,key,t,y=5,height=9):
        rows=opening.render(key,t,self.w-5,height)
        for yy,row in enumerate(rows,y):
            xx=2
            for run,ink in row:
                if run.strip():self.put(yy,xx,run,{'white':WHITE,'gold':GOLD,'green':GREEN,
                    'cyan':CYAN,'red':RED}.get(ink,IDS.get(ink,DIM)))
                xx+=len(run)

    def draw_story(self):
        beat=opening.BY_ID[self.scene]
        footer='T TARTARUS PRACTICE  ENTER TITLE' if self.scene=='finale' else 'ENTER NEXT  ESC TITLE'
        self.frame(beat.heading,footer)
        self.art(beat.art,opening.TRANSITION_SECONDS,height=9)
        top=15
        for line in beat.lines:
            wrapped=textwrap.wrap(line,self.w-8)
            for item in wrapped:
                if top>=self.h-4:return
                self.put(top,4,item)
                top+=1

    def _story_key(self,k):
        if self.scene=='finale' and k in ('t','T'):
            self.deploy()
            return
        if k==ESC or (k in ENTER and self.scene=='finale'):
            self.exit=True;return
        if k not in ENTER:return
        if self.scene=='arrival':
            from persona3_state import AWAKENING
            if self.write(self.store.commit,phase='awakening',day=AWAKENING):self.resume()
        elif self.scene=='awakening':self.open_battle('awakening')
        elif self.scene=='tartarus':self.deploy()

    def options(self):
        s=self.record
        if not s.activity:
            return [row[1] for row in ACTIVITIES]+['Head to the dorm']
        base=['Enter Tartarus','Velvet Room','Rest until tomorrow']
        if s.depth==len(FLOORS):base.append('Wait for the full moon')
        return base

    def draw_calendar(self):
        s=self.record
        stage='AFTER SCHOOL' if not s.activity else 'EVENING'
        self.frame(f'{s.day.strftime("%B").upper()} / {stage}',FOOT)
        for x,label in enumerate(('M','T','W','T','F','S','S')):
            self.put(6,3+4*x,label,TEAL)
        for row,week in enumerate(Calendar().monthdayscalendar(s.day.year,s.day.month),7):
            for x,number in enumerate(week):
                if not number:continue
                mark=number==s.day.day
                moon=s.day.month==5 and number==MOON.day
                self.put(row,2+4*x,f'{number:>2}',GOLD if moon else CYAN if mark else DIM,
                         mark or moon,mark)
        self.put(15,3,f'Thebel  {s.depth}/{len(FLOORS)} checkpoints',TEAL)
        self.put(17,3,f'¥{s.yen}   FIELD KITS {s.aid}',WHITE)
        self.put(19,3,f'ACA {s.academics}  COU {s.courage}  CHA {s.charm}',DIM)
        self.choices(self.options(),7,33,self.w-36)
        if not s.activity and self.i<3:
            self.lines(17,34,ACTIVITIES[self.i][2],self.w-38,3,TEAL)
        if s.activity:
            self.put(17,34,f'FULL MOON IN {(MOON-s.day).days} DAYS',GOLD)

    def _calendar_key(self,k):
        if k==ESC:self.exit=True;return
        pick=self.choose(k,len(self.options()))
        if pick is None:return
        if not self.record.activity and not self.practice:
            if pick<3:
                if self.write(self.store.activity,ACTIVITIES[pick][0]):self.go('evening')
            else:
                # Going straight to the dorm leaves this day's stat unchanged.
                self.practice=True
                self.go('evening')
            return
        self._evening_action(pick)

    def draw_evening(self):
        s=self.record
        self.frame('IWATODAI DORM / EVENING','↑↓ CHOOSE  ENTER OPEN  ESC CALENDAR')
        self.art('dorm',opening.TRANSITION_SECONDS,height=8)
        self.choices(self.evening_options(),13,4,34)
        self.put(13,41,f'FULL MOON IN {(MOON-s.day).days} DAYS',GOLD)

    def evening_options(self):
        return ['Enter Tartarus','Velvet Room','Rest until tomorrow']+(
            ['Wait for the full moon'] if self.record.depth==len(FLOORS) else [])

    def _evening_action(self,pick):
        if pick==0:self.deploy()
        elif pick==1:self.open_velvet(self.page)
        else:self.next_night(skip=pick==3)

    def _evening_key(self,k):
        if k==ESC:self.practice=False;self.go('calendar');return
        pick=self.choose(k,len(self.evening_options()))
        if pick is not None:self._evening_action(pick)

    def next_night(self,skip=False):
        if self.write(self.store.advance_night,skip=skip):
            self.hall=None
            self.resume_hall=None
            self.practice=False
            if self.record.phase=='monorail':self.go('operation')
            else:self.go('calendar')

    @property
    def field_depth(self):
        return self.practice_depth if self.free_expedition else self.record.depth

    @property
    def field_kits(self):
        return self.practice_aid if self.free_expedition else self.record.aid

    def deploy(self):
        self.started=time.monotonic()
        self.free_expedition=self.record.phase in ('complete','monorail')
        self.expedition_back='story' if self.record.phase=='complete' else 'operation'
        self.practice_depth=self.record.depth
        self.practice_aid=self.record.aid
        patrol_seed=None if self.seed is None else self.seed ^ self.record.day.toordinal()
        self.patrol_rng=random.Random(patrol_seed)
        self.guided_expedition=self.record.phase=='tartarus' and self.record.depth==0
        self.sp_bonus=self.record.activity=='lounge' and not self.free_expedition
        base=combat.P3Battle('thebel-patrol',persona=self.record.equipped,seed=self.seed)
        self.caps=base.resources
        self.resources=dict(self.caps)
        self.inventory=dict(base.inventory)
        self.resume_hall=None
        self.hall=Hall(0) if self.guided_expedition else None
        self.go('dark-hour')

    def draw_dark_hour(self):
        elapsed=time.monotonic()-self.started
        if elapsed>=opening.TRANSITION_SECONDS:
            self.go('hall' if self.guided_expedition else 'entrance');self.draw();return
        self.draw_scene_rows(opening.render('dark_hour',elapsed,self.w-1,self.h))

    def entrance_targets(self):
        depth=self.field_depth
        targets=[]
        if self.resume_hall is not None:
            targets.append(('resume',f'Resume {self.resume_hall.floor.number:02d}F'))
        if self.guided_expedition:
            if not depth:targets.append((0,'02F / Entry Hall'))
        elif depth<len(FLOORS):
            targets.append((depth,f'{FLOORS[depth].number:02d}F / Continue ascent'))
        else:
            targets.append(('border','22F / Sealed Border'))
        targets.extend((i,f'{FLOORS[i].number:02d}F / Revisit') for i in range(depth))
        return tuple(targets)

    def draw_entrance(self):
        footer='↑↓ FLOOR  ENTER TRAVEL  X END PRACTICE' if self.free_expedition else '↑↓ FLOOR  ENTER TRAVEL  X EXTRACT'
        self.frame('TARTARUS / ENTRANCE',footer)
        entries=self.entrance_targets()
        self.choices([label for _,label in entries],7,3,29,2)
        right=max(34,self.w//2+1)
        self.put(7,right,f'THEBEL   {self.field_depth}/{len(FLOORS)}',TEAL)
        self.put(9,right,f'FIELD KITS  {self.field_kits}',WHITE)
        if self.free_expedition:self.lines(12,right,'Practice only. No saved rewards.',self.w-right-3,2,TEAL)
        else:self.lines(12,right,'Travel keeps this night’s HP, SP and items.',self.w-right-3,3,TEAL)
        target,_=entries[self.i]
        if target=='border':detail='The next block is still sealed.'
        elif target=='resume':detail='Return to your place on this floor.'
        elif target<self.field_depth:detail='Fresh patrols. Cleared gatekeepers stay gone.'
        else:detail=FLOORS[target].label.title()
        self.lines(17,right,detail,self.w-right-3,3)

    def go_entrance(self,*,resume=False):
        self.resume_hall=self.hall if resume else None
        self.hall=None
        self.go('entrance')

    def _select_floor(self,index):
        if not 0<=index<=min(self.field_depth,len(FLOORS)):
            self.notice='That floor has not been reached.'
            return
        self.resume_hall=None
        if index==len(FLOORS):
            self.hall=None
            self.go('border')
            return
        replay=index<self.field_depth
        offset=self.patrol_rng.randrange(len(FLOORS[index].patrol)) if replay else 0
        self.hall=Hall(index,replay=replay,patrol_offset=offset)
        self.go('hall')

    def _entrance_key(self,k):
        if k in ('x','X',ESC):
            self.overlay='extract'
            return
        entries=self.entrance_targets()
        pick=self.choose(k,len(entries))
        if pick is None:return
        target,_=entries[pick]
        if target=='resume':
            self.hall,self.resume_hall=self.resume_hall,None
            self.go('hall')
        elif target=='border':self._select_floor(len(FLOORS))
        else:self._select_floor(target)

    def end_expedition(self):
        if self.free_expedition:
            self.hall=None
            self.resume_hall=None
            self.free_expedition=False
            if self.expedition_back=='story':self.beat('finale')
            else:self.go('operation')
        else:self.next_night()

    def draw_hall(self):
        hall=self.hall
        floor=hall.floor
        sealed=not hall.stairs_open
        floor_type=(('GATEKEEPER FLOOR' if floor.guardian else 'SHADOW FLOOR') if sealed
                    else 'REVISIT / PATROL' if hall.replay and not hall.defeated else 'FLOOR CLEARED')
        footer='ARROWS / WASD  M KIT  T ENTRANCE  X EXTRACT'
        if not sealed and hall.pos==floor.stairs:footer+='  ENTER STAIRS'
        self.frame(f'{floor.number:02d}F / {floor_type}',footer)
        ox,oy=4,7
        outline=RED if sealed and floor.guardian else BLUE
        self.put(6,ox-1,'╔'+'═'*W+'╗',outline)
        self.put(oy+H,ox-1,'╚'+'═'*W+'╝',outline)
        for y in range(H):
            self.put(oy+y,ox-1,'║',outline);self.put(oy+y,ox+W,'║',outline)
            for x in range(W):
                ch=hall.glyph(x,y)
                color={'@':CYAN,'▒':BLUE,'·':DIM,'⇧':CYAN,'◆':RED,'⊗':RED}.get(ch,WHITE)
                if ch!=' ':self.put(oy+y,ox+x,ch,color,ch in '@◆⇧⊗')
        self.draw_hall_party(34)
        if sealed:
            label=floor.guardian or ('SHADOW CLOSE' if hall.alert else floor.label)
            self.lines(18,34,label,self.w-37,1,RED if floor.guardian or hall.alert else GOLD)
            self.lines(19,34,'Step onto the sealed stairs to fight.',self.w-37,2,GOLD)
            legend='@ You   ◆ Shadow   ⊗ Battle'
        else:
            self.put(18,34,'STAIRS OPEN',CYAN,True)
            if hall.replay and not hall.defeated:
                self.lines(19,34,'Shadows still patrol here.',self.w-37,1,TEAL)
                legend='@ You   ◆ Shadow   ⇧ Stairs'
            else:legend='@ You   ⇧ Stairs'
        self.put(19,4,legend,DIM)
        self.put(20,4,f'FIELD KITS  {self.field_kits}',TEAL)

    def draw_hall_party(self,x):
        width=min(22,self.w-x-15)
        for i,name in enumerate(PARTY):
            if name not in self.resources:continue
            y=5+i*5
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

    def _hall_key(self,k):
        if k in ('t','T',ESC):self.go_entrance(resume=True);return
        if k in ('x','X'):self.overlay='extract';return
        if k in ('m','M'):
            need=any(hp and hp<self.caps[name][0] for name,(hp,_) in self.resources.items())
            if not need or not self.field_kits:
                self.notice='No injured standing ally.' if not need else 'No field kits left.'
                return
            if self.free_expedition:self.practice_aid-=1
            elif not self.write(self.store.commit,aid=self.record.aid-1):return
            self.resources={n:(min(self.caps[n][0],hp+42) if hp else 0,sp)
                            for n,(hp,sp) in self.resources.items()}
            self.notice='First aid restored up to 42 HP.'
            return
        if k in ENTER and self.hall.pos==self.hall.floor.stairs and self.hall.stairs_open:self._stairs()
        elif k in MOVES:
            nextstep=self.hall.step(MOVES[k])
            if nextstep=='battle':self.open_battle(self.hall.encounter)
            elif nextstep=='stairs':self._stairs()

    def draw_border(self):
        self.frame('22F / THEBEL BORDER','ENTER ENTRANCE  X EXTRACT')
        self.art('thebel',opening.TRANSITION_SECONDS,height=10)
        self.lines(17,4,'The next block is sealed. Return to the entrance to revisit any open floor.',count=2)

    def draw_operation(self):
        beat=opening.BY_ID['monorail']
        self.frame(beat.heading,'ENTER BOARD  V VELVET  T PRACTICE  ESC TITLE')
        self.art('monorail',opening.TRANSITION_SECONDS,height=9)
        top=15
        for line in beat.lines:
            for item in textwrap.wrap(line,self.w-8):
                if top>=self.h-5:break
                self.put(top,4,item);top+=1
        details=combat.PERSONAS[self.record.equipped]
        warning=f'{self.record.equipped} is weak to Ice. Change in Velvet Room.' if details['affinity'].get('Ice')=='weak' else 'Action countdown starts in battle.'
        self.put(self.h-5,4,warning,GOLD)

    def _operation_key(self,k):
        if k==ESC:self.exit=True
        elif k in ('v','V'):self.open_velvet('operation')
        elif k in ('t','T'):self.deploy()
        elif k in ENTER:self.open_battle('priestess')

    def open_battle(self,encounter):
        self.encounter=encounter
        state=self.record
        seed=None if self.seed is None else self.seed ^ state.day.toordinal() ^ self.retries
        self.battle=combat.P3Battle(encounter,
            resources=None if encounter in ('awakening','priestess') else self.resources,
            inventory=None if encounter in ('awakening','priestess') else self.inventory,
            persona='Orpheus' if encounter=='awakening' else state.equipped,
            seed=seed)
        self.go('battle')

    def _battle_key(self,k):
        if self.battle.key(k):return
        if self.battle.outcome!='win':
            self.retries+=1
            if self.encounter=='priestess':self.go('operation')
            elif self.encounter=='awakening':self.beat('awakening')
            else:
                # Story nights end on defeat. Practice just returns to its entry.
                self.end_expedition()
            return
        if self.encounter=='awakening':
            if self.write(self.store.commit,phase='tartarus',day=TUTORIAL):self.beat('tartarus')
        elif self.encounter=='priestess':
            if self.write(self.store.commit,phase='complete',day=END):self.beat('finale')
        else:
            self._finish_hall_battle()

    def _finish_hall_battle(self):
        cleared=self.hall.index+1
        if cleared>self.field_depth:
            if self.free_expedition:self.practice_depth=cleared
            elif not self.write(self.store.commit,depth=cleared,yen=min(999999,self.record.yen+25)):
                return
        self.hall.defeated=True
        self.hall.alert=False
        self.resources=self.battle.resources
        self.inventory=dict(self.battle.inventory)
        if self.sp_bonus:
            self.recover(0,6)
            self.sp_bonus=False
        if not self.free_expedition:self.go('shuffle')
        elif self.hall.pos==self.hall.floor.stairs:self._stairs()
        else:self.go('hall')

    def recover(self,hp,sp):
        self.resources={n:(min(self.caps[n][0],left+hp),min(self.caps[n][1],mana+sp)) if left else (left,mana)
                        for n,(left,mana) in self.resources.items()}

    def draw_battle(self):
        self.battle.draw(self)
        if self.notice:self.put(self.h-4,3,self.notice[:self.w-6],GOLD,True)

    def draw_shuffle(self):
        self.frame('SHUFFLE TIME','←→ SELECT  ENTER CLAIM')
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
        mask=self.hall.floor.mask;s=self.record
        if pick==0:
            if mask in s.masks:
                self.notice='Already registered. Pick another card.';return
            if not self.write(self.store.commit,masks=(*s.masks,mask)):return
        elif pick==1:
            if not self.write(self.store.commit,yen=min(999999,s.yen+self.shuffle_yen())):return
        else:self.recover(30,12)
        self.go('hall')
        if self.hall.pos==self.hall.floor.stairs:self._stairs()

    def open_velvet(self,back):
        self.back=back;self.go('velvet')

    def draw_velvet(self):
        self.frame('VELVET ROOM / COMPENDIUM', '↑↓ PICK  ENTER EQUIP  F FUSION  ESC BACK')
        self.art('velvet',opening.TRANSITION_SECONDS,height=6)
        self.choices([('◆ ' if n==self.record.equipped else '  ')+n for n in self.record.masks],
                     12,3,min(27,self.w//2),step=1)
        right=self.w//2+1
        self.put(12,right,f'¥{self.record.yen}',GOLD)
        self.put(13,right,'Equipped: '+self.record.equipped,CYAN)
        self.persona_details(self.record.masks[self.i],right,15,self.w-right-3,18)

    def recipes(self):
        return tuple(self.store.fusion_preview(name) for name,_,_ in FUSIONS)

    def persona_details(self,name,x,move_y,width,affinity_y):
        details=combat.PERSONAS[name]
        self.lines(move_y,x,'Skills: '+', '.join(details['skills']),width,2)
        changes=', '.join(f'{e} {v}' for e,v in details['affinity'].items()) or 'Normal'
        self.lines(affinity_y,x,'Defense: '+changes,width,3,TEAL)

    def draw_fusion(self):
        cards=self.recipes()
        item=cards[self.i]
        footer='↑↓ RECIPE  ENTER REVIEW  ESC BACK' if item.ready else '↑↓ RECIPE  ESC BACK'
        self.frame('VELVET ROOM / FUSION',footer)
        split=max(28,min(41,self.w//2-2))
        for y in range(6,20):self.put(y,split,'│',BLUE)
        self.choices([(card.result,DIM if card.registered else WHITE) for card in cards],6,3,split-5,step=4)
        for n,card in enumerate(cards):
            self.put(7+n*4,7,card.status,TEAL if card.ready else DIM if card.registered else GOLD)
        if not any(card.ready for card in cards):
            label='All recipes registered' if all(card.registered for card in cards) else 'No recipe ready'
            self.put(19,3,label,TEAL)
        x=split+3
        width=self.w-x-3
        self.put(6,x,item.result,CYAN,True)
        for y,parent in enumerate(item.parents,8):
            ok=parent not in item.missing
            self.put(y,x,f'{"✓" if ok else "×"} {parent}',TEAL if ok else GOLD)
        balance=(f'¥{item.cost}  /  ¥{item.balance} after' if item.ready else
                 'Already in compendium' if item.registered else f'¥{item.cost}  /  ¥{self.record.yen} on hand')
        self.put(11,x,balance,GOLD if not item.registered else DIM)
        self.persona_details(item.result,x,13,width,16)

    def draw_fuse_confirm(self):
        item=self.recipes()[self.i]
        self.frame('REGISTER '+item.result.upper()+'?','ENTER FUSE  ESC CANCEL')
        self.put(7,4,' + '.join(item.parents),CYAN)
        self.put(9,4,f'Pay ¥{item.cost}   /   ¥{self.record.yen} → ¥{item.balance}',GOLD)
        self.persona_details(item.result,4,11,self.w-8,13)
        self.put(17,4,'Both parents stay registered.',TEAL)
        self.put(18,4,self.record.equipped+' stays equipped.',TEAL)

    def _velvet_key(self,k):
        if k==ESC:self.go(self.back)
        elif k in ('f','F'):
            self.go('fusion')
            self.i=next((i for i,r in enumerate(self.recipes()) if r.ready),0)
        else:
            pick=self.choose(k,len(self.record.masks))
            if pick is not None and self.write(self.store.commit,equipped=self.record.masks[pick]):
                self.notice='Equipped '+self.record.equipped+'.'

    def _fusion_key(self,k):
        if k==ESC:self.go('velvet');return
        old=self.i
        pick=self.choose(k,len(FUSIONS))
        if old!=self.i:self.notice=''
        if pick is None:return
        preview=self.recipes()[pick]
        if preview.ready:
            self.notice=''
            self.page='fuse-confirm'
        else:self.notice=preview.reason

    def _fuse_confirm_key(self,k):
        if k==ESC:self.page='fusion';self.notice=''
        elif k in ENTER:
            item=self.recipes()[self.i]
            if self.write(self.store.fuse,item.result):
                self.go('velvet')
                self.i=self.record.masks.index(item.result)
                self.notice=f'Registered {item.result}  /  ¥{item.cost} paid.'

    def draw_overlay(self):
        if self.overlay=='extract':
            self.frame('END PRACTICE?' if self.free_expedition else 'END EXPEDITION?','ENTER CONFIRM  ESC STAY')
            detail=('End practice and return without advancing the date.' if self.free_expedition else
                    'The night ends. Cleared checkpoints and claimed cards are saved.')
            self.lines(9,4,detail,count=3)
        elif self.overlay=='quit':
            self.frame('LEAVE PERSONA 3?','ENTER QUIT  ESC STAY')
            self.lines(9,4,'Only recorded checkpoints and time slots carry forward.',count=3)

    def draw(self):
        if self.overlay:self.draw_overlay();return
        {'story':self.draw_story,'calendar':self.draw_calendar,'evening':self.draw_evening,
         'dark-hour':self.draw_dark_hour,'entrance':self.draw_entrance,'hall':self.draw_hall,'border':self.draw_border,
         'operation':self.draw_operation,'battle':self.draw_battle,'shuffle':self.draw_shuffle,
         'velvet':self.draw_velvet,'fusion':self.draw_fusion,'fuse-confirm':self.draw_fuse_confirm}[self.page]()

    def key(self,k):
        if self.overlay:
            if k==ESC:self.overlay=''
            elif k in ENTER:
                if self.overlay=='quit':self.exit=False
                else:self.end_expedition()
                self.overlay=''
            return
        if k in ('q','Q'):
            if self.page in ('dark-hour','entrance','hall','border','battle','shuffle'):
                self.overlay='quit'
            else:self.exit=False
            return
        if self.page=='dark-hour':
            if k in (*ENTER,ESC,' '):self.go('hall' if self.guided_expedition else 'entrance')
            return
        if self.page=='border':
            if k in (*ENTER,ESC,'t','T'):self.go_entrance()
            elif k in ('x','X'):self.overlay='extract'
            return
        {'story':self._story_key,'calendar':self._calendar_key,'evening':self._evening_key,
         'entrance':self._entrance_key,'hall':self._hall_key,'operation':self._operation_key,'battle':self._battle_key,
         'shuffle':self._shuffle_key,'velvet':self._velvet_key,'fusion':self._fusion_key,
         'fuse-confirm':self._fuse_confirm_key}[self.page](k)

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
