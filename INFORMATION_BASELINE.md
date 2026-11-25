# Phantom Campaign information baseline

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
  available. Use Esc for back/cancel; T opens/resumes Classic Trials on the map.
- **Teaching:** teach combat rules where the player first uses them in the field
  drill. Put reference information in Tactics, not on every screen. Keep
  tutorials and detailed inspectors optional.
- **Animations:** no subtitles, descriptions, control overlay, or portrait
  cards. A successful All-Out finisher may show the signature in-game
  lettering as artwork. Only useful distinctions like “Preview only” belong
  in gallery rows.
- **Verify:** at 65×25 and a wide terminal, check labels, prompts and footers
  for clipping and repetition. Follow Enter and Esc through the real screens.
  A view must never write a save or alter gameplay.

## What owns the data

- **Content:** campaign_data.py assembles chapters; chapter modules own
  mission text and rewards. battle_data.py owns base skills, units, Personas
  and trials. Store a mission brief once; add a distinct story introduction
  only when it adds information. Don't store control descriptions in
  battle or save records.
- **Rules and state:** battle_engine.py resolves turns. campaign_combat.py
  derives who actually deploys; the briefing uses that same function.
  campaign_state.py owns the versioned save schema and atomic writes.
  Store only durable progress and loadout choices in saves. Testing state,
  combat state, gallery selection and presentation cues are transient.
  Keep fields required by the decoder until a planned migration.
- **Presentation:** campaign.py, battle_ui.py and animation_gallery.py
  format the values they receive. Don't infer rules from labels or repeat
  source facts in display caches. Use the same source for a value shown in
  more than one context. Show discovered affinities, not hidden resistances.
- **Cinematics:** cinema.py owns the playback registry, with timing from the
  native renderer. Battle and gallery share the renderer. The gallery owns
  preview-only entries; the engine emits actual combat events. Signature
  lettering lives in finishing_type.py, not in the controls.

## Names and versions

- Product: **Phantom Campaign**. Project folder: **Phantom-Campaign**.
  Release download: **Phantom Campaign.zip**. Entry point: **campaign.py**.
  Default save: **campaign-save.json**.
- Name source files after their role and use lower snake case. Name tests
  after what they verify. Keep weekdays, development phases and words like
  “latest” or “final” out of live names; use version history instead.
- Keep stable identifiers for missions and saved keys separate from display
  wording. Never silently redirect, overwrite or migrate existing saves
  for a naming cleanup. Explicit save paths and earlier backups remain usable.
