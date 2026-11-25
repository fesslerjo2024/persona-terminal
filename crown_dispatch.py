"""Optional Kamoshida set piece; the cover/hit and payoff timings are adapted."""

ACTION='crown-dispatch'
TITLE='Send Crown Runner [C]'
COVER_HITS=2
EXPOSED_HITS=3
EXPOSED_DAMAGE_MULTIPLIER=1.5


def _king(b):
    if b.story and b.config.get('id')=='throne-room':
        return next((u for u in b.enemies if u.behavior=='castle-king'),None)


def runners(b):
    king=_king(b)
    if (b.phase!='turn' or b.actor is None or b.actor.enemy or not king or not king.alive
            or b._boss_state.get('crown_used')):
        return []
    trophy=next((u for u in b.enemies if u.behavior=='castle-trophy'),None)
    if trophy is None or trophy.alive:
        return []
    return [u for u in b.combat_allies[1:] if u.alive and not u.down
            and u.status not in ('sleep','freeze','shock','fear','confuse')]


def command(b):
    return (ACTION,TITLE,'Spend this action to send one Thief. Land 2 hits on the King while they climb.') if runners(b) else None


def action_block(b,target,*,pick_target=False):
    eligible=runners(b)
    if not eligible:
        return 'Crown dispatch is not available.'
    if target not in eligible and not (pick_target and target is None):
        return 'Choose a standing teammate other than Joker.'


def use(b,target):
    reason=action_block(b,target)
    if reason:
        return reason
    st=b._boss_state
    st.update(crown_used=True,crown_runner=target,crown_hits=0)
    target.away=True
    if 'pending' in st:
        st['pending'].discard(target)
    b._say(f'{target.name} climbs for the crown. Land two hits on Kamoshida to cover them.')
    b._advance()


def intent(b):
    king=_king(b)
    if king is None or not king.alive:
        return ''
    st=b._boss_state
    if st.get('crown_runner') is not None:
        return f"CROWN RUN / Cover with hits on Kamoshida: {st['crown_hits']}/{COVER_HITS}."
    if st.get('crown_exposed',0):
        return f"CROWN STOLEN / Kamoshida exposed: {st['crown_exposed']} hits left."
    if runners(b):
        return 'TROPHY BROKEN / C: Send a runner or keep fighting.'
    return ''


def _return(b):
    runner=b._boss_state.pop('crown_runner',None)
    if runner is not None:
        runner.away=False
    return runner


def before_state(b):
    if b._boss_state.get('crown_runner') is None:
        return
    king=_king(b)
    if king is not None and not king.alive:
        runner=_return(b)
        b._say(f'{runner.name} returns as the King falls.')
    elif not b.allies[0].alive:
        runner=_return(b)
        b._say(f'{runner.name} retreats with the team.')


def damage_multiplier(b,actor,target):
    if (b._boss_state.get('crown_exposed',0) and not actor.enemy
            and target is _king(b)):
        return EXPOSED_DAMAGE_MULTIPLIER
    return 1


def hit(b,actor,target):
    if actor.enemy or target.behavior!='castle-king' or target is not _king(b):
        return
    st=b._boss_state
    if (runner:=st.get('crown_runner')) is not None:
        if not target.alive:
            return  # before_state brings the runner back for the result.
        st['crown_hits']+=1
        if st['crown_hits']==COVER_HITS:
            _return(b)
            st.pop('pending',None)
            st.update(crown_exposed=EXPOSED_HITS,crown_stagger=True)
            b._say(f'{runner.name} takes the crown and returns. Kamoshida staggers!')
    elif st.get('crown_exposed',0):
        st['crown_exposed']-=1
        if not st['crown_exposed'] and target.alive:
            b._say('Kamoshida steadies himself. The opening closes.')


def stagger(b):
    if b._boss_state.pop('crown_stagger',False):
        b._say('Kamoshida loses his action reeling from the theft.')
        return True
    return False
