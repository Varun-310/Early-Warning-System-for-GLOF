#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <LoRa.h>

// WiFi credentials
#define WIFI_SSID "Mithun"
#define WIFI_PASSWORD "87878787"

// Firebase credentials
#define FIREBASE_API_KEY "AIzaSyD10232-XJuWGt5zFyrf38cesmwJ1dMi8w"
#define FIREBASE_DATABASE_URL "https://glof-ff2e6-default-rtdb.asia-southeast1.firebasedatabase.app/"

// Firebase objects
FirebaseConfig config;
FirebaseAuth auth;
FirebaseData fbData;

// LoRa Pins
#define ss 5
#define rst 14
#define dio0 2

void setup() {
  Serial.begin(115200);
  Serial.println("LoRa Receiver with Firebase Integration for Two Senders");

  // Initialize Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi.");

  // Configure Firebase
  config.api_key = FIREBASE_API_KEY;
  config.database_url = FIREBASE_DATABASE_URL;
  Firebase.reconnectWiFi(true);

  if (!Firebase.signUp(&config, &auth, "", "")) {
    Serial.printf("Firebase sign-up error: %s\n", config.signer.signupError.message.c_str());
  }

  Firebase.begin(&config, &auth);
  Serial.println("Firebase initialized.");

  // Initialize LoRa
  LoRa.setPins(ss, rst, dio0);
  while (!LoRa.begin(433E6)) {
    Serial.println("Initializing LoRa...");
    delay(500);
  }
  LoRa.setSyncWord(0xA5);
  Serial.println("LoRa initialized.");
}

void loop() {
  // Check for LoRa packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    Serial.println("LoRa packet received:");

    String receivedData = "";
    while (LoRa.available()) {
      receivedData += (char)LoRa.read();
    }
    Serial.println("Received Data: " + receivedData);

    // Identify sender
    if (receivedData.indexOf("Sender_1") != -1) {
      processSender1Data(receivedData);
    } else if (receivedData.indexOf("Sender_2") != -1) {
      processSender2Data(receivedData);
    } else {
      Serial.println("Unknown sender ID.");
    }
  }

  delay(100); // Small delay for stability
}

void processSender1Data(String data) {
  Serial.println("Processing data from Sender 1...");

  // Parse data
  String accelX = extractValue(data, "Accel X: ", " m/s^2,");
  String accelY = extractValue(data, "Accel Y: ", " m/s^2,");
  String accelZ = extractValue(data, "Accel Z: ", " m/s^2,");
  String gyroX = extractValue(data, "Gyro X: ", " rad/s,");
  String gyroY = extractValue(data, "Gyro Y: ", " rad/s,");
  String gyroZ = extractValue(data, "Gyro Z: ", " rad/s;");
  String temp = extractValue(data, "Temperature: ", " °C,");
  String humidity = extractValue(data, "Humidity: ", " %,");
  String vibration = extractValue(data, "Vibration: ", " ADC");
  String battery = extractValue(data, "Battery: ", " %");

  // Update Firebase under Sender 1 node
  if (Firebase.ready()) {
    if (Firebase.RTDB.setFloat(&fbData, "/Sender1/MPU6050/AccelX", accelX.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender1/MPU6050/AccelY", accelY.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender1/MPU6050/AccelZ", accelZ.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender1/MPU6050/GyroX", gyroX.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender1/MPU6050/GyroY", gyroY.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender1/MPU6050/GyroZ", gyroZ.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender1/DHT/Temperature", temp.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender1/DHT/Humidity", humidity.toFloat()) &&
        Firebase.RTDB.setInt(&fbData, "/Sender1/Vibration", vibration.toInt())) {
      Serial.println("Sender 1 data updated in Firebase.");
    } else {
      Serial.println("Failed to update Sender 1 data in Firebase.");
      Serial.println(fbData.errorReason());
    }
  } else {
    Serial.println("Firebase is not ready for Sender 1.");
  }
}

void processSender2Data(String data) {
  Serial.println("Processing data from Sender 2...");

  // Parse data
  String gpsLat = extractValue(data, "Lat:", ",Lon:");
  String gpsLon = extractValue(data, "Lon:", ",Alt:");
  String gpsAlt = extractValue(data, "Alt:", ",");
  String accelX = extractValue(data, "Accel X: ", " m/s^2,");
  String accelY = extractValue(data, "Accel Y: ", " m/s^2,");
  String accelZ = extractValue(data, "Accel Z: ", " m/s^2,");
  String gyroX = extractValue(data, "Gyro X: ", " rad/s,");
  String gyroY = extractValue(data, "Gyro Y: ", " rad/s,");
  String gyroZ = extractValue(data, "Gyro Z: ", " rad/s;");
  String waterTemp = extractValue(data, "WaterTemp:", ",");
  String flowRate = extractValue(data, "FlowRate:", ",");
  String voltage = extractValue(data, "Voltage:", ",");
  String battery = extractValue(data, "Battery%:", " %");

  // Update Firebase under Sender 2 node
  if (Firebase.ready()) {
    if (Firebase.RTDB.setFloat(&fbData, "/Sender2/GPS/Latitude", gpsLat.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender2/GPS/Longitude", gpsLon.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender2/GPS/Altitude", gpsAlt.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender2/MPU6050/AccelX", accelX.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender2/MPU6050/AccelY", accelY.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender2/MPU6050/AccelZ", accelZ.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender2/MPU6050/GyroX", gyroX.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender2/MPU6050/GyroY", gyroY.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender2/MPU6050/GyroZ", gyroZ.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender2/Sensors/WaterTemperature", waterTemp.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender2/Sensors/FlowRate", flowRate.toFloat()) &&
        Firebase.RTDB.setFloat(&fbData, "/Sender2/Sensors/Voltage", voltage.toFloat()) &&
        Firebase.RTDB.setInt(&fbData, "/Sender2/Sensors/Batterypercentage", battery.toInt())) {
      Serial.println("Sender 2 data updated in Firebase.");
    } else {
      Serial.println("Failed to update Sender 2 data in Firebase.");
      Serial.println(fbData.errorReason());
    }
  } else {
    Serial.println("Firebase is not ready for Sender 2.");
  }
}

String extractValue(String data, String key, String delimiter) {
  int startIndex = data.indexOf(key);
  if (startIndex == -1) return "";
  startIndex += key.length();
  int endIndex = data.indexOf(delimiter, startIndex);
  if (endIndex == -1) return data.substring(startIndex);
  return data.substring(startIndex, endIndex);
}
