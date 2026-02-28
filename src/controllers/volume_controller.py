# controllers/volume_controller.py

import time

class VolumeController:

    def __init__(self, config, volume_manager):
        self.prev_angle = None
        self.rotation_accumulator = 0

        # self.step_angle = config.KNOB_THRESHOLD      # degrees per volume step
        self.step_angle = 10.0     # degrees per volume step
        self.cooldown = config.KNOB_COOLDOWN         # small delay safety
        self.last_time = 0

        self.volume_manager = volume_manager

    def update(self, fingers, angle, buttons):

        # ✋ All fingers UP (true knob mode)
        if fingers == [1, 1, 1, 1, 1]:

            if self.prev_angle is not None:

                delta = angle - self.prev_angle

                # Handle wraparound (0-360 correction)
                if delta > 180:
                    delta -= 360
                elif delta < -180:
                    delta += 360

                # Accumulate rotation
                self.rotation_accumulator += delta

                now = time.time()

                # Prevent ultra fast jitter spam
                if (now - self.last_time) > self.cooldown:

                    # Rotate Right → Volume Up
                    while self.rotation_accumulator >= self.step_angle:
                        self.volume_manager.increase()
                        buttons[9].set_active()
                        self.rotation_accumulator -= self.step_angle
                        self.last_time = now

                    # Rotate Left → Volume Down
                    while self.rotation_accumulator <= -self.step_angle:
                        self.volume_manager.decrease()
                        buttons[10].set_active()
                        self.rotation_accumulator += self.step_angle
                        self.last_time = now

            self.prev_angle = angle

        else:
            # Reset when leaving knob mode
            self.prev_angle = None
            self.rotation_accumulator = 0