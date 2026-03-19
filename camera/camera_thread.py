import cv2
from PySide6.QtCore import QThread, Signal

class CameraThread(QThread):

    frame_signal = Signal(object)

    def __init__(self, camera_index):
        super().__init__()
        self.camera_index = camera_index
        self.running = True

    def run(self):

        cap = cv2.VideoCapture(self.camera_index)

        while self.running:

            ret, frame = cap.read()

            if ret:
                self.frame_signal.emit(frame)

        cap.release()

    def stop(self):
        self.running = False