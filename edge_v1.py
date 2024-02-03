import json
import os
import psutil
import time
import cv2
import random
import numpy as np
import paho.mqtt.client as mqtt
import cProfile
import onnxruntime as ort
from PIL import Image
from ultralytics import YOLO
from functools import wraps
mqttConfig = json.load(open(file="./util/mqtt_config.json", encoding="utf-8"))
frameConfig = json.load(open(file="./util/frame_config.json", encoding="utf-8"))

#----------------------------PIL GET IMAGES-----------------------------------------#

def get_images():
    image_folder = frameConfig['FOLDER_IMAGES']
    frames = [np.array(Image.open(os.path.join(image_folder, img))) for img in os.listdir(image_folder) if img.endswith(".jpg")]
    return frames

#----------------------------CV2 show image-----------------------------------------#   
def show_images_opencv(window, frame):
    cv2.imshow(window, frame)
    cv2.waitKey(1)
    
 #----------------------------OPENCV GET VIDEO-----------------------------------------#   
def get_video():
    video_folder = frameConfig['FOLDER_VIDEOS']
    return cv2.VideoCapture(video_folder)

video = get_video()
#----------------------------COLLECT FRAMES-----------------------------------------# 
def collect_frames():       
    print(f'Start capture images for {frameConfig["TOTAL_CAPTURE_FRAME"]} frames')
    frames = []
    for _ in range(frameConfig["TOTAL_CAPTURE_FRAME"]):
        ret, frame = video.read()
        if not ret:
            raise Exception("Could not read from camera.")
        frames.append(frame)
        time.sleep(frameConfig["CAPTURE_DELAY"])
    print(f'Total frames: {len(frames)}')
    return frames


#----------------------------INFERENCE ULTRALYTICS-----------------------------------------#
inference = False
label_file = open("./util/label.txt", "r")
class_list = label_file.read().split("\n")
label_file.close()

model = YOLO("./util/parkiritbv2-d.onnx")
detection_colors = []
for i in range(len(class_list)):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    detection_colors.append((b, g, r))
    
def inference(frame):
    print("Start Inference !!")  
    detecting = model(source=frame, imgsz=frameConfig["IMGSZ"], show=True)        
    print(detecting)     
    '''
    DP = detecting[0].numpy() 
    if len(DP) != 0:
        box = detecting[0].boxes[0]  # returns the first box
        clsID = box.cls.numpy()[0]
        conf = box.conf.numpy()[0]
        bb = box.xyxy.numpy()[0]

        # Ensure frame is a numpy array before drawing rectangle
        if isinstance(frame, np.ndarray):
            cv2.rectangle(
                frame,
                (int(bb[0]), int(bb[1])),
                (int(bb[2]), int(bb[3])),
                detection_colors[int(clsID)],
                3,
            )

            # Display class name and confidence
            font = cv2.FONT_HERSHEY_COMPLEX
            cv2.putText(
                frame,
                class_list[int(clsID)] + " " + str(round(conf, 3)) + "%",
                (int(bb[0]), int(bb[1]) - 10),
                font,
                1,
                (255, 255, 255),
                2,
            )
        else:
            raise TypeError("The frame provided to inference is not a valid numpy array.")
    return frame
    ''' 
   
#----------------------------MOTION DETECTION-----------------------------------------#
motion_detected = False
start_time = time.time()

def motion_detection(old_frame, new_frame):
        global motion_detected
        global start_time
        global count
        old_frame_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        new_frame_gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
        frame_diff = cv2.absdiff(old_frame_gray, new_frame_gray)        
        _, thresh = cv2.threshold(frame_diff, frameConfig['THRESHOLD_MD'], 255, cv2.THRESH_BINARY)
        show_images_opencv("thresh", thresh)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
        for contour in contours:           
            if cv2.contourArea(contour) > 100: #threshold sensitivity set 100
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(new_frame, (x, y), (x + w, y + h), (10, 10, 255), 2)
                #show_images_opencv(new_frame)
                motion_detected = True
                start_time = time.time()      
        if motion_detected:
            print("Motion Detected : ", count)


##############################################################################################################################   

def video_run():   
    global motion_detected
    global start_time
    global count
    ret, initial_frame = video.read()
    if not ret:
        print("Failed to read video")
        return
    count = 0
    motion_detected = False
    skip_frame_count = 0  # Initialize skip frame count
    while True: 
        loop_start_time = time.time()  # Record start time of the loop
        try:
            if motion_detected:
                count += 1
                if skip_frame_count > 0:  # Check if there are frames to skip
                    skip_frame_count -= 1  # Decrement skip frame count
                    ret, initial_frame = video.read()  # Read next frame to skip
                    if not ret:
                        raise Exception("Failed to read frame during skip.")
                    continue  # Skip the rest of the loop
                inference_start_time = time.time()  # Record start time of inference
                inference(initial_frame)
                inference_end_time = time.time()  # Record end time of inference
                inference_duration = inference_end_time - inference_start_time  # Calculate duration of inference         
                if (time.time() - start_time) > frameConfig["INFERENCE_DURATION"]:
                    motion_detected = False
                    print("Reset detection")  
                    ret, initial_frame = video.read()   
                skip_frame_count = int(inference_duration * frameConfig["FRAMERATE_TARGET"]) - 1 # Calculate number of frames to skip based on inference duration
            else:   
                count += 1
                ret, next_frame = video.read()
                show_images_opencv("raw", next_frame)
                if not ret:
                    raise Exception("Failed to read next frame.")
                motion_detection(initial_frame, next_frame)
                ret, initial_frame = ret, next_frame
            loop_end_time = time.time()  # Record end time of the loop
            loop_duration = loop_end_time - loop_start_time  # Calculate duration of the loop
            time_to_sleep = max(0, (1 / frameConfig["FRAMERATE_TARGET"]) - loop_duration)  # Calculate time to sleep to maintain target frame rate
            time.sleep(time_to_sleep)  # Sleep to maintain target frame rate
        except Exception as error:
            print("Error:", error)
            break

def main():
    video_run()

if __name__ == '__main__':
    print("START EDGE_V1")
    main()
    

