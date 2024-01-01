import requests
import os

import re

from langchain_core.prompts import PromptTemplate


from simpleaichat.model_type import ModelType
from simpleaichat.prompt import COSER, RAG

# from response_parse import ResponseParse

###基于您的需求，可以对 CustomOutputParser 类进行扩展或修改，以实现特定的逻辑：当响应中包含 action 和 actionInput 时，截取 actionInput 以上的回复加入到上下文中，并执行 action 调用的函数。然后，将函数的输出结果添加到观察结果中，并连同上下文再次发送请求，直到响应中出现 finalAnswer。
# 设置环境变量（仅用于测试，实际部署时更换）
os.environ['OPENAI_API_KEY'] = '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'

class BaseAIGenerator:
    """AI文本生成器的基类。"""


    def generate(self, instruction: str) -> str:
        """生成文本的方法，需要在子类中实现。
        Args:
            instruction (str): 输入提示。
        Returns:
            str: 生成的文本。
        """
        raise NotImplementedError("该方法需要在子类中实现。")

    def generate_with_context(self, instruction: str, context: str) -> str:
        """生成文本的方法，需要在子类中实现。
        Args:
            instruction (str): 输入提示。
            context (str): 上下文。
        Returns:
            str: 生成的文本。
        """
        raise NotImplementedError("该方法需要在子类中实现。")

class OpenAIGenerator(BaseAIGenerator):

    def generate(self, instruction: str) -> str:
        """调用OpenAI API生成文本。
        Args:
            instruction (str): 输入提示。
        Returns:
            str: 生成的文本。
        """
        model_url = "https://api.openai.com"
        url = f"{model_url}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY")
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": instruction}]
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and data['choices']:
                try:
                    return data['choices'][0]['message']['content']
                except (KeyError, IndexError, TypeError) as e:
                    raise Exception(f"解析响应时出错: {e}")
            else:
                raise Exception("响应中没有找到有效的 'choices' 数据")
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")


class LocalLLMGenerator(BaseAIGenerator):
    """使用本地语言模型的生成器。"""

    def generate(self, instruction: str) -> str:
        """调用本地语言模型API生成文本。
        Args:
            instruction (str): 输入提示。
        Returns:
            str: 生成的文本。
        """
        model_url = "http://182.254.242.30:5001"
        url = f"{model_url}/v1/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": instruction,
            "max_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 20,
            "seed": -1,
            "stream": False
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and data['choices']:
                return data['choices'][0]['text']
            else:
                raise Exception("响应中没有找到有效的 'choices' 数据")
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")

    def generate_with_context(self, instruction: str, question: str) -> str:
        """调用本地语言模型API生成文本，并结合额外问题。
        Args:
            instruction (str): 输入提示。
            question (str): 额外的问题。
        Returns:
            str: 生成的文本。
        """
        final_prompt = instruction + "\nQuestion:" + question + "\nAnswer:"
        return self.generate(final_prompt)


