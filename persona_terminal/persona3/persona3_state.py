"""Independent, atomic save for the Persona 3 Terminal field chapter."""
from dataclasses import asdict, dataclass, replace
from datetime import date, timedelta
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import time_ns

from . import persona3_arqa as arqa
from . import persona3_upper as upper
from . import persona3_yabbashah as yabba
from . import persona3_yabbashah_upper as high
from . import persona3_late as late
from . import persona3_late_registry as registry
from . import persona3_junpei as junpei
from . import persona3_discovery_schedule as discovery
from .persona3_field_checkpoint import FieldCheckpoint, decode as decode_field_checkpoint
from .persona3_summit_checkpoint import SummitCarry, decode as decode_summit_carry

from persona_terminal.shared.paths import PROJECT_ROOT


DEFAULT_SAVE=PROJECT_ROOT / 'persona3-save.json'
VERSION=11
V8_FIELDS=('junpei_flowers','theurgy_drill_seen')
SEAL_PHASES=('summit-adamah','great-seal')
LATE_FIELDS=('tziah','tziah_upper','harabah','harabah_upper','adamah')
START=date(2009,4,6)
AWAKENING=date(2009,4,9)
TUTORIAL=date(2009,4,20)
MOON=date(2009,5,9)
END=date(2009,5,10)
LEGACY_PHASES=('arrival','awakening','tartarus','calendar','monorail','complete')
MOON_XP=150
BOSS_AFTERMATH={
    'priestess':('monorail',END,MOON_XP,'monorail-brake'),
    'emperor-empress':('rescue',arqa.AFTER_RESCUE,arqa.RESCUE_XP,'signal'),
    'hotel-lovers':('hotel',upper.AFTER_HOTEL,upper.HOTEL_XP,'hotel-after'),
    'chariot-justice':('august',yabba.AFTER_AUGUST,yabba.AUGUST_XP,'august-after'),
    'hermit':('hermit',high.AFTER_HERMIT,470,'hermit-after'),
}
PHASES=(*LEGACY_PHASES,'rescue','hotel','yakushima','august','hermit',*late.PHASE_DAYS,*SEAL_PHASES,*discovery.CHECKPOINTS,'epilogue')
PERSONAS=('Orpheus','Pixie','Angel','Nekomata',"Jack O'Lantern",'Apsaras',
          'Forneus','Omoikane','Valkyrie','Inugami','Jack Frost',
          'Take-Minakata','Naga','Sati','Principality','Rakshasa','Yamata-no-Orochi','Pale Rider')
FUSIONS=(
    ('Nekomata',('Orpheus','Pixie')),
    ('Apsaras',('Pixie','Angel')),
    ("Jack O'Lantern",('Pixie','Nekomata')),
    ('Forneus',('Apsaras','Angel')),
    ('Omoikane',('Forneus','Pixie')),
    ('Valkyrie',('Angel','Nekomata')),
    ('Inugami',('Omoikane',"Jack O'Lantern")),
    ('Jack Frost',('Apsaras','Pixie')),
    ('Take-Minakata',('Omoikane','Inugami')),
    ('Naga',('Valkyrie','Forneus')),
    ('Sati',('Inugami',"Jack O'Lantern")),
    ('Principality',('Angel','Omoikane')),
    ('Rakshasa',('Naga','Valkyrie')),
    ('Yamata-no-Orochi',('Naga','Sati')),
    ('Pale Rider',('Inugami','Take-Minakata')),
)
_EARLY_RECIPES=FUSIONS
SUMMON_PRICE=dict(zip(PERSONAS,(45,55,75,95,120,110,130,150,155,170,145,185,195,205,215,235,250,255)))
PERSONAS=(*PERSONAS,*registry.PERSONAS)
FUSIONS=(*FUSIONS,*registry.FUSIONS)
SUMMON_PRICE.update(registry.PRICES)
for i,name in enumerate(registry.PERSONAS):SUMMON_PRICE.setdefault(name,280+i*18)
LEVEL_STEPS=(0,100,230,390,600,850,1140,1470,1850,2260,2730,3250,3830,4470,5190,5990,6870,7830,
             *tuple(7830+1000*n+23*n*n for n in range(1,31)))
AWAKENING_XP=35
FLOOR_XP=(65,100,80,130,150)
REPLAY_XP=25


