import json
import base64
from flask import Flask, request, Response, jsonify
import cv2
import numpy as np
import traceback
import time
from datetime import datetime, timedelta

class HTTPServer:
    def __init__(self):
        self.mqttConfig = self.load_config('../util/mqtt_config.json')
        self.topics = self.mqttConfig["LIST_TOPIC_FRAME"].split(',')
        self.data_store = {}
        self.initial_datastore()
        self.app = Flask(__name__)
        self.setup_routes()
        
    
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    def setup_routes(self):
        @self.app.route('/video', methods=['POST'])   
        def receive_video():
            server_timestamp = time.time()
            data = request.data
            
            if data:
                self.process_data(data, server_timestamp)     
                return jsonify({"message": "Data received", "status": 200})    
            else:
                #return Response(json.dumps({"error": "Invalid or no JSON data received."}), status=400, mimetype='application/json')
                return jsonify({"error": "Invalid or no JSON data received"}), 400
            
    def initial_datastore(self):
        for topic in self.topics:
            data = {"frame_id": "-"}   
            self.data_store[topic] = data
            
    def process_data(self, data, server_timestamp):
        payload_size = len(data)
        payload = json.loads(data.decode('utf-8'))
        try:  
            topic = payload.get('topic')        
            if topic in self.topics:                
                client_timestamp = payload.get('timestamp')
                formatted_time = (datetime.fromtimestamp(client_timestamp)+ timedelta(hours=7)).strftime("%d-%m-%Y %H:%M:%S")
                duration = f"{(server_timestamp - client_timestamp) * 1000}"
                data = {
                    "frame_id":  payload.get('id'),
                    "empty_detection": payload.get('empty_detection'),
                    "occupied_detection": payload.get('occupied_detection'),
                    "time" : formatted_time,
                    "duration": duration,
                    "payload_size": payload_size / 1000  # Kilobytes
                }
                self.data_store[topic] = data
                self.decode_frame_payload(topic, payload.get('frame'))
                print( f"|{topic}| id: {self.data_store[topic]['frame_id'] - 1} | Transmission duration: {self.data_store[topic]['duration']} | Payload size: {self.data_store[topic]['payload_size']} kilobytes")  
        except Exception:
            print(f"Error on_message:", print(traceback.format_exc()))
    
    def decode_frame_payload(self, topic, payload):
        payload_decode = base64.b64decode(payload)
        frame_data = np.frombuffer(payload_decode, np.uint8)
        frame_decode = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
        self.data_store[topic]["frame"] =  frame_decode