"""Independent, atomic save for the Persona 3 Terminal field chapter."""
from dataclasses import asdict, dataclass, replace
from datetime import date, timedelta
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import time_ns

DEFAULT_SAVE=Path(__file__).resolve().with_name('persona3-save.json')
VERSION=1
START=date(2009,4,6)
AWAKENING=date(2009,4,9)
TUTORIAL=date(2009,4,20)
MOON=date(2009,5,9)
END=date(2009,5,10)
PHASES=('arrival','awakening','tartarus','calendar','monorail','complete')
PERSONAS=('Orpheus','Pixie','Angel','Nekomata',"Jack O'Lantern",'Apsaras')
FUSIONS=(
    ('Nekomata',('Orpheus','Pixie'),110),
    ('Apsaras',('Pixie','Angel'),130),
    ("Jack O'Lantern",('Pixie','Nekomata'),145),
)


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


def _encode(state):
    data=asdict(state)
    data['day']=state.day.isoformat()
    return (json.dumps({'game':'persona-3-terminal','version':VERSION,'state':data},
                       ensure_ascii=False,indent=2)+'\n').encode()


def _decode(raw):
    data=json.loads(raw)
    if (not isinstance(data,dict) or data.get('game')!='persona-3-terminal'
            or type(data.get('version')) is not int or data['version']!=VERSION
            or set(data)!={'game','version','state'}):
        raise P3SaveError('Not a Persona 3 field save.')
    body=data['state']
    if not isinstance(body,dict) or set(body)!=set(FieldRecord.__dataclass_fields__):
        raise P3SaveError('The field record is incomplete.')
    if not isinstance(body.get('masks'),list):raise P3SaveError('Invalid Persona stock.')
    body={**body,'day':date.fromisoformat(body['day']),'masks':tuple(body['masks'])}
    state=FieldRecord(**body)
    if state.phase not in PHASES or state.activity not in ('','library','track','lounge'):
        raise P3SaveError('Invalid field flags.')
    exact={'arrival':START,'awakening':AWAKENING,'tartarus':TUTORIAL,'monorail':MOON,'complete':END}
    if (state.phase in exact and state.day!=exact[state.phase] or
            state.phase=='calendar' and not TUTORIAL<state.day<MOON or
            state.activity and state.phase!='calendar'):
        raise P3SaveError('Invalid calendar position.')
    for field,cap in (('depth',5),('yen',999999),('aid',99),('academics',99),('charm',99),('courage',99)):
        n=getattr(state,field)
        if type(n) is not int or not 0<=n<=cap:raise P3SaveError('Invalid '+field+'.')
    if (not state.masks or any(m not in PERSONAS for m in state.masks)
            or len(set(state.masks))!=len(state.masks) or state.equipped not in state.masks):
        raise P3SaveError('Invalid Persona stock.')
    return state


class P3Store:
    def __init__(self,path=DEFAULT_SAVE):
        self.path=Path(path)
        self.reload()

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
        return self._write(replace(self.state,**changes))

    def advance_night(self,skip=False):
        s=self.state
        if s.phase not in ('tartarus','calendar'):raise P3SaveError('No night to advance.')
        if skip and s.depth<5:raise P3SaveError('Thebel report still open.')
        day=MOON if skip else s.day+timedelta(days=1)
        return self.commit(day=day,phase='monorail' if day==MOON else 'calendar',activity='')

    def activity(self,kind):
        s=self.state
        if s.phase!='calendar' or s.activity:
            raise P3SaveError('Today’s time slot is already used.')
        updates={
            'library':{'academics':min(99,s.academics+1),'yen':min(999999,s.yen+40)},
            'track':{'courage':min(99,s.courage+1),'aid':min(99,s.aid+1)},
            'lounge':{'charm':min(99,s.charm+1)},
        }
        if kind not in updates:raise P3SaveError('Unknown activity.')
        return self.commit(activity=kind,**updates[kind])

    def fusion_preview(self,result):
        s=self.state
        recipe=next((r for r in FUSIONS if r[0]==result),None)
        if recipe is None:raise P3SaveError('Unknown fusion recipe.')
        _,parents,cost=recipe
        missing=tuple(n for n in parents if n not in s.masks)
        registered=result in s.masks
        balance=s.yen-cost
        return FusionPreview(result,parents,cost,missing,registered,balance)

    def fuse(self,result):
        check=self.fusion_preview(result)
        if not check.ready:raise P3SaveError(check.reason)
        return self.commit(masks=(*self.state.masks,result),yen=check.balance)


@dataclass(frozen=True)
class FusionPreview:
    result: str
    parents: tuple[str,...]
    cost: int
    missing: tuple[str,...]
    registered: bool
    balance: int

    @property
    def ready(self):
        return not self.registered and not self.missing and self.balance>=0

    @property
    def status(self):
        if self.registered:return 'REGISTERED'
        if self.missing:return 'MISSING PARENTS'
        if self.balance<0:return f'NEED ¥{-self.balance} MORE'
        return 'READY'

    @property
    def reason(self):
        if self.registered:return 'No new fusion to register.'
        if self.missing:return 'Register '+', '.join(self.missing)+' first.'
        if self.balance<0:return f'Need ¥{-self.balance} more.'
        return ''
