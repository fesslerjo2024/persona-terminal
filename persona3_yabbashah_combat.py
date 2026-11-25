"""Authored Lower Yabbashah battle formations at terminal scale."""
FOES={
 'lustful-snake':('Lustful Snake',145,'Wind',26,{'Ice':'weak','Wind':'drain'},''),
 'creation-relic':('Creation Relic',158,'Strike',29,{'Strike':'weak','Pierce':'weak','Ice':'resist','Electric':'resist','Wind':'null'},''),
 'ochlocratic-sand':('Ochlocratic Sand',207,'Fire',30,{'Ice':'weak','Fire':'repel'},''),
 'heat-overseer':('Heat Overseer',131,'Fire',29,{'Electric':'weak','Wind':'weak','Fire':'drain','Ice':'drain'},''),
 'sky-overseer':('Sky Overseer',128,'Wind',29,{'Fire':'weak','Ice':'weak','Electric':'drain','Wind':'drain'},''),
 'arcanist-decapitator':('Arcanist Decapitator',334,'Slash',38,{'Ice':'null','Wind':'null'},''),
 'deviant-convict':('Deviant Convict',348,'Strike',40,{},''),
 'tome-atriohy':('Tome of Atrophy',164,'Wind',29,{'Fire':'weak','Electric':'null'},''),
 'controlling-partner':('Controlling Partner',350,'Electric',37,{'Slash':'null','Strike':'null','Light':'null','Dark':'null'},''),
 'dependent-partner':('Dependent Partner',229,'Pierce',36,{'Pierce':'weak','Fire':'null','Ice':'null','Electric':'null','Wind':'null','Light':'null','Dark':'null'},''),
 'elegant-mother':('Elegant Mother',310,'Dark',39,{'Fire':'weak','Wind':'resist'},''),
 'monad-coward':('Cowardly Maya',326,'Dark',38,{},''),
 'monad-shouting':('Shouting Tiara',151,'Wind',29,{'Strike':'weak','Fire':'null'},''),
 'monad-magical':('Magical Magus',140,'Electric',29,{'Fire':'resist','Ice':'resist','Electric':'resist','Wind':'resist','Light':'resist','Dark':'resist'},''),
 'monad-rampage':('Rampage Drive',203,'Strike',38,{'Slash':'resist','Strike':'resist','Pierce':'resist'},''),
}
ENCOUNTERS={
 'yabba-patrol':('Lower Yabbashah Patrol',('lustful-snake','creation-relic')),
 'yabba-77':('Ochlocratic Sands • 77F',('ochlocratic-sand',)*3),
 'yabba-82':('Arcanist Decapitator • 82F',('arcanist-decapitator','heat-overseer','sky-overseer')),
 'yabba-90':('Deviant Convict • 90F',('deviant-convict','tome-atriohy')),
 'yabba-91':('Yabbashah Partners • 91F',('controlling-partner','dependent-partner')),
 'monad-door':('Monad Door • 80F',('elegant-mother',)),
 'monad-passage-maya':('Monad Passage • 91F',('monad-coward',)),
 'monad-passage-guard':('Monad Passage • Inner Guard',('monad-shouting','monad-magical','monad-rampage')),
}
PERSONAS={
 'Rakshasa':(('Cleave','Zan-ei','Marakukaja'),{'Light':'weak','Slash':'resist'}),
 'Yamata-no-Orochi':(('Bufu','Mabufu','Marakukaja'),{'Fire':'weak','Ice':'null'}),
 'Pale Rider':(('Eiha','Garu','Zan-ei'),{'Light':'weak','Dark':'null'}),
}
SKILLS={
 'Zan-ei':('hit','Slash',49,0,'one',10),
}
