import json
import time
import cv2
import random
import numpy as np
import paho.mqtt.client as mqtt
from ultralytics import YOLO
config = json.load(open(file="./util/config.json", encoding="utf-8"))

#----------------------------MQTT SETUP-----------------------------------------#
mqttClient = mqtt.Client()

#def on_message(client, userdata, msg):
#    pass

def on_publish(client, userdata, msg):
    print(f"pub {msg}")
    pass

def initialize_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)        
    mqttClient.on_connect = on_connect
    mqttClient.connect(config["host_address"], config["port"])
    #mqttClient.subscribe(config["topic"])
    mqttClient.loop_start()
    #mqttClient.on_message = on_message
    mqttClient.on_publish = on_publish
    return mqttClient

def publish_image(image):
    print("Publishing image")
    _, frame_encoded = cv2.imencode(".jpg", image)
    mqttClient.publish(config["topic"], frame_encoded.tobytes())

#----------------------------CV2 SETUP-----------------------------------------#
cap = cv2.VideoCapture(0)
def setup_camera():
    cap.set(3, config["frame_width"])
    cap.set(4, config["frame_height"])
    return cap

def collect_frames():
    print("Capturing 100 frame with 5 fps")
    frames = [] 
    for _ in range(100):
        ret, frame = cap.read()
        if not ret:
            raise Exception("Could not read from camera.")
        frames.append(frame)
        time.sleep(0.2)
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
    new_frames = []
    print("Start Inference !!")  
    for frame in frames:
        motion_detected = False
        detecting = model.predict(source=[frame], conf=0.45, save=False, imgsz=320)       
        DP = detecting[0].numpy() 
        print(DP)
        if len(DP) != 0:
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
                )
        new_frames.append(frame)
    for frame in new_frames:
        publish_image(frame)
        time.sleep(0.2)
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
                print("Motion Detected !!") 
                start_time = time.time()      

########################################################################################

def run():   
    global motion_detected
    global start_time
    ret, frame_initial = cap.read()  
    while True:       
        try:
            if  motion_detected:             
                frames = collect_frames()             
                inference(frames)              
                '''if (time.time() - start_time) > 10:
                    motion_detected = False
                    ret, frame_initial = cap.read()
                    print("Reset detection")'''
                ret, frame_initial = cap.read()
            else:   
                ret, frame = cap.read()
                if not ret:
                    raise Exception("Could not read from camera.")
                print("Motion Detected false") 
                motion_detection(frame_initial, frame)  
        except Exception as error:
            print("Error:", error)     

def main():
    initialize_mqtt()
    setup_camera()
    run()

if __name__ == '__main__':
    main()
    

