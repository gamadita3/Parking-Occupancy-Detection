import traceback
import argparse
from mqtt_setup_cloud import MQTTSetup
from source_setup import SourceSetup
from object_detection import Inference

###############################-CLOUD-###############################################

def parse_args():
    parser = argparse.ArgumentParser(description='Run with optional inference')
    parser.add_argument('--enable-inference', action='store_true', help='Enable inference code')
    return parser.parse_args()

def main():
    dataset = True
    source = SourceSetup()
    inference = Inference()
    
    print("Cloud start parking detection !")

    #system_monitor_thread = threading.Thread(target=systemmonitor.start_monitoring)
    #system_monitor_thread.start()
    
    while True: 
        try: 
            if mqtt_client.latest_frame is not None:
                frame = mqtt_client.latest_frame
                height, width = frame.shape[:2]
                print(f"Received frame with resolution: {width}x{height}")
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
    main()
    

