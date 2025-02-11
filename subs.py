import paho.mqtt.client as mqtt
import cv2
import numpy as np

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, message):
    print(f"Message received: Payload size = {len(message.payload)} bytes")
    nparr = np.frombuffer(message.payload, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is not None and img.size > 0:
        print(f"Decoded image shape: {img.shape}")
        print(f"Sample pixel (center): {img[img.shape[0]//2, img.shape[1]//2]}")
        print(f"Image min pixel value: {img.min()}, max pixel value: {img.max()}")

        # Display the received frame
        cv2.imshow("Received Frame", img)
        cv2.waitKey(1)
    else:
        print("Failed to decode image or empty image data.")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect("broker.hivemq.com", 1883, 60)
client.subscribe("live_streaming")
client.loop_start()

cv2.namedWindow("Received Frame", cv2.WINDOW_NORMAL)

try:
    while True:
        cv2.waitKey(1)
except KeyboardInterrupt:
    print("Exiting...")

cv2.destroyAllWindows()
client.loop_stop()
client.disconnect()
