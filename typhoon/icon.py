"""Tray/app icon drawing, shared by the running app and the build script."""

from __future__ import annotations

from PIL import Image, ImageDraw


def make_image(enabled: bool = True, size: int = 64) -> Image.Image:
    """A stylized 'T' icon — cyan on dark, dimmed grey when disabled."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 64  # scale factor so the design holds at any size
    bg = (24, 28, 36, 255)
    fg = (0, 200, 220, 255) if enabled else (110, 110, 110, 255)
    d.rounded_rectangle(
        [4 * s, 4 * s, size - 4 * s, size - 4 * s], radius=12 * s, fill=bg
    )
    # Chunky 'T': crossbar + stem.
    d.rectangle([16 * s, 18 * s, 48 * s, 26 * s], fill=fg)
    d.rectangle([28 * s, 18 * s, 36 * s, 48 * s], fill=fg)
    return img
