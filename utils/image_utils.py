import cv2
import base64

def encode_image(img):

    _, buffer = cv2.imencode(".jpg", img)

    return base64.b64encode(buffer).decode()