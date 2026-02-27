# controllers/scroll_controller.py

import mouse

class ScrollController:

    def update(self, fingers, length, buttons):

        if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0:

            if length < 30:

                if fingers[4] == 1:
                    buttons[5].set_active()
                    mouse.wheel(delta=1)
                else:
                    buttons[6].set_active()
                    mouse.wheel(delta=-1)