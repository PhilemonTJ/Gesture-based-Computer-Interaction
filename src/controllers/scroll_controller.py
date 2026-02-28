# controllers/scroll_controller.py

import mouse

class ScrollController:

    def __init__(self):
        self.baseline_y = None
        self.dead_zone = 10        # ignore small movement near baseline
        self.speed_factor = 0.02   # scale distance to scroll strength
        self.max_scroll = 20       # cap scroll speed

    def update(self, fingers, index_tip, buttons):

        # Scroll Mode → Thumb + Index + Middle UP
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:

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