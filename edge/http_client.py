import requests
import json
import base64
import time
import cv2

class httpSetup:
    def __init__(self):
        self.httpConfig = self.load_config('../util/http_config.json')
        self.frameConfig = self.load_config('../util/frame_config.json')
        self.server_url = self.httpConfig["URL"]
        self.frame_id = 0
        
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    def send_frame(self, frame):
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), self.frameConfig["JPEG_QUALITY"]]
        height, width = frame.shape[:2]
        print(f"Publishing frame with resolution: {width}x{height}")
        
        _, frame_encoded = cv2.imencode(".jpg", frame, encode_params)
        
        # Convert frame to bytes for publishing
        frame_bytes = frame_encoded.tobytes()
        frame_base64 = base64.b64encode(frame_bytes).decode("utf-8")
        #frame_base64 = None
        
        timestamp = time.time()
        #print(f"Sending timestamp: {timestamp}")
        
        self.frame_id += 1
        
        http_message = {
            "id": self.frame_id,
            "frame": frame_base64,
            "timestamp": timestamp
        }
        
       # Serialize the data to JSON and specify 'application/json' content type
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.server_url, json=http_message, headers=headers)
        end_timestamp = time.time()
        
        print(f"HTTP post duration : {(end_timestamp - timestamp) * 1000} ms")
        
        if(response.status_code == 200):           
            print(f"Frame id {self.frame_id} successfully sent \n")
        else:
            print(f"Failed to send frame id  {self.frame_id}. Status code: {response.status_code}, Error: {response.text}")