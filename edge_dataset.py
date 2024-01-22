import json
import os
import time
import cv2
import random
import numpy as np
import paho.mqtt.client as mqtt
from ultralytics import YOLO
mqttConfig = json.load(open(file="./util/mqtt_config.json", encoding="utf-8"))
frameConfig = json.load(open(file="./util/frame_config.json", encoding="utf-8"))

#----------------------------MQTT SETUP-----------------------------------------#
mqtt_client = mqtt.Client()

def on_message(client, userdata, msg):
    pass

def on_publish(client, userdata, msg):
    #print(f"pub {msg}")
    pass

def initialize_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)        
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(mqttConfig["HOST_ADDRESS"], mqttConfig["PORT"])
    #mqtt_client.subscribe(config["topic"])
    mqtt_client.loop_start()
    #mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish
    return mqtt_client

def publish_frame(frame):
    print(f'Publishing frame')
    _, _frameEncoded = cv2.imencode(".jpg", frame)
    mqtt_client.publish(mqttConfig["TOPIC"], _frameEncoded.tobytes())

def publish_batches(frames):
    frames_batch = b''  # Initialize an empty bytes object
    for frame in frames:
        _, frameEncoded = cv2.imencode(".jpg", frame) 
        frames_batch += frameEncoded.tobytes() + b','
    mqtt_client.publish(mqttConfig["TOPIC"], frames_batch)
    

#----------------------------CV2 IMAGES-----------------------------------------#

def get_images():
    image_folder = frameConfig['FOLDER_IMAGES']
    frames = [cv2.imread(os.path.join(image_folder, img)) for img in os.listdir(image_folder) if img.endswith(".jpg")]
    return frames

#----------------------------INFERENCE-----------------------------------------#
inference = False
coco_file = open("./util/label.txt", "r")
class_list = coco_file.read().split("\n")
coco_file.close()

model = YOLO("./util/parking.pt")
detection_colors = []
for i in range(len(class_list)):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    detection_colors.append((b, g, r))
    
#def inference():

#----------------------------MOTION DETECTION-----------------------------------------#
motion_detected = False
start_time = time.time()

def motion_detection(old_frame, new_frame):
        global motion_detected
        global start_time
        old_frame_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        new_frame_gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
        frame_diff = cv2.absdiff(old_frame_gray, new_frame_gray)
        _, thresh = cv2.threshold(frame_diff, 40, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:           
            if cv2.contourArea(contour) > 100: #threshold sensitivity set 100
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(new_frame, (x, y), (x + w, y + h), (10, 10, 255), 2)
                motion_detected = True
                start_time = time.time()      
        if motion_detected:
            print("Motion Detected !!")
            
#----------------------------CV2 show image-----------------------------------------#   
def show_images(frame):
    cv2.imshow('Image', frame)
    cv2.waitKey(30)   
    cv2.destroyAllWindows()     

########################################################################################

def run():   
    global motion_detected
    global start_time
    frames = get_images()
    frame_initial = frames[random.randint(0, len(frames)-1)]
    image_index = 0
    for frame in frames:     
        try:
            if  motion_detected:
                print("Motion detected")    
                #inference(frames)
                motion_detected = False
                show_images(frame)
                frame_initial = frame
            else:   
                frame_detect = frame
                motion_detection(frame_initial, frame_detect)  
        except Exception as error:
            print("Error:", error)     

def main():
    initialize_mqtt()
    run()

if __name__ == '__main__':
    main()
    

