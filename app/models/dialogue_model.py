
from typing import Any, Optional, List

from pydantic import BaseModel


class DialogueManger(BaseModel):
    """对话模型"""
    situation: Optional[str] = None  # 对话情境
    chat_history: Optional[List[str]] = []  # 对话历史
    topic_history: Optional[List[str]] = []  # 话题历史
    intent_history: Optional[List[str]] = []  # 意图历史
    reference: Optional[str] = None  # 参考
    user_name: Optional[str] = None  # 用户名称
    char_name: Optional[str] = None  # 角色名称
    intention: Optional[str] = None  # 意图
    summary: Optional[str] = None  # 摘要
    summary_history: Optional[List[str]] = []  # 摘要历史
    extracted_triplets: Optional[List[str]] = []  # 提取的三元组
    entity_summary: Optional[str] = None  # 实体摘要

    def update_chat_history(self, message: str):
        if self.chat_history is None:
            self.chat_history = []
        self.chat_history.append(message)

