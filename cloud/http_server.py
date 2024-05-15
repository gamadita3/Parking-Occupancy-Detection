import json
import base64
from flask import Flask, request, Response, jsonify
import cv2
import numpy as np
import traceback
import time

class HTTPServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
        self.latest_frame = None
        self.frame_id = 1
               
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    def setup_routes(self):
        @self.app.route('/video', methods=['POST'])   
        def receive_video():
            self.server_timestamp = time.time()
            data = request.data
            
            if data:
                self.payload_size = len(data)
                http_message = json.loads(data.decode('utf-8'))
                
                self.process_data(http_message)     
                return jsonify({"message": "Data received", "status": 200})    
            else:
                #return Response(json.dumps({"error": "Invalid or no JSON data received."}), status=400, mimetype='application/json')
                return jsonify({"error": "Invalid or no JSON data received"}), 400

        
    def process_data(self, data):
        try:
            self.frame_id = data.get('id')
            frame_base64 = data.get('frame')
            client_timestamp = data.get('timestamp')
            
            self.duration = f"{(self.server_timestamp - client_timestamp)*1000}"
               
            print(f"Payload size for id {self.frame_id - 1} : {self.payload_size / 1000} kilobytes")            
            print(f"Transmission duration for id {self.frame_id - 1} : {self.duration}")            
            self.decode_frame_payload(frame_base64)
        except Exception:
            print(f"Error on_message:", print(traceback.format_exc()))

    
    def decode_frame_payload(self, payload):
        payload_decode = base64.b64decode(payload)
        frame_data = np.frombuffer(payload_decode, np.uint8)
        frame_decode = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
        self.latest_frame =  frame_decode