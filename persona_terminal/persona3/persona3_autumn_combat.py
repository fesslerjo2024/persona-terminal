"""Tziah and Lower Harabah formations and tactical behavior at terminal scale."""

FOES={
    'fall-maya':('Ill-Fated Maya',178,'Fire',29,{'Slash':'weak','Fire':'weak'},''),
    'fall-sigil':('Blue Sigil',210,'Ice',32,{'Strike':'weak','Ice':'drain'},''),
    'fall-growth':('Growth Relic',219,'Wind',31,{'Strike':'weak','Wind':'drain'},''),
    'fall-idol':('Liberating Idol',201,'Ice',34,{'Electric':'weak','Ice':'repel'},''),
    'fall-twins':('Crazy Twins',226,'Electric',33,{'Dark':'weak','Electric':'repel'},''),
    'fall-turret':('Scarlet Turret',250,'Fire',36,{'Electric':'weak','Slash':'repel','Strike':'null','Fire':'resist'},''),
    'fall-rampaging':('Rampaging Sand',262,'Fire',34,{'Strike':'weak',**dict.fromkeys(('Fire','Ice','Electric','Wind'),'resist')},''),
    'fall-heartless':('Heartless Relic',368,'Electric',36,{'Electric':'weak','Light':'resist','Dark':'resist'},''),
    'fall-raging':('Raging Turret',520,'Pierce',35,{'Slash':'null','Wind':'weak'},'fall-turret-charge'),
    'fall-terminal':('Terminal Table',555,'Fire',35,{'Strike':'null','Light':'drain'},'fall-table'),
    'fall-jotun':('Jotun of Authority',450,'Slash',36,{'Slash':'drain','Ice':'weak','Fire':'null'},''),
    'fall-purging':('Purging Right Hand',245,'Electric',32,{'Strike':'drain','Electric':'weak','Dark':'repel'},'fall-right'),
    'fall-subservient':('Subservient Left Hand',240,'Fire',32,{'Pierce':'drain','Fire':'weak','Light':'repel'},'fall-left'),
    'fall-isolated':('Isolated Castle',602,'Strike',37,dict.fromkeys(('Fire','Ice','Electric','Wind','Light','Dark'),'null'),'fall-castle'),
    'fall-persecution':('Tome of Persecution',262,'Ice',34,{'Ice':'drain'},'fall-tome'),
    'fall-pagoda':('Pagoda of Disaster',444,'Wind',39,{'Strike':'weak','Electric':'drain','Wind':'drain'},''),
    'fall-wheel':('Dancing Beast Wheel',650,'Strike',42,{'Ice':'null','Light':'resist'},'fall-wheel-charge'),
    'fall-knight':('Demented Knight',358,'Pierce',39,{'Pierce':'null','Fire':'null','Wind':'weak'},''),
    'fall-serpent':('Serpent of Absurdity',274,'Fire',36,{'Fire':'drain','Ice':'weak'},'fall-tome'),
    'fall-sword':('Cruel Greatsword',421,'Slash',42,{'Slash':'null','Light':'weak','Dark':'null'},''),
    'fall-gigas':('Invigorated Gigas',748,'Strike',43,{'Ice':'resist','Light':'null','Dark':'null'},'fall-gigas-charge'),
    'fall-cultist':('Cultist of the Storm',685,'Wind',41,{'Strike':'null','Fire':'resist','Dark':'weak'},'fall-storm'),
    'fall-executive':('Executive Greatsword',302,'Slash',41,{'Fire':'weak','Electric':'drain','Light':'repel'},''),
    'fall-judge':('Merciless Judge',460,'Ice',42,{'Slash':'null','Strike':'null','Ice':'null','Electric':'resist'},'fall-judge'),
    'fall-surveillant':('Resentful Surveillant',276,'Electric',36,{'Slash':'weak','Electric':'resist','Dark':'null'},'fall-watch'),
    'fall-panzer':('Chaos Panzer',626,'Pierce',44,{'Fire':'null','Wind':'null','Light':'repel'},'fall-panzer-charge'),
    'fall-necro':('Necromachinery',820,'Light',44,{'Slash':'null','Ice':'null','Light':'repel'},'fall-necro-charge'),
}

