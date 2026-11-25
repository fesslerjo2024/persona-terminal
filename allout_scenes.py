"""Nine original terminal All-Out posters inspired by Royal gameplay.

Reference reels: https://www.youtube.com/watch?v=8-tIjvQjXS8
and https://www.youtube.com/watch?v=ZdVl3MnMqbc. No art assets are embedded.
"""
from math import cos, sin, tau
from wrestling_scene import Canvas, WIDTH, HEIGHT

# Layerable, asymmetric full-height figures.  Characters used as ink tokens
# are still drawn as visible ASCII; there is no image conversion dependency.
PORTRAITS = {
    'Joker': r"""
        ._  .-----._
      _/ /`/_.--.._ \
     / _/ ///////\_/
    /_/  /_/////  }
    \ ==\__o^o_/==)
     \_   \_v_/ _/
       '.___._.'
    __/###/\###\__        /!
   /####/####\####\___   /R|
  /####/###@@#\#######\_/RR|
 /####/######/ \#######/''
'----/------/   '----'
""",
    'Mona': r"""
       /\            /\
      /##\__________/##\
     /##################\
    ;###.------------.###;
    |##/  OU    OU    \##|
    |##\       v      /##|
     \##'-.__----__.-'##/
      '----------------'
          /=GGGGGGG==/\
     o===/GG/|###| \/ \o
     (_)/###|/___\##\
         \__'     '__/
""",
    'Skull': r"""
          _/V\_V___
       __/GGGGGGGGG\
     _/GGGGGGGGGGGG/       G  G
    /GGG/____::::_\       |G||G|
   /__/ [_oo_  _oo_])     |G||G|
   \    |   VV     |      |G||G|
    \___|  |HHH|   /     \GGGG/
        \__|HHH|__/    __/GGG/
      ====RRRRRR===== /####/
     /#######/\######/####/
    /#######/  \#########/
    \______/    \_______/
""",
    'Panther': r"""
     /\     ____     /\
    /RR\___/GGGG\___/RR\     /| /|
    |RR/ GGGGGGGGG \RR|    |R||R|
    | /\__/=====\__/\ |    |R||R|
     \=\  o\ _ /o  /=/     \RRR/
   GGG/G\   v   /G\GGG      |R|
  GGG/ GG\__-__/GG \GGG     /RR/
 GG/      \RRR/      \GG   /RR/
  / __---/RRRRR\---__ \   /RR/
    /RRRR\RRRRR/RRRR\ \_/RR/
   /RRRRRRRRRRRRRRRRR\/RRR/
   '---/RRRRRRRRR\------'
""",
    'Fox': r"""
        /\         /\
       /R \       / R\
      /  R \_____/ R  \
      |     ^^        |
       \=\__ / \ __/=/
        \ (o) . (o) /
         \       . /
          \  RRR  /
           \_vv__/
      ____/###C###\___
  ===/######//\\######\===>
    /######//CC\\######\
""",
    'Queen': r"""
        .---_______
      _/##//////###\
     /###////#######\
    |###__________###|
    |>==\__OO__OO_/==<
    |    \    v   /   |
     \____\__=___/___/
          |##C##|
   ___^___/#####\___^___
  /##/################\##\==
 /###\###/CCCCCC\#####/###\=
'-----'---'------'---'-----'
""",
    'Noir': r"""
        <--_,,___
           /###/ \__
          /##_/     \
     ____/__/________\____
    (=====HH============)
      {GG /-------\ GG}
     {G~ / \o/ \o/ \ ~G}
      {~ \    v    / ~}
       ~~ \___-___/ ~~
     ____/  >}<{  \___       .---.
    /HHH/  H  o H  \HH\_____/CCC/]
   /___/____H___H___\_______===='
""",
    'Crow': r"""
        __.------.._
     .-/###########\__
    /###\#######_/###=\
   /#####'-----'######==
   \####RRR::RRR#####=/
    |####=-\_/--####|
     \##///###\\\##/
        \_______/
      _/RR/###\RR\___
   __/RR/######\RRRRR\
  /RRRR/####@###\RRRRR\____
 /====/==========\---======\
""",
    'Violet': r"""
            .---.__
          _/RRRRRRR\__
     @---/RRRRRRRRRRR\R\
        /RRR\_____/RRR|RR|__
       |##/==---==\###|RRRRR\
       \=\__o\ /o_/==/  RRRR\
         \   vv   /      \RRR\
          \___-__/       /RR/
      ___##/ V \##___   /RR/
     /####/CCCCC\####\ /RR'
  --/##R##/CCC\##R####\/--
    \___/CCCCC\______/  @
""",
}