def next_story_date(day,*,flower=''):
    late_choice={'spoken':(junpei.FIRST_SHOP_DAY,), 'given':(junpei.PAYOFF_DAY,)}.get(flower,())
    return min((d for d in (MOON,arqa.RESCUE_DAY,arqa.BRIDGE,upper.HOTEL_DAY,
                            *upper.REPORT_DAYS,
                            yabba.OPENS,yabba.YAKUSHIMA,yabba.AUGUST_MOON,high.OPENS,high.HERMIT_DAY,
                            *discovery.PHASE_FOR_DAY,*late.MAJOR_DAYS,junpei.INVITATION,*late_choice) if d>day),default=None)


def level_for(xp):
    return sum(xp>=step for step in LEVEL_STEPS)


def legacy_experience(phase,depth):
    return (AWAKENING_XP if phase not in ('arrival','awakening') else 0)+sum(FLOOR_XP[:depth])+(
        MOON_XP if phase=='complete' else 0)


def distinct_slots(p5,p3):
    left,right=Path(p5),Path(p3)
    if left.resolve()==right.resolve():return False
    try:return not left.samefile(right)
    except FileNotFoundError:return True


class P3SaveError(ValueError):
    pass


@dataclass(frozen=True)
class FieldRecord:
    phase: str='arrival'
    day: date=START
    depth: int=0
    yen: int=50
    aid: int=1
    academics: int=0
    courage: int=0
    charm: int=0
    activity: str=''
    masks: tuple[str,...]=('Orpheus',)
    equipped: str='Orpheus'
    xp: int=0
    archive: tuple[tuple[str,str],...]=(('Orpheus',''),)
    arqa: int=0
    upper: int=0
    rescues: tuple[str,...]=()
    yabba: int=0
    monad: tuple[str,...]=()
    fragments: int=0
    yabba_upper: int=0
    tziah: int=0
    tziah_upper: int=0
    harabah: int=0
    harabah_upper: int=0
    adamah: int=0
    ending: str=''
    junpei_flowers: str=''
    theurgy_drill_seen: bool=False
    theurgy_intro_seen: bool=False
    arqa_tag_seen: bool=False
    aftermath: str=''
    field_checkpoint: FieldCheckpoint | None=None
    affinity_memory: tuple=()
    summit_carry: SummitCarry | None=None

    @property
    def affinity_index(self):
        return {species:dict(entries) for species,entries in self.affinity_memory}

    @property
    def level(self):
        return level_for(self.xp)

    @property
    def next_level_at(self):
        return LEVEL_STEPS[self.level] if self.level<len(LEVEL_STEPS) else None

    @property
    def compendium(self):
        return dict(self.archive)

    @property
    def stock(self):
        entries=self.compendium
        return {name:(entries[name],) if entries[name] else () for name in self.masks}


def _encode(state):
    data=asdict(state)
    for key in ('aftermath','field_checkpoint','affinity_memory','summit_carry'):
        if not data[key]:del data[key]
    if not state.arqa_tag_seen:del data['arqa_tag_seen']
    if not state.theurgy_intro_seen:del data['theurgy_intro_seen']
    data['day']=state.day.isoformat()
    return (json.dumps({'game':'persona-3-terminal','version':VERSION,'state':data},
                       ensure_ascii=False,indent=2)+'\n').encode()


