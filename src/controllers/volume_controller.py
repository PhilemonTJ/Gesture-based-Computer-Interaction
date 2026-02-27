# controllers/volume_controller.py

import time

class VolumeController:

    def __init__(self, config, volume_manager):
        self.prev_angle = None
        self.threshold = config.KNOB_THRESHOLD
        self.cooldown = config.KNOB_COOLDOWN
        self.last_time = 0
        self.volume_manager = volume_manager

    def update(self, fingers, angle, buttons):

        if fingers == [0, 1, 1, 1, 1]:

            if self.prev_angle is not None:
                delta = angle - self.prev_angle

                if delta > 180:
                    delta -= 360
                elif delta < -180:
                    delta += 360

                now = time.time()

                if abs(delta) > self.threshold and (now - self.last_time) > self.cooldown:

                    if delta > 0:
                        self.volume_manager.increase()
                        buttons[9].set_active()
                    else:
                        self.volume_manager.decrease()
                        buttons[10].set_active()

                    self.last_time = now

            self.prev_angle = angle

        else:
            self.prev_angle = None