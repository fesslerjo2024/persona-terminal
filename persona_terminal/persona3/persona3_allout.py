"""Original terminal reinterpretations of Persona 3 Reload's All-Out finishers.

Visual reference: ATLUS' nine-card showcase, 14 December 2023,
https://x.com/p_kouhou/status/1735223109249020133 (direct game stills mirrored
at https://personacentral.com/p3r-aoa/), and the official SEGA character
reference sheets, https://www.sega.jp/topics/detail/231214_3/ .
The character shapes, typography, effects and choreography are drawn from
terminal cells. No frames or game graphics are bundled.
"""

from dataclasses import dataclass
from functools import lru_cache
from .persona3_finisher_detail import draw_finisher, draw_squad_rush
from .persona3_makoto_detail import detail_card

FINISHERS = ('Makoto', 'Yukari', 'Junpei', 'Akihiko', 'Mitsuru',
             'Aigis', 'Koromaru', 'Ken', 'Shinjiro')
FINISH_SECONDS = 2.24
IMPACT_SECONDS = .76


@dataclass(frozen=True)
class Poster:
    shadow: str
    mid: str
    glow: str
    words: tuple[str, str]
    left: bool = False


_POSTERS = {
    'Makoto': Poster('navy','teal','cyan',('DONE AND','DUSTED')),
    'Yukari': Poster('wine','rose','white',('THERE YOU','HAVE IT'),True),
    'Junpei': Poster('navy','violet','cyan',("THAT'S THE",'GAME!')),
    'Akihiko': Poster('dim','slate','white',('NEXT','BOUT')),
    'Mitsuru': Poster('wine','red','rose',('KNEEL','BEFORE ME'),True),
    'Aigis': Poster('ochre','gold','white',('TARGET','NEUTRALIZED')),
    'Koromaru': Poster('dim','slate','white',('WOOF!','WOOF! WOOF!')),
    'Ken': Poster('ochre','amber','gold',('HEAD HELD','HIGH')),
    'Shinjiro': Poster('wine','red','rose',('SAVE YOUR','BREATH'),True),
}

# A 3x5 single-cell block display gives lettering a large terminal silhouette
# without needing a font, game screenshot, or double-width characters.
_LETTERS = {
 'A':(' # ','# #','###','# #','# #'),'B':('## ','# #','## ','# #','## '),
 'C':(' ##','#  ','#  ','#  ',' ##'),'D':('## ','# #','# #','# #','## '),
 'E':('###','#  ','## ','#  ','###'),'F':('###','#  ','## ','#  ','#  '),
 'G':(' ##','#  ','# #','# #',' ##'),'H':('# #','# #','###','# #','# #'),
 'I':('###',' # ',' # ',' # ','###'),'J':('  #','  #','  #','# #',' # '),
 'K':('# #','# #','## ','# #','# #'),'L':('#  ','#  ','#  ','#  ','###'),
 'M':('# #','###','###','# #','# #'),'N':('# #','###','###','###','# #'),
 'O':(' # ','# #','# #','# #',' # '),'P':('## ','# #','## ','#  ','#  '),
 'Q':(' # ','# #','# #',' ##','  #'),'R':('## ','# #','## ','# #','# #'),
 'S':(' ##','#  ',' # ','  #','## '),'T':('###',' # ',' # ',' # ',' # '),
 'U':('# #','# #','# #','# #','###'),'V':('# #','# #','# #','# #',' # '),
 'W':('# #','# #','###','###','# #'),'X':('# #','# #',' # ','# #','# #'),
 'Y':('# #','# #',' # ',' # ',' # '),'Z':('###','  #',' # ','#  ','###'),
 ' ':(' ',' ',' ',' ',' '),"'":('#','#',' ',' ',' '),'!':('#','#','#',' ','#'),
}

def _letter(c,x,y,words,available,bg):
    letters=[[_LETTERS[ch] for ch in part] for part in words]
    widths=[sum(len(glyph[0])+1 for glyph in row)-1 for row in letters]
    block=next((i for i in (1,0) if widths[i]<=available),None)
    if block is None:
        c.put(x-1,y-1,(' '*min(available+2,max(map(len,words))+3),)*5,'dim',True)
        for i,part in enumerate(words):c.put(x,y+2*i,part,'white')
        return
    other=1-block
    by=y+2 if block else y
    sy=y if block else y+6
    c.put(x-1,y-1,(' '*(max(widths[block],len(words[other]))+3),)*9,'dim',True)
    c.put(x,sy,words[other],'white')
    c.put(x,sy+1,'-'*(len(words[other])+1),bg.mid)
    rows=tuple(' '.join(col[j].replace('#','█') for col in letters[block])
               for j in range(5))
    c.put(x+1,by+1,rows,'dim')
    c.put(x,by,rows,bg.glow)


def render_all_out(name, elapsed, w, h, *, finishing=True, cast=(), targets=3):
    """Return a full-viewport, read-only frame as the existing cut-in runs."""
    name=name if name in _POSTERS else 'Makoto'
    bg=_POSTERS[name]
    if not finishing or elapsed < .56:
        return draw_squad_rush(elapsed,w,h,cast,targets,IMPACT_SECONDS)
    t=elapsed-.56
    if name=='Makoto':
        c=detail_card(t,w,h)
        if t>.26:
            x,y=max(2,round(w*.065)),round(h*.50)
            crest=bg.words[1]
            width=4*len(crest)-1
            c.put(x-1,y-1,(' '*(width+3),)*9,'dim',True)
            c.put(x,y,bg.words[0],'white')
            c.put(x,y+1,'─'*width,'teal')
            for j in range(5):
                c.put(x,y+2+j,' '.join(_LETTERS[ch][j].replace('#','█') for ch in crest),
                      'cyan',True)
        return c.finish()
    if t>=.62:
        return _held_poster(name,w,h)
    return _active_poster(name,t,w,h)


@lru_cache(maxsize=24)
def _held_poster(name,w,h):
    # This pose is static; caching immutable runs saves most redraw work.
    return _active_poster(name,.62,w,h)


def _active_poster(name,t,w,h):
    bg=_POSTERS[name]
    c=draw_finisher(name,t,w,h,bg)
    if t>.24:
        x=round(w*.67) if bg.left else max(2,round(w*.045))
        y=round(h*(.39 if name in ('Aigis','Koromaru','Shinjiro') else .57))
        available=w-x-2 if bg.left else round(w*.34)
        if name=='Yukari':
            line=' '.join(bg.words)
            c.put(x-1,y-1,(' '*(len(line)+2),)*3,'dim',True)
            c.put(x,y,line,'white')
            c.put(x,y+1,'─'*len(line),'rose')
        else:
            _letter(c,x,y,bg.words,available,bg)
    return c.finish()
