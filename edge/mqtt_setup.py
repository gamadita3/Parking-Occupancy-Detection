import json
import cv2
import paho.mqtt.client as mqtt

class MQTTSetup:
    def __init__(self):
        self.mqttconfig = self.load_config('../util/mqtt_config.json')
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def connect(self):
        self.client.connect(self.mqttconfig["HOST_ADDRESS"], self.mqttconfig["PORT"], keepalive=60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connecting MQTT to host : ", self.mqttconfig["HOST_ADDRESS"])
        if rc == 0:
            print("Connected to MQTT host !")
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_disconnect(self, client, userdata, rc):
        print("Unexpected MQTT disconnection!")

    def on_message(self, client, userdata, message):
        pass

    def on_publish(self, client, userdata, mid):
        pass

    def publish(self, topic, payload):
        self.client.publish(topic, payload)
        
    def publish_frame(self, frame):
        print(f'Publishing frame')
        _, _frameEncoded = cv2.imencode(".jpg", frame)
        self.publish(self.mqttconfig["TOPIC_FRAME"], _frameEncoded.tobytes())
