import json
import traceback
import time
import argparse
import numpy as np
import threading
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
    parser.add_argument('--monitor', action='store_true', help='Monitor CPU and RAM usage')
    parser.add_argument('--dataset', action='store_true', help='Run using dataset')
    parser.add_argument('--store', action='store_true', help='Store frame')
    return parser.parse_args()

def main():
    motion_detected = False 
    camera = CameraSetup(dataset_enabled)
    inference = Inference(store_enabled)
    motiondetection = MotionDetection()
    systemmonitor = SystemMonitor(monitor_enabled)
    
    initial_frame = camera.get_frame()
    if monitor_enabled :   
        system_monitor_thread = threading.Thread(target=systemmonitor.start_monitoring)
        system_monitor_thread.start()
    
    print("\nEdge start parking detection !")
    
    while True: 
        loop_start_time = time.time()  # Record start time of the loop
        try:                         
            if motion_detected:
                print("\nMotion Detected !")
                print("---resize frame---")
                #initial_frame = camera.compress_resize(initial_frame)
                if inference_enabled:
                    print("\n---Inference---")
                    inference.detect(initial_frame)                  
                    print("\n---Publishing---")
                    protocol.send_frame(inference.frame, inference.total_empty_detection, inference.total_occupied_detection)
                    #camera.show_images_opencv("EDGE_INFERENCE", inferenced_frame)
                else:
                    protocol.send_frame(frame=initial_frame)
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
    http_check = args.http
    if http_check :
        print("Protocol : HTTP")
        protocol = httpSetup()
    else : 
        print("Protocol : MQTT")    #Default MQTT  
        protocol = MQTTSetup()
        protocol.connect()
    inference_enabled = args.inference
    print(f"Inference : {inference_enabled}")
    monitor_enabled = args.monitor
    print(f"Monitoring : {monitor_enabled}")
    dataset_enabled = args.dataset
    print(f"Using Dataset : {dataset_enabled}")
    store_enabled = args.store
    print(f"Store : {store_enabled}")
    main()
    

