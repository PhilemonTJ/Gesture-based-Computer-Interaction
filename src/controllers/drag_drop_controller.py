# controllers/drag_drop_controller.py

import mouse

class DragController:
    def __init__(self, config):
        self.dragging = False
        self.press_threshold = config.DRAG_PRESS_THRESHOLD
        self.release_threshold = config.DRAG_RELEASE_THRESHOLD

    def update(self, drag_length, button):

        if not self.dragging and drag_length < self.press_threshold:
            mouse.press(button='left')
            self.dragging = True

        elif self.dragging and drag_length > self.release_threshold:
            mouse.release(button='left')
            self.dragging = False

        button.is_active = self.dragging
        return self.dragging

    def safe_release(self, button):
        """Release the left mouse button if currently dragging.
        Called when switching to a non-drag gesture mode."""
        if self.dragging:
            mouse.release(button='left')
            self.dragging = False
        button.is_active = False