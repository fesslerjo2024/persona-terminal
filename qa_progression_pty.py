"""Real 65x25 Castle Story progression check, with optional pexpect.

Run: python3 -B qa_progression_pty.py
The app always receives a disposable --save; no default save is used.
"""
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from campaign_state import Campaign
from qa_telegraph import ENTER, ESC, RIGHT, ROOT, Terminal

LEFT = "\x1bOD"
SEED = 4


@contextmanager
def play(save):
    tty = Terminal(save, SEED)
    try:
        yield tty
    finally:
        tty.close()


def has(screen, *features):
    for feature in features:
        assert feature in screen, (feature, screen)


def gate_win(tty):
    tty.need("1", "PERSONA: Arsène")
    has(tty.need(RIGHT, "PERSONA: Pixie"), "Zio")
    tty.need("1", "TARGET  /  Zio")
    tty.need("1", "HOLD UP!")
    return tty.need("7", "PALACE / DEBRIEF", 2.6)


def first_clear(base, stock):
    with play(base) as tty:
        tty.need("2", "PROLOGUE")
        tty.need(ESC, "TRAINING LINK")
        tty.need(ESC, "CASTLE MAP")
        starting = Campaign(base).data
        tty.need("1", "OPERATION BRIEF")
        tty.need(ENTER, "NOW Joker")
        win = gate_win(tty)
        has(win, "FIRST-CLEAR REWARDS", "Credits: +350", "Mask slots: +1",
            "Recruited: Panther", "NEXT ROUTE  /  GUARDHOUSE", "V VELVET")
        after = Campaign(base)
        assert after.data["credits"] == starting["credits"] + 350
        assert after.data["slots"] == starting["slots"] + 1
        assert after.data["cleared"] == {"castle-gate": "S"}
        raw = base.read_bytes()
        stock.write_bytes(raw)
        print("Castle Gate keyboard win: +350 credits, +1 Persona slot, Panther, Guardhouse next.", flush=True)

        # Check the debrief shortcut and preview without hitting any save command.
        squad = tty.need("s", "TEAM CONFIG")
        assert re.search(r"▶\s+\d+ ○ Panther", squad), squad
        has(squad, "Panther  /  125 HP  58 SP")
        tty.need(ESC, "PALACE / DEBRIEF")
        assert base.read_bytes() == raw
        tty.need("v", "[ COMPENDIUM ]")
        tty.need(LEFT, "[ FUSION ]")
        preview = tty.need(ENTER, "FUSION PREVIEW")
        has(preview, "High Pixie", "PRICE 135", "425 ON HAND", "290 AFTER", "Zionga", "Media")
        tty.need(ESC, "[ FUSION ]")
        tty.need(ESC, "PALACE / DEBRIEF")
        assert base.read_bytes() == raw
        print("Squad preview and fusion preview/back did not alter autosave bytes.", flush=True)

        tty.need("v", "[ COMPENDIUM ]")
        tty.need(LEFT, "[ FUSION ]")
        tty.need(ENTER, "FUSION PREVIEW")
        fresh = tty.need("f", "HIGH PIXIE IS REGISTERED")
        has(fresh,"equipped Personas have not changed", "An open slot is ready.")
        registered = Campaign(base).data
        assert registered["credits"] == 290 and "High Pixie" in registered["personas"]
        assert "High Pixie" not in registered["loadout"]
        compendium = tty.need("e", "EQUIPPED High Pixie")
        has(compendium, "High Pixie", "4/4 active", "Zionga", "Media")
        advanced = Campaign(base).data
        assert advanced["loadout"] == [*starting["loadout"], "High Pixie"]
        assert advanced["primary"] == "Arsène"
        tty.need(ESC,"PALACE / DEBRIEF")
        print("High Pixie previewed, fused, then explicitly equipped in the earned fourth slot.", flush=True)


