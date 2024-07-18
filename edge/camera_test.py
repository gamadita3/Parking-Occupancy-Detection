import cv2
import time

def check_camera():
    # Attempt to open the camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return False

    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)

    # Set camera FPS
    cap.set(cv2.CAP_PROP_FPS, 30)

    print("Camera is connected.")
    return cap

def show_preview_and_count_fps(cap):
    # Initialize variables for FPS calculation
    frame_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Display the frame
        cv2.imshow('Camera Preview', frame)
        frame_count += 1

        # Calculate the elapsed time
        elapsed_time = time.time() - start_time
        if elapsed_time > 1.0:
            # Calculate FPS
            fps = frame_count / elapsed_time
            print(f"FPS: {fps:.2f}")
            frame_count = 0
            start_time = time.time()

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    cap = check_camera()
    if cap:
        show_preview_and_count_fps(cap)
