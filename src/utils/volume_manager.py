# utils/volume_manager.py
import subprocess
import time


class VolumeManager:
    """
    macOS volume control using osascript.
    """

    def __init__(self, step=2):
        self.step = step  # logical step

    def increase(self):
        # macOS volume is out of 100, increase relative to current volume
        subprocess.run(["osascript", "-e", f"set volume output volume (output volume of (get volume settings) + {self.step})"])
        time.sleep(0.01)

    def decrease(self):
        subprocess.run(["osascript", "-e", f"set volume output volume (output volume of (get volume settings) - {self.step})"])
        time.sleep(0.01)

    def mute(self):
        subprocess.run(["osascript", "-e", "set volume with output muted"])
