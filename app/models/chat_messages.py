from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func

Base = declarative_base()

class ChatMessages(Base):
    __tablename__ = 'ChatMessages'

    id = Column(Integer, primary_key=True, name='Id')
    session_id = Column(String(255), nullable=True, name='SessionId')  # 会话ID
    user_id = Column(Integer, nullable=True, name='UserId')  # 用户ID
    character_id = Column(Integer, nullable=True, name='CharacterId')  # 角色ID
    message = Column(JSON, nullable=True, name='Message')  # 消息内容
    attachments = Column(JSON, nullable=True, name='Attachments')  # 附件，存储为JSON字符串
    created_at = Column(TIMESTAMP, server_default=func.now(), name='CreatedAt')  # 创建时间
