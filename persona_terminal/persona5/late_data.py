"""Royal late chapters, compressed into original terminal operations.

This is an adapted combat campaign, not an exact dungeon/boss recreation.
Calendar transitions and some traversal puzzles are narrated. The two
finale battles have playable scripts and use terminal-balanced loadouts,
not claimed canonical stats or affinities.
Primary evidence: English game scripts at https://mysh.dev/tools/persona/5r/
and original recorded play at https://bai-gaming.com/guides/persona5royal/ .
"""
from copy import deepcopy
from .battle_data import shadow
from .shuffle_data import SHUFFLE_ENEMIES
from .casino_data import LATE_PAIRS
from .depths_boss import ENEMY_ADDITIONS as DEPTHS_ENEMIES, DEPTHS_FINAL_WAVES
from .lab_boss import ENEMY_ADDITIONS as LAB_ENEMIES, WAVES as LAB_FINAL_WAVES

_NORMALS = ('Power','Ose','Rangda','Skadi','Narcissus','Dakini','Garuda',
            'Cerberus','Kali','Hanuman','Melchizedek','Moloch','Abaddon',
            'Dominion','Throne','Mot','Byakhee','Macabre','Nebiros',
            'Scathach','Fafnir','Baal')
ENEMY_ADDITIONS = {name: deepcopy(SHUFFLE_ENEMIES[name]) for name in _NORMALS}

def _boss(name,hp,skills,sp=100):
    ENEMY_ADDITIONS[name] = shadow(hp,sp,skills,{},'boss',no_knockdown=True,
        adaptation='Terminal-balanced phase; not original boss statistics.')

for name,hp,skills in (
    ('Politician Ooe',430,['Psio','Rakukaja','Rising Slash']),
    ('Former Noble',450,['Eiga','Tarunda','Tempest Slash']),
    ('TV Station President',470,['Freila','Marakukaja','Rising Slash']),
    ('IT Company President',480,['Zionga','Makajam','Megido']),
    ('The Cleaner',530,['Tempest Slash','Eiga','Tarukaja']),
    ('Akechi Robin Hood',500,['Kouga','Eiga','Rising Slash']),
    ('Akechi Loki',660,['Eiga','Megido','Debilitate','Tempest Slash']),
    ('Beast of Human Sacrifice',510,['Rising Slash','Tarukaja']),
    ('Wings of Human Sacrifice',470,['Maragion','Mabufula','Mazionga']),
    ('Tomb of Human Sacrifice',500,['Megido','Marakukaja']),
    ('Shido Samael',680,['Tempest Slash','Matarukaja','Dekaja','Megido']),
    ('Uriel',440,['Maragion','Tempest Slash']),
    ('Raphael',470,['Sword Dance','Rakukaja']),
    ('Gabriel',470,['Mabufula','Diarama']),
    ('Michael',600,['Makouga','Sword Dance','Debilitate']),
    ('Laboratory Guardian',540,['Mapsio','Rakukaja','Megido']),
):
    _boss(name,hp,skills)


ENEMY_ADDITIONS['Shido Final Duel'] = shadow(
    440,100,['Agilao','Bufula','Zionga','Garula','Rising Slash'],{},'cruiser-solo',
    no_knockdown=True,adaptation='Telegraphed elements with a distinct Physical follow-up.')


ENEMY_ADDITIONS.update(DEPTHS_ENEMIES)
ENEMY_ADDITIONS.update(LAB_ENEMIES)

# Royal unlocks the latter pair at a hideout meeting after Rank 10 Faith.
# The late briefing after the tests is the combat campaign's substitute.
_LAB_PAIRS = LATE_PAIRS + (('Joker','Crow'),)
_LAB_BOND_PAIRS = _LAB_PAIRS + (('Joker','Violet'),)


def _n(id,title,mark,before,after,waves,*,hint=None,gate=None,mechanic=None,
       recruits=(),tactic='Compressed Royal route / Adapted combat',**extra):
    pairs = () if extra.get('party_size') == 1 else (
        () if id == 'laboratory-reality' else
        _LAB_BOND_PAIRS if id in ('laboratory-colors','laboratory-choice') else
        _LAB_PAIRS if id.startswith('laboratory-') else LATE_PAIRS)
    extra.setdefault('showtime_pairs',pairs)
    if id.startswith(('cruiser-','depths-')):
        extra['forbidden_team'] = ['Crow','Violet']
    return dict(id=id,title=title,map_mark=mark,brief=before,
        story_after=after,waves=waves,navigator='Oracle',
        tactic=tactic,
        hint=hint or 'Scout carefully, preserve recovery, and change tactics when an attack is ineffective.',
        reward=dict(credits=400,joker_sp=3,**({'teammates':list(recruits)} if recruits else {})),
        story_gate=gate or {},mechanic=mechanic or {},**extra)

