"""SEES late-year roster combat kits and dated Persona awakenings."""
from .persona3_late import when

KITS={
    'Ken':(132,75,'Pierce',('Kouga','Hamaon','Diama','Makouga'),{'Dark':'weak','Light':'null'}),
    'Shinjiro':(207,42,'Strike',('Fatal End','Gigantic Fist','Charge'),{}),
}
SKILLS={
    'Kouga':('hit','Light',55,8,'one',0),
    'Hamaon':('hit','Light',67,12,'one',0),
    'Diama':('heal','',83,6,'ally',0),
    'Makouga':('hit','Light',43,13,'foes',0),
    'Fatal End':('hit','Slash',62,0,'one',12),
    'Gigantic Fist':('hit','Strike',69,0,'one',13),
    'Charge':('buff','attack',0,6,'self',0),
    'Ziodyne':('hit','Electric',75,12,'one',0),
    'Garudyne':('hit','Wind',75,12,'one',0),
    'Bufudyne':('hit','Ice',75,12,'one',0),
    'Deathbound':('hit','Slash',66,0,'foes',13),
    'Mediarama':('heal','',61,12,'team',0),
    'Heat Riser':('buff','all_stats',0,14,'ally',0),
    'Marakunda':('debuff','defense',0,11,'foes',0),
    'Matarunda':('debuff','attack',0,11,'foes',0),
}
THEURGIES={
    'divine':('Divine Retribution','damage','Light',152,'single','Severe Light to one foe, bypassing affinity.'),
    'bleeding':('Bleeding Fury','damage','Strike',159,'single','Severe Strike to one foe, bypassing affinity.'),
}
THEURGY_BY_ALLY={'Ken':'divine','Shinjiro':'bleeding'}
AWAKENINGS={
    'Akihiko':(when(10,5),'Caesar',('Ziodyne',)),
    'Ken':(when(10,6),'Kala-Nemi',()),
    'Yukari':(when(11,5),'Isis',('Garudyne','Mediarama')),
    'Mitsuru':(when(11,18),'Artemisia',('Bufudyne','Marakunda')),
    'Junpei':(when(11,22),'Trismegistus',('Deathbound',)),
    'Aigis':(when(12,30),'Athena',('Heat Riser',)),
}

def evolved(name,day):
    upgrade=AWAKENINGS.get(name)
    return upgrade[1:] if day and upgrade and day>=upgrade[0] else ('',())
