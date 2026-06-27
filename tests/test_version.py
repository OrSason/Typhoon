"""Tests for version surfacing (no keyboard/tray hardware needed).

These only touch ``typhoon/__init__.py`` and ``main.py``'s ``--version`` path,
which is deliberately import-free of the Windows-only deps.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main  # noqa: E402
from typhoon import __version__  # noqa: E402


def test_version_is_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__), __version__


def test_cli_version_flag(capsys=None):
    # Works with or without pytest's capsys: fall back to manual capture.
    if capsys is None:
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main.main(["--version"])
        out = buf.getvalue()
    else:
        rc = main.main(["--version"])
        out = capsys.readouterr().out
    assert rc == 0
    assert out.strip() == f"Typhoon {__version__}"


def test_short_version_flag():
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main.main(["-V"])
    assert rc == 0
    assert __version__ in buf.getvalue()


if __name__ == "__main__":
    import traceback

    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError:
                failures += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    sys.exit(1 if failures else 0)
