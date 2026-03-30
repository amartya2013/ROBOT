import io
from flask import Flask, Response

### You can donate at https://www.buymeacoffee.com/mmshilleh if I saved you time
### Subscribe https://www.youtube.com/@mmshilleh/videos

app = Flask(__name__)

def generate_frames():
    from picamera2 import Picamera2
    import cv2

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"size": (1400, 800)}))
    picam2.start()

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
