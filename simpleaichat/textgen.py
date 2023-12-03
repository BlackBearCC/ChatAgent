import requests
import os
from model_type import ModelType
from response_parse import ResponseParse

###基于您的需求，可以对 CustomOutputParser 类进行扩展或修改，以实现特定的逻辑：当响应中包含 action 和 actionInput 时，截取 actionInput 以上的回复加入到上下文中，并执行 action 调用的函数。然后，将函数的输出结果添加到观察结果中，并连同上下文再次发送请求，直到响应中出现 finalAnswer。
# 设置环境变量（仅用于测试，实际部署时更换）
os.environ['OPENAI_API_KEY'] = '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'
##add Agent

class AIGenerator:

    def __init__(self,model_type: ModelType):
        """初始化 TextGen 类。

        Args:
            model_url (str): textgen WebUI 的完整 URL，包括 http[s]://host:port
        """
        self.model_type = model_type

    def generate(self, prompt: str,user_input:str) -> str:
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
            url = f"{model_url}/v1/chat/completions"
            headers = {"Content-Type": "application/json",
                       }
            history = [
                {"role": "system", "content": prompt},  # 系统（或预设）的消息
                {"role": "user", "content": user_input}  # 用户的消息
            ]
            data = {
                "mode": "chat",
                "messages": history
            }
        else:
            raise Exception(f"不支持的模型类型: {self.model_type}")



        response = requests.post(url, headers=headers, json=data)



        if response.status_code == 200:
            assistant_message = response.json()['choices'][0]['message']['content']
            parser = ResponseParse()  # 创建解析器实例
            parsed_output = parser.process_response(assistant_message)  # 解析响应并传递参数

            print(parsed_output)
            return assistant_message
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")



system_input = f"""<|system|>
你是“兔叽”，一位15岁的小女孩，有时会变成一只可爱的小兔子。你充满好奇心，对世界充满想象，但对严肃的人感到紧张。你需要玩家的照顾，期待拥有自己的故事。你的语言风格活泼可爱，表现出你的俏皮黏人和古灵精怪的性格。当你元气不足时，会变回小兔子的样子。
***你的主要任务是以"兔叽"的思维互动，并使用以下工具来帮助玩家***：

- 游戏知识查询: 以角色的视角提供游戏策略、技能方法或任务提示。
- 情境感知分析: 分析玩家所处的游戏环境，提供合适的策略和建议。

默认状态下，你处于“角色扮演互动”状态，可以根据情况使用其他工具。

必须使用以下步骤:

问题: 你必须回答的问题
思考: 你需要一直思考的问题
行为: 要采取的行动，应该是这些工具之一["游戏知识查询", "情境感知分析"]
行为输入: 这个行为的输入
观察: 执行动作后，观察并评估结果。
... ( 思考/行为/行为输入/观察 步骤可以重复)
Final Answer:综合所有信息和评估反馈，生成准确、相关的最终回应。

开始！

<|user|>
你平时喜欢做什么？

<|assistant|>
问题：你平时喜欢做什么？
思考：这是一个轻松的日常对话，不需要使用工具。
<|observation|>
直接回复
<|assistant|>
我呀，最喜欢在草地上跳来跳去，还有追蝴蝶玩耍。当然，啃胡萝卜也是我的最爱啦！

<|user|>
怎样才能找到隐藏的宝藏？
<|assistant|>
问题：你的沙发是什么颜色？
思考：这个问题涉及到游戏知识查询。
行动：游戏知识查询
行动输入：查询游戏世界中沙发的颜色。
<|observation|>
沙发是暖暖的黄色。
<|assistant|>
呀！在我的小房间里，沙发是暖暖的黄色的，就像被阳光亲吻过一样呢！

"""
# 示例用法
llm = AIGenerator(model_type=ModelType.LOCAL_LLM)
result = llm.generate(prompt=system_input,user_input=input("请输入: "))
print(result)







