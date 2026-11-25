"""Upper Yabbashah encounter data, intent, and Koromaru's starter kit."""
KOROMARU=(134,64,'Slash',('Eiga','Maeiga','Maragion','Revolution'),{'Light':'weak','Dark':'null','Fire':'resist'})
THEURGY=('Hound of Hades','damage','Dark',150,'single','Severe Dark to one enemy, bypassing affinity.')
SKILLS={
    'Eiga':('hit','Dark',53,8,'one',0),
    'Maeiga':('hit','Dark',41,14,'foes',0),
    'Maragion':('hit','Fire',42,12,'foes',0),
    'Revolution':('buff','crit_boost',0,6,'everyone',0),
}
FOES={
    'iron-dice':('Iron Dice',99,'Strike',25,{'Electric':'weak'},''),
    'wrathful-book':('Wrathful Book',91,'Dark',24,{'Fire':'weak','Dark':'resist'},''),
    'shouting-tiara':('Shouting Tiara',102,'Wind',25,{'Dark':'weak','Electric':'drain'},''),
    'wild-drive':('Wild Drive',118,'Pierce',27,{'Electric':'weak','Slash':'resist','Pierce':'resist','Strike':'resist'},''),
    'venomous-magus':('Venomous Magus',270,'Wind',28,{'Electric':'weak','Fire':'null','Wind':'null'},'venom-magus'),
    'blight-finger':('Five Fingers of Blight',129,'Strike',24,{'Dark':'weak','Fire':'null','Pierce':'resist'},''),
    'bloody-maria':('Bloody Maria',330,'Slash',31,{'Pierce':'weak',**dict.fromkeys(('Fire','Ice','Electric','Wind','Light','Dark'),'null')},'maria'),
    'execution-crown':('Executioner’s Crown',200,'Fire',28,{'Fire':'weak','Wind':'drain','Light':'null'},''),
    'skyscraper':('Imposing Skyscraper',476,'Electric',32,{'Electric':'drain','Pierce':'resist','Wind':'resist'},'skyscraper'),
    'monad-bronze':('Bronze Dice',301,'Light',38,{'Electric':'weak','Slash':'null'},''),
    'monad-tiara':('Muttering Tiara',154,'Dark',33,{'Dark':'weak','Wind':'null'},''),
    'monad-iron':('Iron Dice',311,'Strike',39,{'Ice':'weak','Electric':'null','Light':'null'},''),
    'monad-book':('Silent Book',155,'Wind',33,{'Wind':'weak','Fire':'null'},''),
    'monad-platinum':('Platinum Dice',318,'Strike',40,{'Fire':'resist','Ice':'resist','Pierce':'resist','Light':'null'},''),
    'monad-tiara-b':('Muttering Tiara',150,'Light',32,{'Light':'weak','Electric':'null'},''),
    'monad-book-b':('Silent Book',160,'Dark',33,{'Wind':'weak','Fire':'null'},''),
}
ENCOUNTERS={
    'upper-yabba-patrol':('93F • Yabbashah Patrol',('iron-dice','wrathful-book')),
    'upper-yabba-gallery':('Yabbashah Gallery',('shouting-tiara','wild-drive')),
    'upper-yabba-magus':('99F • Venomous Magus',('venomous-magus','blight-finger','blight-finger')),
    'upper-yabba-maria':('105F • Bloody Maria',('bloody-maria','execution-crown')),
    'upper-yabba-tower':('112F • Imposing Skyscraper',('skyscraper',)),
    'upper-monad-bronze':('117F • Monad Passage I',('monad-bronze','monad-tiara')),
    'upper-monad-iron':('117F • Monad Passage II',('monad-iron','monad-book')),
    'upper-monad-platinum':('117F • Monad Passage III',('monad-platinum','monad-tiara-b','monad-book-b')),
}
ROLES={'venom-magus','maria','skyscraper'}


def threat(b):
    for u in b.enemies:
        if not u.alive:continue
        if u.role=='skyscraper' and b.round%3==2:
            return 'ELECTRIC SURGE / Guard before the tower discharges.'
        if u.role=='maria' and b.round%3==2:
            feared=', '.join(a.label for a in b.allies if a.alive and a.status=='fear')
            if feared:return 'GHASTLY WAIL / Clear Fear: '+feared+'.'
        if u.role=='maria' and b.round%3==1:
            return 'EVIL SMILE / Guard to prevent Fear.'
        if u.role=='venom-magus' and b.round%2:
            return 'VENOMOUS MAGUS / Poison deals damage on your turn.'
    return ''


def enemy_turn(b,u,bonus):
    if bonus or u.role not in ROLES:return None
    living=[v for v in b.allies if v.alive]
    if not living:return False
    if u.role=='skyscraper' and b.round%3==2:
        b._say('Imposing Skyscraper releases an electrical surge.')
        again=False
        for target in living:
            again=b._hit(u,target,'Electric',40,False) or again
            if not b.allies[0].alive:break
        return again
    if u.role=='maria' and b.round%3==1:
        b._say('Bloody Maria uses Evil Smile.')
        targets=sorted(living,key=lambda v:(v.hp/v.max_hp,v.label))[:2]
        for target in targets:
            if target.guard or target.status:continue
            target.status='fear';target.status_until=b.round+1
            b._say(f'{target.label} is afraid.')
        return False
    if u.role=='maria' and b.round%3==2 and any(v.status=='fear' for v in living):
        b._say('Bloody Maria uses Ghastly Wail on frightened allies.')
        for target in living:
            if target.status!='fear':continue
            b._hit(u,target,'Almighty',53,False,ignore_affinity=True)
            target.status='';target.status_until=0
            if not b.allies[0].alive:break
        return False
    if u.role=='venom-magus' and b.round%2:
        b._say('Venomous Magus casts Poison Mist.')
        for target in sorted(living,key=lambda v:-v.hp/v.max_hp)[:2]:
            if target.guard or target.status:continue
            target.status='poison';target.status_until=b.round+2
            b._say(f'{target.label} is poisoned.')
        return False
    return None