INK = {'R':'red', 'C':'cyan', 'G':'gold', 'H':'rope',
       '#':'rail', ':':'dim', '=':'face', 'o':'face', 'O':'cyan', '@':'red'}
MARK = {'R':'%', 'C':'+', 'G':'+', 'H':'~'}

# Five high display type, deliberately differing type direction/treatment per
# card, with compact 3-cell letters to leave room for the full portrait.
TYPE = dict(zip('ABDEFGHIJLMNOPRSTUVWY!',
    ('010/101/111/101/101','110/101/110/101/110','110/101/101/101/110',
     '111/100/110/100/111','111/100/110/100/100','111/100/101/101/111',
     '101/101/111/101/101','111/010/010/010/111','011/001/001/101/111',
     '100/100/100/100/111','101/111/111/101/101','101/111/111/111/101',
     '111/101/101/101/111','110/101/110/100/100','110/101/110/101/101',
     '111/100/111/001/111','111/010/010/010/010','101/101/101/101/111',
     '101/101/101/101/010','101/101/111/111/101','101/101/010/010/010',
     '010/010/010/000/010')))

TYPE['C']='111/100/100/100/111'

# word, two pieces of lettering, portrait X, lettering X/Y, ink, length.
CARD = {
    'Joker': ('SHOW', 'THE FINAL ACT', 'CURTAIN CALL', 30, 6, 5, 'red', 3.26),
    'Mona': ('MISSION', 'NEKOMATA FILM CO.', 'ACCOMPLISHED', 0, 29, 5, 'cyan', 3.18),
    'Skull': ('BORING', '!!!   CAUTION   !!!', 'NEXT CHALLENGER?', 25, 3, 5, 'gold', 3.04),
    'Panther': ('OMG!', 'PEACE  <3  CUTE', 'WE OWN THE FRAME.', 0, 32, 5, 'red', 3.12),
    'Fox': ('GOODBYE', 'A SINGLE BRUSHSTROKE', 'THE DRAGON SIGNS OFF.', 30, 1, 4, 'cyan', 3.46),
    'Queen': ('JUSTICE', 'STEEL / IMPACT', 'VERDICT DELIVERED.', 0, 28, 5, 'white', 3.30),
    'Noir': ('ADIEU', 'LE SALON DE NOIR', 'TEA IS SERVED.', 0, 33, 5, 'rope', 3.58),
    'Crow': ('TRUTH', 'NO ONE ELSE DECIDES', 'CASE CLOSED.', 30, 3, 5, 'red', 3.32),
    'Violet': ('DEVOTION', 'THE ROSE STEPS OUT', 'A FLAWLESS FINISH.', 29, 1, 4, 'red', 3.52),
}
TITLES = {
    'Joker':'JOKER // CURTAIN CALL', 'Mona':'MONA // NINE LIVES',
    'Skull':'SKULL // THUNDER RUN', 'Panther':'PANTHER // FLASH POINT',
    'Fox':'FOX // FINAL BRUSHSTROKE', 'Queen':'QUEEN // REDLINE',
    'Noir':'NOIR // AFTERNOON FINALE', 'Crow':'CROW // CASE CLOSED',
    'Violet':'VIOLET // STICK THE LANDING',
}

def _line(c,x0,y0,x1,y1,glyph,ink):
    segment=max(abs(x1-x0),abs(y1-y0),1)
    for i in range(segment+1):
        c.put(round(x0+(x1-x0)*i/segment),round(y0+(y1-y0)*i/segment),glyph,ink)

