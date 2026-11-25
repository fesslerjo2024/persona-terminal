"""Original terminal adaptation of Royal's Qliphoth finale.

Source evidence: English Royal gameplay recorded at
https://www.youtube.com/watch?v=iiIddrIYekE (arm and sin order),
https://www.youtube.com/watch?v=gyk5nw5C0Q4 (1:08 Grail, 13:34 body, 56:59 Satanael).
Royal extracted script references: battle/event/script/0313.bf, 0314.bf, 0311.bf.
Numbers, action economy, sin effects, and recovery are condensed adaptations.
The earlier scripted defeat in the Depths is intentionally unaffected.
"""
from battle_data import SKILLS, shadow

GRAIL = 'depths-grail-unbound'
BODY = 'depths-yaldabaoth'
ARM = 'depths-yaldabaoth-arm'
ARM_NAMES = ('Gun of Execution','Bell of Declaration','Sword of Conviction',
             'Book of Commandments')
# The source boss has special ailments, not these simulator affinity/HP values.
ENEMY_ADDITIONS = {
    'Holy Grail Unbound': shadow(565,80,[],{},GRAIL,no_knockdown=True),
    'Yaldabaoth': shadow(880,80,[],{},BODY,no_knockdown=True),
    **{name:shadow(hp,0,[],{},ARM,no_knockdown=True)
       for name,hp in zip(ARM_NAMES,(86,94,100,112))},
}
DEPTHS_FINAL_WAVES = [['Holy Grail Unbound'],['Yaldabaoth',*ARM_NAMES]]

def _enemy(b,behavior):
    return next((u for u in b.enemies if u.behavior==behavior),None)

def _live(b):
    return [u for u in b.allies if u.alive]

def _target(b,element='Almighty'):
    return min(_live(b),key=lambda u:u.hp/u.max_hp + .55*u.guard +
               (.9 if u.affinity.get(element) in ('null','drain','repel') else 0))

def _attack(b,a,name,power,element='Almighty',*,group=False,**extra):
    b._execute(a,dict(kind='damage',power=power,element=element,accuracy=100,
                      crit=0,target='enemies' if group else 'enemy',**extra),
               None if group else _target(b,element),name)
    # The scripted sequence never chains an extra AI action.
    return False

def _restore(u,hp):
    u.hp=hp;u.guard=False;u.down=False;u.status='';u.status_turns=0
    u.buffs.clear()

def on_spawn(b):
    """Call once after the wave roster, initiatives and boss state are built."""
    st=b._boss_state
    if _enemy(b,GRAIL):
        st.update(lines_open=False,lines_cut=False,grail_turn=0)
        b._say('The Grail feeds on the prisoners. Watch for a chance to sever its lines.')
    if _enemy(b,BODY):
        arms={u.name:u for u in b.enemies if u.behavior==ARM}
        # Slots are already in the turn order; no spawn, clone, or reroll later.
        for arm in arms.values(): arm.hp=0
        st.update(arms=arms,manifested=set(),revived=False,body_turn=0)
        b._say('Yaldabaoth will manifest separate arms. Suppress them to weaken Divine Apex.')

def hidden_enemies(b):
    st=b._boss_state
    manifested=st.get('manifested',())
    return tuple(u for name,u in st.get('arms',{}).items() if name not in manifested)

