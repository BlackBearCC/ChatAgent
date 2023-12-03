import re


def some_function(action_input):
        pass


def execute_action(action, action_input):
    # 根据动作名称执行相应的函数
    # 示例:
    if action == "some_action":
        return some_function(action_input)
    # ...

    return "Action not recognized"


def send_request(input_text):
    # 发送请求到LLM并获取响应
    # 这里是一个示例，具体实现取决于您的LLM调用方式
    # ...
    print("send_request")


class ResponseParse:
    def __init__(self):
        self.temp_context = []  # 初始化临时上下文作为类的属性

    def parse(self, response: str):

        # 检查是否应该结束
        if "Final Answer:" in response:
            return {"type": "finish", "output": response.split("Final Answer:")[-1].strip()}

        # 解析动作和动作输入
        regex = r"行动\s*:(.*?)\n行动输入\s*:[\s]*(.*)"
        match = re.search(regex, response, re.DOTALL)
        if not match:
            raise Exception(f"不符合ReAct标准的输出: `{response}`")

        action = match.group(1).strip()
        action_input = match.group(2).strip()

        # 返回动作和动作输入
        return {"type": "action", "action": action, "input": action_input}


    def process_response(self,response):

        parser = ResponseParse()
        parsed_result = parser.parse(response)

        if parsed_result["type"] == "finish":
            # 处理完成，清除临时上下文并返回最终输出
            self.temp_context.clear()
            return parsed_result["output"]

        if parsed_result["type"] == "action":
            # 截取actionInput以上的回复添加到临时上下文
            self.append(response.split(parsed_result["input"])[0])

            # 执行动作
            action_result = execute_action(parsed_result["action"], parsed_result["input"])

            # 添加到观察结果
            observation = f"观察: {action_result}"

            # 连同上下文再次发送请求
            new_input = self.temp_context + observation
            return send_request(new_input)

        return "Error: " + parsed_result.get("message", "Unknown error")







