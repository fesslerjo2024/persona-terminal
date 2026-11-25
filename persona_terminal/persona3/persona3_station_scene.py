"""October 4 station outskirts and October 5 dorm: original scene adaptation.

Recorded Reload event: https://www.youtube.com/watch?v=wlP_szna7mE&t=1456s
Corroborating PC capture: https://www.youtube.com/watch?v=_HkXOc57bmU&t=14067s
The optional radio check and Makoto's quiet choices are terminal additions.
They do not change the outcome or stand in for Reload's linked episode.
"""

ENTRY='search'
AFTER_MIDNIGHT=frozenset(('aftermath','aftermath_akihiko'))

# title, art kind, body paragraphs, (choice label, next scene ID) pairs
SCENE={
    'search':(
        '10/04 / AFTER THE OPERATION','station-alley',
        ('The Shadows are gone. Fuuka still can’t reach Ken or Shinjiro. '
         'Akihiko is already heading toward the station outskirts.',),
        (('Check the radio','radio'),('Follow Akihiko','confrontation')),
    ),
    'radio':(
        '10/04 / THE RADIO','station-alley',
        ('The channel is silent. Mitsuru asks Akihiko to keep his radio on so '
         'the others can find him in the dark.',),
        (('Follow Akihiko','confrontation'),),
    ),
    'confrontation':(
        '10/04 / TATSUMI PORT ISLAND','station-alley',
        ('Ken: “Two years ago, you lost control of your Persona. My mother died.”',
         'Shinjiro doesn’t deny it. He waits for Ken to finish.'),
        (('Watch the alley','takaya'),),
    ),
    'takaya':(
        '10/04 / THE STATION OUTSKIRTS','station-alley',
        ('Takaya steps out of the dark. He says Shinjiro’s suppressants '
         'were already killing him. A shot rings out. Shinjiro drops.',),
        (('Look toward Ken','shield'),),
    ),
    'shield':(
        '10/04 / THE SECOND SHOT','station-alley',
        ('Takaya turns toward Ken. Shinjiro gets between them before the second shot. '
         'When Makoto reaches the alley, Takaya has fled.',),
        (('Go to Shinjiro','last_words'),),
    ),
    'last_words':(
        '10/04 / THE STATION OUTSKIRTS','station-alley',
        ('Akihiko kneels and takes Shinjiro’s hand. Shinjiro asks him to look after Ken. '
         'Akihiko keeps holding on after Shinjiro goes still.',),
        (('Stay with Akihiko','aftermath_akihiko'),('Stay beside Ken','aftermath')),
    ),
    'aftermath_akihiko':(
        '10/05 / THE EMPTY ROOM','dorm',
        ('At Shinjiro’s door, Akihiko starts to say what he’ll do next. The words won’t come. '
         'Makoto waits with him instead of filling the silence.',),
        (('Return to the calendar',None),),
    ),
    'aftermath':(
        '10/05 / THE EMPTY ROOM','dorm',
        ('Akihiko raises his hand to knock on Shinjiro’s door, then lets it fall.',
         'Ken is still by the stairs. Makoto sits down beside him.'),
        (('Return to the calendar',None),),
    ),
}
