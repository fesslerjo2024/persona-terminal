"""Full-field stage painting for Persona 5 Showtimes, before cast and effects."""
from math import cos, pi, sin



def seed(n):
    return ((n*25173+13849) & 65535)/65536


def burst(s,x,y,p,ink='gold',hot='white',n=34):
    """Bounded warm blast with jagged contours; never a screen flash."""
    r=5+29*min(1,p)
    for i in range(n):
        a=i*2*pi/n+seed(i*971)*.15
        q=r*(.67+.55*seed(807*i))
        u,v=x+q*cos(a),y+q*.73*sin(a)
        s.line((x+cos(a)*q*.25,y+sin(a)*q*.2),(u,v),ink if i%3 else hot)
        if i%5==0:s.dot(u+5*cos(a),v+4*sin(a),hot)
    if p<.37:
        s.oval(x,y,r*.51,r*.35,hot,edge=ink)
    else:
        s.arc(x,y,r*.81,r*.48,ink,start=.45+p,end=5.9+p)
        s.arc(x,y,r*.96,r*.66,hot,start=2.2,end=4.7)


def spark_fan(s,x,y,t,n,ink,hot,spread=1.0,direction=1):
    for j in range(n):
        x0=x+seed(j*895+13)*17*direction
        y0=y+(seed(j*719+22)-.5)*18
        z=seed(j*353+71)
        q=(j*.336+t*.47)%1
        u=x0+direction*q*(45+z*105)
        v=y0+(z-.5)*(12+q*82*spread)
        r=3+14*seed(j*513+7)
        s.line((u-r*direction,v-z*3),(u,v),hot if j%5==0 else ink)


def blossom(s,x,y,k,petal='rose',shade='wine',angle=0):
    for j in range(5):
        a=angle+j*2*pi/5
        px=x+cos(a)*2.1*k;py=y+sin(a)*1.7*k
        if k<=1.85:
            s.face(petal,(px-1.6*k,py),(px-.65*k,py-1.25*k),(px+.67*k,py-1.3*k),
                   (px+1.6*k,py),(px+.63*k,py+1.25*k),(px-.67*k,py+1.26*k),edge=shade)
        else:
            s.oval(px,py,1.7*k,1.4*k,petal,edge=shade)
    if k<.85:
        s.dot(x,y,'amber')
    else:
        s.oval(x,y,1.15*k,.88*k,'amber')
    s.dot(x-.38*k,y-.29*k,'white')


def petals(s,t,n=65,area=(0,200,0,128)):
    low,high,top,bottom=area
    for j in range(n):
        x=low+((seed(j*653+7)+t*(.025+seed(j*912)*.095))%1)*(high-low)
        y=top+((seed(j*893+16)+t*(.01+seed(j*926)*.07))%1)*(bottom-top)
        a=t*1.9+j; k=.7+seed(j*662+82)*2.7
        s.face(('wine','rose','red','white')[j%4],(x-cos(a)*k,y-sin(a)*k),(x-k*.9,y+k*.7),
               (x+cos(a)*k,y+sin(a)*k),(x+k,y-k*.6))


def meadow(s,t,near):
    s.box(0,0,200,128,'plum' if near else 'indigo',grain=3)
    if near:
        for j in range(27):
            x=(seed(j*977+64)*222+t*(j%3+2))%220-10;y=seed(j*761+55)*116
            r=2+j%7*1.6;s.arc(x,y,r,r*.65,('plum','wine','rose','violet')[j%4])
        petals(s,t,35)
        return
    for j in range(5):
        s.oval(31+j*38,52+j%2*4,45,13,'forest',grain=4,edge='teal')
    s.face('moss',(0,49),(36,44),(84,58),(144,47),(200,47),(200,128),(0,128),grain=4)
    s.face('moss',(0,98),(61,76),(130,70),(200,75),(200,86),(122,82),(64,94),(17,128),(0,128),grain=5)
    for j in range(124):
        q=seed(j*211+3);x=seed(j*335+15)*208-4;y=44+84*q
        k=.35+1.33*q*q;wind=sin(j*3+t*2)*k
        s.line((x,y+3.9*k),(x+wind,y),'teal')
        s.line((x,y+2.9*k),(x-2*k,y+1.5*k),'forest')
        blossom(s,x+wind,y,k,('rose','white','gold','red','violet')[j%5],
                ('wine','forest','ochre')[j%3],j)


