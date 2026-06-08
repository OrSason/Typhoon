"""Load/save user configuration from ``config.json`` next to the project."""

from __future__ import annotations

import json
from pathlib import Path

DEFAULTS: dict = {
    # Global hotkey that rewrites the last typed segment.
    "hotkey": "ctrl+alt+space",
    # Start with conversion active.
    "enabled": True,
    # Small pause (seconds) between sending backspaces/characters so target
    # apps keep up. Raise it if replacements come out garbled in slow apps.
    "send_delay": 0.005,
}

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load() -> dict:
    cfg = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            cfg.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            # Corrupt/unreadable config: fall back to defaults silently.
            pass
    return cfg


def save(cfg: dict) -> None:
    CONFIG_PATH.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8"
    )
