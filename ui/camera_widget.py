import cv2
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

class CameraWidget(QLabel):

    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 300)
        self.current_frame = None  # ✅ lưu frame

    def update_frame(self, frame):

        self.current_frame = frame  # ✅ luôn lưu frame mới nhất

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb.shape

        qt_img = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(qt_img)

        pixmap = pixmap.scaled(
            self.width(),
            self.height(),
            Qt.KeepAspectRatio
        )

        self.setPixmap(pixmap)

    # ✅ hàm lấy ảnh hiện tại
    def capture(self):
        return self.current_frame