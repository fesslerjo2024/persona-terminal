"""Optional Chamber of Guilt board. Only local puzzle state; no save writes."""
import curses as C

from battle_ui import CYAN, DIM, ENTER, ESC, GOLD, GREEN, RED, WHITE


# The chamber's two successive slab patterns. 1 means the figure is ON.
SLABS = (
    ("The Blue Slab", (("B", "01010"),)),
    ("The Red and Blue Slab", (("R", "01100"), ("B", "10011"))),
)
LABELS = {"B": "BLUE", "R": "RED"}
COLORS = {"B": CYAN, "R": RED}


class PyramidSwitchboard:
    """CampaignApp adapter: draw(app); key(k) -> None / solved / bypass / back."""

    def __init__(self):
        self.slab = 0
        self.result = None
        self._initialize_slab()
        self.message = "MONA / Read the slab first. Those figures are switches."
        self.message_color = GOLD

    @property
    def pattern(self):
        return SLABS[self.slab][1]

    def _initialize_slab(self):
        self.flips = {row: [False] * 5 for row, _ in self.pattern}
        self.active = next(iter(self.flips))

    def _state(self, row):
        return "".join("1" if is_on else "0" for is_on in self.flips[row])

    def _submit(self):
        wrong = [LABELS[row] for row, expected in self.pattern
                 if self._state(row) != expected]
        if wrong:
            self.message = f"{' and '.join(wrong)} mismatch. The current settings stay put."
            self.message_color = RED
            return None
        if self.slab + 1 == len(SLABS):
            self.result = "solved"
            return self.result
        self.slab += 1
        self._initialize_slab()
        self.message = "MONA / One panel open. This one needs both rows."
        self.message_color = GREEN
        return None

    def key(self, key):
        if self.result:
            return self.result
        if key in (ESC, 27):
            self.result = "back"
        elif key in ENTER or key in (10, 13):
            return self._submit()
        elif isinstance(key, str):
            key = key.upper()
            if key == "S":
                self.result = "bypass"
            elif key == "X":
                self._initialize_slab()
                self.message = "Current slab reset. No progress lost."
                self.message_color = GOLD
            elif key in LABELS:
                if key not in self.flips:
                    self.message = "The red row is locked until the second slab."
                    self.message_color = GOLD
                else:
                    self.active = key
                    self.message = f"{LABELS[key]} selected. Toggle figures with 1–5."
                    self.message_color = COLORS[key]
            elif len(key) == 1 and key in "12345":
                index = int(key) - 1
                row = self.flips[self.active]
                row[index] = not row[index]
                self.message = ""
        elif key in (C.KEY_UP, C.KEY_DOWN) and len(self.flips) > 1:
            self.active = "R" if key == C.KEY_UP else "B"
            self.message = ""
        return self.result

    def draw(self, app):
        title, _ = SLABS[self.slab]
        app.frame("PYRAMID / SWITCHBOARD", "1–5 TOGGLE   ENTER CHECK   X RESET   S SKIP   ESC BACK")
        app.mid(4, f"CHAMBER OF GUILT / {self.slab + 1} OF {len(SLABS)}", GOLD, True)
        app.mid(6, title.upper(), WHITE, True)
        inscription = [(row, f"{LABELS[row]} {code}") for row, code in self.pattern]
        clue_width = 6 + sum(len(text) for _, text in inscription) + 5 * (len(inscription) - 1)
        clue_left = (app.w - clue_width) // 2
        app.put(8, clue_left, "SLAB:", WHITE, True)
        clue_x = clue_left + 6
        for row, text in inscription:
            app.put(8, clue_x, text, COLORS[row], True)
            clue_x += len(text) + 5
        app.mid(9, "Read left to right: 1 = ON, 0 = OFF.", DIM)
        start = max(3, (app.w - 37) // 2)
        app.put(11, start + 14, "  ".join(f"[{i}]" for i in range(1, 6)), DIM)
        for y, row in ((13, "R"), (15, "B")):
            selected = self.active == row
            app.put(y, start, f"{'>' if selected else ' '} {LABELS[row]:4} [{row}]",
                    COLORS[row] if row in self.flips else DIM, selected)
            if row not in self.flips:
                app.put(y, start + 14, "LOCKED ON THIS SLAB", DIM)
                continue
            for i, state in enumerate(self.flips[row]):
                app.put(y, start + 14 + i * 5, " ON" if state else "OFF",
                        COLORS[row] if state else DIM, state)
        app.mid(17, "B / R or ↑ / ↓ selects a row.", WHITE)
        if self.message:
            app.mid(19, self.message, self.message_color, True)
        app.mid(21, "Optional: S takes you straight to the ambush.", DIM)
