"""Quiet calendar/radio motifs and responsive Tartarus floor transfer art."""
from wide_canvas import Canvas

ELEVATOR_SECONDS=1.35


def render_elevator(t,w,h,start_floor,destination):
    """Read-only native scene from entrance through a floor transfer."""
    from persona3_environment_reels import elevator
    if not w or not h:return Canvas(w,h).finish()
    return elevator(t,w,h,start_floor,destination,ELEVATOR_SECONDS)


def render(scene,t,w,h):
    """Draw optional calendar and rescue imagery under existing chrome."""
    from persona3_quiet_motion import render as band
    return band(scene,max(0.,float(t)),w,h)


def render_signal(t,w,h):
    return render('briefing',t,w,h)
