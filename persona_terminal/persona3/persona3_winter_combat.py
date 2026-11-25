"""Terminal-scaled lineups and readable intent for Upper Harabah and Adamah.

Original affinities/lineups: https://aqiu384.github.io/megaten-database/p3r/tartarus
Five-foe formations are staged/condensed to retain the three-foe compact UI.
Only damage affinities are represented; instant-kill immunity is not null damage.
"""

from .persona3_winter import OPENS

PHYSICAL=('Slash','Strike','Pierce')
MAGIC=('Fire','Ice','Electric','Wind','Light','Dark')
SKILLS={
    'Eigaon':('hit','Dark',69,12,'one',0),
    'Herculean Strike':('hit','Strike',48,0,'foes',12),
    'Vile Assault':('hit','Pierce',68,0,'one',13),
    'Diarahan':('heal','',170,16,'ally',0),
    'Megidola':('hit','Almighty',52,18,'foes',0),
}
PERSONAS={
    'Kikuri-Hime':(('Agidyne','Media','Patra','Rakunda'),{'Electric':'weak','Fire':'null'}),
    'Seiryu':(('Bufudyne','Garudyne','Rakukaja'),{'Dark':'weak','Ice':'drain'}),
    'Pazuzu':(('Eigaon','Megidola','Tarunda'),{'Light':'weak','Dark':'repel'}),
    'Koumokuten':(('Herculean Strike','Zionga','Rakukaja'),{'Ice':'weak','Strike':'resist'}),
    'Raphael':(('Vile Assault','Diarahan','Sukukaja'),{'Electric':'weak','Wind':'resist'}),
    'Suzaku':(('Agidyne','Garudyne','Diarahan'),{'Ice':'weak','Fire':'drain'}),
}
PERSONA_LEARNS={'Kikuri-Hime':((21,'Diarahan'),),'Seiryu':((22,'Media'),),
                'Pazuzu':((23,'Rakunda'),),'Koumokuten':((24,'Torrent Shot'),),
                'Raphael':((25,'Kouga'),),'Suzaku':((26,'Maragion'),)}
FUSIONS=(
    ('Kikuri-Hime',('Sati','Kurama Tengu')),
    ('Seiryu',('Black Frost','Yamata-no-Orochi')),
    ('Pazuzu',('Chernobog','Naga')),
    ('Koumokuten',('Ose','Seiryu')),
    ('Raphael',('Daisoujou','Principality')),
    ('Suzaku',('Surt','Kikuri-Hime')),
)
SUMMON_PRICE=dict(zip(PERSONAS,(430,445,475,520,550,565)))
FUSION_DATES={name:OPENS['harabah_upper' if i < 3 else 'adamah']
              for i,name in enumerate(PERSONAS)}

