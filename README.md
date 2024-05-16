# 智慧家電：系統功能與代碼實現

在本章中，我們將深入探討系統的每個組成部分，包括 LINE Bot、Glitch 伺服器和 ESP32 設備。透過一個統一的 Python Flask 應用示例來展示如何集成這些組件，以實現遠程控制燈光的功能。

### 系統概述

本系統包含三個核心部分：

- **LINE Bot**：接收用戶的文字指令。
- **Glitch 伺服器**：作為中央伺服器，處理指令並存儲設備狀態。
- **ESP32**：執行實際的設備控制操作，如開關燈。

所有這些功能都通過一個單一的 Flask 應用實現，該應用在 Glitch 上托管。

#### Flask 應用結構

下面的 Flask 應用包括處理 LINE 消息的路由和管理設備狀態的 API。這些代碼片段都是同一個應用的不同部分，應一起運行在同一個伺服器實例上。

##### Flask 應用的全局設置和路由定義

```python
from flask import Flask, request, jsonify, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from config import *

...
```

#### LINE Bot 功能

LINE Bot 接收用戶的指令，並根據這些指令更新設備狀態。

##### 代碼片段：處理 LINE 消息

```python
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
...
        )
```

#### 設備狀態管理 API

這個 API 路由為 ESP32 提供最新的設備狀態信息。

##### 代碼片段：ESP32 設備狀態 API

```python
@app.route("/esp32/command", methods=['GET'])
def get_command():
    return jsonify(device_status)
```

#### 啟動 Flask 應用

展示如何啟動整個 Flask 應用。

##### 代碼片段：啟動應用

```python
if __name__ == "__main__":
    app.run()
```
#### ESP32 的接收逻辑
ESP32 定期向 Glitch 伺服器發起 HTTP GET 請求，查詢裝置的目前狀態。 然後，根據返回的數據控制相應的硬件，如燈光。

程式碼片段：ESP32 的 HTTP GET 請求
```python
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

...

```

### 系統工作原理

本系統由三個主要組件構成：LINE Bot、Glitch 伺服器和 ESP32 設備，每個組件都承擔著特定的功能，共同實現整個系統的遠程控制能力。以下是各個組件的工作原理和它們之間如何交互：

#### 1. LINE Bot
LINE Bot 是用戶與系統交互的前端界面。用戶通過發送消息如 "turn_on" 或 "turn_off" 來控制設備。這些消息通過 LINE Messaging API 發送到 Glitch 伺服器。

- **接收消息**：當用戶在 LINE 應用上發送消息時，LINE 平台將這些消息以 Webhook 的形式推送到 Glitch 伺服器上的 `/callback` 路由。
- **處理消息**：Glitch 伺服器解析這些消息，並根據消息內容更新全局設備狀態字典 `device_status`。此字典記錄了設備的當前狀態（例如燈的開關狀態）。

#### 2. Glitch 伺服器
Glitch 伺服器扮演中心伺服器的角色，負責接收和處理來自 LINE Bot 的指令，同時也為 ESP32 提供一個查詢當前設備狀態的 API。

- **狀態管理**：伺服器根據從 LINE Bot 接收到的指令更新內部狀態，這些狀態存儲在 `device_status` 字典中。
- **提供狀態信息**：`/esp32/command` 路由允許 ESP32 定期查詢設備的最新狀態，確保設備行為與用戶指令同步。

#### 3. ESP32 設備
ESP32 是實際執行物理操作的組件。它定期向 Glitch 伺服器請求最新的設備狀態，並據此控制連接的硬體（如燈光）。

- **定期查詢**：ESP32 通過 HTTP GET 請求訪問 Glitch 伺服器的 `/esp32/command` 路由，獲取最新的設備狀態信息。
- **執行操作**：根據獲取的狀態信息，ESP32 會控制其 GPIO 端口連接的電器，如開關燈。

#### 整合原理

這個系統通過網路連接實現各組件之間的通信。用戶通過 LINE Bot 發送控制指令，Glitch 伺服器處理這些指令並更新設備狀態，ESP32 則實時檢查這些狀態並執行相應的物理操作。這種設計使得系統可以靈活地擴展到更多設備和功能，同時保持簡單和易於管理。
