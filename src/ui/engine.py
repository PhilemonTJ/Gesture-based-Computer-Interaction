# ui/engine.py — Bridge between UI and gesture backend

import threading
import time
import cv2
import numpy as np
from PIL import Image

from core.config import Config
from core.camera_manager import CameraManager
from utils.hand_detector import HandDetector
from utils.roi_tracker import RoiTracker

from controllers.mouse_movement_controller import MovementController
from controllers.mouse_click_controller import ClickController
from controllers.scroll_controller import ScrollController
from controllers.drag_drop_controller import DragController
from controllers.volume_controller import VolumeController
from controllers.screenshot_controller import ScreenshotController
from utils.volume_manager import VolumeManager

import pyautogui


class GestureEngine:
    """Runs the gesture recognition loop in a background thread.
    
    Exposes a shared `state` dict that the UI polls for live updates.
    """

    def __init__(self, config: Config):
        self.config = config
        self._thread = None
        self._running = False
        self._paused = False

        # Shared state — UI reads this via after() polling
        self.state = {
            "status": "INACTIVE",     # INACTIVE | ACTIVE | PAUSED
            "fps": 0,
            "hand_detected": False,
            "gesture": "None",
            "frame": None,            # PIL Image for camera preview
            "fingers": [0, 0, 0, 0, 0],
        }

        # Gesture toggles (UI can turn individual gestures on/off)
        self.toggles = {
            "cursor": True,
            "left_click": True,
            "right_click": True,
            "drag": True,
            "scroll": True,
            "volume": True,
            "screenshot": True,
        }

    def start(self):
        """Start the gesture loop in a background thread."""
        if self._running:
            return
        self._running = True
        self._paused = False
        self.state["status"] = "CONNECTING"
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def pause(self):
        """Pause gesture processing (camera stays on)."""
        self._paused = True
        self.state["status"] = "PAUSED"

    def resume(self):
        """Resume gesture processing."""
        self._paused = False
        self.state["status"] = "ACTIVE"

    def stop(self):
        """Stop the gesture loop and release camera."""
        self._running = False
        self.state["status"] = "INACTIVE"
        self.state["frame"] = None
        self.state["hand_detected"] = False
        self.state["gesture"] = "None"
        self.state["fps"] = 0

    def _loop(self):
        """Main gesture recognition loop (runs in background thread)."""
        config = self.config

        # Show CONNECTING while MediaPipe and camera load
        self.state["status"] = "CONNECTING"

        detector = HandDetector(detectionCon=0.9, maxHands=1)
        camera = CameraManager(config)

        # Now connected — switch to ACTIVE
        self.state["status"] = "ACTIVE"

        screen_width, screen_height = pyautogui.size()

        rect_x1, rect_y1 = 120, 20
        rect_x2 = config.CAM_WIDTH - rect_x1
        rect_y2 = config.RECT_HEIGHT + rect_y1
        rect_bounds = (rect_x1, rect_y1, rect_x2, rect_y2)

        volume_manager = VolumeManager(step=10)

        movement = MovementController(config, rect_bounds, (screen_width, screen_height))
        click = ClickController(config)
        scroll = ScrollController(config)
        drag = DragController(config)
        volume = VolumeController(config, volume_manager)
        screenshot = ScreenshotController(config)
        roi = RoiTracker(margin=config.ROI_MARGIN, max_lost_frames=config.ROI_MAX_LOST)

        active_mode = "idle"
        prev_time = 0

        try:
            while self._running:
                success, img = camera.read()
                if not success:
                    break

                img = cv2.flip(img, 1)

                # FPS calculation
                curr_time = time.time()
                self.state["fps"] = int(1 / (curr_time - prev_time)) if prev_time else 0
                prev_time = curr_time

                # ROI crop
                roi_frame, offset_x, offset_y = roi.get_frame_region(img)
                hands, _ = detector.findHands(roi_frame, flipType=False)

                if hands:
                    # Offset landmarks
                    lmlist = hands[0]["lmList"]
                    if offset_x != 0 or offset_y != 0:
                        lmlist = [[lm[0] + offset_x, lm[1] + offset_y] + lm[2:]
                                  for lm in lmlist]
                        hands[0]["lmList"] = lmlist

                    frame_h, frame_w = img.shape[:2]
                    roi.update_from_landmarks(lmlist, frame_w, frame_h)

                    fingers = detector.fingersUp(hands[0])
                    self.state["fingers"] = fingers
                    self.state["hand_detected"] = True

                    thumb_tip = (lmlist[4][0], lmlist[4][1])
                    index_tip = (lmlist[8][0], lmlist[8][1])
                    middle_tip = (lmlist[12][0], lmlist[12][1])

                    # Draw landmarks on full frame
                    cv2.circle(img, index_tip, 10, (0, 255, 0), cv2.FILLED)

                    # Draw interaction rectangle
                    cv2.rectangle(img, (rect_x1, rect_y1),
                                  (rect_x2, rect_y2), (255, 0, 0), 2)

                    if not self._paused:
                        # ===== SCREENSHOT =====
                        if self.toggles["screenshot"]:
                            img = screenshot.update(fingers, img, _DummyButton())

                        # ===== VOLUME / SCROLL (guarded by screenshot) =====
                        if screenshot.state == screenshot.IDLE:
                            if self.toggles["volume"]:
                                middle_mcp = (lmlist[9][0], lmlist[9][1])
                                angle = detector.finger_angle(middle_tip, middle_mcp)
                                volume.update(fingers, angle, [_DummyButton()] * 11)

                            if self.toggles["scroll"]:
                                scroll_dist, _, _ = detector.findDistance(index_tip, middle_tip)
                                scroll.update(fingers, index_tip, [_DummyButton()] * 11,
                                              finger_distance=scroll_dist)

                        # ===== GESTURE MODE (sticky) =====
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
                            pass  # sticky move
                        elif (fingers[1] == 1 and fingers[2] == 0
                              and fingers[3] == 0 and fingers[4] == 0):
                            active_mode = "drag"
                        else:
                            active_mode = "idle"

                        # ===== DISPATCH =====
                        if active_mode == "move" and self.toggles["cursor"]:
                            move_length, _, _ = detector.findDistance(index_tip, middle_tip)
                            movement.update(fingers, index_tip, middle_tip,
                                            move_length, _DummyButton(), _DummyButton())

                            if move_length >= movement.join_threshold:
                                if self.toggles["left_click"]:
                                    click.update(lmlist, [_DummyButton()] * 11)
                                else:
                                    click.sync_state(lmlist)
                            else:
                                click.sync_state(lmlist)
                            drag.safe_release(_DummyButton())

                        elif active_mode == "drag" and self.toggles["drag"]:
                            drag_length, _, _ = detector.findDistance(
                                thumb_tip, index_tip, img)
                            drag.update(drag_length, _DummyButton())
                            if drag.dragging:
                                movement.move_cursor_to(index_tip)
                        else:
                            drag.safe_release(_DummyButton())

                    # Update gesture name for UI
                    self.state["gesture"] = _mode_display_name(active_mode)

                else:
                    # Hand lost
                    drag.safe_release(_DummyButton())
                    active_mode = "idle"
                    roi.mark_lost()
                    self.state["hand_detected"] = False
                    self.state["gesture"] = "None"

                # Draw ROI debug
                roi.draw_roi(img)

                # Convert frame for UI display
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img_rgb)
                self.state["frame"] = pil_img

        finally:
            camera.release()
            self._running = False
            self.state["status"] = "INACTIVE"


class _DummyButton:
    """Minimal stand-in for TextButton when running without CV2 overlay."""
    is_active = False
    active_until = 0

    def set_active(self, duration=0.5):
        pass

    def draw(self, img):
        pass


def _mode_display_name(mode: str) -> str:
    names = {
        "idle": "None",
        "move": "Move Mouse",
        "drag": "Drag & Drop",
        "scroll": "Scroll",
        "volume": "Volume Control",
    }
    return names.get(mode, mode.title())
