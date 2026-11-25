"""Dates and durable checkpoints for Persona 3 story discoveries."""
from datetime import date

# phase: (date, scene, phase after completion)
CHECKPOINTS={
    'pharos-visit': (date(2009,6,12),'pharos-visit','calendar'),
    'bunker-setup': (date(2009,8,6),'bunker','august'),
    'shinjiro-return': (date(2009,9,3),'shinjiro','calendar'),
    'club-setup': (date(2009,9,5),'club','hermit'),
    'recovered-recording': (date(2009,11,5),'recording','calendar'),
    'medea-aftermath': (date(2009,11,23),'medea','calendar'),
    'bridge-revelation': (date(2009,12,2),'bridge','calendar'),
    'summit-promise': (date(2010,1,31),'promise','finale'),
}
PHASE_FOR_DAY={d:p for p,(d,_,_) in CHECKPOINTS.items() if p!='medea-aftermath'}
EVENT_NAMES={
    date(2009,6,12):'DORM EVENING',
    date(2009,9,3):'DORM BRIEFING',
    date(2009,11,5):'DORM BRIEFING',
    date(2009,12,2):'DORM BRIEFING',
}
