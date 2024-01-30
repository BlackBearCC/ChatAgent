import re

from ai_generator import AIGenerator
from model_type import ModelType

def generate_steps(text):
    # 构建正则表达式模式，以匹配指定关键字后面的内容
    regex = r"\n思考：(.*?)\n行动：(.*?)\n行动输入：(.*?)\n"
    match = re.search(regex, text, re.DOTALL)
    if match:
        thoughts = match.group(1)  # 提取思考内容
        action = match.group(2)  # 提取行动内容
        action_input = match.group(3)  # 提取行动输入内容
        # 拼接成一个字符串，并以 \n 结尾
        result = f"\n思考: {thoughts}\n行动: {action}\n行动输入: {action_input}\n"
        return result
    else:
        return None



# 根据action_input参数返回一个字符串
def some_function(action_input):
    # 如果需要根据action_input定制化返回结果，可以在这里实现
    # 目前函数只是返回一个示例字符串
    # return "沙发，红色；桌子，黄色"
    return "我喜欢吃西红柿"


# 根据动作名称执行相应的函数，并处理异常情况
def execute_action(action, action_input):
    try:
        if action == "情境感知分析":
            return some_function(action_input)
        else:
            raise ValueError(f"不支持的动作: {action}")
    except Exception as e:
        return f"动作执行错误: {str(e)}"


# 发送请求到LLM并获取响应
def send_request(step_data):
    llm = AIGenerator(model_type=ModelType.LOCAL_LLM)
    result = llm.generate(step_data)
    return result


class ResponseParse:
    def __init__(self, llm_context):
        self.temp_context = []  # 初始化临时上下文作为类的属性
        self.llm_context = llm_context # 初始化llm上下文作为类的属性

    def _parse(self, response: str):

        # 检查是否应该结束
        if "最终回答:" in response:
            return {"type": "finish", "output": response.split("最终回答:")[-1].strip()}

        # 解析动作和动作输入
        regex = r'思考: (.*?)\n行动: (.*?)\n行动输入: (.*?)\n'
        match = re.search(regex, response, re.DOTALL)
        if not match:
            raise Exception(f"不符合ReAct标准的输出: `{response}`")
        action = match.group(2).strip()
        action_input = match.group(3).strip()

        # 返回动作和动作输入
        return {"type": "action", "action": action, "input": action_input}

# 处理响应
    def process_response(self, llm_output):
        # 思路
        # 截取，生成步骤
        # 存为步骤变量
        # 添加“观察”
        # 以上内容发送给llm
        # 解析llm的响应
        # 如果是“最终回答”，则finish
        # 如果是“行动”，则执行动作
        interation_thought_step = ""
        while True:
            # 生成步骤
            thought_step = generate_steps(llm_output)  # 生成步骤的函数，格式化步骤
            interation_thought_step += thought_step

            parsed_result = self._parse(thought_step)
            if parsed_result["type"] == "finish":

                return parsed_result["output"]

            if parsed_result["type"] == "action":


                action_result = execute_action(parsed_result["action"], parsed_result["input"])  # 执行动作
                observation = f"观察: {action_result}\n思考："  # 生成观察结果

                interation_thought_step += observation


                next_input = self.llm_context + interation_thought_step # 生成下一步的输入
                print(next_input)
                llm_output = send_request(next_input)

