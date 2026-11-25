"""Okumura's Spaceport, six original terminal operations.

Royal game scripts: fscr0156 field events; e322–e355 story events.
https://mysh.dev/tools/persona/5r/files/dataR.cpk/script/field
https://mysh.dev/tools/persona/5r/files/dataR.cpk/event/event_data/message/e300
English Royal boss footage: https://www.youtube.com/watch?v=Ojt8V4mgu2U
Condenses alarms, ranks, shift controls and the clock into discrete battles.
HP, skill/reward recipes and the number of bots per group are adaptations.
"""
from battle_data import persona, shadow
from shuffle_data import SHUFFLE_ENEMIES



PERSONA_ADDITIONS = {
    'Lilim': persona(['Eiga','Maeiga','Lullaby','Bufula'],
                     {'Ice':'resist','Wind':'weak','Bless':'weak','Curse':'null'},
                     'Curse / Ice • Sleep'),
    'Decarabia': persona(['Agilao','Maragion','Megidola','Rakunda'],
                          {'Physical':'weak','Fire':'repel','Nuclear':'resist','Curse':'resist'},
                          'Fire • Almighty • defense down'),
    'Mothman': persona(['Zionga','Mazionga','Nocturnal Flash','Sukukaja'],
                        {'Gun':'weak','Electric':'null','Psy':'resist'},
                        'Electric • Dizzy • agility up'),
}


def _shadow(name,hp,sp,skills,**overrides):
    source=SHUFFLE_ENEMIES[name]
    return {**source,'hp':hp,'sp':sp,'skills':list(skills),
            'affinity':dict(source['affinity']),**overrides}


def _worker(hp,weak,skills):
    primary=('Physical','Gun','Fire','Ice','Electric','Wind','Psy','Nuclear','Bless','Curse')
    affinity={e:('weak' if e in weak else 'resist') for e in primary}
    return shadow(hp,21,skills,affinity,'space-worker')


ENEMY_ADDITIONS = {
    'Spaceport Decarabia': _shadow('Decarabia',139,32,('Agilao','Rakunda','Megido')),
    'Spaceport Lilim': _shadow('Lilim',143,35,('Bufula','Lullaby','Tarunda')),
    'Spaceport Mothman': _shadow('Mothman',146,31,('Zionga','Dazzler')),
    'Spaceport Arahabaki': _shadow('Arahabaki',163,33,('Freila','Makajam','Rakunda')),
    'Spaceport Kaiwan': _shadow('Kaiwan',159,34,('Psio','Makajam','Rakukaja')),
    'Cognitive Sugimura': shadow(210,33,['Headbutt','Rakukaja','Cleave'],
                                  {'Physical':'resist'},'aggressive'),
    'Plant Overseer': shadow(167,36,['Marakukaja','Diarama','Kouga'],
                             {'Gun':'resist','Fire':'resist','Curse':'weak'},'support'),
    'Corporobo MDL-WKR': _worker(73,('Fire','Wind'),['Cleave']),
    'Corporobo MDL-CH': _worker(78,('Ice','Psy'),['Headbutt']),
    'Corporobo MDL-AM': _worker(83,('Electric','Nuclear'),['Agi','Bufu','Garu']),
    'Corporobo MDL-DM': _worker(90,('Wind','Bless'),['Cleave','Tarukaja']),
    'Corporobo MDL-GM': _worker(103,('Psy','Curse'),['Headbutt','Cleave']),
    'Execurobo MDL-ED': shadow(410,60,['Rising Slash','Tarukaja'],{},
                              'space-exec',no_knockdown=True),
    'Cognitive Haru': shadow(158,30,['Cleave'],{},'space-cognitive',no_knockdown=True),
    'Shadow Okumura': shadow(1,1,[],{},'space-mammon',no_knockdown=True),
}

_STORY_PAIRS = (('Mona','Panther'),('Skull','Queen'),('Fox','Skull'))
_NAV = dict(navigator='Oracle',oracle_features_available=('support','guard','ufo'),
            showtime_pairs=_STORY_PAIRS)
_FLOOR_RANKS=('Corporobo MDL-WKR','Corporobo MDL-CH','Corporobo MDL-AM',
              'Corporobo MDL-DM','Corporobo MDL-GM')


