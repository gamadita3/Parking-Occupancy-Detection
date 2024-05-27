import streamlit as st
import traceback
import json
import time
import cv2
from source_manager_multi import SourceManager
from display_setup import DisplaySetup
from object_detection import Inference
from system_monitor import SystemMonitor

# Load configuration
dirConfig = json.load(open("../util/dir_config.json", encoding="utf-8"))

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
    frame_placeholders = {}
    stats_placeholders = {}
    
    if run_button:
        st.session_state.run = True

    if stop_button:
        st.session_state.run = False

    start_time = None

    while True:
        try:
            source.receive_data()
            try:
                for topic in source.topics:
                    if source.data_store[topic]['frame'] is not None:                  
                        if topic not in frame_placeholders:
                            frame_placeholders[topic] = st.empty()
                            stats_placeholders[topic] = st.empty()
                            
                        if inference_enabled:
                            print(f"Perform inference topic {topic} frame id {source.data_store[topic]['frame_id']}")
                            inference.detect(source.data_store[topic]['frame'])
                            frame = inference.frame
                            occupied_detection = inference.total_occupied_detection
                            empty_detection = inference.total_empty_detection
                        else :
                            frame = source.data_store[topic]['frame']
                            occupied_detection = source.data_store[topic]['occupied_detection']
                            empty_detection = source.data_store[topic]['empty_detection']
                            
                        frame_placeholders[topic].image(frame, channels="BGR", caption="Live Video Stream")
                        stats_text = f"Topic {topic} | total Detections: {occupied_detection + empty_detection} | Empty: {empty_detection} | Occupied: {occupied_detection}"
                        stats_placeholders[topic].text(stats_text)
                        
                        height, width = source.data_store[topic]['frame'].shape[:2]
                        print(f"Received frame with resolution: {width}x{height} for topic {topic}")
                        print(f"Total Detection {(occupied_detection + empty_detection)} | Empty {empty_detection} | Occupied {occupied_detection}\n")
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
