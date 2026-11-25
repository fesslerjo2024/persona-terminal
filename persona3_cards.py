"""Silver-framed Shuffle Time reward cards, independent of game state."""
from battle_ui import CYAN, DIM, WHITE
from reel_palette import IDS

SILVER=IDS['slate']
BLUE=IDS['navy']
ART=(
    (' ╭╮     ╭╮ ',
     '╭╯╰──┬──╯╰╮',
     '╰╮ ◈ │ ◈ ╭╯',
     ' ╰──╲│╱──╯ ',
     '     ◆     '),
    ('  ╭─────╮  ',
     ' ╱  ╲│╱  ╲ ',
     '│─── ◆ ───│',
     ' ╲  ╱│╲  ╱ ',
     '  ╰─────╯  '),
    ('╔═════════╗',
     ' ╲ ▒▒▒▒▒ ╱ ',
     '  ╰──┬──╯  ',
     '     │     ',
     '   ══╧══   '),
)


def draw(app,cards,selection):
    width=min(24,(app.w-12)//3)
    gap=2
    left=(app.w-(3*width+2*gap))//2
    for i,(name,reward,available) in enumerate(cards):
        x=left+i*(width+gap)
        focus=i==selection
        outline=CYAN if focus else SILVER if available else BLUE
        icon=WHITE if focus and available else CYAN if available else SILVER
        app.put(6,x,'╔'+'═'*(width-2)+'╗',outline,focus)
        for y in range(7,16):
            app.put(y,x,'║',outline)
            app.put(y,x+width-1,'║',outline)
        app.put(7,x+1,'◆'+'─'*(width-4)+'◆',outline)
        app.put(15,x+1,'◆'+'─'*(width-4)+'◆',outline)
        app.put(16,x,'╚'+'═'*(width-2)+'╝',outline,focus)
        for y,line in enumerate(ART[i],9):
            app.put(y,x+(width-len(line))//2,line,icon,focus)
        caption=f' {i+1} {name} '
        app.put(17,x+(width-len(caption))//2,caption,outline,focus,focus)
        app.put(19,x+(width-len(reward))//2,reward,WHITE if available else DIM,focus)
