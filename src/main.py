import cv2
import numpy as np
import pyautogui
import time

from utils.hand_detector import HandDetector
from utils.button import TextButton
from utils.volume_manager import VolumeManager
from utils.roi_tracker import RoiTracker

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
    click = ClickController(config)
    scroll = ScrollController(config)
    drag = DragController(config)
    volume = VolumeController(config, volume_manager)
    screenshot = ScreenshotController(config)
    roi = RoiTracker(margin=config.ROI_MARGIN, max_lost_frames=config.ROI_MAX_LOST)

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

    active_mode = "idle"  # sticky gesture mode tracker
    prev_time = 0           # for FPS counter

    try:
        while True:

            success, img = camera.read()
            if not success:
                print("Failed to grab frame")
                break

            img = cv2.flip(img, 1)

            # ── ROI: crop to hand region for faster detection ──
            roi_frame, offset_x, offset_y = roi.get_frame_region(img)
            hands, _ = detector.findHands(roi_frame, flipType=False)

            reset_buttons()

            # Draw interaction rectangle
            cv2.rectangle(img, (rect_x1, rect_y1),
                          (rect_x2, rect_y2),
                          (255, 0, 0), 2)

            if hands:

                # Offset landmarks from crop coords → full-frame coords
                lmlist = hands[0]["lmList"]
                if offset_x != 0 or offset_y != 0:
                    lmlist = [[lm[0] + offset_x, lm[1] + offset_y] + lm[2:]
                              for lm in lmlist]
                    hands[0]["lmList"] = lmlist

                # Update ROI for next frame
                frame_h, frame_w = img.shape[:2]
                roi.update_from_landmarks(lmlist, frame_w, frame_h)

                fingers = detector.fingersUp(hands[0])

                thumb_tip = (lmlist[4][0], lmlist[4][1])
                index_tip = (lmlist[8][0], lmlist[8][1])
                middle_tip = (lmlist[12][0], lmlist[12][1])


                cv2.circle(img, index_tip, 10, (0, 255, 0), cv2.FILLED)

                # ===== SCREENSHOT (always — multi-frame state machine) ===== #
                img = screenshot.update(fingers, img, buttons[7])

                # Skip volume/scroll when screenshot sequence is active
                # (prevents accidental volume change during open-palm step)
                if screenshot.state == screenshot.IDLE:
                    # ===== VOLUME (only acts on [1,1,1,1,1]) ===== #
                    middle_mcp = (lmlist[9][0], lmlist[9][1])
                    angle = detector.finger_angle(middle_tip, middle_mcp)
                    volume.update(fingers, angle, buttons)

                    # ===== SCROLL (only acts on [1,1,1,0,0]) ===== #
                    scroll_dist, _, _ = detector.findDistance(index_tip, middle_tip)
                    scroll.update(fingers, index_tip, buttons, finger_distance=scroll_dist)

                # ===== GESTURE MODE (sticky — survives finger flicker) ===== #

                # STICKY DRAG: if actively dragging, STAY in drag mode
                # regardless of finger flicker (only DragController decides
                # when to release based on thumb-index distance).
                if drag.dragging:
                    active_mode = "drag"

                elif fingers == [1, 1, 1, 1, 1]:
                    active_mode = "volume"

                elif (fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1
                      and fingers[3] == 0 and fingers[4] == 0):
                    active_mode = "scroll"

                elif (fingers[1] == 1 and fingers[2] == 1
                      and fingers[0] == 0
                      and fingers[3] == 0 and fingers[4] == 0):
                    active_mode = "move"

                elif (active_mode == "move"
                      and fingers[2] == 1
                      and fingers[3] == 0 and fingers[4] == 0):
                    # STICKY MOVE: stay in move while middle is up.
                    # Index may be bending for click — don't leave move mode.
                    pass

                elif (fingers[1] == 1 and fingers[2] == 0
                      and fingers[3] == 0 and fingers[4] == 0):
                    active_mode = "drag"

                else:
                    active_mode = "idle"

                # ===== DISPATCH BASED ON MODE ===== #
                if active_mode == "move":
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

                    # Click only in LOCK mode (fingers spread apart)
                    if move_length >= movement.join_threshold:
                        click.update(lmlist, buttons)
                    else:
                        click.sync_state(lmlist)  # keep edge-trigger in sync
                    drag.safe_release(buttons[8])

                elif active_mode == "drag":
                    drag_length, _, _ = detector.findDistance(
                        thumb_tip, index_tip, img)

                    drag.update(drag_length, buttons[8])

                    if drag.dragging:
                        movement.move_cursor_to(index_tip)

                else:
                    drag.safe_release(buttons[8])

                # Debug overlay: finger state + mode (red text)
                cv2.putText(img, f"Fingers: {fingers}", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.putText(img, f"Mode: {active_mode}", (10, 45),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            else:
                # ── HAND LOST — cleanup ──
                drag.safe_release(buttons[8])
                active_mode = "idle"
                roi.mark_lost()

            # ── Draw ROI debug (green rectangle) ──
            roi.draw_roi(img)
            # ================= FPS COUNTER ================= #
            curr_time = time.time()
            fps = int(1 / (curr_time - prev_time)) if prev_time else 0
            prev_time = curr_time
            cv2.putText(img, f"FPS: {fps}", (img.shape[1] - 120, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

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