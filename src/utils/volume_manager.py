# utils/volume_manager.py
import ctypes
import time


class VolumeManager:
    """
    Robust Windows volume control using virtual key events.
    No COM, no pycaw, no driver dependency.
    """

    VK_VOLUME_UP = 0xAF
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_MUTE = 0xAD

    def __init__(self, step=10):
        self.step = step  # logical step, mapped to key presses

    def _press_key(self, key):
        ctypes.windll.user32.keybd_event(key, 0, 0, 0)
        ctypes.windll.user32.keybd_event(key, 0, 2, 0)

    def increase(self):
        # Each press ≈ 2% on Windows
        presses = max(1, self.step // 2)
        for _ in range(presses):
            self._press_key(self.VK_VOLUME_UP)
            time.sleep(0.01)

    def decrease(self):
        presses = max(1, self.step // 2)
        for _ in range(presses):
            self._press_key(self.VK_VOLUME_DOWN)
            time.sleep(0.01)

    def mute(self):
        self._press_key(self.VK_VOLUME_MUTE)
