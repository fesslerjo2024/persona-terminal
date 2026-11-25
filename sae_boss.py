"""Sae's wheel, adapted from English Royal battle dialogue 030A.

Royal's glass lids and sniper assignment are explicit. This compact version
uses the acting Thief for the shot, a brief fallback window, and a committed
element tell before the attack. Roulette never stakes real or wallet funds.
"""

SAE = 'casino-sae'
ELEMENTS = ('Fire', 'Ice', 'Electric', 'Wind', 'Psy', 'Nuclear')


def _sae(b):
    return next((u for u in b.enemies if u.alive and u.behavior == SAE), None)


def _live(b):
    return [u for u in b.allies if u.alive]


def _strike(b, actor, name, element, power):
    b._execute(actor, dict(kind='damage', element=element, power=power,
                           target='enemies', accuracy=100, crit=0), None, name)
    return False


def _block_before_open(b, action, skill):
    return (_sae(b) is not None and not b._boss_state.get('sae_open')
            and (action in ('attack', 'gun', 'showtime', 'allout') or
                 (skill and skill['target'] in ('enemy', 'enemies'))))


def action_block(b, action, skill=None):
    if _block_before_open(b, action, skill):
        return 'The rigged wheel protects Sae. Watch the spin and Guard.'
    return None


def block_hit(b, target, skill):
    if target.behavior != SAE:
        return False
    st = b._boss_state
    if not st.get('sae_open'):
        b._say('The rigged wheel protects Sae. Watch the first spin.')
        return True
    if st.get('sae_element') == skill.get('element'):
        b._say('The wheel blocks its current element. Change attacks.')
        return True
    return False


def intent(b):
    if not _sae(b):
        return ''
    st = b._boss_state
    if not st.get('sae_open'):
        if st.get('sae_clue'):
            return 'GLASS LID EXPOSED / Snipe it before the next spin.'
        return 'RIGGED ROULETTE / Guard and watch the pockets.'
    if st.get('sae_dance_round'):
        return 'BERSERKER DANCE incoming / Guard before impact.'
    if st.get('sae_final'):
        return 'ALMIGHTY WHEEL / Keep Joker standing.'
    if st.get('sae_element'):
        return f"ROULETTE: {st['sae_element'].upper()} / Guard exposed allies."
    return 'LEVIATHAN / The next spin will name an element.'


def special(b):
    st = b._boss_state
    if (_sae(b) and b.phase == 'turn' and b.actor is not None and not b.actor.enemy
            and st.get('sae_clue') and not st.get('sae_open')):
        return ('story-special', 'Snipe the Glass',
                'Assign the acting Thief to expose the rigged wheel.')
    return None


def use_special(b):
    if not special(b):
        return 'The glass is not exposed yet.'
    b._boss_state['sae_open'] = True
    b._say(f'{b.actor.name} shatters the glass. Sae sheds her disguise; Leviathan can be hit.')
    if b.phase == 'turn':
        b._advance()
    return None


def _arm_dance(b):
    # Story initiative is stable within this wave: one Sae slot later gives all
    # allies a response window, even if an ailment takes away a decision.
    b._boss_state['sae_dance_round'] = b.round + 1
    b._say('The Almighty wheel winds up Berserker Dance.')


def enemy_step(b, a):
    if a.behavior != SAE:
        return None
    st = b._boss_state
    if not st.get('sae_open'):
        if not st.get('sae_clue'):
            st['sae_clue'] = True
            b._say('Oracle: The ball struck a glass lid. Snipe the covered pocket!')
            return False
        st['sae_open'] = True
        b._say('Sae takes the wager and overturns the wheel. Leviathan can now be hit.')
        for u in _live(b):
            b._hurt(u, min(u.hp - 1, 6 if u.guard else 15))
        return False
    if st.get('sae_dance_round'):
        if b.round < st['sae_dance_round']:
            return False
        del st['sae_dance_round']
        return _strike(b, a, 'Berserker Dance', 'Almighty', 63)
    if a.hp * 2 <= a.max_hp:
        if not st.get('sae_final'):
            st['sae_final'] = True
            st.pop('sae_element', None)
            # Don't leave the previous wheel's learned/reported block in Analyze.
            b.seen.pop(a.name, None)
            _arm_dance(b)
            return False
        count = st['sae_close'] = st.get('sae_close', 0) + 1
        if count % 3 == 0:
            _arm_dance(b)
            return False
        return _strike(b, a, 'Brutal Impact', 'Gun', 28)
    if not st.get('sae_element') or st.get('sae_attacks', 0) >= 2:
        element = b.rng.choice(tuple(e for e in ELEMENTS if e != st.get('sae_element')))
        st.update(sae_element=element, sae_attacks=0)
        b._say(f'Roulette lands on {element}. Protect exposed allies and use another element.')
        return False
    st['sae_attacks'] += 1
    return _strike(b, a, 'Roulette Strike', st['sae_element'], 28)
