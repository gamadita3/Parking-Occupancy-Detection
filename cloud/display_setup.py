import cv2

class DisplaySetup:
    def __init__(self):
        pass        

    def show_images_opencv(self, window, frame):
        frame_show = cv2.resize(frame, (854,480))
        cv2.imshow(window, frame_show)
        cv2.waitKey(1)