def _type(c,x,y,word,ink,treatment):
    # Knock out the halftone directly behind display type so a colored
    # terminal and a monochrome terminal read the same headline.
    for j in range(5):
        skew=((4-j)//2 if treatment in ('Skull','Panther') else
              (j//2 if treatment in ('Crow','Fox') else 0))
        c.put(x+skew-1,y+j,' '*(4*len(word)+1),'dim',opaque=True)
    for i,char in enumerate(word):
        mask=TYPE[char].split('/')
        for j,line in enumerate(mask):
            skew=((4-j)//2 if treatment in ('Skull','Panther') else
                  (j//2 if treatment in ('Crow','Fox') else 0))
            c.put(x+i*4+skew,y+j,''.join('#' if b=='1' else ' ' for b in line),ink)

def _paint_portrait(c, who, x, y):
    rows=PORTRAITS[who].strip('\n').splitlines()
    for j,row in enumerate(rows):
        # Clear contours within the silhouette, not across the title.
        start=len(row)-len(row.lstrip())
        c.put(x+start,y+j,' '*max(0,len(row)-start),'dim',opaque=True)
        for i,ch in enumerate(row):
            if ch!=' ':
                c.put(x+i,y+j,MARK.get(ch,ch),INK.get(ch,'white'))

def _oval(c,x,y,rx,ry,ink,ch='o',dashes=1):
    for i in range(0,60,dashes):
        a=i*tau/60
        c.put(round(x+rx*cos(a)),round(y+ry*sin(a)),ch,ink)

FLOWER=(' .@. ','@@@@@',r' \|/ ')
ROSE=('  _@_ ',' (o@o)','  \\/ ')
PAW=(' o o o ','o     o','  (W)  ',' (___) ')
MASKS=(
    (' .====. ',r'/ o  o \ ',r'\__v___/'),
    (r' /\ /\ ',r'< * * >',r' \_w_/ '),
    (' _..._ ',r'( o.o )','  `v`  '),
    (r'  /\_  ',r'.( >< ).',r' \_v_/ '),
)

def _charge(c,t,accent):
    cx,cy=28,7
    for i in range(22):
        angle=i*tau/22
        radius=23+int(10*t)
        xx=round(cx+radius*cos(angle));yy=round(cy+.48*radius*sin(angle))
        gap=max(5,15-int(15*t))
        xx2=round(cx+gap*cos(angle));yy2=round(cy+.4*gap*sin(angle))
        _line(c,xx,yy,xx2,yy2,('./\\-'[(i+int(t*16))%4]),'red' if i%3 else 'rail')
    anchor=((3,1),(43,2),(4,11),(44,10))
    slide=min(1,t/.68)
    for i,(x,y) in enumerate(anchor):
        dx=(14 if i%2==0 else -16)*slide
        dy=(3 if i<2 else -3)*slide
        c.put(x+int(dx),y+int(dy),MASKS[i],'face' if i%2==0 else accent,opaque=True)
    c.put(18,2,'/ /  H O L D   U P  / /','white',opaque=True)
    if t>.38:c.put(15,12,'>>>  P H A N T O M   R U S H  <<<',accent,opaque=True)

def _impact(c,t,accent):
    for i in range(15):
        a=(i+.2)*tau/15
        shift=int(t*16)
        _line(c,28+round(shift*cos(a)),7+round(shift*.48*sin(a)),
              28+round(37*cos(a)),7+round(14*sin(a)),
              'X' if i%4==0 else '/','white' if i%3==0 else accent)
    c.put(20,6,'[  TOTAL IMPACT  ]','white',opaque=True)
    c.put(24,8,'* * * * *','gold',opaque=True)

def _motif(c,who,t):
    pulse=int(t*6)
    for x in range(1,WIDTH-1,5):
        for y in range(HEIGHT):
            if (x*3+y*7)%13<3:
                c.put(x+(y%3),y,'.','dim')
    if who=='Joker':
        for i in range(0,HEIGHT,2):
            c.put(0,i,'##//','red');c.put(53,i,'\\\\##','red')
        for x,y in ((0,0),(47,0),(56,7),(0,13),(48,14)):
            _line(c,x,y,27,7,'/' if x<26 else '\\','rail')
        c.put(3,2,('T','H','E'),'white')
        c.put(3,7,('E','N','D'),'red')
    elif who=='Mona':
        for y in (1,12):
            c.put(0,y,'[]=='*14+'[','rail')
        for i in range(4):
            x=4+i*13
            c.put(x,2,'._____.','dim')
            c.put(x,11,"'-----'",'dim')
        c.put(49,10,PAW,'red')
    elif who=='Skull':
        c.put(0,1,'/!/'*19,'gold')
        c.put(0,13,'/!/'*19,'red')
        _line(c,36,1,55,9,'+','rail')
        _line(c,42,4,27,13,'/','gold')
        c.put(2,12,'TOO EASY  >>>','gold')
    elif who=='Panther':
        for x,y,label in ((1,1,'<< PEACE'),(50,1,'KISS'),(48,8,'<3'),
                          (20,2,'<3'),(2,13,'!!'),(49,12,'CUTE!')):
            c.put(x,y,label,'red' if (x+pulse)%3 else 'rope')
        _oval(c,30,7,28,7,'rope','*',3)
        for x,y in ((25,4),(53,6),(25,10)):
            c.put(x,y,('/!\\','-+-',r'\!/'),'gold')
    elif who=='Fox':
        _oval(c,39,7,16,6,'dim','~',2)
        _oval(c,41,7,13,6,'red','~',3)
        c.put(19,11,(r'  /\_/\ ',r'<[o   o]>',r'  \_v_/~~~~'),'red')
        for i,(x,y) in enumerate(((1,1),(16,2),(25,11),(45,13),(51,5))):
            c.put(x,y,'*' if (i+pulse)%3 else '+','rope')
    elif who=='Queen':
        for y in range(HEIGHT):
            for x in range(1+(4*y)%8,WIDTH,8):
                c.put(x,y,'<>' if y%2 else '[]','rail')
        for i in range(5):
            _line(c,5+i*7,12,55-i*3,1,'/','dim' if i%3 else 'red')
        c.put(46,2,'>>=>','red')
    elif who=='Noir':
        _oval(c,39,7,16,7,'rope','o')
        _oval(c,39,7,14,6,'dim','.',2)
        for x,y in ((1,1),(23,2),(49,0),(51,10),(19,11)):
            c.put(x,y,FLOWER,'rope')
    elif who=='Crow':
        for y,skew in ((1,1),(12,-1)):
            _line(c,0,y,56,y+skew,'-','red')
            for x in range((pulse%2)+2,WIDTH,5):
                yy=round(y+x*skew/56)
                c.put(x,yy-1,chr(92),'rail')
                c.put(x,yy+1,'/','rail')
        for i in range(4):_line(c,31+i*6,14,52+i*3,0,'/','dim')
        c.put(2,10,'==x===x===x==','rail')
    elif who=='Violet':
        _oval(c,42,8,14,6,'rope','.',2)
        c.put(48,1,ROSE,'red')
        c.put(46,10,ROSE,'red')
        for i,(x,y) in enumerate(((5,1),(13,12),(25,1),(30,10),(47,3),(53,8),(1,9))):
            c.put(x+(pulse//3+i)%3,y,';' if (i+pulse)%3 else '*','red')

def _render(who,t):
    word,top,bottom,px,tx,ty,accent,duration=CARD[who]
    t=max(0,min(t,duration))
    c=Canvas()
    if t<.68:
        _charge(c,t,accent)
        return '01 / MASKS IN',c.finish()
    if t<.96:
        _impact(c,t-.68,accent)
        return '02 / ALL-OUT IMPACT',c.finish()
    _motif(c,who,t)
    shift=max(0,round(13*(1-(t-.96)/.34)))
    dx=-shift if px<20 else shift
    _paint_portrait(c,who,px+dx,2)
    if t>=1.10:
        # Drop the type in, followed by the signature stamp/baseline.
        dy=max(0,round(5*(1-(t-1.10)/.23)))
        c.put(tx,ty-2-dy,' '+top+' ',accent,opaque=True)
        _type(c,tx,ty-dy,word,accent,who)
        if t>=1.44:c.put(tx,ty+6,' '+bottom+' ','white',opaque=True)
    return ('03 / FINISHING TOUCH' if t<1.44 else '03 / '+who.upper()+' FINISH'),c.finish()

def _scene(who):
    return lambda elapsed: _render(who,elapsed)

SCENES={TITLES[who]:(card[-1],_scene(who)) for who,card in CARD.items()}
