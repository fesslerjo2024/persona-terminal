"""Optional two-room scale puzzle, based on Royal field event fscr0159_020_100."""
from battle_ui import CYAN, DIM, ESC, GOLD, GREEN, RED, WHITE


class CruiserMouseRoute:
    """Original size/door tradeoff condensed to a reversible terminal route."""

    def __init__(self):
        self.result = None
        self.reset()

    def reset(self):
        self.room = "hall"
        self.statue = True
        self.info = "MONA / Small enough for a vent. Too small for a door."
        self.color = GOLD

    @property
    def mouse(self):
        return self.room == "hall" and self.statue

    def report(self, text, color=GOLD):
        self.info = text
        self.color = color

    def key(self, key):
        if self.result:
            return self.result
        if key in (ESC, 27):
            self.result = "back"
            return self.result
        if not isinstance(key, str):
            return None
        key = key.upper()
        if key == "S":
            self.result = "bypass"
        elif key == "X":
            self.reset()
        elif key == "V":
            if self.mouse:
                self.room = "service"
                self.report("Outside the statue's range. Human again.", GREEN)
            else:
                self.report("The vent is too small in human form.", RED)
        elif key == "T":
            if self.room == "service":
                self.statue = not self.statue
                self.report("Statue reactivated." if self.statue else
                            "Statue disabled. The hall is safe to cross.", CYAN)
            else:
                self.report("The statue switch is in the service room.", RED)
        elif key == "D":
            if self.room == "service":
                self.room = "hall"
                self.report("The active statue shrinks you again." if self.mouse
                            else "Still human. The main bulkhead is within reach.",
                            GOLD if self.mouse else GREEN)
            elif self.mouse:
                self.report("Too small to open the service door. Try the vent.", RED)
            else:
                self.room = "service"
                self.report("Service door opened. The switch is here.", CYAN)
        elif key == "E":
            if self.room != "hall":
                self.report("The main bulkhead is back in the statue hall.", RED)
            elif self.mouse:
                self.report("Too small to open the main bulkhead.", RED)
            else:
                self.result = "solved"
        return self.result

    def draw(self, app):
        app.frame("CRUISER / SERVICE DECK", "V VENT  T SWITCH  D DOOR  E EXIT  X RESET  S SKIP  ESC BACK")
        app.mid(5, "STATUE FIELD / SERVICE ROUTE", GOLD, True)
        app.mid(7, "HALL  <--- vent or service door --->  SERVICE ROOM", DIM)
        app.mid(9, "LOCATION: " + ("STATUE HALL" if self.room == "hall" else "SERVICE ROOM"), WHITE, True)
        app.mid(11, f"FORM: {'MOUSE' if self.mouse else 'HUMAN'}    /    STATUE: {'ON' if self.statue else 'OFF'}",
                GOLD if self.mouse else CYAN, True)
        if self.room == "hall":
            app.put(14, 5, "V  Vent into the service room (mouse only)", CYAN if self.mouse else DIM)
            app.put(15, 5, "D  Open the service door (human only)", DIM if self.mouse else WHITE)
            app.put(16, 5, "E  Open the main bulkhead (human only)", DIM if self.mouse else WHITE)
        else:
            app.put(14, 5, "T  Toggle the statue from outside its range", CYAN)
            app.put(15, 5, "D  Return to the hall through the service door", WHITE)
        app.mid(19, self.info, self.color, True)
        app.mid(21, "Optional: S skips straight to the operation.", DIM)
