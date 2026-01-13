#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ===== WIFI =====
const char* ssid     = "FPT L2";
const char* password = "toto662005";

// ===== PIN =====
#define IR_PIN          27
#define RELAY_PIN       26
#define SERVO_RED_PIN   25
#define SERVO_GRAY_PIN  33

// ===== OLED =====
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// ===== SERVO =====
Servo servoRed;
Servo servoGray;

// ===== WEB SERVER =====
WebServer server(80);

// ===== STATE =====
bool objectDetected = false;
int redCount = 0;
int grayCount = 0;
bool waitingSort = false;
unsigned long waitStart = 0;
const unsigned long SORT_TIMEOUT = 10000; // 10 giây


// ===== RELAY (HIGH trigger) =====
void relayOn()  { digitalWrite(RELAY_PIN, HIGH); }
void relayOff() { digitalWrite(RELAY_PIN, LOW); }

// ===== SERVO ACTIONS =====
void runRedServo() {
  servoRed.write(60);
  delay(4500);
  servoRed.write(0);
}

void runGrayServo() {
  servoGray.write(60);
  delay(4500);
  servoGray.write(0);
}

// ===== OLED UPDATE =====
void updateOLED() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print("Red: ");
  display.println(redCount);
  display.print("Gray: ");
  display.println(grayCount);
  display.display();
}

// ===== API =====
void handleRedBox() {
  Serial.println("🟥 REDBOX command");
  if (!objectDetected) {
    server.send(200, "text/plain", "NO OBJECT");
    return;   // 🔥 BẮT BUỘC
  }
  relayOff();
  delay(2000);
  runRedServo();
  relayOn();
  redCount++;
  objectDetected = false;
  updateOLED();
  server.send(200, "text/plain", "RED OK");
}
void handleGrayBox() {
  Serial.println("⬜ GRAYBOX command");
  if (!objectDetected) {
    server.send(200, "text/plain", "NO OBJECT");
    return;   // 🔥 BẮT BUỘC
  }
  relayOff(); 
  delay(2000); 
  runGrayServo();  
  relayOn();  
  grayCount++;
  objectDetected = false;  
  updateOLED();

  server.send(200, "text/plain", "GRAY OK");
}


void handleRoot() {
  server.send(200, "text/plain",
    "ESP32 SORTER READY\n"
    "/redbox  -> RED SERVO\n"
    "/graybox -> GRAY SERVO"
  );
}

void setup() {
  Serial.begin(115200);

  // ===== PIN MODE =====
  pinMode(IR_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);

  relayOn(); // băng tải chạy mặc định

  // ===== SERVO =====
  servoRed.attach(SERVO_RED_PIN, 500, 2400);
  servoGray.attach(SERVO_GRAY_PIN, 500, 2400);
  servoRed.write(0);
  servoGray.write(0);

  // ===== OLED =====
  Wire.begin();
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }
  display.clearDisplay();
  updateOLED();

  // ===== WIFI =====
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  // ===== WEB =====
  server.on("/", handleRoot);
  server.on("/redbox", HTTP_GET, handleRedBox);
  server.on("/graybox", HTTP_GET, handleGrayBox);
  server.begin();

  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();

  int irValue = digitalRead(IR_PIN);

  // PHÁT HIỆN VẬT (chỉ bắt 1 lần khi chuyển HIGH → LOW)
  if (irValue == LOW && !objectDetected) {
    objectDetected = true;
    detectCount++;

    Serial.print("Object detected - Lần: ");
    Serial.println(detectCount);

    relayOff();   // dừng băng tải

    // ===== LUÂN PHIÊN SERVO =====
    if (detectCount % 2 == 1) {
      Serial.println("➡ Servo hoạt động");
      runRedServo();
      redCount++;
    } else {
      Serial.println("➡ Servo hoạt động");
      runGrayServo();
      grayCount++;
    }

    updateOLED();

    delay(500);   // đợi servo ổn định
    relayOn();    // chạy lại băng tải
  }

  // Khi vật đi khỏi cảm biến
  if (irValue == HIGH) {
    objectDetected = false;
  }
}
