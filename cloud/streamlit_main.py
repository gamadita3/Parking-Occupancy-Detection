import streamlit as st
import traceback
import json
import time
import cv2
from source_manager import SourceManager
from display_setup import DisplaySetup
from object_detection import Inference
from system_monitor import SystemMonitor

def main():
    # Streamlit sidebar options
    st.sidebar.title("Control Panel")
    inference_enabled = st.sidebar.checkbox("Enable Inference", value=False)
    http_check = st.sidebar.checkbox("Use HTTP Protocol", value=False)
    run_button = st.sidebar.button("Run")
    stop_button = st.sidebar.button("Stop")

    # Setup objects
    display = DisplaySetup()
    inference = Inference()
    system_monitor = SystemMonitor(True)
    source = SourceManager()
    source.start_protocol(http_check)

    # Placeholder for video frame and detection counts
    frame_placeholder = st.empty()
    stats_placeholder = st.empty()
    
    if run_button:
        st.session_state.run = True

    if stop_button:
        st.session_state.run = False

    start_time = None

    while st.session_state.get('run', False):
        try:
            source.receive_data()
            try:
                if source.frame_check and source.frame is not None:                  
                    if inference_enabled:
                        print(f"Perform inference frame id {source.frame_id}")
                        inference.detect(source.frame)
                        frame = inference.frame
                        occupied_detection = inference.total_occupied_detection
                        empty_detection = inference.total_empty_detection
                    else :
                        frame = source.frame
                        occupied_detection = source.occupied_detection
                        empty_detection = source.empty_detection
                        
                    
                    frame_placeholder.image(frame, channels="BGR", caption="Live Video Stream")
                            
                    height, width = source.frame.shape[:2]
                    print(f"Received frame with resolution: {width}x{height}")
                    print(f"Total Detection {(occupied_detection + empty_detection)} | Empty {empty_detection} | Occupied {occupied_detection}\n")
                    
                    # Display detection stats
                    stats_text = f"Total Detections: {occupied_detection + empty_detection} | Empty: {empty_detection} | Occupied: {occupied_detection}"
                    stats_placeholder.text(stats_text)
                    
                    source.frame_check = False
                else:
                    continue
            except:
                continue

        except Exception as e:
            st.error(f"Error: {traceback.format_exc()}")
            break

if __name__ == '__main__':
    if 'run' not in st.session_state:
        st.session_state.run = False
    main()
