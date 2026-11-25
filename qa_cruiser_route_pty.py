"""Keyboard QA for the optional Cruiser statue route in the 65x25 app.

Run: python -B qa_cruiser_route_pty.py (requires pexpect).
Only seeded disposable Story and absent Testing saves are used.
"""
from pathlib import Path
from tempfile import TemporaryDirectory

from campaign_combat import build_stage
from campaign_data import CHAPTERS, NODES
from campaign_state import Campaign, TestingCampaign
from qa_telegraph import ENTER, ESC, RIGHT, Terminal

NODE = "cruiser-industry"
SEED = 2
CHAPTER, OPERATION = next((i, j) for i, chapter in enumerate(CHAPTERS)
                          for j, node in enumerate(chapter["nodes"])
                          if node["id"] == NODE)


def expect(screen, *text):
    for fragment in text:
        assert fragment in screen, (fragment, screen)


def brief(term):
    screen = term.need(str(OPERATION + 1), "OPERATION BRIEF")
    expect(screen, "SCREENS AND SERVERS", "P ROUTE", "ENTER DEPLOY", "L KIT")


def open_route(term):
    screen = term.need("p", "CRUISER / SERVICE DECK")
    expect(screen, "FORM: MOUSE    /    STATUE: ON", "LOCATION: STATUE HALL",
           "V VENT  T SWITCH  D DOOR  E EXIT  X RESET  S SKIP  ESC BACK")


def inspect_inventory(term, count):
    term.need("5", f"Medicine ×{count}")
    term.need(ESC, "NOW ")


def retreat(term):
    term.need(ESC, "RETURN TO THE PALACE MAP?")
    term.need(ENTER, "CRUISER MAP")
    brief(term)


def win_puzzle(term):
    term.need("e", "Too small to open the main bulkhead.")
    term.need("d", "Too small to open the service door.")
    service = term.need("v", "Outside the statue's range. Human again.")
    expect(service, "LOCATION: SERVICE ROOM", "FORM: HUMAN    /    STATUE: ON")
    term.need("e", "The main bulkhead is back in the statue hall.")
    hall = term.need("d", "The active statue shrinks you again.")
    expect(hall, "LOCATION: STATUE HALL", "FORM: MOUSE    /    STATUE: ON")
    term.need("v", "LOCATION: SERVICE ROOM")
    term.need("t", "FORM: HUMAN    /    STATUE: OFF")
    term.need("x", "FORM: MOUSE    /    STATUE: ON")
    term.need("v", "LOCATION: SERVICE ROOM")
    term.need("t", "STATUE: OFF")
    hall = term.need("d", "Still human. The main bulkhead is within reach.")
    expect(hall, "LOCATION: STATUE HALL", "FORM: HUMAN    /    STATUE: OFF")
    term.need("v", "The vent is too small in human form.")
    term.need("e", "NOW ")


def check(save, story):
    if story:
        store = Campaign(save)
        store.new_game()
        for operation in NODES:
            if operation["id"] == NODE:
                break
            store.clear(operation["id"], "B")
        original = save.read_bytes()
    else:
        store = TestingCampaign()
    standard = build_stage(store, NODE, SEED).items["Medicine"]
    term = Terminal(save, SEED)
    try:
        if story:
            term.need("1", "CRUISER MAP")
        else:
            term.need("3", "TESTING MODE")
            term.need(RIGHT * CHAPTER, "CRUISER MAP")
        brief(term)
        open_route(term)
        term.need("v", "LOCATION: SERVICE ROOM")
        screen = term.need(ESC, "OPERATION BRIEF")
        expect(screen, "P ROUTE")
        assert "NOW " not in screen
        term.need(ENTER, "NOW ")
        inspect_inventory(term, standard)
        retreat(term)
        open_route(term)
        term.need("s", "NOW ")
        inspect_inventory(term, standard)
        retreat(term)
        open_route(term)
        win_puzzle(term)
        term.need("l", "service route yields one extra Medicine")
        term.need("l", "NOW ")
        inspect_inventory(term, standard + 1)
        term.need("r", "RESTART THIS FIGHT?")
        term.need(ENTER, "NOW ")
        inspect_inventory(term, standard)
    finally:
        term.close()
    if story:
        assert save.read_bytes() == original
    else:
        assert not save.exists()
    mode = 'Story' if story else 'Testing'
    save_result = 'save bytes unchanged' if story else 'no save created'
    print(f"{mode}: compact footer, blocked mouse doors, vent, re-shrink, statue toggle, reset, "
          f"human-only exit, Escape and S passed. Medicine direct/skip/solve/restart: "
          f"{standard}/{standard}/{standard + 1}/{standard}; {save_result}.", flush=True)


if __name__ == "__main__":
    with TemporaryDirectory(prefix="phantom-cruiser-route-") as tmp:
        check(Path(tmp) / "story.json", True)
        check(Path(tmp) / "absent.json", False)