FOES={
    'winter-table':('Angry Table',165,'Fire',30,{'Slash':'weak','Wind':'weak','Ice':'null'},''),
    'winter-seeker':('Fate Seeker',174,'Dark',31,{'Pierce':'weak','Light':'weak','Dark':'repel',**dict.fromkeys(MAGIC[:4],'null')},''),
    'winter-book':('Wrathful Book',175,'Light',32,{'Fire':'weak','Ice':'repel','Light':'drain'},''),
    'winter-perpetual':('Perpetual Sand',176,'Strike',32,{**dict.fromkeys(PHYSICAL,'weak'),**dict.fromkeys(MAGIC,'null')},''),
    'winter-drive':('Slaughter Drive',193,'Strike',34,{'Electric':'weak','Wind':'null'},''),
    'winter-cyclops':('Mad Cyclops',186,'Strike',33,{'Light':'weak',**dict.fromkeys(MAGIC[:4],'resist')},''),
    'winter-lion':('Icebreaker Lion',428,'Ice',38,{'Fire':'weak','Strike':'null','Ice':'null','Dark':'resist'},''),
    'winter-cupid':('Luckless Cupid',183,'Pierce',32,{'Electric':'weak','Fire':'drain','Light':'repel'},''),
    'winter-eldest':('Deadly Eldest Sibling',292,'Dark',36,{'Ice':'drain','Wind':'drain','Dark':'repel'},''),
    'winter-middle':('Blazing Middle Sibling',210,'Fire',32,{'Fire':'repel','Ice':'weak'},''),
    'winter-youngest':('Voltaic Youngest Sibling',209,'Electric',32,{'Electric':'repel','Wind':'weak'},''),
    'winter-dice':('Scornful Dice',512,'Almighty',37,dict.fromkeys(PHYSICAL,'drain'),'winter-scornful'),
    'winter-minotaur':('Minotaur Nulla',584,'Strike',43,{'Strike':'repel','Electric':'null','Light':'resist'},'winter-nulla'),
    'winter-maya':('Bigoted Maya',188,'Dark',34,{'Electric':'null','Light':'weak'},''),
    'winter-raven':('Amenti Raven',196,'Wind',35,{'Pierce':'weak','Dark':'weak','Fire':'repel','Wind':'resist'},''),
    'winter-balance':('Light Balance',201,'Light',34,{'Fire':'weak','Ice':'resist','Electric':'resist','Wind':'weak','Light':'repel','Dark':'repel'},''),
    'winter-death-dice':('Death Dice',198,'Strike',35,{'Fire':'null','Electric':'weak','Wind':'repel','Light':'resist','Dark':'resist'},''),
    'winter-count':('Death Castle',211,'Dark',37,{'Strike':'null','Fire':'null','Electric':'drain','Wind':'weak','Dark':'repel'},''),
    'winter-platinum':('Platinum Dice',202,'Strike',36,{'Slash':'null','Ice':'null','Electric':'weak'},''),
    'winter-sand':('Obsessive Sand',580,'Strike',43,dict.fromkeys(MAGIC,'resist'),''),
    'winter-castle':('Comeback Castle',390,'Strike',41,{'Slash':'repel','Ice':'resist','Electric':'resist'},'winter-comeback'),
    'winter-foot':('Foot Soldier',146,'Slash',34,{'Strike':'resist','Pierce':'repel','Fire':'weak','Ice':'null','Wind':'resist','Light':'drain'},'winter-recruit'),
    'winter-mage':('Mage Soldier',142,'Dark',33,{'Pierce':'weak','Fire':'repel','Electric':'null','Dark':'drain'},'winter-recruit'),
    'winter-overseer':('Overseer of Creation',306,'Light',38,{'Light':'repel','Dark':'repel'},''),
    'winter-noble':('Appropriating Noble',370,'Dark',39,{'Strike':'resist','Ice':'weak','Light':'null'},'winter-appropriating'),
    'winter-serpent':('Invasive Serpent',144,'Pierce',32,{'Strike':'weak','Fire':'drain','Wind':'resist'},'winter-serpent'),
    'winter-judge':('High Judge of Hell',610,'Slash',45,{'Slash':'resist','Strike':'null','Pierce':'resist','Ice':'null','Wind':'null','Dark':'resist'},'winter-judge'),
    'winter-death':('Cultist of Death',612,'Almighty',42,{'Ice':'resist','Electric':'resist','Wind':'weak','Light':'drain','Dark':'drain'},'winter-death'),
    'winter-sinner':('Hedonistic Sinner',307,'Ice',37,{'Slash':'repel','Pierce':'repel','Fire':'null','Electric':'drain'},''),
    'winter-mercenary':('Genocidal Mercenary',685,'Strike',47,{'Slash':'resist','Strike':'repel','Ice':'drain','Electric':'repel','Dark':'repel'},'winter-mercenary'),
    'winter-morbid':('Morbid Book',321,'Dark',39,{'Light':'repel'},''),
    'winter-phantom':('Phantom Master',185,'Ice',33,{'Slash':'null','Pierce':'weak','Ice':'drain','Electric':'resist','Dark':'null'},''),
    'winter-gold':('Gold Hand',342,'Strike',40,{'Slash':'repel','Strike':'repel','Light':'null','Dark':'null'},''),
    'winter-black':('Black Hand',181,'Dark',34,{'Wind':'weak',**dict.fromkeys(('Fire','Ice','Electric','Dark'),'drain')},''),
    'winter-silver':('Silver Hand',183,'Electric',34,{'Strike':'null','Electric':'weak',**dict.fromkeys(('Fire','Ice','Wind'),'drain')},''),
}

