from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
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


class ChatSummaries(Base):
    __tablename__ = 'ChatSummaries'
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False)
    # start_message_id = Column(Integer, ForeignKey('ChatMessages.id'), nullable=False)
    # end_message_id = Column(Integer, ForeignKey('ChatMessages.id'), nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP,server_default=func.now(), name='created_at')

    # Optional: If you want to access related messages directly from a ChatSummary object
    messages = relationship('SummaryMessageAssociations', back_populates='summary')


class SummaryMessageAssociations(Base):
    __tablename__ = 'SummaryMessageAssociations'
    id = Column(Integer, primary_key=True)
    summary_id = Column(Integer, ForeignKey('ChatSummaries.id'), nullable=False)
    message_id = Column(Integer, ForeignKey('ChatMessages.Id'), nullable=False)

    # # Relationships
    summary = relationship('ChatSummaries', back_populates='messages')
    message = relationship('ChatMessages', backref='summary_associations')

class Diary(Base):
    __tablename__ = 'Diaries'
    id = Column(Integer, primary_key=True,name="DiaryId")
    session_id = Column(String(255), nullable=False,name='SessionId')
    content = Column(JSON, nullable=True,name='Content')
    created_at = Column(TIMESTAMP, server_default=func.now(), name='CreatedAt')  # 创建时间