# Persona 5 Terminal

An offline Persona terminal suite with the Persona 3 base-game story and the Persona 5 campaign. See [Information Baseline](INFORMATION_BASELINE.md) for screen, data, and file naming rules.

Run from the extracted directory with Python and a curses terminal:

    python3 campaign.py

The minimum terminal size is 65×25. The default save is campaign-save.json.
Pass --save with an explicit filename for a separate playthrough or to open
an older save. Launching never renames or imports saves. Battle Practice opens
populated Persona 5 chapters and uses only temporary in-memory state. The source archive contains
no player save, passwords, or private workspace files.

The launch picker offers Persona 3, Persona 4, and Persona 5. Use the arrow
keys and Enter, press 3–5, or click a card in mouse-enabled terminals.
The Dark Hour Clock, Golden Tube TV, and Pinned Calling Card animate when highlighted
or activated.
Persona 3 is playable from April 6 through March 5. It uses `persona3-save.json`;
`--p3-save PATH` gives it another slot. Persona 3 and Persona 5 cannot use
the same save. Esc from a title returns to the picker.
Persona 4 is unavailable. Persona 5 runs the original Calling Card intro and
working campaign. Esc at its title returns to the picker. Use
`python3 campaign.py --persona5` to bypass the picker, including in existing
automation. Enter, Space, or Esc skips an intro without selecting anything.

## Persona 3: April to Graduation

Start at Iwatodai, awaken Orpheus on the dorm rooftop, and deploy with Yukari
and Junpei on April 20. Later afternoons give you a choice of study, training,
or time in the dorm; evenings let you explore, prepare Personas, or rest.
The calendar marks full moons, rescue cases, events and free days. The
evening briefing shows the next event and the next actual full moon.
Story scenes use the same arrow keys and Enter as the calendar. When a scene
offers something to inspect, that choice gives context, not a stat reward or
a hidden requirement for the ending. Continue reopens an unfinished scene
from its first beat without replaying the fight that led to it.

Thebel uses five representative floors and stops at 22F until May 10.
Lower Arqa then opens with 23F and four gatekeepers on 28F, 35F, 36F and
42F before the 43F border. Use Left/Right at the Tartarus entrance to choose
the block. A warp is skippable with Enter, Space, or Esc. The entrance
teleporter revisits accessed floors or continues the ascent.
The elevator shows the selected block, gatekeeper or revisit, and supplies.
Use **T** on a floor to return to the entrance during the same night, and
**X** to end the expedition. The entrance can also resume your exact place.
Patrols move with your steps; revisiting brings back ordinary Shadows, not
cleared gatekeepers. Travel retains HP, SP and items. **H** opens recovery outside of battle:
use Medicine, Soul Drops, Revival Beads, field kits, or spend SP on
healing skills. At the Tartarus entrance, **V** opens the Velvet Room
without ending the expedition. Its entrance animation plays each visit;
Enter, Space, or Esc skips it. Story checkpoints are
permanent. First clears and repeat patrols award XP, with smaller repeat
rewards, and levels unlock moves and increase HP/SP. In Makoto's Skills menu,
preview your active Personas with Left/Right and equip with **P**, or cast a
skill from the preview. Makoto can switch once per normal turn.

The Velvet Room's compact recipes consume each parent from active stock and
leave its entry registered. Choose up to one inherited skill. Fusion is free;
use **C** and **R** in the Compendium to review a paid resummon. A fused
result replaces the equipped mask only when that mask was a parent. Existing
Persona 3 saves load without losing dates, progress, or Personas.

From the calendar or evening menu, choose **Wait for next event** to review
and confirm a skip over quiet days, even if Thebel is unfinished. The
evening menu names its destination. An unfinished first survey remains
available on 2F. No activities or bonus XP are awarded for skipped days.
On May 9, walk through the train cars and regroup with Junpei before
the Priestess fight. The timer counts committed combat actions, not
real seconds. Pull the brake after winning. A loss returns to the same pre-board
briefing. Already finished May 9 in an earlier build? **Continue** starts
May 10 without resetting levels, Personas or Thebel checkpoints.

Akihiko joins expeditions on May 23. On June 8, follow the clues to Fuuka,
then fight Emperor and Empress. Their affinities can change; use Fuuka's
Full Analysis to find the current opening. No Tartarus checkpoint is
required for a full-moon operation. June 13 opens Theurgy, Mitsuru's
deployment and Upper Arqa. Before the first expedition with Theurgy, you
can read the short briefing and deploy, or try the optional drill. The
drill gives no rewards and stays available to replay.
Ordinary stat buffs and debuffs last three turns of the affected unit.
**I** (Field Status) and Analyze show remaining turns.

