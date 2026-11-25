"""Original ASCII cels for three Royal-inspired Showtimes.

Reference: gameplay compilation (first three relevant pair timecodes 0:00,
0:35, and 2:40), https://www.youtube.com/watch?v=NzZLv8X2sJA ; gameplay
stills: https://www.lp.zone/t/colors-flying-high-lets-play-persona-5-royal/3971?page=11
and page=13. These are adaptations, not shipped sprites or quoted dialogue.
"""
from bisect import bisect_right
from math import cos, sin, pi
from .wrestling_scene import Canvas

_HERO = {
    'mona': ('cyan', (r' /\_/\ ',r'< O O >',r' \_v_/ ',r'  =~==>'), (
        (r'  / \__',r' _| |_ '), (r'  / >--',r' _| |_ '), (r' __\o/>',r'   /\  '))),
    'panther': ('red', (r' /\_/\  ',r'//[v v]\ ',r'\\_=-_//'), (
        (r'/\ }{ /\ ',r'  /#\  ',r' /   \ ',r'<_   _>'),
        (r'\_}{======>',r'  /#\  ',r' /  _\ ',r'<_     '),
        (r'__}{_//[=]>',r'  /#\   ',r' /   \  ',r'<_   _> '))),
    'skull': ('gold', (r'  .^^^.',r' /[= =]\ ',r' \_W_W_/'), (
        (r'_/[X]\_',r'  |X|  ',r' /   \ ',r'_>   <_'),
        (r'\_[X]========>',r'  |X|  ',r' /   \ ',r'_>   <_'),
        (r'_/X|=====>',r'  /X\    ',r'_/   \_  '))),
    'queen': ('white', (r'  .---.',r' /[===]\ ',r' \_v_v_/'), (
        (r'_/[#]\_',r'  |#|  ',r' /   \ ',r'_|   |_'),
        (r'__/[#]==(O)',r'   |#|    ',r' _/   \_  '),
        (r'_[#]=====(O)',r'  |#|\_(O)',r' _/ \__  '))),
    'fox': ('cyan', (r'  /\  /\ ',r' /<0 0>\ ',r' \__V__/ '), (
        (r' \[<>]/  ',r'  /##\  ',r' /    \ ',r'<_    _>'),
        (r'__\[<>]====>',r'   /##\    ',r' _/    \_  '),
        (r' \\[<>]\\  ',r'   /##\    ',r'  <_  _>   '))),
}
_SHADOW = (r'  /\ /\ ',r' < * * >',r'  \_M_/ ',r'_/[(@)]\_',r'  | @ |  ',r' _/   \_ ')

def _character(c,name,x,y,pose=0,back=False):
    ink,head,poses=_HERO[name]
    rows=head+poses[pose]
    if back:
        swap=str.maketrans('/\\<>[]{}()','\\/><][}{)(')
        w=max(map(len,rows))
        rows=tuple(row.ljust(w)[::-1].translate(swap) for row in rows)
    width=max(map(len,rows))
    for i,row in enumerate(rows):
        c.put(x,y+i,row.ljust(width),'face' if i<len(head) else ink,opaque=True)

def _shot(beats,elapsed):
    ends=tuple(t for t,_ in beats)
    elapsed=min(max(float(elapsed),0.0),ends[-1])
    i=min(bisect_right(ends,elapsed),len(ends)-1)
    start=ends[i-1] if i else 0
    return i,(elapsed-start)/(ends[i]-start),elapsed

def _particles(c,t,seed,count,xmin,xmax,ymin,ymax,ink,chars):
    for i in range(count):
        x=xmin+(i*19+seed+int(t*(2+i%3)))%(xmax-xmin)
        y=ymin+(i*7+seed+int(t*(3+i%2)))%(ymax-ymin)
        c.put(x,y,chars[i%len(chars)],ink)

