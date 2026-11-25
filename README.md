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
terminal adaptations. Attack hints only use affinities you have learned.
Target choices flag known WEAK, DRAIN, and REPEL results. A group attack can
show both a weakness and an absorption or reflection warning; unknown
affinities still stay unknown until an attack reveals them.

The Bank dials are playable in Story. On the Chamber of Guilt, Cruiser's
Screens and Servers, Depths' A Path Painted Through Prison, and Lab
consultation briefings, press **P** to try a short optional route interaction.
The Cruiser route turns the team into mice that can use a vent but cannot
open doors. On the [Depths light floor](https://mysh.dev/tools/persona/5r/view?file=%5CdataR.cpk%5Cscript%5Cfield%5Cfscr0161_002_120.bf),
each step flips the tile you enter. The nine-tile board is original; the
later move limits and disks are intentionally omitted. A solve earns one
extra battle item for that attempt only. Enter deploys
straight from the briefing. Escape backs out and S skips. **L** opens your
field kit on any briefing, showing the active roster and equipped magic and
support without spoiling Shadow affinities.

Signature scripted mechanics include
Kamoshida's Trophy and charge, Piggytron's charge and one-use bait, Kaneshiro's
bodyguard and dwindling cash, Wakaba's aerial phase and ballista, and the
Spaceport robot shifts and charged attacks. Sae starts with rigged roulette
and later calls elemental attacks. Shido has distinct form tactics and a
Joker-only duel. The Grail fight includes its supply lines and Yaldabaoth’s
individually targetable arms; Maruki's finale includes rotating tendrils and
a guarded opening for Joker. The Spaceport boss keeps the shift clock, gives a limited maintenance
break, and shares a confirmed hit reading across copies of that worker model.
One able teammate can act first as each new worker rank or the executive
unit arrives.
Some traversal puzzles, bans, and cinematic
sequences remain narrated instead of simulated. See the chapter module headers
for research and adaptation notes. The January chapter is exposed after the
December finale in this fight-only app; the original calendar and social
stat prerequisites aren’t simulated.

Each campaign fight shuffles its ordinary turn cycle once. New formations
keep that cycle and normally continue at the next slot. A few ambush breaks
start at the next ready Thief instead, without adding a turn. One More and
Baton Pass remain earned extra actions.

At Kamoshida's Throne Room, breaking the trophy unlocks an optional **C**
command to send a standing teammate for the crown. Land two hits on the
king while they are away. They return to their existing place in the turn
order; the theft staggers Kamoshida and makes the next three hits stronger.
You can still beat him directly. When Royal Smash is winding up, its Guard
warning takes priority.

When Azathoth changes its tendrils and takes Tyrant Stance, Oracle warns you
to Guard before Tyrant Chaos. A quick finish can prevent the attack. The
later coordinated Guard and Joker's finishing command are separate.

## Navigator and cut-ins

After the Pyramid, Oracle can provide Moral Support and one Final Guard per
battle. A two-or-more-target All-Out Attack that ends a wave can trigger her
UFO cut-in once per fight. These are predictable terminal adaptations, not a
claim about Royal's Confidant unlocks or original probabilities. Other
All-Out Attacks get the initiating Thief's cut-in; the implemented Showtime
pairs have their own cards. Enter or Esc skips the card, not the hit: on return
to the arena, the lost HP flashes red and drains before the next formation or
debrief. The art and subtitle text are original.
[Atlus' Futaba trailer](https://www.youtube.com/watch?v=asZwmiMgBBc)
shows the original UFO presentation.

## Verification

Run `python3 -B -m unittest discover -q`. Any testing script should use
Testing Mode or a disposable separate save slot, never a live save.

To simulate complete routes, including independent temporary Story saves:

    python3 -B qa_campaign.py --story --retries 2 --strict
    python3 -B qa_campaign.py --story --retries 2 --knowledge observed

The first run uses informed tactics; the second only uses observed
affinities. Simulation is not the same as human keyboard play. With
`pexpect` available, `python3 -B qa_telegraph.py` repeats the 65×25 keyboard
check for Bank, Pyramid and Casino. It uses an absent, isolated save.
`python3 -B qa_finales_pty.py` exercises compact arena layouts and finale
controls through staged fixtures, not whole manual campaigns. Run
`python3 -B qa_pacing.py --help` for the separate deterministic
opening-turn and damage-gap audit.

For a full keyboard check of early Story rewards, fusion, and save/reload, run
`python3 -B qa_progression_pty.py`. After a reward, S opens the recruited
teammate in Squad; V opens the new mask in the Velvet Room. Previewing either
does not equip it without your input. `python3 -B qa_cruiser_route_pty.py`
checks the Cruiser vent, statue and bulkhead in both modes, including that
solving adds one Medicine and restarting removes the extra item.
`python3 -B qa_cutins_save_pty.py --strict-readability` checks actual
terminal HP colors, the finisher cut-in, and that skipping it does not
duplicate the first-clear reward or change what Continue opens.
`python3 -B qa_timing_pty.py` checks the ordinary turn cycle through the
Museum formation switch and compares Guard versus taking Tyrant Chaos at
the same seed. Its fast-finish check uses a low-HP phase fixture.

Original sources include [the Cruiser's mouse route script](https://mysh.dev/tools/persona/5r/view?file=%5CdataR.cpk%5Cscript%5Cfield%5Cfscr0159_020_100.bf),
[the ship's puzzle on a Royal playthrough](https://www.youtube.com/watch?v=bvoNUeXQrZE&t=2219s),
[the Castle's crown diversion dialogue](https://mysh.dev/tools/persona/5r/view?file=%5Cpatch1R.cpk%5Cpatch1R.cpk%5Cbattle%5Cevent%5Cscript%5C0301.bf)
and [a recorded Castle battle](https://www.lp.zone/t/colors-flying-high-lets-play-persona-5-royal/3971/68)
(the trophy trigger and two-hit cover are terminal tuning),
the two Pyramid slab events
[one](https://mysh.dev/tools/persona/5r/view?file=%5CdataR.cpk%5Cscript%5Cfield%5Cfscr0155_003_120.bf)
and [two](https://mysh.dev/tools/persona/5r/view?file=%5CdataR.cpk%5Cscript%5Cfield%5Cfscr0155_003_130.bf);
the Laboratory exercises
[one](https://mysh.dev/tools/persona/5r/view?file=%5CdataR.cpk%5Cscript%5Cfield%5Cfscr0162_009_100.bf),
[two](https://mysh.dev/tools/persona/5r/view?file=%5CdataR.cpk%5Cscript%5Cfield%5Cfscr0162_009_110.bf),
[three](https://mysh.dev/tools/persona/5r/view?file=%5CdataR.cpk%5Cscript%5Cfield%5Cfscr0162_009_120.bf);
and [recorded Depths play](https://www.youtube.com/watch?v=gyk5nw5C0Q4).
The [Royal battle dialogue](https://mysh.dev/tools/persona/5r/view?file=%5CdataR.cpk%5Cbattle%5Cevent%5Cscript%5C0358.bf)
and [recorded Maruki battle](https://www.lp.zone/t/colors-flying-high-lets-play-persona-5-royal/3971?page=25)
show the Tyrant Stance warning and subsequent release. The timing at the
tendril change is a terminal adaptation.
