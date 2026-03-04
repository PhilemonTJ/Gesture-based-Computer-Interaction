# ui/theme.py — Design tokens (strictly from index3.html palette)
# Palette: monochrome warm taupe/brown — NO blue, NO bright colors
# Font: IBM Plex Mono only (weights 300, 400, 500, 600)

# ── Color palette (from :root in index3.html) ──
BLACK = "#000000"
SURFACE = "#0d0b0b"
SURFACE2 = "#131010"
LIGHT = "#D1D0D0"
MID = "#988686"
DEEP = "#5C4E4E"
BORDER = "#1e1a1a"      # solid approximation of rgba(152,134,134,0.12)
BORDER2 = "#2a2424"     # solid approximation of rgba(152,134,134,0.22)

# ── Accent (warm brown, matching .btn-primary in index3.html) ──
ACCENT = "#5C4E4E"
ACCENT_HOVER = "#6e5c5c"

# ── Status indicators (monochrome — NO red/green/yellow) ──
RED = "#5C4E4E"         # inactive  → deep brown (dimmest)
GREEN = "#D1D0D0"       # active    → off-white  (brightest)
YELLOW = "#988686"      # paused    → taupe      (mid)

# ── Font ──
FONT_FAMILY = "IBM Plex Mono"
FONT_FALLBACK = "Consolas"  # fallback if IBM Plex Mono not installed

# ── Sizes ──
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700
SIDEBAR_WIDTH = 260