def desert(s,t):
    s.box(0,0,200,128,'plum',grain=3)
    s.oval(99,43,26,30,'ochre',grain=6,edge='amber')
    s.oval(99,45,20,25,'gold',edge='amber')
    for j in range(4):
        y=31+j*7; r=13+(3-j)*3
        s.line((99-r,y),(99+r,y),'white')
    for side in (-1,1):
        p=101+side*54
        s.face('umber',(p-36,76),(p-19,74),(p-15,54),(p-8,22),(p+4,20),(p+9,31),
               (p+13,61),(p+22,70),(p+35,72),(p+49,87),(p-39,90),edge='red')
        s.path('ochre',(p-12,75),(p-12,56),(p-4,38),(p-4,24))
        for j in range(3):s.path('red',(p+11+j*3,44+j*8),(p+12+j*5,63+j*3),(p+19+j*7,76))
    s.face('ochre',(0,81),(62,77),(98,70),(132,76),(200,82),(200,128),(0,128),grain=5)
    s.face('umber',(89,74),(109,74),(156,128),(38,128),grain=7,edge='amber')
    for j in range(33):
        q=(seed(j*811+71)+t*.23)%1; x=seed(j*701+16)*215-8;y=73+q*q*55
        if not 80-35*q < x < 122+35*q:
            s.path('amber' if j%3 else 'gold',(x,y),(x+q*12+4,y-2*q),(x+q*19+8,y-1))
    for j in range(6):
        q=((t*.53+j*.17)%1)**2;y=75+54*q
        s.line((100,y),(100,75+54*min(1,q+.03+.12*q)),'amber')


def diner(s,t,counter=True,open_door=False):
    s.box(0,0,200,128,'plum',grain=3)
    s.box(0,9,200,67,'ink',grain=6)
    for j in range(9):
        x=8+j*23
        s.box(x,17,x+16,52,'umber',edge='ochre')
        s.box(x+2,19,x+14,45,'navy')
        for k in range(4):
            s.box(x+k*3+2,37-k%3*3,x+k*3+3.7,49,('umber','red','indigo','ochre')[k])
        s.line((x+1,51),(x+15,51),'amber')
    for j in range(2):
        x=28+151*j
        s.face('ochre',(x-12,4),(x+11,4),(x+9,48),(x-7,48),grain=2)
        s.oval(x,19,4,12,'amber',edge='gold')
        for k in (-1,1):s.line((x+k*2,9),(x+k*2,30),'gold')
    s.face('umber',(73,85),(73,39),(79,24),(95,18),(111,18),(129,31),(135,86),edge='ochre')
    if open_door:
        s.box(82,29,127,86,'navy',edge='amber')
        for k in range(11):
            x=86+k*4;y=32+seed(k*971)*34
            s.oval(x,y,1.6,2.4,('cyan','rose','violet','amber')[k%4])
        for k in range(7):s.line((92+k*5,55),(74+k*10,86),'red')
    else:
        s.box(83,35,127,85,'umber',edge='ochre')
        s.oval(105,38,9,9,'wine',edge='rose')
        for k in range(9):
            a=k*pi*2/9;s.line((105+cos(a)*3,38+sin(a)*3),(105+cos(a)*9,38+sin(a)*9),'rose')
        s.line((104,47),(104,85),'red')
    if counter:
        s.face('red',(0,88),(65,69),(130,87),(200,121),(200,128),(0,128),grain=6,edge='rose')
        s.face('umber',(0,100),(58,80),(165,111),(197,128),(0,128),grain=6)
        for j in range(30):
            x=seed(j*991+61)*190;y=97+seed(j*983+16)*31
            s.path('ochre',(x,y),(x+7,y-1),(x+12,y))
    else:
        s.face('wine',(0,104),(85,82),(126,83),(200,102),(200,128),(0,128),edge='ochre')


