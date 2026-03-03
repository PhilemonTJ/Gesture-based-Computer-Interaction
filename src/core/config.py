# core/config.py

class Config:
    # ── Camera ──
    CAM_WIDTH = 640
    CAM_HEIGHT = 480
    CAM_FPS = 30

    # ── Interaction rectangle ──
    FRAME_REDUCTION = 180
    RECT_HEIGHT = 240

    # ── Mouse movement ──
    JOIN_THRESHOLD = 45        # px — below = move, above = lock

    # ── OneEuroFilter (adaptive cursor smoothing) ──
    FILTER_MIN_CUTOFF = 1.0    # lower = smoother at low speeds
    FILTER_BETA = 0.007        # higher = more responsive at high speeds

    # ── ROI tracker ──
    ROI_MARGIN = 80            # px — extra padding around hand bounding box
    ROI_MAX_LOST = 5           # frames — fallback to full-frame after N lost frames

    # ── Click ──
    DOUBLE_CLICK_WINDOW = 0.4  # seconds

    # ── Drag & drop ──
    DRAG_PRESS_THRESHOLD = 20   # px — pinch closer to START drag
    DRAG_RELEASE_THRESHOLD = 50 # px — spread wider to STOP drag

    # ── Scroll ──
    SCROLL_DEAD_ZONE = 10      # px — ignore small movement near baseline
    SCROLL_SPEED_FACTOR = 0.02 # scale distance to scroll strength
    SCROLL_MAX = 20            # cap scroll speed

    # ── Volume (knob) ──
    KNOB_STEP_ANGLE = 10.0     # degrees per volume step
    KNOB_COOLDOWN = 0.15       # seconds

    # ── Screenshot ──
    SCREENSHOT_TIMEOUT = 2.0   # seconds — max time for full sequence
    SCREENSHOT_COOLDOWN = 3.0  # seconds — delay between screenshots
    SCREENSHOT_DEBOUNCE = 3    # frames — hold gesture for N frames