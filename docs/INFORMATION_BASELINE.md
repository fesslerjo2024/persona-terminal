# Persona 5 Terminal information baseline

## Before adding anything to a screen

Keep information only if a first-time player needs it **here** to choose
an action, understand a rule or result, avoid losing something, or find
a next step. A suggested label is not a requirement to display it. If the
screen still makes sense without the line, leave it out.

- **Heading:** identify the screen or decision once. Don't restate the
  selection elsewhere unless the next screen would otherwise be ambiguous.
- **Body:** show choices, state that affects them, and the reason something
  is unavailable. Keep meaningful story beats in their story panels. Save
  outcomes, lock prerequisites, costs, boss threats and irreversible
  consequences belong next to the decision.
- **Footer:** one place for key bindings, with short action names. Don't
  repeat them in a tooltip or at the top. List unfamiliar actions only when
  available. Use Esc for back/cancel. T offers Classic Trials only in
  Persona 5 Battle Practice, reached via the shared selector’s Extras.
- **Teaching:** teach combat rules where the player first uses them in the field
  drill. Put reference information in Tactics, not on every screen. Keep
  tutorials and detailed inspectors optional.
- **Story:** put a character's immediate goal and the reason for the next
  operation on the main route. Let optional observations deepen that context,
  not supply a missing cause. A linear action is a highlighted button with a
  specific verb and Enter support; a numbered optional observation must not
  override an explicit Enter action.
- **Animations:** no subtitles, descriptions, control overlay, or portrait
  cards. A successful All-Out finisher may show the signature in-game
  lettering as artwork. Only useful distinctions like “Preview only” belong
  in gallery rows.
  Draw cinematic geometry on the shared 2×4 dot canvas and pack it into
  fixed-width glyphs. Do not resize the terminal or reuse a scaled legacy
  cel. Use ordinary text cells for readable interface copy. The restored
  Dark Hour clock montage intentionally keeps its original terminal-cell art.
- **Verify:** at 65×25 and a wide terminal, check labels, prompts and footers
  for clipping and repetition. Follow Enter and Esc through the real screens.
  A view must never write a save or alter gameplay.

## Where code lives

- `campaign.py` stays at the root as the public launcher. Its command-line startup
  lives in `persona_terminal/shared/launcher.py`. The two default save files still
  live beside the launcher.
- `persona_terminal/persona3/` and `persona_terminal/persona5/` own their campaign
  data, rules, game-specific artwork and screens. `persona_terminal/shared/` owns
  the series selector, terminal navigation/palette primitives and canvas helpers.
- Regression tests live in `tests/`; design notes and reference sources live here.

## What owns the data

- **Content:** campaign_data.py assembles chapters; chapter modules own
  mission text and rewards. battle_data.py owns base skills, units, Personas
  and trials. Store a mission brief once; add a distinct story introduction
  only when it adds information. Don't store control descriptions in
  battle or save records.
- **Rules and state:** battle_engine.py resolves turns. campaign_combat.py
  derives who actually deploys; the briefing uses that same function.
  campaign_state.py owns the versioned save schema and atomic writes.
  Keep Persona Compendium records, stock, and battle loadout distinct.
  A fusion preview derives its stock and loadout changes from the same rule
  as the commit. Outside of rewards, only a confirmed fusion or resummon changes stock.
  Store only durable progress, discovered clue IDs, and loadout choices in saves. Palace interludes
  such as casino_route.py own temporary choices and coins. Campaign story defines
  scene and clue text. Save discovery IDs and the unfinished opening or
  essential debrief checkpoint, not rendered story text or optional choice history.
  An earned, unclaimed Persona 3 reward or boss aftermath is a durable decision;
  Continue restores it before advancing the calendar. Observed ordinary Shadow
  affinities are stored by species after a victory, never inferred for unknown elements. Testing state,
  combat state, gallery selection and presentation cues are transient.
  Keep fields required by the decoder until a planned migration.
- **Presentation:** the Persona 5 controller (`persona_terminal/persona5/campaign.py`), battle_ui.py and animation_gallery.py
  format the values they receive. Don't infer rules from labels or repeat
  source facts in display caches. Use the same source for a value shown in
  more than one context. Show discovered affinities, not hidden resistances.
- **Palace menus:** palace_menu.py owns common navigation, detail text and
  briefing chrome. Palace theme modules render a frozen view of the
  ordered operations. Locked Story stages show only their position and `???`;
  their names, briefings and revealing labels stay hidden. Battle Practice keeps
  every stage visible. Renderers do not calculate unlocks, accept input, or touch
  saves. Art uses rows 6 through height minus 8. Preserve the shared
  heading and selected-operation detail strip. Both map control rows belong
  at height minus 3 and height minus 2; leave the final terminal row blank.
- **Startup:** title_scene.py owns the calling card landing and title layout.
  CampaignApp owns working title choices and dispatch; startup cannot dispatch
  the key that skipped it.
- **Cinematics:** cinema.py owns the playback registry, with timing from the
  native renderer. Battle and gallery share the renderer. The gallery owns
  preview-only entries; the engine emits actual combat events. Signature
  lettering lives in finishing_type.py, not in the controls.

## Names and versions

- Product: **Persona 5 Terminal**. Existing checkout: **Phantom-Campaign** (retained for launch compatibility).
  Release download: **Persona 5 Terminal.zip**. Entry point: **campaign.py**.
  Default save: **campaign-save.json**.
- Name source files after their role and use lower snake case. Name tests
  after what they verify. Keep weekdays, development phases and words like
  “latest” or “final” out of live names; use version history instead.
- Keep stable identifiers for missions and saved keys separate from display
  wording. Never silently redirect, overwrite or migrate existing saves
  for a naming cleanup. Explicit save paths and earlier backups remain usable.