def _decode(raw):
    data=json.loads(raw)
    if (not isinstance(data,dict) or data.get('game')!='persona-3-terminal'
            or type(data.get('version')) is not int or data['version'] not in (1,2,3,4,5,6,7,8,9,10,VERSION)
            or set(data)!={'game','version','state'}):
        raise P3SaveError('Not a Persona 3 field save.')
    body=data['state']
    if not isinstance(body,dict):raise P3SaveError('The field record is incomplete.')
    fields=set(FieldRecord.__dataclass_fields__)
    version=data['version']
    fields.difference_update(k for k in ('aftermath','field_checkpoint','affinity_memory','summit_carry')
                             if version<11 or k not in body)
    if version<11 or 'arqa_tag_seen' not in body:fields.remove('arqa_tag_seen')
    if version<11 or 'theurgy_intro_seen' not in body:fields.remove('theurgy_intro_seen')
    if version<8:fields.difference_update(V8_FIELDS)
    if version<7:fields.difference_update((*LATE_FIELDS,'ending'))
    if version<6:fields.remove(high.BLOCK)
    if version<5:fields-={'yabba','monad','fragments'}
    if version<4:fields-={'upper','rescues'}
    if version<3:fields.remove('arqa')
    if version==1:fields-={'archive','xp'}
    if set(body)!=fields:
        raise P3SaveError('The field record is incomplete.')
    if not isinstance(body.get('masks'),list):raise P3SaveError('Invalid Persona stock.')
    masks=tuple(body['masks'])
    if data['version']==1:
        if type(body['depth']) is not int or not 0<=body['depth']<=len(FLOOR_XP):
            raise P3SaveError('Invalid depth.')
        body={**body,'xp':legacy_experience(body['phase'],body['depth']),
              'archive':[[name,''] for name in masks]}
    if version<3:
        old_phase=body['phase']
        old_day=date.fromisoformat(body['day'])
        if (old_phase not in LEGACY_PHASES
                or old_phase=='complete' and old_day!=END
                or old_phase=='calendar' and not TUTORIAL<old_day<MOON
                or old_phase=='complete' and body['activity']):
            raise P3SaveError('Invalid original calendar position.')
        body={**body,'arqa':0}
        if old_phase=='complete':body['phase']='calendar'
    if version<4:
        v3_phase=body['phase']
        v3_day=date.fromisoformat(body['day'])
        if version==3 and (v3_phase=='hotel' or
                v3_phase=='complete' and (v3_day!=arqa.BRIDGE or body['activity']) or
                v3_phase=='calendar' and v3_day>=arqa.BRIDGE):
            raise P3SaveError('Invalid original calendar position.')
        body={**body,'upper':0,'rescues':[]}
        if v3_phase=='complete':body['phase']='calendar'
    if version<5:
        old_phase,old_day=body['phase'],date.fromisoformat(body['day'])
        if version==4 and (old_phase in ('august','yakushima') or
                old_phase=='complete' and (old_day!=upper.AFTER_HOTEL or body['activity']) or
                old_phase=='calendar' and old_day>=upper.HOTEL_DAY):
            raise P3SaveError('Invalid original calendar position.')
        body={**body,'yabba':0,'monad':[],'fragments':0}
        if old_phase=='complete':body['phase']='calendar'
    if version<6:
        if body['phase']=='hermit' or date.fromisoformat(body['day'])>yabba.AFTER_AUGUST:
            raise P3SaveError('Invalid original calendar position.')
        body[high.BLOCK]=0
        if version==5 and body['phase']=='complete' and date.fromisoformat(body['day'])==yabba.AFTER_AUGUST:
            body['phase']='calendar'
    if version<7:
        if date.fromisoformat(body['day'])>high.AFTER_HERMIT:
            raise P3SaveError('Invalid original calendar position.')
        body.update(dict.fromkeys(LATE_FIELDS,0),ending='')
    if version<8:
        if body['phase'] in SEAL_PHASES or body['activity'] in junpei.ACTIVITIES:
            raise P3SaveError('Invalid original calendar position.')
        body.update(junpei_flowers='',theurgy_drill_seen=False)
    if (version<9 and body['phase'] in late.AFTERMATH_PHASES or
            version<10 and body['phase'] in discovery.CHECKPOINTS):
        raise P3SaveError('Invalid original calendar position.')
    archive=body['archive']
    if not isinstance(body['monad'],list):raise P3SaveError('Invalid Monad clear record.')
    if not isinstance(body['rescues'],list):raise P3SaveError('Invalid rescue record.')
    if not isinstance(archive,list) or any(not isinstance(item,list) or len(item)!=2 for item in archive):
        raise P3SaveError('Invalid Compendium.')
    body={**body,'day':date.fromisoformat(body['day']),'masks':masks,
          'archive':tuple(tuple(row) for row in archive),'rescues':tuple(body['rescues']),'monad':tuple(body['monad'])}
    if version<11 and body['phase']=='calendar' and not body['activity']:
        # Older builds hard-coded these two debriefs on these dates. Preserve
        # that first replay, but the current receipt can be acknowledged once.
        key={yabba.AFTER_AUGUST:'august-after',high.AFTER_HERMIT:'hermit-after'}.get(body['day'])
        if key:body['aftermath']=key
    field_checkpoint=body.pop('field_checkpoint',None)
    summit_carry=body.pop('summit_carry',None)
    body['affinity_memory']=_decode_affinities(body.get('affinity_memory',[]))
    state=FieldRecord(**body)
    if field_checkpoint is not None:
        state=replace(state,field_checkpoint=decode_field_checkpoint(field_checkpoint,state))
    aftermath_dates={key:day for _,day,_,key in BOSS_AFTERMATH.values()}
    aftermath_dates.update(dict.fromkeys(('monorail-stopped','finale'),END))
    if (not isinstance(state.aftermath,str) or state.aftermath and
            (state.phase!='calendar' or state.activity or state.field_checkpoint or
             aftermath_dates.get(state.aftermath)!=state.day)):
        raise P3SaveError('Invalid pending aftermath.')
    if state.phase not in PHASES or state.activity not in ('','library','track','lounge',*junpei.ACTIVITIES):
        raise P3SaveError('Invalid field flags.')
    exact={'arrival':START,'awakening':AWAKENING,'tartarus':TUTORIAL,'monorail':MOON,'rescue':arqa.RESCUE_DAY,'hotel':upper.HOTEL_DAY,'august':yabba.AUGUST_MOON,'hermit':high.HERMIT_DAY,'complete':yabba.AFTER_AUGUST,**late.PHASE_DAYS,**dict.fromkeys(SEAL_PHASES,late.FINALE),
           **{p:d for p,(d,_,_) in discovery.CHECKPOINTS.items()}}
    if (state.phase in exact and state.day!=exact[state.phase] or
            state.phase=='calendar' and not (TUTORIAL<state.day<=late.FINALE and state.day not in (MOON,arqa.RESCUE_DAY,upper.HOTEL_DAY,yabba.AUGUST_MOON,high.HERMIT_DAY,*late.PHASE_FOR_DAY) and not yabba.YAKUSHIMA<=state.day<yabba.AIGIS)
            or state.arqa and state.day<arqa.OPENS or
            state.phase=='epilogue' and state.day not in (late.RETURN,late.REMEMBER,late.ENDING) or
            state.activity and state.phase!='calendar'):
        raise P3SaveError('Invalid calendar position.')
    for field,cap in (('depth',len(FLOOR_XP)),('arqa',len(arqa.FLOORS)),('upper',len(upper.FLOORS)),('yabba',len(yabba.FLOORS)),(high.BLOCK,len(high.FLOORS)),('fragments',99),('xp',999999),('yen',999999),('aid',99),('academics',99),('charm',99),('courage',99)):
        n=getattr(state,field)
        if type(n) is not int or not 0<=n<=cap:raise P3SaveError('Invalid '+field+'.')
    if summit_carry is not None:
        try:state=replace(state,summit_carry=decode_summit_carry(summit_carry,state))
        except ValueError as exc:raise P3SaveError(str(exc)) from exc
    if not junpei.valid_record(state):raise P3SaveError('Invalid flower errand.')
    if type(state.arqa_tag_seen) is not bool:raise P3SaveError('Invalid field observation.')
    if state.arqa_tag_seen and state.day<arqa.OPENS:raise P3SaveError('Invalid Lower Arqa observation.')
    if type(state.theurgy_drill_seen) is not bool:raise P3SaveError('Invalid Theurgy training flag.')
    if type(state.theurgy_intro_seen) is not bool:raise P3SaveError('Invalid Theurgy introduction flag.')
    terminal=state.phase in ('epilogue','ending')
    if state.ending not in (('true','bad') if terminal else ('',)) or state.phase=='epilogue' and state.ending!='true':
        raise P3SaveError('Invalid ending path.')
    for block in LATE_FIELDS:
        depth=getattr(state,block)
        if (type(depth) is not int or not 0<=depth<=len(registry.BLOCKS.get(block,((),))[0])
                or depth and state.day<registry.OPENS[block]):
            raise P3SaveError('Invalid '+block+' checkpoint.')
    if (any(type(x) is not str or x not in upper.BY_RESCUE or state.day<upper.BY_RESCUE[x].day for x in state.rescues)
            or len(set(state.rescues))!=len(state.rescues)):
        raise P3SaveError('Invalid rescue record.')
    if (any(type(x) is not str or x not in (*yabba.MONAD_STAGES,high.PASSAGE,*(row[0] for row in registry.PASSAGES.values())) for x in state.monad)
            or len(set(state.monad))!=len(state.monad)):
        raise P3SaveError('Invalid Monad clear record.')
    if (state.yabba_upper or high.PASSAGE in state.monad) and state.day<high.OPENS:
        raise P3SaveError('Upper Yabbashah is still sealed.')
    if (not state.masks or any(m not in PERSONAS for m in state.masks)
            or len(set(state.masks))!=len(state.masks) or state.equipped not in state.masks):
        raise P3SaveError('Invalid Persona stock.')
    names=[n for n,_ in state.archive]
    if any(n not in PERSONAS for n in names) or len(set(names))!=len(names) or not set(state.masks)<=set(names):
        raise P3SaveError('Invalid Compendium.')
    if any(skill for _,skill in state.archive):
        from .persona3_combat import SKILLS
        if any(type(skill) is not str or skill and skill not in SKILLS for _,skill in state.archive):
            raise P3SaveError('Invalid inherited skill.')
    elif any(skill!='' for _,skill in state.archive):
        raise P3SaveError('Invalid inherited skill.')
    return state


