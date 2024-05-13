from flask import Flask, request, Response, jsonify
import json

app = Flask(__name__)

@app.route('/video', methods=['POST'])
def handle_video():
    # Parse JSON data from the request
    data = request.get_json()
    if data:
        # Extract fields from the JSON data
        frame_id = data.get('id')
        frame_base64 = data.get('frame')
        timestamp = data.get('timestamp')

        # Print the received data
        print(f"Received data: ID={frame_id}, Timestamp={timestamp}")
        # Optionally print the length of the frame data if it's too large
        print(f"Frame data length: {len(frame_base64)} characters")

        # Respond that the data was received
        return jsonify({"message": "Data received", "status": 200})
    else:
        # Handle the case where no or invalid JSON data is received
        return jsonify({"error": "Invalid or no JSON data received"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
