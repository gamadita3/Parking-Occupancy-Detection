import json
import os
import psutil
import time
import cv2
import csv
import psutil
import math
import threading
from datetime import datetime
from ultralytics import YOLO
frameConfig = json.load(open(file="../util/frame_config.json", encoding="utf-8"))
dirConfig = json.load(open(file="../util/dir_config.json", encoding="utf-8"))

#----------------------------write to csv-----------------------------------------#        
def write_detection(timestamp, empty, occupied, detection):
    with open(dirConfig["CSV_DETECTION"], mode='a', newline='') as detectionFile:  # 'a' for append mode
        writer = csv.writer(detectionFile)
        writer.writerow([timestamp, empty, occupied, detection])
        
def write_fps(fps):
    with open(dirConfig["CSV_FPS"], mode='a', newline='') as fpsFile:  # 'a' for append mode
        writer = csv.writer(fpsFile)
        writer.writerow([fps])
        
def write_monitor(timestamp, cpu_usage, ram_usage, ram_used):
    with open(dirConfig["CSV_MONITOR"], mode='a', newline='') as monitorFile:  # 'a' for append mode
        writer = csv.writer(monitorFile)
        writer.writerow([timestamp, cpu_usage, ram_usage, ram_used])

#----------------------------CV2 show image-----------------------------------------#   
def show_images_opencv(window, frame):
    frame_show = cv2.resize(frame, (854,480))
    cv2.imshow(window, frame_show)
    cv2.waitKey(1)
    
 #----------------------------OPENCV GET VIDEO-----------------------------------------#   
def get_video():
    video_folder = dirConfig['VIDEO']
    return cv2.VideoCapture(video_folder)

video = get_video()

#----------------------------INFERENCE ULTRALYTICS-----------------------------------------#
label_file = open(dirConfig["LABEL"], "r")
class_list = label_file.read().split("\n")
label_file.close()

model = YOLO(dirConfig["MODEL"])
detection_colors = []
detection_colors.append((10, 255, 10))
detection_colors.append((10, 10, 255))
    
def inference(frame):
    global total_objectdetection
    global false_positive
    global false_negative
    global total_empty_detection
    global total_occupied_detection
    
    total_empty_detection = 0
    total_occupied_detection = 0
    
    detecting = model(source=frame, task="detect", imgsz=frameConfig["IMGSZ"], conf=frameConfig["CONFIDENCE"])
    total_objectdetection += 1            
    DP = detecting[0].numpy()
    print("total detection :",len(DP))
    for i in range(len(DP)):
        try:
            boxes = detecting[0].boxes
            box = boxes[i]  # returns one box
            clsID = box.cls.numpy()[0]
            conf = box.conf.numpy()[0]
            bb = box.xyxy.numpy()[0]
            
            if clsID == 0:
                total_empty_detection += 1
            else:
                total_occupied_detection +=1
                
            cv2.rectangle(frame, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), detection_colors[int(clsID)], 3)
            cv2.putText(frame, class_list[int(clsID)] + " " + str(round(conf, 3)) + "%", (int(bb[0]), int(bb[1]) - 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2)
        except Exception as error:
            print("Error inference:", error)
            break
    
    if len(DP) > 12:
        print("False Positive occured")
        false_positive += 1
        image_filename = f"fp_{false_positive}_empty{total_empty_detection}_occ{total_occupied_detection}.jpg"
        save_path = os.path.join(dirConfig["FALSEPOSITIVE"], image_filename)
        cv2.imwrite(save_path, frame)
    elif len(DP) < 12:
        print("False Negative occured")
        false_negative += 1
        image_filename = f"fn_{false_negative}_empty{total_empty_detection}_occ{total_occupied_detection}.jpg"
        save_path = os.path.join(dirConfig["FALSENEGATIVE"], image_filename)
        cv2.imwrite(save_path, frame)
    print("Empty : ", total_empty_detection )
    print("Occupied : ", total_occupied_detection )
    statustime = datetime.now()
    write_detection(statustime.strftime("%H:%M:%S %d:%m:%Y"),total_empty_detection,total_occupied_detection,(total_empty_detection+total_occupied_detection))
    return frame

#----------------------------MONITOR CPU RAM USAGE-----------------------------------------#
def capture_cpu_usage():
    global video_run_flag
    print("start capture cpu usage")
    with open(dirConfig["CSV_MONITOR"], mode='w', newline='') as monitorFile:
        monitorWriter = csv.writer(monitorFile)
        monitorWriter.writerow(['Time', 'CPU Usage (%)','RAM Usage (%)','RAM Used'])      
    while video_run_flag:
        cpu_percent = psutil.cpu_percent(interval=0.5)  # Set capture cpu interval to 0.5 second
        virtual_memory = psutil.virtual_memory()
        ram_percent = virtual_memory.percent
        ram_used = virtual_memory.used / (1024 ** 2)
        #print("CPU : ",cpu_percent)
        write_monitor(time.time(), cpu_percent,ram_percent,ram_used)       
    print("CAPTURE CPU RAM STOP")

##############################################################################################################################   

def video_run():  
    global total_objectdetection
    global video_run_flag
    global false_positive
    global false_negative
    global md
    
    md = 0
    total_objectdetection = 0
    false_positive = 0
    false_negative = 0
    skip_frame_count = 0  
    video_run_flag = True 
    
    ret, initial_frame = video.read()
    if not ret:
        print("Failed to read video")
        return
    
    capture_cpu_usage_thread = threading.Thread(target=capture_cpu_usage)
    capture_cpu_usage_thread.start()
    
    while True: 
        masterloop_start_time = time.time()
        try:
            if skip_frame_count > 0:  # Check if there are frames to skip
                skip_frame_count -= 1  # Decrement skip frame count
                ret, initial_frame = video.read()  # Read next frame to skip
                if not ret:
                    raise Exception("Failed to read frame during skip.")
                continue  # Skip the rest of the loop
            
            inferenced_frame = inference(initial_frame)
            show_images_opencv("INFERENCE", inferenced_frame)
            
            masterloop_end_time = time.time()
            masterloop = masterloop_end_time - masterloop_start_time 
            print("total loop duration : ", masterloop)
            FPS = 1/(masterloop)
            write_fps(FPS)
            print("FPS per loop : ", FPS)
                    
            skip_frame_count = math.ceil(masterloop * frameConfig["FRAMERATE_TARGET"]) # Calculate number of frames to skip based on inference duration
            print("total skip frame :", skip_frame_count)
                    
        except Exception as error:
            #print("Error:", error)
            print("Total object detection frame : ", total_objectdetection)
            break
    video_run_flag = False

def main():        
    video_run()
    
if __name__ == '__main__':
    
    with open(dirConfig["CSV_DETECTION"], mode='w', newline='') as detectionFile:
        detectionWriter = csv.writer(detectionFile)
        detectionWriter.writerow(['time','empty','occupied','total_detection'])
    with open(dirConfig["CSV_FPS"], mode='w', newline='') as fpsFile:
        fpsWriter = csv.writer(fpsFile)
        fpsWriter.writerow(['FPS'])
    start_time = time.time()  
    print("START PARKING DETECTION")
    main()
    end_time = time.time()
    print("TOTAL TIME : ",(end_time-start_time))
    


