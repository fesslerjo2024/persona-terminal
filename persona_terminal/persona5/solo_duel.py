"""The solo Shido fight's outward tells and fixed follow-up rules."""
from .battle_data import SKILLS

BEHAVIOR='cruiser-solo'
ELEMENTS=('Bufula','Agilao','Zionga','Garula')
AFFINITY_SCORE={'weak':4,'normal':2,'resist':1,'null':0,'repel':0,'drain':0}


def _strike(b,shido,joker,*,power=47,crit=8):
    skill=dict(SKILLS['Rising Slash'],power=power,hp=0,accuracy=96,crit=crit)
    return b._execute(shido,skill,joker,'Rising Slash')


def intent(b):
    if not any(u.alive and u.behavior==BEHAVIOR for u in b.enemies):
        return ''
    if b._boss_state.get('duel_open'):
        return 'SHIDO IS OPEN  /  Strike or recover before he gets his footing.'
    name=b._boss_state.get('duel_tell')
    if name:
        element=SKILLS[name]['element']
        return f'SHIDO READIES {element.upper()}  /  Switch masks or Guard.'
    return 'SHIDO WINDS UP  /  Physical attack next.'


def enemy_step(b,actor):
    if actor.behavior!=BEHAVIOR:
        return None
    joker=b.allies[0]
    st=b._boss_state
    # The enemy is allowed an honest One More after a real knockdown. It
    # must not follow a telegraphed spell with the same weakness spell again.
    slot=(b.round,b.cursor)
    if st.get('duel_used_slot')==slot:
        return _strike(b,actor,joker,power=28,crit=0)
    st['duel_used_slot']=slot
    next_move=st.pop('duel_tell',None)
    if not next_move:
        overextended=st.pop('duel_open',False)
        result=False if overextended else _strike(b,actor,joker,power=53 if 'duel_last_spell' not in st else 50)
        if joker.alive:
            options=(n for n in ELEMENTS if n!=st.get('duel_last_spell'))
            move=max(options,key=lambda n:(AFFINITY_SCORE[joker.affinity.get(SKILLS[n]['element'],'normal')],
                                           b.rng.random()))
            st['duel_tell']=move
            b._say(f"Shido readies a {SKILLS[move]['element']} spell.")
        return result
    st['duel_last_spell']=next_move
    s=dict(SKILLS[next_move],power=52,accuracy=96,chance=10)
    result=b._execute(actor,s,joker,next_move)
    if joker.alive and joker.guard and actor.alive:
        st['duel_open']=True
        if actor.buffs.get('defense',(0,0))[0]>=0:actor.buffs['defense']=(-1,1)
        b._say('Shido overextends into Joker’s guard. His defense falls.')
    return result
