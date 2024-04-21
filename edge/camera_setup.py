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
            self.capture = cv2.VideoCapture(camera_index, cv2.CAP_V4L)
            self.config_camera()
        
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    def config_camera(self):
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.frameconfig["FRAME_WIDTH"])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frameconfig["FRAME_HEIGHT"])

    def get_frame(self):
        ret, frame = self.capture.read()
        if ret:
            return frame
        else :
            print("Error capturing frame")
                
    def show_images_opencv(self, window, frame):
        #frame_show = cv2.resize(frame, (854,480))
        cv2.imshow(window, frame)
        cv2.waitKey(1)
    
    def compress_resize(self, frame):
        height, width = frame.shape[:2]
        print(f"Previous frame with resolution: {width}x{height}")
        print("Byte size of previous frame:", frame.nbytes, "bytes")    
        resized_frame = cv2.resize(frame, (854,480), interpolation=cv2.INTER_AREA)   
        height, width = resized_frame.shape[:2]  
        print(f"Resized frame with resolution: {width}x{height}")
        print("Byte size of resized frame:", resized_frame.nbytes, "bytes")
        return resized_frame