ENCOUNTERS={
    'tziah-patrol':('Tziah • Gilded Patrol',('fall-maya','fall-sigil')),
    'tziah-125':('125F • Rampaging Sand and Heartless Relic',('fall-heartless','fall-rampaging','fall-rampaging')),
    'tziah-126':('126F • Raging Turret',('fall-raging',)),
    'tziah-132':('132F • Terminal Table',('fall-terminal',)),
    'tziah-136':('136F • Jotun of Authority',('fall-jotun','fall-purging','fall-subservient')),
    'tziah-143':('143F • Isolated Castle',('fall-isolated',)),
    'tziah-high-patrol':('Tziah • Royal Patrol',('fall-growth','fall-idol')),
    'tziah-151':('151F • Pagoda of Disaster',('fall-pagoda','fall-persecution','fall-persecution')),
    'tziah-155':('155F • Dancing Beast Wheel',('fall-wheel',)),
    'tziah-161':('161F • Demented Knights',('fall-knight','fall-knight')),
    'tziah-170':('170F • Cruel Greatsword',('fall-sword','fall-serpent','fall-serpent')),
    'tziah-171':('171F • Invigorated Gigas',('fall-gigas',)),
    'harabah-patrol':('Harabah • Lower Patrol',('fall-twins','fall-turret')),
    'harabah-179':('179F • Cultist of the Storm',('fall-cultist',)),
    'harabah-184':('184F • Merciless Judge',('fall-judge','fall-executive')),
    'harabah-188':('188F • Chaos Panzer',('fall-panzer','fall-surveillant','fall-surveillant')),
    'harabah-193':('193F • Necromachinery',('fall-necro',)),
}
REPLAY_ENCOUNTERS={'tziah':'tziah-patrol','tziah_upper':'tziah-high-patrol','harabah':'harabah-patrol'}

PERSONAS={
    'Black Frost':(('Bufula','Mabufu','Eiga'),{'Light':'weak','Ice':'drain','Fire':'resist','Dark':'resist'}),
    'Ose':(('Tempest Slash','Sonic Punch','Tarukaja'),{'Light':'weak','Slash':'resist','Dark':'resist'}),
    'Kurama Tengu':(('Garula','Magarula','Sukukaja'),{'Electric':'weak','Wind':'null'}),
    'Chernobog':(('Eiga','Maeiga','Tempest Slash'),{'Fire':'weak','Dark':'null'}),
    'Surt':(('Agidyne','Maragion','Tarunda'),{'Ice':'weak','Fire':'drain'}),
    'Daisoujou':(('Kouga','Makouga','Diarama'),{'Dark':'weak','Light':'null'}),
}
SKILLS={
    'Bufula':('hit','Ice',53,8,'one',0),
    'Tempest Slash':('hit','Slash',58,0,'one',12),
    'Garula':('hit','Wind',54,8,'one',0),
    'Magarula':('hit','Wind',41,13,'foes',0),
    'Agidyne':('hit','Fire',73,12,'one',0),
    'Makouga':('hit','Light',48,14,'foes',0),
    'Bufudyne':('hit','Ice',70,12,'one',0),
    'Garudyne':('hit','Wind',69,12,'one',0),
}
PERSONA_LEARNS={'Black Frost':((16,'Bufudyne'),),'Kurama Tengu':((17,'Garudyne'),),
                'Ose':((16,'Rakukaja'),),'Chernobog':((17,'Rakunda'),),
                'Surt':((18,'Matarukaja'),),'Daisoujou':((18,'Media'),)}
FUSIONS=(('Black Frost',('Jack Frost','Jack O\'Lantern')),('Ose',('Rakshasa','Valkyrie')),
         ('Kurama Tengu',('Ose','Angel')),('Chernobog',('Pale Rider','Naga')),
         ('Surt',('Chernobog','Sati')),('Daisoujou',('Principality','Kurama Tengu')))
