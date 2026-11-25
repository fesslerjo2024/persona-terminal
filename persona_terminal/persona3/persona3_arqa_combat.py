"""Authored Lower Arqa formations and early Full Moon/Theurgy content.

The combat values are scaled for the terminal campaign, not the console
game's level curve. Encounter identifiers are independent of display names.
"""

FOES={
    'frivolous':('Frivolous Maya',82,'Strike',22,{'Strike':'weak','Ice':'weak','Wind':'resist'},''),
    'heat-balance':('Heat Balance',90,'Fire',20,{'Electric':'weak','Wind':'weak','Fire':'resist','Ice':'resist'},''),
    'wisp':("Will O’ Wisp Raven",174,'Fire',29,{'Ice':'weak','Fire':'drain','Wind':'resist'},''),
    'lightning-eagle':('Lightning Eagle',76,'Electric',21,{'Wind':'weak','Pierce':'weak','Ice':'resist'},''),
    'heretic':('Heretic Magus',178,'Wind',26,{'Electric':'weak','Wind':'resist'},'magus'),
    'grievous':('Grievous Table',75,'Fire',23,{'Ice':'weak','Fire':'null'},''),
    'dice':('Disturbing Dice',187,'Strike',30,{'Electric':'vulnerable','Fire':'resist'},'dice'),
    'twins':('Slaughter Twins',88,'Slash',24,{'Wind':'weak','Ice':'null','Light':'weak','Dark':'resist'},''),
    'relic':('Clairvoyant Relic',285,'Fire',31,{'Light':'null','Dark':'null'},'relic'),
    'empress':('Empress',235,'Slash',24,{},'empress'),
    'emperor':('Emperor',245,'Electric',25,{},'emperor'),
    'drill-raven':('Black Raven',89,'Wind',16,{'Fire':'null','Wind':'resist'},''),
}

ENCOUNTERS={
    'arqa-patrol':('Lower Arqa Patrol',('frivolous','heat-balance')),
    'arqa-ravens':('Will O’ Wisp Raven • 28F',('wisp','lightning-eagle','lightning-eagle')),
    'arqa-magus':('Heretic Magus • 35F',('heretic','grievous','grievous')),
    'arqa-dice':('Disturbing Dice • 36F',('dice','twins','twins')),
    'arqa-relic':('Clairvoyant Relic • 42F',('relic',)),
    'emperor-empress':('Tartarus Entry • June 8',('empress','emperor')),
    'theurgy-drill':('Theurgy Field Test',('drill-raven',)),
}

PERSONAS={
    'Forneus':(('Bufu','Skewer','Rakukaja'),{'Electric':'weak','Ice':'resist'}),
    'Omoikane':(('Zio','Kouha','Sukukaja'),{'Fire':'weak','Electric':'resist'}),
    'Valkyrie':(('Cleave','Skewer','Rakunda'),{'Fire':'weak','Slash':'resist'}),
    'Inugami':(('Agi','Eiha','Sukunda'),{'Ice':'weak','Dark':'resist'}),
    'Jack Frost':(('Bufu','Mabufu','Sukukaja'),{'Fire':'weak','Ice':'null'}),
}
SKILLS={
    'Kouha':('hit','Light',35,5,'one',0),
    'Eiha':('hit','Dark',35,5,'one',0),
    'Mabufu':('hit','Ice',29,8,'foes',0),
    'Sonic Punch':('hit','Strike',37,0,'one',8),
    'Tarukaja':('buff','attack',0,4,'ally',0),
    'Sukunda':('debuff','agility',0,4,'one',0),
    'Diarama':('heal','',80,7,'ally',0),
}
PERSONA_LEARNS={
    'Forneus':((6,'Mabufu'),),
    'Omoikane':((7,'Rakunda'),),
    'Valkyrie':((6,'Tarukaja'),),
    'Inugami':((6,'Maragi'),),
}

ARCANA={'empress':('Pierce','Strike','Slash'),
        'emperor':('Electric','Fire','Ice','Wind')}
RELIC_SEQUENCE=('Fire','Ice','Electric','Wind')

# IDs are command/action IDs; display names are shared with the original reel.
THEURGIES={
    'cadenza':('Cadenza','heal','',0,'team','Restore 50% max HP to living allies; raises Accuracy/Evasion.'),
    'jacks':('Jack Brothers','damage','Almighty',75,'group','Heavy group damage with a chance to knock enemies down.'),
    'cyclone':('Cyclone Arrow','damage','Wind',119,'single','Heavy Wind to one enemy, bypassing affinity.'),
    'blast':('Hack n’ Blast','damage','Slash',125,'single','Heavy Slash to one enemy, bypassing affinity.'),
    'blizzard':('Blizzard Edge','damage','Ice',123,'single','Heavy Ice to one enemy, bypassing affinity.'),
    'lightning':('Lightning Spike','damage','Electric',89,'group','Heavy Electric to all enemies, bypassing affinity.'),
}
FUSION_SPELLS={'cadenza':frozenset(('Orpheus','Apsaras')),
               'jacks':frozenset(("Jack O'Lantern",'Jack Frost'))}
PARTY_THEURGY={'Yukari':'cyclone','Junpei':'blast','Akihiko':'lightning','Mitsuru':'blizzard'}
