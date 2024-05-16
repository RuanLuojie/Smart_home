# Smart Home Appliances: System Functions and Code Implementation

In this chapter, we will delve into each component of the system, including the LINE Bot, Glitch server, and ESP32 device. We'll demonstrate how to integrate these components to achieve remote control of lighting functions through a unified Python Flask application example.

### System Overview

This system consists of three core parts:

- **LINE Bot**: Receives user text commands.
- **Glitch Server**: Acts as a central server, processing commands and storing device status.
- **ESP32**: Executes actual device control operations, such as toggling lights.

All of these functionalities are implemented through a single Flask application, which is hosted on Glitch.

#### Flask Application Structure

The Flask application below includes routes for handling LINE messages and managing device status via an API. These code snippets represent different parts of the same application and should run together on the same server instance.

##### Global Setup and Route Definition for Flask Application

```python
from flask import Flask, request, jsonify, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from config import *

app = Flask(__name__)

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# Device status dictionary
device_status = {'light': 'off'}
```

#### LINE Bot Functionality

The LINE Bot receives user commands and updates device status based on these commands.

##### Code Snippet: Handling LINE Messages

```python
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.lower()
    if text == "turn_on":
        device_status['light'] = 'on'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Light has been turned on.")
        )
    elif text == "turn_off":
        device_status['light'] = 'off'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Light has been turned off.")
        )
```

#### Device Status Management API

This API route provides the latest device status information for ESP32.

##### Code Snippet: ESP32 Device Status API

```python
@app.route("/esp32/command", methods=['GET'])
def get_command():
    return jsonify(device_status)
```

#### Starting the Flask Application

Demonstrates how to start the entire Flask application.

##### Code Snippet: Starting the Application

```python
if __name__ == "__main__":
    app.run()
```

#### Original Code

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from config import *

app = Flask(__name__)

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)  # Replace with your Channel access token
handler = WebhookHandler(YOUR_CHANNEL_SECRET)  # Replace with your Channel secret

# Dictionary for storing device status
device_status = {'light': 'off'}  # Default: light is off

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.lower()
    if text == "turn_on":
        device_status['light'] = 'on'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Light has been turned on.")
        )
    elif text == "turn_off":
        device_status['light'] = 'off'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Light has been turned off.")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Unknown command.")
        )

@app.route("/esp32/command", methods=['GET'])
def get_command():
    return jsonify(device_status)

if __name__ == "__main__":
    app.run()

```

#### ESP32 Receiving Logic
The ESP32 periodically makes HTTP GET requests to the Glitch server to query the current status of the device. Then, based on the returned data, it controls the corresponding hardware, such as lights.

Code Snippet: HTTP GET Request in ESP32
```python
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "your_ssid";
const char* password = "your_password";

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
        http.begin("http://your-glitch-server-url.glitch.me/esp32/command");  // Make sure URL is correct
        int httpCode = http.GET();

        if (httpCode == 200) {
            String payload = http.getString();
            Serial.println("Received command: " + payload);
            // Parse instructions from payload and execute corresponding actions
        } else {
            Serial.println("Error on HTTP request");
        }
        http.end();
    }
    delay(10000); // Request every 10 seconds, adjust frequency as needed
}
```

### System Operation Principle

This system comprises three main components: LINE Bot, Glitch server, and ESP32 device, each serving specific functions and collectively achieving remote control capability for the entire system. Here's how each component works and how they interact:

#### 1. LINE Bot
The LINE Bot is the frontend interface for user interaction with the system. Users control devices by sending messages such as "turn_on" or "turn_off." These messages are sent to the Glitch server via the LINE Messaging API.

- **Receiving Messages**: When a user sends a message on the LINE app, the LINE platform pushes these messages to the `/callback` route on the Glitch server via Webhook.
- **Handling Messages**: The Glitch server parses these messages and updates the internal state based on the message content, which is stored in the `device_status` dictionary.

#### 2. Glitch Server
The Glitch server acts as the central server, responsible for receiving and processing commands from the LINE Bot, and also providing an API for ESP32 to query the current device status.

- **State Management**: The server updates the internal state based on commands received from the LINE Bot, which are stored in the `device_status` dictionary.
- **Providing Status Information**: The `/esp32/command` route allows ESP32 to periodically query the latest device status, ensuring synchronization between device behavior and user commands.

#### 3

. ESP32 Device
The ESP32 is the component responsible for executing physical operations. It periodically requests the latest device status from the Glitch server and controls the connected hardware (such as lights) accordingly.

- **Periodic Query**: ESP32 accesses the `/esp32/command` route on the Glitch server via HTTP GET requests to retrieve the latest device status information.
- **Executing Operations**: Based on the retrieved status information, ESP32 controls the appliances connected to its GPIO ports, such as turning lights on or off.

#### Integration Principle

This system communicates between components via network connections. Users send control commands through the LINE Bot, which are processed by the Glitch server and then executed by ESP32 in real-time. This design allows for flexible expansion to additional devices and functionalities while remaining simple and manageable.
