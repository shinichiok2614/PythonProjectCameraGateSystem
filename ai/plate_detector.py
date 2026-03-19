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

    def crop_plate(self, frame):

        boxes = self.detect(frame)

        if len(boxes) == 0:
            return None

        x1, y1, x2, y2 = map(int, boxes[0][:4])

        return frame[y1:y2, x1:x2]