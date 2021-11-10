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
from googleapiclient.discovery import build
import json

app = Flask(__name__)

with open("secret.json") as f:
    secret = json.load(f)

#GOOGLE_API
ENGINE = secret["ENGINE"]
KEY = secret["KEY"]

CUSTOM_SEARCH_ENGINE_ID = ENGINE
API_KEY = KEY

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

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

#google_apiで検索して、URLを出す
def search_g(word, num):
    search = build(
    "customsearch", 
    "v1", 
    developerKey = API_KEY
    )

    results = search.cse().list(
                    q = word,
                    cx = CUSTOM_SEARCH_ENGINE_ID,
                    num = num
                ).execute()

    results = results["items"]

    result = []
    for i in results:
        result.append(i["link"])

    result = ', '.join(map(str, result))

    return result

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    num = 5
    line_bot_api.reply_message(
        event.reply_token,
        [TextSendMessage(text=f"「{event.message.text}」での検索上位[{num}]件です！"),
        TextSendMessage(text=search_g(event.message.text, num))
        ]
    )

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)