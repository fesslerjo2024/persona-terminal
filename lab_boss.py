"""Playable adaptation of the final laboratory battle.

Source: Persona 5 Royal English battle scripts 0358, 0359 and 0367
(https://mysh.dev/tools/persona/5r/files/dataR.cpk/battle/event/script).
Recorded gameplay: https://www.youtube.com/watch?v=_nkVqd-q5MU (5:02:09
through 5:34:49). The terminal combines Maruki/Azathoth into one target,
uses one affinity rotation and one partial regrowth coupled to the first
Tyrant Stance, and converts the
fused Adam Kadmon cutscene into a coordinated Guard and Joker command.
Command bans and the human fistfight are not simulated.
"""
from battle_data import SKILLS, shadow

AZATHOTH = 'lab-azathoth'
PROTECTION = 'lab-protection'
ASSISTANCE = 'lab-assistance'
HEALING = 'lab-healing'
KADMON = 'lab-kadmon'
FUSED = 'lab-fused'
TENDRILS = (PROTECTION, ASSISTANCE, HEALING)
AFFINITIES = (
    {'Physical': 'weak', 'Gun': 'weak', 'Fire': 'resist', 'Wind': 'resist',
     'Bless': 'resist', 'Nuclear': 'resist'},
    {'Fire': 'weak', 'Ice': 'weak', 'Electric': 'weak', 'Wind': 'weak',
     'Physical': 'resist', 'Gun': 'resist'},
    {'Psy': 'weak', 'Nuclear': 'weak', 'Bless': 'weak', 'Curse': 'weak',
     'Physical': 'resist', 'Gun': 'resist'},
)

WAVES = (
    ('Tentacle of Protection', 'Tentacle of Assistance', 'Tentacle of Healing', 'Maruki Azathoth'),
    ('Maruki with Adam Kadmon',),
    ('Adam Kadmon',),
)

ENEMY_ADDITIONS = {
    'Tentacle of Protection': shadow(62, 0, [], AFFINITIES[0], PROTECTION),
    'Tentacle of Assistance': shadow(58, 0, [], AFFINITIES[1], ASSISTANCE),
    'Tentacle of Healing': shadow(58, 0, [], AFFINITIES[2], HEALING),
    'Maruki Azathoth': shadow(345, 100, [], {}, AZATHOTH, no_knockdown=True),
    'Maruki with Adam Kadmon': shadow(240, 100, [], {}, KADMON, no_knockdown=True),
    'Adam Kadmon': shadow(100, 100, [], {}, FUSED, no_knockdown=True),
}


def _active(b, behavior):
    return next((u for u in b.enemies if u.alive and u.behavior == behavior), None)


def _living(b):
    return [u for u in b.allies if u.alive]


def _protection(b):
    u = _active(b, PROTECTION)
    return u if u and not u.down and u.status not in ('sleep', 'freeze') else None


def _sweep(b, a, name, element, power):
    b._execute(a, dict(kind='damage', element=element, power=power,
                       target='enemies', accuracy=100, crit=0), None, name)
    return False  # Named boss moves never take a second automatic action.


def on_spawn(b):
    if _active(b, AZATHOTH):
        b._say('ORACLE / Three readings on Azathoth. The front tendril blocks attacks on the core.')
    elif _active(b, KADMON):
        b._say('Maruki seizes the Treasure and calls forth Adam Kadmon.')
    elif _active(b, FUSED):
        b._say('Maruki fuses with Adam Kadmon. Oracle searches for a way through its armor.')
        # The scripted defense encounter must not inherit turn-denial ailments.
        for u in _living(b):
            u.status = ''
            u.status_turns = 0


def before_state(b):
    """Clear surviving tendrils once their core falls, including on a group KO."""
    core = next((u for u in b.enemies if u.behavior == AZATHOTH), None)
    if core is None or core.alive:
        return
    attached = [u for u in b.enemies if u.alive and u.behavior in TENDRILS]
    if attached:
        for u in attached:
            b._hurt(u, u.hp)
        b._say('With Azathoth broken, the remaining tendrils collapse.')


def block_hit(b, target, skill):
    if target.behavior == AZATHOTH and _protection(b):
        b._say('The Tentacle of Protection shields Azathoth. Knock it down or sever it.')
        return True
    if target.behavior == FUSED:
        b._say('Adam Kadmon’s fused armor repels the blow. Follow Oracle’s lead.')
        return True
    return False


def intent(b):
    if _active(b, FUSED):
        if b._boss_state.get('lab_finish'):
            return 'OPENING / Joker: 9 Take the Shot.'
        if b._boss_state.get('lab_pending'):
            live = _living(b)
            guarding = sum(u.guard for u in live)
            return f'FULL FORCE / Guard every standing ally ({guarding}/{len(live)}).'
        return 'ADAM KADMON / Wait for Oracle’s opening.'
    if _active(b, AZATHOTH):
        if b._boss_state.get('lab_charge'):
            return 'TYRANT STANCE / Guard before Tyrant Chaos.'
        return ('SHIELD TENDRIL / Topple or sever the protector.' if _protection(b) else
                'AZATHOTH EXPOSED / Hit the core.')
    if _active(b, KADMON):
        return 'ADAM KADMON / Keep Maruki from recovering.'
    return ''


