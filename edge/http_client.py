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
        frame_quality = self.frameConfig["JPEG_QUALITY"]
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), frame_quality]
        height, width = frame.shape[:2]
        
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
        
        http_payload = json.dumps(http_message)
        headers = {'Content-Type': 'application/json'}     
        response = requests.post(self.server_url, data=http_payload, headers=headers)
        end_timestamp = time.time()
        
        print(f"Payload size for id {self.frame_id - 1}: {len(http_payload) / 1000} kilobytes")
        print(f"Publishing frame with resolution {width}x{height} and jpeg quality {frame_quality}%")
        print(f"HTTP post duration : {(end_timestamp - timestamp) * 1000} ms")
        
        if(response.status_code == 200):           
            print(f"Frame id {self.frame_id - 1} successfully sent \n")
        else:
            print(f"Failed to send frame id  {self.frame_id - 1}. Status code: {response.status_code}, Error: {response.text}")