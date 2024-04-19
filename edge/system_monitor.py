import csv
import psutil
import time
import json

class SystemMonitor:
    def __init__(self, flag):
        self.dirconfig = self.load_config('../util/dir_config.json')
        self.video_run_flag = flag
        
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def start_monitoring(self):
        print("Starting CPU and RAM usage capture")
        with open(self.dirconfig["SYSTEM_MONITOR"], mode='w', newline='') as file:
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
