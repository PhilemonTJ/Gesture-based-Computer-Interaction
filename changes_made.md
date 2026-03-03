# Changes Made — March 1–2, 2026

All changes made since the last pull on `refactor/controllers` branch.

---

## Bug Fixes

###  Gesture Mutual Exclusion (`main.py`)
- **Before:** All 6 controllers ran on every frame independently — drag, click, scroll, volume could all fire simultaneously
- **After:** Controllers run through an **if/elif priority chain**. Only the active gesture's controllers execute
- Added `active_mode` variable with **sticky mode** — movement mode persists when index bends for click

###  DragController Had No Finger Guard (`drag_drop_controller.py`)
- **Before:** Drag only checked thumb-index distance — fired anytime thumb was near index, regardless of gesture
- **After:** Drag only runs when `active_mode == "drag"` (index up, middle down)
- Added **hysteresis** — press at <20px, release at >50px (prevents mid-drag release from jitter)
- Added `safe_release()` method for clean transitions between modes

###  Click Fired During All Gestures (`mouse_click_controller.py`, `main.py`)
- **Before:** Click detection ran on every frame regardless of gesture mode
- **After:** Click only fires in **lock mode** (index+middle spread apart ≥45px)
- Added `sync_state()` method to prevent phantom clicks on mode switch

###  Drag Stayed Pressed When Hand Left Camera (`main.py`)
- **Before:** If hand left the frame during drag, `mouse.release()` never ran — mouse stayed pressed forever
- **After:** `else` branch on hand detection calls `drag.safe_release()` and resets mode to idle

###  Screenshot Never Triggered (`screenshot_controller.py`)
- **Before:** `is_fist` required `[1,0,0,0,0]` and `is_open` required `[0,1,1,1,1]` — didn't match natural hand poses
- **After:** Both now **ignore thumb** — fist = all 4 fingers down, open = all 4 fingers up
- Added **frame-count debounce** (3 frames) — prevents accidental triggers from brief poses

###  Volume/Scroll Fired During Screenshot Gesture (`main.py`)
- **Before:** Open palm step `[1,1,1,1,1]` triggered volume controller during screenshot sequence
- **After:** Volume and scroll are **skipped** when screenshot state machine is active (not IDLE)

---

## New Features

### FPS Counter (`main.py`)
- Live FPS displayed in **green** in the top-right corner of camera window

### Debug Overlay (`main.py`)
- **Red text** in top-left showing current `Fingers: [0,1,1,0,0]` array and `Mode: move`
- Visible during runtime for real-time gesture debugging

### Cursor Movement During Drag (`mouse_movement_controller.py`)
- Extracted `move_cursor_to(pointer)` method from `update()`
- Cursor now follows index fingertip during active drag (not just movement mode)

---

## Architecture Improvements

### Centralized Config (`core/config.py`)
All hardcoded thresholds moved to one file:

| Constant | Value | Purpose |
|---|---|---|
| `JOIN_THRESHOLD` | 45 | Move vs lock finger distance (px) |
| `DOUBLE_CLICK_WINDOW` | 0.4 | Double click time window (s) |
| `DRAG_PRESS_THRESHOLD` | 20 | Pinch distance to start drag (px) |
| `DRAG_RELEASE_THRESHOLD` | 50 | Spread distance to stop drag (px) |
| `SCROLL_DEAD_ZONE` | 10 | Ignore small scroll movement (px) |
| `SCROLL_SPEED_FACTOR` | 0.02 | Scroll sensitivity |
| `SCROLL_MAX` | 20 | Max scroll speed |
| `KNOB_STEP_ANGLE` | 10.0 | Degrees per volume step |
| `KNOB_COOLDOWN` | 0.15 | Volume action cooldown (s) |
| `SCREENSHOT_DEBOUNCE` | 3 | Frames to hold gesture |

All 6 controllers now accept `config` in `__init__()`.

---

## New Files
- `INSTRUCTIONS.txt` — Gesture guide with all 7 gestures and quick reference card
- `src/utils/filters.py` — OneEuroFilter (created, not yet integrated)
- `src/utils/roi_tracker.py` — ROI tracking (created, not yet integrated)

## Modified Files
| File | Changes |
|---|---|
| `src/main.py` | Priority chain, sticky mode, FPS, debug overlay, hand-lost cleanup, screenshot isolation |
| `src/core/config.py` | 14 centralized constants (was 6) |
| `src/controllers/drag_drop_controller.py` | Hysteresis, safe_release, config |
| `src/controllers/mouse_click_controller.py` | sync_state, lock-only click, config |
| `src/controllers/mouse_movement_controller.py` | move_cursor_to extraction, config |
| `src/controllers/screenshot_controller.py` | Thumb-agnostic detection, debounce, config |
| `src/controllers/scroll_controller.py` | Config |
| `src/controllers/volume_controller.py` | Config |
| `.gitignore` | Added `brain/` |
