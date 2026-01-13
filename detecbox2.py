from ultralytics import YOLO
import cv2
import requests
import time

# ===== LOAD MODEL =====
model = YOLO("best (4).pt")

# ===== ESP32-CAM STREAM =====
CAM_URL = "http://192.168.102.35:81/stream"
cap = cv2.VideoCapture(CAM_URL)

# ===== ESP32 SERVO API =====
SERVO1_60 = "http://192.168.102.60/servo1/60"
SERVO1_0  = "http://192.168.102.60/servo1/0"

SERVO2_60 = "http://192.168.102.60/servo2/60"
SERVO2_0  = "http://192.168.102.60/servo2/0"

# ===== TIME CONFIG =====
SERVO_ON_TIME = 4
COOLDOWN_TIME = 2

# ===== STATE =====
servo1_active = False
servo2_active = False

servo1_until = 0
servo2_until = 0

cooldown1_until = 0
cooldown2_until = 0

# ===== FRAME SKIP =====
frame_count = 0
SKIP_FRAMES = 5

print("🚀 YOLO AUTO SORTING STARTED")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Mất kết nối camera, đang reconnect...")
            cap = cv2.VideoCapture(CAM_URL)
            time.sleep(1)
            continue

        frame_count += 1
        annotated_frame = frame.copy()

        detected_red = False
        detected_gray = False

        # ===== YOLO DETECT =====
        if frame_count % SKIP_FRAMES == 0:
            results = model(frame, conf=0.5, imgsz=640, verbose=False)

            for r in results:
                boxes = r.boxes
                if boxes is None:
                    continue

                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = model.names[cls].lower()

                    if conf < 0.5:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # ===== COLOR BY CLASS =====
                    if class_name == "redbox":
                        color = (0, 0, 255)
                        detected_red = True
                    elif class_name == "graybox":
                        color = (128, 128, 128)
                        detected_gray = True
                    else:
                        color = (0, 255, 0)

                    # ===== DRAW BOX =====
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

                    # ===== DRAW LABEL WITH BACKGROUND =====
                    label = f"{class_name} {conf:.2f}"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.7
                    thickness = 2

                    (tw, th), _ = cv2.getTextSize(label, font, font_scale, thickness)

                    cv2.rectangle(
                        annotated_frame,
                        (x1, y1 - th - 10),
                        (x1 + tw + 6, y1),
                        color,
                        -1
                    )

                    cv2.putText(
                        annotated_frame,
                        label,
                        (x1 + 3, y1 - 5),
                        font,
                        font_scale,
                        (255, 255, 255),
                        thickness
                    )

        now = time.time()

        # ===== SERVO 1 (REDBOX) =====
        if detected_red and not servo1_active and now >= cooldown1_until:
            try:
                requests.get(SERVO1_60, timeout=1)
                servo1_active = True
                servo1_until = now + SERVO_ON_TIME
                print("🔴 Redbox → Servo1 60°")
            except:
                print("❌ Lỗi Servo1")

        if servo1_active and now >= servo1_until:
            try:
                requests.get(SERVO1_0, timeout=1)
                servo1_active = False
                cooldown1_until = now + COOLDOWN_TIME
                print("↩ Servo1 về 0°")
            except:
                print("❌ Lỗi Servo1 reset")

        # ===== SERVO 2 (GRAYBOX) =====
        if detected_gray and not servo2_active and now >= cooldown2_until:
            try:
                requests.get(SERVO2_60, timeout=1)
                servo2_active = True
                servo2_until = now + SERVO_ON_TIME
                print("⚪ Graybox → Servo2 60°")
            except:
                print("❌ Lỗi Servo2")

        if servo2_active and now >= servo2_until:
            try:
                requests.get(SERVO2_0, timeout=1)
                servo2_active = False
                cooldown2_until = now + COOLDOWN_TIME
                print("↩ Servo2 về 0°")
            except:
                print("❌ Lỗi Servo2 reset")

        # ===== INFO TEXT =====
        if detected_red:
            cv2.putText(annotated_frame, "Redbox Detected!", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if detected_gray:
            cv2.putText(annotated_frame, "Graybox Detected!", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), 2)

        # ===== DISPLAY =====
        cv2.imshow("YOLO AUTO SORTING", annotated_frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    # ===== CLEANUP =====
    try:
        requests.get(SERVO1_0, timeout=1)
        requests.get(SERVO2_0, timeout=1)
        print("🔄 Reset servos")
    except:
        print("❌ Lỗi reset")

    cap.release()
    cv2.destroyAllWindows()
    print("🛑 Program stopped")
