# Persona 5 Terminal maintenance

Read docs/INFORMATION_BASELINE.md before changing screen text, game data, or
file names. Keep the default save and mission identifiers stable. Show one
footer for controls and no unnecessary captions or repeated descriptions.
Keep mechanics, state, display formatting and preview art in their own
modules. Use only disposable saves for verification.

Run python3 -B -W error -m unittest discover -q before shipping changes.
