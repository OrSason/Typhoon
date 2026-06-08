"""Typhoon application: keyboard hooks, global hotkey, and system-tray icon.

Run with ``python main.py``. The app sits in the tray; press the configured
hotkey (default ``Ctrl+Alt+Space``) to rewrite the last thing you typed into
the other keyboard layout.
"""

from __future__ import annotations

import threading
import time

import keyboard
import pystray
from PIL import Image

from . import config, icon, layout
from .tracker import TypedBuffer


class TyphoonApp:
    def __init__(self) -> None:
        self.cfg = config.load()
        self.buffer = TypedBuffer()
        self.enabled = bool(self.cfg["enabled"])
        # While we programmatically send keystrokes, ignore the events they
        # generate so they don't corrupt the buffer.
        self._replacing = threading.Lock()
        self._suppress = False
        self.icon: pystray.Icon | None = None

    # ----- keyboard handling -------------------------------------------------

    def _on_key(self, event: keyboard.KeyboardEvent) -> None:
        if self._suppress or event.event_type != "down":
            return
        # ``event.name`` is the logical key; for printable keys it's the char.
        name = event.name or ""
        char = name if len(name) == 1 else None
        self.buffer.feed_key(name, char)

    def _replace_last_segment(self) -> None:
        """Rewrite the buffered text into the other layout, in place."""
        if not self.enabled:
            return
        # Serialize replacements; ignore re-triggers while one is in flight.
        if not self._replacing.acquire(blocking=False):
            return
        try:
            original = self.buffer.text
            if not original.strip():
                return
            fixed = layout.convert(original)
            if fixed == original:
                return

            delay = float(self.cfg["send_delay"])
            self._suppress = True
            try:
                # Delete what's there, then type the corrected text.
                for _ in range(len(original)):
                    keyboard.send("backspace")
                    time.sleep(delay)
                keyboard.write(fixed, delay=delay)
            finally:
                # Let the OS drain our synthetic events before re-listening.
                time.sleep(0.02)
                self._suppress = False

            self.buffer.set(fixed)
        finally:
            self._replacing.release()

    # ----- tray icon ---------------------------------------------------------

    def _make_image(self) -> Image.Image:
        return icon.make_image(self.enabled)

    def _refresh_icon(self) -> None:
        if self.icon is not None:
            self.icon.icon = self._make_image()
            self.icon.title = f"Typhoon — {'on' if self.enabled else 'off'}"

    def _toggle(self, *_args) -> None:
        self.enabled = not self.enabled
        self.cfg["enabled"] = self.enabled
        config.save(self.cfg)
        self._refresh_icon()
        if self.icon is not None:
            self.icon.update_menu()

    def _quit(self, *_args) -> None:
        keyboard.unhook_all()
        if self.icon is not None:
            self.icon.stop()

    def _menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(
                "Enabled",
                self._toggle,
                checked=lambda _item: self.enabled,
            ),
            pystray.MenuItem(f"Hotkey: {self.cfg['hotkey']}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._quit),
        )

    # ----- lifecycle ---------------------------------------------------------

    def run(self) -> None:
        keyboard.hook(self._on_key)
        keyboard.add_hotkey(
            self.cfg["hotkey"], self._replace_last_segment, suppress=False
        )
        self.icon = pystray.Icon(
            "typhoon", self._make_image(), "Typhoon", self._menu()
        )
        self.icon.run()


def main() -> None:
    TyphoonApp().run()
