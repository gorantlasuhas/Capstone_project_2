import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import *
import time

model = YOLO('yolov8s.pt')

# Function to check if a point crosses a line
def is_crossing_line(point, cy, offset):
    return abs(point[1] - cy) < offset

video_file = "WhatsApp Video 2023-10-29 at 12.33.10_5aa8e9bb.mp4"
cap = cv2.VideoCapture(video_file)

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")

# Define a list of COCO classes that correspond to vehicles
vehicle_classes = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']

tracker = Tracker()
cy1 = 194
cy2 = 220
offset = 6

# Counter variables
counter1 = 0
counter2 = 0
vehicledown = {}
vehicleup = {}

# Video writer setup
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_filename = "output_video.mp4"
output_video = cv2.VideoWriter(output_filename, fourcc, 20.0, (1020, 500))

start_time = time.time()
output_interval = 20  # in seconds

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (1020, 500))

    # Draw horizontal lines
    cv2.line(frame, (0, cy1), (1020, cy1), (0, 255, 0), 2)
    cv2.line(frame, (0, cy2), (1020, cy2), (0, 255, 255), 2)

    results = model.predict(frame)
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")
    vehicle_list = []

    for index, row in px.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])
        d = int(row[5])

        c = class_list[d]
        if c in vehicle_classes:
            vehicle_list.append([x1, y1, x2, y2])

    bbox_id = tracker.update(vehicle_list)
    for bbox in bbox_id:
        x1, y1, x2, y2, id = bbox
        cx = int(x1 + x2) // 2
        cy = int(y1 + y2) // 2
        cv2.circle(frame, (cx, cy), 4, (255, 0, 255), -1)

        # Check if the vehicle has crossed the lines
        if is_crossing_line((cx, cy), cy1, offset):
            if id not in vehicledown:
                vehicledown[id] = True
                counter1 += 1

        if is_crossing_line((cx, cy), cy2, offset):
            if id not in vehicleup:
                vehicleup[id] = True
                counter2 += 1

    # Display counters
    cv2.putText(frame, f"Down: {counter1}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Up: {counter2}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow('frame', frame)
    
    # Write frame to output video
    output_video.write(frame)

    current_time = time.time()
    elapsed_time = current_time - start_time

    # Check if 20 seconds have passed to create a new output video
    if elapsed_time >= output_interval:
        output_video.release()
        print(f"Output video saved as {output_filename}")
        start_time = time.time()

        # Create a new output video
        output_filename = f"output_video_{int(elapsed_time // output_interval)}.mp4"
        output_video = cv2.VideoWriter(output_filename, fourcc, 20.0, (1020, 500))
        
        # Reset counters and dictionaries
        counter1 = 0
        counter2 = 0
        vehicledown = {}
        vehicleup = {}

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
output_video.release()
cv2.destroyAllWindows()
