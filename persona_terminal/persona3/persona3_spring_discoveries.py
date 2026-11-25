"""Original short scenes for the April arrival, June rescue and August bunker.

Recorded Reload anchors:
- April 6: https://www.youtube.com/watch?v=mGtdLakznyA
- June 8: https://heartbeat2.com/modhgggfx (5:38, 30:41, 31:57)
- August 6: https://www.youtube.com/watch?v=eZ5POMdLX5Y&t=166s

Optional observations are terminal additions. June folds Natsuki's earlier
account into the existing reunion so the search doesn't have to restart.
"""

SCENES={
    'arrival':('platform',{
        'platform':(
            '04/06 / LAST TRAIN TO IWATODAI','arrival',
            ('You’re Makoto, a new student at Gekkoukan. The last train pulls out, '
             'but the clock over the platform hasn’t moved. Your dorm lights are still on.',),
            (('Go to the dorm','boy'),),
        ),
        'boy':(
            '04/06 / THE DORM LOBBY','dorm',
            ('A boy you’ve never met is waiting at the desk. He turns a paper around '
             'so the blank signature line faces you.',),
            (('Read the paper','contract'),('Sign your name','key')),
        ),
        'contract':(
            '04/06 / THE CONTRACT','dorm',
            ('There’s no school seal. Just a sentence about owning the choices '
             'you make, and room at the bottom for your name.',),
            (('Sign your name','key'),),
        ),
        'key':(
            '04/06 / A ROOM KEY','dorm',
            ('The boy is gone when you look up. Yukari brings a room key and '
             'looks at the chair you were facing. She doesn’t ask.',),
            (('Head upstairs',None),),
        ),
    }),
    'fuuka':('reunion',{
        'reunion':(
            '06/08 / AT THE ENTRANCE','tartarus',
            ('You bring Fuuka back to the entrance. Her classmate Natsuki stops short. '
             '“We locked you in at school. I left you there. I thought someone would come.”',),
            (('Stay with them','shield'),),
        ),
        'shield':(
            '06/08 / LUCIA','tartarus',
            ('Two Shadows cut across the entrance. Fuuka steps in front of Natsuki. '
             'Her Persona, Lucia, appears between them and the Shadows.',),
            (('Listen to Fuuka','analysis'),),
        ),
        'analysis':(
            '06/08 / A VOICE IN TARTARUS','tartarus',
            ('Fuuka keeps her eyes on the Shadows. “Their defenses keep changing. '
             'Give me a moment and I can tell you where to strike.”',),
            (('Face the Shadows',None),),
        ),
    }),
    'bunker':('threshold',{
        'threshold':(
            '08/06 / THE UNDERGROUND PASSAGE','station-alley',
            ('Takaya is waiting beyond the threshold. “The Dark Hour gives people like us '
             'a world of our own. Why would you end it?” Jin stays by the door.',),
            (('Stay with the squad','sealed'),),
        ),
        'sealed':(
            '08/06 / THE DOOR SHUTS','tartarus',
            ('Takaya and Jin withdraw. The door slams behind them. '
             'Fuuka points deeper into the passage, where the Shadow is moving.',),
            (('Check the exit','door'),('Get the squad ready',None)),
        ),
        'door':(
            '08/06 / THE SEALED EXIT','tartarus',
            ('The handle won’t turn. Behind you, Aigis has already turned to '
             'face the sound coming down the passage.',),
            (('Get the squad ready',None),),
        ),
    }),
}
