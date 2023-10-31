import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import *

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

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (1020, 500))

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
            # Handle the vehicle crossing the line here
            pass

        if is_crossing_line((cx, cy), cy2, offset):
            # Handle the vehicle crossing the other line here
            pass

    # ... (Rest of your code)

    cv2.imshow('frame', frame)

    # ... (Rest of your code)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()