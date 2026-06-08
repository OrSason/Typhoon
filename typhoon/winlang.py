"""Switch the Windows input language of the focused window.

After Typhoon fixes a wrong-layout word, the *layout* is usually still wrong —
so this nudges the foreground window onto the target language (English/Hebrew)
so your next keystrokes come out right.

Implemented with the Win32 ``WM_INPUTLANGCHANGEREQUEST`` message, which targets
just the focused window's input context (no global state, no admin needed).
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

WM_INPUTLANGCHANGEREQUEST = 0x0050
KLF_ACTIVATE = 0x00000001

# Keyboard layout identifiers (low word = language id).
_LAYOUTS = {
    "en": "00000409",  # English (US)
    "he": "0000040D",  # Hebrew
}

_user32 = ctypes.windll.user32
_user32.LoadKeyboardLayoutW.restype = wintypes.HKL
_user32.LoadKeyboardLayoutW.argtypes = [wintypes.LPCWSTR, wintypes.UINT]
_user32.PostMessageW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]


def switch(lang: str) -> bool:
    """Switch the focused window to *lang* (``"en"`` or ``"he"``).

    Returns True if a request was posted. Never raises — language switching is
    a nicety, not worth crashing the replacement over.
    """
    code = _LAYOUTS.get(lang)
    if code is None:
        return False
    try:
        hkl = _user32.LoadKeyboardLayoutW(code, KLF_ACTIVATE)
        hwnd = _user32.GetForegroundWindow()
        if not hwnd or not hkl:
            return False
        _user32.PostMessageW(hwnd, WM_INPUTLANGCHANGEREQUEST, 0, hkl)
        return True
    except OSError:
        return False
