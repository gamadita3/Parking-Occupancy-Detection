import json
import time
import cv2
import numpy as np
import paho.mqtt.client as mqtt
mqttConfig = json.load(open(file="./util/mqtt_config.json", encoding="utf-8"))

#----------------------------GLOBAL VARIABLE-----------------------------------------#
last_frame_time = None
frame_count = 0
total_time = 0
mqtt_client = mqtt.Client()

#----------------------------MQTT SETUP-----------------------------------------#
def on_message(client, userdata, msg):
    global last_frame_time, frame_count, total_time
    try:   
        # Record the receive time
        start_time = time.time()
        
        # Calculate the transmission time
        transmission_time = time.time() - start_time
        total_time += transmission_time
        print(f"Transmission time: {transmission_time}")
        
        # Calculate FPS using the time difference between the last frame and current frame
        if last_frame_time is not None:
            fps = 1 / (start_time - last_frame_time)
            print(f"Current FPS: {fps}")
        last_frame_time = start_time
            
        # Decode message payload and display the frame
        frame_data = np.frombuffer(msg.payload, dtype=np.uint8)
        frame_decode = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
        frame_show = cv2.resize(frame_decode, (854,480))
        cv2.imshow("stream", frame_show)
            
        frame_count += 1        
    except Exception as e:
        print(f"Error: {e}")

def initialize_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)        
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(mqttConfig["HOST_ADDRESS"], mqttConfig["PORT"])
    mqtt_client.subscribe(mqttConfig["TOPIC"])
    mqtt_client.on_message = on_message
    #mqtt_client.on_publish = on_publish
    return mqtt_client

########################################################################################

def run():  
    while True:
        mqtt_client.loop()
        cv2.waitKey(1)

def main():
    initialize_mqtt()
    run()

if __name__ == '__main__':
    main()


