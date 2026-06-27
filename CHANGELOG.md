# Changelog

All notable changes to Typhoon are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).
See [docs/VERSIONING.md](docs/VERSIONING.md) for how versions are decided.

## [Unreleased]

## [0.2.0] - 2026-06-27

### Added
- Single SemVer source of truth in `typhoon/__init__.py` (`__version__`),
  surfaced everywhere the app presents itself.
- `python main.py --version` (and `-V`) prints `Typhoon <version>` and exits
  without loading the Windows keyboard/tray libraries.
- Version shown in the tray-icon tooltip and as a header item in the
  right-click menu.
- `docs/VERSIONING.md` documenting the patch/minor/major rules and release flow.
- This changelog.

## [0.1.0] - 2026-06-08

### Added
- Initial release: Windows background tray app that rewrites the last typed
  segment into the correct keyboard layout (Hebrew ⇄ English) on a global
  hotkey, with auto-detection of direction.
- Configurable, rebindable hotkey (default `Ctrl+Alt+Win`), persisted to
  `config.json`.
- Optional input-language switch after a fix so the next keystrokes use the
  right layout.
- "Start with Windows" run-at-login toggle (per-user `Run` registry key).
- PyInstaller one-file build (`build.py`) producing a standalone `Typhoon.exe`.

[Unreleased]: https://github.com/OrSason/Typhoon/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/OrSason/Typhoon/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/OrSason/Typhoon/releases/tag/v0.1.0
