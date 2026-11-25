# Persona 5 Terminal

An offline Persona terminal suite with a Persona 3 spring chapter and the Persona 5 campaign. See [Information Baseline](INFORMATION_BASELINE.md) for screen, data, and file naming rules.

Run from the extracted directory with Python and a curses terminal:

    python3 campaign.py

The minimum terminal size is 65×25. The default save is campaign-save.json.
Pass --save with an explicit filename for a separate playthrough or to open
an older save. Launching never renames or imports saves. The Testing Mode opens every populated
chapter and uses only temporary in-memory state. The source archive contains
no player save, passwords, or private workspace files.

The launch picker offers Persona 3, Persona 4, and Persona 5. Use the arrow
keys and Enter, press 3–5, or click a card in mouse-enabled terminals.
The Dark Hour Clock, Tube TV, and Tumbling Card animate when highlighted
or activated.
Persona 3 has a playable spring chapter. It uses `persona3-save.json`;
`--p3-save PATH` gives it another slot. Persona 3 and Persona 5 cannot use
the same save. Esc from a title returns to the picker.
Persona 4 is unavailable. Persona 5 runs the original Calling Card intro and
working campaign. Esc at its title returns to the picker. Use
`python3 campaign.py --persona5` to bypass the picker, including in existing
automation. Enter, Space, or Esc skips an intro without selecting anything.

## Persona 3: April to the first full moon

Start at Iwatodai, awaken Orpheus on the dorm rooftop, and deploy with Yukari
and Junpei on April 20. Later afternoons give you a choice of study, training,
or time in the dorm; evenings let you explore, prepare Personas, or rest.

Thebel uses five representative floors and stops at the sealed 22F border.
The entrance teleporter revisits accessed floors or continues the ascent.
Use **T** on a floor to return to the entrance during the same night, and
**X** to end the expedition. The entrance can also resume your exact place.
Patrols move with your steps; revisiting brings back ordinary Shadows, not
cleared gatekeepers. Travel retains HP, SP and items. Story checkpoints are
permanent; repeat patrols offer smaller Shuffle Time coin rewards and do not
duplicate Persona registrations. Practice from the May 9 briefing or the
epilogue retains no rewards or progress. The Velvet Room uses compact terminal recipes and keeps
both parent entries. Equip a Persona from the compendium before battle.

May 9 opens the monorail whether or not you finish Thebel. The train timer
counts committed combat actions, not real seconds. A failure returns to
pre-board preparation on the same date. This is a Reload-inspired early slice,
not a full recreation of every day, floor, or Persona system.

## Campaign

All nine story maps are represented: Castle, Museum, Bank, Pyramid, Spaceport,
Casino, Cruiser, Depths/Mementos, and Laboratory. Route names and original
briefings are based on the game; enemy numbers, waves, and combat pacing are
terminal adaptations. Only discovered weaknesses are highlighted.

The Bank dials are playable in Story. Signature scripted mechanics include
Kamoshida's Trophy and charge, Piggytron's charge and one-use bait, Kaneshiro's
bodyguard and dwindling cash, Wakaba's aerial phase and ballista, and the
Spaceport robot shifts and charged attacks. Sae’s Casino now has a playable
Members Floor route and House of Darkness. Later features include the
Grail's supply line, Yaldabaoth’s targetable arms and Satanael finish, and
the Laboratory’s role-based tendrils and coordinated Guard into Joker’s
final strike. Remaining route puzzles may be compressed into story. See
the chapter modules for research and adaptation notes. January opens after
December in this fight-only app, without the original social prerequisites.

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
current squad HP, SP, and items across these breaks. Joker faces the Arena
solo against three rounds of opponents with a modest between-round recovery,
then the team uses Crow’s card
loophole to bring down the bridge. In the heist, watch the
first spin, expose the glass, and read the wheel’s announced changes. The boss
sequence is a compact adaptation, not a recreation of Royal’s full wagers.

References: [recorded Casino entry preview](https://www.bilibili.com/video/BV1214y1J7HP/),
[recorded Royal palace run](https://www.youtube.com/watch?v=x5LDcdELNwo)
(chapter timings 55:30 dice, 1:06:15 giant slot, 1:07:29 main terminal,
1:10:33 green, 1:11:17 red, 1:29:20 House of Darkness), and
[Royal’s field script index](https://mysh.dev/tools/persona/5r/files/dataR.cpk/script/field)
(`fscr0157_006` through `fscr0157_013`). The original entry look was checked on video;
the longer control sequence was checked against the game scripts, not from
successful playback of the full recording. Combat lineup sizes, tactics,
and payout steps are compressed for terminal pacing.

## Velvet Room and Shadow Contracts

Use **V** on the map to enter the Velvet Room. A brief blue prison-gate
scene leads into its working Fusion and Compendium menu. Enter, Esc, or
Space skips the scene without activating a menu choice. To see it again,
exit the room and press V. Use Left/Right to switch the menu tabs.
First fusion remains a straightforward registration. Re-fusing an already
registered mask previews retained, added and removed skills before an
explicit confirmation. Only a previous inheritance tracked as such can be
replaced; Skill Card moves and older unclassified extras remain. A revision
leaves the mask equipped if it was already equipped.

Testing Mode offers **X** on the Fusion tab for a separate fresh practice
stock; it doesn't affect the full Testing roster or your Story save. In Story,
when an eligible Shadow is down during Hold Up, a Shadow Contract may offer
a new Persona instead of an All-Out Attack. The Shadow withdraws, but the
recruit only registers when that operation's first clear saves. There is no
repeat contract farming or recruitment in Classic Trials.

Combat displays your current and previewed mask’s defenses, and labels
only discovered enemy reactions. Attempt exits and unsaved victories
ask before discarding the current result.

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
Press **P** to play all, **L** to loop the current scene, **R** to replay,
or **Esc** to back out.
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
not change battle damage or save data. The cut-in takes its cast and direct
knockout result from the actual combat event; a later burn tick does not
award the All-Out finishing signature. In a Story or Testing fight,
**?**, then **C**, puts completed repeat variants on Short playback for
this session. Unseen clips and Gallery playback stay full length.

Art references: [Royal Showtime gameplay](https://www.youtube.com/watch?v=NzZLv8X2sJA),
[Queen & Noir gameplay](https://www.youtube.com/watch?v=Dv9JIJk7t7E),
[Royal All-Out gameplay compilation](https://www.youtube.com/watch?v=8-tIjvQjXS8),
[ATLUS Futaba spotlight](https://p-ch.jp/news/3885/) and
[Royal Oracle gameplay](https://www.youtube.com/watch?v=W3J4rSjfgeE).
All character-cell art was drawn for this app; no game images, video or audio
are bundled.