def special(b):
    if (b.phase == 'turn' and b.actor is b.allies[0] and b.actor.alive
            and b._boss_state.get('lab_finish') and _active(b, FUSED)):
        return ('story-special', 'Take the Shot',
                'The others hold off Full Force. Grapple up and strike the mask.')
    return None


def use_special(b):
    if special(b) is None:
        return 'Joker needs the team to hold Adam Kadmon in place first.'
    boss = _active(b, FUSED)
    b._say('The Thieves hold back the fist with their Personas.')
    b._say('Joker grapples to Adam Kadmon’s head and fires. Maruki’s mask shatters.')
    b._hurt(boss, boss.hp)
    if not b._state() or b.phase == 'turn':
        b._advance()
    return None


def _can_respond(u):
    return (u.alive and u.status not in ('sleep', 'freeze')
            and not (u.status == 'burn' and u.hp <= max(1, u.max_hp // 12)))


def _arm_tyrant(b):
    st = b._boss_state
    st['lab_charge'] = True
    # The engine discards these from pending as their playable slots begin.
    # Keep the warning active through an initiative change or a skipped turn.
    st['pending'] = {u for u in b.allies if _can_respond(u)}
    b._say('Azathoth assumes Tyrant Stance. ORACLE / Guard before Tyrant Chaos!')


def _azathoth(b, a):
    st = b._boss_state
    count = st['lab_azathoth_turn'] = st.get('lab_azathoth_turn', 0) + 1
    arms = [u for u in b.enemies if u.behavior in TENDRILS]
    if st.get('lab_charge'):
        if any(_can_respond(u) for u in st['pending']):
            return False
        del st['lab_charge']
        del st['pending']
        st['lab_repeat_at'] = count + 3  # Two ordinary actions before another Stance.
        return _sweep(b, a, 'Tyrant Chaos', 'Almighty', 42)
    # Keep this finite: one reinforcement and one reshuffle, not an
    # indefinitely healing boss if the party has little elemental coverage.
    if not st.get('lab_shift') and a.hp * 3 <= a.max_hp * 2:
        st['lab_shift'] = True
        revived = []
        for u in arms:
            u.affinity = dict(AFFINITIES[(TENDRILS.index(u.behavior) + 1) % len(TENDRILS)])
            b.seen.pop(u.name, None)
            if not u.alive:
                u.hp = max(1, u.max_hp // 2)
                u.down = u.guard = False
                u.status = ''
                u.status_turns = 0
                u.buffs.clear()
                revived.append(u.name)
        b._say('ORACLE / The tendril signatures just changed. Previous affinity readings are stale.')
        if revived:
            b._say('Azathoth regrows severed tendrils once.')
        _arm_tyrant(b)
        return False
    if st.get('lab_repeat_at', count + 1) <= count:
        _arm_tyrant(b)
        return False
    return _sweep(b, a, 'Neuro Slash', 'Physical', 23)


def _fused(b):
    st = b._boss_state
    if st.get('lab_finish'):
        return False  # The team is holding the fist until Joker acts.
    if not st.get('lab_pending'):
        st['lab_pending'] = True
        b._say('ORACLE / Full Force incoming. Everybody Guard so we can hold that fist!')
        return False
    live = _living(b)
    caught = all(u.guard for u in live)
    for u in live:
        damage = min(u.hp - 1, 11 if u.guard else 38)
        if damage > 0:
            b._hurt(u, damage)
            b._say(f'{u.name}: {damage} from Full Force' + (' [GUARD].' if u.guard else '.'))
    if caught:
        st['lab_finish'] = True
        st.pop('lab_pending', None)
        b._say('ORACLE / That’s it! Keep him pinned; Joker, Take the Shot [9].')
    else:
        # A botched defense cannot end this scripted wave. The next
        # scheduled cycle is a fresh chance to coordinate the whole squad.
        b._say('The defense scatters. Full Force is winding up again. Everyone Guard.')
    return False


def enemy_step(b, a):
    role = a.behavior
    if role == AZATHOTH:
        return _azathoth(b, a)
    if role == PROTECTION:
        return False  # Its cover is applied in block_hit, not a wasted turn log.
    if role == ASSISTANCE:
        core = _active(b, AZATHOTH)
        if core and core.buffs.get('attack', (0, 0))[0] < 1:
            b._execute(a, SKILLS['Tarukaja'], core, 'Tarukaja')
        elif core:
            target = max(_living(b), key=lambda u: u.hp)
            if target.buffs.get('defense', (0, 0))[0] >= 0:
                b._execute(a, SKILLS['Rakunda'], target, 'Rakunda')
        return False
    if role == HEALING:
        core = _active(b, AZATHOTH)
        if core and core.max_hp - core.hp >= 16:
            b._execute(a, dict(SKILLS['Dia'], power=21), core, 'Healing Tendril')
        return False
    if role == KADMON:
        if b.round % 3 == 0 and a.hp < a.max_hp * .55:
            restored = min(28, a.max_hp - a.hp)
            for u in _living(b):
                u.sp = max(0, u.sp - 3)
            a.hp += restored
            b._say(f'Maruki drains the squad’s SP and recovers {restored} HP.')
            return False
        return _sweep(b, a, 'Adam Kadmon’s sweep', 'Almighty', 34)
    if role == FUSED:
        return _fused(b)
    return None
