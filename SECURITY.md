# Security & Privacy — Gesture-Based Computer Interaction

## Overview

This application runs **entirely offline** on the user's local machine.
No internet connection is required. No data leaves the device.

---

## Data Handling

| Data Type | Collected? | Stored? | Transmitted? |
|---|---|---|---|
| Camera video feed | ✅ Processed in real-time | ❌ Never recorded | ❌ Never sent |
| Hand landmark coordinates | ✅ Computed per frame | ❌ Discarded after use | ❌ Never sent |
| Screenshots | ✅ On explicit gesture | ✅ Saved to user's Pictures folder | ❌ Never sent |
| User credentials / PII | ❌ Not applicable | ❌ Not applicable | ❌ Not applicable |

---

## Network Usage

**This application makes zero network requests.**

- No HTTP calls, no WebSocket connections, no telemetry, no analytics
- No network libraries (`requests`, `socket`, `urllib`, `http`) are imported anywhere in the codebase
- The application functions identically with the internet disconnected

### How to Verify

1. **Code inspection** — the source is open; search for any network import:
   ```bash
   grep -r "import requests\|import socket\|import urllib\|import http" src/
   # Returns: 0 results
   ```

2. **Firewall test** — block the application in Windows Firewall.
   It runs identically, proving it never attempted network access.

3. **Network monitor** — run Wireshark or Windows Resource Monitor while
   the app is active. Filter by the Python process. Zero packets = zero sharing.

---

## OS-Level Permissions

| Permission | Why Needed | Scope |
|---|---|---|
| **Camera** | Hand detection via MediaPipe | Only used while app is running; visible camera window confirms active usage |
| **Mouse/keyboard control** | Gesture-driven cursor, clicks, scrolling | Actions only triggered by recognized hand gestures |
| **Screen capture** | Screenshot gesture (fist→open→fist) | Requires deliberate 3-step gesture; saves to user's Pictures/Screenshots folder; audible beep confirms capture |
| **System volume** | Volume knob gesture | Changes volume via standard Windows audio API |

- **No admin/root privileges** required — runs as a normal user process
- **No background services** — only active when the application window is open
- **No startup registration** — does not auto-start with Windows

---

## Input Injection Safety

The application uses `mouse` and `pyautogui` libraries to simulate hardware input (clicks, movement, scrolling). Safeguards in place:

1. **Gesture-gated** — input only fires in response to recognized hand gestures detected by MediaPipe
2. **Mutual exclusion** — only one gesture mode (move, click, drag, scroll, volume) is active at a time
3. **Hand-loss cleanup** — if the hand leaves the camera frame, all active inputs (e.g., drag) are immediately released
4. **Debounced triggers** — screenshot requires holding a gesture for multiple consecutive frames, preventing accidental activation
5. **Edge-triggered clicks** — clicks fire once on finger bend transition, not continuously while bent

---

## Screenshot Security

- Screenshots are saved to `%USERPROFILE%\Pictures\Screenshots` (Windows default)
- Capture requires a deliberate 3-step gesture: open palm → fist (within 2 seconds)
- Each gesture step must be held for 3+ consecutive frames (prevents accidental triggers)
- An audible beep (1200 Hz) sounds on capture
- A Windows toast notification confirms the screenshot with a preview
- 3-second cooldown between screenshots prevents spam

---

## Dependencies

All dependencies are listed in `requirements.txt` with pinned versions.
To audit for known vulnerabilities:

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

| Dependency | Purpose | Network Usage |
|---|---|---|
| `opencv-python` | Camera capture, image processing | None |
| `mediapipe` | Hand landmark detection (ML) | None (model runs locally) |
| `numpy` | Numerical computation | None |
| `pyautogui` | Screenshot capture | None |
| `mouse` | Mouse control (click, move, scroll) | None |
| `pycaw` | Windows audio API | None |
| `win11toast` | Toast notifications | None |

---

## For Production Deployment

If distributed as a standalone application:

- [ ] Code sign the executable (prevents tampering warnings)
- [ ] Add camera permission prompt on first launch
- [ ] Include in-app privacy policy accessible from settings
- [ ] Pin and audit all dependency versions
- [ ] Add on/off toggle for input injection (UI already designed)