ENCOUNTERS={
    'winter-harabah-patrol':('199F • Ember Landing',('winter-table','winter-seeker')),
    'winter-icebreaker':('203F • Icebreaker Lion',('winter-lion','winter-cupid')),
    'winter-harabah-mid':('209F • Fractured Gallery',('winter-book','winter-perpetual')),
    'winter-siblings':('212F • Three Siblings',('winter-eldest','winter-middle','winter-youngest')),
    'winter-scornful':('218F • Scornful Dice',('winter-dice',)),
    'winter-harabah-high':('221F • Upper Ember Gallery',('winter-drive','winter-cyclops')),
    'winter-nulla':('225F • Minotaur Nulla',('winter-minotaur',)),
    'winter-adamah-patrol':('227F • Adamah Landing',('winter-maya','winter-raven')),
    'winter-obsessive':('230F • Obsessive Sand',('winter-sand',)),
    'winter-adamah-mid':('233F • Prism Gallery',('winter-balance','winter-death-dice')),
    'winter-comeback':('236F • Comeback Castle',('winter-castle','winter-foot','winter-mage')),
    'winter-overseers':('241F • Overseers of Creation',('winter-overseer','winter-overseer')),
    'winter-appropriating':('246F • Appropriating Noble',('winter-noble','winter-serpent','winter-serpent')),
    'winter-high-judge':('247F • High Judge of Hell',('winter-judge',)),
    'winter-adamah-high':('250F • Upper Prism Gallery',('winter-count','winter-platinum')),
    'winter-cultist':('253F • Cultist of Death',('winter-death',)),
    'winter-hedonistic':('254F • Hedonistic Sinners',('winter-sinner','winter-sinner')),
    'winter-genocidal':('255F • Genocidal Mercenary',('winter-mercenary',)),
    'winter-monad-book':('225F • Monad Passage I',('winter-morbid','winter-phantom','winter-phantom')),
    'winter-monad-hands':('225F • Monad Passage II',('winter-gold','winter-black','winter-silver')),
}


def _intent(b,u):
    if u.role=='winter-scornful':
        return 'MEGIDOLAON / Guard against Almighty.' if b.round%3==0 else ''
    if u.role=='winter-nulla':
        return 'DEATHBOUND / Guard against a wide Slash attack.' if b.round%3==0 else ''
    if u.role=='winter-comeback':
        return ('REINFORCEMENTS / The Castle can raise its soldiers once.'
                if not getattr(b,'_winter_reinforced',False) else '')
    if u.role=='winter-appropriating':
        return 'SPIRIT DRAIN / Guard Makoto to keep his SP.' if b.round%3==2 and b.allies[0].sp else ''
    if u.role=='winter-judge':
        return 'VORPAL BLADE / Guard against a wide Slash attack.' if b.round%3==2 else ''
    if u.role=='winter-death':
        return 'MEGIDOLAON / Guard against Almighty.' if b.round%3==1 else ''
    if u.role=='winter-mercenary':
        return 'TENTARAFOO / Guard to resist the accuracy penalty.' if b.round%3==2 else ''
    return ''


def threat(b):
    """Read-only and valid before the first enemy round."""
    return next((message for u in b.enemies if u.alive and (message:=_intent(b,u))),'')


def _sweep(b,u,element,power,name):
    b._say(f'{u.label} uses {name}.')
    extra=False
    for ally in b.allies:
        if ally.alive:extra=b._hit(u,ally,element,power,False) or extra
        if not b.allies[0].alive:break
    return extra


def enemy_turn(b,u,bonus):
    """None falls through to engine AI; scripted hits use ordinary combat."""
    if bonus:return None  # Bonus actions cannot immediately repeat a volley.
    if u.role=='winter-scornful':
        if b.round%3==0:return _sweep(b,u,'Almighty',43,'Megidolaon')
        if b.round%3==2:
            b._say('Scornful Dice builds up to Megidolaon.')
            return False
    if u.role=='winter-nulla' and b.round%3==0:
        return _sweep(b,u,'Slash',43,'Deathbound')
    if u.role=='winter-comeback' and not getattr(b,'_winter_reinforced',False):
        recruits=[v for v in b.enemies if v.role=='winter-recruit' and not v.alive]
        if recruits:
            b._winter_reinforced=True
            for v in recruits:
                v.hp=v.max_hp//2
                v.down=False
                v.status='';v.status_until=0
                b.clear_stats(v)
            b._say('Comeback Castle calls in reserve soldiers.')
            return False
    if u.role=='winter-appropriating' and b.round%3==2 and b.allies[0].sp:
        makoto=b.allies[0]
        spent=min(makoto.sp,4 if makoto.guard else 14)
        makoto.sp-=spent
        b._say(f'Appropriating Noble drains {spent} SP from {makoto.label}.')
        return False
    if u.role=='winter-serpent' and b.round%3==2:
        living=[a for a in b.allies if a.alive and not a.guard and not a.status]
        if living:
            target=max(living,key=lambda a:a.hp/a.max_hp)
            target.status='poison';target.status_until=b.round+1
            b._say(f'{u.label} poisons {target.label}.')
            return False
    if u.role=='winter-judge' and b.round%3==2:
        return _sweep(b,u,'Slash',56,'Vorpal Blade')
    if u.role=='winter-death' and b.round%3==1:
        return _sweep(b,u,'Almighty',49,'Megidolaon')
    if u.role=='winter-mercenary' and b.round%3==2:
        b._say('Genocidal Mercenary uses Tentarafoo.')
        for ally in b.allies:
            if ally.alive and not ally.guard:
                b.modify_stat(ally,'agility',max(-2,ally.agility-1))
        return False
    return None
