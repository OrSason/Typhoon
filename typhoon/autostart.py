"""Run-at-login support via the per-user Windows registry Run key.

Uses ``HKEY_CURRENT_USER\\...\\Run`` so it needs no admin rights and only ever
affects the current user. The command is (re)written from the *current* exe or
script path each time autostart is enabled, so it stays correct if you move the
project or rebuild the exe.
"""

from __future__ import annotations

import sys
import winreg
from pathlib import Path

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_VALUE_NAME = "Typhoon"


def _launch_command() -> str:
    """The command Windows should run at login to start Typhoon."""
    if getattr(sys, "frozen", False):
        # Frozen one-file exe: just point at it.
        return f'"{sys.executable}"'
    # Running from source: use pythonw.exe (no console window) + main.py.
    exe_dir = Path(sys.executable).parent
    pythonw = exe_dir / "pythonw.exe"
    runner = pythonw if pythonw.exists() else Path(sys.executable)
    main_py = Path(__file__).resolve().parent.parent / "main.py"
    return f'"{runner}" "{main_py}"'


def is_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            value, _ = winreg.QueryValueEx(key, _VALUE_NAME)
            return bool(value)
    except FileNotFoundError:
        return False


def enable() -> None:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
        winreg.SetValueEx(key, _VALUE_NAME, 0, winreg.REG_SZ, _launch_command())


def disable() -> None:
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, _VALUE_NAME)
    except FileNotFoundError:
        pass


def toggle() -> bool:
    """Flip autostart and return the new state."""
    if is_enabled():
        disable()
        return False
    enable()
    return True
