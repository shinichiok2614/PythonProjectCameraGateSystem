from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from camera.camera_thread import CameraThread
from ui.camera_widget import CameraWidget

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera System")
        self.setGeometry(100, 100, 900, 400)

        central = QWidget()
        layout = QHBoxLayout()

        # 2 camera widget
        self.cam1 = CameraWidget()
        self.cam2 = CameraWidget()

        layout.addWidget(self.cam1)
        layout.addWidget(self.cam2)

        central.setLayout(layout)
        self.setCentralWidget(central)

        # threads
        self.thread1 = CameraThread(0)
        self.thread2 = CameraThread(1)

        self.thread1.frame_signal.connect(self.cam1.update_frame)
        self.thread2.frame_signal.connect(self.cam2.update_frame)

        self.thread1.start()
        self.thread2.start()

    def closeEvent(self, event):

        self.thread1.stop()
        self.thread2.stop()

        self.thread1.quit()
        self.thread2.quit()

        self.thread1.wait()
        self.thread2.wait()

        event.accept()