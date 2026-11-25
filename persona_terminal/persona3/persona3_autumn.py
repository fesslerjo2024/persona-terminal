"""Reload-informed representative Tziah and Lower Harabah floors."""
from datetime import date
from .persona3_thebel import Floor, W

OPENS={'tziah':date(2009,9,10),'tziah_upper':date(2009,10,6),'harabah':date(2009,11,6)}
NAMES={'tziah':'Lower Tziah','tziah_upper':'Upper Tziah','harabah':'Lower Harabah'}

# Start, stairs, pillars, patrol. Formations remain attached to real floors;
# these compact maps are authored for the terminal, not console layouts.
_LAYOUTS=(
    ((2,2),(20,7),((6,2,8,6),(12,4,14,8),(17,2,18,4)),
     ((15,5),(16,5),(17,5),(18,5),(19,5),(19,6),(18,6),(17,6))),
    ((20,8),(2,2),((5,4,8,8),(10,2,13,4),(16,4,17,7)),
     ((15,2),(16,2),(17,2),(18,2),(18,3),(17,3),(16,3),(15,3))),
    ((2,8),(19,2),((4,2,6,5),(8,5,11,8),(14,2,17,6)),
     ((14,7),(15,7),(16,7),(17,7),(18,7),(19,7),(19,6),(19,5))),
    ((19,2),(3,8),((4,3,7,7),(10,2,12,5),(14,5,17,8)),
     ((15,2),(16,2),(17,2),(18,2),(18,3),(17,3),(16,3),(15,3))),
    ((2,5),(20,5),((4,2,6,4),(7,5,10,8),(12,2,15,6),(17,7,20,8)),
     ((16,3),(17,3),(18,3),(19,3),(20,3),(20,4),(19,4),(18,4))),
    ((19,8),(3,2),((4,4,7,8),(9,2,12,5),(14,5,16,8)),
     ((17,3),(18,3),(19,3),(20,3),(20,4),(19,4),(18,4),(17,4))),
)

def _floor(n, encounter, name, mask, layout, guardian='', flip=False):
    start,stairs,pillars,patrol=_LAYOUTS[layout]
    if flip:
        def mirror(pos):return W-1-pos[0],pos[1]
        start,stairs=mirror(start),mirror(stairs)
        pillars=tuple((W-1-x1,y0,W-1-x0,y1) for x0,y0,x1,y1 in pillars)
        patrol=tuple(mirror(p) for p in patrol)
    return Floor(n,encounter,name,mask,pillars,patrol,start,stairs,guardian)


LOWER_TZIAH=(
    _floor(119,'tziah-patrol','GILDED VESTIBULE','Black Frost',4),
    _floor(125,'tziah-125','SAND AND RELIC','Ose',0,'Rampaging Sand and Heartless Relic'),
    _floor(126,'tziah-126','TURRET LANDING','Black Frost',1,'Raging Turret'),
    _floor(132,'tziah-132','TERMINAL TABLE','Ose',2,'Terminal Table',True),
    _floor(136,'tziah-136','AUTHORITY GATE','Black Frost',3,'Jotun of Authority',True),
    _floor(143,'tziah-143','ISOLATED KEEP','Ose',5,'Isolated Castle',True),
)
UPPER_TZIAH=(
    _floor(145,'tziah-high-patrol','GOLDEN CORRIDOR','Kurama Tengu',0,flip=True),
    _floor(151,'tziah-151','DISASTER GATE','Chernobog',2,'Pagoda of Disaster'),
    _floor(155,'tziah-155','DANCING WHEEL','Kurama Tengu',4,'Dancing Beast Wheel',True),
    _floor(161,'tziah-161','KNIGHTS’ CROSSING','Chernobog',1,'Demented Knights',True),
    _floor(170,'tziah-170','SWORD AND SERPENT','Kurama Tengu',5,'Cruel Greatsword'),
    _floor(171,'tziah-171','GIGAS GATE','Chernobog',3,'Invigorated Gigas'),
)
LOWER_HARABAH=(
    _floor(173,'harabah-patrol','BLACK ARCADE','Surt',5),
    _floor(179,'harabah-179','STORM GATE','Daisoujou',3,'Cultist of the Storm'),
    _floor(184,'harabah-184','JUDGMENT GATE','Surt',0,'Merciless Judge and Executive Greatsword'),
    _floor(188,'harabah-188','CHAOS GATE','Daisoujou',2,'Chaos Panzer and Resentful Surveillant',True),
    _floor(193,'harabah-193','NECROMACHINERY GATE','Surt',4,'Necromachinery',True),
)
BLOCKS={
    'tziah':(LOWER_TZIAH,144,(270,370,360,385,420,445)),
    'tziah_upper':(UPPER_TZIAH,172,(315,425,440,455,475,490)),
    'harabah':(LOWER_HARABAH,198,(365,480,510,525,570)),
}