def _decode_affinities(rows):
    from .persona3_combat import AFFINITY_MARKS,ELEMENTS
    if not isinstance(rows,list) or len(rows)>256:
        raise P3SaveError('Invalid affinity memory.')
    entries={}
    for row in rows:
        if not isinstance(row,list) or len(row)!=2 or type(row[0]) is not str or not 0<len(row[0])<=80:
            raise P3SaveError('Invalid affinity entry.')
        species,known=row
        if species in entries or not isinstance(known,list) or not known or len(known)>len(ELEMENTS):
            raise P3SaveError('Invalid affinity species.')
        known_by_type={}
        for pair in known:
            if (not isinstance(pair,list) or len(pair)!=2 or type(pair[0]) is not str or type(pair[1]) is not str
                    or pair[0] not in ELEMENTS or pair[0] in known_by_type or pair[1] not in AFFINITY_MARKS or pair[1]=='unknown'):
                raise P3SaveError('Invalid remembered affinity.')
            known_by_type[pair[0]]=pair[1]
        entries[species]=tuple(known_by_type.items())
    return tuple(entries.items())


def available_fusions(day):
    # The April list remains short; the extension opens with Lower Arqa.
    early=_EARLY_RECIPES if day>=yabba.OPENS else _EARLY_RECIPES[:12] if day>=upper.OPENS else _EARLY_RECIPES[:8] if day>=arqa.OPENS else _EARLY_RECIPES[:3]
    dates={key:unlock for module in registry.TACTICS_MODULES
           for key,unlock in getattr(module,'FUSION_DATES',{}).items()}
    fallback=(late.when(9,10),late.when(9,10),late.when(10,6),late.when(10,6),
              late.when(11,6),late.when(11,6),late.when(12,10),late.when(12,10),late.JANUARY,late.JANUARY)
    return (*early,*(recipe for i,recipe in enumerate(registry.FUSIONS)
                     if day>=dates.get(recipe[0],fallback[min(i,len(fallback)-1)])))


