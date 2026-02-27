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
        self.dragging = False

    def update(self, fingers, index_tip, dragging, button):
        index_x, index_y = index_tip

        move_gesture = (fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 1)

        if move_gesture or dragging:

            button.is_active = True

            converted_x = np.interp(index_x,
                                    [self.rect_x1, self.rect_x2],
                                    [0, self.screen_width])
            converted_y = np.interp(index_y,
                                    [self.rect_y1, self.rect_y2],
                                    [0, self.screen_height])

            curr_x = self.prev_x + (converted_x - self.prev_x) / self.smoothening
            curr_y = self.prev_y + (converted_y - self.prev_y) / self.smoothening

            curr_x = max(0, min(curr_x, self.screen_width))
            curr_y = max(0, min(curr_y, self.screen_height))

            mouse.move(int(curr_x), int(curr_y))

            self.prev_x, self.prev_y = curr_x, curr_y