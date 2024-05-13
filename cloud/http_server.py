import json
import base64
from aiohttp import web
import cv2
import numpy as np
import traceback
import time

class HTTPServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.app = web.Application()
        self.host = host
        self.port = port
        self.setup_routes()
        self.latest_frame = None
               
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    def setup_routes(self):
        self.app.add_routes([web.post('/video', self.receive_video)])
    
    async def receive_video(self, request):
        try:
            data = await request.json()
            json_string = json.dumps(data)
            byte_size = len(json_string.encode('utf-8'))
            print(f"Message size: {byte_size} Byte")
            await self.process_data(data)
            return web.json_response({"message": "Data received", "status": 200})
        except Exception as e:
            print(f"Error processing video: {traceback.format_exc()}")
            return web.json_response({"error": "Invalid or no JSON data received"}, status=400)

        
    async def process_data(self, data):
        try:
            self.frame_id = data.get('id')
            frame_base64 = data.get('frame')
            client_timestamp = data.get('timestamp')
            
            server_timestamp = time.time()
            
            print(f"Message http id {self.frame_id} : {client_timestamp}")
            print(f"HTTP tranmission time : {(server_timestamp - client_timestamp) * 1000} ms")
            self.decode_frame_payload(frame_base64)
        except Exception:
            print(f"Error on_message:", print(traceback.format_exc()))

    
    def decode_frame_payload(self, payload):
        if payload is not None :
            payload_decode = base64.b64decode(payload)
            frame_data = np.frombuffer(payload_decode, np.uint8)
            frame_decode = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
            self.latest_frame =  frame_decode
        
    def run(self):
        web.run_app(self.app, host=self.host, port=self.port)