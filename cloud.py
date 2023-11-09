import json
import cv2
import numpy as np
import paho.mqtt.client as mqtt
config = json.load(open(file="./util/config.json", encoding="utf-8"))

#----------------------------CV2 SETUP-----------------------------------------#
cv2.namedWindow("stream", cv2.WINDOW_NORMAL)


#----------------------------MQTT SETUP-----------------------------------------#
mqttClient = mqtt.Client()

def on_message(client, userdata, msg):
    image_data = np.frombuffer(msg.payload, dtype=np.uint8)
    image_decode = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    cv2.imshow("stream", image_decode)
    cv2.waitKey(1)

#def on_publish(client, userdata, msg):
#    pass

def initialize_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)        
    mqttClient.on_connect = on_connect
    mqttClient.connect(config["host_address"], config["port"])
    mqttClient.subscribe(config["topic"])
    mqttClient.on_message = on_message
    #mqttClient.on_publish = on_publish
    return mqttClient

########################################################################################

def run():  
    while True:
        mqttClient.loop()
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

def main():
    initialize_mqtt()
    run()

if __name__ == '__main__':
    main()


