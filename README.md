# Phantom Campaign

An offline Persona-inspired terminal campaign. See [Information Baseline](INFORMATION_BASELINE.md) for screen, data, and file naming rules.

Run from the extracted directory with Python and a curses terminal:

    python3 campaign.py

The minimum terminal size is 65×25. The default save is campaign-save.json.
Pass --save with an explicit filename for a separate playthrough or to open
an older save. Launching never renames or imports saves. The Testing Mode opens every populated
chapter and uses only temporary in-memory state. The source archive contains
no player save, passwords, or private workspace files.

## Campaign

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

On the title screen, press **4** to open the gallery (Quit is **5**).
From the **Testing Mode** map, press **G**. Esc from the gallery returns to
the same palace and mission without resetting your practice loadout.
On the map, **T** opens Classic Trials. **Esc** goes back: from Classic
Trials setup or its main battle menu it returns to the map, and an active
Classic fight stays paused. **Esc** from the palace map returns to the title.
Use Left/Right for categories, Up/Down to select, and Enter to preview.
Press **P** to play all clips in order, **R** to replay, or **Esc** to back out.
Gallery previews do not read or alter battle progress.

The eight Showtimes are full original ASCII scenes. **All-Out Attacks** has
nine animated character finishers. **Oracle Support** has three action-only
scenes: the squad recovery relay, Final Guard's shield, and the UFO flyover.
Final Guard is a preview only in this build. Playback is artwork only:
no portrait cards, scene captions, or control overlays. The only lettering
during playback is the signature text on a finishing All-Out Attack
(including the UFO); non-lethal hits and Showtimes stay text-free. Clips redraw against
the current terminal dimensions. Each Showtime is blocked afresh using those
dimensions: the actors, props, motion paths and colored scenery share one
stage. The All-Out and Oracle clips also use native cells. No centered legacy
frame, border, or font scaling is used during playback.

The game uses the same scenes in eligible fights. Enter, Space or Esc skips
the cut-in without replaying or cancelling damage. The animation pack does
not change unlocks, battle rules, damage or save data.

Art references: [Royal Showtime gameplay](https://www.youtube.com/watch?v=NzZLv8X2sJA),
[Queen & Noir gameplay](https://www.youtube.com/watch?v=Dv9JIJk7t7E),
[Royal All-Out gameplay compilation](https://www.youtube.com/watch?v=8-tIjvQjXS8),
[ATLUS Futaba spotlight](https://p-ch.jp/news/3885/) and
[Royal Oracle gameplay](https://www.youtube.com/watch?v=W3J4rSjfgeE).
All character-cell art was drawn for this app; no game images, video or audio
are bundled.
