"""Authored native terminal clips, plus an explicit legacy cel test adapter."""
from functools import cache, partial
from typing import NamedTuple


class NativeClip(NamedTuple):
    seconds: float
    draw: object
    finisher: str | None = None
    contextual: bool = False


def _merge(*sets):
    catalog = {}
    for scenes in sets:
        duplicate = catalog.keys() & scenes.keys()
        if duplicate:
            raise ValueError(f'Duplicate cinematics: {sorted(duplicate)}')
        catalog.update(scenes)
    return catalog


@cache
def _native_catalog():
    # Every time comes from the same scene source used to draw the clip.
    import native_showtime
    import satanael_scene
    import wide_allout
    import wide_oracle

    def bind(draw, lengths):
        return {title: NativeClip(seconds, partial(draw, title))
                for title, seconds in lengths.items()}

    return _merge(
        {title: NativeClip(seconds, partial(wide_oracle.render, title),
                          'Oracle' if title == wide_oracle.TITLE else None, True)
         for title, (seconds, _, _) in wide_oracle._SCENES.items()},
        {title: NativeClip(wide_allout.SECS[actor], partial(wide_allout.render, title), actor, True)
         for title, actor in wide_allout.BY_TITLE.items()},
        bind(native_showtime.render, native_showtime.DURATIONS),
        bind(satanael_scene.render, {satanael_scene.TITLE: satanael_scene.SECONDS}),
    )


def has(title):
    return title in _native_catalog()


def duration(title):
    clip = _native_catalog().get(title)
    return clip.seconds if clip is not None else 0.0


def paint(title,t,width,height,*,finishing=True,cast=(),targets=0):
    """Draw directly at the current viewport size, never from a legacy cel."""
    clip = _native_catalog()[title]
    context = dict(cast=cast,targets=targets,finishing=finishing) if clip.contextual else {}
    beat,frame = clip.draw(t,width,height,**context)
    if finishing and clip.finisher is not None:
        from finishing_type import apply
        frame = apply(frame,clip.finisher,t,width,height)
    return beat,frame


@cache
def _legacy_catalog():
    # The old 57x15 frames remain for historical regression tests and are
    # not the authority for playback, native render selection, or duration.
    import allout_scenes
    import oracle_scene
    import showtime_finales
    import showtime_openers
    import showtime_stage
    import wrestling_scene

    return _merge(
        {wrestling_scene.TITLE: (wrestling_scene.SECONDS, wrestling_scene.render)},
        oracle_scene.SCENES, allout_scenes.SCENES, showtime_finales.SCENES,
        showtime_openers.SCENES, showtime_stage.SCENES,
    )


def get(title):
    """Legacy compact renderer lookup, retained for existing compatibility."""
    return _legacy_catalog().get(title)
