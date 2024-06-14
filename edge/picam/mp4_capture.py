import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (1920, 1080)})
picam2.configure(video_config)

encoder = H264Encoder(20000000)
output = FfmpegOutput('test.mp4')

picam2.start_recording(encoder, output)
time.sleep(360)
picam2.stop_recording()