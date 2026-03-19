import easyocr

class OCRReader:

    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    def read(self, image):

        results = self.reader.readtext(image)

        if not results:
            return "Không đọc được"

        text = ""

        for r in results:
            text += r[1] + " "

        return text.strip()