Upper Arqa spans representative floors from 44F to the 69F border.
Elizabeth posts missing-person cases on June 18 and June 26. Use **R** at
the entrance or in the calendar to see open cases; on the correct floor,
move near the survivor and press **R**. July 6 is the last night to help.
Fast-forward pauses on each new report date. After the final report, waiting
for July 7 warns you that open cases will expire.

At the hotel, Makoto and Yukari are locked for this operation only. Use
**Enter** to toggle the other squadmates and **S** to deploy. Outside the
hotel, Makoto is the only locked slot. The second hotel fight uses the
same team, HP, SP, items and Theurgy charge. **H** opens
recovery between fights. Search rooms across both floors; **I** describes
the selected mirror if the reflection is hard to read. A defeat returns to the briefing; the operation
is saved only after both Shadows are defeated.

Lower Yabbashah opens July 18. Its 80F Monad Door is a fixed optional sample
of Reload's roaming Doors. The 91F Passage and 117F Passage are repeatable
attempts until cleared, with HP, SP, charge, and items carried between their
fights. Open an available Monad challenge with **G**. The entrance's
Recovery Clock (**C**) trades seven Twilight Fragments for full HP and SP.
Aigis joins after Yakushima on July 24, with Orgia Mode and squad buffs.

On August 6 the armored Shadow splits into Chariot and Justice. Defeat
both halves before the survivor can act and revive its partner. Upper
Yabbashah and Koromaru, including Hound of Hades, become available August 8.
Read the 99F, 105F, and 112F threats for Poison, Fear, and Electric attacks.
At Club Escapade on September 5, damage can interrupt Hermit's Mega and
Giga Sparks. Defeat it before Tera Spark or Guard for the discharge.
Continue from September 6 to both halves of Tziah, Fortune and Strength,
the November bridge operation, and Chidori. Ken and Shinjiro arrive on
their own dates; the October operation has the Reload roster restrictions.
The Velvet Room adds new recipes as Tartarus opens. Optional calendar
scenes appear on the dates they are available.

Upper Harabah's two-stage **225F Monad Passage** becomes available after
its gatekeeper. On December 31, Ryoji's decision branches into an alternate
graduation or opens Adamah and the January route. On January 31, the
summit opens at **257F**. At **258F**, fight the patrol for extra supplies
or keep climbing. The summit readies your squad without forcing you
to grind. Checkpoints are **259F Jin**, **263F Takaya**, and **264F Nyx**.
Victory saves that checkpoint. In the same session, keep HP/SP and supplies
or choose **R** to restock before the next fight. Nyx has all **14 Arcana**,
then Makoto faces the **Great Seal** sequence alone. Both routes include their
March endings and post-credits scenes.

Practice from a boss briefing does not save rewards or Velvet Room changes.
This adapts the base game's main story with representative floors, condensed
scenes, and its own combat pacing. Episode Aigis is a separate expansion
and isn't included.

## Campaign

All nine story maps are represented: Castle, Museum, Bank, Pyramid, Spaceport,
Casino, Cruiser, Depths/Mementos, and Laboratory. Route names and original
briefings are based on the game; enemy numbers, waves, and combat pacing are
terminal adaptations. Only discovered weaknesses are highlighted.

In Story mode, examine the two Bank vault receipts to work out the first
PIN, or use the on-screen hint if you get stuck. Signature scripted mechanics include
Kamoshida's Trophy and charge, Piggytron's charge and one-use bait, Kaneshiro's
bodyguard and dwindling cash, Wakaba's aerial phase and ballista, and the
Spaceport robot shifts and charged attacks. Sae’s Casino now has a playable
Members Floor route and House of Darkness. Later features include the
first Grail encounter (survive, rather than deplete its HP), the later supply
line, Yaldabaoth’s targetable arms and Satanael finish, and
the Laboratory’s role-based tendrils and coordinated Guard into Joker’s
final strike. Remaining route puzzles may be compressed into story. See
the chapter modules for research and adaptation notes. January opens after
December in this fight-only app, without the original social prerequisites.

New Game opens with the November casino escape, arrest, and Sae’s questioning.
The April flashback starts with the first trip to Shujin and a short fight in
the escape from the cells. The full Field Drill is available from the Palace
map instead of interrupting that escape. Continue resumes an
unfinished opening at its last completed step. Main-route introductions give
the reason for each target before deployment. Essential first-clear scenes
stay pending if you leave the debrief; Continue opens the scene without
replaying the fight. The casino capture and reversal can also be revisited
from the cleared *Leviathan and the Escape* briefing.
At the Spaceport press console, choose a break that gives the crew enough
time to cross. The console does not start a real-time countdown.
In the Pyramid, examining both mural fragments enables **C Review Clue**
in the relevant briefings; skipping them does not block the Palace.
The Laboratory finale includes Maruki’s offer and a separate coda.


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
Fusion consumes both parents from stock and keeps their Compendium records.
Review the result, inherited skill, credit cost, equipped Personas, and any
new lead’s weaknesses before confirming. Skill Cards preview their effect and
show duplicates and full skill lists as unavailable. If a parent was equipped or led the lineup, the result
takes its place. Re-fusion can replace a previously tracked inherited skill,
but preserves Skill Card moves and older unclassified extras. In the
Compendium, select an archived Persona and press Enter to review its
resummon cost; confirming returns it to stock with its registered skills.
Equip it separately if you want it in battle.

