"""Silver-framed Shuffle Time reward cards, independent of game state."""
from persona_terminal.shared.terminal_constants import CYAN, DIM, GOLD, WHITE
from ..shared.reel_palette import IDS
from .persona3_menu_art import shuffle_plate

SILVER=IDS['slate']
BLUE=IDS['navy']
_KINDS=('persona','coin','cup')
_COLORS={'white':WHITE,'cyan':CYAN,'dim':DIM,'gold':GOLD,**IDS}


def draw(app,cards,selection):
    width=min(24,(app.w-12)//3)
    gap=2
    left=(app.w-(3*width+2*gap))//2
    for i,(name,reward,available) in enumerate(cards):
        x=left+i*(width+gap)
        focus=i==selection
        outline=CYAN if focus else SILVER if available else BLUE
        app.put(6,x,'╔'+'═'*(width-2)+'╗',outline,focus)
        for y in range(7,16):
            app.put(y,x,'║',outline)
            app.put(y,x+width-1,'║',outline)
        app.put(7,x+1,'◆'+'─'*(width-4)+'◆',outline)
        app.put(15,x+1,'◆'+'─'*(width-4)+'◆',outline)
        app.put(16,x,'╚'+'═'*(width-2)+'╝',outline,focus)
        artwork=shuffle_plate(_KINDS[i],width-4,7,available,focus)
        for y,runs in enumerate(artwork,8):
            col=x+2
            for text,ink in runs:
                if text.strip():app.put(y,col,text,_COLORS[ink],focus)
                col+=len(text)
        caption=f' {i+1} {name} '
        app.put(17,x+(width-len(caption))//2,caption,outline,focus,focus)
        app.put(19,x+(width-len(reward))//2,reward,WHITE if available else DIM,focus)