NODES = (
    dict(id='spaceport-entry',region='Spaceport',title='The Biometric Gate',map_mark='GATE',
         tactic='Find Mona / Open the biometric gate',**_NAV,
         brief='Rejoin Mona and the Beauty Thief. Only someone with Haru’s family credentials can open the inner gate.',
         story_before='Mona and a masked girl are already inside Okumura’s Palace. Catch up to them before trying the biometric gate.',
         story_after='The counterfeit fiancé is defeated. Haru reaches for the gate key.',
         hint='Keep the support robots from shaping the whole fight. If a status lands, recover before the next hit can exploit it.',
         preview='Sugimura’s cognitive double and two worker robots.',
         waves=[['Cognitive Sugimura','Corporobo MDL-WKR','Corporobo MDL-WKR']],
         reward=dict(teammates=['Noir'],personas=['Lilim'],skill_cards=['Psio'],
                     credits=265,joker_hp=6)),
    dict(id='spaceport-ranks',region='Spaceport',title='Company Ranks',map_mark='ID',
         tactic='Read employee clues / Steal the IDs',**_NAV,
         brief='Oracle opens the terminal and pulls a map. The next doors only recognize progressively higher employee ranks.',
         story_before='The robots talk about their supervisors. Rather than picking a fight with every uniform, the Thieves match each clue to the employee with the right ID.',
         story_after='The last ID opens the route to the factory. Haru recognizes her father’s company, down to how little it cares what happens to exhausted workers.',
         hint='The ranks fight differently. Find ways to knock targets down while resisting the urge to spend every group spell on the first formation.',
         preview='Two supervisor details with different ranks supporting them.',
         waves=[['Corporobo MDL-AM','Corporobo MDL-WKR','Spaceport Mothman'],
                ['Corporobo MDL-GM','Corporobo MDL-DM','Spaceport Kaiwan']],
         reward=dict(personas=['Mothman'],skill_cards=['Mapsio'],credits=280,joker_sp=5)),
    dict(id='spaceport-factory',region='Spaceport',title='Lunch Break',map_mark='PRESS',
         tactic='Stop the press / Clear the patrol',press_console=True,**_NAV,
         brief='Use the shift console to hold the press open. Fight past the patrol on the far side.',
         story_before='Workers marked spent are fed into a furnace beyond the hydraulic press. Hold the press open long enough to cross, then clear the catwalk patrol.',
         story_after='The assembly line leads toward a vehicle large enough to take the ruler off the station. Futaba traces a path around the outer hull.',
         hint='Bring two forms of offense and a recovery option. Watch for reflected weapon attacks, and heal early if a group spell clips several allies.',
         preview='A press-side patrol and the guards above the incinerator.',
         waves=[['Spaceport Decarabia','Corporobo MDL-CH'],
                ['Spaceport Arahabaki','Plant Overseer']],
         reward=dict(personas=['Decarabia'],skill_cards=['Maeiga'],credits=295,joker_hp=8)),
    dict(id='spaceport-airlocks',region='Spaceport',title='Outside the Hull',map_mark='LOCK',
         tactic='Clear hull patrols / Reach the launch gantry',**_NAV,
         brief='Fight past the two patrols guarding the outer hull and launch gantry.',
         story_before='The elevator won’t take the crew to the Treasure. Oracle routes the team along the outer hull. Get past its patrols to reach the launch gantry.',
         story_after='The SS Utopia is Okumura’s escape craft. The Thieves can now reach it from the station and know where to return after the calling card.',
         hint='Read Analyze before committing to a repeated attack. Bring enough coverage to change plans if a rank takes little damage from your first choice.',
         preview='Two formations stationed along the outer hull and launch gantry.',
         waves=[['Spaceport Lilim','Corporobo MDL-DM'],
                ['Spaceport Kaiwan','Corporobo MDL-GM','Corporobo MDL-WKR']],
         reward=dict(skill_cards=['Kouga','Dekunda'],credits=325,joker_sp=6,
                     team_skills={'Noir':['Rakunda']})),
    dict(id='spaceport-heist',region='Spaceport',title='Countdown to Launch',map_mark='UTOPIA',
         tactic='Calling card / Stop the launch',**_NAV,
         brief='Noir delivers the card to her father’s study. Return to the SS Utopia before Okumura can leave with the Treasure.',
         story_before='Okumura finds the card and contacts the police. Inside, the Treasure takes shape and the station’s launch sequence starts.',
         story_after='The launch attempt does not settle the heist. Deep inside the station, the Thieves corner Shadow Okumura. He offers Mona a job rather than admitting who his company has hurt.',
         hint='Treat this as a loadout check. Know which allies can pass Baton, and keep a mix of wide spells and inexpensive attacks for the last operation.',
         preview='Two robot lines between the Thieves and the launch chamber.',
         waves=[['Corporobo MDL-AM','Corporobo MDL-DM','Spaceport Mothman'],
                ['Corporobo MDL-GM','Plant Overseer']],
         reward=dict(skill_cards=['Mediarama'],credits=345,joker_hp=5,joker_sp=4)),
    dict(id='spaceport-boss',region='Spaceport',title='The Executive Floor',map_mark='MAMMON',
         tactic='Clear squads / Guard the big attacks',**_NAV,
         brief='Okumura protects himself with disposable units. Break their formation before he can call a new shift.',
         story_before='Mona turns down the offer. Okumura orders his workers to protect him, then shows Noir how readily he would discard even an image of his daughter.',
         story_after='The last robot falls. Pick up the Treasure and clear the executive floor.',
         hint='Drop all three workers in a rank by the end of round 2 or they get one full reissue. Chain weakness hits and Baton Passes. Guard against the charges that follow.',
         preview='Five worker ranks, an executive unit, the cognitive copy, then the exposed ruler.',
         waves=[[name]*3 for name in _FLOOR_RANKS]+[
            ['Execurobo MDL-ED'],['Cognitive Haru'],['Shadow Okumura']],
         spaceport_clock=(2,2,2,2,2),
         items={'Soul Drop':3,'Snuff Soul':2},
         reward=dict(skill_cards=['Marakunda'],credits=475,joker_hp=9,joker_sp=7)),
)

CHAPTERS = (dict(id='spaceport', title='Okumura’s Spaceport', nodes=NODES,
                 brief='The trail of breakdowns leads toward Okumura Foods. Mona wants to follow it before the rest of the team is ready.',
                 completion='Okumura’s collapse puts the Thieves under suspicion.'),)
