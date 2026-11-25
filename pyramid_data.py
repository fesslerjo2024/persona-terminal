"""Pyramid of Wrath, Royal story in six original terminal operations.

Story references (the game scripts, with original footage for combat):
https://mysh.dev/tools/persona/5r/files/dataR.cpk/script/field (fscr0155)
https://mysh.dev/tools/persona/5r/files/dataR.cpk/event/event_data/message/e200 (e288–e299)
https://mysh.dev/tools/persona/5r/files/dataR.cpk/event/event_data/message/e300 (e300–e311)
https://www.youtube.com/watch?v=3jmbezV7wFA (English Royal, boss starts at 3:22:46)
Route compression, enemy formations, loadouts, rewards, and numbers are
terminal adaptations. No source dialogue. No supernatural diagnosis of Futaba.
"""
from battle_data import persona, shadow
from shuffle_data import SHUFFLE_ENEMIES


PERSONA_ADDITIONS = {
    'Anzu': persona(['Garula','Magarula','Masukukaja','Rakunda'],
                    {'Gun':'weak','Electric':'resist','Wind':'repel','Nuclear':'weak'},
                    'Wind • agility up • defense down'),
    'Isis': persona(['Kouga','Makouga','Diarama','Energy Shower'],
                    {'Psy':'weak','Bless':'null'},
                    'Bless • healing • party ailment recovery'),
    'Thoth': persona(['Freila','Mafreila','Megido','Dekaja'],
                     {'Psy':'weak','Nuclear':'null','Bless':'null','Curse':'resist'},
                     'Nuclear • Almighty • strip buffs'),
}


def _shadow(name,hp,sp,skills,**overrides):
    source=SHUFFLE_ENEMIES[name]
    return {**source,'hp':hp,'sp':sp,'skills':list(skills),
            'affinity':dict(source['affinity']),**overrides}


ENEMY_ADDITIONS = {
    'Pyramid Sandman': _shadow('Sandman',113,26,('Garula','Dormina')),
    'Pyramid Naga': _shadow('Naga',129,30,('Zionga','Rising Slash')),
    'Pyramid Anzu': _shadow('Anzu',125,29,('Garula','Sukukaja')),
    'Pyramid Lamia': _shadow('Lamia',138,31,('Eiga','Rising Slash')),
    'Pyramid Isis': _shadow('Isis',142,32,('Kouga','Diarama','Rakukaja'),behavior='support'),
    'Pyramid Thoth': _shadow('Thoth',162,35,('Freila','Psio','Tarukaja')),
    'Papyrus Bandit': shadow(188,36,['Garula','Tempest Slash','Sukukaja'],
                             {'Wind':'resist'},'aggressive',alias='Garuda'),
    'Coffin-Borne God': shadow(199,36,['Eiga','Tempest Slash','Makajam'],
                               {'Wind':'weak','Gun':'resist','Electric':'drain'},'ailment',alias='Mot'),
    'Jewel Warden': shadow(149,31,['Kouga','Rakukaja','Energy Drop'],
                            {'Bless':'null','Psy':'weak'},'support'),
    'Mural Shade': shadow(130,24,['Dazzler','Eiga'],
                           {'Physical':'resist','Wind':'weak'},'ailment'),
    'Cognitive Wakaba': shadow(650,75,['Garula','Rising Slash'],{},
                               'pyramid-wakaba',no_knockdown=True),
}

_BANK_PAIRS = (('Mona','Panther'),('Skull','Queen'))
_PYRAMID_PAIRS = _BANK_PAIRS + (('Fox','Skull'),)


