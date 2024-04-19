import json
import time
import cv2
import random
import numpy as np
import paho.mqtt.client as mqtt
from ultralytics import YOLO
mqttConfig = json.load(open(file="./util/mqtt_config.json", encoding="utf-8"))
frameConfig = json.load(open(file="./util/frame_config.json", encoding="utf-8"))

#----------------------------MQTT SETUP-----------------------------------------#
mqtt_client = mqtt.Client()

#def on_message(client, userdata, msg):
#    pass

def on_publish(client, userdata, msg):
    #print(f"pub {msg}")
    pass

def initialize_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)        
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(mqttConfig["HOST_ADDRESS"], mqttConfig["PORT"])
    #mqtt_client.subscribe(config["topic"])
    mqtt_client.loop_start()
    #mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish
    return mqtt_client

def publish_frame(frame):
    #print(f'Publishing frame')
    _, _frameEncoded = cv2.imencode(".jpg", frame)
    mqtt_client.publish(mqttConfig["TOPIC"], _frameEncoded.tobytes())

def publish_batches(frames):
    for frame in frames:
        _, _frameEncoded = cv2.imencode(".jpg", frame) 
        frames_batch = b','.join(_frameEncoded.tobytes())
    mqtt_client.publish(mqttConfig["TOPIC"], frames_batch)

#----------------------------CV2 SETUP-----------------------------------------#
cap = cv2.VideoCapture(0)
def setup_camera():
    cap.set(3, frameConfig["FRAME_WIDTH"])
    cap.set(4, frameConfig["FRAME_HEIGHT"])
    return cap

def collect_frames():   
    '''print(f'Capturing 100 frame with 5 fps')
    frames = [] 
    for _ in range(100):
        ret, frame = cap.read()
        if not ret:
            raise Exception("Could not read from camera.")
        frames.append(frame)
        time.sleep(0.2)
    return frames'''
    
    print(f'Start capture images for {frameConfig["CAPTURE_TIME"]} seconds')
    frames = []
    _startCapture = time.time()
    #print(_startCapture)
    while (time.time() - _startCapture) < frameConfig["CAPTURE_TIME"]:
        ret, frame = cap.read()
        if not ret:
            raise Exception("Could not read from camera.")
        #print(f'frame : {frame}')
        #publish_frame(frame)
        frames.append(frame)
        time.sleep(frameConfig["CAPTURE_DELAY"])
    _totalTime = time.time() - _startCapture
    print(f'Total time: {_totalTime}')
    print(f'Total frames: {len(frames)}')
    return frames
    
        

#----------------------------INFERENCE-----------------------------------------#
inference = False
coco_file = open("./util/coco.txt", "r")
class_list = coco_file.read().split("\n")
coco_file.close()

model = YOLO("./util/yolov8n.pt", "v8")
detection_colors = []
for i in range(len(class_list)):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    detection_colors.append((b, g, r))

def inference(frames):
    global motion_detected
    _newFrames = []
    _countFrame = 0
    print("Start Inference !!")  
    for frame in frames:
        _countFrame += 1
        detecting = model.predict(source=[frame], conf=0.45, save=False, imgsz=320)       
        DP = detecting[0].numpy() 
        print(detecting)
        '''if len(DP) != 0:
            for i in range(len(detecting[0])):
                print(i)

                boxes = detecting[0].boxes
                box = boxes[i]  # returns one box
                clsID = box.cls.numpy()[0]
                conf = box.conf.numpy()[0]
                bb = box.xyxy.numpy()[0]

                cv2.rectangle(
                    frame,
                    (int(bb[0]), int(bb[1])),
                    (int(bb[2]), int(bb[3])),
                    detection_colors[int(clsID)],
                    3,
                )

                # Display class name and confidence
                font = cv2.FONT_HERSHEY_COMPLEX
                cv2.putText(
                    frame,
                    class_list[int(clsID)] + " " + str(round(conf, 3)) + "%",
                    (int(bb[0]), int(bb[1]) - 10),
                    font,
                    1,
                    (255, 255, 255),
                    2,
                )'''
        _newFrames.append(frame)
        print(f'Total frames: {len(frames)}')
        print(f'Inference frame : {_countFrame}')
    _countPub = 0
    for frame in _newFrames:
        _countPub += 1
        print(f'Publishing image {_countPub} of {len(_newFrames)}')
        publish_frame(frame)
        #time.sleep(0.1)
    #return frame

#----------------------------MOTION DETECTION-----------------------------------------#
motion_detected = False
start_time = time.time()

def motion_detection(old_frame, new_frame):
        global motion_detected
        global start_time
        old_frame_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        new_frame_gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
        frame_diff = cv2.absdiff(old_frame_gray, new_frame_gray)
        _, thresh = cv2.threshold(frame_diff, 40, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:           
            if cv2.contourArea(contour) > 100: #threshold sensitivity set 100
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(new_frame, (x, y), (x + w, y + h), (10, 10, 255), 2)
                motion_detected = True
                start_time = time.time()      
        if motion_detected:
            print("Motion Detected !!")

########################################################################################

def run():   
    global motion_detected
    global start_time
    ret, frame_initial = cap.read()  
    while True:       
        try:
            if  motion_detected:             
                frames = collect_frames() 
                publish_batches(frames)            
                #inference(frames)         //disable inference     
                '''if (time.time() - start_time) > 10:
                    motion_detected = False
                    ret, frame_initial = cap.read()
                    print("Reset detection")'''
                motion_detected = False
                ret, frame_initial = cap.read()
            else:   
                ret, frame = cap.read()
                if not ret:
                    raise Exception("Could not read from camera.")
                #print("Motion Detected false") 
                motion_detection(frame_initial, frame)  
        except Exception as error:
            print("Error:", error)     

def main():
    initialize_mqtt()
    setup_camera()
    run()

if __name__ == '__main__':
    main()
    

