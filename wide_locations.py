"""Full-width native-cell location scenery behind the seven Showtime cels."""
from math import sin


def _dots(c, w, a, b, tick, salt, count, glyphs, speed=0):
    if b <= a:
        return
    for i in range(count):
        x = (i*23+i*i*3+salt+tick*speed) % w
        y = a+(i*29+i*i//3+salt+tick*(i%2)) % (b-a)
        c.put(x,y,glyphs[i%len(glyphs)],'dim')


def _sides(w,l,spacing,offset):
    for x in range(offset,w,spacing):
        if x < l-2 or x > l+58:
            yield x


def _field(c,t,l,o,w,h):
    horizon=o+4
    for x in range(0,w,7):
        y=horizon-1+round(1.45*sin((x+l)/10)+.55*sin(x/4))
        c.put(x,y,'_...--~' if x%3 else '._--.._','dim')
        if (x+l)%6<3:
            c.put(x+2,y+1,'_-..','rope')
    c.put(w*3//4,max(0,o//3),(" .---."," /  . )"," '-.-'"),'dim')
    _dots(c,w,0,horizon,int(t*3),11,w//7,".'+")
    for x in range(1,w,4):
        if not l+2 <= x < l+54:
            c.put(x,o+10+(x//4)%2,('.@.',r'\|/','_|_'),'rope' if x%3 else 'dim')
    # Plant rows widen toward the viewer; nearer stems sway independently.
    for y in range(o+15,h,2):
        d=y-o-14
        for x in range((y*7)%11,w,8+d//2):
            u=(x*17+y*11)%9
            c.put(x,y,('.^.',",.'",'.@.',"_.",r'\|/')[u%5],'rope' if u<4 else 'dim')
            if d>3 and u in (1,3,5):
                bend=int(t*5+x+y)%3-1
                c.put(x+bend,y-1,'+' if u==3 else '.','dim')
                c.put(x,y,('/','|','\\')[bend+1],'rope')


def _desert(c,t,l,o,w,h):
    for x in range(0,w+8,12):
        y=o+2-round(2.4*abs(sin((x+13)/18)))
        c.put(x,y,("  ___       ","_/   \\__    ","        \\___"),'dim')
    c.put(max(1,w//7),max(0,o//3),(" .--.","(    )"," '--'"),'rope')
    for x in _sides(w,l,13,3):
        c.put(x,o+7+(x//13)%3,(' | .','/|_|',' |'),'dim')
    for y in range(o+10,h):
        d=y-o-9
        if d%3==1:
            c.put((y*11)%21-6,y,('___.._.'+' '*max(4,d))*(w//11+2),'dim')
        _dots(c,w,y,y+1,int(t*9),y,w//16,"..~'",speed=2)
    mid=l+28
    for x in (0,w-1):
        c.line(mid+(x-mid)//6,o+11,x,h-1,'dim','.')


def _diner(c,t,l,o,w,h):
    for y in (max(0,o-4),o+1,o+10,o+12):
        # Wall seam and countertop; no outline around the viewport.
        c.put(0,y,('._' if y<o+1 else '_-')*(w//2+1),'dim')
    for x in _sides(w,l,14,3):
        c.put(x,max(0,o-4),('|','|','|','|'),'dim')
        c.put(x-2,o,(' .-. ','(===)'," '-' "),'rope')
        c.put(x-2,o+6,('+---+---+','| . | . |','+---+---+'),'dim')
    for x in range(4,w,14):
        c.put(x,o+14,(' .----.'," '-||-'",'   ||','  _||_'),'rope')
        c.put(x-1,o+18,' .___.','dim')
    for y in range(o+19,h,2):
        step=12+(y-o)//4
        c.put((y*7)%step-step,y,('.._'+' '*max(1,step-3))*(w//step+2),'dim')
    for x in range(10,w-3,17):
        rise=(int(t*5)+x)%4
        c.put(x+rise//2,o+9-rise,'.' if rise==3 else '~','dim')


def _kabuki(c,t,l,o,w,h):
    # Shoji bays form depth at the sides, with a sloping stage floor.
    for x in _sides(w,l,12,2):
        y=max(0,o-3+(x//12)%2)
        c.put(x,y,'.---------.','dim')
        for r in range(y+1,o+10):
            c.put(x,r,'|----+----|' if (r-y)%3==0 else '|    :    |','rope' if r==y+1 else 'dim')
        c.put(x,o+10,'+---------+','dim')
    if o>=2:
        c.put(0,o-2,'   \\_______/ '*((w+13)//14),'dim')
    for x in (max(1,l-5),min(w-3,l+60)):
        c.put(x,max(0,o-3),('|','|','o','O','o'),'rope')
    for x in range(-5,w+8,12):
        target=l+28+(x-l-28)//3
        c.line(target,o+11,x,h-1,'dim','/' if x<l+28 else '\\')
    for y in range(o+15,h,3):
        c.put(0,y,('_.__________.'*((w+12)//13))[:w],'dim')
    _dots(c,w,max(0,o-5),h,int(t*9),17,w//4,".'*.",speed=1)


def _tunnel(c,t,l,o,w,h):
    cx,v=l+28,o+5
    for x in (0,w-1):
        mag=x-cx
        for d in (0,3,7):
            c.line(cx+mag//6,v-3-d//3,x,max(0,o-5-d),'dim','\\' if mag<0 else '/')
        c.line(cx+mag//5,v+3,x,h-1,'rope','.' if mag<0 else ':')
    for x in range(0,w+8,13):
        c.put(x,max(0,o-5)+int(abs(x-cx)/max(7,w//6)),'.___.','dim')
    for y in range(o+6,h,3):
        d=max(1,y-v)
        step=6+d
        drift=(int(t*(14+d))+y*5)%step
        for x in range(-drift,w,step):
            c.put(x,y,'_'*max(1,d//6),'dim')
    for side in (-1,1):
        for k in range(6):
            f=(t*.95+k/6)%1
            x=cx+side*int((w//2+5)*f*f)
            y=v-int((v+2)*f*f)
            c.put(x,y,'[=]' if f>.7 else '.','rope' if f>.5 else 'dim')


def _roof(c,t,l,o,w,h):
    for x in range(-1,w,9):
        y=max(0,o-4+int(3*sin(x/8))+(x//9)%3)
        bw=5+(x//9)%3
        c.put(x,y,'+'+'-'*(bw-2)+'+','dim')
        if x%2:
            c.put(x+bw//2,y-1,"'",'dim')
        for r in range(y+1,o+10):
            slots=''.join('.' if (x+r*3+j*5)%11==1 else ' ' for j in range(bw-2))
            c.put(x,r,'|'+slots+'|','dim')
    for y in range(o+15,h,2):
        d=y-o-14
        for x in range((y*9)%13-7,w,8+d//4):
            c.put(x,y,'___.' if d%2 else ' .-','dim')
    for x in (max(0,l-11),min(w-7,l+61)):
        c.put(x,o+11,(' .----.','/_::::_\\','|______|'),'rope')
    _dots(c,w,0,h,int(t*12),73,w//3,"//.",speed=2)


def _chapel(c,t,l,o,w,h):
    cx=l+28
    apex=max(0,o-6)
    for x in (2,w-3):
        # Tall ribs stagger away from the aisle.
        mx=(x+cx)//2
        c.line(cx,apex,mx,apex+1,'rope','_')
        c.line(mx,apex+1,x,min(h-1,o+9),'dim','/' if x<cx else '\\')
    for x in _sides(w,l,13,3):
        y=max(0,o-1+(x//13)%2)
        c.put(x,y,('    /\\','   /  \\','  / /\\ \\',' /_/__\\_\\',' | :||: |',' | .||. |',
                   ' |_:||:_|','   |  |'),'rope')
        c.put(x+1,o+11,(' )',' |','_|_'),'dim')
    for x in range(-4,w+6,13):
        c.line(cx+(x-cx)//5,o+11,x,h-1,'dim','/' if x<cx else '\\')
    for y in range(o+16,h,3):
        c.put(0,y,('.'+' '*max(1,y-o-13))*(w//2+1),'dim')
    _dots(c,w,apex,h,int(t*5),45,w//4,".'*.",speed=1)


_LOCATIONS={
    'ROSE & REVOLVER':_field,
    'HIGHWAY TO TROUBLE':_desert,
    'MIDNIGHT TAKEOUT':_diner,
    'THE DUEL AT DUSK':_kabuki,
    'TEA IN THE CROSSHAIRS':_tunnel,
    'TWO SIDES OF THE MASK':_roof,
    'THE LAST WALTZ':_chapel,
}


def paint(canvas,title,t,left,top,width,height):
    """Place location scenery below a 57x15 storyboard; no labels or chrome."""
    location=_LOCATIONS.get(title)
    if location is not None and width>0 and height>0:
        location(canvas,t,left,top,width,height)
