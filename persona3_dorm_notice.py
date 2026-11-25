"""Dated, original notes from teammates. No reminders or story unlock logic."""
from dataclasses import dataclass
from datetime import date

import persona3_arqa as arqa
import persona3_late as late
import persona3_yabbashah as yabba
import persona3_yabbashah_upper as high


@dataclass(frozen=True)
class DormNote:
    author: str
    body: str


_NOTES={
    arqa.AKIHIKO_JOINS:DormNote('Akihiko',"I'm cleared to fight again. If you're climbing tonight, I'm in."),
    arqa.BRIDGE:DormNote('Fuuka',"The new gauges don't all charge the same way. Let's try them out."),
    yabba.OPENS:DormNote('Fuuka',"A red door isn't part of the climb. Save it for when we've got SP."),
    high.OPENS:DormNote('Mitsuru',"Koromaru handles Dark attacks. Remember him when choosing a squad."),
    late.KEN:DormNote('Ken',"I can take a turn healing if Yukari sits out. Just ask me."),
}


def note_for(day: date) -> DormNote | None:
    """A note is current for its dated milestone, never a standing banner."""
    return _NOTES.get(day)


def lounge_line(day: date) -> str:
    """Original low-key dorm flavor; the existing lounge recovery perk is unchanged."""
    if day>=late.AIGIS:return 'Aigis sets out an extra mug. “For after patrol.”'
    if day>=arqa.AFTER_RESCUE:return 'Fuuka leaves a thermos by the radio for tonight.'
    return 'Yukari puts the kettle on. Junpei brings the cups.'
