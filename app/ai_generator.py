import asyncio
import re
import time
from abc import ABC, abstractmethod
from http import HTTPStatus

import aiohttp
import httpx
import requests
import os

from langchain_community.chat_message_histories import MongoDBChatMessageHistory, FileChatMessageHistory

from app import prompt
import dashscope

dashscope.api_key = "sk-dc356b8ca42c41788717c007f49e134a"
###基于您的需求，可以对 CustomOutputParser 类进行扩展或修改，以实现特定的逻辑：当响应中包含 action 和 actionInput 时，截取 actionInput 以上的回复加入到上下文中，并执行 action 调用的函数。然后，将函数的输出结果添加到观察结果中，并连同上下文再次发送请求，直到响应中出现 finalAnswer。
# 设置环境变量（仅用于测试，实际部署时更换）
os.environ['OPENAI_API_KEY'] = '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'

import json
from fastapi import FastAPI, HTTPException


##sk-dc356b8ca42c41788717c007f49e134a

class BaseAIGenerator(ABC):
    """AI文本生成器的基类，定义了生成器的基本结构和必须实现的方法。"""

    def __init__(self):
        self.response_text = ""  # 存储生成的响应文本

    @abstractmethod
    def generate_normal(self, prompt: str, callback=None):
        """生成正常文本的方法，需要在子类中实现，并支持回调功能。

        Args:
            prompt (str): 输入提示。
            callback (function): 回调函数，用于处理生成的文本。
        """
        pass

    @abstractmethod
    def config_llm(self):
        """配置语言模型，需要在子类中实现。"""
        pass

    def get_response_text(self):
        """获取当前的响应文本。"""
        return self.response_text