CRUISER = (
 _n('cruiser-guests','A Ship for the Chosen','VIP',
    'The conspiracy leads to Shido, a politician who sees Japan as a sinking world. Board his ship and learn who can get you into the central hall.',
    'Two letters are collected. Statue-controlled corridors turn intruders into mice; the Thieves use vents, switches, and human-form doors to continue.',
    [['Politician Ooe'],['Former Noble']],mechanic=dict(kind='narrated_mouse_route')),
 _n('cruiser-industry','Screens and Servers','LETTERS',
    'The next letters belong to the TV station president and the IT company president. Entertainment halls, mouse passages, and the ship\'s exterior connect their guarded rooms.',
    'Four letters are secured. Only the cleaner remains between the team and access to the central hall.',
    [['TV Station President'],['IT Company President']]),
 _n('cruiser-cleaner','The Fifth Letter','ENGINE',
    'The cleaner controls the final recommendation. The pursuit leads below the passenger decks toward the engine room.',
    'The fifth letter is obtained, but Akechi intercepts the Thieves before they can finish securing the route.',
    [['Cerberus','Kali'],['The Cleaner']]),
 _n('cruiser-akechi','Behind the Detective Mask','RIVAL',
    'Akechi blocks the engine-room exit. You know how Crow fights beside you; you don’t yet know how much he was holding back.',
    'Akechi’s mask is on the floor. At the far end of the engine room, another pair of footsteps stops.',
    [['Akechi Robin Hood'],['Akechi Loki']],forbidden_team=['Crow'],
    gate=dict(requires='five_letters')),
 _n('cruiser-sacrifice','The Weight of His Supporters','THRONE',
    'After the public calling card, Shido rides the Beast of Human Sacrifice. The monument changes into wings and a tomb before Shido fights directly.',
    'Shido abandons his monument and overwhelms the others, isolating Joker for the final exchange.',
    [['Beast of Human Sacrifice'],['Wings of Human Sacrifice'],['Tomb of Human Sacrifice'],['Shido Samael']],
    forbidden_team=['Crow'],gate=dict(requires='public_calling_card'),
    mechanic=dict(kind='adapted_sequential_phases')),
 _n('cruiser-duel','Joker Stands Alone','DUEL',
    'Shido has forced Joker into a one-on-one finish. The final duel is separated into its own operation for terminal pacing.',
    'Shido falls. His attempt to collapse the Palace forces an escape. Outside, the election coverage continues.',
    [['Shido Final Duel']],party_size=1,forbidden_team=['Crow'],
    solo_threats=('Ice','Fire','Electric','Wind'),
    hint='Switch or Guard against the announced element. Guard makes Shido overextend, opening a turn to recover or strike.'),
)
DEPTHS = (
 _n('depths-prison','The Prison Beneath Tokyo','CELLS',
    'The Thieves enter the depths of Mementos. The cells hold people who have accepted captivity rather than the burden of choosing for themselves.',
    'The passages descend toward a shrine at the bottom of the prison.',
    [['Melchizedek','Moloch']],forbidden_team=['Crow','Violet']),
 _n('depths-floor','A Path Painted Through Prison','TILES',
    'Floor panels change color as the team crosses them. Later routes add move limits and Vermillion Disks. These traversal puzzles are narrated in this combat edition.',
    'The final panels open the way to the Prison of Acedia and the apparent treasure.',
    [['Abaddon'],['Moloch','Melchizedek']],forbidden_team=['Crow','Violet'],
    mechanic=dict(kind='narrated_floor_toggle',not_implemented=['tile_grid','move_limit','disk_inventory'])),
 _n('depths-grail','A Treasure That Will Not Fall','GRAIL',
    'The prisoners sustain the Grail. Recover between attacks and survive its charged Eternal Light; damage cannot finish it.',
    'You survived, but the Grail isn’t finished. Something is happening above ground in Shibuya.',
    [['Holy Grail First Encounter']],forbidden_team=['Crow','Violet'],
    hint='Heal after Arrow of Light. Guard when the Grail charges Eternal Light.',
    mechanic=dict(kind='survive_eternal_light')),
 _n('depths-rebellion','Choose Rebellion Again','RETURN',
    'Joker rejects the false god\'s bargain and restores his companions\' resolve. Back in the merged city, the team climbs toward the temple.',
    'The first guardians fall. The ascent continues through the distorted city.',
    [['Uriel'],['Raphael']],forbidden_team=['Crow','Violet'],
    gate=dict(requires='reject_false_god_and_reunite_team')),
 _n('depths-guardians','The Last Guardians','ASCENT',
    'Gabriel and Michael stand on the final ascent. The Thieves press toward the Holy Grail without accepting the world\'s imposed order.',
    'The path reaches the temple. The Grail no longer has a prison full of willing supporters to conceal its nature.',
    [['Gabriel'],['Michael']],forbidden_team=['Crow','Violet']),
 _n('depths-yaldabaoth','The God of Control','FREEDOM',
    'The Grail feeds through its supply lines. Sever them, then confront Yaldabaoth and the arms it manifests.',
    'The god of control falls. The Metaverse begins to recede. On the other side, something has changed.',
    DEPTHS_FINAL_WAVES,forbidden_team=['Crow','Violet'],
    hint='Cut the lines when Oracle finds the opening. Break the god’s arms to weaken its charge.',
    mechanic=dict(kind='grail_arms_and_finisher')),
)
LABORATORY = (
 _n('laboratory-reality','A World Without Loss','TRUTH',
    'It’s January. Tokyo has started the new year as though the night you defeated the Grail never happened. At Leblanc, there’s an extra cup on the counter.',
    'The squad regroups after the first visit. Someone is waiting by the sealed route.',
    [['Byakhee','Macabre']],recruits=('Violet',),forbidden_team=['Violet'],gate=dict(requires='royal_third_semester_and_rejection_of_false_reality'),
    mechanic=dict(kind='compressed_early_story_visits')),
 _n('laboratory-daat','The Route Through Mementos','CONTROL',
    'The deeper laboratory route is sealed. Follow Oracle’s lead into the new Da’at route in Mementos to find what powers the barrier.',
    'The connection is altered. The team returns to the laboratory with its deeper path accessible.',
    [['Nebiros','Scathach']],gate=dict(requires='laboratory_barrier_discovered'),
    mechanic=dict(kind='narrated_daat_control_room')),
 _n('laboratory-records','The Research Behind the Wish','RECORDS',
    'Follow the research trail into the patient archive. Open a record while Oracle releases the research wing’s lock.',
    'The records lead to a room where patients are offered a very particular kind of treatment.',
    [['Macabre','Byakhee'],['Laboratory Guardian']],gate=dict(requires='daat_control_room_resolved'),
    lab_room='archive',tactic='Read a patient record / Clear the research wing'),
 _n('laboratory-counseling','Answers He Wants to Hear','TESTS',
    'A consultation terminal asks what should happen to a patient’s painful memory. Give your answer and find a way through the ward.',
    'Back at the hideout, Violet shows Joker a routine in her own style. Their new Showtime is ready for the final approach.',
    [['Scathach','Nebiros']],lab_room='consult',tactic='Answer the consultation / Reach the next ward'),
 _n('laboratory-colors','A Path Toward Eden','COLORS',
    'The Twilight Corridor’s switch changes where the light bridge leads. Cross it, then clear the patrol guarding the route to Eden.',
    'The route is secure. Maruki asks the team to hear him out before they return.',
    [['Fafnir'],['Baal']],gate=dict(requires='research_and_consultations'),
    lab_room='bridge',tactic='Switch the bridge / Fight through to Eden'),
 _n('laboratory-choice','Our Own Tomorrow','CHOICE',
    'Maruki has one tendril to protect Azathoth, one to strengthen it and one to heal it. Break the protection and hit the core.',
    'The last shot brings Adam Kadmon down. The floor of the laboratory begins to give way.',
    LAB_FINAL_WAVES,
    gate=dict(requires='route_secured_and_final_offer_rejected_and_calling_card'),
    hint='Read the shifted tendril affinities. If Full Force is charging, guard with every standing ally.',
    mechanic=dict(kind='azathoth_tendrils_and_kadmon',story_epilogue='maruki-coda')),
)

CHAPTERS = tuple(dict(id=id,title=title,brief=brief,completion=completion,nodes=nodes)
 for id,title,brief,completion,nodes in (
 ('cruiser','Shido\'s Cruiser','The casino trap points to Shido, a politician close to taking power. The Thieves follow the trail to his ship.','The confession does not end the crisis.',CRUISER),
 ('depths','Mementos Depths','Shido has confessed. A Palace built from far more than one person’s desires is still changing Tokyo.','Tokyo is free of the Grail.',DEPTHS),
 ('laboratory','Maruki\'s Laboratory','Find out what changed while Tokyo was celebrating.','The Thieves choose their own tomorrow.',LABORATORY),
))
