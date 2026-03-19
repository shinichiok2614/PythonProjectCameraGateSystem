from ultralytics import YOLO
import cv2

class PlateDetector:

    def __init__(self):
        self.model = YOLO("license_plate_detector.pt")

    def detect(self, frame):

        results = self.model(frame)

        boxes = results[0].boxes

        if boxes is None:
            return []

        return boxes.xyxy.cpu().numpy()

    def draw(self, frame):

        boxes = self.detect(frame)

        for box in boxes:

            x1, y1, x2, y2 = map(int, box[:4])

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                2
            )

        return frame