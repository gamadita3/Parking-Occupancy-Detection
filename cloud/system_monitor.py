import csv
import psutil
import time
import json

class SystemMonitor:
    def __init__(self, flag):
        self.dirConfig = self.load_config('../util/monitor_dir.json')
        self.video_run_flag = flag
        
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def start_monitoring(self):
        print("Starting CPU and RAM usage capture")
        with open(self.dirConfig["SYSTEM_MONITOR_CLOUD"], mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'CPU Usage (%)', 'RAM Usage (%)', 'RAM Used (MB)'])
            while self.video_run_flag:
                cpu_percent = psutil.cpu_percent(interval=0.5)
                virtual_memory = psutil.virtual_memory()
                ram_percent = virtual_memory.percent
                ram_used = virtual_memory.used / (1024 ** 2)  # Convert from bytes to MB
                writer.writerow([time.time(), cpu_percent, ram_percent, ram_used])
        print("Capture of CPU and RAM usage stopped")

    def stop_monitoring(self):
        self.video_run_flag = False
    
    def initial_monitor_protocol(self):
        with open(self.dirConfig["PROTOCOL_DURATION"], mode='w', newline='') as protocolFile:  
            writer = csv.writer(protocolFile)
            writer.writerow(['Frame_ID', 'Payload_size', 'Duration'])
            
    def monitor_protocol(self, frame_id, payload, duration):
        with open(self.dirConfig["PROTOCOL_DURATION"], mode='a', newline='') as protocolFile:  
            writer = csv.writer(protocolFile)
            writer.writerow([frame_id, payload, duration])
    
