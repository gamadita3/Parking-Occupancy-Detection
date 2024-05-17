import threading
import json
import csv
from mqtt_setup_cloud import MQTTSetup
from http_server import HTTPServer

class SourceManager:
    def __init__(self):
        self.frame = None
        self.frame_check = False
        self.frame_id = 1
        self.protocol = None
        self.empty_detection = 0
        self.occupied_detection = 0
        self.dirConfig = json.load(open(file="../util/dir_config.json", encoding="utf-8"))
        
    def start_protocol(self, http_check):
        if http_check :
            print("Protocol : HTTP")
            self.protocol = HTTPServer()
            http_thread = threading.Thread(target=self.protocol.app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
            http_thread.daemon = True
            http_thread.start()
        else : 
            print("Protocol : MQTT")    #Default Protocol
            self.protocol = MQTTSetup()
            self.protocol.connect()   
        
    def receive_data(self):    
        if self.frame_id != self.protocol.frame_id :
            self.write_duration_csv()
            self.frame = self.protocol.latest_frame
            self.empty_detection = self.protocol.empty_detection
            self.occupied_detection = self.protocol.occupied_detection
            self.frame_id = self.protocol.frame_id
            self.frame_check = True
        else :
            self.frame_check = False
            
    def write_duration_csv(self):
        with open(self.dirConfig["CSV_PROTOCOL_DURATION"], mode='a', newline='') as file:  # 'a' for append mode
            writer = csv.writer(file)
            writer.writerow([(self.protocol.frame_id-1), self.protocol.payload_size, self.protocol.duration])