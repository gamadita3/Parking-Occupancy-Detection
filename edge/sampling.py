import time
from mqtt_setup_edge import MQTTSetup


class Sampling:
    def __init__(self):
        self.samplingConfig = self.load_config('../util/sampling_config.json')
        self.protocol = MQTTSetup()
        self.last_sent_time = time.time() - 300  
        
    def save_sample(self, frame, currentTime):       
        if currentTime - self.last_sent_time >= self.samplingConfig["SAMPLE_INTERVAL"] :
                self.protocol.send_sample(frame)
                self.last_sent_time = time.time()