# controllers/scroll_controller.py

import mouse

class ScrollController:

    def __init__(self, config):
        self.baseline_y = None
        self.dead_zone = config.SCROLL_DEAD_ZONE
        self.speed_factor = config.SCROLL_SPEED_FACTOR
        self.max_scroll = config.SCROLL_MAX
        self.lock_threshold = config.JOIN_THRESHOLD  # reuse same threshold

    def update(self, fingers, index_tip, buttons, finger_distance=0):

        # Scroll Mode → Thumb + Index + Middle UP
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:

            # 🔒 Scroll Lock — fingers spread apart = pause scrolling
            if finger_distance >= self.lock_threshold:
                return

            current_y = index_tip[1]

            # 🟢 Capture baseline once when scroll mode starts
            if self.baseline_y is None:
                self.baseline_y = current_y
                return

            # Distance from baseline
            delta = self.baseline_y - current_y

            # Dead zone near baseline (no scroll)
            if abs(delta) < self.dead_zone:
                return

            # Convert distance to scroll amount
            scroll_amount = int(delta * self.speed_factor)

            # Clamp to avoid extreme jumps
            scroll_amount = max(-self.max_scroll,
                                min(self.max_scroll, scroll_amount))

            if scroll_amount > 0:
                buttons[5].set_active()  # Scroll Up
            else:
                buttons[6].set_active()  # Scroll Down

            mouse.wheel(delta=scroll_amount)

        else:
            # 🔴 Reset baseline when thumb released
            self.baseline_y = None