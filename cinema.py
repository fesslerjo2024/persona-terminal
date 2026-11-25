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


def paint(title,t,width,height):
    """Compose in real terminal cells on every frame, including after resize."""
    import wide_wrestling
    import wide_oracle
    import wide_allout
    import wide_locations
    from wide_canvas import Canvas

    if title == wrestling_scene.TITLE:
        return wide_wrestling.render(t,width,height)
    if title in oracle_scene.SCENES:
        return wide_oracle.render(title,t,width,height)
    from cutins import ALL_OUT
    if any(card[0]==title for card in ALL_OUT.values()):
        return wide_allout.render(title,t,width,height)
    beat,action = get(title)[1](t)
    left=(width-wrestling_scene.WIDTH)//2
    # Raise the action slightly on extra-tall terminals. The new foreground
    # has room below without introducing a letterboxed matte.
    top=(height-wrestling_scene.HEIGHT)//2-(height>=32)
    screen=Canvas(width,height)
    wide_locations.paint(screen,title,t,left,top,width,height)
    screen.overlay(action,left,top)
    return beat,screen.finish()
