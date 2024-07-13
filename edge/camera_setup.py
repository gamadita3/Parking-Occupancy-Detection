import cv2
import json

class CameraSetup:
    def __init__(self, dataset, camera_index=0):
        self.sourceConfig = self.load_config('../util/source_config.json')
        if dataset:
            print("Source : Dataset")
            self.capture = cv2.VideoCapture(self.sourceConfig["DATASET"])
            print (self.capture)
        else:            
            self.capture = cv2.VideoCapture(camera_index, cv2.CAP_V4L)     #USB Camera
            self.config_camera()
        
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    def config_camera(self):
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.sourceConfig["FRAME_WIDTH"])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.sourceConfig["FRAME_HEIGHT"])

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
        previous_height, previous_width = frame.shape[:2]    
        resized_frame = cv2.resize(frame, (854,480), interpolation=cv2.INTER_AREA)   
        latest_height, latest_width = resized_frame.shape[:2]  
        print(f"Resized frame from res {previous_width}x{previous_height} to {latest_width}x{latest_height}")
        print(f"Byte size of resized from {frame.nbytes / 10000} kilobytes to {resized_frame.nbytes / 1000} kilobytes")
        print(f"Reduced by {(frame.nbytes - resized_frame.nbytes) / 1000} kilobytes")
        return resized_frame
