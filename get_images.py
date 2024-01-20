import cv2
import os
import json

frameConfig = json.load(open(file="./util/frame_config.json", encoding="utf-8"))

def show_video():
    image_folder = frameConfig['FOLDER_IMAGES']
    frames = [cv2.imread(os.path.join(image_folder, img)) for img in os.listdir(image_folder) if img.endswith(".jpg")]
    for frame in frames:
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    show_video()
