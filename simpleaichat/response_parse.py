import re

from ai_generator import AIGenerator
from model_type import ModelType


# from model_type import ModelType
# from textgen import AIGenerator


def some_function(action_input):
    return "沙发，红色；桌子，黄色"


def execute_action(action, action_input):
    # 根据动作名称执行相应的函数
    # 示例:
    if action == "游戏知识查询":
        re = some_function(action_input)
        return re
    # ...
    else:
        raise Exception(f"不支持的动作: {action}")


def send_request(step_input):
    # 发送请求到LLM并获取响应
    llm = AIGenerator(model_type=ModelType.OPENAI)
    result = llm.generate(system_prompt=step_input)
    return result


class ResponseParse:
    def __init__(self):
        self.temp_context = []  # 初始化临时上下文作为类的属性

    def _parse(self, response: str):

        # 检查是否应该结束
        if "Final Answer:" in response:
            return {"type": "finish", "output": response.split("Final Answer:")[-1].strip()}

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
            parsed_result = self._parse(response)
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
                step_input = ''.join(self.temp_context)
                response = send_request(step_input)

            else:
                return "Error: " + parsed_result.get("message", "Unknown error")










