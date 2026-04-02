
import cv2
from flask import Flask, Response, jsonify
from picamera2 import Picamera2
from gpiozero import Motor, PWMOutputDevice
from ultralytics import YOLO
from time import sleep
import threading
import os
from gpiozero import Button


SOUND_PIN = 15

sound_sensor = Button(SOUND_PIN, pull_up=False)



# --- YOLO Model ---
model = YOLO("yolov8n.pt")

# --- Shared state ---
person_detected = False
detection_enabled = False   # off by default
detection_lock = threading.Lock()

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
    motor1.forward(); motor2.forward(); motor3.forward(); motor4.forward()
    set_speed(0.8); sleep(duration); stop_all()

def backward(duration):
    motor1.backward(); motor2.backward(); motor3.backward(); motor4.backward()
    set_speed(0.8); sleep(duration); stop_all()

def right(duration):
    motor1.backward(); motor2.forward(); motor3.forward(); motor4.backward()
    set_speed(0.8); sleep(duration); stop_all()

def left(duration):
    motor1.forward(); motor2.backward(); motor3.backward(); motor4.forward()
    set_speed(0.8); sleep(duration); stop_all()


app = Flask(__name__)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
FRAME_SIZE = (1400, 800)

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": FRAME_SIZE}))
picam2.start()

COMMANDS = {
    "forward": "forward(0.8)",
    "backward": "backward(0.8)",
    "left": "left(0.8)",
    "right": "right(0.8)",
    "stop": "stop_all()"
}


def generate_frames():
    global person_detected, detection_enabled
    while True:
        frame_rgb = picam2.capture_array()
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        with detection_lock:
            enabled = detection_enabled

        if enabled:
            # Run YOLO detection
            results = model(frame, verbose=False)
            found_person = False

            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    if model.names[cls] == "person":
                        found_person = True
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = float(box.conf[0])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f"PERSON {conf:.0%}", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            with detection_lock:
                person_detected = found_person
        else:
            # Detection off — clear state and overlay a label
            with detection_lock:
                person_detected = False
            cv2.putText(frame, "Detection OFF", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)

        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            continue

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            buffer.tobytes() +
            b'\r\n'
        )


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/detection_status')
def detection_status():
    with detection_lock:
        return jsonify({"person_detected": person_detected, "detection_enabled": detection_enabled})

@app.route('/sound_status')
def sound_status():
    return jsonify(sound_sensor.is_pressed)


@app.route('/toggle_detection', methods=['POST'])
def toggle_detection():
    global detection_enabled
    with detection_lock:
        detection_enabled = not detection_enabled
        state = detection_enabled
    return jsonify({"detection_enabled": state})


@app.route("/<action>")
def handle_action(action):
    if action in ("video_feed", "detection_status", "toggle_detection", "favicon.ico"):
        return "Not found", 404
    message = COMMANDS.get(action)
    if message:
        exec(message)
        return message
    return "Invalid command", 404


