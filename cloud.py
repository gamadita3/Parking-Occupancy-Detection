import json
import cv2
import numpy as np
import paho.mqtt.client as mqtt
mqttConfig = json.load(open(file="./util/mqtt_config.json", encoding="utf-8"))

#----------------------------CV2 SETUP-----------------------------------------#
cv2.namedWindow("stream", cv2.WINDOW_NORMAL)


#----------------------------MQTT SETUP-----------------------------------------#
mqtt_client = mqtt.Client()

def on_message(client, userdata, msg):
    '''frame_data = np.frombuffer(msg.payload, dtype=np.uint8)
    frame_decode = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
    cv2.imshow("raw_stream", frame_decode)'''
    
    frames_data = msg.payload.split(b',')
    frames = [cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), 1) for frame in frames_data]
    for frame in frames:
        cv2.imshow("Received Frame", frame)
        #cv2.waitKey(1)

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

########################################################################################

def run():  
    while True:
        mqtt_client.loop()
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

def main():
    initialize_mqtt()
    run()

if __name__ == '__main__':
    main()


