"""Playable early Casino route, with later operations kept on the existing map.

Terminal-sized formations and stats are adaptations. Royal footage chapters:
https://www.youtube.com/watch?v=x5LDcdELNwo (Staff-Only, Dice, Slot, Darkness).
Recorded entry preview: https://www.bilibili.com/video/BV1214y1J7HP/
The Royal field scripts (0157_006_120, 0157_007_110 and _130, 0157_009_021,
0157_010_020 and _130, 0157_012_120, 0157_013_100) document the events.
"""
from copy import deepcopy

from battle_data import shadow
from shuffle_data import SHUFFLE_ENEMIES

ENEMY_ADDITIONS = {
    'Midnight Queen': shadow(137,46,('Agilao','Mazionga'), {'Fire':'null','Electric':'resist','Wind':'weak'},'aggressive'),
    'Auspicious Pachyderm': shadow(300,40,('Tempest Slash','Miracle Punch'),
        {'Physical':'resist','Gun':'resist','Wind':'drain','Psy':'weak'},'aggressive'),
    'Wandering Reviver': shadow(238,55,('Mapsio','Maragion'),
        {'Physical':'resist','Wind':'weak','Bless':'weak','Curse':'resist'},'ailment'),
    'Casino Arena Guardian': shadow(460,100,['Rising Slash','Rakukaja','Zionga'],{},'boss',
                                    no_knockdown=True,adaptation='Terminal-balanced phase; not original boss statistics.'),
    'Sae Leviathan': shadow(860,100,['Tempest Slash','Megido','Dekaja','Matarunda'],{},'boss',
                            no_knockdown=True,adaptation='Terminal-balanced phase; not original boss statistics.'),
    'Snake King': shadow(375,55,('Mazionga',), {'Gun':'resist'},'casino-snake',no_knockdown=True),
}
ENEMY_ADDITIONS.update({n:deepcopy(SHUFFLE_ENEMIES[n]) for n in ('Power','Ose','Rangda','Skadi')})

# Casino Crow is the Robin Hood phase, not the unlocked Loki training kit.
ROBIN_HOOD = dict(skills=['Kouga','Makouga','Eiga','One-shot Kill','Rakunda'],
                  affinity={'Bless':'resist','Curse':'weak'})
PRE_CASINO_PAIRS = (('Mona','Panther'),('Skull','Queen'),('Fox','Skull'),
                    ('Fox','Panther'),('Noir','Mona'))
LATE_PAIRS = PRE_CASINO_PAIRS + (('Queen','Noir'),)


def _n(id,title,mark,brief,after,waves,*,hint,recruits=(),**extra):
    pairs = () if extra.get('party_size') == 1 else (
        PRE_CASINO_PAIRS if id=='casino-service' else LATE_PAIRS)
    extra.setdefault('story_gate',{})
    extra.setdefault('mechanic',{})
    return dict(id=id,title=title,map_mark=mark,brief=brief,story_after=after,
                waves=waves,navigator='Oracle',forbidden_team=['Violet'],
                tactic='Compressed Royal route / Adapted combat',
                team_overrides={'Crow':ROBIN_HOOD},showtime_pairs=pairs,hint=hint,
                reward=dict(credits=400,joker_sp=3,**({'teammates':list(recruits)} if recruits else {})),
                **extra)


NODES = (
    _n('casino-service','Behind the Tables','CARD',
       'Sae’s courthouse has turned into a casino. Cross the staff corridors for a security keycard, then ambush the guard holding the members card.',
       'Oracle pulls the Casino map from the terminal. The members card starts the elevator, and Crow joins the active roster.',
       [['Midnight Queen','Midnight Queen'],['Auspicious Pachyderm']],recruits=('Crow',),
       hint='Bring a few different elements. You need to get past two different security teams.'),
    _n('casino-rigging','Turn the House Against Itself','SLOTS',
       'The exchange wants 50,000 coins for a High Limit card. Clear the dice control room so Crow and Oracle can turn the house’s rigging against it.',
       'The jackpot buys a High Limit card, but the elevator attendant still demands a reservation. The crew goes to see Sae in the real courtroom.',
       [['Wandering Reviver'],['Ose','Rangda']],wave_breaks={1:'dice',2:'slots'},
       hint='Clearing a guard opens the controls. The squad’s HP and SP carry over.'),
    _n('casino-darkness','House of Darkness','DARK',
       'After the real court visit changes Sae’s cognition, the elevator admits the crew. The first high-limit attraction is a dark maze with a 1,000-coin entry fee.',
       'The attendant pays the 10,000-coin prize. It covers the entry fee for Joker’s next challenge, the Battle Arena.',
       [['Rangda','Power'],['Snake King']],wave_breaks={1:'darkness'},
       hint='Bring healing. The exit attendant can charge a party-wide Electric attack.',
       story_gate=dict(requires='real_world_courthouse_visit')),
    _n('casino-arena','The Unfair Arena','SOLO',
       'Joker enters the Battle Arena alone. The casino changes the terms and sends successive opponents rather than honoring a fair contest.',
       'Joker wins the arena prize. The team reunites at the bridge to the manager\'s floor.',
       [['Ose'],['Power'],['Casino Arena Guardian']],party_size=1,
       hint='Solo operation: bring healing and support on Joker; do not depend on a Baton Pass.'),
    _n('casino-bridge','A Million-Coin Toll','BRIDGE',
       'Sae raises the bridge fee from one hundred thousand to one million coins. Akechi uses the casino\'s own card and coin rules to meet the demand.',
       'The route to the treasure is secured. The calling card and heist follow the team\'s fixed plan, rather than an immediate attack.',
       [['Skadi','Rangda']],story_gate=dict(requires='high_limit_trials_complete'),
       mechanic=dict(kind='narrated_coin_loophole'),
       hint='Scout carefully, preserve recovery, and change tactics when an attack is ineffective.'),
    _n('casino-heist','Leviathan and the Escape','HEIST',
       'On the planned heist, Sae becomes Leviathan. Her roulette is another rigged game. This terminal encounter compresses its exposure into a conventional boss battle.',
       'Sae is defeated. Joker draws the pursuit and is captured; the interrogation and the team\'s deception lead into the hunt for Shido. This is not a routine treasure theft ending.',
       [['Sae Leviathan']],story_gate=dict(requires='planned_calling_card_and_heist'),
       mechanic=dict(kind='adapted_boss',not_implemented=['roulette','special_assignment']),
       hint='Scout carefully, preserve recovery, and change tactics when an attack is ineffective.'),
)
CHAPTERS = (dict(id='casino',title="Sae's Casino",brief='Beat a house built on rigged justice.',
                 completion='The arrest is part of a larger plan.',nodes=NODES),)
