# controllers/screenshot_controller.py

import time
import pyautogui
import winsound
import os

class ScreenshotController:

    def __init__(self, config):
        self.IDLE = 0
        self.FIST = 1
        self.OPEN = 2

        self.state = self.IDLE
        self.timer = 0
        self.timeout = config.SCREENSHOT_TIMEOUT
        self.cooldown = config.SCREENSHOT_COOLDOWN
        self.last_time = 0

        os.makedirs("screenshots", exist_ok=True)

    def is_fist(self, fingers):
        return fingers == [1,0,0,0,0]

    def is_open(self, fingers):
        return fingers == [0,1,1,1,1]

    def update(self, fingers, img, button):

        current_time = time.time()

        if current_time - self.last_time < self.cooldown:
            return img

        if self.state == self.IDLE:
            if self.is_fist(fingers):
                self.state = self.FIST
                self.timer = current_time

        elif self.state == self.FIST:
            if current_time - self.timer > self.timeout:
                self.state = self.IDLE
            elif self.is_open(fingers):
                self.state = self.OPEN

        elif self.state == self.OPEN:
            if current_time - self.timer > self.timeout:
                self.state = self.IDLE
            elif self.is_fist(fingers):

                filename = f"screenshots/screenshot_{int(time.time())}.png"
                screenshot = pyautogui.screenshot()
                screenshot.save(filename)
                winsound.Beep(1200, 150)

                button.set_active(1.0)

                self.last_time = current_time
                self.state = self.IDLE

        return img