"""Original ASCII reels: kabuki stage and moonlit highway.

Staging references: recorded Royal gameplay, The Kabuki Kid and Drive Hard:
https://www.lp.zone/t/colors-flying-high-lets-play-persona-5-royal/3971?page=16
https://www.lp.zone/t/colors-flying-high-lets-play-persona-5-royal/3971?page=17
https://www.youtube.com/watch?v=F6BYdZ34KOM (3:51 and 4:53).
"""
from bisect import bisect_right
from math import pi, sin
from wrestling_scene import Canvas, WIDTH

DUSK = 'THE DUEL AT DUSK'
TEA = 'TEA IN THE CROSSHAIRS'
DUEL_BEATS = ((1., '01 / CURTAIN OF PETALS'), (2.1, '02 / FOX DRAWS'),
              (3.35, '03 / THE FLOOR SPLITS'), (4.57, '04 / PANTHER DESCENDS'),
              (5.67, '05 / PARASOL SWEEP'), (6.31, '06 / BEAUTY STRIKES'),
              (8.4, '07 / FINAL BOW'))
TEA_BEATS = ((1., '01 / MIDNIGHT RENDEZVOUS'), (2.12, '02 / MONA TRANSFORMS'),
             (3.43, '03 / NOIR TAKES THE ROOF'), (4.67, '04 / FULL THROTTLE'),
             (5.8, '05 / ROOFTOP SALVO'), (6.62, '06 / BREAK THROUGH'),
             (8.45, '07 / TEA IS SERVED'))

FOX = (
    r'    /|        |\ ',
    r'   / |________| \ ',
    r'  /  _/^^^^\_   \ ',
    r' /  / >    < \   |',
    r' |  \_      _/   |',
    r'  \   \_()_/    /',
    r'   \__/\/\_\___/',
    r'  ////| /\ |\\\\ ',
    r' /___/| \/ |\___\ ',
)
PANTHER = (
    r'    /\.-::::-. /\ ',
    r'   /__\ .--. /__\ ',
    r'  (##(|/====\|)##)',
    r'  (###|\o  o/|###)',
    r' (####/\_v_/\####)',
    r' (##/ _/|Y|\_ \##)',
    r'    \ /|###|\ /',
    r'     V |###| V',
    r'       /___\ ',
)
NOIR = (
    r'          /~~\ ',
    r'    .---_/== /',
    r' __/____(o)_/____',
    r' \_______________/',
    r'   (###/. .\###)',
    r'   (##|  v  |##)',
    r'    \#\___/#/',
    r'     .-}> {<-.',
    r'    /  /o\   \ ',
)
MONA = (
    r'    /|         |\ ',
    r'   / |_.----._.| \ ',
    r'   |/  _______  \|',
    r'  /  / O   O \  \ ',
    r' |  |    v    |  |',
    r'  \  \__\_/__/  /',
    r'   \-._____.-/',
    r'     ==\___/==>',
    r'      /|___|\ ',
)
FOX_HEAD=(r' /|___|\ ', r'<  > <  >', r' \_()_/ ')
PANTHER_HEAD=(r'/\.__./\ ',r'(=/oo\=)',r' ~\v/~ ')
NOIR_HEAD=(r'    /\ ',r'===/__)===',r' {(. .)} ',r'  \_v_/  ')
FOE_HEAD=(r' /\  /\ ',r'<  * *  >',r' \__W__/ ')
FOE_BODY=(r'__/[#]\__',r'  | @ | ',r' _/   \_ ',r'/_/   \_\ ')
FOX_READY=(r' <_/V\___[]',r'  |##|    |',r' _/  \_   |')
FOX_CUT=(r'  _/V_/>======',r' / /##|    ',r'<_/  \___  ')
FOX_BOW=(r' /\_V_/\ ',r'  /##\  ',r' /_/\_\ ')
PANTHER_READY=(r' _/Y\_ ',r'/ |#| \ ',r' _/ \_ ')
PANTHER_DROP=(r'\__Y__/',r'  |#|  ',r' _/ \_ ')
PANTHER_CUT=(r' __Y====',r' /##/   ',r'<_/ \__ ')
NOIR_STAND=(r' _/}>{\_ ',r'   /o\   ',r'  _| |_  ')
NOIR_LEAP=(r'___/}>{\__',r' /_/o\_>  ',r'     \_   ')
NOIR_BRACE=(r' _/}>{\_______',r'/_/ /o\=======>',r'   _/ \_   ')
CAT=(r' /\_/\ ',r'( O O )',r' \_v_/ ',r' =/=/>>',r' (_|_) ')
VAN=(r'    /=================\ ',r' __/  | [ M ] [] | [O] \__',
     r'| []  |         _|______/ |>>',r'|_____*==PHANTOM========O_|',
     r'  \_(*)_/        \_(*)_/')
