"""Story-only adaptations of signature mechanics from Persona 5 Royal."""
from functools import lru_cache
from importlib import import_module
from importlib.util import find_spec

from .battle_data import SKILLS

_EXTENSIONS = ('sae_boss', 'depths_boss', 'lab_boss', 'solo_duel')


@lru_cache(maxsize=None)
def _extension(name):
    module = f'{__package__}.{name}'
    return import_module(module) if find_spec(module) is not None else None


def _hooks(name):
    for extension in _EXTENSIONS:
        module = _extension(extension)
        hook = getattr(module, name, None)
        if hook is not None:
            yield hook


def on_spawn(b):
    for hook in _hooks('on_spawn'):
        hook(b)


def hidden_enemies(b):
    return {u for hook in _hooks('hidden_enemies') for u in hook(b)}


def before_state(b):
    for hook in _hooks('before_state'):
        hook(b)


def action_block(b, action, skill=None):
    for hook in _hooks('action_block'):
        reason = hook(b, action, skill)
        if reason:
            return reason
    return None

def _living(units):
    return [u for u in units if u.alive]

def _active(battle, behavior):
    return next((u for u in battle.enemies if u.alive and u.behavior==behavior),None)

def _push(b,a,action,element,power,*,group=False):
    target=None if group else min(_living(b.allies),key=lambda u:u.hp/u.max_hp+.45*u.guard-.2*(u.status=='sleep'))
    return b._execute(a,dict(kind='damage',element=element,power=power,
                            target='enemies' if group else 'enemy',accuracy=100,crit=0),
                      target,action)

def _charge(b,text):
    b._boss_state['pending']=set(_living(b.allies))
    b._say(text)

def _finish_charge(b,actor,name,element,power):
    pending=b._boss_state.get('pending')
    if pending is None:return None
    if any(u.alive for u in pending):return False
    del b._boss_state['pending']
    _push(b,actor,name,element,power,group=True)
    return False

def _cover(b,target):
    if target.behavior!='bank-kaneshiro':return None
    bodyguard=_active(b,'bank-bodyguard')
    return bodyguard if bodyguard and not bodyguard.down and bodyguard.status not in ('sleep','freeze') else None

def intercept(b,target,skill):
    bodyguard=_cover(b,target)
    if bodyguard:
        b._say(f'{bodyguard.name} intercepts the hit.')
        return bodyguard
    return target

def target_block(b,target,skill):
    if (target.behavior=='pyramid-wakaba' and not b._boss_state.get('grounded')
            and skill['kind']=='damage' and skill.get('element')=='Physical'):
        return 'Wakaba is airborne. Use magic or Gun.'
    return None

def block_hit(b,target,skill):
    if any(hook(b,target,skill) for hook in _hooks('block_hit')):return True
    reason=target_block(b,target,skill)
    if reason:
        b._say(reason)
        return True
    if target.behavior=='bank-kaneshiro' and _cover(b,target):
        b._say('The bodyguard shields Kaneshiro from the group attack.')
        return True
    return False

def intent(b):
    for hook in _hooks('intent'):
        result=hook(b)
        if result:return result
    st=b._boss_state
    if _active(b,'castle-king') and 'pending' in st:return 'ROYAL SMASH incoming. Guard before the swing.'
    if _active(b,'bank-piggytron'):
        if 'pending' in st:return 'MARCH OF THE PIGGY: Guard'+(' or 9: offer bait.' if special(b) else '.')
        return 'PIGGYTRON  /  Watch for Super VIP Form.'
    if _active(b,'bank-kaneshiro'):
        return 'HIRED GUARDS  /  Disable the Bodyguard to expose Kaneshiro.' if _active(b,'bank-bodyguard') else 'MAKE IT RAIN  /  Heal before the follow-up.'
    if _active(b,'pyramid-wakaba'):
        if 'pending' in st:return 'SPHINX DIVE incoming. Guard before impact.'
        if special(b):return 'BALLISTA READY  /  Press 9 to ground Wakaba.'
        return 'WAKABA GROUNDED  /  Take the opening.' if st.get('grounded') else 'WAKABA AIRBORNE  /  Magic or Gun. Melee won’t reach.'
    if _active(b,'space-worker'):
        return 'SHIFT CLOCK  /  '+('Reissue spent. Finish this squad.' if st.get('reissued') else f"Clear by end of round {st.get('due',_shift_deadline(b))-1}.")
    if _active(b,'space-exec'):
        return 'BIG BANG CHALLENGE incoming. Guard.' if 'pending' in st else 'EXECUTIVE DIRECTOR  /  Watch the charge.'
    if _active(b,'space-cognitive'):
        return 'SELF-DESTRUCT armed. Stop it or Guard.' if 'pending' in st else 'COGNITIVE HARU  /  Watch for Okumura’s order.'
    if _active(b,'casino-snake') and 'pending' in st:return 'CONCENTRATE → MAZIONGA incoming. Guard before the shock.'
    return ''

def special(b):
    st=b._boss_state
    if b.phase!='turn':return None
    for hook in _hooks('special'):
        result=hook(b)
        if result:return result
    if _active(b,'bank-piggytron') and 'pending' in st and not st.get('bait') and b.items.get('Medicine',0):
        return ('story-special','Bait Piggytron','Sacrifice one Medicine and cancel the charge (once).')
    if _active(b,'pyramid-wakaba') and st.get('ready'):
        return ('story-special','Fire Ballista','Ground the sphinx to create a damage window.')
    return None

