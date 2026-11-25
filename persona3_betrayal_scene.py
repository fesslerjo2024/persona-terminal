"""The November 4 betrayal, staged as a short terminal story.

Reload gameplay reference: https://www.youtube.com/watch?v=_HkXOc57bmU&t=16812s
The bell, Dark Hour, observatory, and reversal also correspond to the
extracted Reload events 101–102. The text and choices here are original.
"""
ENTRY = 'dorm'
SOURCE = 'https://www.youtube.com/watch?v=_HkXOc57bmU&t=16812s'

# Art is existing scenery. The optional photograph is perspective, not
# a progression item. As Aigis, the player acts only on her refusal.
SCENE = {
    'dorm': (
        'NOVEMBER 4 / THE CELEBRATION', 'dorm',
        ('You beat the twelfth Shadow. The Dark Hour was supposed to be over.',
         'Then the dorm clock stops at midnight. The Kirijo guests turn into coffins.'),
        (('Follow the sound of the bell', 'bell'), ('Look at the group photo', 'photo')),
    ),
    'photo': (
        'THE MISSING FACES', 'dorm',
        ('Everyone meant to take another photo once Aigis and Ikutsuki arrived. The shutter never clicked a second time.',),
        (('Follow the sound of the bell', 'bell'),),
    ),
    'bell': (
        'A BELL IN THE DARK', 'tartarus',
        ('The bell comes from Tartarus. Mitsuru leads the way. Aigis is at the entrance beside Ikutsuki. She doesn’t turn when they call to her.',),
        (('Approach Aigis', 'reveal'),),
    ),
    'reveal': (
        'AT THE FOOT OF TARTARUS', 'tartarus',
        ('Ikutsuki palms a controller. He tells S.E.E.S. the twelve Shadows were pieces of Death. Every victory put another piece back in place.',),
        (('Reach for your Evoker', 'observatory'),),
    ),
    'observatory': (
        'THE SCHOOL OBSERVATORY', 'tartarus-roof',
        ('Aigis moves before Makoto can draw. He wakes bound to a cross. Across the room, Ikutsuki tells Aigis to shoot Takeharu Kirijo.',),
        (('Watch Aigis', 'refuse'),),
    ),
    'refuse': (
        'AIGIS / THE LAST ORDER', 'tartarus-roof',
        ('Aigis holds her fire. Ikutsuki draws his own gun. Two shots ring out; Takeharu falls. Then Ikutsuki orders her to kill the others.',),
        (('Free your teammates', 'release'),),
    ),
    'release': (
        'THE RESTRAINTS OPEN', 'tartarus-roof',
        ('Aigis frees S.E.E.S. Koromaru snatches the controller when Ikutsuki tries again. Wounded and cornered, Ikutsuki goes over the edge.',),
        (('Follow Mitsuru', 'aftermath'),),
    ),
    'aftermath': (
        'AFTER THE BELL', 'dorm',
        ('Mitsuru kneels beside her father. Aigis waits by the stairs until Akihiko helps Mitsuru up. Nobody speaks on the way home.',),
        (('Return to the dorm', None),),
    ),
}
