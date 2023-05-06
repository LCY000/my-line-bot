import openai
import os

from collections import defaultdict
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

# 設定OpenAI API密鑰
openai.api_key = os.environ["OPENAI_API_KEY"]

# 載入ChatGPT模型
model_engine = "text-davinci-003"

# 設定生成的文本長度
output_length = 300

# 建立一個字典，用來儲存每個Line用戶的前6個對話
user_dialogues = defaultdict(list)

def chatgpt(input_text, user_id):
    # 每個Line用戶只保留前6個對話
    user_dialogues[user_id] = user_dialogues[user_id][-5:] + [input_text]

    # 合併每個Line用戶的前6個對話，作為ChatGPT的輸入
    input_history = "\n".join(user_dialogues[user_id])

    # 生成回應
    response = openai.Completion.create(
        engine=model_engine,
        prompt=input_history,
        max_tokens=output_length,
        temperature=1.3
    )

    # 輸出回應
    return response.choices[0].text

app = Flask(__name__)

line_bot_api = LineBotApi('5Upflq5dGSdO0XcPbzx+s3QdYSA6C+bknNz/4xWrs7HvMulaIdcU0K5ojdFd8c6/c6jdL2pqHWY9MHQrRBbEp0yG2hmxgpkY4kiILYkLWvgCYDR3zpT3rn1vLKnF3emHNh9qeLjXHSNQ1AfMDfOPQQdB04t89/1O/w1cDnyilFU=')
webhook_handler = WebhookHandler('0f6fa69d1a0843d685a121d4d975b078')

@app.route("/")
def home():
    return "LINE BOT API Server is running."

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        webhook_handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@webhook_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    response = chatgpt(event.message.text, user_id)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response))

if __name__ == "__main__":
    app.run()