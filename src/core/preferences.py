# core/preferences.py — Persistent user preferences (JSON-based)

import json
import os


_PREFS_DIR = os.path.join(os.path.expanduser("~"), ".gesturex")
_PREFS_FILE = os.path.join(_PREFS_DIR, "prefs.json")

_DEFAULTS = {
    "camera_always_allow": False,
}


def _load() -> dict:
    """Load preferences from disk, falling back to defaults."""
    if os.path.exists(_PREFS_FILE):
        try:
            with open(_PREFS_FILE, "r") as f:
                data = json.load(f)
            # Merge with defaults so new keys are always present
            merged = {**_DEFAULTS, **data}
            return merged
        except (json.JSONDecodeError, OSError):
            pass
    return dict(_DEFAULTS)


def _save(prefs: dict):
    """Write preferences to disk."""
    os.makedirs(_PREFS_DIR, exist_ok=True)
    with open(_PREFS_FILE, "w") as f:
        json.dump(prefs, f, indent=2)


def get(key: str):
    """Get a single preference value."""
    return _load().get(key, _DEFAULTS.get(key))


def set(key: str, value):
    """Set a single preference value and persist."""
    prefs = _load()
    prefs[key] = value
    _save(prefs)
