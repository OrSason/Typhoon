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

from . import autostart, config, icon, layout, winlang
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
        # Ignore keys pressed while Ctrl/Alt/Win are held: that's a shortcut
        # (e.g. our own hotkey), not text. Without this the hotkey's Space
        # leaks into the buffer and corrupts the first replacement.
        if self._modifier_held():
            return
        # ``event.name`` is the logical key; for printable keys it's the char.
        name = event.name or ""
        char = name if len(name) == 1 else None
        self.buffer.feed_key(name, char)

    @staticmethod
    def _modifier_held() -> bool:
        for mod in ("ctrl", "alt", "left windows", "right windows"):
            try:
                if keyboard.is_pressed(mod):
                    return True
            except (ValueError, KeyError):
                pass
        return False

    # Modifier keys that may be held down when the hotkey fires; we force them
    # up before sending synthetic input so they don't get stuck or alter it.
    _MODIFIERS = (
        "ctrl", "left ctrl", "right ctrl",
        "alt", "left alt", "right alt", "alt gr",
        "shift", "left shift", "right shift",
        "left windows", "right windows",
    )

    def _release_modifiers(self) -> None:
        for mod in self._MODIFIERS:
            try:
                keyboard.release(mod)
            except (ValueError, KeyError):
                # Not every name exists on every layout/keyboard — ignore.
                pass

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
            direction = layout.detect_direction(original)
            fixed = layout.convert(original, direction)
            if fixed == original:
                return

            delay = float(self.cfg["send_delay"])
            self._suppress = True
            try:
                # The hotkey is still physically held (e.g. Ctrl+Alt), so let
                # go of the modifiers first — otherwise our backspaces become
                # Ctrl+Backspace and typed chars get modified.
                self._release_modifiers()
                time.sleep(0.01)
                # Delete what's there, then type the corrected text.
                for _ in range(len(original)):
                    keyboard.send("backspace")
                    time.sleep(delay)
                # restore_state_after=False is critical: the default re-presses
                # the modifiers we just released, which leaves Ctrl "stuck".
                keyboard.write(fixed, delay=delay, restore_state_after=False)
            finally:
                # Let the OS drain our synthetic events before re-listening.
                time.sleep(0.02)
                self._suppress = False

            self.buffer.set(fixed)

            # The layout was wrong, so switch the focused window to the target
            # language too — that way your *next* keystrokes come out right.
            if self.cfg.get("switch_language", True):
                winlang.switch("en" if direction == "he2en" else "he")
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

    def _toggle_autostart(self, *_args) -> None:
        autostart.toggle()
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
            pystray.MenuItem(
                "Start with Windows",
                self._toggle_autostart,
                checked=lambda _item: autostart.is_enabled(),
            ),
            pystray.MenuItem(f"Hotkey: {self.cfg['hotkey']}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._quit),
        )

    # ----- lifecycle ---------------------------------------------------------

    def run(self) -> None:
        keyboard.hook(self._on_key)
        # suppress=True so the hotkey combo (incl. its Space) never reaches the
        # focused app — otherwise a stray Space gets inserted next to the text.
        keyboard.add_hotkey(
            self.cfg["hotkey"], self._replace_last_segment, suppress=True
        )
        self.icon = pystray.Icon(
            "typhoon", self._make_image(), "Typhoon", self._menu()
        )
        self.icon.run()


def main() -> None:
    TyphoonApp().run()
