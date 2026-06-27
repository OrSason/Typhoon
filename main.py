"""Entry point for Typhoon. Run: ``python main.py`` (``--version`` to print the version)."""

from __future__ import annotations

import sys

from typhoon import __version__


def main(argv: list[str] | None = None) -> int:
    """CLI front door.

    ``--version`` / ``-V`` prints the version and exits without touching the
    Windows keyboard/tray libraries (so it works anywhere, including CI). Any
    other invocation launches the tray app.
    """
    args = sys.argv[1:] if argv is None else argv
    if any(a in ("-V", "--version") for a in args):
        print(f"Typhoon {__version__}")
        return 0
    # Import lazily: the tray app pulls in Windows-only deps (keyboard/pystray).
    from typhoon.app import main as run_app

    run_app()
    return 0


if __name__ == "__main__":
    sys.exit(main())
