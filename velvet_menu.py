"""Blue prison chrome for the Velvet Room's real campaign interfaces."""
from battle_ui import CYAN, DIM, GOLD, WHITE
from reel_palette import IDS

BLUE = IDS['navy']
STEEL = IDS['slate']


def panel(app, room, heading, footer, *, practice=False):
    """A blue cell frame; body content and input stay with the campaign."""
    left, right, floor = 1, app.w-3, app.h-3
    app.put(1,left,'╔'+'═'*(right-left-1)+'╗',BLUE,True)
    for y in range(2,floor):
        app.put(y,left,'║',BLUE)
        app.put(y,right,'║',BLUE)
        app.put(y,0,'│',STEEL)
        app.put(y,right+1,'│',STEEL)
    app.put(floor,left,'╚'+'═'*(right-left-1)+'╝',BLUE,True)
    room = 'VELVET ROOM / PRACTICE' if practice and not room else 'VELVET ROOM'+(' / '+room if room else '')
    app.put(2,3,' ◈ '+room+' ',CYAN,True,True)
    if app.testing:
        flag='PRACTICE' if practice and room!='VELVET ROOM / PRACTICE' else 'TESTING' if not practice else ''
        if flag:app.put(2,right-2-len(flag),flag,STEEL,True)
    app.put(3,3,'╶'+'─'*(right-5)+'╴',BLUE)
    if heading:app.put(4,3,heading[:right-4],CYAN,True)
    app.mid(app.h-2,footer,CYAN)
    if app.notice:
        app.put(app.h-4,3,app.notice[:right-4],GOLD,True)


def tabs(app, compendium, credits):
    for x, active, name in ((3,not compendium,'FUSION'),(17,compendium,'COMPENDIUM')):
        label=f'[ {name} ]' if active else f'  {name}  '
        app.put(4,x,label,CYAN if active else STEEL,True,active)
    funds=f'{credits:,} cr'
    app.put(4,app.w-6-len(funds),funds,GOLD,True)


def selector(app, items, y, x, width, count, index):
    """Single-row choices. Local navigation rules are the standard menu keys."""
    start=min(max(0,index-count//2),max(0,len(items)-count))
    for i,(title,available) in enumerate(items[start:start+count],start):
        key=str(i+1) if i<9 else ' '
        current=i==index
        label=f'{"◆" if current else " "} {key} {title}'[:width].ljust(width)
        app.put(y+i-start,x,label,CYAN if current else WHITE if available else STEEL,current,current)


def detail_split(app):
    x=min(app.w-32,max(31,round(app.w*.43)))
    app.put(5,3,'─'*(x-5),BLUE)
    app.put(5,x,'┬'+'─'*(app.w-x-5),BLUE)
    for y in range(6,app.h-6):
        app.put(y,x,'│',BLUE)
    return x+2,app.w-x-8
