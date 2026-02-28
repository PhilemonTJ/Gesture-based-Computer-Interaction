# controllers/mouse_movement_controller.py

import numpy as np
import mouse

class MovementController:
    def __init__(self, config, rect_bounds, screen_size):
        self.smoothening = config.SMOOTHENING
        self.rect_x1, self.rect_y1, self.rect_x2, self.rect_y2 = rect_bounds
        self.screen_width, self.screen_height = screen_size

        self.prev_x = 0
        self.prev_y = 0

        # Distance threshold between index & middle
        self.join_threshold = 35  # tune if needed

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

                # Convert to screen coords
                converted_x = np.interp(
                    pointer_x,
                    [self.rect_x1, self.rect_x2],
                    [0, self.screen_width]
                )

                converted_y = np.interp(pointer_y,
                                        [self.rect_y1, self.rect_y2],
                                        [0, self.screen_height])

                # Smooth movement
                curr_x = self.prev_x + (converted_x - self.prev_x) / self.smoothening
                curr_y = self.prev_y + (converted_y - self.prev_y) / self.smoothening

                # Clamp
                curr_x = max(0, min(curr_x, self.screen_width))
                curr_y = max(0, min(curr_y, self.screen_height))

                mouse.move(int(curr_x), int(curr_y))

                self.prev_x, self.prev_y = curr_x, curr_y
                
            else:
                # 🔹 LOCK MODE (apart)
                lock_button.set_active()