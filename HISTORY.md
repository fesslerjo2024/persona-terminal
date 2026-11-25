# Project history

This repository combines the retained source snapshots with the current game.
The older commits were reconstructed from backups in the order supported by the
archives. They are not the original development commits. Their messages identify
the recovered artifact and record the SHA-256 of its imported source manifest.
Changes between retained snapshots and builds that were not retained are not
represented.

| Branch | What it contains |
| --- | --- |
| `main` | The recovered Friday baseline, the later cinematics and campaign checkpoints, the shared menu and initial Persona 3 slice, then the current Persona Terminal suite. |
| `archive/weekend` | The separate weekend reconstruction, starting from the same recovered Friday baseline and ending at its final retained working build. This is an archive, not the recommended branch to play. |

The archived weekend source described itself as a recreation, not the exact
missing Bank-era rollback. The retained snapshots are preserved for comparison;
they are not evidence that the missing source was recovered.

Game saves and local backups are not tracked. If you run an old checkpoint, use
a separate clone or worktree and a new save filename. Use the [Windows setup
guide](WINDOWS.md) for the current `main` branch; older checkpoints may use
different controls or launch options.
