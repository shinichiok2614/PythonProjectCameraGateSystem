import cv2
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QImage, QPixmap

class CameraWidget(QLabel):

    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 300)

    def update_frame(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb.shape

        qt_img = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        self.setPixmap(QPixmap.fromImage(qt_img))