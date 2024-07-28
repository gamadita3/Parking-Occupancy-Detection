import json
import traceback
import time
import argparse
import datetime
import threading
from mqtt_setup_edge import MQTTSetup
from http_client import httpSetup
from camera_setup import CameraSetup
from object_detection import Inference
from system_monitor import SystemMonitor
samplingConfig = json.load(open(file="../util/sampling_config.json", encoding="utf-8"))

###############################-EDGE-###############################################

def parse_args():
    parser = argparse.ArgumentParser(description='Run edge device with optional parameters')
    parser.add_argument('--inference', action='store_true', help='Enable inference code')
    parser.add_argument('--http', action='store_true', help='Using HTTP protocol')
    parser.add_argument('--dataset', action='store_true', help='Run using dataset')
    parser.add_argument('--store', action='store_true', help='enable store frame')
    parser.add_argument('--FPS', action='store_true', help='enable FPS counter')
    return parser.parse_args()

def main():
    dataset_enabled = True
    camera = CameraSetup(dataset_enabled)
    inference = Inference(store_enabled)
    
    initial_frame = camera.get_frame()
    print(f"\nEdge start parking detection ! at {datetime.datetime.now().time()}")
    start_time = time.time()
    protocol.ack = True
    
    while True: 
        if protocol.ack:
            loop_start_time = time.time()  # Record start time of the loop
            try:                         
                if inference_enabled:
                    print("\n---Inference---")
                    inference.detect(initial_frame)                  
                    print("\n---Publishing---")
                    protocol.send_frame(inference.frame, inference.total_empty_detection, inference.total_occupied_detection)
                    #camera.show_images_opencv("EDGE_INFERENCE", inferenced_frame)
                else:
                    protocol.send_frame(frame=initial_frame)
                    #camera.show_images_opencv("EDGE_RAW", initial_frame)     
                initial_frame = camera.get_frame()
                print("##################################################")                   
                loop_end_time = time.time()
                if fps_enabled :
                    total_loop_time = loop_end_time - loop_start_time    
                    FPS = 1/total_loop_time if total_loop_time != 0 else float('inf')
                    print("FPS per loop : ", FPS)                                   
            except Exception :
                print("Error:", print(traceback.format_exc()))
                break
    print(f"\nEdge stop parking detection ! at {datetime.datetime.now().time()}")

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
    dataset_enabled = args.dataset
    print(f"Using Dataset : {dataset_enabled}")
    store_enabled = args.store
    print(f"Store : {store_enabled}")
    fps_enabled = args.FPS
    print(f"FPS : {fps_enabled}")
    main()
    

