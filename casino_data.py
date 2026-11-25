"""Playable early Casino route, with later operations kept on the existing map.

Terminal-sized formations and stats are adaptations. Royal footage chapters:
https://www.youtube.com/watch?v=x5LDcdELNwo (Staff-Only, Dice, Slot, Darkness).
Recorded entry preview: https://www.bilibili.com/video/BV1214y1J7HP/
Arena footage starts at 1:42:25 in the walkthrough above. Royal field scripts
0157_015_110–140 establish the solo rounds and prize; 0157_011_100 records
the raised toll and two-card loophole used at the Bridge of Judgment.
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
    # Arena-only versions, so regular Shadows elsewhere retain their stats.
    'Arena Ganesha': shadow(110,0,(),
        {'Wind':'drain','Psy':'weak'},'aggressive'),
    'Arena Rangda': shadow(72,12,('Eiha',),
        {'Physical':'repel','Gun':'repel','Fire':'null','Electric':'weak','Bless':'weak','Curse':'null'},'aggressive'),
    'Arena Thor': shadow(345,56,('Zionga','Rakukaja'),
        {'Electric':'null','Bless':'resist','Curse':'resist'},'boss',no_knockdown=True),
    'Sae Leviathan': shadow(860,100,[],{},'casino-sae',
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
       'The arena pays 100,000 coins. Joker rejoins the team at the Bridge of Judgment.',
       [['Arena Ganesha']*2,['Arena Rangda']*3,['Arena Thor']],party_size=1,
       solo_threats=('Electric','Curse'),between_wave_recovery=(.26,8),items={'Stun Gun':2},
       hint='Bring varied magic, healing and an Electric-safe mask. Two Stun Guns are supplied; recover some HP and SP between rounds.'),
    _n('casino-bridge','A Million-Coin Toll','BRIDGE',
       'Clear the guard at the Bridge of Judgment, then present the arena prize. Crow has a contingency if the house changes the rules.',
       'The bridge lowers and the route to the Treasure is secured. The crew can proceed with the calling card and heist.',
       [['Skadi']],wave_breaks={1:'bridge'},story_gate=dict(requires='high_limit_trials_complete'),
       hint='The bridge reads deposits from High Limit cards.'),
    _n('casino-heist','Leviathan and the Escape','HEIST',
       'Sae insists on one more game at her own wheel. Catch the rigging before she can turn it against the crew.',
       'Sae is defeated. Joker draws the pursuit and is captured; the interrogation and the team\'s deception lead into the hunt for Shido. This is not a routine treasure theft ending.',
       [['Sae Leviathan']],story_gate=dict(requires='planned_calling_card_and_heist'),
       mechanic=dict(kind='roulette_boss'),
       hint='Guard through the first spin. When Oracle spots the glass, use the special action to break it.'),
)
CHAPTERS = (dict(id='casino',title="Sae's Casino",brief='Beat a house built on rigged justice.',
                 completion='The arrest is part of a larger plan.',nodes=NODES),)
