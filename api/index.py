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
# output_length = request.args.get('length', 300)

# 建立一个字典，用来储存每个Line用户的对话
user_dialogues = defaultdict(list)

# 用一个字典来记录用户最后一次发送的消息的序号
last_message_indices = defaultdict(int)

# 定义每批次对话历史的最大长度
MAX_HISTORY_LENGTH = 10

def chatgpt(input_text, user_id):
    
    # 取得用户的对话历史
    dialogues = user_dialogues[user_id]
    
    # 如果对话数量超过最大长度，就进行分批处理
    num_batches = len(dialogues) // MAX_HISTORY_LENGTH
    if len(dialogues) % MAX_HISTORY_LENGTH != 0:
        num_batches += 1
    batched_dialogues = [dialogues[i:i+MAX_HISTORY_LENGTH] for i in range(0, len(dialogues), MAX_HISTORY_LENGTH)]
    
    # 用一个变量来记录用户最后一次发送的消息是否为偶数
    last_message_is_even = last_message_indices[user_id] % 2 == 0
    
    # 将历史对话转成 OpenAI API 所需的格式，即显示谁说的
    history_formatted = ""
    for batch in batched_dialogues:
        for i, dialogue in enumerate(batch):
            # 根据用户最后一次发送的消息是奇数还是偶数来决定是用户说的话还是AI说的话
            if i % 2 == 0:
                if last_message_is_even:
                    history_formatted += f"\nUser: {dialogue}"
                else:
                    history_formatted += f"\nAI: {dialogue}"
            else:
                if last_message_is_even:
                    history_formatted += f"\nAI: {dialogue}"
                else:
                    history_formatted += f"\nUser: {dialogue}"

    # 生成回应
    response = openai.Completion.create(
        engine=model_engine,
        prompt=input_text,
        additional_text=history_formatted,
        # max_tokens=output_length,
        temperature=1.0
    )

    # 将这次的输入和回应加入用户的对话历史中
    user_dialogues[user_id].append(input_text)
    user_dialogues[user_id].append(response.choices[0].text)
    
    # 更新用户最后一次发送的消息的序号
    last_message_indices[user_id] += 1

    # 输出回应
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