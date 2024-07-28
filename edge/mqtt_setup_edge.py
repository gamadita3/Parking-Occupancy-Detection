import json
import cv2
import paho.mqtt.client as mqtt
import time
import base64

class MQTTSetup:
    def __init__(self):
        self.mqttConfig = self.load_config('../util/mqtt_config.json')
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.frame_id = 0
        self.ack = False #TESTING PROTOCOL
        
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def connect(self):
        self.client.connect(self.mqttConfig["HOST_ADDRESS"], self.mqttConfig["PORT"], keepalive=60)
        self.client.subscribe([(self.mqttConfig["TOPIC_ACK"], self.mqttConfig["QOS"])]) #TESTING PROTOCOL
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connecting MQTT to host: ", self.mqttConfig["HOST_ADDRESS"])
        if rc == 0:
            print("Connected to MQTT host !")
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_disconnect(self, client, userdata, rc):
        print("Unexpected MQTT disconnection!")

    def on_message(self, client, userdata, message): #TESTING PROTOCOL
        if message.topic == self.mqttConfig["TOPIC_ACK"]: 
            payload = message.payload.decode('utf-8')
            if message.payload.decode('utf-8') == str(self.frame_id):
                self.ack = True
                print("Received ACK from cloud")

    def on_publish(self, client, userdata, mid):
        print(f"Message published successfully, Message ID: {mid}")

    def publish(self, topic, payload):
        result, mid = self.client.publish(topic, payload, qos=self.mqttConfig["QOS"])
        if result == mqtt.MQTT_ERR_SUCCESS:
            print(f"Publish initiated for topic {topic}")
        else:
            print(f"Failed to initiate publish for topic {topic}, error code: {result}")
        
    def send_frame(self, frame=None, empty_detection=0, occupied_detection=0):
        frame_quality = self.mqttConfig["JPEG_QUALITY"]
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), frame_quality]
        height, width = frame.shape[:2]
        _, frame_encoded = cv2.imencode(".jpg", frame, encode_params)
        
        # Convert frame to bytes for publishing
        frame_bytes = frame_encoded.tobytes()
        frame_base64 = base64.b64encode(frame_bytes).decode("utf-8")
        
        timestamp = time.time()
        self.frame_id += 1
        
        mqtt_message = {
            #"topic": self.mqttConfig["TOPIC_FRAME"],
            "id": self.frame_id,
            "frame": frame_base64,
            "empty_detection": empty_detection,
            "occupied_detection": occupied_detection,
            "timestamp": timestamp
        }
    
        mqtt_payload = json.dumps(mqtt_message)
        self.ack = False #TESTING PROTOCOL
        self.publish(self.mqttConfig["TOPIC_FRAME"], mqtt_payload)
        
        
        print(f"Payload size for id {self.frame_id - 1}: {len(mqtt_payload) / 1000} kilobytes")
        print(f"Publishing frame with resolution {width}x{height} and jpeg quality {frame_quality}%")
        print(f"Total frame sent: {self.frame_id - 1}")
        
    def send_sample(self, frame):
        height, width = frame.shape[:2]
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 100]  # PNG compression level 0 (no compression)
        _, frame_encoded = cv2.imencode(".jpg", frame, encode_params)
        
        # Convert frame to bytes for publishing
        frame_bytes = frame_encoded.tobytes()
        frame_base64 = base64.b64encode(frame_bytes).decode("utf-8")

        timestamp = time.time()
        
        mqtt_message = {
            "frame": frame_base64,
            "timestamp": timestamp
        }
        mqtt_payload = json.dumps(mqtt_message)
        self.publish(self.mqttConfig["TOPIC_SAMPLE"], mqtt_payload)
        
        print(f"Publishing frame sample with resolution {width}x{height} !!!")
        
    def publish_timestamp(self):
        timestamp = time.time()
        print("Publish timestamp")
        self.publish(self.mqttConfig["TOPIC_FRAME"], timestamp)