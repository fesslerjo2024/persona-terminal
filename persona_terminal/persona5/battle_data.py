"""Combat data for Oracle's Velvet Room simulations.

Named moves, elemental identities, and party roles follow Royal. HP, SP pools,
damage, training formations, and some move effects are tuned for this terminal
sim rather than imported game statistics. No game assets or dialogue.
References: https://persona.atlus.com/p5r/
 https://blog.playstation.com/2020/05/07/editors-choice-persona-5-royal-steals-hearts-with-style/
 https://aqiu384.github.io/megaten-database/p5r/metaverse
"""
ELEMENTS = ('Physical','Gun','Fire','Ice','Electric','Wind','Psy','Nuclear','Bless','Curse','Almighty')
SKILLS = {}


def add(name, kind, power=0, *, element='Almighty', sp=0, hp=0, target='enemy', **extra):
    SKILLS[name] = dict(kind=kind, element=element, power=power, sp=sp, hp=hp,
                       target=target, **extra)


for single, group, element, status in (
    ('Agilao', 'Maragion', 'Fire', 'burn'),
    ('Bufula', 'Mabufula', 'Ice', 'freeze'),
    ('Zionga', 'Mazionga', 'Electric', 'shock'),
    ('Garula', 'Magarula', 'Wind', None),
    ('Psio', 'Mapsio', 'Psy', None),
    ('Freila', 'Mafreila', 'Nuclear', None),
    ('Kouga', 'Makouga', 'Bless', None),
    ('Eiga', 'Maeiga', 'Curse', None),
):
    effect = dict(status=status, chance=24) if status else {}
    add(single, 'damage', 51, element=element, sp=8, accuracy=95, **effect)
    add(group, 'damage', 42, element=element, sp=16, accuracy=95, target='enemies', **effect)

for name, element, status in (
    ('Agi','Fire','burn'),('Bufu','Ice','freeze'),('Zio','Electric','shock'),
    ('Garu','Wind',None),('Psi','Psy',None),('Frei','Nuclear',None),
    ('Kouha','Bless',None),('Eiha','Curse',None),
):
    add(name, 'damage', 33, element=element, sp=4, accuracy=95,
        **(dict(status=status, chance=20) if status else {}))

for name, power, cost, target, crit, accuracy in (
    ('Cleave', 45, 6, 'enemy', 12, 95),
    ('Headbutt',55,9,'enemy',12,92),
    ('Rising Slash',61,10,'enemy',15,93),
    ('Vajra Blast',48,13,'enemies',10,88),
    ('Miracle Punch',45,8,'enemy',38,77),
    ('Sword Dance',72,21,'enemy',44,92),
    ('One-shot Kill',72,17,'enemy',35,91),
    ('Riot Gun',56,24,'enemies',18,89),
    ('Tempest Slash',59,17,'enemy',17,88),
):
    elem = 'Gun' if name in ('One-shot Kill','Riot Gun') else 'Physical'
    add(name,'damage',power,element=elem,hp=cost,target=target,crit=crit,accuracy=accuracy,
        **(dict(status='forget',chance=30) if name=='Headbutt' else {}))

add('Megido','damage',48,sp=15,target='enemies',accuracy=96)
add('Megidola','damage',59,sp=24,target='enemies',accuracy=95)
for name,power,cost,target in (('Dia',45,3,'ally'),('Diarama',83,6,'ally'),
                               ('Media',40,7,'allies'),('Mediarama',65,12,'allies'),('Diarahan',155,18,'ally')):
    add(name,'heal',power,sp=cost,target=target)
