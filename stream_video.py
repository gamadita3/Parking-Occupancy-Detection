import cv2
import json
import random
import numpy as np
import paho.mqtt.client as mqtt
from ultralytics import YOLO
mqttConfig = json.load(open(file="./util/mqtt_config.json", encoding="utf-8"))
frameConfig = json.load(open(file="./util/frame_config.json", encoding="utf-8"))
dirConfig = json.load(open(file="./util/dir_config.json", encoding="utf-8"))

#----------------------------MQTT SETUP-----------------------------------------#
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)   

def on_message(client, userdata, msg):
    pass

def on_publish(client, userdata, msg):
    print(f"publish callback : {msg}")
    pass

def publish_frame(frame):
    print(f'Publishing frame')
    _, frameEncoded = cv2.imencode(".jpg", frame)
    mqtt_client.publish(mqttConfig["TOPIC"], frameEncoded.tobytes())

def publish_batches(frames):
    frames_batch = b''  # Initialize an empty bytes object
    for frame in frames:
        _, frameEncoded = cv2.imencode(".jpg", frame) 
        frames_batch += frameEncoded.tobytes() + b','
    mqtt_client.publish(mqttConfig["TOPIC"], frames_batch)
    
def initialize_mqtt():       
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(mqttConfig["HOST_ADDRESS"], mqttConfig["PORT"])
    mqtt_client.loop_start()
    mqtt_client.on_publish = on_publish
    return mqtt_client

 #----------------------------OPENCV GET VIDEO-----------------------------------------#   
def get_video():
    video_folder = dirConfig['VIDEO']
    video_source = cv2.VideoCapture(video_folder)
    print(f"Total frames : {int(video_source.get(cv2.CAP_PROP_FRAME_COUNT))}")
    return video_source

video = get_video()

#----------------------------CV2 show image-----------------------------------------#   
def show_images_opencv(window, frame):
    frame_show = cv2.resize(frame, (854,480))
    cv2.imshow(window, frame_show)
    cv2.waitKey(1)
    
###############################################################################################

def main(): 
    while True: 
        try:
            ret, frame = video.read()
            if not ret:
                print("Failed to read video")
                return
            show_images_opencv('source', frame)
            publish_frame(frame)
        except Exception as error:
            print("Error:", error)     
    
if __name__ == '__main__':
    initialize_mqtt()
    main()