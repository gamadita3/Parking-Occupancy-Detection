import json
import traceback
import threading
import time
import csv
import psutil
import datetime
import numpy as np
from mqtt_setup import MQTTSetup
from camera_setup import CameraSetup
from motion_detection import MotionDetection
from object_detection import Inference
from system_monitor import SystemMonitor
dirConfig = json.load(open(file="../util/dir_config.json", encoding="utf-8"))

########################################################################################################


#############################################################################################################################  

def main():
    motion_detected = False 
    dataset = True
    camera = CameraSetup(dataset)
    inference = Inference()
    motiondetection = MotionDetection()
    systemmonitor = SystemMonitor(True)
    
    print("Edge start parking detection !")
    
    initial_frame = camera.get_frame
    #system_monitor_thread = threading.Thread(target=systemmonitor.start_monitoring)
    #system_monitor_thread.start()
    
    '''
    with open(dirConfig["CSV_FPS"], mode='w', newline='') as file:
        write_fps = csv.writer(file)
        write_fps.writerow(['FPS'])
        with open(dirConfig["CSV_STATUS"], mode='w', newline='') as file:
            write_status = csv.writer(file)
            write_status.writerow(['time','empty','occupied','total_detection'])
            while True: 
                loop_start_time = time.time()  # Record st art time of the loop
                try:                            
                    if motion_detected:
                        inferenced_frame = inference.detect(initial_frame)
                        #mqtt_client.publish_frame(inferenced_frame)
                        camera.show_images_opencv("INFERENCE", inferenced_frame)
                        motion_detected = False
                        initial_frame = camera.get_frame                 
                    else:   
                        next_frame = camera.get_frame
                        motiondetection.detect_motion(initial_frame, next_frame)
                        initial_frame = next_frame
                        #show_images_opencv("RAW",initial_frame)
                        
                    loop_end_time = time.time()
                    total_loop_time = loop_end_time - loop_start_time 
                    FPS = 1/(total_loop_time)
                    write_fps.writerow([FPS])
                    print("FPS per loop : ", FPS)
                            
                except Exception as error:
                    print("Error:", error)
                    break
    '''
    
    while True: 
                loop_start_time = time.time()  # Record st art time of the loop
                try:                            
                    if motion_detected:
                        inferenced_frame = inference.detect(initial_frame)
                        #mqtt_client.publish_frame(inferenced_frame)
                        camera.show_images_opencv("INFERENCE", inferenced_frame)
                        motion_detected = False
                        initial_frame = camera.get_frame                 
                    else:   
                        next_frame = camera.get_frame
                        camera.show_images_opencv("RAW",initial_frame)
                        motiondetection.detect_motion(initial_frame, next_frame)
                        initial_frame = next_frame
                        camera.show_images_opencv("RAW",initial_frame)
                        
                    loop_end_time = time.time()
                    total_loop_time = loop_end_time - loop_start_time 
                    FPS = 1/(total_loop_time)
                    #write_fps.writerow([FPS])
                    print("FPS per loop : ", FPS)
                            
                except Exception :
                    print("Error:", print(traceback.format_exc()))
                    break

if __name__ == '__main__':
    mqtt_client = MQTTSetup()
    mqtt_client.connect()
    main()
    

