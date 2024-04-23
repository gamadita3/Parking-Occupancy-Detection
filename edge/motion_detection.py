import cv2
import copy
import os
import time
import json

class MotionDetection:
    def __init__(self):
        self.frameconfig = self.load_config('../util/frame_config.json')
        self.dirconfig = self.load_config('../util/dir_config.json')
        self.motion_detected = False
        self.md_count = 0
        
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    def detect_motion(self, old_frame, new_frame):
        contour_frame = copy.copy(new_frame)
        old_frame_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        new_frame_gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
        frame_diff = cv2.absdiff(old_frame_gray, new_frame_gray)
        _, thresh = cv2.threshold(frame_diff, self.frameconfig["THRESHOLD_MD"], 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > self.frameconfig["CONTOUR_SENSITIVITY"]:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(contour_frame, (x, y), (x + w, y + h), (10, 10, 255), 2)
                
                self.motion_detected = True
                self.md_count += 1
                #print("Motion detected")
                
                image_filename_md = f"md_{self.md_count}.jpg"
                save_path_md = os.path.join(self.dirconfig["MOTIONDETECTION"], image_filename_md)
                cv2.imwrite(save_path_md, contour_frame)
                
                return self.motion_detected

    def reset(self):
        self.motion_detected = False