def bowl(s,x,y,k,t):
    s.face('navy',(x-27*k,y),(x+27*k,y),(x+20*k,y+12*k),(x+12*k,y+18*k),
           (x-13*k,y+17*k),(x-21*k,y+12*k),edge='ochre')
    s.oval(x,y,27*k,8*k,'ochre',edge='amber')
    s.oval(x,y-2*k,23*k,7*k,'red',edge='wine')
    for j in range(95):
        a=seed(j*755+27)*2*pi;r=seed(j*389+51); bx=x+cos(a)*21*k*r; by=y-3*k+sin(a)*5*k*r-(1-r)*9*k
        s.path(('amber','gold','rose','red','white')[j%5],(bx-1.4*k,by),(bx,by-.7*k),(bx+1.6*k,by+.8*k))
    for j in range(6):
        px=x+(j-2.5)*6*k
        for a in range(6):
            s.line((px+sin(j+t*2.5+a*.5)*3*k,y-(8+a*3)*k),
                   (px+sin(j+t*2.5+(a+1)*.5)*3*k,y-(11+a*3)*k),'amber' if j%2 else 'slate')
    s.path('gold',(x-25*k,y-15*k),(x+23*k,y-9*k));s.path('ochre',(x-25*k,y-13*k),(x+23*k,y-7*k))


def screens(s,t,pan=0):
    s.box(0,0,200,128,'umber',grain=4)
    for j in range(6):
        x=j*40-20-pan
        s.box(x,0,x+35,78,'umber',edge='ochre')
        s.face('ochre',(x+3,4),(x+32,4),(x+32,65),(x+3,74),grain=3)
        for k in range(9):
            bx=x+seed(j*871+k*797)*32; by=seed(j*717+k*939)*65
            s.face('slate',(bx,by-3),(bx+2,by),(bx,by+3),(bx-2,by),grain=5)
        for k in range(3):
            x0=x+2+k*7
            s.path('ochre',(x0,57+k*3),(x0+7,48+k*2),(x0+13,52+k*3),(x0+19,45+k*2))
        s.line((x,78),(x+35,78),'red')
    s.face('plum',(0,87),(68,68),(129,70),(200,87),(200,128),(0,128),edge='red')
    for i in range(5):
        y=73+(i/4)**2*55
        s.line((0,y),(200,y),'amber' if i%3==1 else 'ochre')
    for i in range(-4,5):s.line((102+i*14,72),(102+i*55,128),'ochre')
    for j in range(24):
        x=seed(j*921+7)*200; y=14+(seed(j*994+38)*108-t*2.5)%110
        blossom(s,x,y,.55+seed(j*731)*.6,'rose','wine',t)


def road_city(s,t):
    s.box(0,0,200,128,'indigo',grain=4)
    h=59; x0=101
    s.oval(134,29,19,18,'rose',grain=6,edge='amber')
    s.face('violet',(118,25),(147,23),(158,19),(156,27),(139,30),(119,33),grain=5)
    for side in (-1,1):
        for j in range(9):
            q=((j+.75)/9+t*.22)%1
            x=x0+side*(q*q*109+7);w=2+q*16; y=h-q*(32+seed(j*937+37)*27)
            s.box(x-w,y,x+w,h+(q**2)*21,'ink',edge='wine')
            for a in range(3):
                for b in range(6):
                    u=x+(a-1)*w*.54; v=y+5+b*(h-y-6)/6
                    if v>h or (a+2*b+j)%6==0:continue
                    s.box(u-w*.13,v,u+w*.15,v+1+q*2,('amber','rose','ochre','white')[(a+b+j)%4])
    s.face('indigo',(92,56),(112,56),(203,128),(-3,128),edge='violet')
    for j in range(7):
        q=((j/7+t*.78)%1)**2;y=59+69*q
        for side in (-1,1):
            s.line((102+side*(3+26*q),y),(102+side*(4+31*q),y+1+9*q),'rose' if j%2 else 'amber')
    s.line((92,57),(0,126),'violet');s.line((112,57),(200,124),'violet')


