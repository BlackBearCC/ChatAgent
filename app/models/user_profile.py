from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = 'UserProfiles'
    id = Column(Integer, name="UserId",primary_key=True)
    name = Column(String(255),name="Name", nullable=False)
    interests = Column(Text, name="Interests", nullable=True)
    personality = Column(Text, name="Personality", nullable=True)
    emotional_state = Column(Text, name="EmotionalState", nullable=True)
    physical_state = Column(Text, name="PhysicalState", nullable=True)
    location = Column(Text, name="Location", nullable=True)
    action = Column(Text, name="Action", nullable=True)
    session_id = Column(String(255), name="SessionId", nullable=False)