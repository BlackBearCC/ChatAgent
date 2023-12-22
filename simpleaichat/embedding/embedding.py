import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel





# 初始化嵌入模型
class Embedding:
    def __init__(self, model_name: str, scores_callback=None):
        # 加载预训练模型的分词器
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        # 加载预训练的模型本身
        self.model = AutoModel.from_pretrained(model_name)
        self.scores_callback = scores_callback

    # 对给定文本进行编码，返回嵌入向量
    def encode(self, texts: list) -> Tensor:
        # 使用分词器处理文本，限制最大长度为512，开启填充和截断，并将结果转换为PyTorch张量
        batch_dict = self.tokenizer(texts, max_length=512, padding=True, truncation=True, return_tensors='pt')
        # 通过模型获取嵌入输出
        outputs = self.model(**batch_dict)
        # 获取每个输入文本的第一个令牌的隐藏状态，通常用作序列的代表性嵌入
        embeddings = outputs.last_hidden_state[:, 0]
        # 使用L2范数对嵌入向量进行正则化
        embeddings = F.normalize(embeddings, p=2, dim=1)
        # 假设 embeddings 是通过上述类获取的一系列文本嵌入
        scores = (embeddings[:1] @ embeddings[1:].T) * 100
        # 计算第一个嵌入向量与其他所有嵌入向量的点积，得到相似性得分
        # 在调用回调函数之前检查它是否存在
        if self.scores_callback:
            self.scores_callback(scores.tolist())

        return embeddings








