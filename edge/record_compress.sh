#!/bin/bash

# Constants for video recording
RECORDING_TIME_SECONDS=43200
FRAME_RATE=30
FRAME_WIDTH=1280
FRAME_HEIGHT=960
OUTPUT_FILENAME='17-07-24.mp4'

# Start recording using ffmpeg with real-time compression
echo "Recording started..."
ffmpeg -f v4l2 -framerate $FRAME_RATE -video_size ${FRAME_WIDTH}x${FRAME_HEIGHT} -i /dev/video0 -t $RECORDING_TIME_SECONDS -vcodec libx264 -crf 27 -preset veryfast $OUTPUT_FILENAME
echo "Recording finished. Video saved as: $OUTPUT_FILENAME"