class P3Store:
    def __init__(self,path=DEFAULT_SAVE):
        self.path=Path(path)
        self.reload()

    def practice_copy(self):
        """Loadout changes during an expedition practice stay in memory."""
        return PracticeStore(self.state)

    def _read(self):
        with self.path.open('rb') as stream:
            return stream.read(256*1024+1)

    def reload(self):
        self.state=None;self._raw=None
        try:self._raw=self._read()
        except FileNotFoundError:self.status='missing';return
        except OSError:self.status='unreadable';return
        try:
            if len(self._raw)>256*1024:raise P3SaveError('Field save exceeds size limit.')
            self.state=_decode(self._raw)
        except (ValueError,TypeError,KeyError):
            self.status='unreadable'
            try:other=json.loads(self._raw)
            except (UnicodeDecodeError,ValueError):return
            if isinstance(other,dict) and ('cleared' in other and 'teammates' in other
                    or 'game' in other and other['game']!='persona-3-terminal'):
                self.status='foreign'
            return
        self.status='ready'

    def _write(self,new,*,backup=False):
        raw=_encode(new)
        _decode(raw)  # Reuse the decoder for every durable mutation.
        self.path.parent.mkdir(parents=True,exist_ok=True)
        try:current=self._read()
        except FileNotFoundError:current=None
        if current!=self._raw:
            raise P3SaveError('Field save changed elsewhere. Return to the title and reload.')
        if current is not None and backup:
            if len(current)>256*1024:raise P3SaveError('Move the oversized save aside before starting over.')
            old=self.path.with_name(f'{self.path.stem}.backup-{time_ns()}{self.path.suffix}')
            with old.open('xb') as stream:
                stream.write(current);stream.flush();os.fsync(stream.fileno())
        temp=None
        try:
            with NamedTemporaryFile(mode='wb',dir=self.path.parent,prefix='.sees-',delete=False) as stream:
                temp=stream.name
                stream.write(raw);stream.flush();os.fsync(stream.fileno())
            os.replace(temp,self.path)
        finally:
            if temp and os.path.exists(temp):os.unlink(temp)
        self._raw,self.state,self.status=raw,new,'ready'
        return new

    def new_game(self,confirm=False):
        if self.status=='foreign':raise P3SaveError('That file belongs to another game.')
        if self.status!='missing' and not confirm:
            raise P3SaveError('Confirm a separate Persona 3 New Game backup.')
        if self.path.is_symlink():
            raise P3SaveError('Choose a regular Persona 3 save path.')
        return self._write(FieldRecord(),backup=self.status!='missing')

    def commit(self,**changes):
        if self.status!='ready':raise P3SaveError('No readable Persona 3 campaign.')
        if 'masks' in changes and 'archive' not in changes:
            entries=self.state.compendium
            for name in changes['masks']:entries.setdefault(name,'')
            changes['archive']=tuple(entries.items())
        return self._write(replace(self.state,**changes))

    def affinity_changes(self,updates=None):
        if not updates:return {}
        known=self.state.affinity_index
        for species,entries in updates.items():
            if entries:known.setdefault(species,{}).update(entries)
        return {'affinity_memory':tuple((n,tuple(entries.items())) for n,entries in known.items())}

    def grant_xp(self,amount,*,affinity_updates=None,**progress):
        if type(amount) is not int or amount<0:raise P3SaveError('Invalid experience award.')
        return self.commit(xp=min(999999,self.state.xp+amount),**progress,**self.affinity_changes(affinity_updates))

    def advance_night(self,skip=False):
        s=self.state
        if s.phase not in ('tartarus','calendar'):raise P3SaveError('No night to advance.')
        if s.aftermath or s.field_checkpoint and s.field_checkpoint.pending:
            raise P3SaveError('Finish the pending scene or reward first.')
        if skip and s.phase!='calendar':raise P3SaveError('Finish the first night before waiting.')
        target=next_story_date(s.day,flower=s.junpei_flowers)
        if target is None:raise P3SaveError('There is no later story day in this chapter.')
        day=target if skip else s.day+timedelta(days=1)
        phase={MOON:'monorail',arqa.RESCUE_DAY:'rescue',upper.HOTEL_DAY:'hotel',yabba.YAKUSHIMA:'yakushima',
               yabba.AUGUST_MOON:'august',high.HERMIT_DAY:'hermit',**late.PHASE_FOR_DAY,**discovery.PHASE_FOR_DAY}.get(day,'calendar')
        return self.commit(day=day,phase=phase,activity='',field_checkpoint=None)

    def junpei(self,action):
        s=self.state
        if action not in ('talk','buy','give'):
            raise P3SaveError('Unknown errand choice.')
        available=junpei.option(s,evening=action=='give') if s is not None else None
        if not available or available[0]!=action:
            raise P3SaveError('That choice is not available today.')
        if action=='talk':return self.commit(junpei_flowers='spoken',activity='junpei')
        if action=='buy':
            if s.yen<junpei.PRICE:raise P3SaveError(f'You need ¥{junpei.PRICE-s.yen} more.')
            return self.commit(junpei_flowers='bought',activity='flower-shop',yen=s.yen-junpei.PRICE)
        return self.commit(junpei_flowers='given')

    def finish_junpei(self):
        if self.state is None or not junpei.payoff_due(self.state):
            raise P3SaveError('There is no hospital visit today.')
        return self.commit(junpei_flowers='seen',activity='hospital')

    def advance_boss_aftermath(self):
        key=self.state.aftermath
        if not key:raise P3SaveError('No boss aftermath is pending.')
        return self.commit(aftermath={'monorail-brake':'monorail-stopped','monorail-stopped':'finale'}.get(key,''))

    def claim_field_card(self,pick,mask,coins,restored=None):
        s=self.state
        checkpoint=s.field_checkpoint
        if checkpoint is None or not checkpoint.pending:raise P3SaveError('No card is pending.')
        if pick==0:
            if mask in s.masks:raise P3SaveError('Already registered. Pick another card.')
            updates={'masks':(*s.masks,mask)}
        elif pick==1:updates={'yen':min(999999,s.yen+coins)}
        elif pick==2 and restored is not None:
            checkpoint=replace(checkpoint,resources=tuple(restored.items()))
            updates={}
        else:raise P3SaveError('Invalid card choice.')
        return self.commit(field_checkpoint=replace(checkpoint,pending=False),**updates)

    def clear_operation(self,operation,*,affinity_updates=None,summit_carry=None):
        if operation in BOSS_AFTERMATH:
            phase,day,award,aftermath=BOSS_AFTERMATH[operation]
            if self.state.phase==phase:
                return self.grant_xp(award,phase='calendar',day=day,aftermath=aftermath,affinity_updates=affinity_updates)
        phase_for={'fortune-strength':'october','hanged-man':'november','chidori':'chidori'}
        if operation in phase_for and self.state.phase==phase_for[operation]:
            day,xp=late.AFTER_BATTLES[operation]
            return self.grant_xp(xp,phase=late.AFTERMATH_FOR.get(operation,'medea-aftermath'),day=day,affinity_updates=affinity_updates)
        if operation in late.SUMMIT_IDS:
            i=late.SUMMIT_IDS.index(operation)
            if self.state.phase==late.SUMMIT_PHASES[i]:
                if i+1<len(late.SUMMIT_PHASES):
                    return self.commit(phase=late.SUMMIT_PHASES[i+1],summit_carry=summit_carry,
                                       **self.affinity_changes(affinity_updates))
                return self.commit(phase='great-seal',summit_carry=None,**self.affinity_changes(affinity_updates))
        if operation=='great-seal' and self.state.phase=='great-seal':
            return self.grant_xp(1800,phase='epilogue',day=late.RETURN,ending='true',affinity_updates=affinity_updates)
        raise P3SaveError('That operation is not active.')

    def finish_discovery(self):
        if self.state is None or self.state.phase not in discovery.CHECKPOINTS:
            raise P3SaveError('No story scene is pending.')
        state=self.state
        tomorrow=state.day+timedelta(days=1) if state.phase=='bridge-revelation' else state.day
        return self.commit(phase=discovery.CHECKPOINTS[state.phase][2],day=tomorrow)

    def finish_aftermath(self):
        if self.state is None or self.state.phase not in late.AFTERMATH_PHASES:
            raise P3SaveError('No aftermath scene is pending.')
        return self.commit(phase='calendar')

    def ryoji_choice(self,spare):
        if self.state.phase!='decision' or type(spare) is not bool:raise P3SaveError('No decision is pending.')
        if spare:return self.commit(phase='calendar',day=late.JANUARY)
        return self.commit(phase='ending',day=late.ENDING,ending='bad')

    def begin_summit(self):
        if self.state.phase!='finale':raise P3SaveError('The summit is not open.')
        return self.commit(phase='summit-adamah')

    def reach_summit(self):
        if self.state.phase!='summit-adamah':raise P3SaveError('The ascent is not active.')
        return self.commit(phase=late.SUMMIT_PHASES[0])

    def ending_next(self):
        s=self.state
        if s.phase!='epilogue':raise P3SaveError('No epilogue is active.')
        if s.day==late.RETURN:return self.commit(day=late.REMEMBER)
        if s.day==late.REMEMBER:return self.commit(day=late.ENDING)
        return self.commit(phase='ending')


    def trip_next(self):
        if self.state.phase!='yakushima':raise P3SaveError('No trip is active.')
        day={yabba.YAKUSHIMA:yabba.BEACH,yabba.BEACH:yabba.AIGIS-timedelta(days=1)}.get(self.state.day,yabba.AIGIS)
        return self.commit(day=day,phase='calendar' if day==yabba.AIGIS else 'yakushima')

    def clear_monad(self,key,*,affinity_updates=None):
        s=self.state
        rewards={**yabba.MONAD_REWARD,high.PASSAGE:high.PASSAGE_REWARD,
                 **{row[0]:row[2] for row in registry.PASSAGES.values()}}
        if (s.phase!='calendar' or s.day<(high.OPENS if key==high.PASSAGE else yabba.OPENS)
                or key not in rewards or key in s.monad):
            raise P3SaveError('That Monad reward is not available.')
        xp,fragments,yen=rewards[key]
        return self.grant_xp(xp,monad=(*s.monad,key),fragments=min(99,s.fragments+fragments),
                             yen=min(999999,s.yen+yen),affinity_updates=affinity_updates)

    def spend_fragments(self,count):
        if self.state.day<yabba.OPENS or type(count) is not int or not 0<count<=self.state.fragments:
            raise P3SaveError('Not enough Twilight Fragments.')
        return self.commit(fragments=self.state.fragments-count)

    def rescue_civilian(self,ident,floor):
        s=self.state
        person=upper.BY_RESCUE.get(ident)
        if (s.phase!='calendar' or person is None or person.floor!=floor or
                not person.day<=s.day<=upper.RESCUE_DEADLINE or ident in s.rescues):
            raise P3SaveError('That rescue is no longer active.')
        return self.commit(rescues=(*s.rescues,ident),yen=min(999999,s.yen+person.yen),
                           aid=min(99,s.aid+person.kits))

    def activity(self,kind):
        s=self.state
        if s.phase!='calendar' or s.activity:
            raise P3SaveError('Today’s time slot is already used.')
        updates={
            'library':{'academics':min(99,s.academics+1),'yen':min(999999,s.yen+60)},
            'track':{'courage':min(99,s.courage+1),'aid':min(99,s.aid+1)},
            'lounge':{'charm':min(99,s.charm+1)},
        }
        if kind not in updates:raise P3SaveError('Unknown activity.')
        return self.commit(activity=kind,**updates[kind])

    def fusion_preview(self,result):
        s=self.state
        recipe=next((r for r in available_fusions(s.day) if r[0]==result),None)
        if recipe is None:raise P3SaveError('Unknown fusion recipe.')
        _,parents=recipe
        missing=tuple(n for n in parents if n not in s.masks)
        return FusionPreview(result,parents,missing,result in s.masks,result in s.compendium)

    def inheritance_options(self,result):
        from .persona3_combat import persona_skills
        check=self.fusion_preview(result)
        if not check.ready:return ()
        innate=set(persona_skills(result,self.state.level))
        options=[]
        for name in check.parents:
            for skill in persona_skills(name,self.state.level,self.state.stock[name]):
                if skill not in innate and not any(x[1]==skill for x in options):
                    options.append((name,skill))
        return tuple(options)

    def fuse(self,result,skill=''):
        check=self.fusion_preview(result)
        if not check.ready:raise P3SaveError(check.reason)
        if skill and skill not in {s for _,s in self.inheritance_options(result)}:
            raise P3SaveError('That skill cannot be inherited here.')
        active=tuple(name for name in self.state.masks if name not in check.parents)
        equipped=result if self.state.equipped in check.parents else self.state.equipped
        return self.commit(masks=(*active,result),equipped=equipped,
                           archive=(*self.state.archive,(result,skill)))

    def resummon(self,name):
        s=self.state
        if name not in s.compendium:raise P3SaveError('Register that Persona first.')
        if name in s.masks:raise P3SaveError('Already in your stock.')
        cost=SUMMON_PRICE[name]
        if s.yen<cost:raise P3SaveError(f'Need ¥{cost-s.yen} more.')
        return self.commit(masks=(*s.masks,name),yen=s.yen-cost)


class PracticeStore(P3Store):
    def __init__(self,state):
        self.state,self.status=state,'ready'

    def _write(self,new,*,backup=False):
        _decode(_encode(new))
        self.state=new
        return new


@dataclass(frozen=True)
class FusionPreview:
    result: str
    parents: tuple[str,...]
    missing: tuple[str,...]
    active: bool
    registered: bool

    @property
    def ready(self):
        return not self.registered and not self.missing

    @property
    def status(self):
        if self.active:return 'IN STOCK'
        if self.registered:return 'IN COMPENDIUM'
        if self.missing:return 'MISSING PARENTS'
        return 'READY'

    @property
    def reason(self):
        if self.active:return 'Already in your stock.'
        if self.registered:return 'Resummon it from the Compendium.'
        if self.missing:return 'Need '+', '.join(self.missing)+' in stock.'
        return ''
