import json
import os
import psutil
import time
import cv2
import random
import numpy as np
import paho.mqtt.client as mqtt
import cProfile
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
def show_images_opencv(frame):
    cv2.imshow('Image', frame)
    cv2.waitKey(1)
    
#----------------------------PIL show image-----------------------------------------#   
def show_images_pil(frame):
    pil_image = Image.fromarray(frame)
    pil_image.show()
    time.sleep(3)
    pil_image.close()
    
 #----------------------------OPENCV GET VIDEO-----------------------------------------#   
def get_video():
    video_folder = frameConfig['FOLDER_VIDEOS']
    return cv2.VideoCapture(video_folder)

video = get_video()

#----------------------------INFERENCE-----------------------------------------#
inference = False
label_file = open("./util/label.txt", "r")
class_list = label_file.read().split("\n")
label_file.close()

model = YOLO("./util/parking.pt")
detection_colors = []
for i in range(len(class_list)):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    detection_colors.append((b, g, r))
    

    
def inference(frame):
    print("Start Inference !!")  
    detecting = model(source=frame, imgsz=224)    
    #print(detecting)   
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
        _, thresh = cv2.threshold(frame_diff, 40, 255, cv2.THRESH_BINARY)
        show_images_opencv(thresh)
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

#---------------------calculate processor pi usage------------------#
def calculate_usage_pi(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the process id of the current process
        pid = os.getpid()
        # Create a psutil process object using the pid
        psutil_process = psutil.Process(pid)
        
        # Record the start time and CPU times
        start_time = time.time()
        start_cpu_times = psutil_process.cpu_times()
        
        # Execute the function
        result = func(*args, **kwargs)
        
        # Record the end time and CPU times
        end_time = time.time()
        end_cpu_times = psutil_process.cpu_times()
        
        # Calculate the elapsed time and CPU times
        elapsed_time = end_time - start_time
        user_time = end_cpu_times.user - start_cpu_times.user
        system_time = end_cpu_times.system - start_cpu_times.system
        cpu_usage = (user_time + system_time) / elapsed_time * 100
        
        # Calculate power usage assuming a constant rate (this is a placeholder as actual power usage would require hardware support)
        power_usage = cpu_usage * 0.15  # in Watts, assuming 0.15W per percentage of CPU usage
        
        # Estimate process complexity as the number of contours processed
        complexity = len(kwargs.get('contours', []))
        
        print(f"Processor usage: {cpu_usage:.2f}%")
        print(f"Power usage: {power_usage:.2f}W")
        print(f"Process complexity (number of contours processed): {complexity}")
        
        return result
    return wrapper


##############################################################################################################################

def image_run():   
    global motion_detected
    global start_time
    frames = get_images()
    frame_initial = frames[0]
    count = 0
    motion_detected = False
    for frame in frames:     
        try:
            if  motion_detected:
                count += 1   
                print(f"Frame : {count}")
                frame_initial = frame
            else:   
                count += 1
                frame_detect = frames[count]
                motion_detection(frame_initial, frame_detect)
        except Exception as error:
            print("Error:", error)     

def video_run():   
    global motion_detected
    global start_time
    global count
    ret, frame_initial = video.read()
    if not ret:
        print("Failed to read video")
        return
    count = 0
    motion_detected = False
    while True: 
        try:
            if  motion_detected:
                count += 1   
                inferenced_frame = inference(frame_initial) 
                show_images_opencv(frame_initial)
                ret, frame_initial = video.read()
                if (time.time() - start_time) > 10:
                    motion_detected = False
                    #show_images_opencv(frame_initial)
                    print("Reset detection")
                #show_images_opencv(frame_initial)
            else:   
                count += 1
                ret, next_frame = video.read()
                #show_images_opencv(next_frame)
                if not ret:
                    raise Exception("Failed to read next frame.")
                motion_detection(frame_initial, next_frame)
            time.sleep(1/60)  # Limit to 60 fps
        except Exception as error:
            print("Error:", error)
            break

def main():
    #image_run()
    video_run()

if __name__ == '__main__':
    print("START EDGE_V1")
    cProfile.run('video_run()', sort='cumtime')
    

