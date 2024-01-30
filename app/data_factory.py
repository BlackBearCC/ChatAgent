# Function to extract data and save as JSON
import json
import os


def escape_control_characters(s):
    return s.replace("\n", "\\n").replace("\r", "\\r")


def format_item(item):
    # 格式化每一项以确保它以正确的方式呈现
    item = item.strip()
    if not item.startswith('{'):
        item = '{' + item
    if not item.endswith('}'):
        item += '}'

    # 转义控制字符
    item = escape_control_characters(item)
    # 在question和response之间添加换行符
    item = item.replace('",\n "response"', '",\n\n "response"')
    return item


## 格式化数据
def save_formatted_data(file_path, formatted_data, callback=None):
    with open(file_path, 'a', encoding='utf-8') as f:
        for data_item in formatted_data:
            f.write(data_item + "\n")

    if callback:
        callback()


## 保存数据
def extract_and_save_as_json(data, file_path, callback=None):
    # 分割消息并处理每一部分
    items = data.split("\n\n")
    formatted_data = [format_item(item) for item in items]

    # 调用 save_formatted_data 函数
    save_formatted_data(file_path, formatted_data, callback)

# Calling the function with the sample data and the output file pathdata = {dict: 6} {'choices': [{'finish_reason': 'length', 'index': 0, 'logprobs': None, 'text': '"你今天早上吃了什么？",\n response": "thought: 这个问题很简单啊，我吃了一个香喷喷的三明治和一个甜甜圈呢！\naction: 直接回答工具\naction_input: 告诉我今天早上的食物\nobservation: 根据... 讨论好朋友应该具有什么样的特质\nobservation: 根据实际情况回答\nfinal_a... View
