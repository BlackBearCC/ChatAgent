from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()

class DialogueManager(Base):
    __tablename__ = 'DialogueManagers'


    id = Column(Integer, primary_key=True, name='DialogueId')
    situation = Column(Text, nullable=True, name='Situation')
    chat_history = Column(JSON, nullable=True, name='ChatHistory')  # 聊天历史，存储为JSON字符串
    topic_history = Column(Text, nullable=True, name='TopicHistory')  # 话题历史
    intent_history = Column(Text, nullable=True, name='IntentHistory')  # 意图历史
    reference = Column(Text, nullable=True, name='Reference')  # 参考
    user_id = Column(Integer, nullable=True, name='UserId')  # 用户ID
    character_id = Column(Integer, nullable=True, name='CharacterId')  # 角色ID
    intention = Column(Text, nullable=True, name='Intention')  # 意图
    summary = Column(Text, nullable=True, name='Summary')  # 摘要
    summary_history = Column(Text, nullable=True, name='SummaryHistory')  # 摘要历史
    extracted_triplets = Column(Text, nullable=True, name='ExtractedTriplets')  # 提取的三元组
    entity_summary = Column(Text, nullable=True, name='EntitySummary')  # 实体摘要
    session_id = Column(String(255), nullable=True, name='SessionId')  # 会话ID
    # def update_chat_history(self, message: str):
    #     if self.chat_history:
    #         history = json.loads(self.chat_history)
    #     else:
    #         history = []
    #     history.append(message)
    #     self.chat_history = json.dumps(history)

    # 类似的方法可以用于其他列表属性
