"""Build a standalone Typhoon.exe with PyInstaller.

Usage:
    python build.py

Produces ``dist/Typhoon.exe`` — a single-file, no-console tray app that runs
without a Python install. Requires the build dependency:
    pip install pyinstaller
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ICON_PATH = ASSETS / "typhoon.ico"


def generate_icon() -> None:
    """Render the app icon to a multi-resolution .ico for the exe."""
    from typhoon.icon import make_image

    ASSETS.mkdir(exist_ok=True)
    base = make_image(enabled=True, size=256)
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base.save(ICON_PATH, format="ICO", sizes=sizes)
    print(f"icon -> {ICON_PATH}")


def build() -> int:
    if importlib.util.find_spec("PyInstaller") is None:
        print(
            "PyInstaller not found. Install build deps first:\n"
            "    pip install -r requirements-build.txt",
            file=sys.stderr,
        )
        return 1

    generate_icon()

    # Invoke via the current interpreter so it works without the venv's
    # Scripts dir being on PATH.
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",        # single self-contained .exe
        "--windowed",       # no console window (it's a tray app)
        "--name", "Typhoon",
        "--icon", str(ICON_PATH),
        # pystray/keyboard pull their backends dynamically — pin them so the
        # frozen exe doesn't miss them.
        "--hidden-import", "pystray._win32",
        "--hidden-import", "PIL._tkinter_finder",
        str(ROOT / "main.py"),
    ]
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode == 0:
        print(f"\nBuilt: {ROOT / 'dist' / 'Typhoon.exe'}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
