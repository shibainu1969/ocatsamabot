from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
import random

from urllib.request import urlopen
from urllib.request import Request
from json import dumps
from json import loads
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

JST = timezone(timedelta(hours=+9), 'JST')

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=create_response(event.message.text)))

CLIENT_ID = "J3duGtdHH2j3V1QjsWHIPDUnnaaA2zZ5"
CLIENT_SECRET = "bpRomX3y0fHo7p5Z"
ACCESS_TOKEN_PUBLISH_URL = "https://api.ce-cotoha.com/v1/oauth/accesstokens"
SENTENCE_TYPE_URL = "https://api.ce-cotoha.com/v1/api/dev/nlp/sentence_type"
NE_URL = "https://api.ce-cotoha.com/v1/api/dev/nlp/ne"
KEYWORD_URL = "https://api.ce-cotoha.com/v1/api/dev/nlp/keyword"

def create_response(message):
    sentence_type = eval_sentence(message)
    if (sentence_type == "greeting"):
        hour = datetime.now(JST).hour
        if (0 <= hour < 5):
            return "こんばんニャ"
        elif (5 <= hour < 11):
            return "おはようニャ"
        elif (11 <= hour < 17):
            return "こんにちニャ"
        elif (17 <= hour < 24):
            return "こんばんニャ"
        else:
            return "なんかおかしいニャ"
    else:
        return random.choice(["ニャー！", "ニャーニャー！", "ねむいニャ", "ねたニャ", "おなかがすいたニャ", "あそんでニャ", "チュール！ チュール！"])

def eval_sentence(message):
    access_token = get_access_token()
    json_str = {
      "sentence":message
    }

    request_header = {
      "Content-Type":"application/json",
      "charset":"UTF-8",
      "Authorization":"Bearer " + access_token
    }
    url = Request(SENTENCE_TYPE_URL, dumps(json_str).encode(), request_header)
    response = loads(urlopen(url).read())
    if (response["result"]["dialog_act"][0] == "greeting"):
        return "greeting"
    else:
        return "default"

def get_access_token():
    json_str = {
      "grantType":"client_credentials",
      "clientId":CLIENT_ID,
      "clientSecret":CLIENT_SECRET
    }

    request_header = {"Content-Type":"application/json", "charset":"UTF-8"}
    url = Request(ACCESS_TOKEN_PUBLISH_URL, dumps(json_str).encode(), request_header)
    response = loads(urlopen(url).read())
    return response["access_token"]


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
