import openai
import os

def chatgpt(input):
    # 設定OpenAI API密鑰
    openai.api_key = "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"

    # 載入ChatGPT模型
    model_engine = "text-davinci-003"

    # 設定使用者輸入
    input_text = input

    # 設定生成的文本長度
    # output_length = 300

    # 生成回應
    # response = model.complete(prompt, max_tokens=100)
    response = openai.Completion.create(
        engine=model_engine,
        prompt=input_text,
        # max_tokens=output_length,
    )

    # 輸出回應
    return response.choices[0].text