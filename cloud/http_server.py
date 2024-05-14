import json
import base64
from flask import Flask, request, Response, jsonify
import cv2
import numpy as np
import traceback

class HTTPServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
        self.latest_frame = None
               
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    def setup_routes(self):
        @self.app.route('/video', methods=['POST'])   
        def receive_video():
            # Parse JSON data from request
            data = request.get_json()
            
            if data:
                # Re-encode the parsed JSON to a string
                json_string = json.dumps(data)

                # Calculate the byte size of the re-encoded JSON
                byte_size = len(json_string.encode('utf-8'))
                
                print(f"Message size : {byte_size} Byte")
                self.process_data(data)     
                return jsonify({"message": "Data received", "status": 200})    
            else:
                # Manually create JSON response for error handling
                #return Response(json.dumps({"error": "Invalid or no JSON data received."}), status=400, mimetype='application/json')
                return jsonify({"error": "Invalid or no JSON data received"}), 400

        
    def process_data(self, data):
        try:
            self.frame_id = data.get('id')
            frame_base64 = data.get('frame')
            client_timestamp = data.get('timestamp')
            
            print(f"Message http id {self.frame_id} : {client_timestamp}")
            self.decode_frame_payload(frame_base64)
        except Exception:
            print(f"Error on_message:", print(traceback.format_exc()))

    
    def decode_frame_payload(self, payload):
        payload_decode = base64.b64decode(payload)
        frame_data = np.frombuffer(payload_decode, np.uint8)
        frame_decode = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
        self.latest_frame =  frame_decode