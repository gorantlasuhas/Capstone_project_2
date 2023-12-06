from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import *
import uuid
import os

app = Flask(__name__)
CORS(app) 
model = YOLO('yolov8s.pt')

# Function to check if a point crosses a line
def is_crossing_line(point, cy, offset):
    return abs(point[1] - cy) < offset

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")

# Define a list of COCO classes that correspond to vehicles
vehicle_classes = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']

tracker = Tracker()

def generate_frames(video_file_path):
    cap = cv2.VideoCapture(video_file_path)

    cy1 = 194
    cy2 = 220
    offset = 6

    # Counter variables
    counter1 = 0
    counter2 = 0
    vehicledown = {}
    vehicleup = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (1020, 500))

        # Process the frame using the YOLO model
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

        # Track vehicles using the tracker
        bbox_id = tracker.update(vehicle_list)
        for bbox in bbox_id:
            x1, y1, x2, y2, id = bbox
            cx = int(x1 + x2) // 2
            cy = int(y1 + y2) // 2

            # Check if the vehicle has crossed the lines
            if is_crossing_line((cx, cy), cy1, offset):
                if id not in vehicledown:
                    vehicledown[id] = True
                    counter1 += 1

            if is_crossing_line((cx, cy), cy2, offset):
                if id not in vehicleup:
                    vehicleup[id] = True
                    counter2 += 1

        # Draw counters on the frame
        cv2.putText(frame, f"Down: {counter1}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Up: {counter2}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # Encode the frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/process_video', methods=['POST'])
def process_video_route():
    try:
        # Get the uploaded file from the request
        video_file = request.files['video']

        # Check if the file is available
        if not video_file:
            return jsonify({"error": "No video file uploaded"})

        # Generate a unique filename using uuid
        filename = f"temp_video_{uuid.uuid4().hex}.mp4"
        video_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(video_file_path)

        return Response(generate_frames(video_file_path), mimetype='multipart/x-mixed-replace; boundary=frame',
                        headers={'filename': filename})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)

