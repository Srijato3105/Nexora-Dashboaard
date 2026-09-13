import cv2
from flask import Flask, render_template, Response, request, jsonify
import datetime

app = Flask(__name__)

# Initialize the hardware camera (0 is the default system camera)
camera = cv2.VideoCapture(0)

def generate_frames():
    """Reads frames from the camera and encodes them for web streaming."""
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            # Yield the frame for the multipart stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Serves the main dashboard UI from the templates folder."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Provides the continuous video stream to the frontend image tag."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/dispatch', methods=['POST'])
def dispatch_task():
    """Receives and processes dispatch commands from the frontend operator panel."""
    data = request.get_json()
    
    # Extract telemetry data sent by the JavaScript fetch request
    task_type = data.get('task_type', 'Unknown')
    destination = data.get('destination', 'Unknown')
    item = data.get('item', 'None')
    priority = data.get('priority', 'Normal')
    
    # Log the mission details to the server console
    print("\n--- New Nexora Mission Dispatched ---")
    print(f"Task Classification: {task_type}")
    print(f"Target Destination: {destination}")
    print(f"Payload/Subject: {item}")
    print(f"Urgency: {priority}")
    print("-------------------------------------\n")
    
    # Future integration: TCP/IP or Serial communication to the ESP32 navigation module 
    # would be triggered here to initiate physical movement.
    
    # Return a success response with a timestamp back to the frontend
    return jsonify({
        "status": "success", 
        "message": "Mission parameters received and logged by the control server.",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    # Binds to 0.0.0.0 to allow access from tablets or other devices on the local network
    app.run(host='0.0.0.0', port=5000, debug=True)
