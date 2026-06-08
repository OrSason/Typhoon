# Typhoon ⌨️🌀

A tiny **Windows background app** that fixes text you typed in the **wrong keyboard
layout**. You meant to write English but Windows was set to Hebrew, so `hello`
came out as `יקךךם`. Press a hotkey and Typhoon rewrites the last thing you typed
into the correct layout — in place, in whatever app you're using.

It works both ways (Hebrew ⇄ English) and auto-detects the direction.

## How it works

Typhoon lives in your system tray and quietly keeps a buffer of the last segment
you typed. When you press the hotkey it:

1. Reads the buffered text (e.g. `יקךךם`).
2. Re-maps each character to the key on the *other* layout (`hello`).
3. Deletes the original with backspaces and types the corrected version.

The buffer is cleared whenever you press Enter/Tab/Esc or move the caret with the
arrow keys, so it only ever rewrites your current word/phrase.

## Setup

```powershell
# from the project root
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

A cyan **T** icon appears in the tray. Type some gibberish, then press the hotkey.

> **Note:** the `keyboard` library installs a low-level Windows hook. If the
> hotkey or replacement doesn't work, run the terminal **as Administrator** —
> elevated apps (and some games) ignore input from non-elevated processes.

### Default hotkey

`Ctrl + Alt + Space` — rewrite the last typed segment.

## Build a standalone .exe

No Python needed on the target machine — produce a single self-contained exe:

```powershell
pip install -r requirements-build.txt
python build.py
```

Output: **`dist\Typhoon.exe`** (~16 MB, one file, no console window). Double-click
it to run; it appears in the tray just like `python main.py`. The build also
generates `assets\typhoon.ico` for the exe icon.

> If the hotkey needs admin rights (see note above), right-click `Typhoon.exe`
> → **Run as administrator**, or set that permanently via the exe's
> Properties → Compatibility tab.

## Configuration

A `config.json` is created/read at the project root (it's git-ignored — it's your
local preference). Defaults:

```json
{
  "hotkey": "ctrl+alt+space",
  "enabled": true,
  "send_delay": 0.005,
  "switch_language": true
}
```

- **hotkey** — any combo the [`keyboard`](https://github.com/boppreh/keyboard)
  library understands, e.g. `"ctrl+alt+q"` or `"pause"`.
- **send_delay** — pause between synthetic keystrokes. Increase it (e.g. `0.02`)
  if replacements come out garbled in a slow app.
- **switch_language** — after fixing text, also switch the focused window's
  input language to match (Hebrew gibberish → English keyboard, and vice-versa)
  so your *next* keystrokes are already in the right layout. Set `false` to
  leave the input language untouched.

You can also toggle Typhoon on/off, **Start with Windows**, or quit from the tray
icon's right-click menu.

## Start with Windows

Right-click the tray icon → **Start with Windows** to launch Typhoon
automatically at login. This writes a per-user entry under
`HKCU\Software\Microsoft\Windows\CurrentVersion\Run` (no admin needed) pointing
at the current exe (or `pythonw main.py` when running from source). Toggle it off
the same way. The path is refreshed every time you enable it, so it survives
moving the project or rebuilding the exe.

## Tests

The layout conversion is pure logic and has no hardware dependency:

```powershell
python tests\test_layout.py
# or, if you have pytest:
pytest
```

## Project layout

```
main.py              # entry point
typhoon/
  layout.py          # Hebrew<->English key maps + convert()
  tracker.py         # in-memory "what did I just type" buffer
  config.py          # config.json load/save
  app.py             # keyboard hooks, global hotkey, tray icon
tests/
  test_layout.py
```

## Caveats

- The buffer mirrors your keystrokes; it can't see text you select with the
  mouse or paste. Typhoon rewrites what *it* recorded since the last reset.
- Windows-only (relies on the Win32 keyboard hook via `keyboard`).