LITTLE=(r'   /==========\ ',r' _/[] |M| [O]  \_',r'|_____|________O_|',r'  (*)        (*)')
CANOPY=(r'         .-o-.',r'    _.-"" /|\ ""-._',r'  ."    /  |  \    ".',
        r' /_____/___|___\_____\ ',r'    \-.____|____.-/',r'           J')
CLOSING=(r'      _.-o-._',r'  _.-" /|\  \"-._',r' (____/_|_\_____.)',r'         J')
BLOOM=(r'   \  |  /',r' -  \ | /  -',r'>>---*O*---<<',r' -  / | \  -',r'   /  |  \ ')


def _cue(table, elapsed):
    t = max(0., min(elapsed,table[-1][0]))
    k = min(bisect_right(tuple(end for end,_ in table),t),len(table)-1)
    start = table[k-1][0] if k else 0.
    return k,(t-start)/(table[k][0]-start),t


def _center(c,y,text,ink='gold'):
    c.put((WIDTH-len(text))//2,y,text,ink,opaque=True)


def _end_card(c,title,ink):
    w=28
    _center(c,12,'/'+('='*w)+'\\',ink)
    _center(c,13,'|'+title.center(w)+'|','white')
    _center(c,14,'\\'+('='*w)+'/',ink)


def _actor(c,x,y,head,body,ink):
    c.put(x,y,head,'face',opaque=True)
    c.put(x,y+len(head),body,ink,opaque=True)


def _foe(c,x,y,down=False):
    if down:
        c.put(x,y,(r'   ____/\_/\_',r'  /_[#]__*_*__),'), 'foe',opaque=True)
    else:
        _actor(c,x,y,FOE_HEAD,FOE_BODY,'foe')


def _petals(c,t,extra=False):
    tick=int(t*12)
    for i in range(24 if extra else 12):
        x=(i*19+tick*(1+i%2))%WIDTH
        y=(i*11+tick//(2+i%3))%13
        c.put(x,y,'.+*..:'[i%6],'red' if i%3 else 'gold')


def _hall(c,t):
    c.put(0,0,'-'*WIDTH,'rail')
    c.put(0,1,r'\\\        +------------+   +------------+        ///','dim')
    for x in (8,20,35,47):
        c.put(x,2,('|','o','O','o'),'gold')
    for x in (1,14,42,55):
        c.put(x,4,('|',)*6,'dim')
    for y in (4,6,8):
        c.put(2,y,'------------+'+' '*27+'+------------','dim')
    c.put(0,10,'\\'+'_'*54+'/','dim')
    c.put(0,11,r'   /        /       /     :     \       \        \ ','dim')
    c.put(0,12,r'  /        /       /      :      \       \        \ ','rail')
    c.put(0,13,'='*WIDTH,'rail')
    c.put(0,14,r' \_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/','dim')
    _petals(c,t)


def render_duel(elapsed):
    shot,f,t=_cue(DUEL_BEATS,elapsed)
    c=Canvas(); _hall(c,t)
    if shot==0:
        slide=int((1-f)*6)
        c.put(6-slide,3,FOX,'cyan',opaque=True)
        c.put(33+slide,3,PANTHER,'red',opaque=True)
        _center(c,1,'[ KABUKI STAGE / TWILIGHT ]')
        _center(c,12,'< F O X  /  P A N T H E R >','white')
    elif shot==1:
        _foe(c,31,4)
        _actor(c,42,5,PANTHER_HEAD,PANTHER_READY,'red')
        c.put(37,1,CLOSING,'gold',opaque=True)
        _actor(c,9+int(f*12),5,FOX_HEAD,FOX_CUT if f>.6 else FOX_READY,'cyan')
        if f>.57:
            for n in range(9):
                c.put(20+n*2,9-n//3,'/' if n%2 else '*','white')
        _center(c,13,'[ THE BLADE LEAVES THE SHEATH ]','cyan')
    elif shot==2:
        _foe(c,28+int(f*4),3-int(sin(pi*f)*2))
        _actor(c,7+int(f*5),5,FOX_HEAD,FOX_CUT,'cyan')
        _actor(c,43,5,PANTHER_HEAD,PANTHER_READY,'red')
        for i in range(6):
            lift=max(0,int(7*sin(pi*max(0,min(1,f*1.7-i*.13)))))
            c.put(17+i*5,11-lift,(' __',r'/_/\ ',r'\_\/'),'gold' if i%2==0 else 'dim',opaque=True)
        _center(c,13,'[ FLOOR PANELS CASCADE ]')
    elif shot==3:
        _actor(c,8,5,FOX_HEAD,FOX_READY,'cyan')
        _foe(c,49,5)
        x=40-int(f*17); y=int(3-2*sin(pi*f))
        _actor(c,x,y+4,PANTHER_HEAD,PANTHER_DROP,'red')
        c.put(x-8+(int(t*8)%2),max(0,y-1),CANOPY,'red',opaque=True)
        for i in range(5):c.put(x+16+i*2,y+i//2,'>' if i%2 else '.','gold')
        _center(c,13,'[ PANTHER TAKES CENTER STAGE ]','red')
    elif shot==4:
        _actor(c,7,5,FOX_HEAD,FOX_BOW,'cyan')
        x=24+int(f*5)
        _foe(c,40+int(f*5),4)
        _actor(c,x,7,PANTHER_HEAD,PANTHER_CUT,'red')
        c.put(x-6,2,CANOPY if f<.54 else CLOSING,'red',opaque=True)
        for i in range(10):
            c.put(27+i*2,10-int(3*sin(i*pi/9))+int(f*2),'-' if i%3 else '*','white')
        _center(c,13,'[ PARASOL SWEEP ]')
    elif shot==5:
        _foe(c,39,10,True)
        _actor(c,6,6,FOX_HEAD,FOX_BOW,'cyan')
        _actor(c,46,5,PANTHER_HEAD,PANTHER_CUT,'red')
        _petals(c,t,True)
        if f<.7:
            c.put(21,3,BLOOM,'flash',opaque=True)
            for i in range(7):c.put(16+i*4,11-i,'/' if int(t*14)%2 else '+','gold')
        _center(c,13,'[ THE STAGE FALLS SILENT ]','white')
    else:
        _petals(c,t,True)
        c.put(6,3,FOX,'cyan',opaque=True)
        c.put(33,3,PANTHER,'red',opaque=True)
        _center(c,1,'< F O X  /  P A N T H E R >','gold')
        _end_card(c,DUSK,'red')
    return DUEL_BEATS[shot][1],c.finish()


def _road(c,t):
    c.put(0,0,r'\ \           .--------------------------.          / /','rail')
    c.put(0,1,r' \ \    .---"                            "---.     / /','dim')
    c.put(0,2,r'  \ +--"                                      "--+ /','dim')
    c.put(0,4,'+-'+'-'*53+'-+','dim')
    for i in range(8):
        x=(i*13-int(t*27))%64-3
        c.put(x,2,'.o.' if i%2 else '[=]','gold')
        c.put((x*2)%61-2,13,'--' if i%2 else '*---','cyan')
    c.put(int(-t*34)%12-11,11,' ..=== ..=== '*7,'dim')
    c.put(int(-t*45)%16-15,14,'====    =====   '*5,'rail')


def _van(c,x,y,t,small=False):
    c.put(x,y,LITTLE if small else VAN,'cyan',opaque=True)
    if not small:
        for dx in (5,20):c.put(x+dx,y+4,'o' if int(t*16)%2 else '*','face')
        c.put(x+27,y+2,'>>==','gold')


def _burst(c,x,y,f):
    c.put(x-4,y-2,BLOOM,'flash' if f<.43 else 'red',opaque=f<.7)
    for i in range(9):
        dx=round((i-4)*(1+1.7*f));dy=int(sin(i*pi/3)*(1+2*f))
        c.put(x+dx,y+dy,'*' if i%2==0 else '.', 'gold' if f<.70 else 'dim')


def render_tea(elapsed):
    shot,f,t=_cue(TEA_BEATS,elapsed)
    c=Canvas(); _road(c,t)
    if shot==0:
        slide=int((1-f)*6)
        c.put(7-slide,3,NOIR,'noir',opaque=True)
        c.put(33+slide,3,MONA,'cyan',opaque=True)
        _center(c,1,'[ MIDNIGHT / EXPRESSWAY ]')
        _center(c,12,'< N O I R  /  M O N A >','white')
    elif shot==1:
        x=8+int(f*6)
        _foe(c,45,4)
        _actor(c,37,3,NOIR_HEAD,NOIR_STAND,'noir')
        if f<.32:
            c.put(x,6-int(f*4),CAT,'cyan',opaque=True)
            c.put(x-4,11,'--->>','gold')
        elif f<.63:
            c.put(x-3,5,(r'    \   /*',r' --==O==//--',r'    /  \\'), 'flash',opaque=True)
            _van(c,x,8,t,True)
        else:
            _van(c,x,7,t)
        _center(c,13,'[ MONA: VAN FORM ]','white')
    elif shot==2:
        x=8+int(f*10)
        _foe(c,48,4); _van(c,x,8,t)
        y=2-int(2*sin(pi*f))
        _actor(c,x+17-int(f*7),y,NOIR_HEAD,NOIR_LEAP if f<.7 else NOIR_BRACE,'noir')
        c.put(x-6,10,'< < <','white')
        _center(c,13,'[ NOIR: BOARDING ]','noir')
    elif shot==3:
        x=13+int(3*sin(f*pi)); y=8+(int(t*10)%2)
        for i in range(6):c.put((i*9-int(t*34))%57-6,8+i%3,'----','dim')
        _foe(c,47,4); _van(c,x,y,t)
        _actor(c,x+8,y-7,NOIR_HEAD,NOIR_BRACE,'noir')
        _center(c,13,'[ ROOF TEAM / FULL THROTTLE ]','cyan')
    elif shot==4:
        x=9+int(f*6)
        _van(c,x,8,t); _foe(c,47,4)
        _actor(c,x+6-(int(t*14)%2),1,NOIR_HEAD,NOIR_BRACE,'noir')
        for i in range(3):
            p=f*2.8-i*.28
            if 0<=p<=1.1:
                c.put(25+int(p*23),7-i-int(p*2),'~~~~=>*','gold' if i==0 else 'flash')
        if f>.6:_burst(c,46,6,(f-.60)/.40)
        _center(c,13,'[ NOIR: ROOFTOP SALVO ]')
    elif shot==5:
        for i in range(4):
            p=max(0,min(1,f*1.35-i*.105))
            if p:_burst(c,39+i*4,3+i%2*3,p)
        _van(c,16+int(f*15),8,t)
        _actor(c,23+int(f*15),1,NOIR_HEAD,NOIR_BRACE,'noir')
        if f>.3:_foe(c,38+int(f*9),10,True)
        _center(c,13,'[ BREAK THROUGH ]','white')
    else:
        c.put(8,3,NOIR,'noir',opaque=True)
        c.put(34,3,MONA,'cyan',opaque=True)
        c.put(25,7,(' ~  ~ ' if int(f*7)%2 else '  ~ ~ ', ' .---.)',r' \___/'), 'gold',opaque=True)
        _center(c,1,'< N O I R  /  M O N A >','gold')
        _end_card(c,TEA,'cyan')
    return TEA_BEATS[shot][1],c.finish()


SCENES = {DUSK:(DUEL_BEATS[-1][0],render_duel),
          TEA:(TEA_BEATS[-1][0],render_tea)}
