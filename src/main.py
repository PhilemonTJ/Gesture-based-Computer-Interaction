import cv2
import numpy as np
import pyautogui

from utils.hand_detector import HandDetector
from utils.button import TextButton
from utils.volume_manager import VolumeManager

from core.config import Config
from core.camera_manager import CameraManager

from controllers.mouse_movement_controller import MovementController
from controllers.mouse_click_controller import ClickController
from controllers.scroll_controller import ScrollController
from controllers.drag_drop_controller import DragController
from controllers.volume_controller import VolumeController
from controllers.screenshot_controller import ScreenshotController


def main():

    # ================= INITIALIZATION ================= #

    config = Config()

    detector = HandDetector(detectionCon=0.9, maxHands=1)
    camera = CameraManager(config)

    screen_width, screen_height = pyautogui.size()

    rect_x1, rect_y1 = 120, 20
    rect_x2 = config.CAM_WIDTH - rect_x1
    rect_y2 = config.RECT_HEIGHT + rect_y1

    rect_bounds = (rect_x1, rect_y1, rect_x2, rect_y2)

    volume_manager = VolumeManager(step=10)

    # ================= CONTROLLERS ================= #

    movement = MovementController(config, rect_bounds, (screen_width, screen_height))
    click = ClickController()
    scroll = ScrollController()
    drag = DragController()
    volume = VolumeController(config, volume_manager)
    screenshot = ScreenshotController(config)

    # ================= BUTTONS ================= #

    button_start_y = config.CAM_HEIGHT - config.FRAME_REDUCTION + 5
    button_gap_y = 35

    buttons = [
        TextButton("Mouse Moving", 10, button_start_y),
        TextButton("Mouse Lock", 200, button_start_y),
        TextButton("Left Click", 10, button_start_y + button_gap_y),
        TextButton("Right Click", 200, button_start_y + button_gap_y),
        TextButton("Double Click", 390, button_start_y + button_gap_y),
        TextButton("Scroll Up", 10, button_start_y + 2 * button_gap_y),
        TextButton("Scroll Down", 200, button_start_y + 2 * button_gap_y),
        TextButton("Screenshot", 10, button_start_y + 3 * button_gap_y),
        TextButton("Drag & Drop", 200, button_start_y + 3 * button_gap_y),
        TextButton("Volume Up", 10, button_start_y + 4 * button_gap_y),
        TextButton("Volume Down", 200, button_start_y + 4 * button_gap_y),
    ]

    def reset_buttons():
        for button in buttons:
            if button.active_until == 0:
                button.is_active = False

    # ================= MAIN LOOP ================= #

    try:
        while True:

            success, img = camera.read()
            if not success:
                print("Failed to grab frame")
                break

            img = cv2.flip(img, 1)
            hands, img = detector.findHands(img, flipType=False)

            reset_buttons()

            # Draw interaction rectangle
            cv2.rectangle(img, (rect_x1, rect_y1),
                          (rect_x2, rect_y2),
                          (255, 0, 0), 2)

            if hands:

                lmlist = hands[0]["lmList"]
                fingers = detector.fingersUp(hands[0])

                thumb_tip = (lmlist[4][0], lmlist[4][1])
                index_tip = (lmlist[8][0], lmlist[8][1])
                middle_tip = (lmlist[12][0], lmlist[12][1])


                cv2.circle(img, index_tip, 10, (0, 255, 0), cv2.FILLED)

                # ================= SCREENSHOT ================= #
                img = screenshot.update(fingers, img, buttons[7])

                # ================= VOLUME ================= #
                middle_mcp = (lmlist[9][0], lmlist[9][1])
                angle = detector.finger_angle(middle_tip, middle_mcp)

                volume.update(fingers, angle, buttons)

                # ================= DRAG ================= #
                drag_length, _, _ = detector.findDistance(
                    thumb_tip, index_tip, img)

                dragging = drag.update(drag_length, buttons[8])

                # ================= MOVEMENT ================= #
                # Distance between index & middle
                move_length, _, _ = detector.findDistance(
                    index_tip, middle_tip)

                movement.update(
                    fingers,
                    index_tip,
                    middle_tip,
                    move_length,
                    buttons[0],   # Mouse Moving
                    buttons[1]    # Mouse Lock
                )

                # ================= CLICK ================= #
                click_length, _, _ = detector.findDistance(
                    index_tip, middle_tip, img)

                click.update(lmlist, buttons)

                # ================= SCROLL ================= #
                scroll.update(fingers, index_tip, buttons)

            # ================= DRAW BUTTONS ================= #
            for button in buttons:
                button.draw(img)

            cv2.imshow("GCI - Camera Feed", img)

            key = cv2.waitKey(1)
            if key & 0xFF in [27, ord('q')]:
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()