"""Original late-story scenes based on recorded Persona 3 Reload and its script.

The bridge and graduation references are at:
https://www.youtube.com/watch?v=_HkXOc57bmU&t=20984s
https://www.youtube.com/watch?v=_HkXOc57bmU&t=31287s
Source events 100, 121–123, and 150 in the extracted Reload script.
"""

BRIDGE_NEXT_DAY = frozenset(('warning', 'offer'))

SCENES = {
    'pharos-farewell': ('sunlight', {
        'sunlight': (
            'NOVEMBER 4 / AT THE BEDSIDE', 'dorm',
            ('Sunlight reaches the foot of the bed. Pharos is there. He’s never come during the day before.',),
            (('Sit up and listen', 'farewell'),),
        ),
        'farewell': (
            'A LAST VISIT', 'dorm',
            ('Pharos: “Everything’s come back to me. I know where I have to go now. But I wanted to see you once more before I left.”',),
            (('Tell him you’ll remember him', 'empty'), ('Ask if he has to go', 'empty')),
        ),
        'empty': (
            'THE DOOR STAYS CLOSED', 'dorm',
            ('Pharos smiles, though his eyes are wet. Then the space at the foot of the bed is empty. You never hear the door open.',),
            (('Go downstairs', None),),
        ),
    }),
    'bridge': ('crossing', {
        'crossing': (
            'DECEMBER 2 / MOONLIGHT BRIDGE', 'stars',
            ('Ryoji leans on the railing. He’s still awake in the Dark Hour. For the first time, Aigis knows exactly why that frightens her.',),
            (('Watch Aigis approach', 'recognition'),),
        ),
        'recognition': (
            'AT THE RAILING', 'stars',
            ('Aigis: “I fought you on this bridge ten years ago.” Ryoji backs away. Then he remembers the name he had then: Death.',),
            (('Stand your ground', 'reading'),),
        ),
        'reading': (
            'IWATODAI DORM / LOST SIGNAL', 'dorm',
            ('Fuuka felt a Persona flare and then lost contact with Aigis. Now she’s found a faint signal on Moonlight Bridge.',),
            (('Follow Fuuka’s reading', 'search'),),
        ),
        'search': (
            'BACK AT THE CROSSING', 'stars',
            ('Aigis is down. Koromaru barks beside her. Ryoji is still here, but he makes no move to stop you when you kneel.',),
            (('Check on Aigis', 'child'),),
        ),
        'child': (
            'THE CHILD ON THE BRIDGE', 'stars',
            ('Ryoji: “She couldn’t destroy me, so she sealed me inside a child who was here that night. That child was you, Makoto.”',),
            (('Think back to Pharos', 'connection'),),
        ),
        'connection': (
            'THE VOICE YOU KNEW', 'stars',
            ('The boy at your bedside called himself Pharos. Ryoji is the same person. He tries to say more, then his knees give out.',),
            (('Bring them both home', 'warning'),),
        ),
        'warning': (
            'THE NEXT EVENING', 'dorm',
            ('Ryoji tells S.E.E.S. why Death is called the Appriser: his arrival means Nyx is coming.',
             'If Nyx reaches humanity, human life will end. That’s the Fall.'),
            (('Ask if the Fall can be stopped', 'offer'),),
        ),
        'offer': (
            'BEFORE THE YEAR ENDS', 'dorm',
            ('Ryoji offers to let you kill him on December 31. The Fall would still come, but you’d forget the Dark Hour and wouldn’t know to fear it.',),
            (('Leave the decision for December 31', None),),
        ),
    }),
    'roof': ('knock', {
        'knock': (
            'MARCH 5 / A KNOCK AT THE DOOR', 'dorm',
            ('Aigis is on the other side of the door. It’s graduation day. The ceremony has already begun, but her voice is unsteady.',),
            (('Let Aigis in', 'remember'),),
        ),
        'remember': (
            'AIGIS REMEMBERS', 'dorm',
            ('Aigis: “I remember the Dark Hour. And I remember us, before we climbed. Do you still know where we were going to meet?”',),
            (('Walk with her to the roof', 'speech'),),
        ),
        'speech': (
            'GEKKOUKAN / GRADUATION', 'bridge',
            ('At the podium, Mitsuru reaches the part about her father’s sudden illness. The words stop her. In the audience, Yukari looks up.',),
            (('Hear what Mitsuru says next', 'remembered'),),
        ),
        'remembered': (
            'THE PROMISE COMES BACK', 'bridge',
            ('Mitsuru puts down her notes. She says she won’t turn away from the future. Junpei gets to his feet. They know where to go.',),
            (('Return to the roof', 'spring'),),
        ),
        'spring': (
            'THE SCHOOL ROOFTOP', 'roof',
            ('Aigis: “I used to protect you because I was told to. I’d choose it now, even if nobody told me to.” The wind lifts her ribbon.',),
            (('Listen for the others', 'footsteps'),),
        ),
        'footsteps': (
            'FOOTSTEPS ON THE STAIRS', 'roof',
            ('Someone calls your name from the stairs. Aigis looks down at you. They’re almost here. You don’t have to get up.',),
            (('Let yourself rest', None),),
        ),
    }),
}
