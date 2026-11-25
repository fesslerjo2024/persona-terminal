# Persona 5 Terminal

An offline Persona-inspired terminal campaign. See [Information Baseline](INFORMATION_BASELINE.md) for screen, data, and file naming rules.

Run from the extracted directory with Python and a curses terminal:

    python3 campaign.py

The minimum terminal size is 65×25. The default save is campaign-save.json.
Pass --save with an explicit filename for a separate playthrough or to open
an older save. Launching never renames or imports saves. The Testing Mode opens every populated
chapter and uses only temporary in-memory state. The source archive contains
no player save, passwords, or private workspace files.

The Calling Card plays on launch and opens the live title menu. Press Enter,
Space or Esc to skip straight to the menu without selecting an item.

## Campaign

All nine story maps are represented: Castle, Museum, Bank, Pyramid, Spaceport,
Casino, Cruiser, Depths/Mementos, and Laboratory. Route names and original
briefings are based on the game; enemy numbers, waves, and combat pacing are
terminal adaptations. Only discovered weaknesses are highlighted.

The Bank dials are playable in Story. Signature scripted mechanics include
Kamoshida's Trophy and charge, Piggytron's charge and one-use bait, Kaneshiro's
bodyguard and dwindling cash, Wakaba's aerial phase and ballista, and the
Spaceport robot shifts and charged attacks. Sae’s Casino now has a playable
Members Floor route and a first House of Darkness pass. Later route puzzles and scripted
boss twists may be narrated or represented by conventional waves in this
checkpoint, rather than implemented exactly. See the chapter module headers
for research and adaptation notes. The January chapter is exposed after the
December finale in this fight-only app; the original calendar and social
stat prerequisites aren’t simulated.

### Palace menus
Controls stay the same on all nine maps: Left/Right changes Palace and
Up/Down or a number selects an operation. The map is a different object in
each Palace: castle cross-section, framed exhibit wall, vault dial, tomb
mural, factory dispatch, Casino elevator, boarding pass and deck plan,
subway-to-prison record, or treatment terminal. Themed briefings keep the
same deployment information. Presentation cues are brief and do not block
input, unlock routes, or write saves. Both rows of map shortcuts sit above
the terminal’s bottom edge. The Casino keeps its operation list in numerical
order alongside the lift, whose moving cabin docks on its actual floor label.

### Sae’s Casino
The staff-only route uses two fights for the security keycard and members
card. The Members Floor interludes let you turn the dice room against the
house, follow Oracle’s red and green control leads, and exchange the giant
slot jackpot for a High Limit card. These casino coins are local to the
attempt, never spendable Velvet Room credits. The House of Darkness has a
short locked-door/vent detour and its own exit attendant. Combat carries
current squad HP, SP, and items across these breaks. The Battle Arena, bridge,
and heist still use the earlier compact adaptation.

References: [recorded Casino entry preview](https://www.bilibili.com/video/BV1214y1J7HP/),
[recorded Royal palace run](https://www.youtube.com/watch?v=x5LDcdELNwo)
(chapter timings 55:30 dice, 1:06:15 giant slot, 1:07:29 main terminal,
1:10:33 green, 1:11:17 red, 1:29:20 House of Darkness), and
[Royal’s field script index](https://mysh.dev/tools/persona/5r/files/dataR.cpk/script/field)
(`fscr0157_006` through `fscr0157_013`). The original entry look was checked on video;
the longer control sequence was checked against the game scripts, not from
successful playback of the full recording. Combat lineup sizes, tactics,
and payout steps are compressed for terminal pacing.

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
