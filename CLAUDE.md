# Typhoon — repo-specific guidance

Windows-only background tray app that fixes wrong-keyboard-layout text
(Hebrew ⇄ English). Pure Python.

## Commands

- **Setup:** `py -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt`
- **Run:** `python main.py` (lives in the system tray; hotkey rewrites last typed text)
- **Test:** `python tests\test_layout.py` (or `pytest`)
- **Build exe:** `pip install -r requirements-build.txt; python build.py` →
  `dist\Typhoon.exe` (one-file, windowed). `build.py` generates `assets\typhoon.ico`.

## Architecture

- `typhoon/layout.py` — the character maps (`EN_TO_HE` / `HE_TO_EN`) and
  `convert()`. **Pure, unit-tested.** Add new layouts/keys here.
- `typhoon/tracker.py` — `TypedBuffer`, the pure keystroke buffer + reset rules.
- `typhoon/config.py` — reads/writes `config.json` (git-ignored, user-local).
- `typhoon/icon.py` — `make_image()`, the tray/exe icon drawing (shared by the
  app and `build.py`).
- `typhoon/app.py` — the only module that touches `keyboard`/`pystray`. Keyboard
  hooks feed the buffer; the hotkey triggers in-place replacement.
- `build.py` — PyInstaller one-file build; renders the `.ico` then freezes
  `main.py`.

## Conventions

- Keep keyboard/tray side-effects confined to `app.py`; keep `layout.py` and
  `tracker.py` import-free of hardware libs so they stay testable.
- `config.json` is local-only — never commit it (already in `.gitignore`).
- When editing replacement logic in `app.py`, remember the `_suppress` flag:
  synthetic keystrokes must not feed back into the buffer.
