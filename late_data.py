"""Royal late chapters, compressed into original terminal operations.

This is an adapted combat campaign, not an exact dungeon/boss recreation.
Calendar transitions and some traversal puzzles are narrated. The two
finale battles have playable scripts and use terminal-balanced loadouts,
not claimed canonical stats or affinities.
Primary evidence: English game scripts at https://mysh.dev/tools/persona/5r/
and original recorded play at https://bai-gaming.com/guides/persona5royal/ .
"""
from copy import deepcopy
from battle_data import shadow
from shuffle_data import SHUFFLE_ENEMIES
from casino_data import LATE_PAIRS
from depths_boss import ENEMY_ADDITIONS as DEPTHS_ENEMIES, DEPTHS_FINAL_WAVES
from lab_boss import ENEMY_ADDITIONS as LAB_ENEMIES, WAVES as LAB_FINAL_WAVES

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
    ('Holy Grail First Encounter',650,['Megido','Marakukaja']),
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
       recruits=(),**extra):
    pairs = () if extra.get('party_size') == 1 else (
        () if id == 'laboratory-reality' else
        _LAB_BOND_PAIRS if id in ('laboratory-colors','laboratory-choice') else
        _LAB_PAIRS if id.startswith('laboratory-') else LATE_PAIRS)
    extra.setdefault('showtime_pairs',pairs)
    if id.startswith(('cruiser-','depths-')):
        extra['forbidden_team'] = ['Crow','Violet']
    return dict(id=id,title=title,map_mark=mark,brief=before,
        story_after=after,waves=waves,navigator='Oracle',
        tactic='Compressed Royal route / Adapted combat',
        hint=hint or 'Scout carefully, preserve recovery, and change tactics when an attack is ineffective.',
        reward=dict(credits=400,joker_sp=3,**({'teammates':list(recruits)} if recruits else {})),
        story_gate=gate or {},mechanic=mechanic or {},**extra)

CRUISER = (
 _n('cruiser-guests','A Ship for the Chosen','VIP',
    'Shido imagines Japan as a sinking world and his supporters as the passengers worth saving. A membership card leads to Ooe and the former noble, the first two recommendation holders.',
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
    'Akechi fights the team with Robin Hood, then reveals Loki and his black mask. He is an opponent here, not a selectable ally.',
    'Akechi confronts Shido\'s cognitive version of him and seals the bulkhead. The Thieves carry on, secure the route, and prepare their public calling card.',
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
    'Shido falls. His attempt to collapse the Palace forces an escape. His confession still does not free society from its desire to surrender responsibility.',
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
    'The Holy Grail draws strength from the prisoners. Winning this shortened combat represents surviving the encounter, not destroying the Grail.',
    'The public sustains the Grail. The Thieves are erased from Shibuya and wake in the Velvet Room; the wardens reunite as Lavenza and the false master is exposed.',
    [['Holy Grail First Encounter']],forbidden_team=['Crow','Violet'],
    mechanic=dict(kind='scripted_story_defeat_after_combat')),
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
    'The public rallies behind the Thieves. Joker manifests Satanael for the decisive shot, ending the god of control. The Royal branch continues only if its earlier story conditions were met.',
    DEPTHS_FINAL_WAVES,forbidden_team=['Crow','Violet'],
    hint='Cut the lines when Oracle finds the opening. Break the god’s arms to weaken its charge.',
    mechanic=dict(kind='grail_arms_and_finisher')),
)
LABORATORY = (
 _n('laboratory-reality','A World Without Loss','TRUTH',
    'In Royal\'s third semester, fulfilled wishes conceal Maruki\'s altered reality. The early visits expose his power and Sumire\'s identity; the Thieves choose their own future.',
    'The team regroups. Sumire accepts her own identity and joins as Violet. The deeper laboratory route remains blocked until Maruki\'s connection through Mementos is addressed.',
    [['Byakhee','Macabre']],recruits=('Violet',),forbidden_team=['Violet'],gate=dict(requires='royal_third_semester_and_rejection_of_false_reality'),
    mechanic=dict(kind='compressed_early_story_visits')),
 _n('laboratory-daat','The Route Through Mementos','CONTROL',
    'The Thieves explore the new Mementos route beyond the former depths, following it to the control room that feeds Maruki\'s Palace.',
    'The connection is altered. The team returns to the laboratory with its deeper path accessible.',
    [['Nebiros','Scathach']],gate=dict(requires='laboratory_barrier_discovered'),
    mechanic=dict(kind='narrated_daat_control_room')),
 _n('laboratory-records','The Research Behind the Wish','RECORDS',
    'Recorded memories and research notes reveal Maruki\'s losses and the development of his cognitive research. The team obtains access by understanding these records.',
    'The identification checks are passed. The next area judges whether people fit the doctor\'s preferred version of happiness.',
    [['Macabre','Byakhee'],['Laboratory Guardian']],gate=dict(requires='daat_control_room_resolved')),
 _n('laboratory-counseling','Answers He Wants to Hear','TESTS',
    'The special consultations reward answers that match Maruki\'s standards, not the player\'s own beliefs. In this version the team navigates the tests in narration.',
    'Back at the hideout, Violet shows Joker a routine in her own style. Their new Showtime is ready for the final approach.',
    [['Scathach','Nebiros']],mechanic=dict(kind='narrated_consultations',canonical_answers=['B','C','D'])),
 _n('laboratory-colors','A Path Toward Eden','COLORS',
    'Color controls switch the light bridges through the Twilight Corridor. The Thieves reach the treasure route, then return for the final decision and calling card.',
    'The team refuses Maruki\'s offer. The next visit is the confrontation, not another ordinary exploration trip.',
    [['Fafnir'],['Baal']],gate=dict(requires='research_and_consultations'),
    mechanic=dict(kind='narrated_color_bridges')),
 _n('laboratory-choice','Our Own Tomorrow','CHOICE',
    'Maruki has one tendril to protect Azathoth, one to strengthen it and one to heal it. Break the protection and hit the core.',
    'The Thieves create Joker\'s opening against Adam Kadmon. Maruki and Joker\'s final human struggle ends the Palace; they return to an uncertain future they can choose for themselves.',
    LAB_FINAL_WAVES,
    gate=dict(requires='route_secured_and_final_offer_rejected_and_calling_card'),
    hint='Read the shifted tendril affinities. If Full Force is charging, guard with every standing ally.',
    mechanic=dict(kind='azathoth_tendrils_and_kadmon',not_implemented=['human_fistfight'])),
)

CHAPTERS = tuple(dict(id=id,title=title,brief=brief,completion=completion,nodes=nodes)
 for id,title,brief,completion,nodes in (
 ('cruiser','Shido\'s Cruiser','Gather five letters and confront the man at the helm.','The confession does not end the crisis.',CRUISER),
 ('depths','Mementos Depths','Challenge the prison and the god of control.','The original final conflict is resolved.',DEPTHS),
 ('laboratory','Maruki\'s Laboratory','Royal branch: reject a happiness imposed on everyone.','The Thieves choose their own tomorrow.',LABORATORY),
))
