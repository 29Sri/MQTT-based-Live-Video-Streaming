import os
import cv2
import argparse
from time import time, sleep
import paho.mqtt.publish as publish

def size(s):
    try:
        width, height = map(int, s.split(','))
        return width, height
    except:
        raise argparse.ArgumentTypeError("Size must be <width,height> in pixel values")

def pause(start, fps):
    """Pause to maintain FPS"""
    stop = time()
    sleep_time = max(0, 1 / fps - (stop - start))
    sleep(sleep_time)

# Arguments
parser = argparse.ArgumentParser(description="MQTT Face Detection Streamer")
parser.add_argument("--broker_ip", help="IP address of your MQTT broker", type=str, default="broker.hivemq.com")
parser.add_argument("--topic", help="Topic to stream the video", type=str, default="live_streaming")
parser.add_argument("--max_fps", help="Maximum FPS desired value", type=int, default=5)
parser.add_argument("--resize", help="Resize image to <width,height>", type=size, default=(128, 128))

args = parser.parse_args()

# Initialize camera
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Unable to access the camera.")
    exit()

print(f"Streaming at {args.max_fps} FPS started...")

while True:
    start_time = time()

    # Capture frame
    ret, frame = camera.read()
    if not ret:
        print("Failed to capture image. Exiting...")
        break

    # Resize the frame and encode it as a JPEG byte array
    resized_frame = cv2.resize(frame, args.resize, interpolation=cv2.INTER_AREA)
    byte_img = cv2.imencode(".jpg", resized_frame)[1].tobytes()

    # Debug: Preview the captured frame in a window
    cv2.imshow("Publisher Preview", resized_frame)
    if cv2.waitKey(1) == 27:  # Press ESC to exit
        break

    # Debug: Check pixel values
    print(f"Sample pixel (center): {resized_frame[resized_frame.shape[0]//2, resized_frame.shape[1]//2]}")
    print(f"Frame min pixel value: {resized_frame.min()}, max pixel value: {resized_frame.max()}")

    # Publish the frame
    try:
        publish.single(args.topic, byte_img, hostname=args.broker_ip)
    except Exception as e:
        print(f"Error sending message: {e}")

    # Pause to maintain FPS
    pause(start_time, args.max_fps)

# Release camera and clean up
camera.release()
cv2.destroyAllWindows()
