import openai
import os

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

def chatgpt(input):
    # 設定OpenAI API密鑰
    openai.api_key = os.environ["OPENAI_API_KEY"]
    # openai.api_key = "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"

    # 載入ChatGPT模型
    model_engine = "text-davinci-003"

    # 設定使用者輸入
    input_text = input

    # 設定生成的文本長度
    output_length = 300

    # 生成回應
    # response = model.complete(prompt, max_tokens=100)
    response = openai.Completion.create(
        engine=model_engine,
        prompt=input_text,
        max_tokens=output_length,
        temperature=1.7
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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=chatgpt(event.message.text)))


if __name__ == "__main__":
    app.run()
    # print(chatgpt("hello world"))





# import openai
# import os

# from flask import Flask, request, abort

# from linebot import (
#     LineBotApi, WebhookHandler
# )
# from linebot.exceptions import (
#     InvalidSignatureError
# )
# from linebot.models import (
#     MessageEvent, TextMessage, TextSendMessage,
# )

# app = Flask(__name__)

# line_bot_api = LineBotApi('5Upflq5dGSdO0XcPbzx+s3QdYSA6C+bknNz/4xWrs7HvMulaIdcU0K5ojdFd8c6/c6jdL2pqHWY9MHQrRBbEp0yG2hmxgpkY4kiILYkLWvgCYDR3zpT3rn1vLKnF3emHNh9qeLjXHSNQ1AfMDfOPQQdB04t89/1O/w1cDnyilFU=')
# webhook_handler = WebhookHandler('0f6fa69d1a0843d685a121d4d975b078')

# # 設定 OpenAI API 密鑰
# openai.api_key = os.environ["OPENAI_API_KEY"]
# # openai.api_key = "OPENAI_API_KEY"

# # 設定 GPT-3.5 模型的檢索引擎
# model_engine = "text-davinci-003"

# # 設定生成的文本長度
# output_length = 200


# @app.route("/")
# def home():
#     return "LINE BOT API Server is running."

# @app.route("/callback", methods=['POST'])
# def callback():
#     # get X-Line-Signature header value
#     signature = request.headers['X-Line-Signature']

#     # get request body as text
#     body = request.get_data(as_text=True)
#     app.logger.info("Request body: " + body)

#     # handle webhook body
#     try:
#         webhook_handler.handle(body, signature)
#     except InvalidSignatureError:
#         print("Invalid signature. Please check your channel access token/channel secret.")
#         abort(400)

#     return 'OK'


# @webhook_handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):

#     # 使用 GPT-3.5 模型生成文本
#     response = openai.Completion.create(
#         engine=model_engine,
#         prompt=event.message.text,
#         max_tokens = output_length,
#     )

#     # 取得生成的文本
#     output_text = response.choices[0].text

#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=output_text))

# if __name__ == "__main__":
#     app.run()