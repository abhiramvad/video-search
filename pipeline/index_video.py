import cv2
import sqlite3
from datetime import datetime
import tensorflow as tf
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import pytesseract

# Load the MobileNetV2 model
model = MobileNetV2(weights="imagenet")


# Function to detect objects in a frame
def detect_objects(frame):
    # Resize the frame to the input size of the model
    frame = cv2.resize(frame, (224, 224))

    # Preprocess the frame for model input
    frame = img_to_array(frame)
    frame = np.expand_dims(frame, axis=0)
    frame = preprocess_input(frame)

    # Make predictions using the model
    predictions = model.predict(frame)
    decoded_predictions = decode_predictions(predictions, top=5)[0]

    detected_objects = [label for (_, label, _) in decoded_predictions]
    print(detected_objects)
    return detected_objects


# Function to process video frames and collect object data
def process_video(video_file, db_file):
    cap = cv2.VideoCapture(video_file)
    # frame_rate = 30  # Extract one frame per second
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create a table to store object data with timestamps
    cursor.execute('''CREATE TABLE IF NOT EXISTS video_objects
                      (frame_number INTEGER PRIMARY KEY, timestamp TEXT, objects TEXT)''')

    current_frame = 0
    frame_number = 0

    while current_frame < total_frames:
        ret, frame = cap.read()
        if not ret:
            break

        # Calculate the timestamp based on frame number and frame rate
        # timestamp_seconds = frame_number / frame_rate
        # print(timestamp_seconds)
        # timestamp = str(datetime.utcfromtimestamp(timestamp_seconds))

        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
        print(timestamp)

        # Detect objects in the frame
        detected_objects = detect_objects(frame)

        # Convert the detected objects to a comma-separated string
        objects_str = ", ".join(detected_objects)
        print(frame_number,timestamp,objects_str)
        # Insert object data into the database
        cursor.execute("INSERT INTO video_objects VALUES (?, ?, ?)", (frame_number, timestamp, objects_str))
        conn.commit()

        current_frame += 1
        frame_number += 1

    cap.release()
    conn.close()

    print(f"Video processing complete. {total_frames} frames processed.")


if __name__ == "__main__":
    video_file = "data/wildlife.mp4"  # Replace with your video file
    db_file = "../video_objects_v2.db"  # SQLite database file

    process_video(video_file, db_file)
