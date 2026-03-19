https://github.com/opencv/opencv/tree/master/data/haarcascades

pip freeze > requirements.txt

pip install -r requirements.txt

Workflow làm việc trong PyCharm

Mỗi bước bạn muốn làm có thể tạo branch hoặc module riêng.

Ví dụ tiến trình:

Step 1

camera/

    camera_manager.py

test mở 2 camera.

Step 2
    
    capture_service.py

test chụp ảnh.

Step 3

ai/

    plate_detector.py
    
    test YOLO.

Step 4

    ocr_reader.py

test EasyOCR.

Step 5
    
    api_service.py

test gửi JHipster.

PySide6