def before_state(b):
    """Call after Joker loss check and before ordinary wave/victory checks."""
    st=b._boss_state
    grail=_enemy(b,GRAIL)
    if grail is not None and not grail.alive and not st.get('lines_cut'):
        _restore(grail,max(1,grail.max_hp//4))
        st['lines_open']=True
        b._say('Will of the People restores the Grail. Sever the supply lines.')
    body=_enemy(b,BODY)
    if body is None or body.alive or st.get('finished'): return
    _restore(body,1)
    if st.get('finisher_ready'):return
    st['finisher_ready']=True
    st.pop('apex_round',None); st.pop('return_round',None)
    for arm in st.get('arms',{}).values(): arm.hp=0
    b._say('Rays of Control strikes. The public rallies, and Joker calls Satanael.')
    b._say('Use Sinful Shell to end the fight.')

def intent(b):
    st=b._boss_state
    if _enemy(b,GRAIL):
        if st.get('lines_cut'): return 'LINES CUT / The Grail is vulnerable.'
        if st.get('lines_open'): return '9: Cut Supply Lines to stop the healing.'
        return 'WILL OF THE PEOPLE / Healing lines intact.'
    if not _enemy(b,BODY): return ''
    if st.get('finisher_ready'): return 'SATANAEL / Joker can fire Sinful Shell.'
    if 'apex_round' in st: return 'DIVINE APEX / Suppress arms or Guard.'
    if 'return_round' in st: return 'ARM RETURN / One revival only.'
    n=sum(u.alive for u in st.get('arms',{}).values())
    return f'GOD OF CONTROL / {n} active arms.'

def block_hit(b,target,skill):
    if target.behavior==BODY and b._boss_state.get('finisher_ready'):
        b._say('The final opening belongs to Satanael. Use Sinful Shell.')
        return True
    return False

def special(b):
    if b.phase!='turn' or b.actor is None or b.actor.enemy:return None
    st=b._boss_state
    if _enemy(b,GRAIL) and st.get('lines_open') and not st.get('lines_cut'):
        return ('story-special','Cut Supply Lines','Trade this action to end the Grail’s healing.')
    if (b.actor is b.allies[0] and _enemy(b,BODY) and st.get('finisher_ready')
            and not st.get('finished')):
        return ('story-special','Sinful Shell','Satanael ends the fight.')
    return None

def use_special(b):
    row=special(b)
    if not row:return 'This special action is not available.'
    st=b._boss_state
    if row[1]=='Cut Supply Lines':
        st['lines_cut']=True
        b._say('The Thieves cut the supply lines. Will of the People can no longer heal the Grail.')
    else:
        st['finisher_ready']=False;st['finished']=True
        body=_enemy(b,BODY)
        b._hurt(body,body.hp)
        b._say('Satanael fires Sinful Shell. Yaldabaoth falls.')
    b._state()
    if b.phase=='turn':b._advance()
    return None

def _manifest(b,arm):
    _restore(arm,arm.max_hp)
    b._boss_state['manifested'].add(arm.name)
    b._say(f'{arm.name} manifests. Target it directly to suppress it.')

def on_round(b):
    st=b._boss_state
    if st.get('return_round',b.round+1)>b.round: return
    st.pop('return_round')
    arm=st.pop('return_arm')
    if not st.get('finisher_ready') and not arm.alive:
        _restore(arm,max(1,arm.max_hp//2))
        st.setdefault('arm_born',{})[arm.name]=b.round
        b._say(f'{arm.name} re-forms at half HP. This revival will not repeat.')

def _arm_step(b,a):
    st=b._boss_state
    if st.get('finisher_ready') or st.get('arm_born',{}).get(a.name)==b.round:
        return False
    # Stagger attacks: each arm acts on alternate rounds, with at most two
    # attacking together. Suppressed arms simply lose their existing turn slot.
    ix=ARM_NAMES.index(a.name)
    if (b.round+ix)%2:return False
    alternate=bool(st.setdefault('arm_turns',{}).get(a.name,0)%2)
    st['arm_turns'][a.name]=st['arm_turns'].get(a.name,0)+1
    if ix==0:
        return _attack(b,a,'Distorted Avarice',21,'Gun') if alternate else _attack(
            b,a,'Distorted Lust',19,'Gun',status='dizzy',chance=26)
    if ix==1:
        name='Distorted Envy' if alternate else 'Distorted Vanity'
        b._execute(a,SKILLS['Tarunda' if alternate else 'Rakunda'],_target(b),name)
    elif ix==2:
        target=_target(b)
        loss=min(target.sp,4 if not target.guard else 1)
        target.sp-=loss
        b._say(f'Distorted Gluttony drains {loss} SP from {target.name}.')
    elif alternate:
        b._execute(a,SKILLS['Rakukaja'],_enemy(b,BODY),'Distorted Pride')
    else:
        target=_target(b)
        b._execute(a,SKILLS['Tarukaja'],target,'Distorted Wrath')
        b._execute(a,SKILLS['Rakunda'],target,'Distorted Wrath')
    return False

def enemy_step(b,a):
    st=b._boss_state
    if a.behavior==GRAIL:
        st['grail_turn']+=1
        if not st['lines_open']:
            st['lines_open']=True
            b._say('Oracle spots a route to the Grail’s supply lines. Use the special action.')
        if not st.get('lines_cut') and a.hp*5<a.max_hp*4:
            before=a.hp;a.hp=min(a.max_hp,a.hp+85)
            b._say(f'Will of the People restores {a.hp-before} HP to the Grail.')
            return False
        return _attack(b,a,'Arrow of Light',34) if st['grail_turn']%2 else _attack(
            b,a,'Eternal Light',26,group=True)
    if a.behavior==ARM:return _arm_step(b,a)
    if a.behavior!=BODY:return None
    if st.get('finisher_ready'):return False
    st['body_turn']+=1
    if 'apex_round' in st:
        if b.round<st['apex_round']:return False
        del st['apex_round']
        n=sum(u.alive for u in st['arms'].values())
        return _attack(b,a,'Rays of Control',36+9*n,group=True)
    # The stable story initiative plus a round boundary gives every living
    # player slot a turn between the tell and the release. No sleep deadlock.
    if a.hp*5<=a.max_hp*3 and not st.get('apex_spent'):
        st.update(apex_round=b.round+1,apex_spent=True)
        b._say('Divine Apex charges. Destroy arms to weaken it, or Guard.')
        return False
    for name in ARM_NAMES:
        if name in st['arms'] and name not in st['manifested']:
            _manifest(b,st['arms'][name])
            st.setdefault('arm_born',{})[name]=b.round
            if st['body_turn']>1:return _attack(b,a,'Control Pulse',25)
            return False
    fallen=[st['arms'][n] for n in ARM_NAMES if n in st['manifested'] and not st['arms'][n].alive]
    if fallen and not st.get('revived'):
        st.update(revived=True,return_arm=fallen[0],return_round=b.round+1)
        b._say(f'{fallen[0].name} will re-form next round at half HP, once.')
        return False
    return _attack(b,a,'Arrow of Control',38) if st['body_turn']%2 else _attack(
        b,a,'Control Pulse',27,group=True)
