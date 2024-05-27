import json
import cv2
import base64
import paho.mqtt.client as mqtt
import numpy as np
import traceback
import ntplib
import time

class MQTTSetup:
    def __init__(self):
        self.mqttConfig = self.load_config('../util/mqtt_config.json')
        self.client = mqtt.Client()
        self.ntpClient = ntplib.NTPClient()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.data_store = {}
    
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def connect(self):
        self.client.connect(self.mqttConfig["HOST_ADDRESS"], self.mqttConfig["PORT"], keepalive=60)
        self.topics = self.mqttConfig["LIST_TOPIC_FRAME"].split(',')
        for topic in self.topics:
            self.client.subscribe([(topic, self.mqttConfig["QOS"])])
            self.data_store[topic] = {}
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connecting MQTT to host: ", self.mqttConfig["HOST_ADDRESS"])
        if rc == 0:
            print("Connected to MQTT host !")
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_disconnect(self, client, userdata, rc):
        print("Unexpected MQTT disconnection!")
    
    def printProtocol(self,topic):
        print(f"print protocol |{topic}| {self.data_store[topic]}")

    def on_message(self, client, userdata, message):
        try:
            server_timestamp = time.time()
            if message.topic in self.topics:                
                mqtt_message = json.loads(message.payload)             
                client_timestamp = mqtt_message['timestamp']
                duration = f"{(server_timestamp - client_timestamp) * 1000}"
                data = {
                    "frame_id": mqtt_message['id'],
                    "empty_detection": mqtt_message['empty_detection'],
                    "occupied_detection": mqtt_message['occupied_detection'],
                    "duration": duration,
                    "payload_size": len(message.payload) / 1000  # Kilobytes
                }
                self.data_store[message.topic] = data
                self.decode_frame_payload(message.topic, mqtt_message['frame']) 
                print(f"|{message.topic}| Transmission duration for id {self.data_store[message.topic]['frame_id'] - 1} : {self.data_store[message.topic]['duration']}")
                print(f"|{message.topic}| Payload size for id {self.data_store[message.topic]['frame_id'] - 1} : {self.data_store[message.topic]['payload_size']} kilobytes")   
                #self.printProtocol(message.topic)
                
            else:
                print("Received info:", message.payload.decode('utf-8'))          
        except Exception:
            print(f"Error on_message:", print(traceback.format_exc()))


    def on_publish(self, client, userdata, mid):
        print(f"Message published successfully, Message ID: {mid}")

    def publish(self, topic, payload):
        result, mid = self.client.publish(topic, payload)
        if result == mqtt.MQTT_ERR_SUCCESS:
            print(f"Publish initiated for Message ID: {mid}")
        else:
            print(f"Failed to initiate publish, error code: {result}")
            
    def decode_frame_payload(self, topic, payload):
        payload_decode = base64.b64decode(payload)
        frame_data = np.frombuffer(payload_decode, np.uint8)
        frame_decode = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
        self.data_store[topic]["frame"] =  frame_decode
        
    