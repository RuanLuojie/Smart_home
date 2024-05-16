#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "nga";
const char* password = "0958188700";

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("WiFi connected");
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin("http://translucent-charm-agustinia.glitch.me/esp32/command");  // 确保 URL 正确
        int httpCode = http.GET();

        if (httpCode == 200) {
            String payload = http.getString();
            Serial.println("Received command: " + payload);
            // 解析 payload 中的命令并执行相应操作
        } else {
            Serial.println("Error on HTTP request");
        }
        http.end();
    }
    delay(1000); // 10 秒请求一次，根据需要调整频率
}