add('Recarm','revive',50,sp=8,target='ally')
add('Energy Drop','cure',0,sp=4,target='ally')
add('Energy Shower','cure',0,sp=8,target='allies')
for name,stat,kind,cost,target in (
    ('Tarukaja','attack','buff',8,'ally'),('Matarukaja','attack','buff',24,'allies'),
    ('Rakukaja','defense','buff',8,'ally'),('Marakukaja','defense','buff',24,'allies'),
    ('Sukukaja','agility','buff',8,'ally'),('Masukukaja','agility','buff',24,'allies'),
    ('Tarunda','attack','debuff',8,'enemy'),('Matarunda','attack','debuff',24,'enemies'),
    ('Rakunda','defense','debuff',8,'enemy'),('Marakunda','defense','debuff',24,'enemies'),
    ('Sukunda','agility','debuff',8,'enemy'),('Masukunda','agility','debuff',24,'enemies'),
):
    add(name,kind,25,sp=cost,target=target,stat=stat)
add('Dekaja','dekaja',sp=10,target='enemies')
add('Dekunda','dekunda',sp=10,target='allies')
add('Debilitate','debuff',25,sp=30,target='enemy',stat='all')
for name,status,cost,target,chance in (
    ('Dormina','sleep',3,'enemy',92),
    ('Lullaby','sleep',8,'enemies',48),
    ('Dazzler','dizzy',5,'enemy',88),
    ('Nocturnal Flash','dizzy',8,'enemies',55),
    ('Evil Smile','fear',8,'enemies',55),
    ('Makajam','forget',5,'enemy',82),
):
    add(name,'ailment',sp=cost,target=target,status=status,chance=chance)

# Training-item commands are cast by the inventory system, not by Personas.
add('Medicine','heal',50,target='ally')
add('Life Ointment','revive',100,target='ally')
add('Revival Bead','revive',50,target='ally')
add('Soul Drop','restore',10,target='ally')
add('Snuff Soul','restore',25,target='ally')
add('Hiranya','cure',target='ally')
add('Molotov Cocktail','damage',42,element='Fire',accuracy=100,status='burn',chance=60)
add('Freeze Spray','damage',42,element='Ice',accuracy=100,status='freeze',chance=60)
add('Stun Gun','damage',42,element='Electric',accuracy=100,status='shock',chance=60)
add('Air Cannon','damage',42,element='Wind',accuracy=100)
ITEMS = {
    name: dict(count=count,skill=name)
    for name,count in (('Medicine',3),('Life Ointment',1),('Revival Bead',2),
                      ('Soul Drop',2),('Snuff Soul',1),('Hiranya',2),
                      ('Molotov Cocktail',1),('Freeze Spray',1),('Stun Gun',1),('Air Cannon',1))
}


def unit(hp,sp,skills,affinity=None,rounds=3,**extra):
    return dict(hp=hp,sp=sp,skills=list(skills),affinity=affinity or {},rounds=rounds,**extra)


# Curated training loadouts. Mona and Violet carry extra agility support
# for this simulation, not as a claim about their canonical level-up lists.
TEAM = {
    'Mona':unit(120,55,['Garula','Magarula','Diarama','Mediarama','Recarm','Miracle Punch','Sukunda'],
                {'Electric':'weak','Wind':'resist'},5,persona='Zorro',role='Wind • healing • critical hits'),
    'Skull':unit(180,37,['Zionga','Mazionga','Headbutt','Tempest Slash','Tarukaja','Matarukaja'],
                 {'Wind':'weak','Electric':'resist'},3,persona='Captain Kidd',role='Electric • physical • attack buffs'),
    'Panther':unit(125,58,['Agilao','Maragion','Dormina','Lullaby','Tarunda','Matarunda','Dekaja','Diarama'],
                    {'Ice':'weak','Fire':'resist'},6,persona='Carmen',role='Fire • sleep • attack down • buff wipe'),
    'Fox':unit(158,38,['Bufula','Mabufula','Rising Slash','Vajra Blast','Sukukaja','Masukukaja'],
                {'Fire':'weak','Ice':'resist'},4,persona='Goemon',role='Ice • physical • agility buffs'),
    'Queen':unit(151,49,['Freila','Mafreila','Diarama','Mediarama','Energy Shower','Rakukaja','Marakukaja'],
                  {'Psy':'weak','Nuclear':'resist'},6,persona='Johanna',role='Nuclear • healing • defense buffs'),
    'Noir':unit(144,46,['Psio','Mapsio','One-shot Kill','Riot Gun','Energy Drop','Dekunda'],
                 {'Nuclear':'weak','Psy':'resist'},1,persona='Milady',role='Psy • gun skills • cleansing'),
    'Crow':unit(146,47,['Eiga','Maeiga','Megido','Riot Gun','Debilitate'],
                 {'Bless':'weak','Curse':'null'},5,persona='Loki',role='Curse • Almighty • gun damage'),
    'Violet':unit(137,45,['Kouga','Makouga','Sword Dance','Diarahan','Masukukaja'],
                   {'Curse':'weak','Bless':'null'},6,persona='Cendrillon',role='Bless • critical hits • emergency healing'),
}


