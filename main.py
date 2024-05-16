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

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN) 
handler = WebhookHandler(YOUR_CHANNEL_SECRET)  

device_status = {'light': 'off'} 

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
