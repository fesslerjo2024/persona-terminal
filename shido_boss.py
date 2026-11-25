"""Royal-inspired Shido forms, built for the campaign's shorter combat rhythm.

Primary reference: Royal battle scripts 030E/030F/0310
https://mysh.dev/tools/persona/5r/files/dataR.cpk/battle/event/script
English Royal footage: https://www.youtube.com/watch?v=bvoNUeXQrZE
(Shido encounter and solo phase near the end). Affinities cross-checked at
https://velvet-run.com/games/persona-5-royal/encounters/shido .
Skill values, cadence, and the nonlethal alternative to instant defeat are local.
"""
from battle_data import SKILLS

ELEMENTS = ('Fire','Ice','Electric','Wind','Psy','Nuclear','Bless','Curse')
FORM_AFFINITIES = {
    'cruiser-beast': {'Physical':'repel','Gun':'repel'},
    'cruiser-wings': dict.fromkeys(ELEMENTS,'resist'),
    'cruiser-tomb': {'Gun':'resist'},
    'cruiser-samael': {},
    'cruiser-duel': {},
}
FORM_HP = dict(zip(FORM_AFFINITIES, (375,350,390,570,430)))
_HEAT_RISER = dict(kind='buff', target='self', stat='all')

_WING_SPELLS = (
    ('Agidyne','Fire'), ('Bufudyne','Ice'), ('Ziodyne','Electric'),
    ('Garudyne','Wind'), ('Psiodyne','Psy'), ('Freidyne','Nuclear'),
    ('Kougaon','Bless'), ('Eigaon','Curse'),
)
_DUEL_SPELLS = (
    ('Inferno','Fire'), ('Diamond Dust','Ice'), ('Thunder Reign','Electric'),
    ('Panta Rhei','Wind'),
)
_COACH = {
    'cruiser-beast':'BEAST  /  Read each hit. Brace when it draws back.',
    'cruiser-wings':'WINGS  /  Adapt if your spells lose force.',
    'cruiser-tomb':'TOMB  /  Heal before the cannon charges.',
    'cruiser-samael':'SAMAEL  /  Strip boosts. Heal before the next heavy hit.',
    'cruiser-duel':'FINAL DUEL  /  Read his next move. Switch masks.',
}


def _active(b):
    return next((u for u in b.enemies if u.alive and u.behavior in FORM_AFFINITIES),None)


def _install_profile(unit):
    if unit.behavior in FORM_AFFINITIES:
        unit.affinity.update(FORM_AFFINITIES[unit.behavior])


def prepare(b):
    """Install target affinities once as the engine spawns a Shido wave."""
    for unit in b.enemies:
        _install_profile(unit)


on_spawn = prepare


def block_hit(b, target, skill):
    """Equip the profile before a first hit even without a prepare() call.

    The existing strike path handles damage, reflection, discovery, etc.
    """
    _install_profile(target)
    return False


def intent(b):
    """Return the current cue without using RNG, advancing turns or changing state."""
    if b.phase != 'turn':
        return ''
    boss=_active(b)
    if boss is None:
        return ''
    charge=b._boss_state.get('shido_charge')
    if charge:
        name,element,_,_,target=charge
        if target and not target.alive:
            return f'{name.upper()} incoming. Heal or Guard before impact.'
        who=f' for {target.name}' if target and len(b.allies)>1 else ''
        elem=f' ({element})' if boss.behavior=='cruiser-duel' else ''
        # Let the move name and current target, not the foe's affinities, be known.
        return f'{name.upper()}{elem}{who} incoming. Guard or heal.'
    return _COACH[boss.behavior]


def _live(b):
    return [u for u in b.allies if u.alive]


def _target(b, *, exclude_joker=False):
    living=_live(b)
    if exclude_joker:
        teammates=[u for u in living if u.name!='Joker']
        if teammates:
            living=teammates
    return min(living,key=lambda u:u.hp/u.max_hp+.60*u.guard+.09*u.down,default=None)


def _hit(b,a,name,element,power,*,group=False,target=None,status=None):
    recipient=None if group else target if target is not None and target.alive else _target(b)
    if not group and recipient is None:
        return False
    spec=dict(kind='damage', element=element, power=power,
              target='enemies' if group else 'enemy', accuracy=100, crit=0)
    if status:
        spec.update(status=status,chance=17)
    b._execute(a,spec,recipient,name)
    # Scripted slots do not chain a second attack merely because a weakness was hit.
    return False


