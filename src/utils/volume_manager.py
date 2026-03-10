# utils/volume_manager.py
import subprocess
import time


class VolumeManager:
    """
    Linux volume control using amixer (PulseAudio/PipeWire compatible).
    """

    def __init__(self, step=2):
        self.step = step  # logical step

    def increase(self):
        subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{self.step}%+"])
        time.sleep(0.01)

    def decrease(self):
        subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{self.step}%-"])
        time.sleep(0.01)

    def mute(self):
        subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "toggle"])
