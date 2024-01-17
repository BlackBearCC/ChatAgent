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
        # self._history_data = False
        self._history_data = []  # 初始化一个空的历史记录列表
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

    def history(self, history: list):
        self._history_data = history
        return self

    def update_history(self):
        # self.history_data.append((query, generated_text))
        return self  # 返回self以支持链式调用

    @abstractmethod
    def config_llm(self):
        """内部方法：在子类中实现具体的文本生成逻辑。"""
        raise NotImplementedError

    def get_history(self):
        """获取当前的历史记录。"""
        return self._history_data

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

    # def history_data(self):
    #     self.history_data = []
    #     return self

    def generate_normal(self, instruction: str, query: str):
        url = self.config_llm()[0]
        headers = self.config_llm()[1]
        final_prompt = f"{instruction}\n 问:{self._history_data}{query}\n预期输出:"
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
                try:
                    self.response_text = data['choices'][0]['text']

                except (KeyError, IndexError, TypeError) as e:
                    raise Exception(f"解析响应时出错: {e}")
                # if self._history_data:
                #     self.question_text = f"\nuser:{query}"
                #     self.response_text = f"\n兔叽:{data['choices'][0]['text']}"
                #     self._history_data.append((self.question_text, self.response_text))
                #     print(self.question_text)
                #     print(self.response_text)
                # else:
                #     self.response_text = data['choices'][0]['text']
            else:
                raise Exception("响应中没有找到有效的 'choices' 数据")
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")
        return self

    def get_response_text(self):
        return super().get_response_text()

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
                try:
                    self.response_text = data['choices'][0]['text']
                    print(self.response_text)
                except (KeyError, IndexError, TypeError) as e:
                    raise Exception(f"解析响应时出错: {e}")
                # if self._history_data:
                #     self.question_text = f"\nuser:{query}"
                #     self.response_text = f"\n兔叽:{data['choices'][0]['text']}"
                #     self._history_data.append((self.question_text, self.response_text))
                #     print(self.question_text)
                #     print(self.response_text)
                # else:
                #     self.response_text = data['choices'][0]['text']
            else:
                raise Exception("响应中没有找到有效的 'choices' 数据")
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")
        return self

    def update_history(self):
        return super().update_history()

    def get_response_text(self):
        return super().get_response_text()

class IntentionGenerator(LocalLLMGenerator):
    def __init__(self):
        super().__init__()
        self._intent_history = []

    def generate_normal(self, instruction: str, query: str):
        url = self.config_llm()[0]
        headers = self.config_llm()[1]
        final_prompt = f"{instruction}\n 问:{self._intent_history}{query}\n预期输出:"
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
                try:
                    self.response_text = data['choices'][0]['text']

                except (KeyError, IndexError, TypeError) as e:
                    raise Exception(f"解析响应时出错: {e}")
                # if self._history_data:
                #     self.question_text = f"\nuser:{query}"
                #     self.response_text = f"\n兔叽:{data['choices'][0]['text']}"
                #     self._history_data.append((self.question_text, self.response_text))
                #     print(self.question_text)
                #     print(self.response_text)
                # else:
                #     self.response_text = data['choices'][0]['text']
            else:
                raise Exception("响应中没有找到有效的 'choices' 数据")
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")
        return self
    def history(self, history: list):
        self._intent_history = history
        return self
    def update_history(self):
        super().update_history()

    def config_llm(self):
        super().config_llm()
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
        self._final_answer = ""
        self._history_data = []
        self._topic_changed = False

        # self._history_data = []

    def history(self, history: list):
        self._history_data = history
        return self

    def get_history(self):
        return self._history_data

    def generate_normal(self, instruction: str, query: str):
        pass

    def generate_with_rag(self, instruction: str, context: str, query: str):
        GREEN = '\033[32m'
        RESET = '\033[0m'
        history = self._history_data

        def print_colored_sections(text, keywords, end_keyword):
            final_answer_start = text.find(end_keyword)
            if final_answer_start != -1:
                # 将"FINAL ANSWER"及其后的文本设置为绿色
                final_answer_end = len(text)
                green_section = f"\033[92m{text[final_answer_start:final_answer_end]}\033[0m"
                text = text[:final_answer_start] + green_section

            for keyword in keywords:
                start = text.find(keyword)
                if start != -1:
                    end = text.find(end_keyword, start)
                    if end == -1:
                        end = len(text)
                    # 将关键字到结束关键字之间的文本设置为蓝色
                    colored_section = f"\033[94m{text[start:end]}\033[0m"
                    text = text[:start] + colored_section + text[end:]
            print(text)

        # if self._history_data:
        final_prompt = f"<|im_start|>{instruction}\n 参考资料:\n{context}\n{prompt.RAG}\n历史记录：{history}\n回答流程：\n{prompt.AGENT_REACT}\n<|im_end|>\n{prompt.REACT_FEW_SHOT}\nuser:{query}\n兔叽:"
        # else:
        #     final_prompt = f"<|im_start|>{instruction}\n 参考资料:\n{context}\n{prompt.RAG}\n<|im_end|>\n{prompt.REACT_FEW_SHOT}\nuser:{query}\n兔叽:"

        messages = [{"role": "user", "content": final_prompt}]
        response = dashscope.Generation.call(
            dashscope.Generation.Models.qwen_max,
            messages=messages,
            result_format='message',  # set the result to be "message" format.
        )
        if response.status_code == HTTPStatus.OK:
            # print(response)
            # self.question_text = f"\nuser:{query}"
            # self.response_text = f"\n兔叽：{response['output']['choices'][0]['message']['content']}"
            # self._history_data.append((self.question_text, self.response_text))
            self.response_text = response['output']['choices'][0]['message']['content']
            keywords = ["THOUGHT", "ACTION", "OBSERVATION"]
            end_keyword = "FINAL ANSWER"
            text = f"\n思维链===>\n{self.response_text}"
            print_colored_sections(text, keywords, end_keyword)
            parts = text.split("FINAL_ANSWER:")
            if len(parts) > 1:
                answer_parts = parts[1].split("TOPIC_CHANGED:")
                if answer_parts:
                    self._final_answer = answer_parts[0].strip()
                    self._topic_changed = answer_parts[1].strip()
                else:
                    raise ValueError("未找到指定关键词后的内容")
            else:
                raise ValueError("未找到指定关键词后的内容")
        else:
            raise Exception(f"请求失败，状态码: {response.status_code}")
        return self

    def get_final_answer(self):
        return self._final_answer

    def get_topic_changed(self) -> bool:
        return self._topic_changed

    keywords = ["THOUGHT", "ACTION", "OBSERVATION"]

    # 打印文本，关键字部分为蓝色
    # print_colored_keywords(text, keywords)
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
