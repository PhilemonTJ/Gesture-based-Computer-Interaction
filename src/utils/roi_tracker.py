"""
RoiTracker – Region-of-Interest tracker for hand detection.

Maintains a small bounding window around the detected hand so that the
hand-landmark model can be run on a smaller crop instead of the full frame,
improving speed and robustness.
"""


class RoiTracker:
    """
    Tracks a rectangular region of interest around the hand.

    Parameters
    ----------
    margin : int
        Extra pixels to add around the landmark bounding box on each side
        when computing the ROI crop.
    max_lost_frames : int
        Number of consecutive "lost" frames before falling back to full-frame
        detection.
    """

    def __init__(self, margin: int = 80, max_lost_frames: int = 5):
        self.margin = margin
        self.max_lost_frames = max_lost_frames

        # State
        self.roi_active: bool = False
        self.roi_box: tuple[int, int, int, int] = (0, 0, 0, 0)  # x, y, w, h
        self.lost_counter: int = 0

    # ------------------------------------------------------------------
    def get_frame_region(self, full_frame):
        """
        Return the frame region to feed into the hand model.

        Parameters
        ----------
        full_frame : numpy.ndarray
            The full-resolution BGR frame from the camera.

        Returns
        -------
        roi_frame : numpy.ndarray
            Either the cropped ROI or the full frame.
        offset_x : int
            X offset of the crop's top-left corner in full-frame coords.
        offset_y : int
            Y offset of the crop's top-left corner in full-frame coords.
        """
        if not self.roi_active or self.lost_counter >= self.max_lost_frames:
            # Fall back to full-frame detection.
            return full_frame, 0, 0

        frame_h, frame_w = full_frame.shape[:2]
        rx, ry, rw, rh = self.roi_box

        # Expand by margin and clamp to frame bounds.
        x1 = max(0, rx - self.margin)
        y1 = max(0, ry - self.margin)
        x2 = min(frame_w, rx + rw + self.margin)
        y2 = min(frame_h, ry + rh + self.margin)

        # Safety: if the crop is too small, fall back to full frame.
        if (x2 - x1) < 50 or (y2 - y1) < 50:
            return full_frame, 0, 0

        roi_frame = full_frame[y1:y2, x1:x2]
        return roi_frame, x1, y1

    # ------------------------------------------------------------------
    def update_from_landmarks(self, lm_list, frame_w: int, frame_h: int):
        """
        Recompute the ROI box from raw full-frame landmark positions.

        Parameters
        ----------
        lm_list : list[list[int]]
            21 landmarks, each ``[px, py, pz]`` in **full-frame** pixel coords.
        frame_w : int
            Width of the full frame (for clamping).
        frame_h : int
            Height of the full frame (for clamping).
        """
        xs = [lm[0] for lm in lm_list]
        ys = [lm[1] for lm in lm_list]

        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        # Add a small internal padding so the ROI isn't skin-tight.
        pad = 20
        x_min = max(0, x_min - pad)
        y_min = max(0, y_min - pad)
        x_max = min(frame_w, x_max + pad)
        y_max = min(frame_h, y_max + pad)

        self.roi_box = (x_min, y_min, x_max - x_min, y_max - y_min)
        self.roi_active = True
        self.lost_counter = 0

    # ------------------------------------------------------------------
    def mark_lost(self):
        """
        Call once per frame when no hand is detected.

        After ``max_lost_frames`` consecutive calls the tracker reverts to
        full-frame detection on the next ``get_frame_region`` call.
        """
        self.lost_counter += 1
        if self.lost_counter >= self.max_lost_frames:
            self.roi_active = False

    # ------------------------------------------------------------------
    def draw_roi(self, img, color=(0, 255, 0), thickness=2):
        """
        Draw the current ROI rectangle on the image (debug overlay).

        Parameters
        ----------
        img : numpy.ndarray
            Image to draw on (modified in-place).
        color : tuple
            BGR color for the rectangle.
        thickness : int
            Line thickness.
        """
        if not self.roi_active:
            return

        import cv2
        rx, ry, rw, rh = self.roi_box
        cv2.rectangle(img, (rx, ry), (rx + rw, ry + rh), color, thickness)
