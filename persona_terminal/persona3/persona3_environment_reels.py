"""Tartarus and Champs de Fleurs, drawn in the same dot grid as the cut-ins."""
from math import cos, pi, sin, tau
from .persona3_detail_tools import Stage, ease, unit


def _moon(s,x,y,rx,ry,ink,dark):
    s.disc(x,y,rx,ry,ink,6,ink)
    for i in range(7):
        offset=1-(i+1)*.058
        s.ring(x-rx*.11,y-ry*.06,rx*offset,ry*offset,dark,.09*i+.1,.09*i+4.1)
    for dx,dy,ax,ay in ((.30,-.25,.18,.21),(-.42,.17,.15,.14),(.22,.39,.16,.09)):
        s.disc(x+dx*rx,y+dy*ry,ax*rx,ay*ry,dark,5,ink)


def _facade(s,x,y,w,bottom,ink,edge,t,far=False):
    if w<=0:return
    cap=y+1.8
    s.shape(((x-1,y),(x+w+1,y),(x+w,bottom),(x,bottom)),ink,6,edge)
    s.path(((x-1,cap),(x+w+1,cap)),edge)
    lamps='teal' if far else edge
    for row in range(max(1,int((bottom-y)//5))):
        yy=y+3+row*5
        for i in range(max(1,int(w//3))):
            xx=x+1+i*2.8
            if (row*7+i*19+round(t*2))%9>4:continue
            s.rect(xx,yy,.7,1.6,lamps,6)
    if not far:
        s.path(((x+w-1,y+4),(x+w-1,bottom)),edge)


def _highrise(s,x,y,w,h,phase,illum=False):
    # A different silhouette on every bolt-on piece of the labyrinth.
    lean=sin(x*.31)*w*.37
    q=((x-w/2,y+h),(x-w*.6+lean,y+h*.29),(x-w*.37+lean,y+h*.19),
       (x-w*.4+lean,y),(x+w*.4+lean,y+h*.02),(x+w*.46+lean,y+h*.23),
       (x+w*.65,y+h*.30),(x+w*.58,y+h))
    s.shape(q,'navy',8,'teal' if illum else 'slate')
    for j in range(1,9):
        n=j/9
        cx=x+lean*(1-n)
        width=w*(.4+.2*n)
        yy=y+h*n
        s.path(((cx-width,yy-1),(cx+width,yy+.6)),'teal' if illum and j%3==0 else 'slate')
        for i in (-3,-2,-1,0,1,2,3):
            xx=cx+i*width*.23
            if (j*23+i*7+int(phase*3))%7>3:continue
            s.rect(xx,yy+1,.30,1.6,'cyan' if illum and i%3==0 else 'teal',5)


def tartarus(t,w,h):
    s=Stage(w,h)
    f=ease(unit(t,0,1.43))
    _moon(s,67-4*f,30,19,26,'green','forest')
    for i in range(6):
        y=29+i*9
        s.path(tuple((j*10,y+sin(j*.82+i+t)*4) for j in range(11)), 'forest')
    s.particles(t,'teal',164,speed=5)
    # A lattice of distorted annexes surrounds the impossibly narrow central spine.
    for x,y,width,height,bright in ((44,14,16,86,False),(61,23,13,75,False),
                                    (53,5,10,97,True),(32,43,14,62,False),
                                    (70,44,16,58,False),(46,30,15,73,True),
                                    (58,37,12,67,True),(39,57,14,47,False)):
        _highrise(s,50+(x-50)*(1+f*.28), y+5*(1-f),width*(.88+.20*f),height,
                  t,bright)
    s.shape(((0,88),(22,82),(45,72),(54,72),(83,84),(100,88),(100,100),(0,100)),
            'navy',8,'slate')
    for i in range(9):
        u=(i/9)**1.8
        y=73+u*27
        span=4+u*39
        s.path(((50-span,y),(50+span,y)),'teal' if i%3 else 'cyan')
        for j in (-1,1):
            s.path(((50+j*span,y),(50+j*span*.84,y+3)),'slate')
    s.shape(((44,76),(45,61),(49,56),(54,56),(57,60),(58,76)), 'slate',7,'teal')
    s.shape(((47,75),(47,64),(51,61),(55,64),(55,75)), 'navy',8,'cyan')
    s.path(((51,63),(51,76)), 'teal')
    return s.c.finish()


def _lift_room(s,t,arrival,p):
    # Gothic rails remain aligned to the gate as the grate leaves frame.
    for side in (-1,1):
        outer,inner=50+side*49,50+side*(20+6*p)
        s.shape(((outer,9),(inner,24),(inner,75),(outer,97)),'navy',7,'slate')
        for j in range(6):
            x=outer+(inner-outer)*j*.15
            s.path(((x,9+j*2.5),(x,97-j*4)),'navy' if j%2 else 'teal')
        for j in range(6):s.path(((outer,10+j*15),(inner,24+j*10)), 'slate')
    s.shape(((50-20,75),(50+20,75),(100,100),(0,100)),'navy',7,'slate')
    for i in range(7):
        y=75+i*i*.68
        span=19+i*5.2
        s.path(((50-span,y),(50+span,y)), 'teal' if i%3 else 'slate')
    s.shape(((30,74),(30,25),(36,15),(65,15),(72,25),(72,74)), 'navy',8,
            'green' if arrival else 'teal')
    s.ring(51,29,18,15,'teal',pi,tau)
    rail_move=22*p
    for side in (-1,1):
        start=51+side*rail_move
        for i in range(6):
            x=start+side*i*3.4
            s.path(((x,26),(x,73)), 'slate' if i%2 else 'teal')
            s.path(((x,26),(x+side*.54,26),(x+side*.54,73)), 'cyan' if not arrival and i==0 else 'navy')
        s.path(((start,43),(start+side*18,43)), 'slate')
        s.path(((start,60),(start+side*18,60)), 'slate')
    for i in (-1,1):
        x=51+i*22
        s.shape(((x-1,31),(x+1,31),(x+1,41),(x-1,41)), 'teal',6,'slate')
        s.disc(x,36,.7,1.5,'green' if arrival else 'cyan')


def elevator(t,w,h,start,destination,duration):
    t=unit(t,0,duration)
    s=Stage(w,h)
    sign=(destination>start)-(destination<start)
    marker='^' if sign>0 else 'v' if sign<0 else '-'
    if t<.25:
        _lift_room(s,t,False,1-ease(t/.25));floor=start;read='teal'
    elif t<.73:
        p=unit(t,.25,.73)
        for side in (-1,1):
            x=50+side*25
            s.shape(((x-3,0),(x+3,0),(x+3,100),(x-3,100)), 'navy',6,'slate')
            for i in range(15):
                y=((i*17+floor_speed(p,sign))%100)
                xx=x+sin(i*43)*20
                speed=(1-abs(p-.48))*8
                s.path(((xx,y),(xx,y+speed*4)), 'teal' if i%4 else 'cyan')
                if i%4==0:s.path(((xx-4,y),(xx+4,y)), 'slate')
        pulse=max(0,1-abs(p-.48)*2.45)
        for i in range(6):
            s.ring(50,51,7+i*8+p*9,20+i*5+p*18,'white' if pulse>.65 and i in (1,2) else 'cyan',
                   i*.43+p*3,i*.43+5.1+p*3)
        floor=round(start+(destination-start)*ease(p));read='cyan'
    else:
        _lift_room(s,t,True,ease(unit(t,.73,1)));floor=destination;read='green';marker='-'
    packed=s.c.pack()
    sread=f'| {floor:02d} {marker}|'
    row=min(h-1,max(0,round(h*.16)))
    packed.put(max(0,(w-len(sread))//2),row,sread,read,True)
    return packed.finish()


def floor_speed(p,sign):return p*433*(sign or 1)


def _hotel_exterior(s,t):
    _moon(s,79,24,12,18,'green','forest')
    s.particles(t,'teal',124,speed=1,region=(0,0,100,63))
    for i in range(8):
        x=i*16-7
        _facade(s,x,43+(i*37)%14,12,85,'navy','forest',t,True)
    s.shape(((21,82),(21,37),(31,37),(31,28),(40,28),(42,15),(59,15),(62,28),(69,28),
             (69,37),(80,37),(80,82)), 'navy',8,'green')
    for i in range(11):
        x=23+i*5.4
        s.path(((x,40),(x,78)), 'forest')
        for y in (45,56,67):
            if i in (4,5,6) and y>52:continue
            s.rect(x+.8,y,3.2,6,'wine' if i%3==0 else 'forest',6,'rose' if i%4==1 else 'teal')
            s.path(((x+2.3,y),(x+2.3,y+6)),'navy')
    s.shape(((37,38),(40,32),(61,32),(66,38),(64,51),(36,51)), 'wine',7,'rose')
    # A petal emblem is the sign's silhouette, not a subtitle.
    for i in range(5):
        a=i*tau/5
        s.disc(51+cos(a)*4,41+sin(a)*5,2.5,3.8,'rose',5,'wine')
    s.disc(51,41,1.5,2,'rose')
    s.shape(((42,81),(42,57),(59,57),(59,81)), 'forest',7,'green')
    s.path(((50.5,58),(50.5,81)),'green')
    for i in range(7):s.path(((21-i*1.8,81+i*i*.48),(80+i*1.8,81+i*i*.48)),'forest')
    s.path(((45,82),(31,100)),'teal')
    s.path(((56,82),(73,100)),'teal')


def _hotel_interior(s,t):
    for side in (-1,1):
        a=50+side*50; b=50+side*28
        s.shape(((a,0),(b,13),(b,77),(a,100)),'wine',6,'rose')
        for i in range(8):
            x=a+(b-a)*i/8
            s.path(((x,0),(x,91-i*2)),'rose' if i%4==0 else 'wine')
        s.ring(50+side*35,45,3,10,'amber')
        s.disc(50+side*35,45,1,3,'rose')
    s.shape(((16,78),(41,59),(60,59),(86,78),(100,100),(0,100)), 'navy',8,'wine')
    for i in range(7):
        y=77+i*i*.69;dx=27+i*4.1
        s.path(((50-dx,y),(50+dx,y)),'wine' if i%2 else 'rose')
    s.disc(50,45,20,34,'navy',8,'rose')
    s.disc(50,45,17.3,30,'slate',5,'wine')
    for i in range(8):
        y=25+i*6
        s.path(((38+(i%3),y),(61-(i%2),y-10)), 'rose' if i%2 else 'teal')
    for i in range(10):
        angle=i*tau/10+t*.2
        s.disc(50+cos(angle)*19,45+sin(angle)*33,.7,1.3,'rose')
    s.shape(((38,45),(44,40),(48,49),(52,47),(50,60),(46,64),(42,51)), 
            'navy',7,'wine')
    s.path(((51,19),(49,37),(54,46),(51,51),(63,57),(59,70)), 'teal')
    s.path(((51,51),(47,58),(48,66),(45,72)), 'rose')


def hotel_arrival(t,w,h):
    s=Stage(w,h);_hotel_exterior(s,t);return s.c.finish()


def hotel_mirror(t,w,h):
    s=Stage(w,h);_hotel_interior(s,t);return s.c.finish()


def hotel_wipe(t,w,h,duration):
    t=unit(t,0,duration)
    if t<.12:return hotel_arrival(0.,w,h)
    if t>.84:return hotel_mirror(0.,w,h)
    s=Stage(w,h);_hotel_exterior(s,0)
    inside=Stage(w,h);_hotel_interior(inside,0)
    f=ease(unit(t,.12,.84))
    # Diagonal fractures open, then the reflected room occupies the view.
    # Replace microdots before packing, never splice a font or tile.
    for yy,row in enumerate(s.c.rows):
        p=yy/max(1,s.c.h-1)
        core=round(s.c.w*(.46+.21*(p-.5)*(1-f)))
        length=round(s.c.w*(.005+.64*f))
        lo=max(0,core-length);hi=min(s.c.w,core+length)
        row[lo:hi]=inside.c.rows[yy][lo:hi]
        for d in (-1,1):
            x=core+d*length
            s.c.put(x,yy,'white' if .24<f<.69 and (yy+int(t*45))%10<3 else 'rose')
            s.c.put(x+2*d,yy,'wine')
    for i in range(15):
        u=i*tau/15
        x=50+f*45*cos(u);y=47+f*48*sin(u)
        s.path(((x-.6,y+.8),(x,y),(x+.8,y-1.9)),'rose' if i%4 else 'teal')
    return s.c.finish()


def monorail(w,h,car,t,*,braking=False,stopped=False):
    """Wide moving windows, rail sparks and a compact driver-cab action."""
    s=Stage(w,h)
    v=t*(61 if braking else 25)
    s.shape(((0,0),(100,0),(81,18),(19,18)), 'navy',8,'teal')
    s.shape(((0,81),(43,63),(57,63),(100,81),(100,100),(0,100)), 'navy',8,'slate')
    for j in range(7):
        y=68+j*j*.93
        spread=8+j*8
        s.path(((50-spread,y),(50+spread,y)), 'slate' if j%2 else 'teal')
    if braking:
        s.shape(((0,12),(100,12),(78,70),(21,70)), 'navy',8,'slate')
        for side in (-1,1):
            d=50+side*14
            s.path(((50+side*2,29),(d,65),(50+side*47,97)),
                   'teal' if stopped else 'amber')
            s.path(((50+side*4,35),(d+side*2,64),(50+side*48,94)),
                   'green' if stopped else 'gold')
        for i in range(7):
            y=34+i*5
            s.path(((47-i*3,y),(53+i*3,y)), 'slate')
        s.shape(((8,100),(22,70),(80,70),(93,100)), 'navy',7,'teal')
        for i in range(6):
            x=26+i*8.1
            s.disc(x,79,1.4,3.1,'green' if stopped else 'rose' if i%2 else 'gold',7,'teal')
        s.shape(((45,100),(44,84),(55,84),(57,100)), 'slate',8,'teal')
        s.path(((50,89),(50+(6 if stopped else -2),66)), 'white')
        s.disc(50+(6 if stopped else -2),66,3,7,'green' if stopped else 'amber',7,'white')
        if not stopped:
            for i in range(18):
                x=(i*31+v)%100
                y=31+(i*23)%34
                s.path(((x,y),(x+2.1,y+3)), 'amber' if i%4 else 'white')
    else:
        for side in (-1,1):
            for i in range(4):
                x=50+side*(17+i*10)
                s.shape(((x-5,18),(x+5,17),(x+6,56),(x-6,57)), 'navy',8,'teal')
                for j in range(4):
                    k=(i*11+j*5+v*.47+car*17)%10-5
                    y=23+(i*7+j*9)%25
                    s.path(((x+k-1.5,y),(x+k+1.5,y)), 'forest' if j%2 else 'green')
                shade='violet' if car==1 else 'slate'
                s.shape(((x-6,57),(x+6,56),(x+7,76),(x-7,78)), shade,7,'teal')
                s.path(((x-6,68),(x+6,66)), 'navy')
            s.path(((50+side*12,14),(50+side*29,3),(50+side*48,2)),'slate')
        s.shape(((42,66),(41,23),(46,15),(54,15),(59,23),(58,66)), 'navy',8,'teal')
        s.path(((50,18),(50,66)), 'cyan')
        s.disc(49,46,.8,1.8,'gold')
    return s.c.finish()
