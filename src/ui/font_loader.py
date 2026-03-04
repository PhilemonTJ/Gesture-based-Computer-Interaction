# ui/font_loader.py — Load bundled IBM Plex Mono font at runtime (Windows)
#
# Uses the Windows GDI API (AddFontResourceExW) to register .ttf files
# for the current process only — no admin rights, no system-wide install.
# The fonts are removed on cleanup.

import os
import sys
import ctypes
from pathlib import Path

# Windows GDI constants
FR_PRIVATE = 0x10  # font is available only to this process

# Resolve fonts directory (works both as script and PyInstaller bundle)
if getattr(sys, "frozen", False):
    # Running as PyInstaller .exe — fonts are in _MEIPASS/ui/fonts
    _BASE = Path(sys._MEIPASS) / "ui" / "fonts"
else:
    # Running as script — fonts are next to this file
    _BASE = Path(__file__).resolve().parent / "fonts"

_loaded_fonts: list[str] = []


def load_fonts() -> int:
    """
    Register all .ttf files in the bundled fonts directory.

    Returns the number of fonts successfully loaded.
    Must be called BEFORE creating any Tkinter/CTk widgets.
    """
    if os.name != "nt":
        return 0  # only Windows is supported

    gdi32 = ctypes.windll.gdi32
    count = 0

    for ttf in sorted(_BASE.glob("*.ttf")):
        result = gdi32.AddFontResourceExW(str(ttf), FR_PRIVATE, 0)
        if result > 0:
            _loaded_fonts.append(str(ttf))
            count += result

    return count


def unload_fonts() -> None:
    """Remove all fonts registered by load_fonts()."""
    if os.name != "nt":
        return

    gdi32 = ctypes.windll.gdi32
    for path in _loaded_fonts:
        gdi32.RemoveFontResourceExW(path, FR_PRIVATE, 0)
    _loaded_fonts.clear()
