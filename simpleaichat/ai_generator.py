import requests
import os
from model_type import ModelType
import re

# from response_parse import ResponseParse

###基于您的需求，可以对 CustomOutputParser 类进行扩展或修改，以实现特定的逻辑：当响应中包含 action 和 actionInput 时，截取 actionInput 以上的回复加入到上下文中，并执行 action 调用的函数。然后，将函数的输出结果添加到观察结果中，并连同上下文再次发送请求，直到响应中出现 finalAnswer。
# 设置环境变量（仅用于测试，实际部署时更换）
os.environ['OPENAI_API_KEY'] = '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'
class AIGenerator:

    def __init__(self, model_type: ModelType):
        """初始化 TextGen 类。

        Args:
            model_url (str): textgen WebUI 的完整 URL，包括 http[s]://host:port
        """
        self.model_type = model_type

    def generate(self, input_prompt :str) -> str:
        # user_input="<|user|> "+user_input
        """调用 textgen Web API 并返回输出。

        Args:
            prompt (str): 用于生成文本的提示。
            max_new_tokens (int): 生成的最大令牌数。
            user_input (str): 用户输入


        Returns:
            str: 生成的文本。
        """
        if self.model_type == ModelType.OPENAI:

            model_url = "https://api.openai.com"
            url = f"{model_url}/v1/chat/completions"
            headers = {"Content-Type": "application/json",
                       "Authorization": f"Bearer " + os.getenv("OPENAI_API_KEY"),
                       }
            history = [
                {"role": "system", "content": input_prompt},  # 系统（或预设）的消息
                {"role": "user", "content": input_prompt}  # 用户的消息
            ]
            data = {
                "model": "gpt-3.5-turbo",  # 确保这里指定了正确的模型
                "messages": history
            }
        elif self.model_type == ModelType.LOCAL_LLM:

            model_url = "http://123.60.183.64:5001"
            url = f"{model_url}/v1/completions"
            headers = {"Content-Type": "application/json",
                       }
            history = [
                # {"role": "system", "content": prompt},  # 系统（或预设）的消息
                {"role": "user", "content" :input_prompt}  # 用户的消息
            ]
            data = {
                "prompt": input_prompt,
                "max_tokens": 300,
                "temperature": 0.5,
                "top_p": 0.9,
                "seed": 10,
                "stream": False,
            }
        else:
            raise Exception(f"不支持的模型类型: {self.model_type}")

        response = requests.post(url, headers=headers, json=data)
        # print(response.json())

        if response.status_code == 200:
            # 解析 JSON 数据
            data = response.json()

            # 检查 'choices' 是否存在且非空
            if 'choices' in data and data['choices']:
                # 提取 'text' 字段
                assistant_message = data['choices'][0]['text']
                # response_parse = ResponseParse()
                # response_parse.process_response(assistant_message)

                return assistant_message
            else:
                raise Exception("响应中没有找到有效的 'choices' 数据")
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")

