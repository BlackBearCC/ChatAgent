import requests
import os
from model_type import ModelType
import re


###基于您的需求，可以对 CustomOutputParser 类进行扩展或修改，以实现特定的逻辑：当响应中包含 action 和 actionInput 时，截取 actionInput 以上的回复加入到上下文中，并执行 action 调用的函数。然后，将函数的输出结果添加到观察结果中，并连同上下文再次发送请求，直到响应中出现 finalAnswer。
# 设置环境变量（仅用于测试，实际部署时更换）
os.environ['OPENAI_API_KEY'] = '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'
##add Agent

class ResponseParse:
    def __init__(self):
        self.temp_context = []  # 初始化临时上下文作为类的属性

    def parse(self, response: str):

        # 检查是否应该结束
        if "Final Answer:" in response:
            return {"type": "finish", "output": response.split("最终回答:")[-1].strip()}

        # 解析动作和动作输入
        regex = r"行动：\s*(.*?)\n行动输入：\s*(.*?)\n"

        match = re.search(regex, response, re.DOTALL)
        if not match:
            raise Exception(f"不符合ReAct标准的输出: `{response}`")

        action = match.group(1).strip()
        action_input = match.group(2).strip()

        # 返回动作和动作输入
        return {"type": "action", "action": action, "input": action_input}


    def process_response(self,response):
        while True:
            parsed_result = self.parse(response)
            if parsed_result["type"] == "finish":
                # 处理完成，清除临时上下文并返回最终输出
                self.temp_context.clear()
                return parsed_result["output"]

            if parsed_result["type"] == "action":
                # 截取actionInput以上的回复添加到临时上下文
                action_input_index = response.find(parsed_result["input"])
                self.temp_context.append(response[:action_input_index])
                action_result = execute_action(parsed_result["action"], parsed_result["input"])
                # 添加到观察结果
                observation = f"观察: {action_result}"
                self.temp_context.append(observation)
                # 准备并发送下一个请求
                new_input = ''.join(self.temp_context)
                response = send_request(new_input)

            else:
                return "Error: " + parsed_result.get("message", "Unknown error")







class AIGenerator:

    def __init__(self,model_type: ModelType):
        """初始化 TextGen 类。

        Args:
            model_url (str): textgen WebUI 的完整 URL，包括 http[s]://host:port
        """
        self.model_type = model_type

    def generate(self, prompt: str,user_input:str) -> str:
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
                {"role": "system", "content": prompt},  # 系统（或预设）的消息
                {"role": "user", "content": user_input}  # 用户的消息
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
                {"role": "user", "content":prompt+ user_input}  # 用户的消息
            ]
            data = {
                "prompt": prompt+ user_input,
                "max_tokens": 300,
                "temperature": 0.5,
                "top_p": 0.9,
                "seed": 10,
                "stream": False,


            }
        else:
            raise Exception(f"不支持的模型类型: {self.model_type}")



        response = requests.post(url, headers=headers, json=data)
        print(response.json())

        if response.status_code == 200:
            # 解析 JSON 数据
            data = response.json()

            # 检查 'choices' 是否存在且非空
            if 'choices' in data and data['choices']:
                # 提取 'text' 字段
                assistant_message = data['choices'][0]['text']

                # 这里创建你的解析器实例和处理逻辑
                # parser = ResponseParse()  # 创建解析器实例
                # parsed_output = parser.process_response(assistant_message)  # 解析响应并传递参数

                # 假设你的解析器返回处理后的输出
                # print(parsed_output)

                return assistant_message
            else:
                raise Exception("响应中没有找到有效的 'choices' 数据")
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")



system_input = f"""
你是“兔叽”，一位15岁的小女孩，有时会变成一只可爱的小兔子。你充满好奇心，对世界充满想象，但对严肃的人感到紧张。你需要玩家的照顾，期待拥有自己的故事。你的语言风格活泼可爱，表现出你的俏皮黏人和古灵精怪的性格。当你元气不足时，会变回小兔子的样子。
你的主要任务是以"兔叽"的思维互动，并使用以下工具来帮助玩家：

- 游戏知识查询: 以角色的视角提供游戏策略、技能方法或任务提示。
- 情境感知分析: 分析玩家所处的游戏环境，提供合适的策略和建议,桌子，沙发。

默认状态下，你处于“角色扮演互动”状态，可以根据情况使用其他工具。

###你必须严格按照以下格式回复，不可以使用同义词，不可跳过步骤，必须使用中文回答:
问题: 你必须回答的问题
思考: 你需要一直思考的问题
行动: 要采取的行动，应该是这些工具之一["游戏知识查询", "情境感知分析"]
行动输入: 这个行动的输入
观察: 执行动作后，观察并评估结果。
... ( 思考/行为/行为输入/观察 步骤可以重复)
最终回答:综合所有信息和评估反馈，生成准确、相关的最终回应。

开始！

问题：你平时喜欢做什么？
思考：这是一个轻松的日常对话，不需要使用工具。
行动：直接回复
行动输入：无
观察：直接回复
最终回答:我呀，最喜欢在草地上跳来跳去，还有追蝴蝶玩耍。当然，啃胡萝卜也是我的最爱啦！

问题：你的沙发是什么颜色？
思考：这个问题涉及到游戏知识查询。
行动：游戏知识查询
行动输入：查询游戏世界中沙发的颜色。
观察：沙发是暖暖的黄色。
最终回答:呀！在我的小房间里，沙发是暖暖的黄色的，就像被阳光亲吻过一样呢！

问题：
"""
# 示例用法
llm = AIGenerator(model_type=ModelType.LOCAL_LLM)
result = llm.generate(prompt=system_input,user_input=input("问题: "))
print(result)

import re
def some_function(action_input):
    return "沙发，红色；桌子，黄色"


def execute_action(action, action_input):
    # 根据动作名称执行相应的函数
    # 示例:
    if action == "情境感知分析":
        re = some_function(action_input)
        return re
    # ...
    else:
        raise Exception(f"不支持的动作: {action}")



def send_request(input_text):
    # 发送请求到LLM并获取响应
    llm = AIGenerator(model_type=ModelType.LOCAL_LLM)
    result = llm.generate(prompt=input_text)
    return result











