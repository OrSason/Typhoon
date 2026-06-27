# Versioning

Typhoon follows [Semantic Versioning 2.0.0](https://semver.org/): `MAJOR.MINOR.PATCH`.

## Single source of truth

The version lives in **one** place:

```python
# typhoon/__init__.py
__version__ = "0.2.0"
```

Everything that shows a version reads it from there — never hard-code a version
anywhere else:

- **CLI:** `python main.py --version` (or `-V`) prints `Typhoon <version>` and exits.
- **Tray app:** the version appears in the tray-icon tooltip and as the
  (disabled) header item at the top of the right-click menu.
- **Frozen exe:** `Typhoon.exe` surfaces the same tooltip/menu since it freezes
  the same code.

## When to bump (what each part means)

Decide the bump from the nature of the change:

| Change | Bump | Example |
| --- | --- | --- |
| **Breaking** — removes/renames a config key, changes the default hotkey behavior, or otherwise breaks an existing user's setup | **MAJOR** | drop `switch_language`, change `config.json` schema incompatibly |
| **Feature** — new, backward-compatible capability | **MINOR** | add a new layout pair, a new tray option, a `--version` flag |
| **Fix** — backward-compatible bug fix, no new capability | **PATCH** | stop Ctrl getting stuck, fix first-press echo |

Rule of thumb: **patch = fix, minor = feature, major = breaking.**

Pre-1.0.0 note: while on `0.x`, anything can in principle change, but we still
apply the table above so the history stays meaningful.

## Release flow

1. Make your change on a feature/fix branch.
2. Move the relevant lines from `[Unreleased]` in `CHANGELOG.md` into a new
   version section with today's date.
3. Bump `__version__` in `typhoon/__init__.py` to match.
4. Verify: `python main.py --version`, `python tests/test_layout.py`,
   `python tests/test_version.py`.
5. Open a PR. After merge, tag the commit `vMAJOR.MINOR.PATCH`.
