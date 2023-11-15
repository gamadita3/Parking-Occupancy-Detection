import json
import cv2
import numpy as np
import random
from PIL import Image
import paho.mqtt.client as mqtt
from ultralytics import YOLO
mqttConfig = json.load(open(file="./util/mqtt_config.json", encoding="utf-8"))
frameConfig = json.load(open(file="./util/frame_config.json", encoding="utf-8"))

#----------------------------CV2 SETUP-----------------------------------------#
cv2.namedWindow("stream", cv2.WINDOW_NORMAL)


#----------------------------MQTT SETUP-----------------------------------------#
mqtt_client = mqtt.Client()
received_frame = None

def on_message(client, userdata, msg):
    global received_image
    frame_data = np.frombuffer(msg.payload, dtype=np.uint8)
    frame_decode = cv2.imdecode(frame_data, cv2.IMREAD_UNCHANGED)
    #print(f'frame: {frame_decode}')
    cv2.imshow("raw_stream", frame_decode)
    #cv2.waitKey(1)
    received_frame = frame_decode
    

#def on_publish(client, userdata, msg):
#    pass

def initialize_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)        
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(mqttConfig["HOST_ADDRESS"], mqttConfig["PORT"])
    mqtt_client.subscribe(mqttConfig["TOPIC"])
    mqtt_client.on_message = on_message
    #mqtt_client.on_publish = on_publish
    return mqtt_client

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

def inference(frame):
    global received_image
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
    cv2.imshow("inferenced", frame) 
    received_image = None

########################################################################################

def run():  
    while True:
        mqtt_client.loop()
        if received_image is not None:
            inference(received_image)
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

def main():
    initialize_mqtt()
    run()

if __name__ == '__main__':
    main()