def van(s,x,y,k,head_on=False):
    def pt(a,b):return x+a*k,y+b*k
    def poly(ink,*pts,edge=None):s.face(ink,*(pt(*p) for p in pts),edge=edge)
    def path(ink,*pts):s.path(ink,*(pt(*p) for p in pts))
    def el(a,b,w,h,ink,edge=None):s.oval(*pt(a,b),k*w,k*h,ink,edge=edge)
    if head_on:
        poly('ink',(-30,10),(-28,-10),(-23,-25),(-17,-33),(17,-33),(23,-25),(29,-12),(31,15),
             (23,22),(-20,22),edge='slate')
        poly('teal',(-19,-25),(18,-25),(24,-8),(-24,-8),edge='cyan')
        poly('navy',(-16,-22),(16,-22),(19,-13),(-19,-13))
        poly('gold',(-5,-33),(4,-33),(5,18),(-4,18),edge='ochre')
        for a in (-1,1):
            el(a*23,20,6,8,'navy','slate')
            el(a*19,6,6,5,'gold','amber')
            el(a*19,6,3,2,'white')
        path('white',(-15,16),(16,16));path('slate',(-26,12),(25,12))
    else:
        poly('ink',(-36,-16),(-20,-25),(21,-21),(35,-10),(42,8),(37,18),(-36,15),
             (-46,9),(-45,-5),edge='slate')
        poly('teal',(-32,-14),(-17,-20),(16,-17),(24,-9),(-33,-7),edge='cyan')
        path('navy',(-20,-19),(-19,-8));path('navy',(-4,-18),(-3,-9))
        poly('ochre',(19,-20),(26,-17),(38,14),(32,15),edge='gold')
        for a in (-25,27):
            el(a,15,8,9,'navy','slate');el(a,15,4,5,'slate','navy')
            for i in range(7):
                z=2*pi*i/7;path('teal',(a+cos(z),15+sin(z)),(a+cos(z)*3.5,15+sin(z)*4))
        el(38,2,4,3,'gold','amber');el(39,1,2.3,1.4,'white')
        path('slate',(-43,9),(-34,10),(35,12))


def arena(s,t,close=False,front=False):
    s.box(0,0,200,128,'umber',grain=3)
    for j in range(156):
        a=seed(j*591+813); b=seed(j*941+18)
        x=200*a;y=19+b*55
        if y+11*sin(x*.06)<70:
            s.dot(x,y,('rose','slate','amber','navy')[j%4])
            if j%4==0:s.line((x-1.2,y+1.7),(x+1.4,y+1.7),'ochre')
            if (j+int(t*8))%37==0:s.oval(x,y,1.5,1.2,'amber')
    for j in range(6):
        x=7+j*37
        s.oval(x,5,6,2,'gold' if j%3 else 'rose',edge='amber')
        s.face('gold' if j%3 else 'rose',(x-2,6),(x+2,6),(x+29,91),(x-32,91),grain=1)
    if close:
        top,base=76,119; backA,backB=-20,223; frontA,frontB=-18,217
    else:
        top,base=60,108; backA,backB=44,154; frontA,frontB=14,192
    s.face('ochre',(backA,top),(backB,top),(frontB,base),(frontA,base),grain=5,edge='amber')
    s.oval(102,(top+base)/2,29,13,'gold',grain=3,edge='amber')
    s.arc(102,(top+base)/2,23,9,'white')
    for j in range(4):
        ang=j*pi/2+t*.15
        s.path('gold',(102+cos(ang)*24,(top+base)/2+sin(ang)*9),
               (102+cos(ang+.4)*32,(top+base)/2+sin(ang+.4)*12))
    s.face('navy',(frontA,base),(frontB,base),(frontB,base+12),(frontA,base+14),edge='ochre')
    post(s,backA,top,27);post(s,backB,top,27)
    for i in range(3):
        y=11+i*7
        s.path('gold' if i==0 else 'red',(frontA,base-y),(backA,top-y),(backB,top-y),(frontB,base-y))
        if front:s.path('amber',(frontA,base-y),(frontB,base-y))
    post(s,frontA,base,32);post(s,frontB,base,32)


