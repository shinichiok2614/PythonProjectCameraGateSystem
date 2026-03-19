from PySide6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel
)

from camera.camera_thread import CameraThread
from ui.camera_widget import CameraWidget

import cv2
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

from ai.face_detector import FaceDetector
from ai.plate_detector import PlateDetector


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.face_detector = FaceDetector()
        self.plate_detector = PlateDetector()

        self.setWindowTitle("Camera System")
        self.setGeometry(100, 100, 900, 700)

        central = QWidget()
        main_layout = QVBoxLayout()

        # =====================
        # ROW 1: CAMERA
        # =====================
        cam_layout = QHBoxLayout()

        self.cam1 = CameraWidget()
        self.cam2 = CameraWidget()

        cam_layout.addWidget(self.cam1)
        cam_layout.addWidget(self.cam2)

        # =====================
        # ROW 2: BUTTON
        # =====================
        btn_layout = QHBoxLayout()

        self.btn_cap1 = QPushButton("Chụp Camera 1")
        self.btn_cap2 = QPushButton("Chụp Camera 2")

        btn_layout.addWidget(self.btn_cap1)
        btn_layout.addWidget(self.btn_cap2)

        # =====================
        # ROW 3: RESULT
        # =====================
        result_layout = QHBoxLayout()

        self.result1 = QLabel()
        self.result2 = QLabel()

        self.result1.setFixedSize(400, 300)
        self.result2.setFixedSize(400, 300)

        result_layout.addWidget(self.result1)
        result_layout.addWidget(self.result2)

        # add layout
        main_layout.addLayout(cam_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(result_layout)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # =====================
        # THREAD
        # =====================
        self.thread1 = CameraThread(1)
        self.thread2 = CameraThread(0)

        self.thread1.frame_signal.connect(self.cam1.update_frame)
        self.thread2.frame_signal.connect(self.cam2.update_frame)

        self.thread1.start()
        self.thread2.start()

        # =====================
        # BUTTON EVENT
        # =====================
        self.btn_cap1.clicked.connect(self.capture_cam1)
        self.btn_cap2.clicked.connect(self.capture_cam2)

    # =====================
    # CAPTURE FUNCTIONS
    # =====================
    def capture_cam1(self):

        frame = self.cam1.capture()

        if frame is not None:
            # copy để không làm ảnh gốc
            frame_copy = frame.copy()

            detected = self.face_detector.draw(frame_copy)

            self.show_image(detected, self.result1)

    def capture_cam2(self):

        frame = self.cam2.capture()

        if frame is not None:
            frame_copy = frame.copy()

            detected = self.plate_detector.draw(frame_copy)

            self.show_image(detected, self.result2)

    # =====================
    # SHOW IMAGE
    # =====================
    def show_image(self, frame, label):

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
            label.width(),
            label.height(),
            Qt.KeepAspectRatio
        )

        label.setPixmap(pixmap)

    # =====================
    # CLOSE
    # =====================
    def closeEvent(self, event):

        self.thread1.stop()
        self.thread2.stop()

        self.thread1.quit()
        self.thread2.quit()

        self.thread1.wait()
        self.thread2.wait()

        event.accept()