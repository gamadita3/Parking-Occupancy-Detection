import os
import paho.mqtt.client as mqtt
import base64
import json
import cv2
import numpy as np
from datetime import datetime, timedelta
mqttConfig = json.load(open(file="../util/mqtt_config.json", encoding="utf-8"))
samplingConfig = json.load(open(file="../util/sampling_config.json", encoding="utf-8"))

def on_connect(client, userdata, flags, rc):
    host = mqttConfig["HOST_ADDRESS"]
    print(f"Connected to {host}")
    topics = mqttConfig["LIST_TOPIC_SAMPLE"].split(',')
    for topic in topics:
        client.subscribe([(topic, mqttConfig["QOS"])])

# Callback when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    try:
        print(f"Received message on topic: {msg.topic}")
        mqtt_message = json.loads(msg.payload)
        frame_base64 = mqtt_message['frame']
        timestamp = (datetime.fromtimestamp(mqtt_message['timestamp'])+ timedelta(hours=7)).strftime('%d-%m-%y_%H%M')
        
        # Decode the base64 string to bytes
        payload_decode = base64.b64decode(frame_base64)
        frame_data = np.frombuffer(payload_decode, np.uint8)
        frame_decode = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)

        # Construct the filename and save path
        filename = f"{msg.topic}_{timestamp}.jpg"
        sample_location = samplingConfig["SAMPLE_LOCATION"]
        file_path = os.path.join((f"{sample_location}_{msg.topic}"), filename)

        # Save the frame as a JPEG file
        cv2.imwrite(file_path, frame_decode)
        print(f"Saved {file_path}")
    except Exception as e:
        print(f"Failed to process message: {e}")

# Setup MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(mqttConfig["HOST_ADDRESS"], mqttConfig["PORT"], keepalive=60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
client.loop_forever()
