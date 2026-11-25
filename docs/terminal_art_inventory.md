# Terminal artwork audit

This pass redraws shipped pictorial art as native 2×4 microdot geometry. It
does not rewrite UI markers, map symbols, meter bars, section dividers, text
menus, progress, or input. A route marker or paint boundary is not a picture.
Animations and selector cards already drawn on the microgrid remain in use.
The previously approved Makoto finisher and the restored Dark Hour clock
montage keep their original frames.

| Live surface | Owner and visual references |
| --- | --- |
| Persona 3 exploration, discoveries and story stills | [Persona 3 story art notes](persona3_story_art_references.md) |
| Persona 3 menu illustrations and reward cards | [Persona 3 menu art notes](persona3_menu_art_references.md). The title strip also uses native dot bevels rather than drawn ASCII strokes. |
| Persona 5 all nine Palace maps | [Palace map art notes](persona5_palace_art_references.md) |
| Persona 5 Palace interludes | [Persona 5 story art notes](persona5_story_art_references.md) |
| Persona 5 fallback battle cut-in | The red/black diagonal burst is an original nod to the [in-game battle framing](https://playcraft.space/gallery/persona-5-royal/battle-command-attack-star/) in ATLUS capture. It replaces the asterisks, has no caption, and does not represent a specific technique or a replacement for an authored scene. |

Old compact cinema renderers are retained for the historical test adapter
(`cinema.get`), not used by live playback or the galleries. The selector
draft comparison is a separate local tool, not an additional game menu.