NODES = (
    dict(id='pyramid-desert',region='Pyramid',title='Stolen Papyrus',map_mark='MAP',tactic='Recover the map / Split pressure',
         navigator='Mona',showtime_pairs=_PYRAMID_PAIRS,
         brief='Shadow Futaba sends the Thieves to a desert town for a map stolen by bandits.',
         story_before='Futaba asks the Thieves to change her heart. Her Palace is a pyramid that she believes will be her tomb. The Shadow offers a way inside if the team recovers the missing papyrus.',
         story_after='The bandit drops the papyrus. Shadow Futaba trades the team a sketch of the pyramid and points them toward the central stairway.',
         hint='The bandit moves quickly. Clear the lighter patrol, then keep one answer to a long exchange in reserve.',
         preview='A desert patrol, then the leader guarding the stolen papyrus.',
         waves=[['Pyramid Sandman','Pyramid Naga'],['Papyrus Bandit']],
         reward=dict(personas=['Anzu'],skill_cards=['Sukukaja'],credits=235,joker_sp=4)),
    dict(id='pyramid-light',region='Pyramid',title='Light Across the Chasm',map_mark='GEMS',tactic='Find gems / Turn the light',
         navigator='Mona',showtime_pairs=_PYRAMID_PAIRS,
         brief='Take the gems from the Anubis statues to their matching pedestals. Reflected light makes a way across the gap.',
         story_before='A boulder blocks the obvious passage. Slabs and statuettes mark a second route. The Thieves follow the light instead of trying to force the doors.',
         story_after='The gems light up the hidden bridge. Back at the main stairway, the first part of the mural catches the beam.',
         hint='Do not let the warden protect its attendant for free. Check attack effects and change elements rather than losing a turn to repeated absorption.',
         preview='Two small groups mark the buried gem route.',
         waves=[['Pyramid Anzu','Pyramid Naga'],['Jewel Warden','Pyramid Isis']],
         reward=dict(skill_cards=['Kouga'],credits=240,joker_hp=6)),
    dict(id='pyramid-guilt',region='Pyramid',title='Chamber of Guilt',map_mark='COFFIN',tactic='Read the slab / Break status pressure',
         navigator='Mona',showtime_pairs=_PYRAMID_PAIRS,
         brief='Read the stone slab before touching the switches. The wrong configuration sends the team down into a trap.',
         story_before='The chambers mix warning slabs with switchable colored figures. The team pieces the controls together but still tumbles into quicksand on its way toward the next hall.',
         story_after='The Coffin-Borne God falls. The Thieves reach the next reflecting chamber, but the voices behind the murals are harder to shake than the trap.',
         hint='Bring ailment recovery. Alternate a focused skill with attacks that can exploit a status instead of giving the chain away.',
         preview='One ambush after the trap: a coffin guardian and two attendants.',
         waves=[['Coffin-Borne God','Pyramid Lamia','Pyramid Naga']],
         reward=dict(personas=['Isis'],skill_cards=['Diarama'],credits=255,joker_sp=5)),
    dict(id='pyramid-murals',region='Pyramid',title='The Broken Murals',map_mark='MURAL',tactic='Restore memories / Open the path',
         navigator='Mona',showtime_pairs=_PYRAMID_PAIRS,
         brief='Reorder the mural fragments and turn the gallery mirrors. The ballista here breaks a wall; it is not part of the later boss battle.',
         story_before='The murals show painful pieces of Futaba’s past. The images are filtered through guilt and fear, not a reliable record of what happened to her mother.',
         story_after='A corridor opens when the last beam reaches the stairway. The team sees how often Futaba heard the same accusation and how hard it became to doubt it.',
         hint='Separate the heavy caster from its support. A well-timed buff wipe can undo more damage than another basic attack.',
         preview='The gallery’s first guard line and a heavier caster behind it.',
         waves=[['Pyramid Isis','Mural Shade'],['Pyramid Thoth','Pyramid Lamia']],
         reward=dict(personas=['Thoth'],skill_cards=['Dekunda'],credits=275,joker_hp=7)),
    dict(id='pyramid-door',region='Pyramid',title='The Door to Her Room',map_mark='DOOR',tactic='Secure the route / Deliver the card',
         navigator='Mona',showtime_pairs=_PYRAMID_PAIRS,
         brief='The final door echoes Futaba’s real bedroom. Secure the approach, then return to her with the calling card.',
         story_before='At the top of the stairs is a room no one can force open. The team fights only to secure the route; the decision to let them in is Futaba’s.',
         story_after='The calling card reaches Futaba. In the real world, she opens her door herself. The way through the heart of the pyramid finally responds.',
         hint='Save recovery for the later patrol. You do not have to rush past every Shadow to finish this route.',
         preview='A sentry pair and the last guard line before the sealed door.',
         waves=[['Pyramid Anzu','Jewel Warden'],['Pyramid Thoth','Mural Shade']],
         reward=dict(skill_cards=['Energy Shower'],credits=290,joker_sp=5)),
    dict(id='pyramid-boss',region='Pyramid',title='The Sphinx Above the Tomb',map_mark='SPHINX',tactic='Read the dive / Create an opening',
         navigator='Mona',showtime_pairs=_PYRAMID_PAIRS,pyramid_ballista=True,
         brief='Futaba’s fear has taken Wakaba’s shape. Hold on through the dive until Futaba can make an opening.',
         story_before='A Sphinx wearing Wakaba’s face comes out of the sky. It is a distortion made from Futaba’s fear, not Wakaba herself. Futaba steps into the Palace to face it.',
         story_after='Futaba’s Necronomicon helps the team bring the Sphinx down. Back outside, she stops Medjed and later joins the Thieves as their navigator, Oracle.',
         hint='Guard when the Sphinx climbs for a dive. Use the ballista when Futaba brings it online, then attack while the Sphinx is grounded.',
         preview='One prolonged fight, from the Sphinx’s first dive to Futaba’s counterattack.',
         waves=[['Cognitive Wakaba']],
         reward=dict(oracle=['support','guard','ufo'],slots=1,skill_cards=['Rakukaja'],
                     credits=425,joker_hp=8,joker_sp=6)),
)
