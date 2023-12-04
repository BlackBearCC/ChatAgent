import re

from ai_generator import AIGenerator
from model_type import ModelType


# 根据action_input参数返回一个字符串
def some_function(action_input):
    # 如果需要根据action_input定制化返回结果，可以在这里实现
    # 目前函数只是返回一个示例字符串
    return "沙发，红色；桌子，黄色"

# 根据动作名称执行相应的函数，并处理异常情况
def execute_action(action, action_input):
    try:
        if action == "游戏知识查询":
            return some_function(action_input)
        else:
            raise ValueError(f"不支持的动作: {action}")
    except Exception as e:
        return f"动作执行错误: {str(e)}"


# 发送请求到LLM并获取响应
def send_request(step_input):
    llm = AIGenerator(model_type=ModelType.OPENAI)
    result = llm.generate(system_prompt=step_input)
    return result


class ResponseParse:
    def __init__(self):
        self.temp_context = []  # 初始化临时上下文作为类的属性

    def _parse(self, response: str):

        # 检查是否应该结束
        if "最终回答:" in response:
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

# 处理响应
    def process_response(self, response):
        try:
            while True:
                parsed_result = self._parse(response)

                if parsed_result["type"] == "finish":
                    self.temp_context.clear()
                    return parsed_result["output"]

                if parsed_result["type"] == "action":
                    action_input_index = response.find(parsed_result["input"])
                    self.temp_context.append(response[:action_input_index])
                    action_result = execute_action(parsed_result["action"], parsed_result["input"])  # 执行动作
                    observation = f"观察: {action_result}"  # 生成观察结果
                    self.temp_context.append(observation)  # 将观察结果加入到临时上下文中
                    step_input = ''.join(self.temp_context)  # 生成下一步的输入
                    response = send_request(step_input)
        except Exception as e:
            return f"处理响应时出错: {str(e)}"










