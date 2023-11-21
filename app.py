import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS  # Import Flask-CORS


app = Flask(__name__)
CORS(app)  # Enable CORS for your Flask app (allow all origins, * for development)

# Function to convert timestamp strings to seconds
def timestamp_to_seconds(timestamp_str):
    try:
        # Attempt to parse the timestamp with milliseconds
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            # If parsing with milliseconds fails, parse without milliseconds
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("Invalid timestamp format")

    return (timestamp - datetime(1970, 1, 1)).total_seconds()


# Function to fetch data from the SQLite database
def fetch_data_from_db(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Query to select all rows from the video_objects table
    cursor.execute("SELECT timestamp, objects FROM video_objects")
    rows = cursor.fetchall()

    data = []

    # Create a list of dictionaries with timestamps and objects
    for row in rows:
        timestamp, objects = row
        data.append({"timestamp": timestamp, "objects": objects})

    conn.close()

    return data

@app.route('/video', methods=['GET'])
def get_video():
    video_file = "pipeline/data/wildlife.mp4"  # Adjust the path to your video file

    return send_file(video_file, mimetype='video/mp4')

@app.route('/video_data', methods=['GET'])
def get_video_data():
    db_file = "video_objects_v2.db"  # Replace with your SQLite database file path
    keyword = request.args.get('keyword')

    # Fetch data from the database
    data = fetch_data_from_db(db_file)

    if keyword:
        # Filter data based on the keyword
        response_data = [item for item in data if keyword.lower() in item['objects'].lower()]
        filtered_data = []
        for item in response_data:
            if keyword.lower() in item['objects'].lower():
                timestamp_seconds = item['timestamp']
                filtered_data.append({"time": timestamp_seconds,"color": '#ffc837', "title": keyword})

        return jsonify(filtered_data[:5])
    else:
        return jsonify(data)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
