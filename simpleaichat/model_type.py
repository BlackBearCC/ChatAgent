from enum import Enum

class ModelType(Enum):
    """模型类型枚举类。"""
    LOCAL_LLM = "local_llm"
    OPENAI = "openai"