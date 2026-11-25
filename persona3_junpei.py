"""An optional, dated Reload-inspired errand. The payoff stays out of menus."""
from datetime import date

INVITATION=date(2009,11,7)
FIRST_SHOP_DAY=date(2009,11,8)
LAST_GIFT_DAY=date(2009,11,21)
PAYOFF_DAY=date(2010,1,21)
PRICE=250
STEPS=('', 'spoken', 'bought', 'given', 'seen')
ACTIVITIES=('junpei','flower-shop','hospital')
PAYOFF=('HOSPITAL VISIT','dorm',(
    'Junpei and Mitsuru lead you to a room at the hospital. Chidori is awake. She doesn’t remember the Dark Hour or the people she met there.',
    'Junpei starts to speak, then simply sits beside her. By the window, a vase of white flowers catches the light.',
))
CONFIRMATION={
    'talk':'Junpei mentions the white flowers she likes.',
    'buy':'You bought the white flowers.',
    'give':'Junpei takes the flowers and decides to visit her.',
}


def valid_record(record):
    flag=record.junpei_flowers
    if type(flag) is not str or flag not in STEPS:return False
    earliest={'spoken':INVITATION,'bought':FIRST_SHOP_DAY,'given':FIRST_SHOP_DAY,'seen':PAYOFF_DAY}
    if flag and record.day<earliest[flag]:return False
    return (record.activity not in ACTIVITIES or
            record.activity=='junpei' and record.day==INVITATION and flag=='spoken' or
            record.activity=='flower-shop' and FIRST_SHOP_DAY<=record.day<=LAST_GIFT_DAY and flag in ('bought','given') or
            record.activity=='hospital' and record.day==PAYOFF_DAY and flag=='seen')


def option(record,evening=False):
    """The single currently relevant choice, or None; no future story hints."""
    if record.phase!='calendar':return None
    flag=record.junpei_flowers
    if evening:
        if flag=='bought' and FIRST_SHOP_DAY<=record.day<=LAST_GIFT_DAY:
            return 'give','Give Junpei the flowers','You can give them to him in the lounge.'
        return None
    if record.activity:return None
    if record.day==INVITATION and not flag:
        return 'talk','Talk with Junpei','Junpei asked if you had time after school.'
    if flag=='spoken' and FIRST_SHOP_DAY<=record.day<=LAST_GIFT_DAY:
        return 'buy','Stop by the flower shop',f'White flowers cost ¥{PRICE}.'
    return None


def payoff_due(record):
    return record.phase=='calendar' and record.day==PAYOFF_DAY and record.junpei_flowers=='given'
