"""Optional Exam Room sequence. The terminal keeps no player/save state.

Adapted from the original English consultation scripts
fscr0162_009_100, fscr0162_009_110, fscr0162_009_120:
https://mysh.dev/tools/persona/5r/files/dataR.cpk/script/field
and recorded play: https://www.youtube.com/watch?v=WnPB3-rTrDs .
Prompts, candidate responses, and huddles below are original paraphrases.
The treatment detour is signaled rather than adding an extra combat gate.
"""
from battle_ui import CYAN, DIM, ESC, GOLD, GREEN, RED, WHITE


EXAMS = (
    (
        "A FRIEND IN TROUBLE",
        "At school, a threatening group leads your friend away. "
        "Charge in alone and you could both get hurt; find a teacher "
        "and you may be too late.",
        ("Confront the group yourself.", "Find someone who can help your friend."),
        "B",
        "A teacher might not get there in time, but Maruki doesn't "
        "want a second person getting hurt. Which route tries to help "
        "without putting you in the fight?",
    ),
    (
        "THE DREAM THAT WON'T MOVE",
        "You've worked for years toward a dream that still won't come "
        "true. It hurts to keep trying. If you stop now, all that work "
        "may have been for nothing.",
        ("Stay with the same goal and keep working.", "Get there at any cost.",
         "Leave that goal behind and pursue a different dream."),
        "C",
        "Maruki objects to hurting others, and he sees wearing yourself "
        "down for a dream as another kind of harm. What gives you a way out?",
    ),
    (
        "THE POWER TO CHANGE HEARTS",
        "Imagine you could change anyone's thoughts or feelings without "
        "ever being caught. The exam asks what you'd do with that power.",
        ("Take secrets that could make you money.", "Leave every heart alone.",
         "Rewrite your own heart to ease your pain.",
         "Change harmful hearts to build a better society.",
         "Make the person you love feel the same way."),
        "D",
        "Maruki distrusts using the power for personal gain. But he also "
        "thinks someone with the means to end other people's suffering "
        "shouldn't just stand by.",
    ),
)


class LabConsultation:
    """CampaignApp adapter: draw(app); key(k) -> None / solved / bypass / back."""

    def __init__(self):
        self.result = None
        self._reset()

    def _reset(self):
        self.room = 0
        self.huddle = False
        self.notice = "ORACLE / Answer as Maruki would, not as yourself."
        self.notice_color = GOLD

    def key(self, k):
        if self.result:
            return self.result
        if k in (ESC, 27):
            self.result = "back"
        elif isinstance(k, str) and len(k) == 1:
            key = k.upper()
            if key == "S":
                self.result = "bypass"
            elif key == "X":
                self._reset()
            elif key == "H":
                self.huddle = not self.huddle
            else:
                _, _, choices, expected, _ = EXAMS[self.room]
                if key not in "ABCDE"[:len(choices)]:
                    return None
                if key != expected:
                    self.notice = "Treatment detour flagged. Try another elevator."
                    self.notice_color = RED
                elif self.room + 1 == len(EXAMS):
                    self.result = "solved"
                else:
                    self.room += 1
                    self.huddle = False
                    self.notice = f"Elevator {key} accepted. The next exam is ready."
                    self.notice_color = GREEN
        return self.result

    def draw(self, app):
        title, situation, choices, _, clue = EXAMS[self.room]
        app.frame("LAB / EXAM ROOM", "A–E ANSWER   H HUDDLE   X RESET   S SKIP   ESC BACK")
        app.put(4, 3, f"CONSULTATION {self.room + 1}/{len(EXAMS)}  /  {title}", GOLD, True)
        app.lines(6, 3, situation, limit=4)
        for idx, answer in enumerate(choices):
            app.put(11 + idx, 3, f"[{'ABCDE'[idx]}]", CYAN, True)
            app.put(11 + idx, 7, answer, WHITE)
        if self.huddle:
            app.lines(17, 3, "HUDDLE / " + clue, limit=3, color=CYAN)
        else:
            app.put(17, 3, "H to compare notes with the team.", DIM)
        app.lines(app.h - 4, 3, self.notice, limit=1, color=self.notice_color)
