import requests

class TextGen:
    def __init__(self, model_url: str):
        """初始化 TextGen 类。

        Args:
            model_url (str): textgen WebUI 的完整 URL，包括 http[s]://host:port
        """
        self.model_url = model_url

    def generate(self, prompt: str, max_new_tokens: int = 250) -> str:
        """调用 textgen Web API 并返回输出。

        Args:
            prompt (str): 用于生成文本的提示。
            max_new_tokens (int): 生成的最大令牌数。

        Returns:
            str: 生成的文本。
        """
        url = f"{self.model_url}/api/v1/generate"
        params = {
            "prompt": prompt,
            "max_new_tokens": max_new_tokens
        }
        response = requests.post(url, json=params)

        if response.status_code == 200:
            return response.json()["results"][0]["text"]
        else:
            raise Exception(f"API 请求失败，状态码: {response.status_code}")

# 使用示例
llm = TextGen(model_url="http://123.60.183.64:5000")
result = llm.generate(prompt="写一个关于太空的故事。")
print(result)