def _warn(b,name,element,power,*,group=False,target=None):
    st=b._boss_state
    st['shido_charge']=(name,element,power,group,target)
    st['pending']=set(_live(b))
    b._say(f'{name} is coming. Use the opening to heal or Guard.')
    return False


def _resolve(b,a):
    st=b._boss_state
    if 'shido_charge' not in st:
        return None
    name,element,power,group,target=st['shido_charge']
    if any(u.alive for u in st.get('pending',())):
        return False
    del st['shido_charge']
    st.pop('pending',None)
    # If a telegraphed ally fell, do not surprise an unannounced replacement.
    if not group and target is not None and not target.alive:
        b._say(f'{name} loses its target.')
        return False
    return _hit(b,a,name,element,power,group=group,target=target)


def _beast(b,a,turn):
    if turn%3==2:
        return _warn(b,'Beast King’s Wrath','Physical',53,group=True)
    if turn%3==0 and a.buffs and any(sign<0 for sign,_ in a.buffs.values()):
        b._execute(a,SKILLS['Dekunda'],None,'Dekunda')
        return False
    return _hit(b,a,'Arm of Destruction','Physical',32)


def _wings(b,a,turn):
    if turn%3==0:
        return _warn(b,'Royal Wing Beam','Almighty',50,group=True)
    name,element=_WING_SPELLS[(turn-1)%len(_WING_SPELLS)]
    return _hit(b,a,name,element,29)


def _tomb(b,a,turn):
    if turn%3==2:
        b._say('Unholy Convergence feeds the cannon.')
        return _warn(b,'Pyramid Blast','Almighty',61,group=True)
    return _hit(b,a,'Cannon Fire','Gun',36)


def _samael(b,a,turn):
    if turn%5==1:
        b._execute(a,_HEAT_RISER,None,'Heat Riser')
        return False
    if turn%5==2:
        return _hit(b,a,'Bloodbath','Physical',28,group=True,status='fear')
    if turn%5==3:
        target=_target(b,exclude_joker=True)
        if target and target.name!='Joker':
            return _warn(b,'Tyrant’s Purge','Physical',55,target=target)
        return _warn(b,'Megidolaon','Almighty',53,group=True)
    if turn%5==4 and any(sign>0 for u in _live(b) for sign,_ in u.buffs.values()):
        b._execute(a,SKILLS['Dekaja'],None,'Dekaja')
        return False
    return _hit(b,a,'Mapsiodyne','Psy',25,group=True)


def _duel(b,a,turn):
    joker=_target(b)
    if joker is None:
        return False
    st=b._boss_state
    pressing=a.hp*2<=a.max_hp
    if pressing and not st.get('shido_glare'):
        st['shido_glare']=True
        b._say('Shido fixes his gaze on Joker. The next opening will not last.')
    if turn%4==1:
        return _hit(b,a,'Tyrant’s Fist','Physical',29 if pressing else 26,target=joker)
    if turn%4==2:
        i=st.get('shido_element',0)
        st['shido_element']=i+1
        name,element=_DUEL_SPELLS[i%len(_DUEL_SPELLS)]
        return _warn(b,name,element,40 if pressing else 36,target=joker)
    if turn%4==3:
        b._execute(a,_HEAT_RISER,None,'Heat Riser')
        return False
    return _warn(b,'Tyrant’s Wave','Almighty',50 if pressing else 44,target=joker)


_FORMS = {'cruiser-beast':_beast,'cruiser-wings':_wings,'cruiser-tomb':_tomb,
          'cruiser-samael':_samael,'cruiser-duel':_duel}


def enemy_step(b,a):
    """Return None for unrelated encounters; otherwise take one scheduled slot."""
    custom=_FORMS.get(a.behavior)
    if custom is None:
        return None
    if not a.alive or not _live(b):
        return False
    _install_profile(a)
    charge_result=_resolve(b,a)
    if charge_result is not None:
        return charge_result
    st=b._boss_state
    turn=st['shido_turn']=st.get('shido_turn',0)+1
    return custom(b,a,turn)
