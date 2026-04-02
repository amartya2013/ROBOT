from ultralytics import YOLO
import cv2
from picamera2 import Picamera2

model = YOLO("yolov8n.pt")

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (800, 600)}))
picam2.start()

while True:
    weird_frame = picam2.capture_array()  # already BGR
    frame = cv2.cvtColor(weird_frame, cv2.COLOR_BGR2RGB)
    results = model(frame)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])

            if model.names[cls] == "person":
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.putText(frame, "PERSON", (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # ✅ ALWAYS show frame
    cv2.imshow("FireBot Vision", frame)

    # ✅ REQUIRED for window to update
    if cv2.waitKey(1) & 0xFF == 27:  # press ESC to exit
        break

picam2.stop()
cv2.destroyAllWindows()
