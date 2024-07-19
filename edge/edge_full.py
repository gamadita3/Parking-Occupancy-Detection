import json
import traceback
import time
import argparse
import datetime
import threading
import math
from mqtt_setup_edge import MQTTSetup
from http_client import httpSetup
from camera_setup import CameraSetup
from motion_detection import MotionDetection
from object_detection import Inference
from system_monitor import SystemMonitor
samplingConfig = json.load(open(file="../util/sampling_config.json", encoding="utf-8"))

###############################-EDGE-###############################################

def parse_args():
    parser = argparse.ArgumentParser(description='Run edge device with optional parameters')
    parser.add_argument('--inference', action='store_true', help='Enable inference code')
    parser.add_argument('--http', action='store_true', help='Using HTTP protocol')
    parser.add_argument('--monitor', action='store_true', help='Monitor CPU and RAM usage')
    parser.add_argument('--dataset', action='store_true', help='Run using dataset')
    parser.add_argument('--store', action='store_true', help='enable store frame')
    parser.add_argument('--FPS', action='store_true', help='enable FPS counter')
    return parser.parse_args()

def main():
    motion_detected = True
    camera = CameraSetup(dataset_enabled)
    inference = Inference(store_enabled)
    motiondetection = MotionDetection()
    systemmonitor = SystemMonitor(monitor_enabled)
    last_sent_time = time.time()
    
    initial_frame = camera.get_frame()
    if monitor_enabled :   
        system_monitor_thread = threading.Thread(target=systemmonitor.start_monitoring)
        system_monitor_thread.start()
    
    print(f"\nEdge start parking detection ! at {datetime.datetime.now().time()}")
    
    skip_frame_count = 0  
    system_start_time = time.time()
    
    while True: 
        masterloop_start_time = time.time()
        loop_start_time = time.time()  # Record start time of the loop
        current_time = datetime.datetime.now().time()
        try:       
            if skip_frame_count > 0:  # Check if there are frames to skip
                skip_frame_count -= 1  # Decrement skip frame count
                initial_frame = camera.get_frame()  # Read next frame to skip
                continue  # Skip the rest of the loop      
                       
            if motion_detected:
                #print("\nMotion Detected !")
                #print("---resize frame---")
                #initial_frame = camera.compress_resize(initial_frame)
                initial_frame = camera.compress_frame(initial_frame)
                if inference_enabled:
                    if datetime.time(samplingConfig["SAMPLE_START_HOUR"], 0) <= current_time <= datetime.time(samplingConfig["SAMPLE_STOP_HOUR"], 0):
                        if time.time() - last_sent_time >= samplingConfig["SAMPLE_INTERVAL"] :
                            protocol.send_sample(frame=initial_frame)
                            last_sent_time = time.time()
                    print("\n---Inference---")
                    inference.detect(initial_frame)                  
                    print("\n---Publishing---")
                    protocol.send_frame(inference.frame, inference.total_empty_detection, inference.total_occupied_detection)
                    camera.show_images_opencv("EDGE_INFERENCE", inference.frame)
                else:
                    if datetime.time(samplingConfig["SAMPLE_START_HOUR"], 0) <= current_time <= datetime.time(samplingConfig["SAMPLE_STOP_HOUR"], 0):
                        if time.time() - last_sent_time >= samplingConfig["SAMPLE_INTERVAL"] :
                            protocol.send_sample(frame=initial_frame)
                            last_sent_time = time.time()
                    protocol.send_frame(frame=initial_frame)
                    #camera.show_images_opencv("EDGE_RAW", initial_frame)     
                initial_frame = camera.get_frame()
                print("##################################################")              
            else:   
                if datetime.time(samplingConfig["SAMPLE_START_HOUR"], 0) <= current_time <= datetime.time(samplingConfig["SAMPLE_STOP_HOUR"], 0):
                    if time.time() - last_sent_time >= samplingConfig["SAMPLE_INTERVAL"] :
                            protocol.send_sample(frame=initial_frame)
                            last_sent_time = time.time()                                          
                next_frame = camera.get_frame()         
                #motion_detected = motiondetection.detect_motion(initial_frame, next_frame)
                initial_frame = next_frame
                #camera.show_images_opencv("RAW",initial_frame)              
            loop_end_time = time.time()
            if fps_enabled :   
                total_loop_time = loop_end_time - loop_start_time  
                print("loop duration : ", total_loop_time)                 
                time_to_sleep = max(0, (1 / 7.5) - total_loop_time)  # Calculate time to sleep to maintain target frame rate
                if time_to_sleep != 0 :
                    print("loop duration : ", total_loop_time)
                    time.sleep(time_to_sleep)                   
                masterloop_end_time = time.time()
                masterloop = masterloop_end_time - masterloop_start_time 
                FPS = 1/(masterloop)                  
                #FPS = float('inf') if total_loop_time == 0 else 1 / total_loop_time
                print("FPS per loop : ", FPS)          
                skip_frame_count = math.ceil(masterloop * 7.5) # Calculate number of frames to skip based on inference duration
                print("total skip frame :", skip_frame_count)                                        
        except Exception :
            print("Error:", print(traceback.format_exc()))
            break
    system_end_time = time.time()
    total_time_system = system_end_time - system_start_time
    print("TOTAL SYSTEM PROCESS : ", total_time_system)

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
    fps_enabled = args.FPS
    print(f"FPS : {fps_enabled}")
    main()
    