def persona(skills, affinity, role):
    return dict(skills=skills,affinity=affinity,role=role)


PERSONAS = {
    'Arsène':persona(['Eiha','Eiga','Cleave','Rakunda','Marakunda','Sukunda'],
                    {'Ice':'weak','Bless':'weak','Curse':'resist'},'Curse • physical • defense debuff'),
    'Jack Frost':persona(['Bufula','Mabufula','Rakunda'],
                        {'Fire':'weak','Ice':'null'},'Ice • defense debuff'),
    'High Pixie':persona(['Zionga','Garula','Diarama','Media','Dormina'],
                        {'Wind':'resist','Nuclear':'weak','Gun':'weak'},'Electric / Wind • recovery • sleep'),
    'Shiki-Ouji':persona(['Psio','Mapsio','Rakukaja','Marakukaja','Tarukaja'],
                        {'Physical':'null','Gun':'null','Bless':'null','Curse':'null','Nuclear':'weak'},'Psy • defensive switch • buffs'),
    'Makami':persona(['Freila','Mafreila','Energy Drop','Dekunda','Rakunda'],
                    {'Electric':'weak','Nuclear':'null','Bless':'resist','Curse':'resist'},'Nuclear • cleansing • defense debuff'),
    'Angel':persona(['Kouga','Makouga','Dia','Rakukaja','Recarm'],
                    {'Bless':'null','Curse':'weak'},'Bless • recovery • revival'),
    'Orthrus':persona(['Agilao','Maragion','Tempest Slash','Rakunda','Dekaja'],
                      {'Ice':'weak','Fire':'drain'},'Fire • physical • buff wipe'),
}


def shadow(hp,sp,skills,affinity=None,behavior='balanced',**extra):
    return unit(hp,sp,skills,affinity,0,behavior=behavior,**extra)