def next_encounter(save, upgrade):
    before = save.read_bytes()
    with play(save) as tty:
        cmap = tty.need("1", "CASTLE MAP")
        has(cmap, "▶  02", "Guardhouse")
        tty.need(ENTER, "OPERATION BRIEF")
        if upgrade:
            kit = tty.need("l", "FIELD KIT")
            # Kit aggregates elements; exact skills should come from Persona page.
            has(kit, "Joker", "Electric")
            tty.need(ESC, "OPERATION BRIEF")
        arena = tty.need(ENTER, "NOW Joker")
        assert "? ? ? ?" in arena and "[WEAK]" not in arena, arena
        tty.need("1", "PERSONA: Arsène")
        if upgrade:
            high = tty.need(LEFT, "PERSONA: High Pixie")
            has(high, "Zionga", "Garula", "Diarama")
            assert "[WEAK]" not in high
            assert "Eiha" not in high
            stock = tty.need(RIGHT, "PERSONA: Arsène")
            has(stock, "Eiha")
            assert "Zionga" not in stock
            tty.need(LEFT, "PERSONA: High Pixie")
            skill, damage, hp = "Zionga", 74, 29
        else:
            lantern = tty.need(LEFT, "Jack-o'-Lantern")
            has(lantern, "Agi")
            assert "Zionga" not in lantern
            tty.need(RIGHT, "PERSONA: Arsène")
            pixie = tty.need(RIGHT, "PERSONA: Pixie")
            has(pixie, "Zio")
            assert "Zionga" not in pixie
            skill, damage, hp = "Zio", 48, 55
        tty.need("1", "TARGET  /  "+skill)
        post = tty.need("2", "NOW Joker +1")
        has(post, f"Bicorn {hp}H")
        log = tty.need("l", f"Bicorn takes {damage} damage [WEAK].")
        has(log, "Joker → "+skill+".")
        if upgrade:
            has(log, "Joker switches to High Pixie.")
    assert before == save.read_bytes()
    print(f"{'Equipped' if upgrade else 'Stock'} Guardhouse restart: {skill} hit Bicorn for {damage}, "
          f"{hp} HP left; unknown before strike, weak only after; unfinished save unchanged.", flush=True)


def replay(save):
    before = save.read_bytes()
    with play(save) as tty:
        tty.need("1", "CASTLE MAP")
        tty.need("1", "CASTLE GATE")
        tty.need(ENTER, "NOW Joker")
        result = gate_win(tty)
        has(result, "Replay complete. First-clear rewards cannot repeat.", "BEST MEDAL KEPT")
        assert "FIRST-CLEAR REWARDS" not in result
    assert before == save.read_bytes()
    print("Castle Gate replay: no duplicate credits, slots, or recruitment; all save bytes unchanged.", flush=True)


def follow_registered_reward(save):
    """Clear Guardhouse for a direct mask reward and verify focused preview."""
    with play(save) as tty:
        tty.need("1", "CASTLE MAP")
        tty.need(ENTER, "OPERATION BRIEF")
        tty.need(ENTER, "NOW Joker")
        tty.need("1", "PERSONA: Arsène")
        tty.need(LEFT, "PERSONA: High Pixie")
        tty.need("1", "TARGET  /  Zionga")
        tty.need("2", "NOW Joker +1")
        tty.need("6", "Pass to Skull")
        tty.need("2", "NOW Skull")
        tty.need("1", "Mazionga")
        win = tty.need("2", "PALACE / DEBRIEF", 1.7)
        has(win, "FIRST-CLEAR REWARDS", "Registered: Bicorn", "Skill cards: Dia", "V VELVET")
        after = save.read_bytes()
        assert "Bicorn" not in Campaign(save).data["loadout"]
        preview = tty.need("v", "[ COMPENDIUM ]")
        assert re.search(r"▶\s+\d+ ○ Bicorn", preview), preview
        has(preview, "Cleave, Garu, Tarunda", "4/4 active", "Defense:")
        tty.need(ESC, "PALACE / DEBRIEF")
        assert after == save.read_bytes()
        assert "Bicorn" not in Campaign(save).data["loadout"]
    print("Guardhouse win registered Bicorn; V focused Bicorn's real skills, without equipping or changing save bytes.", flush=True)


def main():
    with TemporaryDirectory(prefix="phantom-progression-") as temp:
        base, stock = (Path(temp)/n for n in ("progression.json", "stock.json"))
        first_clear(base, stock)
        next_encounter(stock, False)
        next_encounter(base, True)
        replay(base)
        follow_registered_reward(base)
    for path in ("campaign.py","battle_ui.py","battle_engine.py","campaign_state.py","campaign_data.py","early_data.py"):
        print(f"{sha256((ROOT/path).read_bytes()).hexdigest()}  {path}")


if __name__ == "__main__":
    main()
