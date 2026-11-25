"""Signature All-Out lettering, drawn as part of the final action pose."""
from ..shared.wide_canvas import Canvas
from ..shared.detail_canvas import DotCanvas

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

# Complete wording stays readable below the big display word. The words come
# from the in-game finishing touches; the layout and cell art are original.
MARKS = {
    'Joker': ("THE SHOW'S OVER", 'OVER', 'red', .26, 1.65),
    'Mona': ('MISSION ACCOMPLISHED', 'MISSION', 'cyan', .30, 1.64),
    'Skull': ("FREAKIN' BORING", 'BORING', 'gold', .25, 1.52),
    'Panther': ('omg!! We are SO awesome', 'OMG!', 'rose', .28, 1.48),
    'Fox': ('IT WAS FUN WHILE IT LASTED, GOODBYE.', 'GOODBYE', 'teal', .70, 1.79),
    'Queen': ('JUSTICE HAS PREVAILED.', 'JUSTICE', 'cyan', .29, 1.55),
    'Noir': ('Adieu', 'ADIEU', 'rose', .71, 1.72),
    'Crow': ('I DECIDE THE TRUTH', 'TRUTH', 'red', .27, 1.67),
    'Violet': ('Beauty is Devotion', 'DEVOTION', 'rose', .27, 1.60),
    'Oracle': ('Git Gud', 'GUD', 'green', .27, 2.10),
}


def apply(frame,who,t,w,h):
    phrase,display,ink,anchor,start=MARKS[who]
    if t<start:
        return frame
    c=Canvas(w,h)
    # Preserve every original cell first, including any background ink.
    for y,row in enumerate(frame):
        x=0
        for run,color in row:
            c.put(x,y,run,color,True)
            x+=len(run)
    margin=max(2,min(5,w//21))
    wide=4*len(display)-1
    left=max(margin,min(w-wide-margin,round(w*anchor-wide/2)))
    phase=min(1,(t-start)/.23)
    y=max(1,min(5,round(h*.075))-round(2*(1-phase)))
    skew=1 if who in ('Skull','Panther','Crow') else 0
    # Hand-set bitmap letters occupy the same cells as before, but each
    # pixel now has shape and depth on the 2×4 subcell grid.
    dots=DotCanvas(w,h)
    for j in range(5):
        a=left+skew*((4-j)//2)
        for i,ch in enumerate(display):
            bits=TYPE[ch].split('/')[j]
            for k,bit in enumerate(bits):
                if bit!='1':continue
                x0=(a+i*4+k)*2
                y0=(y+j)*4
                for dx in range(2):
                    for dy in range(4):
                        dots.put(x0+dx,y0+dy,'white' if dy==0 and (i+k)%3==0 else ink)
    for yy,row in enumerate(dots.finish()):
        x=0
        for run,color in row:
            if run.strip():c.put(x,yy,run,color)
            x+=len(run)
    x=max(margin,min(w-len(phrase)-margin,left+(wide-len(phrase))//2))
    c.put(x-1,y+6,' '+phrase+' ','white',True)
    for x0,d in ((left-4,-1),(left+wide+3,1)):
        c.put(x0,y+1,'⠢',ink)
        c.put(x0+d,y+2,'⠂',ink)
    return c.finish()