@app.route("/")
def home():
    return """<!DOCTYPE html>
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
 
        /* Person detection card */
        .person-card {
            padding: 14px 10px;
            border-radius: 10px;
            background: #020617;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
            border: 2px solid transparent;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
 
        .person-card.detected {
            border-color: #22c55e;
            box-shadow: 0 0 14px rgba(34, 197, 94, 0.5);
        }
 
        .person-card.clear {
            border-color: #374151;
        }
 
        .person-badge {
            font-weight: bold;
            font-size: 13px;
            padding: 4px 10px;
            border-radius: 20px;
            transition: background 0.3s, color 0.3s;
        }
 
        .person-badge.detected {
            background: #22c55e;
            color: #000;
        }
 
        .person-badge.clear {
            background: #374151;
            color: #9ca3af;
        }
 
        /* Sound detection card */
        .sound-card {
            padding: 14px 10px;
            border-radius: 10px;
            background: #020617;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
            border: 2px solid #374151;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
 
        .sound-card.active {
            border-color: #f59e0b;
            box-shadow: 0 0 14px rgba(245, 158, 11, 0.5);
        }
 
        .sound-badge {
            font-weight: bold;
            font-size: 13px;
            padding: 4px 10px;
            border-radius: 20px;
            transition: background 0.3s, color 0.3s;
        }
 
        .sound-badge.active {
            background: #f59e0b;
            color: #000;
        }
 
        .sound-badge.quiet {
            background: #374151;
            color: #9ca3af;
        }
 
        .pulse-sound {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #f59e0b;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulseSound 0.6s infinite;
        }
 
        @keyframes pulseSound {
            0%   { box-shadow: 0 0 4px #f59e0b; transform: scale(1); }
            50%  { box-shadow: 0 0 16px #f59e0b; transform: scale(1.3); }
            100% { box-shadow: 0 0 4px #f59e0b; transform: scale(1); }
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
 
        .spacer { visibility: hidden; }
 
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
 
        .pulse-red {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #22c55e;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulseGreen 1s infinite;
        }
 
        /* Detection toggle button */
        .detection-toggle {
            width: 100%;
            margin-top: 4px;
            padding: 10px;
            border-radius: 10px;
            border: 2px solid #374151;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            letter-spacing: 1px;
        }
 
        .detection-toggle.on {
            background: #14532d;
            border-color: #22c55e;
            color: #22c55e;
            box-shadow: 0 0 12px rgba(34,197,94,0.4);
        }
 
        .detection-toggle.off {
            background: #1f2937;
            border-color: #374151;
            color: #6b7280;
        }
 
        .detection-toggle:hover {
            filter: brightness(1.2);
        }
 
        @keyframes pulse {
            0% { box-shadow: 0 0 5px lime; }
            50% { box-shadow: 0 0 20px lime; }
            100% { box-shadow: 0 0 5px lime; }
        }
 
        @keyframes pulseGreen {
            0% { box-shadow: 0 0 4px #22c55e; }
            50% { box-shadow: 0 0 16px #22c55e; }
            100% { box-shadow: 0 0 4px #22c55e; }
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
 
            <!-- PERSON DETECTION CARD -->
            <div class="person-card clear" id="personCard">
                <span>🧍 Person Detection</span>
                <span class="person-badge clear" id="personBadge">CLEAR</span>
            </div>
            <button class="detection-toggle off" id="detectionToggle" onclick="toggleDetection()">
                🔴 DETECTION OFF — Click to Enable
            </button>
 
            <!-- SOUND DETECTION CARD -->
            <div class="sound-card" id="soundCard">
                <span>🔊 Sound Detection</span>
                <span class="sound-badge quiet" id="soundBadge">QUIET</span>
            </div>
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
 
function toggleDetection() {
    fetch('/toggle_detection', { method: 'POST' })
        .then(res => res.json())
        .then(data => updateToggleButton(data.detection_enabled));
}
 
function updateToggleButton(enabled) {
    const btn = document.getElementById("detectionToggle");
    if (enabled) {
        btn.className = "detection-toggle on";
        btn.textContent = "🟢 DETECTION ON — Click to Disable";
    } else {
        btn.className = "detection-toggle off";
        btn.textContent = "🔴 DETECTION OFF — Click to Enable";
    }
}
 
// Poll person detection every 500ms
function pollDetection() {
    fetch('/detection_status')
        .then(res => res.json())
        .then(data => {
            updateToggleButton(data.detection_enabled);
 
            const card  = document.getElementById("personCard");
            const badge = document.getElementById("personBadge");
 
            if (!data.detection_enabled) {
                card.className  = "person-card clear";
                badge.className = "person-badge clear";
                badge.textContent = "OFF";
                return;
            }
 
            if (data.person_detected) {
                card.className  = "person-card detected";
                badge.className = "person-badge detected";
                badge.innerHTML = "<span class='pulse-red'></span>DETECTED";
            } else {
                card.className  = "person-card clear";
                badge.className = "person-badge clear";
                badge.textContent = "CLEAR";
            }
        })
        .catch(() => {});
}
 
// Poll sound status every 500ms
function pollSound() {
    fetch('/sound_status')
        .then(res => res.json())
        .then(data => {
            const card  = document.getElementById("soundCard");
            const badge = document.getElementById("soundBadge");
 
            if (data === true || data.sound === true || data === "true") {
                card.className  = "sound-card active";
                badge.className = "sound-badge active";
                badge.innerHTML = "<span class='pulse-sound'></span>SOUND";
            } else {
                card.className  = "sound-card";
                badge.className = "sound-badge quiet";
                badge.textContent = "QUIET";
            }
        })
        .catch(() => {});
}
 
setInterval(pollSound, 100);
pollSound();
 
setInterval(pollDetection, 100);
pollDetection();
 
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


if __name__ == "__main__":
    try:
        app.run(host=HOST, port=PORT, threaded=True)
    finally:
        picam2.stop()