class LocalLLMGenerator(BaseAIGenerator):
    """使用本地语言模型的生成器。"""

    def __init__(self):
        super().__init__()
        self.model_url = "http://182.254.242.30:5001"
        self._usage = "None"

    def config_llm(self):
        url = f"{self.model_url}/v1/completions"
        headers = {"Content-Type": "application/json"}
        return url, headers

    def generate_normal(self, prompt: str, callback=None):
        url, headers = self.config_llm()
        data = {
            "prompt": prompt,
            "max_tokens": 200,
            "temperature": 0.5,
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

                    if callback:
                        callback(self.response_text,self._usage)

                except (KeyError, IndexError, TypeError) as e:
                    raise Exception(f"解析响应时出错: {e}")
            else:
                raise Exception("响应中没有找到有效的 'choices' 数据")
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")


class OpenAIGenerator(BaseAIGenerator):
    """使用 OpenAI API 进行文本生成的生成器。"""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_url = "https://api.openai.com"

    def config_llm(self):
        """配置 OpenAI API 的URL和请求头。"""
        url = f"{self.model_url}/v1/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        return url, headers

    def generate_normal(self, prompt: str, callback=None):
        """使用 OpenAI API 生成文本，并支持回调功能。

        Args:
            prompt (str): 输入提示。
            callback (function): 回调函数，用于处理生成的文本。
        """
        url, headers = self.config_llm()
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and data['choices']:
                try:
                    self.response_text = data['choices'][0]['message']['content']
                    if callback:
                        callback(self.response_text)
                except (KeyError, IndexError, TypeError) as e:
                    raise Exception(f"解析响应时出错: {e}")
            else:
                raise Exception("响应中没有找到有效的 'choices' 数据")
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")

# class ChatGlmGenerator(BaseAIGenerator):
#     """使用 ChatGPT LLM 进行文本生成的生成器。"""
#
#     def generate_normal(self, prompt: str, callback=None):
#         pass
#
#     def config_llm(self):
#         pass
#
#     def async_sync_call_streaming(self, prompt: str, callback=None, session_id=None):
#         from zhipuai import ZhipuAI
#         client = ZhipuAI(api_key="34db50950083f87397175d443f7404a3.QvOuGFfMerpYgQEE")  # 请填写您自己的APIKey
#         response = client.chat.completions.create(
#             model="glm-4",  # 填写需要调用的模型名称
#             temperature=0.8,
#             messages=[
#                 {"role": "user",
#                  "content":f"{prompt}"},
#             ],
#             stream=False,
#         )
#         print(response.choices[0].message)


class QianWenGenerator(BaseAIGenerator):
    """QianWenGenerator 类，一个专门用于生成特定类型文本的生成器。"""

    def __init__(self):
        super().__init__()
        self._final_answer = ""
        self._topic_changed = False
        self._usage = ""
        self._response_text = ""


    def generate_normal(self, prompt: str, callback=None):
        messages = [{"role": "user", "content": prompt}]
        response =dashscope.Generation.call(
            dashscope.Generation.Models.qwen_max_longcontext,
            stream=True,
            messages=messages,
            result_format='message',  # set the result to be "message" format.
        )

        if response.status_code == HTTPStatus.OK:

            # 假设data包含了生成的文本
            try:
                self._response_text = response['output']['choices'][0]['message']['content']
                self._usage = response['usage']
                if callback:
                    callback(self._response_text, self._usage)
            except KeyError as e:
                raise Exception(f"解析响应时出错: {e}")
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")


    async def async_sync_call_streaming(self,prompt_text,callback=None,session_id=None,query=None):
        # DASHSCOPE_API_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
        # headers = {
        #     'Authorization': f'Bearer sk-dc356b8ca42c41788717c007f49e134a',
        #     'Content-Type': 'application/json',
        #     'X-DashScope-SSE': 'enable',
        # }
        # data = {
        #     "model": "qwen-max-longcontext",
        #     "temperature": 1,
        #     "input": {
        #         "messages": [
        #             {
        #                 "role": "user",
        #                 "content":f"{prompt_text}"
        #             }
        #         ]
        #     },
        #     "parameters": {
        #     }
        # }




        DASHSCOPE_API_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
        messages = [
            {'role': 'user', 'content': f"{prompt_text}"}]
        response_generator = dashscope.Generation.call(
            model='qwen-max-longcontext',

            prompt=f"{prompt_text}",
            stream=True,
            incremental_output=False,
            temperature=1,
            top_k=66,
            top_p=0.9)
        for response in response_generator:
            if response.status_code == HTTPStatus.OK:
                print(response.output)  # The output text
                self._response_text = response.output.text
                # event_data = {
                #     "event": response.output.finish_reason,
                #     "data": response.output.text,  # 使用文本内容作为事件数据
                #     # 可以添加其他支持的字段，如 event, id
                # }
                data = response.output.text.replace("\n", "\\n")
                yield data
                if response.output.finish_reason== 'stop':
                    if callback:
                        await callback(response.output.text, session_id, query)
                # yield json.dumps(self._response_text).encode('utf-8')



                # print(response.output.text)  # The usage information


                # for item in response.output:
                #     # 将每个 JSON 对象转换为字符串并编码为字节
                #     yield json.dumps(item).encode('utf-8')
                #     yield b'\n'  # 添加换行符以分隔 JSON 对象
            else:
                event_data = {
                    "event": response.status_code,
                    "data": response.message,  # 使用文本内容作为事件数据
                    # 可以添加其他支持的字段，如 event, id
                }
                print(response)
                yield event_data
                # print(response.code)  # The error code.
                # print(response.message)  # The error message.

        # async with aiohttp.ClientSession() as session:
        #     async with session.post(DASHSCOPE_API_URL, headers=headers, json=data) as response:
        #         async for res in response.output.text:
        #             yield res
        #
        #             if callback:
        #                 await callback(res,session_id,query)



        paragraph = ''
        # response_generator = dashscope.Generation.call(
        #     model='qwen-max-longcontext',
        #     prompt=prompt_text,
        #     stream=True,
        #     top_p=0.9)
        # for response in response_generator:
        #     if response.status_code == HTTPStatus.OK:
        #         print(response.output)  # The output text
        #         self._response_text = response.output.text
        #         yield json.dumps(self._response_text).encode('utf-8')
        #         print(response.usage)  # The usage information
        #         # for item in response.output:
        #         #     # 将每个 JSON 对象转换为字符串并编码为字节
        #         #     yield json.dumps(item).encode('utf-8')
        #         #     yield b'\n'  # 添加换行符以分隔 JSON 对象
        #     else:
        #         print(response.code)  # The error code.
        #         print(response.message)  # The error message.

        # chat_content = paragraph
        # for i in range(200):  # 示例：产生10行文本
        #     yield f"line {i}\n"
        # if callback:
        #     self._response_text = response_generator
        #     await callback(self._response_text)
        #     yield  self._response_text
        # self._response_text = response_generator
    def get_final_answer(self):
        """获取最终答案文本。"""
        return self._final_answer

    def get_topic_changed(self) -> bool:
        """检查话题是否改变。"""
        return self._topic_changed
    
    def get_response_text(self):
        """获取当前的响应文本。"""
        return self._response_text
    
    def config_llm(self):
        # 配置您的QianWen语言模型
        pass




    # def __init__(self):
    #     super().__init__()
    #     self._final_answer = ""
    #     self._history_data = []
    #     self._topic_changed = False
    #
    #     # self._history_data = []
    #
    # def history2(self, history2: list):
    #     self._history_data = history2
    #     return self
    #
    # def get_history(self):
    #     return self._history_data
    #
    # def generate_normal(self, prompt: str):
    #     pass
    #
    # def generate_with_rag(self, prompt):
    #     GREEN = '\033[32m'
    #     RESET = '\033[0m'
    #     history2 = self._history_data
    #
    #     def print_colored_sections(text, keywords, end_keyword):
    #         final_answer_start = text.find(end_keyword)
    #         if final_answer_start != -1:
    #             # 将"FINAL ANSWER"及其后的文本设置为绿色
    #             final_answer_end = len(text)
    #             green_section = f"\033[92m{text[final_answer_start:final_answer_end]}\033[0m"
    #             text = text[:final_answer_start] + green_section
    #
    #         for keyword in keywords:
    #             start = text.find(keyword)
    #             if start != -1:
    #                 end = text.find(end_keyword, start)
    #                 if end == -1:
    #                     end = len(text)
    #                 # 将关键字到结束关键字之间的文本设置为蓝色
    #                 colored_section = f"\033[94m{text[start:end]}\033[0m"
    #                 text = text[:start] + colored_section + text[end:]
    #         print(text)
    #
    #     # if self._history_data:
    #
    #     # else:
    #     #     final_prompt = f"<|im_start|>{instruction}\n 参考资料:\n{context}\n{prompt.RAG}\n<|im_end|>\n{prompt.REACT_FEW_SHOT}\nuser:{query}\n兔叽:"
    #
    #     messages = [{"role": "user", "content": prompt}]
    #     response = dashscope.Generation.call(
    #         dashscope.Generation.Models.qwen_max,
    #         messages=messages,
    #         result_format='message',  # set the result to be "message" format.
    #     )
    #     if response.status_code == HTTPStatus.OK:
    #
    #         self.response_text = response['output']['choices'][0]['message']['content']
    #         print(self.response_text)
    #         keywords = ["THOUGHT", "ACTION", "OBSERVATION"]
    #         end_keyword = "FINAL_ANSWER"
    #         text = f"\n思维链===>\n{self.response_text}"
    #         print_colored_sections(text, keywords, end_keyword)
    #         parts = text.split("FINAL_ANSWER")
    #         if len(parts) > 1:
    #             answer_parts = parts[1].split("TOPIC_CHANGED")
    #
    #             if answer_parts:
    #                 self._final_answer = answer_parts[0].strip()
    #
    #                 cleaned_text = re.sub(r'[^a-zA-Z]', '', answer_parts[1].strip())
    #                 self._topic_changed = cleaned_text
    #             else:
    #                 raise ValueError("未找到指定关键词后的内容")
    #         else:
    #             raise ValueError("未找到指定关键词后的内容")
    #     else:
    #         raise Exception(f"请求失败，状态码: {response.status_code}")
    #     return self
    #
    # def get_final_answer(self):
    #     return self._final_answer
    #
    # def get_topic_changed(self) -> bool:
    #     return self._topic_changed
    #
    # keywords = ["THOUGHT", "ACTION", "OBSERVATION"]
    #
    # # 打印文本，关键字部分为蓝色
    # # print_colored_keywords(text, keywords)
    # def config_llm(self):
    #     pass

