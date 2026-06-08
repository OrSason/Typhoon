"""Unit tests for the layout conversion (no keyboard hardware needed)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typhoon import layout  # noqa: E402


def test_hebrew_gibberish_to_english():
    # The canonical example: 'hello' typed on a Hebrew layout.
    assert layout.convert("יקךךם") == "hello"


def test_english_to_hebrew_roundtrip():
    word = "shalom"
    he = layout.convert(word, direction="en2he")
    assert layout.convert(he, direction="he2en") == word


def test_direction_autodetect_prefers_hebrew_fix():
    assert layout.detect_direction("יקךךם") == "he2en"
    assert layout.detect_direction("hello") == "en2he"


def test_unmapped_characters_pass_through():
    assert layout.convert("123 ", direction="he2en") == "123 "


def test_multiword_phrase():
    # 'hi there' on a Hebrew layout, space preserved.
    typed = layout.convert("hi there", direction="en2he")
    assert layout.convert(typed) == "hi there"


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
