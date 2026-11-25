"""Dated campaign spine for the latter half of Persona 3 Reload.

Original condensed scenes; references are captured gameplay, not copied dialogue:
https://www.youtube.com/watch?v=TmJVOkf4B-w&t=284s
https://www.youtube.com/watch?v=tAfniKvSOQg&t=1335s
https://www.youtube.com/watch?v=DZeopghkZ0k&t=1226s
https://www.youtube.com/watch?v=YhKutNpiiNU&t=406s
https://www.youtube.com/watch?v=bfs3xWP1ltI
https://www.youtube.com/watch?v=EgQ_Ywd8Fbw&t=10920s
"""
from datetime import date

def when(month,day):
    return date(2009 if month>=4 else 2010,month,day)

KEN=when(8,28)
SHINJIRO=when(9,3)
OCT=when(10,4)
OCT_AFTER=when(10,5)
NOV=when(11,3)
NOV_AFTER=when(11,4)
IKUTSUKI=when(11,5)
RYOJI=when(11,9)
CHIDORI=when(11,22)
CHIDORI_AFTER=when(11,23)
RYOJI_RETURN_WALK=when(11,26)
BRIDGE=when(12,2)
AIGIS=when(12,30)
DECISION=when(12,31)
JANUARY=when(1,1)
FINALE=when(1,31)
RETURN=when(3,3)
REMEMBER=when(3,4)
ENDING=when(3,5)

SHINJIRO_THROUGH=OCT
SUMMIT_IDS=('strega-jin','strega-takaya','nyx-avatar')
SUMMIT_PHASES=('summit-jin','summit-takaya','summit-nyx')
STORY_DAYS={
    KEN:('AUGUST 28 / KEN','dorm',('Ken joins the team. He has a spear, a steady hand, and a reason for wanting to fight Shadows.',)),
    RYOJI:('THE TRANSFER STUDENT','dorm',(
        'Ryoji arrives at Gekkoukan and falls in step beside Junpei. Aigis cannot explain why she wants him to stay away from Makoto.',
    )),
    RYOJI_RETURN_WALK:('WALK HOME','dorm',(
        'Ryoji waits by the school gate. He wants to know which shops stay open late. You walk as far as the station before either of you checks the time.',
    )),
    AIGIS:('WHAT AIGIS CHOOSES','dorm',(
        'Aigis returns to the dorm. Staying with the others is no longer an order. It is the first thing she has decided for herself.',
    )),
}
STORY_NAMES={day:entry[0] for day,entry in STORY_DAYS.items()}
AFTERMATH_PHASES={'station-aftermath':OCT_AFTER,'bridge-aftermath':NOV_AFTER}
AFTERMATH_FOR={'fortune-strength':'station-aftermath','hanged-man':'bridge-aftermath'}
PHASE_DAYS={**AFTERMATH_PHASES,'october':OCT,'november':NOV,'chidori':CHIDORI,'decision':DECISION,
            'finale':FINALE,**dict.fromkeys(SUMMIT_PHASES,FINALE),'ending':ENDING}
MAJOR_DAYS=(KEN,SHINJIRO,when(9,10),OCT,when(10,6),NOV,IKUTSUKI,when(11,6),RYOJI,CHIDORI,RYOJI_RETURN_WALK,
            BRIDGE,when(12,10),AIGIS,DECISION,FINALE)
PHASE_FOR_DAY={OCT:'october',NOV:'november',CHIDORI:'chidori',DECISION:'decision',FINALE:'finale'}
AFTER_BATTLES={'fortune-strength':(OCT_AFTER,650),'hanged-man':(NOV_AFTER,850),'chidori':(CHIDORI_AFTER,490)}
OPERATION={
    'october':('OCTOBER 4 / IWATODAI STATION','fortune-strength','bridge',(
        'There are two readings near the station. Ken and Shinjiro are not responding. The rest of S.E.E.S. will take the operation.',
    )),
    'november':('NOVEMBER 3 / MOONLIGHT BRIDGE','takaya-jin','bridge',(
        'Fuuka locates the twelfth Shadow at Moonlight Bridge. Ikutsuki told you all twelve must fall to end the Dark Hour. Strega is blocking the way.',
    )),
    'chidori':('NOVEMBER 22 / CHIDORI','chidori','bridge',(
        'Chidori, the Strega member S.E.E.S. took to the hospital after Escapade, has left. Junpei went after her. Find him before Strega does.',
    )),
    'finale':('JANUARY 31 / TARTARUS SUMMIT','strega-jin','stars',(
        'The Dark Hour has begun. Climb past the last relay and meet Nyx above Tartarus.',
    )),
}
INTERLUDES={
    JANUARY:('JANUARY 1 / THE NEW YEAR','roof',(
        'S.E.E.S. chooses to face Nyx. On the first morning of the year, nobody asks what they might have forgotten.',
        'Adamah is open. The summit can be reached on January 31.',
    )),
}
SUMMIT_HEADS=(
    ('259F / JIN','Jin blocks the stairs. He has prepared for the way you fight.'),
    ('263F / TAKAYA','Takaya waits alone at the next landing. Nyx is close now.'),
    ('264F / NYX AVATAR','Above Tartarus, the moon hangs low enough to blot out the sky.'),
)
TRUE_END=(
    ('MARCH 3 / AN ORDINARY DAY','roof','The city has moved on. Makoto walks home while the others try to remember what feels missing.'),
    ('MARCH 4 / ONE LAST PROMISE','stars','The others talk about graduation. Makoto listens, waiting for someone else to remember the promise.'),
    ('MARCH 5 / THE ROOFTOP','roof','The others remember their promise and hurry upstairs. In the spring sun, Aigis holds Makoto as he closes his eyes.'),
)
BAD_END=(
    ('MARCH 5 / GRADUATION','bad','The class graduates. Nobody remembers the Dark Hour, but the uneasiness never lifts.'),
    ('MARCH 5 / AFTER THE CEREMONY','bad','Makoto and his friends decide to sing one more song. Somewhere outside, the world keeps getting quieter.'),
)
