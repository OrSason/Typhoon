"""Keyboard-layout character maps and conversion logic.

The standard Israeli Hebrew keyboard maps each physical QWERTY key to a
Hebrew character. When you *mean* to type English but Windows is set to the
Hebrew layout, every keystroke produces the Hebrew char that shares that
physical key — so ``hello`` comes out as ``יקךךם``.

``EN_TO_HE`` below is keyed by the English character produced on a US-QWERTY
layout and maps to the Hebrew character produced by the same physical key.
``HE_TO_EN`` is the inverse. :func:`convert` auto-detects which way to flip.
"""

from __future__ import annotations

# English (US-QWERTY) char -> Hebrew char on the same physical key.
EN_TO_HE: dict[str, str] = {
    # top letter row  q w e r t y u i o p
    "q": "/", "w": "'", "e": "ק", "r": "ר", "t": "א",
    "y": "ט", "u": "ו", "i": "ן", "o": "ם", "p": "פ",
    # home row  a s d f g h j k l ; '
    "a": "ש", "s": "ד", "d": "ג", "f": "כ", "g": "ע",
    "h": "י", "j": "ח", "k": "ל", "l": "ך", ";": "ף", "'": ",",
    # bottom row  z x c v b n m , . /
    "z": "ז", "x": "ס", "c": "ב", "v": "ה", "b": "נ",
    "n": "מ", "m": "צ", ",": "ת", ".": "ץ", "/": ".",
}

# Inverse map: Hebrew char -> English char on the same physical key.
HE_TO_EN: dict[str, str] = {he: en for en, he in EN_TO_HE.items()}


def _is_hebrew(ch: str) -> bool:
    """True if *ch* is in the Hebrew Unicode block (U+0590–U+05FF)."""
    return "֐" <= ch <= "׿"


def detect_direction(text: str) -> str:
    """Guess which way to convert based on the script of *text*.

    Returns ``"he2en"`` when the text looks like Hebrew gibberish that should
    become English (the common case), otherwise ``"en2he"``.
    """
    hebrew = sum(1 for c in text if _is_hebrew(c))
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    # Tie goes to he2en: that's the annoyance this app exists to fix.
    return "he2en" if hebrew >= latin else "en2he"


def convert(text: str, direction: str | None = None) -> str:
    """Re-map *text* between the Hebrew and English keyboard layouts.

    Characters with no mapping (digits, spaces, unknown symbols) pass through
    unchanged. When *direction* is ``None`` it is auto-detected.
    """
    if direction is None:
        direction = detect_direction(text)
    table = HE_TO_EN if direction == "he2en" else EN_TO_HE
    return "".join(table.get(ch, ch) for ch in text)
