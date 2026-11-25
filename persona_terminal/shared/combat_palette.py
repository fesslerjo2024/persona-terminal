"""Shared attack pigments and monochrome markers for the terminal suite."""
from .reel_palette import IDS as SCENE_INKS

from .terminal_constants import CYAN, GOLD, GREEN, RED, WHITE

# Stable element colors and single-cell symbols. Affinity results keep their
# separate W/R/N/etc. palette, and monochrome terminals still have the symbols.
P3_MARKS={
    'Slash':('╱',SCENE_INKS['rose']),
    'Strike':('■',SCENE_INKS['ochre']),
    'Pierce':('▸',SCENE_INKS['violet']),
    'Fire':('▲',RED),
    'Ice':('◇',SCENE_INKS['navy']),
    'Electric':('ϟ',GOLD),
    'Wind':('≈',GREEN),
    'Light':('✦',WHITE),
    'Dark':('●',SCENE_INKS['wine']),
    'Almighty':('◆',SCENE_INKS['teal']),
}

P5_MARKS={
    'Physical':P3_MARKS['Slash'],
    'Gun':('▪',SCENE_INKS['ochre']),
    **{element:P3_MARKS[element] for element in ('Fire','Ice','Electric','Wind')},
    'Psy':('✧',SCENE_INKS['violet']),
    'Nuclear':('⊕',CYAN),
    'Bless':P3_MARKS['Light'],
    'Curse':P3_MARKS['Dark'],
    'Almighty':P3_MARKS['Almighty'],
}
