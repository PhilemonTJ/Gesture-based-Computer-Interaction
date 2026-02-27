# controllers/mouse_click_controller.py

import mouse
import threading
import time

class ClickController:
    def __init__(self):
        self.l_delay = 0
        self.r_delay = 0

        self.l_thread = threading.Thread(target=self.reset_left)
        self.r_thread = threading.Thread(target=self.reset_right)

    def reset_left(self):
        time.sleep(1)
        self.l_delay = 0
        self.l_thread = threading.Thread(target=self.reset_left)

    def reset_right(self):
        time.sleep(1)
        self.r_delay = 0
        self.r_thread = threading.Thread(target=self.reset_right)

    def update(self, fingers, length, buttons):

        if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 1:

            if length < 40:

                if fingers[3] == 0 and fingers[4] == 0 and self.l_delay == 0:
                    buttons[2].set_active()
                    mouse.click(button='left')
                    self.l_delay = 1
                    self.l_thread.start()

                elif fingers[3] == 1 and fingers[4] == 0 and self.r_delay == 0:
                    buttons[3].set_active()
                    mouse.click(button='right')
                    self.r_delay = 1
                    self.r_thread.start()

                elif fingers[3] == 0 and fingers[4] == 1:
                    buttons[4].set_active()
                    mouse.double_click(button='left')