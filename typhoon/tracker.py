"""A small in-memory buffer of what the user has recently typed.

This is deliberately pure (no keyboard library imports) so the segmentation
logic can be unit-tested. The keyboard hooks in :mod:`typhoon.app` feed it.
"""

from __future__ import annotations


class TypedBuffer:
    """Tracks the current typed segment so it can be rewritten on demand.

    The buffer accumulates printable characters (including spaces, so a short
    phrase can be fixed at once) and is cleared whenever the user does
    something that makes the on-screen text diverge from what we've recorded —
    pressing Enter, Tab, Escape, or moving the caret with arrows/Home/End.
    """

    # Keys that end the current segment and invalidate the buffer.
    RESET_KEYS = frozenset(
        {
            "enter", "return", "tab", "esc", "escape",
            "up", "down", "left", "right",
            "home", "end", "page up", "page down",
            "delete",
        }
    )

    def __init__(self) -> None:
        self._chars: list[str] = []

    @property
    def text(self) -> str:
        return "".join(self._chars)

    def __len__(self) -> int:
        return len(self._chars)

    def append(self, ch: str) -> None:
        """Record a single printable character that was typed."""
        self._chars.append(ch)

    def backspace(self) -> None:
        """Mirror a Backspace keypress."""
        if self._chars:
            self._chars.pop()

    def reset(self) -> None:
        self._chars.clear()

    def set(self, text: str) -> None:
        """Replace the buffer contents (used after we rewrite the text)."""
        self._chars = list(text)

    def feed_key(self, name: str, char: str | None) -> None:
        """Update the buffer from a key event.

        *name* is the key's logical name (e.g. ``"space"``, ``"backspace"``)
        and *char* is the printable character it produced, if any.
        """
        if name in self.RESET_KEYS:
            self.reset()
        elif name == "backspace":
            self.backspace()
        elif name == "space":
            self.append(" ")
        elif char is not None and len(char) == 1 and char.isprintable():
            self.append(char)
