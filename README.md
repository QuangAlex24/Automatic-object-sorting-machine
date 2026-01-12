# 🤖 Automatic Object Sorting Machine (ESP32-CAM + AI)

## 📌 Giới thiệu
Dự án **Máy tự động phân loại đồ vật** sử dụng **ESP32-CAM kết hợp AI** để nhận dạng vật thể và điều khiển **servo** phân loại đồ vật một cách tự động.

Hệ thống truyền hình ảnh từ ESP32-CAM về **Python Server** để xử lý nhận dạng.  
Kết quả phân loại được gửi đến **Node-RED** để giám sát và **điều khiển servo thông qua ESP32**.

---

## ⚙️ Chức năng chính

### 🔹 1. Nhận dạng đồ vật bằng AI
- ESP32-CAM chụp ảnh vật thể
- Gửi ảnh đến Python Server
- Sử dụng **Object Detection (YOLO / OpenCV)**
- Phân loại theo từng nhóm (ví dụ: kim loại, nhựa, giấy…)

### 🔹 2. Phân loại tự động bằng Servo
- Servo điều khiển cửa / cần gạt
- Mỗi loại vật thể tương ứng với một góc servo
- Phân loại nhanh, chính xác

### 🔹 3. Giám sát & điều khiển qua Node-RED
- Hiển thị:
  - Hình ảnh camera
  - Loại vật thể đã phát hiện
  - Số lượng từng loại
- Điều khiển thủ công servo khi cần

### 🔹 4. Kết nối ESP32 – Python – Node-RED
- ESP32-CAM ↔ Python: HTTP / WebSocket
- Python ↔ Node-RED: MQTT / HTTP
- Node-RED ↔ ESP32: MQTT

---

## 🧰 Phần cứng sử dụng
- ESP32-CAM
- ESP32 / Arduino (điều khiển servo)
- Servo motor (SG90 / MG996R)
- Băng tải (tuỳ chọn)
- Nguồn cấp

---

## 💻 Phần mềm & Công nghệ
- **Arduino IDE** (ESP32 / ESP32-CAM)
- **Python** (AI & Server)
- **OpenCV / YOLOv8**
- **Node-RED**
- **MQTT / HTTP**
- **ESP32 WiFi**
