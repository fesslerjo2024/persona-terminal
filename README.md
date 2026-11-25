# Phantom Campaign — weekend reconstruction

This is a separate recreation and expansion built after the verified Bank build
was missing from the restored cloud workspace. **It is not the exact Bank
rollback.** It does not change the surviving original Phantom Link source and
does not use the old campaign save by default. No remote or network access is
needed to play.

Run from the extracted directory with Python and a curses terminal:

    python3 campaign.py

The minimum terminal is 65×25. Start a separate playthrough using
`python3 campaign.py --save my-weekend-save.json`. Avoid using this option
with a story save from another build. The Testing Mode opens every populated
chapter and uses only temporary in-memory state. The source archive contains
no player save, passwords, or private workspace files.

## What is implemented in this checkpoint

All nine story maps are represented: Castle, Museum, Bank, Pyramid, Spaceport,
Casino, Cruiser, Depths/Mementos, and Laboratory. Route names and original
briefings are based on the game; enemy numbers, waves, and combat pacing are
terminal adaptations. Only discovered weaknesses are highlighted.

The Bank dials are playable in Story. Signature scripted mechanics include
Kamoshida's Trophy and charge, Piggytron's charge and one-use bait, Kaneshiro's
bodyguard and dwindling cash, Wakaba's aerial phase and ballista, and the
Spaceport robot shifts and charged attacks. Later route puzzles and scripted
boss twists may be narrated or represented by conventional waves in this
checkpoint, rather than implemented exactly. See the chapter module headers
for research and adaptation notes. The January chapter is exposed after the
December finale in this fight-only app; the original calendar and social
stat prerequisites aren’t simulated.

## Verification

Run `python3 -B -m unittest discover -q`. Any testing script should use
Testing Mode or a disposable separate save slot, never a live save.

## Animation Gallery

On the title screen, press **4** to open the gallery (Quit is now **5**).
Use Left/Right for categories, Up/Down to select, and Enter to preview.
Press **P** to play all clips in order, **R** to replay, or **Esc** to back out.
Gallery previews do not read or alter battle progress.

**Showtimes → 6 Palace Body Slam** is a full ASCII scene: ring entrance,
Queen’s lariat, Noir’s dropkick, the double dive and the referee’s count.
The same scene plays for Queen and Noir’s Showtime in combat. Enter, Space,
or Esc skips the cut-in without skipping damage.
