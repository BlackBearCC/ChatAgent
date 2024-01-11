from abc import ABC, abstractmethod
from http import HTTPStatus

import requests
import os

from langchain_community.chat_message_histories import MongoDBChatMessageHistory, FileChatMessageHistory

from simpleaichat import prompt
import dashscope

dashscope.api_key = "sk-dc356b8ca42c41788717c007f49e134a"
###基于您的需求，可以对 CustomOutputParser 类进行扩展或修改，以实现特定的逻辑：当响应中包含 action 和 actionInput 时，截取 actionInput 以上的回复加入到上下文中，并执行 action 调用的函数。然后，将函数的输出结果添加到观察结果中，并连同上下文再次发送请求，直到响应中出现 finalAnswer。
# 设置环境变量（仅用于测试，实际部署时更换）
os.environ['OPENAI_API_KEY'] = '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'


##sk-dc356b8ca42c41788717c007f49e134a

class BaseAIGenerator(ABC):
    """AI文本生成器的基类。"""

    def __init__(self):
        self.response_text = ""
        self._use_history = False
        self._history = []  # 初始化一个空的历史记录列表
        self.question_text = ""

    @abstractmethod
    def generate_normal(self, instruction: str, query: str):
        return self

    @abstractmethod
    def generate_with_rag(self, instruction: str, context: str, query: str):
        """生成带有额外查询的文本的方法，需要在子类中实现。
        Args:
            instruction (str): 输入提示。
            context (str): 上下文。
            query (str): 查询问题。
        Returns:
            str: 生成的文本。
        """
        return self

    def history(self):
        self._use_history = True
        return self

    def update_history(self):
        # self.history.append((query, generated_text))
        return self  # 返回self以支持链式调用

    @abstractmethod
    def config_llm(self):
        """内部方法：在子类中实现具体的文本生成逻辑。"""
        raise NotImplementedError

    def get_history(self):
        """获取当前的历史记录。"""
        return self._history

    def get_response_text(self):
        """获取当前的回复"""
        return self.response_text


class LocalLLMGenerator(BaseAIGenerator):
    """使用本地语言模型的生成器。"""

    def __init__(self):
        super().__init__()

    def config_llm(self):
        model_url = "http://182.254.242.30:5001"
        url = f"{model_url}/v1/completions"
        # url = f"{model_url}/v1/chat/completions" ##chat模式
        headers = {"Content-Type": "application/json"}
        return url, headers

    # def history(self):
    #     self.history = []
    #     return self

    def generate_normal(self, instruction: str, query: str):
        url = self.config_llm()[0]
        headers = self.config_llm()[1]
        final_prompt = f"{instruction}\n 问:{query}\n兔叽:"


    def generate_with_rag(self, instruction: str, context: str, query: str):
        url = self.config_llm()[0]
        headers = self.config_llm()[1]
        history = self.get_history()
        final_prompt = f"<|im_start|>{instruction}\n 参考资料:\n{context}\n{prompt.RAG}\n历史记录：{history}\n<|im_end|>\nuser:{query}\n兔叽:"
        data = {
            "prompt": final_prompt,
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
                if self._use_history:
                    self.question_text = f"\nuser:{query}"
                    self.response_text = f"\n兔叽:{data['choices'][0]['text']}"
                    self._history.append((self.question_text, self.response_text))
                    print(self.question_text)
                    print(self.response_text)
                else:
                    self.response_text = data['choices'][0]['text']
            else:
                raise Exception("响应中没有找到有效的 'choices' 数据")
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")
        return self

    def update_history(self):
        return super().update_history()

    def get_response_text(self):
        return super().get_response_text()


class OpenAIGenerator(BaseAIGenerator):

    def generate_normal(self, instruction: str, query: str):
        super().generate_normal()

    def update_history(self):
        super().update_history()

    def config_llm(self):
        model_url = "https://api.openai.com"
        url = f"{model_url}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY")
        }
        return url, headers

    def generate_with_rag(self, instruction: str, context: str, query: str):
        url = self.config_llm()[0]
        headers = self.config_llm()[1]
        history = self.get_history()
        final_prompt = f"<|im_start|>{instruction}\n 参考资料:\n{context}\n{prompt.RAG}\n历史记录：{history}\n<|im_end|>\nuser:{query}\n兔叽:"

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": final_prompt}]
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and data['choices']:
                try:
                    self.response_text = data['choices'][0]['message']['content']
                    print(self.response_text)
                except (KeyError, IndexError, TypeError) as e:
                    raise Exception(f"解析响应时出错: {e}")
            else:
                raise Exception("响应中没有找到有效的 'choices' 数据")
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")
        return self


class QianWenGenerator(BaseAIGenerator):
    def __init__(self):
        super().__init__()
        # self._history = []

    def history(self):
        super().history()

    def generate_normal(self, instruction: str, query: str):
        pass

    def generate_with_rag(self, instruction: str, context: str, query: str):
        GREEN = '\033[32m'
        RESET = '\033[0m'
        history = self.get_history()
        if self._use_history:
            final_prompt = f"<|im_start|>{instruction}\n 参考资料:\n{context}\n{prompt.RAG}\n历史记录：{history}\n<|im_end|>\n{prompt.FEW_SHOT}\nuser:{query}\n兔叽:"
        else:
            final_prompt = f"<|im_start|>{instruction}\n 参考资料:\n{context}\n{prompt.RAG}\n<|im_end|>\n{prompt.FEW_SHOT}\nuser:{query}\n兔叽:"

        messages = [{"role": "user", "content": final_prompt}]
        response = dashscope.Generation.call(
            dashscope.Generation.Models.qwen_max,
            messages=messages,
            result_format='message',  # set the result to be "message" format.
        )
        if response.status_code == HTTPStatus.OK:
            # print(response)
            self.question_text = f"\nuser:{query}"
            self.response_text = f"\n兔叽：{response['output']['choices'][0]['message']['content']}"
            self._history.append((self.question_text, self.response_text))
            print(f"{GREEN}\n========最终回答========={self.response_text}{RESET}")
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
        return self
    def config_llm(self):
        pass
# def _generate_text(self, instruction: str) -> str:
#     url = self.config_llm()[0]
#     headers = self.config_llm()[1]
#     data = {
#         "model": "gpt-3.5-turbo",
#         "messages": [{"role": "user", "content": instruction}]
#     }
#     response = requests.post(url, headers=headers, json=data)
#
#     if response.status_code == 200:
#         data = response.json()
#         if 'choices' in data and data['choices']:
#             try:
#                 return data['choices'][0]['message']['content']
#             except (KeyError, IndexError, TypeError) as e:
#                 raise Exception(f"解析响应时出错: {e}")
#         else:
#             raise Exception("响应中没有找到有效的 'choices' 数据")
#     else:
#         raise Exception(f"API 请求失败，状态码: {response.status_code}")