def post(s,x,y,h):
    s.box(x-2.8,y-h,x+2.8,y+6,'navy',edge='slate')
    for j in range(3):
        s.oval(x,y-h*.89+j*6,3,2.5,'violet',edge='slate')


def city_roof(s,t):
    s.box(0,0,200,128,'ink',grain=2)
    for j in range(17):
        x=j*16-5;y=45-seed(j*391+65)*31; w=9+seed(j*793+99)*8
        s.box(x,y,x+w,69,'indigo',grain=5,edge='navy')
        for k in range(12):
            bx=x+(k%3+1)*w/4;by=y+3+(k//3)*7
            s.line((bx,by),(bx,by+2),'slate' if k%2==0 else 'navy')
        if j%4==1:s.line((x+w*.5,y),(x+w*.5,y-12),'slate')
    s.face('indigo',(0,84),(64,62),(137,63),(200,82),(200,128),(0,128),edge='slate')
    for j in range(4):
        y=72+j*j*6;s.line((0,y),(200,y),'slate')
    for j in range(-5,6):s.line((102+j*16,66),(102+j*48,128),'navy')
    rain(s,t,66,'navy')


def rain(s,t,n,ink):
    for j in range(n):
        x=(seed(j*917+71)*217-t*(7+2*(j%3)))%218-9
        y=(seed(j*783+77)*130+t*(31+8*(j%3)))%136
        s.line((x,y),(x-2.4,y+2.1+j%4),ink if j%5 else 'slate')


def chapel(s,t,dream=False):
    s.box(0,0,200,128,'indigo' if not dream else 'plum',grain=4)
    if dream:
        s.oval(102,62,101,50,'rose',grain=5,edge='wine')
        s.oval(102,64,92,43,'violet',grain=4,edge='white')
        for j in range(14):
            a=seed(j*970+32)*200;y=68+seed(j*773+17)*60
            s.line((a,y),(a+45,y-11),'rose' if j%2 else 'violet')
        petals(s,t,48)
        return
    for j in range(7):
        x=101+(j-3)*29
        y=33+abs(j-3)*4
        s.face('slate',(x-8,y+48),(x-8,y),(x,y-12),(x+8,y),(x+8,y+48),edge='violet')
        for k in range(6):
            a=11+k*6
            s.face(('rose','teal','violet','navy')[(j+k)%4],
                   (x-6,y+a),(x,y+a-8),(x+6,y+a),(x,y+a+9),edge='slate')
        s.line((x,y-9),(x,y+48),'navy')
    s.oval(101,30,32,27,'navy',edge='slate')
    for j in range(12):
        a=2*pi*j/12
        s.face(('violet','teal','rose','slate')[j%4],(101+cos(a)*8,30+sin(a)*7),
               (101+cos(a-.21)*22,30+sin(a-.21)*19),
               (101+cos(a)*30,30+sin(a)*25),(101+cos(a+.21)*22,30+sin(a+.21)*19),edge='navy')
    s.oval(101,30,6,5,'cyan',edge='violet')
    s.face('indigo',(0,102),(69,79),(133,79),(200,102),(200,128),(0,128),edge='slate')
    for j in range(5):
        y=90+j*j*2.5;s.line((0,y),(200,y),'slate')
    for j in range(-4,5):s.line((101+j*15,79),(101+j*48,128),'violet')
