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
from ai.ocr_reader import OCRReader

from services.auth_service import AuthService
from services.api_service import ApiService
from utils.image_utils import encode_image

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.face_detector = FaceDetector()
        self.plate_detector = PlateDetector()
        self.ocr_reader = OCRReader()

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

        self.btn_send = QPushButton("Gửi dữ liệu")
        main_layout.addWidget(self.btn_send)

        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)

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

        self.plate_text_label = QLabel("Biển số: ")
        main_layout.addWidget(self.plate_text_label)

        self.captured_face = None
        self.captured_plate = None

        self.face_detect_image = None
        self.plate_detect_image = None

        self.plate_text_value = ""

        self.auth_service = AuthService("http://localhost:8080")
        self.api_service = ApiService(
            "http://localhost:8080/api/nhat-ky-ra-vao-quan-nhans"
        )

        self.token = None

        self.btn_send.clicked.connect(self.send_data)
    # =====================
    # CAPTURE FUNCTIONS
    # =====================
    def capture_cam1(self):

        frame = self.cam1.capture()

        if frame is not None:

            frame_copy = frame.copy()

            # detect mặt
            detected = self.face_detector.draw(frame_copy)

            self.show_image(detected, self.result1)

            # =====================
            # LƯU ẢNH GỐC
            # =====================
            self.captured_face = frame

            # =====================
            # LƯU ẢNH DETECT (CROP MẶT)
            # =====================
            faces = self.face_detector.detect(frame)

            if len(faces) > 0:

                x, y, w, h = faces[0]

                face_crop = frame[y:y + h, x:x + w]

                self.face_detect_image = face_crop

            else:
                self.face_detect_image = None

    def capture_cam2(self):

        frame = self.cam2.capture()

        if frame is not None:

            frame_copy = frame.copy()

            detected = self.plate_detector.draw(frame_copy)

            self.show_image(detected, self.result2)

            # =====================
            # LƯU ẢNH GỐC
            # =====================
            self.captured_plate = frame

            # =====================
            # CROP BIỂN SỐ
            # =====================
            plate_crop = self.plate_detector.crop_plate(frame)

            if plate_crop is not None:

                # ✅ LƯU ẢNH DETECT
                self.plate_detect_image = plate_crop

                # OCR
                text = self.ocr_reader.read(plate_crop)

                self.plate_text_value = text

                self.plate_text_label.setText(f"Biển số: {text}")

            else:
                self.plate_detect_image = None
                self.plate_text_value = ""
                self.plate_text_label.setText("Không thấy biển số")
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

    def send_data(self):

        if self.captured_face is None or self.captured_plate is None:
            self.status_label.setText("Chưa chụp đủ ảnh")
            return

        # =====================
        # LOGIN
        # =====================
        if self.token is None:

            success = self.auth_service.login("admin", "admin")

            if not success:
                self.status_label.setText("Login thất bại")
                return

            self.token = self.auth_service.token

        # =====================
        # ENCODE ẢNH
        # =====================
        face_base64 = encode_image(self.captured_face)
        plate_base64 = encode_image(self.captured_plate)

        face_detect_base64 = ""
        plate_detect_base64 = ""

        if self.face_detect_image is not None:
            face_detect_base64 = encode_image(self.face_detect_image)

        if self.plate_detect_image is not None:
            plate_detect_base64 = encode_image(self.plate_detect_image)

        # =====================
        # DATA
        # =====================
        data = {

            "pictureQuanNhanMat": face_base64,
            "pictureQuanNhanMatContentType": "image/jpeg",

            "pictureQuanNhanBienSo": plate_base64,
            "pictureQuanNhanBienSoContentType": "image/jpeg",

            # ✅ THÊM 2 FIELD NÀY
            "pictureQuanNhanMatDetect": face_detect_base64,
            "pictureQuanNhanMatDetectContentType": "image/jpeg",

            "pictureQuanNhanBienSoDetect": plate_detect_base64,
            "pictureQuanNhanBienSoDetectContentType": "image/jpeg",

            "bienSoQuanNhanXeMayOCR": self.plate_text_value
        }

        # =====================
        # CALL API
        # =====================
        status = self.api_service.send(data, self.token)

        if status == 200 or status == 201:
            self.status_label.setText("Gửi thành công")
        else:
            self.status_label.setText("Lỗi API")