ENEMIES = {
    "Jack-o'-Lantern":shadow(87,28,['Agi','Agilao'],{'Fire':'drain','Ice':'weak','Wind':'weak'},'aggressive'),
    'Pixie':shadow(91,35,['Zio','Dia','Rakunda'],{'Gun':'weak','Ice':'weak','Electric':'resist','Bless':'resist','Curse':'weak'},'support'),
    'Bicorn':shadow(103,28,['Cleave','Tarunda','Garu'],{'Electric':'weak','Curse':'resist'},'aggressive'),
    'Silky':shadow(104,26,['Bufula','Dormina'],{'Fire':'weak','Ice':'resist','Electric':'weak'},'ailment'),
    'Slime':shadow(124,30,['Headbutt','Tarunda'],{'Physical':'resist','Gun':'resist','Fire':'weak','Wind':'weak'},'aggressive'),
    'Black Ooze':shadow(148,37,['Headbutt','Matarunda','Eiga'],{'Physical':'resist','Gun':'resist','Ice':'resist','Electric':'weak','Psy':'weak','Bless':'weak','Curse':'null'},'aggressive'),
    'Oni':shadow(151,24,['Tempest Slash','Cleave','Tarukaja'],{'Physical':'resist','Gun':'resist'},'aggressive'),
    'Nue':shadow(121,42,['Maeiga','Evil Smile','Tempest Slash'],{'Fire':'weak','Ice':'resist','Curse':'null'},'ailment'),
    'Shiki-Ouji':shadow(158,40,['Psio','Mapsio','Tarukaja'],{'Physical':'null','Gun':'null','Bless':'null','Curse':'null','Nuclear':'weak'},'balanced'),
    'Queen Mab':shadow(153,52,['Maragion','Mazionga','Diarama','Marakukaja','Rakunda'],{'Wind':'weak','Fire':'resist','Electric':'resist'},'support'),
    'Arahabaki':shadow(137,49,['Freila','Makajam','Rakunda','Masukunda'],{'Physical':'repel','Gun':'repel','Psy':'weak','Nuclear':'weak','Bless':'resist','Curse':'resist'},'ailment'),
    'Cerberus':shadow(188,44,['Maragion','Agilao','Tempest Slash'],{'Fire':'drain','Ice':'weak','Nuclear':'resist'},'aggressive'),
    'Thor':shadow(215,47,['Mazionga','Zionga','Tempest Slash','Tarukaja'],{'Electric':'null','Psy':'weak','Bless':'resist','Curse':'resist'},'aggressive'),
    'Rangda':shadow(168,55,['Maragion','Eiga','Evil Smile'],{'Physical':'repel','Gun':'repel','Fire':'null','Electric':'weak','Bless':'weak','Curse':'null'},'ailment'),
    'Twin Wardens':shadow(299,89,['Agilao','Bufula','Zionga','Garula','Psio','Freila','Kouga','Eiga','Megidola','Tarunda','Marakukaja','Dekunda'],{},'boss'),
    'The Reaper':shadow(1120,102,[],{},'reaper',no_knockdown=True),
}

ENCOUNTERS = {
    'Castle Downfall':dict(
        description='Warm up on the Castle’s patrol, then break a tougher formation.',
        hint='Spread your affinities. Cover healing, and save at least one elemental item.',
        waves=[["Jack-o'-Lantern",'Pixie','Bicorn'],['Silky','Slime','Oni']]),
    'Bank Lockdown':dict(
        description='Hard-shelled Shadows demand more than brute force. Three waves.',
        hint='Choose Nuclear or Psy coverage and watch for reflected gunfire.',
        waves=[['Black Ooze','Silky'],['Shiki-Ouji','Nue','Queen Mab'],['Arahabaki','Oni']]),
    'Sheriruth Gauntlet':dict(
        description='A deep-Mementos sweep with mixed affinities and aggressive spellcasters.',
        hint='Electric, Ice, Psy and Bless can start chains; rotate Joker’s mask to guard his weak point.',
        waves=[['Rangda','Cerberus','Silky'],['Thor','Arahabaki'],['Cerberus','Thor']],
        between_wave_recovery=(.20,7)),
    'Wardens’ Examination':dict(
        description='A sparring simulation against the Twin Wardens. They deny easy knockdowns.',
        hint='Use Nuclear on the opening defender. The Wardens have no weakness; counter their stat pressure.',
        waves=[['Shiki-Ouji','Silky'],['Twin Wardens','Rangda']],between_wave_recovery=(.25,8)),
    'Reaper Alert':dict(
        description='A single sustained battle. The Reaper changes tactics as its health falls. No reinforcements.',
        hint='Guard when it Concentrates. In later phases favor attack debuffs and recovery before the next blast.',
        waves=[['The Reaper']]),
    'Wild Card: Joker Solo':dict(
        description='Three solo rounds with a recovery break between each. There are no allies or Baton Pass.',
        hint='Guard prevents a weakness knockdown. Switch to a safer mask, and avoid the final Shadow’s reflected shots.',
        waves=[['Silky'],['Shiki-Ouji'],['Arahabaki']],
        between_wave_recovery=(.32,10),party_size=1),
    'Mementos Shuffle':dict(
        description='Three different Shadows are drawn from across Mementos on every deployment.',
        hint='No preview. Bring flexible elements, healing and an answer to repels.',
        waves=[[]],shuffle_count=3),
}
