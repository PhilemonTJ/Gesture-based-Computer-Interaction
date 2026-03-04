# controllers/mouse_movement_controller.py

import numpy as np
import mouse
import time
from utils.filters import OneEuroFilter


class MovementController:
    def __init__(self, config, rect_bounds, screen_size):
        self.rect_x1, self.rect_y1, self.rect_x2, self.rect_y2 = rect_bounds
        self.screen_width, self.screen_height = screen_size

        # Distance threshold between index & middle
        self.join_threshold = config.JOIN_THRESHOLD

        # Adaptive smoothing filters (one per axis)
        self.filter_x = OneEuroFilter(
            min_cutoff=config.FILTER_MIN_CUTOFF,
            beta=config.FILTER_BETA
        )
        self.filter_y = OneEuroFilter(
            min_cutoff=config.FILTER_MIN_CUTOFF,
            beta=config.FILTER_BETA
        )

    def move_cursor_to(self, pointer):
        """Move the cursor to follow a point in camera-space.

        Uses OneEuroFilter for adaptive smoothing:
        - slow movement → heavy smoothing (no jitter)
        - fast movement → light smoothing (responsive)

        Args:
            pointer: (x, y) in camera pixel coordinates.
        """
        pointer_x, pointer_y = pointer

        # Convert camera coords to screen coords
        converted_x = np.interp(
            pointer_x,
            [self.rect_x1, self.rect_x2],
            [0, self.screen_width]
        )
        converted_y = np.interp(
            pointer_y,
            [self.rect_y1, self.rect_y2],
            [0, self.screen_height]
        )

        # Adaptive smoothing
        t = time.time()
        smooth_x = self.filter_x(t, converted_x)
        smooth_y = self.filter_y(t, converted_y)

        # Clamp
        smooth_x = max(0, min(smooth_x, self.screen_width))
        smooth_y = max(0, min(smooth_y, self.screen_height))

        mouse.move(int(smooth_x), int(smooth_y))

    def update(self, fingers, index_tip, middle_tip,
               distance, move_button, lock_button):

        # Both index and middle must be up & thumb is down
        if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[3] == 0 and fingers[4] == 0:

            # Calculate pointer position = midpoint
            pointer_x = (index_tip[0] + middle_tip[0]) // 2
            pointer_y = (index_tip[1] + middle_tip[1]) // 2

            # Decide mode based on distance
            if distance < self.join_threshold:
                # 🔹 MOVE MODE (joined)
                move_button.set_active()
                self.move_cursor_to((pointer_x, pointer_y))

            else:
                # 🔹 LOCK MODE (apart)
                lock_button.set_active()