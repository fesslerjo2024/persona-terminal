"""Original short, interactive scenes for the summer and autumn story route.

The club intercut preserves Junpei's absence and the existing Hermit debrief.
The Medea scene always plays the same outcome; the choices follow the action.
References: recorded September operation https://www.youtube.com/watch?v=imeLsTFqkEM
and November confrontation https://www.youtube.com/watch?v=K5-bMBOWfHY&t=755s.
"""

SCENES={
    'pharos-visit':('bedside',{
        'bedside':(
            'THE BOY AT THE BEDSIDE','dorm',
            ('The boy from the dorm lobby is sitting beside your bed. '
             'You never heard the door. “You can call me Pharos,” he says.',),
            (('Ask about the contract','paper'),('Listen','quiet')),
        ),
        'paper':(
            'THE CONTRACT','dorm',
            ('“The paper was only the beginning,” Pharos says. '
             'He looks at the hand you signed with. “You’ve made other choices since then.”',),
            (('Let him finish','quiet'),),
        ),
        'quiet':(
            'BACK TO SLEEP','dorm',
            ('A car passes outside. When you look back from the window, '
             'the chair is empty. You say his name once, just to remember it.',),
            (('Turn out the light',None),),
        ),
    }),
    'shinjiro':('recruit',{
        'recruit':(
            '09/03 / THE DORM LOUNGE','dorm',
            ('Akihiko shifts over to make room. Shinjiro stays by the door. '
             'When Mitsuru mentions Ken is living here now, his hand goes still on the latch.',),
            (('Make room for Shinjiro','return'),('Ask if he knows Ken','ken')),
        ),
        'ken':(
            'A NAME AT THE DOOR','dorm',
            ('Shinjiro looks toward the stairs. “Is he upstairs?” '
             'Akihiko nods. Shinjiro lets go of the latch, but doesn’t move to leave.',),
            (('Wait for him','return'),),
        ),
        'return':(
            'BACK WITH S.E.E.S.','dorm',
            ('“Put me on the roster,” Shinjiro says. Akihiko slides the list '
             'across the table. Shinjiro takes the pencil.',),
            (('Update the roster',None),),
        ),
    }),
    'club':('outside',{
        'outside':(
            '09/05 / OUTSIDE CLUB ESCAPADE','club',
            ('You count the team at the entrance. Junpei’s the only one missing. '
             'Shinjiro says Junpei told him he wouldn’t make the briefing.',),
            (('Try Junpei’s phone','missed'),('Check the club entrance','cutaway')),
        ),
        'missed':(
            'NO ANSWER','club',
            ('The call rings out. You can still hear music from inside, '
             'but the club’s neon has stopped flickering.',),
            (('Look toward the service door','cutaway'),),
        ),
        'cutaway':(
            'BEHIND THE CLUB','station-alley',
            ('Junpei knows Chidori from their talks after school. He’d let her think he led S.E.E.S.',
             'She blocks his way. “Tell your team to call off the fight.”'),
            (('Return to S.E.E.S.','signal'),),
        ),
        'signal':(
            'BACK AT THE ENTRANCE','club',
            ('Fuuka finds the Shadow under the dance floor. '
             'She checks the entrance once more. Junpei still hasn’t come back.',),
            (('Follow Fuuka’s signal',None),),
        ),
    }),
    'medea':('shot',{
        'shot':(
            '11/22 / AFTER THE FIGHT','station-alley',
            ('Chidori lowers her weapon. Junpei starts toward her. '
             'Takaya fires before anyone can cross the distance. Junpei falls.',),
            (('Check Junpei','check'),),
        ),
        'check':(
            'BESIDE JUNPEI','station-alley',
            ('You kneel next to Junpei and call his name. No answer. '
             'Chidori comes close enough for you to hear her breathing. “Let me.”',),
            (('Step aside','choice'),),
        ),
        'choice':(
            'CHIDORI’S CHOICE','station-alley',
            ('Chidori takes Junpei’s hand. “I know what it will cost,” she says. '
             'She doesn’t look to Takaya or to you for permission.',),
            (('Give her room','medea'),),
        ),
        'medea':(
            'MEDEA','station-alley',
            ('Medea appears behind Chidori. The light gathers around their joined hands. '
             'As it leaves Chidori, Junpei takes a breath.',),
            (('Stay with them','morning'),),
        ),
        'morning':(
            '11/23 / TWO FLAMES','dorm',
            ('When Junpei wakes, he asks where Chidori is. His own Persona answers first. '
             'Hermes and Medea have become Trismegistus.',),
            (('Return to the calendar',None),),
        ),
    }),
}
