import traceback
import argparse
import csv
import json
import time
from source_manager import SourceManager
from display_setup import DisplaySetup
from object_detection import Inference
from system_monitor import SystemMonitor
dirConfig = json.load(open(file="../util/dir_config.json", encoding="utf-8"))

###############################-CLOUD-###############################################

def parse_args():
    parser = argparse.ArgumentParser(description='Run edge device with optional parameters')
    parser.add_argument('--inference', action='store_true', help='Enable inference code')
    parser.add_argument('--http', action='store_true', help='Using HTTP protocol')
    return parser.parse_args()

def main():
    start_time = None
    display = DisplaySetup()
    inference = Inference()
    systemMonitor = SystemMonitor(True)
    
    print("Cloud start parking detection !")

    #system_monitor_thread = threading.Thread(target=systemMonitor.start_monitoring)
    #system_monitor_thread.start()
    
    while True:
        try: 
            #! LIMITER (Disable when deployed)
            if source.frame_id == 2:
                start_time = time.time()  # Start the timer when frame_id reaches 2
            if start_time and (time.time() - start_time) > 60:  # 60 seconds = 1 minutes
                break  # Stop the loop after 1 minutes
            #!!!!!!!!!!!!!!!!!!!!!!!!

            source.receive_data()
            if source.frame_check:
                height, width = source.frame.shape[:2]
                print(f"Received frame with resolution: {width}x{height}")
                print(f"Total Detection {(source.occupied_detection + source.empty_detection)} | Empty {source.empty_detection} | Occupied {source.occupied_detection}")
                print("##################################################\n") 
                if inference_enabled:                
                    inferenced_frame = inference.detect(source.frame)
                    display.show_images_opencv("CLOUD_INFERENCE", inferenced_frame)
                else:
                    display.show_images_opencv("CLOUD_RAW", source.frame)
        except Exception :
            print("Error main:", print(traceback.format_exc()))
            break

if __name__ == '__main__':
    args = parse_args() 
    http_check = args.http
    inference_enabled = args.inference
    source = SourceManager()
    source.start_protocol(http_check)        
    with open(dirConfig["CSV_PROTOCOL_DURATION"], mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["FRAME_ID","BYTE_SIZE","DURATION"])
    main()
    

