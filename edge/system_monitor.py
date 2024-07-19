import csv
import psutil
import datetime
import json

class SystemMonitor:
    def __init__(self, flag):
        self.dirconfig = self.load_config('../util/monitor_dir.json')
        self.video_run_flag = flag
        if self.video_run_flag :
            print("Initialize monitor CPU and RAM usage")
            with open(self.dirconfig["SYSTEM_MONITOR_EDGE"], mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Time', 'CPU Usage (%)', 'RAM Usage (%)', 'RAM Used (MB)'])
        
        
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def start_monitoring(self):
        print("Starting CPU and RAM usage capture monitor")
        while self.video_run_flag:
            with open(self.dirconfig["SYSTEM_MONITOR_EDGE"], mode='a', newline='') as file:
                cpu_percent = psutil.cpu_percent(interval=0.5)
                virtual_memory = psutil.virtual_memory()
                ram_percent = virtual_memory.percent
                ram_used = virtual_memory.used / (1024 ** 2)
                current_time = datetime.datetime.now()
                formatted_time = current_time.strftime("%d/%m/%y %H:%M:%S.%f")[:-3]
                writer = csv.writer(file)
                writer.writerow([formatted_time, cpu_percent, ram_percent, ram_used])

    def stop_monitoring(self):
        self.video_run_flag = False
