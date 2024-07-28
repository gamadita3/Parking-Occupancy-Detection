import streamlit as st
import traceback
import json
import time
import cv2
import numpy
from source_manager_multi import SourceManager
from display_setup import DisplaySetup
from object_detection import Inference
from system_monitor import SystemMonitor

def main():
    # Streamlit sidebar options
    st.sidebar.title("Control Panel")
    inference_enabled = st.sidebar.checkbox("Enable Inference", value=False)
    http_check = st.sidebar.checkbox("Use HTTP Protocol", value=True)

    # Setup objects
    display = DisplaySetup()
    inference = Inference()
    system_monitor = SystemMonitor(True) 
    source = SourceManager()
    source.start_protocol(http_check)
    system_monitor.initial_monitor_protocol() #protocol monitoring
    latest_frame_id = "-" #protocol monitoring
    start_time = None #protocol monitoring
    monitor_limit = False #protocol monitoring

    # Placeholder for video frame and detection counts
    frame_placeholders = {}
    stats_placeholders = {}

    while True:
        try:
            source.receive_data()
            
            #! LIMITER MONITOR PROTOCOL 
            if source.data_store['PSM-edge1']['frame_id'] == 2:
                print('MONITOR PROTOCOL START !!')
                start_time = time.time()  # Start the timer when frame_id reaches 2
                monitor_limit = True
            if monitor_limit and (time.time() - start_time) > 600:  # 600 seconds = 10 minutes
                monitor_limit = False
                print('MONITOR PROTOCOL STOPPED !!')
                break  # Stop the loop after 1 minutes
            #!!!!!!!!!!!!!!!!!!!!!!!!
            
            try:
                for topic in source.topics:
                    if topic not in frame_placeholders:
                            print(f"Set placeholders for topic {topic}")
                            frame_placeholders[topic] = st.empty()
                            stats_placeholders[topic] = st.empty()
                            blank_frame = numpy.zeros((720, 1280, 3), dtype=numpy.uint8)
                            blank_text = f"<div style='text-align: center'>Topic {topic} | No data available</div>"
                            frame_placeholders[topic].image(blank_frame, channels="BGR", caption=f"{topic} | No image")
                            stats_placeholders[topic].markdown(blank_text, unsafe_allow_html=True)
                            st.markdown('<div style="margin-bottom: 30px;"></div>', unsafe_allow_html=True)
                               
                    if (source.data_store[topic]['frame_id'] != "-"):              
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
                            
                        if monitor_limit and latest_frame_id != source.data_store[topic]['frame_id']:
                            latest_frame_id = source.data_store[topic]['frame_id']
                            system_monitor.monitor_protocol(source.data_store[topic]['frame_id'], source.data_store[topic]['payload_size'], source.data_store[topic]['duration']) #protocol monitoring  
                        
                        frame_placeholders[topic].image(frame, channels="BGR", caption=f"{topic} | {source.data_store[topic]['time']}")
                        stats_text = f"<div style='text-align: center'>Topic {topic} | Total Detections: {occupied_detection + empty_detection} | Empty: {empty_detection} | Occupied: {occupied_detection}</div>"
                        stats_placeholders[topic].markdown(stats_text, unsafe_allow_html=True)
                        st.markdown('<div style="margin-bottom: 50px;"></div>', unsafe_allow_html=True)
                        
                        height, width = source.data_store[topic]['frame'].shape[:2]
                        #print(f"Received frame with resolution: {width}x{height} for topic {topic}")
                        #print(f"Total Detection {(occupied_detection + empty_detection)} | Empty {empty_detection} | Occupied {occupied_detection}\n")
                    else:
                        continue
            except Exception as e:
                continue
        except Exception as e:
            st.error(f"Error: {traceback.format_exc()}")
            break

if __name__ == '__main__':
    if 'run' not in st.session_state:
        st.session_state.run = False
    main()
