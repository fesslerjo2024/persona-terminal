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
Spaceport robot shifts and charged attacks. Sae starts with rigged roulette
and later calls elemental attacks. Shido has distinct form tactics and a
Joker-only duel. The Grail fight includes its supply lines and Yaldabaoth’s
individually targetable arms; Maruki's finale includes rotating tendrils and
a guarded opening for Joker. Some traversal puzzles, bans, and cinematic
sequences remain narrated instead of simulated. See the chapter module headers
for research and adaptation notes. The January chapter is exposed after the
December finale in this fight-only app; the original calendar and social
stat prerequisites aren’t simulated.

## Navigator and cut-ins

After the Pyramid, Oracle can provide Moral Support and one Final Guard per
battle. A two-or-more-target All-Out Attack that ends a wave can trigger her
UFO cut-in once per fight. These are predictable terminal adaptations, not a
claim about Royal's Confidant unlocks or original probabilities. Other
All-Out Attacks get the initiating Thief's cut-in; the implemented Showtime
pairs have their own cards. The art and subtitle text are original.
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
