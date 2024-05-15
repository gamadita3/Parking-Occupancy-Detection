import json
import traceback
import threading
import time
import csv
import datetime
import argparse
import numpy as np
from mqtt_setup_edge import MQTTSetup
from http_client import httpSetup
from camera_setup import CameraSetup
from motion_detection import MotionDetection
from object_detection import Inference
from system_monitor import SystemMonitor
dirConfig = json.load(open(file="../util/dir_config.json", encoding="utf-8"))

###############################-EDGE-###############################################

def parse_args():
    parser = argparse.ArgumentParser(description='Run edge device with optional parameters')
    parser.add_argument('--inference', action='store_true', help='Enable inference code')
    parser.add_argument('--http', action='store_true', help='Using HTTP protocol')
    return parser.parse_args()

def send_protocol(frame, total_detection=None):
    if http_protocol :
        http_setup.send_frame(frame)
    else : #default MQTT
        #mqtt_client.publish_detection(total_detection)
        mqtt_client.publish_frame(frame) 

def main():
    motion_detected = False 
    dataset = True
    camera = CameraSetup(dataset)
    inference = Inference()
    motiondetection = MotionDetection()
    systemmonitor = SystemMonitor(True)
    
    print("Edge start parking detection !")
    
    initial_frame = camera.get_frame()
    #system_monitor_thread = threading.Thread(target=systemmonitor.start_monitoring)
    #system_monitor_thread.start()
    
    while True: 
        loop_start_time = time.time()  # Record start time of the loop
        try:                            
            if motion_detected:
                print("\nMotion Detected !")
                print("---resize frame---")
                initial_frame = camera.compress_resize(initial_frame)
                if inference_enabled:
                    print("\n---Inference---")
                    inferenced_frame, total_detection = inference.detect(initial_frame)
                    
                    print("\n---Publishing---")
                    send_protocol(inferenced_frame)
                    #camera.show_images_opencv("EDGE_INFERENCE", inferenced_frame)
                else:
                    send_protocol(initial_frame)
                    #camera.show_images_opencv("EDGE_RAW", initial_frame)
                
                motion_detected = False
                initial_frame = camera.get_frame()
                print("##################################################")              
            else:   
                next_frame = camera.get_frame()           
                motion_detected = motiondetection.detect_motion(initial_frame, next_frame)
                initial_frame = next_frame
                #camera.show_images_opencv("RAW",initial_frame)
                
            loop_end_time = time.time()
            total_loop_time = loop_end_time - loop_start_time 
            FPS = float('inf') if total_loop_time == 0 else 1 / total_loop_time
            #print("FPS per loop : ", FPS)               
                    
        except Exception :
            print("Error:", print(traceback.format_exc()))
            break

if __name__ == '__main__':
    args = parse_args() 
    http_protocol = args.http
    if http_protocol :
        print("Protocol : HTTP")
        http_setup = httpSetup()
    else : 
        print("Protocol : MQTT")    #Default MQTT  
        mqtt_client = MQTTSetup()
        mqtt_client.connect()
    inference_enabled = args.inference
    main()
    

