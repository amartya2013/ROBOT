
import cv2
from flask import Flask, Response, jsonify, render_template
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
    message = COMMANDS.get(action)
    if message:
        exec(message)
        return message
    return "Invalid command", 404


@app.route("/")
def home():
    return render_template('index.html')



try:
    app.run(host=HOST, port=PORT, threaded=True)
finally:
    picam2.stop()

