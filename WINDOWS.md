# Play Persona Terminal on Windows

Use **Windows Terminal with Ubuntu in WSL** for the recommended setup. If you already have 64-bit Python on Windows and want to try running it without WSL, see [Native Windows](#optional-native-windows). You do not need to install Persona 3 or Persona 5.

## 1. Download the game

1. Sign in to GitHub with the account that can open this private repository.
2. Choose **Code → Download ZIP** on the repository page. In File Explorer, right-click the ZIP and choose **Extract All**. Pick a folder you can write to, such as a Games folder in your user profile. Don't run the game from inside the ZIP.
3. Open the extracted folder that contains **`campaign.py`** (there may be a nested folder). Right-click a blank part of the folder and choose **Open in Terminal**. Use a **PowerShell** tab. Run `Get-Item .\campaign.py` to check you're in the right folder.

Git is not required for the ZIP route. See [GitHub's download instructions](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-files-from-github) if you prefer to clone.

## 2. Set up Ubuntu in WSL once

If you already use Ubuntu in WSL, skip to [Launch](#3-launch). Otherwise, open **PowerShell as administrator** and run:

```powershell
wsl --install -d Ubuntu
```

Restart if prompted. Open **Ubuntu** from Start once and finish its first-run setup, including creating a Linux username and password. If WSL is blocked on a managed PC, ask your IT administrator rather than changing security policy. Microsoft's [WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install) covers supported Windows versions and installation issues.

## 3. Launch

From the **PowerShell tab opened in the extracted game folder**, run:

```powershell
wsl -d Ubuntu
```

You're now in Ubuntu. Run these commands in that same tab:

```bash
ls campaign.py
python3 --version
```

If `ls` can't find the file, type `exit` and reopen PowerShell from the actual folder containing `campaign.py`. Use Python **3.12 or newer** for this setup. If Python is missing, run `sudo apt update && sudo apt install python3` inside Ubuntu. If an older Ubuntu release only offers an older Python, use Ubuntu 24.04 or newer rather than replacing its system Python. Check that the terminal module imports, then start the game:

```bash
python3 -c "import curses; print('Terminal support ready')"
python3 campaign.py
```

You should see the Persona selector. **3** opens Persona 3, **5** opens Persona 5, and **X** opens Extras. Persona 4 is a placeholder. **Extras → Persona 5 → Battle Practice** is a quick way to verify the controls without changing a Story save. Use the arrows, **Enter**, and **Esc** to navigate. At the selector, **Q** quits. Once Python and the terminal are set up, the game itself runs offline.

### Keep WSL saves on its local drive if needed

If saving from the Windows-mounted folder fails, copy the extracted folder into a **new, unused** folder in your Ubuntu home directory and run it there. From the extracted folder inside Ubuntu:

```bash
mkdir -p "$HOME/Games"
cp -R . "$HOME/Games/PersonaTerminal"
cd "$HOME/Games/PersonaTerminal"
python3 campaign.py
```

Only use this example if `$HOME/Games/PersonaTerminal` does not already exist; otherwise choose a new folder. This copies any saves already present, so don't alternate between the two copies and expect progress to stay synchronized. Microsoft's [WSL filesystem guidance](https://learn.microsoft.com/en-us/windows/wsl/interop) explains the difference between Windows-mounted folders and Ubuntu's local drive.

## Optional: Native Windows

The game uses Python's `curses` module, which [standard Windows Python does not include](https://docs.python.org/3/howto/curses.html). The [windows-curses package](https://pypi.org/project/windows-curses/) provides an alternative. Use WSL if the native package, controls, or artwork do not work on your machine.

1. Install **64-bit CPython 3.13** from [Python's official Windows downloads](https://www.python.org/downloads/windows/). On a typical Intel or AMD PC, choose **Windows installer (64-bit)**, not the 32-bit or embeddable package. Use WSL on ARM if a suitable native wheel is unavailable. See [Python's Windows setup instructions](https://docs.python.org/3.13/using/windows.html) for the Python launcher.
2. From **PowerShell** in the game folder, create an isolated environment and install the wheel:

   ```powershell
   py -3.13 --version
   py -3.13 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install --only-binary=:all: windows-curses
   .\.venv\Scripts\python.exe -c "import curses; print('Terminal support ready')"
   ```

   If `py` isn't found, reopen PowerShell after installing Python. If `python --version` shows Python 3.13, you can substitute `python -m venv .venv` for the `py -3.13` creation command. CPython 3.12 also has Windows x64 wheels; if that's what you installed, replace `-3.13` with `-3.12`. There is no need to activate the environment or change PowerShell execution policy.
3. Run these two lines in the same PowerShell tab each time:

   ```powershell
   $env:ESCDELAY = "55"
   .\.venv\Scripts\python.exe .\campaign.py
   ```

   The first line tells this project's launcher not to call the Unix-style `set_escdelay` function on the Windows compatibility layer. If the import works but running the game produces a different curses error or input/display problems, use the WSL route rather than adjusting Windows security settings or reinstalling Python repeatedly.

## Saves and common fixes

- **Terminal says it's too small:** Maximize Windows Terminal, close other split panes, or reduce the font size in the active profile. The game needs **65 columns × 25 rows**; around **96 × 35** leaves more space. [Terminal appearance settings](https://learn.microsoft.com/en-us/windows/terminal/customize-settings/profile-appearance).
- **Art is missing or shows boxes:** Try a Unicode-capable monospaced font in the active profile (for example, Cascadia Mono). Relaunch inside Windows Terminal, not in an editor's output pane. If native Windows still misdraws the dot art, use WSL.
- **Keep your progress when downloading an update:** By default, Persona 3 uses `persona3-save.json` and Persona 5 uses `campaign-save.json`, both next to `campaign.py`. Close the game and copy those two files to a safe folder before replacing the source folder. Copy them into a fresh extract, or keep them elsewhere and pass their paths when launching. Use separate files for each game and avoid opening the same save in two running copies.
- **Try a separate save slot:** In Ubuntu, run `python3 campaign.py --p3-save "p3-test.json" --save "p5-test.json"` in the game folder. On native Windows, run the same arguments after `.\.venv\Scripts\python.exe .\campaign.py`. These filenames do not replace the defaults.

For campaign details and keyboard shortcuts, return to the [main README](README.md).
