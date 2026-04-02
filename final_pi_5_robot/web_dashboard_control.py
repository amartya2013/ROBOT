import os
import cv2
from flask import Flask, Response
from picamera2 import Picamera2
from gpiozero import Motor, PWMOutputDevice
from time import sleep

# Motor A
motor1 = Motor(forward=26, backward=16)
enable1 = PWMOutputDevice(13)

# Motor B
motor2 = Motor(forward=5, backward=6)
enable2 = PWMOutputDevice(12)


motor3 = Motor(forward=23, backward=22)
enable3 = PWMOutputDevice(19)

motor4 = Motor(forward=17, backward=27)
enable4 = PWMOutputDevice(18)
            
def set_speed(speed):
    enable1.value = speed
    enable2.value = speed
    enable3.value = speed
    enable4.value = speed

def stop_all():
    motor1.stop()
    motor2.stop()
    motor3.stop()
    motor4.stop()
    
def forward(duration):
    motor1.forward()
    motor2.forward()
    motor3.forward()
    motor4.forward()
    set_speed(0.8)
    sleep(duration)
    stop_all()
    
def backward(duration):
    motor1.backward()
    motor2.backward()
    motor3.backward()
    motor4.backward()
    set_speed(0.8)
    sleep(duration)
    stop_all()
    
def right(duration):
    motor1.backward()
    motor2.forward()
    motor3.forward()
    motor4.backward()
    set_speed(0.8)
    sleep(duration)
    stop_all()
    
    
def left(duration):
    motor1.forward()
    motor2.backward()
    motor3.backward()
    motor4.forward()
    set_speed(0.8)
    sleep(duration)
    stop_all()
    
    
app = Flask(__name__)

# --- Config ---
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
FRAME_SIZE = (1400, 800)

# --- Camera setup ---
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": FRAME_SIZE}))
picam2.start()

# --- Command map ---
COMMANDS = {
    "forward": "forward(0.8)",
    "backward": "backward(0.8)",
    "left": "left(0.8)",
    "right": "right(0.8)",
    "stop": "stop_all()"
}


def generate_frames():
    try:
        while True:
            frame_rgb = picam2.capture_array()
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            success, buffer = cv2.imencode('.jpg', frame)
            if not success:
                continue

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                buffer.tobytes() +
                b'\r\n'
            )
    except GeneratorExit:
        pass


# --- Routes ---

@app.route("/")
def home():
    return"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FireBot Remote Control</title>

    <style>
        :root {
            --bg: #0b1220;
            --panel: #111827;
            --accent: #ef4444;
            --accent-glow: rgba(239, 68, 68, 0.6);
            --blue: #3b82f6;
            --text: #e5e7eb;
        }

        body {
            margin: 0;
            font-family: "Segoe UI", Tahoma, sans-serif;
            background: radial-gradient(circle at top, #1f2937, #020617);
            color: var(--text);
        }

        h1 {
            text-align: center;
            padding: 15px;
            letter-spacing: 2px;
            color: var(--accent);
            text-shadow: 0 0 10px var(--accent-glow);
        }

        .dashboard {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            padding: 20px;
        }

        .panel {
            background: var(--panel);
            border-radius: 16px;
            padding: 15px;
            box-shadow: 0 0 25px rgba(0,0,0,0.6);
        }

        .video img {
            width: 100%;
            border-radius: 12px;
            border: 2px solid #1f2937;
        }

        .telemetry {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .stat {
            padding: 10px;
            border-radius: 10px;
            background: #020617;
            display: flex;
            justify-content: space-between;
            font-size: 14px;
        }

        .controls {
            margin-top: 20px;
            display: grid;
            grid-template-columns: repeat(3, 80px);
            gap: 15px;
            justify-content: center;
        }

        button {
            background: #1f2937;
            border: 1px solid #374151;
            color: white;
            font-size: 20px;
            padding: 15px;
            border-radius: 12px;
            cursor: pointer;
            transition: 0.2s;
        }

        button:hover {
            background: var(--blue);
            box-shadow: 0 0 15px var(--blue);
        }

        .stop {
            background: var(--accent);
        }

        .stop:hover {
            box-shadow: 0 0 20px var(--accent-glow);
        }

        .spacer {
            visibility: hidden;
        }

        .status-bar {
            margin-top: 15px;
            padding: 10px;
            background: #020617;
            border-radius: 10px;
            text-align: center;
            font-size: 14px;
        }

        .pulse {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: lime;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 5px lime; }
            50% { box-shadow: 0 0 20px lime; }
            100% { box-shadow: 0 0 5px lime; }
        }
    </style>
</head>

<body>

<h1>🚒 FIREBOT REMOTE CONTROL SYSTEM</h1>

<div class="dashboard">

    <!-- LEFT: VIDEO -->
    <div class="panel video">
        <img src="/video_feed">
        <div class="status-bar" id="status">
            <span class="pulse"></span> System Online
        </div>
    </div>

    <!-- RIGHT: TELEMETRY + CONTROLS -->
    <div class="panel">

        <div class="telemetry">
            <div class="stat"><span>🔥 Temperature</span><span id="temp">72°C</span></div>
            <div class="stat"><span>🔋 Battery</span><span id="battery">85%</span></div>
            <div class="stat"><span>📡 Signal</span><span id="signal">Strong</span></div>
        </div>

        <div class="controls">
            <div class="spacer"></div>
            <button onclick="sendCommand('forward')">⬆</button>
            <div class="spacer"></div>

            <button onclick="sendCommand('left')">⬅</button>
            <button class="stop" onclick="sendCommand('stop')">⏹</button>
            <button onclick="sendCommand('right')">➡</button>

            <div class="spacer"></div>
            <button onclick="sendCommand('backward')">⬇</button>
            <div class="spacer"></div>
        </div>

    </div>

</div>

<script>
function sendCommand(cmd) {
    fetch('/' + cmd)
        .then(res => res.text())
        .then(data => {
            document.getElementById("status").innerHTML =
                "<span class='pulse'></span> " + data;
        });
}

// Keyboard controls
document.addEventListener("keydown", function(e) {
    if (e.key === "w") sendCommand("forward");
    if (e.key === "s") sendCommand("backward");
    if (e.key === "a") sendCommand("left");
    if (e.key === "d") sendCommand("right");
    if (e.key === " ") sendCommand("stop");
});
</script>

</body>
</html>
"""

def generate_frames():

    while True:
        frame_rgb = picam2.capture_array()
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/<action>")
def handle_action(action):
    message = COMMANDS.get(action)
    if message:
        exec(message)  # Replace with GPIO / motor control
        return message
    return "Invalid command", 404


# --- Run app ---
if __name__ == "__main__":
    try:
        app.run(host=HOST, port=PORT, threaded=True)
    finally:
        picam2.stop()
