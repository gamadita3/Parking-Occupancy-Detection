import cv2
from picamera2 import Picamera2

# Grab images as numpy arrays and leave everything else to OpenCV.
cv2.startWindowThread()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (1920, 1080)}))
picam2.start()

while True:
    source_frame = picam2.capture_array()
    convert_frame = cv2.cvtColor(source_frame, cv2.COLOR_BGR2RGB)

    cv2.imshow("Camera", convert_frame)
    cv2.waitKey(1)