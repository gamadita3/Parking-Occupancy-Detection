import threading
import json
import csv
from mqtt_setup_cloud_multi import MQTTSetup
from http_server_multi import HTTPServer

class SourceManager:
    def __init__(self):
        
        self.data_store = {}
        self.dirConfig = json.load(open(file="../util/monitor_dir.json", encoding="utf-8"))
        
    def start_protocol(self, http_check):
        if http_check :
            print("Protocol : HTTP")
            self.protocol = HTTPServer()
            http_thread = threading.Thread(target=self.protocol.app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
            http_thread.daemon = True
            http_thread.start()
            self.topics = self.protocol.topics
            #http_thread = threading.Thread(target=self.protocol.setup_routes)
            #http_thread.start()
    
        else : 
            print("Protocol : MQTT")    #Default Protocol
            self.protocol = MQTTSetup()
            self.protocol.connect()   
            self.topics = self.protocol.topics
        
    def receive_data(self):  
        for topic in self.protocol.topics:       
            self.data_store[topic] = self.protocol.data_store[topic]
            
    def write_duration_csv(self, topic, data):
        with open((self.dirConfig["CSV_PROTOCOL"],topic), mode='a', newline='') as file:  # 'a' for append mode
            writer = csv.writer(file)
            writer.writerow([(data['frame_id']-1), data['payload_size'], data['duration']])