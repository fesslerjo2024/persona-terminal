"""Short, original scenes for the Yakushima trip and Yukari's discovery.

Scene order follows Reload's July 20, July 21, and November 5 beats.
The two clicks are an original continuity cue for a text-only rendition.
"""

VILLA_FRAGMENT='Two sharp clicks. “I let this go too far,” Eiichiro says. “What happens tonight is on me.”'

SCENES={
    'villa':('villa', {
        'villa':('YAKUSHIMA / KIRIJO VILLA','dorm',(
            'A Kirijo Group experiment went wrong ten years ago. Takeharu Kirijo says that’s when the Dark Hour began.',
            'Takeharu starts the tape. The scientist on screen is Yukari’s father, Eiichiro Takeba.',
        ),(('Watch the recording','tape'),)),
        'tape':('THE VILLA RECORDING','dorm',(
            VILLA_FRAGMENT,
            'The screen goes dark. Yukari steps outside.',
        ),(('Follow Yukari outside','terrace'),('Give Yukari a moment',None))),
        'terrace':('OUTSIDE THE VILLA','villa-shore',(
            'Yukari holds the railing. “I used to imagine what I’d ask him if I heard his voice again. I didn’t think I’d hear it like this.”',
        ),(('Stay with her a while',None),('Let her have the terrace',None))),
    }),
    'shore':('shore', {
        'shore':('YAKUSHIMA / THE SHORE','villa-shore',(
            'A girl at the waterline turns before you call to her. She looks past the others and straight at you.',
        ),(('Approach the girl','aigis'),('Look at the tracks in the sand','tracks'))),
        'tracks':('AT THE WATERLINE','villa-shore',(
            'One trail of footprints crosses the wet sand in a perfectly straight line. Not even the breakers knocked her off course.',
        ),(('Approach the girl','aigis'),)),
        'aigis':('AIGIS','villa-shore',(
            '“My name is Aigis. I can’t explain it yet, but I know I need to be near you.”',
            'When Mitsuru calls from the path, Aigis falls into step beside you.',
        ),(('Head back with Aigis',None),)),
    }),
    'recording':('fuuka', {
        'fuuka':('NOVEMBER 5 / THE RECOVERED FILE','dorm',(
            'Fuuka sets a disc beside Yukari. “I found another copy of the villa recording on Ikutsuki’s computer. It runs longer.”',
        ),(('Play the recovered recording','original'),)),
        'original':('EIICHIRO’S RECORDING','dorm',(
            'Two sharp clicks. Eiichiro looks into the lens.',
            '“I let this go too far. I’m shutting it down. We were never supposed to bring those Shadows together.”',
        ),(('Hear Yukari out','isis'),('Replay the July fragment','july-echo'))),
        'july-echo':('THE VILLA RECORDING / JULY','dorm',(
            VILLA_FRAGMENT,
            'The screen goes dark.',
        ),(('Hear Yukari out','isis'),('Compare what changed','difference'))),
        'difference':('WHAT THE VILLA DIDN’T SHOW','dorm',(
            'You recognize the clicks. The villa tape cut off before Eiichiro said he was shutting down the experiment.',
        ),(('Hear Yukari out','isis'),)),
        'isis':('YUKARI / ISIS','dorm',(
            'Yukari: “I’m still angry he didn’t come home. But the longer tape lets me hear what he tried to stop. I can carry that.”',
            'Io becomes Isis.',
        ),(('Return to the dorm',None),)),
    }),
}
