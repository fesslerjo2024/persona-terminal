"""Full-viewport, hand-drawn ringside cels for Queen and Noir."""
from bisect import bisect_right
from math import cos, pi, sin

from wrestling_scene import ACTION, BEATS, BODIES, ENDS, HEADS, SECONDS
from wide_canvas import Canvas

# These are additional hand-drawn cels, not expanded copies of the small set.
# The full-size Queen has a visor, rivets, and armored greaves; Noir has a
# wide brim, curls, a bow, and flared boots. Head ink stays constant in motion.
_HEAD = {
    'queen': (r'    .--------.   ',r'   / /// /////\  ',r'  | [========]|  ',r'   \_==[]==__/  '),
    'noir':  (r'       _/\       ',r'     _/___)_     ',r'  ==\________)== ',r'    {(o . o)}    ',r'    ~\__v__/~    '),
    'foe':   (r'   /\___/\      ',r'  /   ^ ^ \     ',r' < [ * * ] >    ',r'  \__\_/_/     '),
}
_REST = {
    'queen': (r' __/^|[#]|^\__ ',r'/___\|#.#|/___\ ',r'  [] |###| []  ',r'     /##\     ',
              r'    /_/\_\    ',r'   _| |  | |_  ',r'  |___|  |___| '),
    'noir':  (r'  _/\}>  <{/\_ ',r' /__/  \/  \__\ ',r'    \  ()  /   ',r'     /|##|\    ',
              r'    /      \   ',r'   <__/\__>   ',r'   /_/  \_\   '),
    'foe':   (r'  /\__[@]__/\  ',r' /__\[===]/__\ ',r'   / | @ | \   ',r'     |___|     ',
              r'    /|   |\    ',r'   _||   ||_   ',r'  /__|   |__\  '),
}
_MOVE = {
    ('queen','run'): (
        r'  __/^|[#]|^\==>',r' /___\|#.#|  >>>',r'     |###|    ',r'     /##\     ',
        r'  __/ /  \_   ',r' <___/   _/|  ',r'        |__|  '),
    ('queen','strike'): (
        r' __/^|[#]|^\==============>',r'/___\|#.#|=================>',r'  [] |###|                 ',
        r'     /##\     ',r' ___/ |  \____',r'<_____/  |____>'),
    ('queen','climb'): (
        r' \___^[###]^___/ ',r'  \_\|#.#|/_/  ',r'      |###|     ',r'      /##\___ ',
        r'     _|   ___>',r'    |____/    '),
    ('queen','dive'): (
        r'\====^|[#]|^====/',r' \___\|#.#|/___/',r'      |###|       ',r'       /#\       ',
        r'      /___\      ',r'      |_ _|      '),
    ('queen','victory'): (
        r'\_|\__^[#]^__/|_/',r' \_\\|#.#|//_/',r'      |###|     ',r'      /###\    ',
        r'      /   \    ',r'     _|   |_   ',r'    |__| |__| '),
    ('noir','run'): (
        r'   /\}>  <{/\=>',r'  /__/ \/  \__\ ',r'     \ () /   ',r'      /##|    ',
        r' _____/  \_  ',r'<____/    \_ '),
    ('noir','kick'): (
        r'         _/\}>  <{\__ ',r'    ____/__\/__/  \_\ ',
        r'>>=<___/__ /()|\____ ',r'>>=<______/ ##\___/ ',r'              \__> ',
        r'                 \_\ '),
    ('noir','climb'): (
        r' \___}>  <{___/ ',r'  \_\  \/  /_/ ',r'     \ () /    ',r'      /##\___ ',
        r'     _|   ___>',r'    <__/\/    '),
    ('noir','dive'): (
        r'\====}>  <{====/',r' \__\  \/  /__/',r'     \ () /    ',r'      /##\    ',
        r'     /____\   ',r'       /\     '),
    ('noir','victory'): (
        r' \___}>  <{___/ ',r'  \_\  \/  /_/  ',r'     \ () /     ',r'      /##\     ',
        r'     /____\    ',r'     <_/\_>    '),
}
_DOWN = (r'      _/\_ ___          ',r'--<*_/__\/[@]\____*>--- ',r'  __/________________\_ ')
_MIRROR = str.maketrans('/\\<>[]{}()','\\/><][}{)(')


def _cel(c, width, x, feet, who, pose='ready', mirror=False, large=False):
    if large:
        head, body = _HEAD[who], _MOVE.get((who,pose),_REST[who])
    else:
        head = HEADS[who]
        body = ACTION.get(who,{}).get(pose,BODIES[who])
    rows = head+body
    size=max(map(len,head+_REST[who])) if large else max(map(len,head+BODIES[who]))
    # Attack poses may reach beyond the neutral body's footprint.
    x=x-size//2
    if mirror:
        span=max(map(len,rows))
        x-=span-size
        rows=tuple(r.ljust(span)[::-1].translate(_MIRROR) for r in rows)
    for i,row in enumerate(rows):
        c.put(x,feet-len(rows)+1+i,row,'face' if i<len(head) else who,opaque=True)


