import json
import time
import cv2
import numpy as np
import paho.mqtt.client as mqtt
config = json.load(open(file="./config.json", encoding="utf-8"))

#----------------------------MQTT SETUP-----------------------------------------#
mqttClient = mqtt.Client()

#def on_message(client, userdata, msg):
#    pass

def on_publish(client, userdata, msg):
    print(f"pub {msg}")
    pass

def initialize_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)        
    mqttClient.on_connect = on_connect
    mqttClient.connect(config["host_address"], config["port"])
    #mqttClient.subscribe(config["topic"])
    mqttClient.loop_start()
    #mqttClient.on_message = on_message
    mqttClient.on_publish = on_publish
    return mqttClient

def publish_image(image):
    _, frame_encoded = cv2.imencode(".jpg", image)
    mqttClient.publish(config["topic"], frame_encoded.tobytes())

#----------------------------CAM SETUP-----------------------------------------#
cap = cv2.VideoCapture(0)
def setup_camera():
    cap.set(3, config["res_width"])
    cap.set(4, config["res_height"])
    return cap

########################################################################################

def run():  
    while True:
        ret, frame = cap.read()
        publish_image(frame)
        #time.sleep(1)

def main():
    initialize_mqtt()
    setup_camera()
    run()

if __name__ == '__main__':
    main()
    

