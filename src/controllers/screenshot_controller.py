# controllers/screenshot_controller.py

import time
import pyautogui
import winsound
import os
import threading


class ScreenshotController:

    def __init__(self, config):
        self.IDLE = 0
        self.OPEN = 1

        self.state = self.IDLE
        self.timer = 0
        self.timeout = config.SCREENSHOT_TIMEOUT
        self.cooldown = config.SCREENSHOT_COOLDOWN
        self.last_time = 0

        # Debounce: gesture must be held for N consecutive frames
        self.debounce = config.SCREENSHOT_DEBOUNCE
        self.fist_frames = 0
        self.open_frames = 0

        self.screenshot_dir = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def is_fist(self, fingers):
        # All 4 fingers curled (ignore thumb — its position varies in a fist)
        return fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0

    def is_open(self, fingers):
        # All 4 fingers extended (ignore thumb — user may or may not extend it)
        return fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1

    def _show_toast(self, filepath):
        """Show a Snipping Tool-like toast notification with screenshot preview."""
        try:
            from win11toast import toast
            abs_path = os.path.abspath(filepath)
            toast(
                "Screenshot Captured.",
                f"Saved to {os.path.basename(filepath)}",
                image=abs_path,
                duration="short",
                on_click=abs_path,   # clicking the toast opens the image
            )
        except Exception:
            pass  # silently fail if toast can't be shown

    def update(self, fingers, img, button):

        current_time = time.time()

        if current_time - self.last_time < self.cooldown:
            return img

        # ── Count consecutive frames for debounce ──
        if self.is_fist(fingers):
            self.fist_frames += 1
            self.open_frames = 0
        elif self.is_open(fingers):
            self.open_frames += 1
            self.fist_frames = 0
        else:
            self.fist_frames = 0
            self.open_frames = 0

        fist_held = self.fist_frames >= self.debounce
        open_held = self.open_frames >= self.debounce

        # ── State machine: OPEN PALM → FIST = screenshot ──
        if self.state == self.IDLE:
            if open_held:
                self.state = self.OPEN
                self.timer = current_time

        elif self.state == self.OPEN:
            if current_time - self.timer > self.timeout:
                self.state = self.IDLE
            elif fist_held:

                filename = os.path.join(self.screenshot_dir, f"screenshot_{int(time.time())}.png")
                screenshot = pyautogui.screenshot()
                screenshot.save(filename)
                winsound.Beep(1200, 150)

                # Show toast notification in a separate thread (non-blocking)
                threading.Thread(target=self._show_toast, args=(filename,), daemon=True).start()

                button.set_active(1.0)

                self.last_time = current_time
                self.state = self.IDLE

        return img