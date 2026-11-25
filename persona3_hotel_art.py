"""Original terminal scenery for the July full moon at Champs de Fleurs."""
from persona3_environment_reels import hotel_arrival, hotel_mirror, hotel_wipe
from persona3_scenic_detail import hotel_still

DURATION = 1.4


def render(scene,t,w,h):
    """Return clipped native cells. Story state, controls and saves stay outside."""
    t=max(0.,min(float(t),DURATION))
    if scene=='intro':return hotel_wipe(t,w,h,DURATION)
    if scene=='arrival':return hotel_arrival(t,w,h)
    if scene=='mirror':return hotel_mirror(t,w,h)
    return hotel_still(scene,t,w,h)
