"""Original terminal cut-ins; no game artwork or dialogue is bundled."""

import wrestling_scene

ALL_OUT = {
    'Joker':   ('JOKER // CURTAIN CALL', 'The wildcard closes the case.'),
    'Mona':    ('MONA // NINE LIVES', 'Small silhouette. Very large problem.'),
    'Skull':   ('SKULL // THUNDER RUN', 'The last thing they hear is the thunder.'),
    'Panther': ('PANTHER // FLASH POINT', 'The runway goes up in flames.'),
    'Fox':     ('FOX // FINAL BRUSHSTROKE', 'One stroke cuts through the scenery.'),
    'Queen':   ('QUEEN // REDLINE', 'No brakes on the way to the verdict.'),
    'Noir':    ('NOIR // AFTERNOON FINALE', 'The tea can wait.'),
    'Crow':    ('CROW // CASE CLOSED', 'The detective leaves no loose ends.'),
    'Violet':  ('VIOLET // STICK THE LANDING', 'The last step is all precision.'),
}

SHOWTIMES = {
    frozenset(('Mona','Panther')): ('ROSE & REVOLVER', 'A bouquet makes a very good distraction.'),
    frozenset(('Skull','Queen')): ('HIGHWAY TO TROUBLE', 'Run the light. Flank on the left.'),
    frozenset(('Fox','Skull')): ('MIDNIGHT TAKEOUT', 'Dinner with a side of demolition.'),
    frozenset(('Fox','Panther')): ('THE DUEL AT DUSK', 'All eyes on the last shot.'),
    frozenset(('Noir','Mona')): ('TEA IN THE CROSSHAIRS', 'Service is finished.'),
    frozenset(('Queen','Noir')): ('PALACE BODY SLAM', 'The ring has one rule: stay down.'),
    frozenset(('Joker','Crow')): ('TWO SIDES OF THE MASK', 'Two rivals agree on one thing: the target.'),
    frozenset(('Joker','Violet')): ('THE LAST WALTZ', 'One perfect step. Two blades finish the dance.'),
}
ORACLE = ('ORACLE // UFO PAYLOAD', 'Necronomicon marks the drop zone.')

def all_out(actor, oracle_drop=False):
    return ORACLE if oracle_drop else ALL_OUT.get(actor,('ALL-OUT ATTACK','The squad moves as one.'))

def showtime(pair):
    return SHOWTIMES.get(frozenset(pair),('SHOWTIME','Two Thieves. One opening.'))

# These presentation assets do not grant, unlock, or alter battle effects.
ORACLE_SUPPORT = ('ORACLE // MORAL SUPPORT', 'Necronomicon relays a burst of HP and SP.')
FINAL_GUARD = ('ORACLE // FINAL GUARD', 'A last-second shield covers the squad.')
CUTIN_SECONDS = 1.22


def duration(title):
    return wrestling_scene.SECONDS if title == wrestling_scene.TITLE else CUTIN_SECONDS

PAIR_STYLES = {
    'ROSE & REVOLVER':        ('MONA × PANTHER', 'ROSE / RICOCHET', ('✦', '◆', '✧'), 'red'),
    'HIGHWAY TO TROUBLE':     ('SKULL × QUEEN', 'IGNITION / OVERDRIVE', ('≻', '»', '›'), 'gold'),
    'MIDNIGHT TAKEOUT':       ('FOX × SKULL', 'SMOKE / IMPACT', ('⟐', '◆', '◇'), 'cyan'),
    'THE DUEL AT DUSK':       ('FOX × PANTHER', 'SILHOUETTE / CROSSHAIR', ('✧', '✦', '×'), 'red'),
    'TEA IN THE CROSSHAIRS':  ('NOIR × MONA', 'CALM / CROSSHAIR', ('◇', '⟐', '◆'), 'gold'),
    'PALACE BODY SLAM':       ('QUEEN × NOIR', 'LOCK / TAKEDOWN', ('»', '×', '◆'), 'gold'),
    'TWO SIDES OF THE MASK':  ('JOKER × CROW', 'MASK / SPLIT STRIKE', ('◆', '◇', '×'), 'red'),
    'THE LAST WALTZ':         ('JOKER × VIOLET', 'STEP / CROSSBLADE', ('✿', '×', '✧'), 'cyan'),
}

SOLO_STYLES = {
    'Joker': ('WILD CARD', ('♠', '◆', '◇'), 'red'),
    'Mona': ('NINE LIVES', ('◆', '✦', '◇'), 'gold'),
    'Skull': ('THUNDER', ('ϟ', '✦', 'ϟ'), 'gold'),
    'Panther': ('FLASH POINT', ('✦', '✧', '✦'), 'red'),
    'Fox': ('FINAL STROKE', ('╱', '◆', '╲'), 'cyan'),
    'Queen': ('REDLINE', ('›', '»', '›'), 'gold'),
    'Noir': ('FINALE', ('♦', '◇', '♦'), 'red'),
    'Crow': ('BLACK MASK', ('◇', '◈', '◇'), 'red'),
    'Violet': ('LAST STEP', ('✿', '✧', '✿'), 'cyan'),
}

ORACLE_STYLES = {
    ORACLE[0]: ('UFO DROP', ('◉', '◆', '◉')),
    ORACLE_SUPPORT[0]: ('RECOVERY SIGNAL', ('+', '◉', '+')),
    FINAL_GUARD[0]: ('DEFENSE SIGNAL', ('[', '◆', ']')),
}


def look(title):
    """Return (kind, cast, motif label, tokens, palette) for the shared renderer."""
    if title in PAIR_STYLES:
        cast, motif, tokens, palette = PAIR_STYLES[title]
        return 'SHOWTIME', cast, motif, tokens, palette
    if title in ORACLE_STYLES:
        motif, tokens = ORACLE_STYLES[title]
        return 'NAVIGATION CUT-IN', 'ORACLE / NECRONOMICON', motif, tokens, 'green'
    for actor, card in ALL_OUT.items():
        if title == card[0]:
            motif, tokens, palette = SOLO_STYLES[actor]
            return 'ALL-OUT ATTACK', actor.upper(), motif, tokens, palette
    return 'CUT-IN', 'PHANTOM THIEVES', 'IMPACT', ('◆', '×', '◆'), 'red'
