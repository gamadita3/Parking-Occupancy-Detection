import requests
import json
import base64
import time
import cv2

class httpSetup:
    def __init__(self):
        self.httpConfig = self.load_config('../util/http_config.json')
        self.mqttConfig = self.load_config('../util/mqtt_config.json')
        self.server_url = self.httpConfig["URL"]
        self.frame_id = 0
        self.ack = False #TESTING PROTOCOL
        
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    def send_frame(self, frame=None, empty_detection=0, occupied_detection=0):
        frame_quality = self.httpConfig["JPEG_QUALITY"]
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), frame_quality]
        height, width = frame.shape[:2]
        _, frame_encoded = cv2.imencode(".jpg", frame, encode_params)
        
        # Convert frame to bytes for publishing
        frame_bytes = frame_encoded.tobytes()
        frame_base64 = base64.b64encode(frame_bytes).decode("utf-8")
        
        timestamp = time.time()
        self.frame_id += 1
        
        http_message = {
            "topic": self.mqttConfig["TOPIC_FRAME"],
            "id": self.frame_id,
            "frame": frame_base64,
            "empty_detection": empty_detection,
            "occupied_detection": occupied_detection,
            "timestamp": timestamp
        }
        
        http_payload = json.dumps(http_message)
        headers = {'Content-Type': 'application/json'}     
        response = requests.post(self.server_url, data=http_payload, headers=headers)
        end_timestamp = time.time()
        self.ack = True #TESTING PROTOCOL
        
        print(f"Payload size for id {self.frame_id - 1}: {len(http_payload) / 1000} kilobytes")
        print(f"Publishing frame with resolution {width}x{height} and jpeg quality {frame_quality}%")
        print(f"Total frame sent: {self.frame_id - 1}")
        print(f"HTTP post duration : {(end_timestamp - timestamp) * 1000} ms")
        
        if(response.status_code == 200):           
            print(f"Frame id {self.frame_id - 1} successfully sent \n")
        else:
            print(f"Failed to send frame id  {self.frame_id - 1}. Status code: {response.status_code}, Error: {response.text}")