SUMMON_PRICE=dict(zip(PERSONAS,(280,290,315,330,370,385)))

# This is an adaptation of the bosses' telegraphed burst/support patterns:
# normal weakness/Guard rules still matter. Guard protects against the burst.
BURSTS={
    'fall-turret-charge':('AIMED VOLLEY','Pierce',53,3,2),
    'fall-wheel-charge':('WHEEL IMPACT','Strike',56,3,2),
    'fall-gigas-charge':('HERCULEAN STRIKE','Strike',63,4,3),
    'fall-panzer-charge':('CANNON VOLLEY','Pierce',60,3,2),
    'fall-necro-charge':('MEGIDOLAON','Almighty',62,3,2),
    'fall-storm':('STORM FRONT','Wind',58,3,2),
}
SUPPORT={'fall-right','fall-left','fall-tome','fall-watch'}
TACTICS=SUPPORT|set(BURSTS)|{'fall-table','fall-castle','fall-judge'}


def threat(b):
    for u in b.enemies:
        if not u.alive:continue
        beat=BURSTS.get(u.role)
        if beat and b.round%beat[3]==beat[4]:
            return f'{beat[0]} / Guard against the sweep.'
        if u.role=='fall-judge' and b.round%2==0:
            return 'ICE VERDICT / Guard or change vulnerable Personas.'
        if u.role=='fall-table' and b.round%3==2:
            return 'TERMINAL TABLE / Brace for waves of Fire.'
        if u.role in SUPPORT and b.round%2==0 and len([x for x in b.enemies if x.alive])>1:
            return f'{u.label} is preparing support.'
    return ''


def enemy_turn(b,u,bonus):
    if u.role not in TACTICS:return None
    living=[v for v in b.allies if v.alive]
    if not living:return False
    if u.role=='fall-judge':
        # Do not let a first Ice weakness become a second unannounced Ice hit.
        # An odd turn and any One More use an ordinary weapon strike.
        if bonus or b.round%2:
            target=min(living,key=lambda v:(v.hp/v.max_hp,v.label))
            return b._hit(u,target,'Pierce',33)
        b._say('Merciless Judge uses Mabufudyne.')
        again=False
        for target in living:
            again=b._hit(u,target,'Ice',42,False) or again
            if not b.allies[0].alive:break
        return again
    if bonus and u.role=='fall-necro-charge':
        target=min(living,key=lambda v:(v.hp/v.max_hp,v.label))
        return b._hit(u,target,'Strike',33,False)
    if bonus:return None
    beat=BURSTS.get(u.role)
    if beat:
        title,element,power,period,release=beat
        if b.round%period==release:
            b._say(f'{u.label} unleashes {title.lower()}.')
            again=False
            for target in living:
                again=b._hit(u,target,element,power,False,ignore_affinity=element=='Almighty') or again
                if not b.allies[0].alive:break
            return again
    if u.role=='fall-table' and b.round%3==2:
        b._say('Terminal Table releases a wave of fire.')
        for t in living:
            b._hit(u,t,'Fire',45,False)
            if not b.allies[0].alive:break
        return False
    if u.role in SUPPORT and b.round%2==0:
        primary=b.enemies[0]
        if primary is not u and primary.alive:
            if u.role in ('fall-left','fall-tome') and primary.hp<=primary.max_hp-48:
                primary.hp+=48
                b._say(f'{u.label} restores 48 HP to {primary.label}.')
                return False
            if u.role in ('fall-right','fall-watch') and primary.defense<1:
                b.modify_stat(primary,'defense',1)
                b._say(f'{u.label} raises {primary.label}’s defense.')
                return False
    if u.role=='fall-castle' and b.round%3==2:
        target=min(living,key=lambda a:(a.defense,a.hp/a.max_hp))
        if not target.guard and target.defense>=0:
            b.modify_stat(target,'defense',-1)
            b._say(f'{u.label} breaks {target.label}’s defense.')
            return False
    return None