def _crash(c,x,y,ink='flash'):
    c.put(x,y,(r'       \  |  /',r'  ----- \ | / -----',
               ' >>   [ *#* ]   <<',r'  ----- / | \ -----',r'       /  |  \ '),ink,opaque=True)

def _fallout(c,f,x,y,ink,marks):
    """Throw drifting debris and let it settle into the stage art."""
    for j in range(15):
        rad=f*(3+j%7)
        dx=int(rad*cos((j*11)%29))
        dy=int(rad*sin((j*17)%29)+f*f*5)
        if j%5/5>f-.32:
            c.put(x+dx+j%5,y+dy,marks[j%len(marks)],ink)

_ROSE = ((1.08,'01 / FLOWER FIELD'),(2.12,'02 / MONA OFFERS A ROSE'),
         (3.08,'03 / PANTHER TURNS'),(4.45,'04 / CROSSFIRE'),
         (5.63,'05 / MONA TOSSES THE BOMB'),(6.12,'06 / ROSE BURST'),
         (7.78,'07 / ROSE & REVOLVER'))

def _meadow(c,t):
    c.put(0,4,r"___....--~~--...______...--~~-..___...--~~-...___", 'dim')
    for x in range(0,55,4):
        y=10+(x//4)%2
        c.put(x,y,(r".@.", r"\|/",r"_|_"),'red' if x%8 else 'gold')
    c.put(0,13,'~.~~~..~~....~~~..~~~....~~..~~~~....~~~~..~~...~~~~','green')
    _particles(c,t,23,20,1,56,0,12,'gold',".'+")

def rose(elapsed):
    i,f,t=_shot(_ROSE,elapsed); c=Canvas();_meadow(c,t)
    if i==0:
        _character(c,'mona',3+int(f*6),6+int(f*9)%2)
        _character(c,'panther',34-int(f*5),4+int(f*4)%2,0,True)
        c.put(48-int(f*7),5,_SHADOW,'foe',True)
        c.put(13+int(f*5),8,r'--{@}', 'red')
    elif i==1:
        _character(c,'mona',9+int(f*8),6,1)
        _character(c,'panther',29-int(f*3),4,0,True)
        c.put(19+int(f*7),8,r'---{@}', 'red')
        c.put(41,5,_SHADOW,'foe',True)
    elif i<=3:
        x=30+int(f*3)
        c.put(45+(i==3 and int(f*2)),5,_SHADOW,'foe',True)
        _character(c,'mona',7,6,0)
        y=3+(i==3 and int(f*12)%2)
        _character(c,'panther',x-9,y,1 if i==2 else 2)
        if i==3:
            # Two offset comic muzzle flares, with staggered trails.
            q=int(f*13)
            c.put(x+3,y+3,' *'+('-'*(9+q%5))+'>','flash')
            c.put(x+3,y+4,'  '+('. '*(5+q%3))+'*','gold')
            _particles(c,t,31,17,40,56,2,11,'flash','+.')
    elif i==4:
        _character(c,'panther',27,4,0)
        _character(c,'mona',12+int(f*5),6-int(sin(f*pi)*2),2)
        c.put(46,5,_SHADOW,'foe',True)
        x=22+int(f*26); y=7-int(sin(pi*f)*6)
        c.put(x,y,(" .'","(o)"),'gold',True)
        c.put(x-7,y+1,'. . .','dim')
    elif i==5:
        _character(c,'mona',9,6);_character(c,'panther',20,4)
        _crash(c,33,4)
        _particles(c,t,19,29,34,57,1,12,'red','@*+')
    else:
        _character(c,'mona',9+int(f*5),6-int(sin(pi*f)*2),2 if f<.48 else 0)
        _character(c,'panther',20+int(f*5),4,0, f>.62)
        c.put(42,9,(r' ___.-*.__',r'//_(@)_\_'), 'foe',True)
        _fallout(c,f,43,4,'red','@*+.')
        _particles(c,t,17,15,34,57,4,12,'gold','...*')
        c.put(20+int(f*3),9,'{@}--','red',True)
    return _ROSE[i][1],c.finish()

_ROAD = ((1.06,'01 / DUST ON THE HORIZON'),(2.00,'02 / SKULL WINDS UP'),
         (2.93,'03 / THE HANDOFF'),(4.65,'04 / QUEEN: RAPID-FIRE FISTS'),
         (5.79,'05 / LAST THROUGH THE GUARD'),(6.23,'06 / DUST IMPACT'),
         (7.91,'07 / HIGHWAY TO TROUBLE'))

def _desert(c,t):
    c.put(0,2,r' _/\___     _____     _/\_   ___       _    /\____', 'dim')
    c.put(0,3,r'/      \___/     \___/    \_/   \_____/ \__/      \_', 'dim')
    c.put(0,10,r'___.-____..___--_.._--______..____..._..______..___','gold')
    c.put(4,4, (r'  (+) ',r'   |  ',r' _[+]_',r'   |  ',r' __|__'), 'rail')
    c.put(0,12, '= = = = = = = = = = = = = = = = = = = = = =  =','dim')
    _particles(c,t,9,16,1,55,3,13,'gold','.~')

def road(elapsed):
    i,f,t=_shot(_ROAD,elapsed); c=Canvas();_desert(c,t)
    if i==0:
        _character(c,'skull',7+int(f*5),4+int(f*8)%2,0 if f<.76 else 1)
        _character(c,'queen',2+int(f*3),5,0)
        c.put(48-int(f*9),5,_SHADOW,'foe',True)
        c.put(17+int(f*6),11,'. . ~', 'gold')
    elif i<=2:
        x=12+int(f*(5 if i==1 else 12))
        _character(c,'skull',x,4,0 if i==1 and f<.58 else 1)
        _character(c,'queen',5 if i==1 else 8+int(f*9),4,0)
        c.put(39+(i==2 and int(f*3)),5,_SHADOW,'foe',True)
        if i==2 and f>.42:
            c.put(31+int(f*4),6,'==<*','flash')
    elif i<=4:
        q=20+int(f*(7 if i==3 else 12))
        c.put(40+int(f*6),5,_SHADOW,'foe',True)
        _character(c,'skull',8-int(f*3),5,0)
        _character(c,'queen',q,3 if i==3 else 4,1+int(t*13)%2)
        if i==3:
            # Offset afterimages show the sweep of the fists.
            for n in range(5):
                x=q+10+(n*7+int(t*21))%16
                c.put(x,3+n,'--(O)>' if n%2 else '..(O)', 'flash' if n%2 else 'cyan')
        else:
            c.put(q+11,7,'====(O)>>>','flash')
    elif i==5:
        _character(c,'skull',10,5)
        _character(c,'queen',23,3,2)
        _crash(c,37,4)
        _particles(c,t,7,22,36,57,1,12,'gold','.*-')
    else:
        _character(c,'skull',10+int(f*5),5,1 if f<.4 else 0)
        _character(c,'queen',23+int(f*6),3+int(f*2),2 if f<.35 else 0)
        c.put(43+int(f*4),8,(r' /\____',r'/_/(@)\_'), 'foe',True)
        _fallout(c,f,44,4,'gold','.-*~')
        _particles(c,t,11,12,37,57,7,13,'dim','.~')
    return _ROAD[i][1],c.finish()


_BEEF = ((1.05,'01 / FOX BEEF BOWL'),(2.28,'02 / FOX PLATES THE USUAL'),
         (3.30,'03 / A SHADOW BURSTS IN'),(4.51,'04 / SKULL FIRES BACK'),
         (5.78,'05 / FOX CUTS THE FLYING BOMB'),(6.18,'06 / LAST ORDER'),
         (7.92,'07 / MIDNIGHT TAKEOUT'))

def _bowl(c,x,y,ink='gold'):
    c.put(x,y,(r'  ( )  ',r' ( . ) ',r'\=====/',r' \___/ '),ink,True)

def _shop(c,t,broken=False):
    c.put(0,1,'+'+'-'*55+'+','rail')
    for x in (4,16,28):
        c.put(x,2,('  |  ',r' /-\ ','(===)',r' \_/ '),'red',True)
    for x in (3,36):
        c.put(x,6,'|'+'='*11+'|','dim')
    door=(r'/\ /\ /\ ',r'\ \\// /',r' \\// / ',r' ./ __ .',r'//_ / //',r'/    \\ ') if broken else (
        '+-----+','|     |','|  o  |','|     |','|     |','+-----+')
    c.put(46,3,door,'rail',True)
    c.put(0,10,'_'*56,'rail')
    c.put(0,12,'='*56,'gold')
    c.put(0,13," |[]|  . .  |[]|  . .  |[]|  . .  |[]|  . .  |[]| ",'dim')
    for k in range(4):
        c.put(20+k*3,4-int(t*5+k)%3,'~','dim')

def beef(elapsed):
    i,f,t=_shot(_BEEF,elapsed);c=Canvas();_shop(c,t,i>=2)
    if i==0:
        _character(c,'fox',10,3,0 if f<.5 else 2)
        _character(c,'skull',38-int(f*7),4+int(f*9)%2,0,True)
        _bowl(c,19+int(f*2),6)
        c.put(22+int(f*2),5,'~','white')
    elif i==1:
        _character(c,'fox',10,3)
        _character(c,'skull',31,4,0,True)
        _bowl(c,20+int(f*8),6)
    elif i==2:
        x=46-int(f*10)
        c.put(x,4,_SHADOW,'foe',True)
        _character(c,'fox',8,3)
        _character(c,'skull',27-int(f*4),4)
        _bowl(c,19,7)
        _particles(c,t,4,14,35,57,2,10,'gold','/.*')
    elif i==3:
        _character(c,'fox',8,3)
        x=21+int(f*3)
        _character(c,'skull',x,4+int(t*12)%2,2)
        c.put(41+int(f*3),4,_SHADOW,'foe',True)
        _bowl(c,15,7)
        c.put(x+10,8,'**'+('-'*(5+int(f*7)))+'>','flash')
    elif i==4:
        _character(c,'skull',8,4,2)
        x=12+int(f*20)
        _character(c,'fox',x,4-int(sin(pi*f)*3),1)
        c.put(43,5,_SHADOW,'foe',True)
        if f<.66:
            px=24+int(f*26);py=7-int(sin(pi*f)*4)
            c.put(px,py,"(o)~",'gold',True)
        else:
            for sx,sy in ((38,2),(41,4),(44,6)):
                c.put(sx,sy,'///','flash')
            c.put(47,7,'(*)','gold',True)
    elif i==5:
        _character(c,'skull',7,5)
        _character(c,'fox',17,4,1)
        _crash(c,35,3)
        _particles(c,t,14,22,31,57,1,11,'red','.*+')
    else:
        _character(c,'fox',17+int(f*3),4,1 if f<.32 else 2)
        _character(c,'skull',7+int(f*3),5,0 if f<.66 else 2)
        c.put(44,9,(r' /_.---._',r'/_/(@)\_'), 'foe',True)
        _bowl(c,27-int(f*9),7-int(sin(pi*f)*2))
        _fallout(c,f,45,4,'gold','/.+*')
        _particles(c,t,24,10,30,57,5,12,'dim','~..')
    return _BEEF[i][1],c.finish()

SCENES = {
    'ROSE & REVOLVER': (_ROSE[-1][0],rose),
    'HIGHWAY TO TROUBLE': (_ROAD[-1][0],road),
    'MIDNIGHT TAKEOUT': (_BEEF[-1][0],beef),
}
