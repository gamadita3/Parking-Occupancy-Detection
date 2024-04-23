import traceback
import argparse
import csv
import json
from mqtt_setup_cloud import MQTTSetup
from source_setup import SourceSetup
from object_detection import Inference
dirConfig = json.load(open(file="../util/dir_config.json", encoding="utf-8"))

###############################-CLOUD-###############################################

def parse_args():
    parser = argparse.ArgumentParser(description='Run with optional inference')
    parser.add_argument('--enable-inference', action='store_true', help='Enable inference code')
    return parser.parse_args()

# Function to write FPS to CSV
def write_duration_csv(byte_size, duration):
    with open(dirConfig["CSV_MQTT_DURATION"], mode='a', newline='') as file:  # 'a' for append mode
        writer = csv.writer(file)
        writer.writerow([byte_size, duration])

def main():
    source = SourceSetup()
    inference = Inference()
    
    print("Cloud start parking detection !")

    #system_monitor_thread = threading.Thread(target=systemmonitor.start_monitoring)
    #system_monitor_thread.start()
    
    while True: 
        try: 
            if mqtt_client.latest_frame is not None:
                frame = mqtt_client.latest_frame
                write_duration_csv(mqtt_client.payload_size, mqtt_client.duration)
                height, width = frame.shape[:2]
                print(f"Received frame with resolution: {width}x{height}")
                print("##################################################\n") 
                if inference_enabled:                
                    inferenced_frame = inference.detect(frame)
                    source.show_images_opencv("CLOUD_INFERENCE", inferenced_frame)
                else:
                    source.show_images_opencv("CLOUD_RAW", frame)
                mqtt_client.latest_frame = None
                
        except Exception :
            print("Error main:", print(traceback.format_exc()))
            break

if __name__ == '__main__':
    mqtt_client = MQTTSetup()
    mqtt_client.connect()
    inference_enabled = parse_args().enable_inference
    with open(dirConfig["CSV_MQTT_DURATION"], mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["BYTE_SIZE","DURATION"])
    main()
    

