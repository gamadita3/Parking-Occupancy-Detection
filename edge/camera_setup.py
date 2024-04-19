import cv2
import json

class CameraSetup:
    def __init__(self, dataset, camera_index=0):
        self.frameconfig = self.load_config('../util/frame_config.json')
        self.dirconfig = self.load_config('../util/dir_config.json')
        if dataset:
            print("Source : Dataset")
            self.capture = cv2.VideoCapture(self.dirconfig["VIDEO"])
        else:
            print("Source : Camera")
            self.capture = cv2.VideoCapture(camera_index)
            self.config_camera
        
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    def config_camera(self):
        self.capture.set(3, self.frameconfig["FRAME_WIDTH"])
        self.capture.set(4, self.frameconfig["FRAME_HEIGHT"])
        return self.capture

    def get_frame(self):
        ret, frame = self.capture.read()
        if ret:
            return frame
        else :
            print("Error capturing frame")
                
    def show_images_opencv(self, window, frame):
        frame_show = cv2.resize(frame, (854,480))
        cv2.imshow(window, frame_show)
        cv2.waitKey(1)
