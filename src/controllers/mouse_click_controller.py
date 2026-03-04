# controllers/mouse_click_controller.py
import mouse
import time

class ClickController:
    def __init__(self, config):
        self.prev_index_bent = False
        self.prev_middle_bent = False

        self.last_index_click_time = 0
        self.double_click_window = config.DOUBLE_CLICK_WINDOW

    def is_index_bent(self, lmList):
        tip_y = lmList[8][1]
        pip_y = lmList[7][1]
        return tip_y > pip_y

    def is_middle_bent(self, lmList):
        tip_y = lmList[12][1]
        pip_y = lmList[11][1]
        return tip_y > pip_y

    def update(self, lmList, buttons):

        index_bent = self.is_index_bent(lmList)
        middle_bent = self.is_middle_bent(lmList)

        current_time = time.time()
        click_type = None

        # ================= LEFT CLICK (Index Bend) =================
        if index_bent and not self.prev_index_bent:

            # Check for double click
            if current_time - self.last_index_click_time < self.double_click_window:
                mouse.double_click(button='left')
                buttons[4].set_active()  # Double Click
                self.last_index_click_time = 0
                click_type = "Double Click"
            else:
                mouse.click(button='left')
                buttons[2].set_active()  # Left Click
                self.last_index_click_time = current_time
                click_type = "Left Click"

        # ================= RIGHT CLICK (Middle Bend) =================
        if middle_bent and not self.prev_middle_bent:
            mouse.click(button='right')
            buttons[3].set_active()
            click_type = "Right Click"

        self.prev_index_bent = index_bent
        self.prev_middle_bent = middle_bent
        
        return click_type

    def sync_state(self, lmList):
        """Update prev_bent without triggering clicks.
        Call this when clicks are disabled (e.g. move mode)
        so the edge-trigger stays in sync."""
        self.prev_index_bent = self.is_index_bent(lmList)
        self.prev_middle_bent = self.is_middle_bent(lmList)