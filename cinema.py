"""Central lookup for authored terminal cinematics and their exact runtime."""
from functools import cache

import oracle_scene
import wrestling_scene


@cache
def _catalog():
    # Deferred imports avoid dependency cycles; some scene modules reuse
    # cut-in titles, and cutins.duration routes through this registry.
    import allout_scenes
    import showtime_finales
    import showtime_openers
    import showtime_stage

    authored = {}
    sets = (
        {wrestling_scene.TITLE: (wrestling_scene.SECONDS, wrestling_scene.render)},
        oracle_scene.SCENES, allout_scenes.SCENES, showtime_finales.SCENES,
        showtime_openers.SCENES, showtime_stage.SCENES,
    )
    for scenes in sets:
        duplicate = authored.keys() & scenes.keys()
        if duplicate:
            raise ValueError(f'Duplicate cinematics: {sorted(duplicate)}')
        authored.update(scenes)
    return authored


def get(title):
    return _catalog().get(title)
