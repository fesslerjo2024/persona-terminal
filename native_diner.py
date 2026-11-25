"""Native Midnight Takeout: a late-night counter built in terminal cells."""
from math import cos, pi, sin, tau
from wide_canvas import Canvas

TITLE = 'MIDNIGHT TAKEOUT'
SECONDS = 7.92


def f(t,a,b):
    return max(0,min(1,(t-a)/(b-a)))


def sprite(c,x,y,art,ink):
    for j,line in enumerate(art,y):
        line=line.rstrip()
        c.put(x-len(line)//2,j,line,ink,True)


MASKS = {
    'fox': (
        (" /\\  /\\ ",'/[.][.]\\','\\  /\\  /',' \\__/_/ '),
        ('   /\\       /\\   ', '  /  \\_____/  \\  ', ' / . /_   _\\ . \\ ',
         '(   [o]   [o]   )', ' \\     /\\     / ', '   \\___/\\___/   ')),
    'skull': (
        (' _/^^\\_ ','/[.][.]\\','| /_/  |','\\_###_/ '),
        ('   .^/^/^/.   ', ' _/^^^^^^^\\_ ', '/ /__   __\\ \\',
         '|  [.] [.]  |', '\\_  /_\\  _/', '  \\_#_#_/  ')),
    'shadow': (
        (' ^\\___/^ ', '/   *   \\','|  (_)  |',' \\_###_/'),
        ('  ^\\_______/^  ', ' /\\___   ___/\\ ', '/  .*  |  *.  \\',
         '|    .---.    |', ' \\  (_____)  /','  \\_#######_/  ')),
}
COSTUME = {'fox':('cyan','teal'),'skull':('gold','amber'),'shadow':('violet','wine')}


def person(c,name,x,foot,pose='walk',t=0):
    big=c.h>=30 and c.w>=78
    face,ink=COSTUME[name]
    head=MASKS[name][big]
    leg=round(sin(t*17)*(2 if big else 1)) if pose in ('walk','run') else 0
    body_h=7 if big else 5
    hip=foot-3
    sprite(c,x,foot-body_h-len(head)+1,head,face)
    c.put(x-3,hip-3,(' <#> ' if name=='fox' else ' [#] '),'white',True)
    c.put(x-3,hip-2,'/[##]\\',ink,True)
    c.put(x-3,hip-1,'|[##]|',ink,True)
    c.put(x-3,hip,' \\==/ ',ink,True)
    # Full-body joint paths vary the silhouette, not just screen position.
    reach = 8 if big else 5
    if pose=='stir':
        a=x+reach; b=hip-2+round(sin(t*14))
    elif pose=='cut':
        a=x+reach; b=hip-5+round(sin(t*9)*4)
    elif pose=='aim':
        a=x+reach; b=hip-3
    elif pose=='stagger':
        a=x-reach; b=hip-5
    else:
        a=x+reach//2+leg; b=hip
    c.line(x+2,hip-3,(x+a)//2,hip-2,ink)
    c.line((x+a)//2,hip-2,a,b,face)
    c.line(x-2,hip-3,x-reach//2,hip+leg,ink)
    c.line(x-2,hip+1,x-3-leg,foot,ink)
    c.line(x+2,hip+1,x+3+leg,foot,ink)
    c.put(x-4-leg,foot,'_/','white')
    c.put(x+2+leg,foot,'\\_','white')
    if pose in ('cut','aim'):
        c.line(a,b,a+(9 if big else 5),b-(2 if pose=='cut' else 0),'white','=')
    return a,b


def bowl(c,x,y,t):
    sprite(c,x,y,(" . . . . "," (:::::) ","  \\___/  "),'amber')
    for j in range(6):
        rise=(int(t*11)+j*2)%7
        c.put(x+j%3-1+round(sin(j+t*4)*2),y-1-rise,'~' if rise<3 else '.','rose' if rise>3 else 'white')


def diner(c,t):
    w,h=c.w,c.h
    ceiling=round(h*.12)
    counter=round(h*.69)
    # Staggered blue tile under lacquer and warm lamps. Every bay is constructed
    # from the actual room dimensions, including the angled foreground floor.
    c.put(0,ceiling,'=.'*((w+1)//2),'wine')
    for x in range(-2,w,max(11,w//8)):
        peak=round(h*.17)+x%3
        if x%2:
            c.line(x+3,ceiling,x+3,peak+1,'ochre','|')
            c.put(x,peak+2,(' _---_ ','(_____)',' . . . '),'amber')
        for y in range(peak+7,counter-2,3):
            shift=(y//3)%2*3
            c.put(x+shift,y,':____:___','navy')
    width=max(37,round(w*.61))
    c.put(0,counter,'='*width+'\\','amber')
    for j in range(1,4):
        c.put(0,counter+j,('=-' *((width+1)//2))[:width]+'|','ochre' if j%2 else 'wine')
    for index in range(5):
        x=round(w*(.07+.13*index))
        y=counter+4+index%2
        c.put(x-3,y,('.-----.'," '-+-' ",'   |   ','  _|_  '),'rose')
    for x in range(-w//3,w+w//3,max(8,w//10)):
        c.line(w//2+(x-w//2)//5,counter+1,x,h-1,'navy','.')
    for n in range(5):
        y=counter+3+round((n/4)**2*(h-counter-4))
        c.put(0,y,(' .   '*((w+4)//5))[:w],'wine')
    door=round(w*.82)
    r=max(5,w//13)
    c.line(door-r,round(h*.24),door-r,counter+1,'teal')
    c.line(door+r,round(h*.24),door+r,counter+1,'teal')
    c.put(door-r,round(h*.24),'_'*(r*2+1),'teal')
    for i in range(w//7):
        x=(i*19+int(t*6))%w
        c.put(x,(i*7)%max(1,counter-3),'*' if i%6==0 else '.','rose' if i%3==0 else 'navy')


def burst(c,x,y,t):
    for i in range(32):
        a=tau*i/32
        r=3+t*(4+(i%6)*c.w*.047)
        u=x+round(cos(a)*r); v=y+round(sin(a)*r*.46)
        c.put(u,v,'*' if t<.35 else '.','amber' if i%3 else 'rose')
        if t<.54 and i%4==0:c.line(x+(u-x)*.48,y+(v-y)*.48,u,v,'gold')


def render(title,t,w,h):
    assert title==TITLE
    c=Canvas(w,h)
    diner(c,t)
    ground=round(h*.87)
    level=round(h*.69)
    cook=round(w*(.18+.12*f(t,0,1.5)-.07*f(t,5.4,7.1)))
    customer=round(w*(.51-.09*f(t,0,1.8)+.12*f(t,2.2,3.3)-.09*f(t,6.25,7.4)))
    foe=round(w*(.92-.24*f(t,1.3,3.15)+.29*f(t,5.0,6.1)))
    cut=.0
    if t<2.25:
        person(c,'fox',cook,level,'stir',t)
        person(c,'skull',customer,ground,'walk',t)
        bowl(c,round(w*(.26+.14*f(t,.7,1.95))),level-3,t)
        if t>1.18:person(c,'shadow',foe,ground,'walk',t)
        beat='counter'
    elif t<3.38:
        person(c,'fox',cook,level,'stir',t)
        person(c,'skull',customer,ground,'aim',t)
        person(c,'shadow',foe,ground,'walk',t)
        bowl(c,round(w*.44),level-3,t)
        beat='ambush'
    elif t<5.18:
        cut=f(t,3.40,4.92)
        x=round(w*(.56+.11*cut))
        y=ground-5-round(sin(pi*cut)*h*.34)
        person(c,'shadow',foe,ground,'stagger',t)
        sx,sy=person(c,'skull',customer-4,ground,'aim',t)
        if t<3.68:c.line(sx+3,sy,x,y,'amber','*')
        hop=f(t,3.65,4.82)
        cook=round(w*(.29+.22*hop))
        a,b=person(c,'fox',cook,ground-round(h*.26*sin(pi*hop)), 'cut',t)
        c.put(x,y,'(_)*','amber',True)
        if cut>.57:
            c.line(a,b,x+7,y-3,'cyan','/')
            c.line(x-3,y+2,x+7,y-3,'white')
        beat='slash'
    else:
        spread=f(t,5.18,6.61)
        if t<6.61:burst(c,round(w*.70),ground-4,spread)
        person(c,'fox',round(w*(.55-.34*f(t,5.52,7.15))),level,'walk',t)
        person(c,'skull',customer,ground,'stagger' if t<6.03 else 'walk',t)
        bowl(c,round(w*(.48-.11*f(t,6.18,7.68))),level-4,t)
        beat='settle'
    return beat,c.finish()