Persona 5 Battle Practice offers **X** on the Fusion tab for a separate fresh practice
stock; it doesn't affect the full Testing roster or your Story save. In Story,
when an eligible Shadow is down during Hold Up, a Shadow Contract may offer
a new Persona instead of an All-Out Attack. The Shadow withdraws, but the
recruit only registers when a victory saves.
Replays can register a missed, eligible Shadow once without granting first-clear
bonuses again. There is no duplicate recruitment or recruitment in Classic Trials.
Ordinary enemy affinities you learn by attacking carry between story battles
after a victory in both campaigns; untested elements and phase-changing
bosses stay separate.

Combat displays your current and previewed mask’s defenses, and labels
only discovered enemy reactions. Both games place HP and SP bars next to
each ally, and briefly mark what a move changed on the affected rows.
The battle log keeps the longer history. Persona 3 shows who is due to act
next; an exposed boss is vulnerable but is not necessarily knocked down.
Item numbers do not move when stock
runs out during a fight. On a defeat, **A** opens Adjust Lead where
available; Escape cancels the change, and Enter applies your choice.
Persona 3 Continue restores pending Shuffle Time choices and required post-boss
scenes before returning to the calendar. The final ascent remembers carried
HP, SP, supplies, and charge. Restock restores resources without clearing
Theurgy. Last-day exits warn before expiring a rescue or dated errand.
Reload's November recording can replay the original July fragment. On
Lower Arqa revisits, look for details by the stair rails. Attempt exits and unsaved victories
ask before discarding the current result.

## Verification

Run `python3 -B -m unittest discover -q`. Any testing script should use
Battle Practice or a disposable separate save slot, never a live save.

## Extras

From the shared series selector, open **Extras** (or press **X**).
Choose **Persona 3** or **Persona 5**, then **Animation Gallery** or
**Battle Practice**. Press **Esc** to move back one level. Neither game’s
normal title screen contains testing shortcuts, and story tutorials are
unchanged. Extras never change story saves.

In Persona 5 Battle Practice, **T** opens Classic Trials. Esc backs out
to the practice map, and Esc from that map returns to Persona 5 Extras.

In Persona 3's gallery and practice lists, **Left/Right** changes group
and **Up/Down** selects an entry. Each group remembers its selection while
you browse.

The Persona 3 **All-Out Attacks** gallery includes each fighter's finisher
and the shared Squad Rush. In battle, a nonlethal All-Out plays the short
rush; a winning hit continues to the initiating fighter's finish card.
All nine finishers and Squad Rush use an illustrated 2×4 dot grid inside
each character cell for extra detail without resizing the terminal. The
same technique is used for the opening, Tartarus elevator, Velvet Room,
Theurgies and Oracle reels. The Dark Hour countdown retains the original
layered-clock artwork and timing. See the [Persona 3 art references](persona3_allout_references.md)
and [cinematic reference notes](persona3_animation_references.md).

### Persona 5 Animation Gallery
Use Left/Right for categories, Up/Down to select, and Enter to preview.
Press **P** to play all, **L** to loop the current scene, **R** to replay,
or **Esc** to back out.
Gallery previews do not read or alter battle progress.

The eight Showtimes are redrawn from scratch as original 2×4 dot scenes. **All-Out Attacks** has
nine animated character finishers. **Oracle Support** has three action-only
scenes: the squad recovery relay, Final Guard's shield, and the UFO flyover.
Once unlocked, Final Guard blocks the first lethal enemy hit on an ally
once per battle. Playback is artwork only:
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

### Visual reference notes

- [Live terminal artwork audit and references](terminal_art_inventory.md)

- [Selector, Persona 3 opening, and smaller visual cues](suite_animation_references.md)
- [Persona 5 Showtimes](persona5_showtime_references.md)
- [Persona 5 All-Out Attacks and Oracle](persona5_finish_references.md)
- [Persona 5 startup, Velvet Room, and Sinful Shell](persona5_story_references.md)

These notes distinguish in-game references from original staging. All
illustrations are drawn with terminal characters; no game images, video,
or audio are bundled.
