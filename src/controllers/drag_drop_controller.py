# controllers/drag_drop_controller.py

import mouse

class DragController:
    def __init__(self):
        self.dragging = False

    def update(self, drag_length, button):

        if drag_length < 40:
            if not self.dragging:
                mouse.press(button='left')
                self.dragging = True
            button.is_active = True
        else:
            if self.dragging:
                mouse.release(button='left')
                self.dragging = False
            button.is_active = False

        return self.dragging