def use_special(b):
    for extension in _EXTENSIONS:
        module=_extension(extension)
        hook=getattr(module,'special',None)
        if hook is not None and hook(b):return module.use_special(b)
    row=special(b)
    if row is None:return 'This special action is not available.'
    st=b._boss_state
    if row[1]=='Bait Piggytron':
        st.pop('pending');st['bait']=True
        b.items['Medicine']-=1
        b._say('The Medicine distracts Piggytron. The charge stops.')
    else:
        st['grounded']=3;st['ready']=False;st['ballista_fired']=True
        u=_active(b,'pyramid-wakaba')
        b._hurt(u,min(90,u.hp))
        b._say('The ballista hits. Wakaba is grounded!')
    if b._state() and b.phase!='turn':return None
    b._advance()
    return None

def _shift_deadline(b):
    durations=b.config.get('spaceport_clock',())
    return 1+durations[b.wave-1] if b.wave<=len(durations) else 4

def on_round(b):
    for hook in _hooks('on_round'):
        hook(b)
    st=b._boss_state
    if _active(b,'space-worker') and not st.get('reissued') and b.round>=st.get('due',_shift_deadline(b)):
        for u in b.enemies:
            u.hp=u.max_hp;u.down=False;u.status='';u.status_turns=0
        st['reissued']=True
        b._say('The production line reissues this squad. No further reissues for this rank.')
    if _active(b,'pyramid-wakaba') and not st.get('ballista_fired') and b.round>=3:
        if not st.get('ready'):b._say('Futaba awakens Necronomicon and rigs a ballista.')
        st['ready']=True
    if 'support' in b.config.get('oracle_features',()) and not b._support_used:
        injured=[u for u in _living(b.allies) if u.hp*2<u.max_hp]
        if injured:
            b._support_used=True
            for u in _living(b.allies):
                u.hp=min(u.max_hp,u.hp+24);u.sp=min(u.max_sp,u.sp+5)
            b._say('ORACLE / MORAL SUPPORT: the squad recovers HP and SP.')

def enemy_step(b,a):
    for hook in _hooks('enemy_step'):
        result=hook(b,a)
        if result is not None:return result
    behavior=a.behavior;st=b._boss_state
    if behavior=='castle-trophy':
        king=_active(b,'castle-king')
        if king and king.hp<king.max_hp*.8:
            king.hp=min(king.max_hp,king.hp+22);b._say('The Trophy heals Kamoshida.')
        return False
    if behavior=='castle-king':
        done=_finish_charge(b,a,'Royal Smash','Almighty',49)
        if done is not None:return done
        st['king_turn']=st.get('king_turn',0)+1
        if a.hp*3<a.max_hp*2 and st['king_turn']%2==0:
            _charge(b,'The King winds up Royal Smash.');return False
        return _push(b,a,'King’s Strike','Physical',32)
    if behavior=='bank-piggytron':
        done=_finish_charge(b,a,'March of the Piggy','Physical',60)
        if done is not None:return done
        st['pig_turn']=st.get('pig_turn',0)+1
        if st['pig_turn']%2==0:
            _charge(b,'Piggytron enters Super VIP Form.');return False
        return _push(b,a,'Missile Party','Fire',23,group=True)
    if behavior=='bank-kaneshiro':
        st['payments']=st.get('payments',3)
        if a.hp*2<=a.max_hp and st['payments']:
            for u in _living(b.allies):b._hurt(u,min(60,int(u.hp*(.24 if u.guard else .46))))
            st['payments']-=1
            b._say('Kaneshiro makes it rain. His bankroll shrinks.')
        elif b.round%2==0:
            st['payments']=max(0,st['payments']-1)
            _push(b,a,'Zionga','Electric',30)
        else:
            b._execute(a,dict(SKILLS['Lullaby'],chance=37),None,'Lullaby')
        if not st['payments']:
            for u in b.enemies:
                if u.alive and u.behavior in ('bank-bodyguard','bank-hitman'):
                    b._hurt(u,u.hp);b._say(f'{u.name} leaves when the cash runs out.')
        return False
    if behavior=='pyramid-wakaba':
        done=_finish_charge(b,a,'Sphinx Dive','Almighty',56)
        if done is not None:return done
        if st.get('grounded',0):
            st['grounded']-=1
            return _push(b,a,'Wing Strike','Physical',25)
        if b.round%3==2:
            _charge(b,'Wakaba climbs high. Guard for the dive.');return False
        return _push(b,a,'Wing Sweep','Wind',27,group=True)
    if behavior=='space-exec':
        done=_finish_charge(b,a,'Big Bang Challenge','Almighty',65)
        if done is not None:return done
        if b.round%3==2:
            _charge(b,'The Executive Director starts charging Big Bang Challenge.');return False
        return _push(b,a,'Executive Order','Physical',36)
    if behavior=='space-cognitive':
        done=_finish_charge(b,a,'Self-Destruct','Almighty',59)
        if done is not None:
            if 'pending' not in st:b._hurt(a,a.hp)
            return done
        _charge(b,'Okumura orders Cognitive Haru to self-destruct.');return False
    if behavior=='casino-snake':
        done=_finish_charge(b,a,'Charged Mazionga','Electric',63)
        if done is not None:return done
        st['snake_turn']=st.get('snake_turn',0)+1
        if a.hp*2<=a.max_hp and st['snake_turn']%3==0:
            _charge(b,'Snake King concentrates. Charged Mazionga is coming.');return False
        shocked=[u for u in _living(b.allies) if u.status=='shock']
        if shocked:
            target=min(shocked,key=lambda u:u.hp/u.max_hp+.45*u.guard)
            return b._execute(a,dict(kind='damage',element='Physical',power=29,
                                     target='enemy',accuracy=96),target,'Fang Strike')
        if a.sp>=16:
            a.sp-=16
            return b._execute(a,SKILLS['Mazionga'],None,'Mazionga')
        return _push(b,a,'Fang Strike','Physical',29)
    if behavior=='space-mammon':
        b._say('Okumura has no employees left to order around.')
        return False
    return None
