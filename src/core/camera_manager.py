# core/camera_manager.py

import cv2

class CameraManager:
    def __init__(self, config):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.CAM_FPS)

    def read(self):
        return self.cap.read()

    def release(self):
        self.cap.release()