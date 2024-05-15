import traceback
import threading
import argparse
import csv
import json
import time
from mqtt_setup_cloud import MQTTSetup
from http_server import HTTPServer
from source_setup import SourceSetup
from object_detection import Inference
from system_monitor import SystemMonitor
dirConfig = json.load(open(file="../util/dir_config.json", encoding="utf-8"))

###############################-CLOUD-###############################################

def parse_args():
    parser = argparse.ArgumentParser(description='Run edge device with optional parameters')
    parser.add_argument('--inference', action='store_true', help='Enable inference code')
    parser.add_argument('--http', action='store_true', help='Using HTTP protocol')
    return parser.parse_args()
    
def empty_frame():
    global frame
    frame = None
    if http_protocol :
        http.latest_frame = None
    else : #default MQTT
        mqtt.latest_frame = None

# Function to write FPS to CSV
def write_duration_csv(frame_id, byte_size, duration):
    with open(dirConfig["CSV_PROTOCOL_DURATION"], mode='a', newline='') as file:  # 'a' for append mode
        writer = csv.writer(file)
        writer.writerow([(frame_id-1), byte_size, duration])
        
def receive_protocol():
    global frame
    global frame_id
    global frame_check
    if http_protocol :
        if frame_id != http.frame_id :
            write_duration_csv(http.frame_id, http.payload_size, http.duration)
            frame = http.latest_frame
            frame_id = http.frame_id
            frame_check = True
        else :
            frame_check = False
    else : #default MQTT
        if frame_id != mqtt.frame_id :
            write_duration_csv(mqtt.frame_id, mqtt.payload_size, mqtt.duration)
            frame = mqtt.latest_frame
            frame_id = mqtt.frame_id
            frame_check = True
        else :
            frame_check = False

def main():
    global frame  
    global frame_id
    global frame_check
    frame = None
    frame_id = 1
    frame_check = False
    start_time = None
    source = SourceSetup()
    inference = Inference()
    systemMonitor = SystemMonitor(True)
    
    print("Cloud start parking detection !")

    #system_monitor_thread = threading.Thread(target=systemMonitor.start_monitoring)
    #system_monitor_thread.start()
    
    while True:
        try: 
            if frame_id == 2:
                start_time = time.time()  # Start the timer when frame_id reaches 2
            if start_time and (time.time() - start_time) > 600:  # 600 seconds = 10 minutes
                break  # Stop the loop after 10 minutes
            
            receive_protocol()
            if frame_check:
                height, width = frame.shape[:2]
                print(f"Received frame with resolution: {width}x{height}")
                print("##################################################\n") 
                if inference_enabled:                
                    inferenced_frame = inference.detect(frame)
                    source.show_images_opencv("CLOUD_INFERENCE", inferenced_frame)
                else:
                    source.show_images_opencv("CLOUD_RAW", frame)
                #http_setup.latest_frame = None
                #empty_frame()
        except Exception :
            print("Error main:", print(traceback.format_exc()))
            break

if __name__ == '__main__':
    args = parse_args() 
    http_protocol = args.http
    inference_enabled = args.inference
    if http_protocol :
        print("Protocol : HTTP")
        http = HTTPServer()
        http_thread = threading.Thread(target=http.app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
        http_thread.daemon = True
        http_thread.start()
    else : 
        print("Protocol : MQTT")    #Default Protocol
        mqtt = MQTTSetup()
        mqtt.connect()   
    with open(dirConfig["CSV_PROTOCOL_DURATION"], mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["FRAME_ID","BYTE_SIZE","DURATION"])
    main()
    

