import cv2
import os
import json

frameConfig = json.load(open(file="./util/frame_config.json", encoding="utf-8"))

def show_images():
    image_folder = frameConfig['FOLDER_IMAGES']
    frames = [cv2.imread(os.path.join(image_folder, img)) for img in os.listdir(image_folder) if img.endswith(".jpg")]
    for frame in frames:
        cv2.imshow('Image', frame)
        cv2.waitKey(30)  # Display each frame for 30ms before moving to the next
    cv2.destroyAllWindows()

if __name__ == "__main__":
    show_images()