def _arena(c,w,h,t,floor,back,far,near,impact):
    mid=w//2; last=w-1; tier=max(2,back-1)
    # Ceiling rig and angled spotlights; the square belongs to the *ring*,
    # not to the window. The hall runs continuously under it toward all edges.
    c.put(0,0,('/=\\='*((w+3)//4))[:w],'wine')
    c.put(0,1,('- -- '*((w+4)//5))[:w],'violet')
    for x,aim in ((w//7,w//3),(w//3,w//5),(w*2//3,w*4//5),(w*6//7,w*2//3)):
        lamp='rose' if x<mid else 'teal'
        c.put(x-2,2,'[=]',lamp,True)
        c.line(x,3,aim,tier-1,lamp)
        c.line(x+2,3,min(last,aim+w//14),tier-1,'slate')
        if (int(t*10)+x)%23<4:
            c.put(x-1,3,'+*','face')
    # Distinct tiers of heads, benches, raised arms and changing camera glints.
    for y in range(4,back+2):
        row=''.join('o' if (x*11+y*19)%31 in (1,8,17)
                    else '.' if (x*7+y*13)%13<3
                    else '/' if (x*13+y*3)%49==5 else ' ' for x in range(w))
        c.put(0,y,row,('navy','violet','wine')[(y//2)%3])
        if y%3==0:
            for x in range((y*7)%13,w,18):
                c.put(x,y,'[ ]','violet' if (x+y)%5 else 'amber')
    phase=int(t*8)
    for j in range(8):
        x=(j*31+17)%w; y=4+((j*11+phase//7)%max(1,tier-4))
        if (j*5+phase)%11 < (6 if impact else 2):
            c.put(x,y,'+' if j%2 else '*','face')
    # Raised trapezoid, distant ropes and turnbuckle pads.
    for y in range(back,floor+1):
        f=(y-back)/max(1,floor-back)
        l=round(far+(near-far)*f)
        r=last-l
        c.put(l,y,' '*(r-l+1),'dim',True)
        c.put(l,y,'/' + ('. ' * ((r-l)//2))[:max(0,r-l-1)] + '\\','navy')
    for k in (1,3,5):
        y=back-k
        c.line(far,y,last-far,y,'teal' if k==3 else 'violet','=')
        c.put(far-2,y,'[O]','rail',True)
        c.put(last-far,y,'[O]','rail',True)
        c.line(far,y,near, min(floor,y+(floor-back)),'slate')
        c.line(last-far,y,last-near,min(floor,y+(floor-back)),'slate')
    for x in (far-1,last-far+1):
        c.line(x,back-6,x,back+1,'rail','|')
        for k in (1,3,5):
            c.put(x,back-k,'O','face')
    c.line(near,floor,last-near,floor,'rail','=')
    for y in range(floor+1,h):
        # Striped cloth and a staggered audience at bottom corners.
        l=max(0,near-(y-floor)//2)
        r=last-l
        fabric=''.join('/' if (x+y*2)%7 in (0,1) else '.' if (x+2*y)%9==4
                       else '-' if y==h-1 else ' ' for x in range(r-l+1))
        c.put(l,y,fabric,'wine' if y%2 else 'rose',True)
        for x in (l,min(last,r)):
            c.put(x,y,'|' if y<h-1 else '+','face')
    for x in (near,last-near):
        c.line(x,floor-2,x,min(h-1,floor+2),'rail','|')
        c.put(x,floor,'O','face')
    if h-floor>5:
        for x in (w//4,mid,w*3//4):
            c.put(x-3,floor+3,(r'  /^\  ',r' < + > ',r'  \/  '),'violet',True)


def _burst(c,x,y,f,reach):
    rings=max(1,int(reach*(.3+f*.75)))
    for k in range(12):
        a=k*pi/6
        dx=round(cos(a)*rings)
        dy=round(sin(a)*rings*.55)
        c.line(x+round(dx*.48),y+round(dy*.48),x+dx,y+dy,'flash')
        c.put(x+dx,y+dy,'*' if k%3 else '+','face')
    c.put(x-3,y,'< *#* >','flash',True)


def _debris(c,x,y,f,t,amount=20):
    for j in range(amount):
        if f>.9 and j%4==0:continue
        radius=(.18+f)*((j%10)+2)
        a=(j*13)%37*pi/18
        xx=round(x+radius*cos(a)*2.4)
        yy=round(y+radius*sin(a)*.65+f*f*3)
        c.put(xx,yy,'.' if (j+int(t*20))%3 else '*','dim' if j%3 else 'flash')


def render(elapsed,width,height):
    """Return a label for caller metadata and a width x height array of runs."""
    w,h=max(1,int(width)),max(1,int(height))
    t=min(max(float(elapsed),0.),SECONDS)
    i=min(bisect_right(ENDS,t),len(BEATS)-1)
    start=ENDS[i-1] if i else 0.
    f=(t-start)/(ENDS[i]-start)
    floor=round(h*.79);back=round(h*.44); center=w//2
    far,near=round(w*.17),max(1,round(w*.055))
    c=Canvas(w,h)
    _arena(c,w,h,t,floor,back,far,near,i in (5,6))
    large=w>=78 and h>=30
    def s(who,x,feet=floor-1,pose='ready',mirror=False):
        _cel(c,w,round(x*w),feet,who,pose,mirror,large)
    def down(x=.50):
        line=_DOWN if large else (r'--<*_[(@)]_*>--',)
        c.put(round(x*w)-len(line[-1])//2,floor-len(line),line,'foe',True)

    if i<=1:
        g=f*.72 if i==0 else .72+f*.28
        s('foe',.50)
        s('queen',.16+.065*g,floor-1-int(t*9)%2,'run' if int(t*9)%2 else 'ready')
        s('noir',.84-.065*g,floor-1-int(t*8)%2,'run' if int(t*8)%2 else 'ready',True)
        c.put(center-3,3,('  _o_  ',' /___\\ ','   *   '),'gold',True)
        if i==1:
            for j in range(1,4):
                r=j*max(3,w//16)+round(f*6)
                c.put(center-r,4,'((', 'flash')
                c.put(center+r,4,'))', 'flash')
    elif i==2:
        s('foe',.50+max(0,f-.54)*.17,floor-1-int(max(0,f-.50)*5),'ready',f>.62)
        s('noir',.775,mirror=True)
        x=.225+min(1,f*1.48)*.17
        c.put(round(x*w)-w//12,floor-3,'..-->>','queen')
        s('queen',x,pose='strike' if f>.43 else 'run')
        if f>.58:_burst(c,round(w*.52),floor-(8 if large else 5),(f-.58)/.42,max(4,w//13))
    elif i==3:
        s('queen',.22)
        s('foe',.56-max(0,f-.44)*.40,floor-1-round(max(0,f-.50)*4))
        x=.775-min(1,f*1.72)*.17
        y=floor-1-round(sin(f*pi)*h*.21)
        c.put(round(x*w)+w//18,y-3,'<<--..','noir')
        s('noir',x,y,'kick')
        if f>.52:_burst(c,round(w*.52),floor-(7 if large else 4),(f-.52)/.48,max(4,w//13))
    elif i==4:
        down(.47)
        y=floor-1-round(f*h*.31)
        s('queen',.22-f*.085,y,'climb',True)
        s('noir',.63+f*.21,y-1,'climb')
        c.put(round(w*.14),max(4,y-2),'*','face')
        c.put(round(w*.84),max(4,y-2),'*','face')
    elif i==5:
        down(.48)
        qx=.14+f*.28;nx=.84-f*.27
        y=floor-1-round(h*.30*(1-f*f))
        c.put(round(qx*w)-5,max(2,y-round(h*.23)),r'\ \ ', 'queen')
        c.put(round(nx*w)+3,max(2,y-round(h*.23)),r'/ /', 'noir')
        s('queen',qx,y,'dive')
        s('noir',nx,y-1,'dive')
    elif i==6:
        down(.49)
        s('queen',.37+f*.045,floor-1,'dive')
        s('noir',.63-f*.045,floor-1,'dive')
        _burst(c,center,floor-max(3,h//7),f,max(7,w//9))
        _debris(c,center,floor-h//5,f,t)
    elif i==7:
        down(.50)
        s('queen',.30,floor-1,'ready')
        c.put(center-(12 if large else 7),floor-(7 if large else 4),
              (r'      ____/}>{\__ ',r' _/\_/____/o\____>',r'<_/ \____________') if large else
              (r' __/}>{\ ',r'/_==/o\_>'),'noir',True)
        x=round(w*.66); y=floor-(7 if large else 4)
        c.put(x,y,('  (o)  ',r' __|___',r'/_/ \_ ') if (t-start)%.60<.22
              else ('  (o)  ',r' __|_/ ',r'/_/ \_ '),'face',True)
        for j in range(min(3,1+int((t-start)/.6))):
            c.put(center-round(w*.08)+j*round(w*.08),back-4,'*','flash')
    else:
        down(.49)
        s('queen',.30+f*.08,floor-1,'victory' if f>.38 else 'ready')
        s('noir',.56+f*.035,floor-1-round(f*2),'victory' if f>.50 else 'ready')
        x=round(w*.72); y=floor-5-round(f*h*.14)
        c.put(x,y,('  (o)/',' __|/',r'  / \ '),'face',True)
        for j in range(3):
            c.put(center-round(w*.08)+j*round(w*.08),back-4,'+' if int(t*8)%3==j else '*','flash')
    return BEATS[i][1],c.finish()
