from sqlalchemy.orm import sessionmaker
from .db import engine
from sqlalchemy import update
from app.models.character_profile import CharacterProfile
from ... import prompt
from ...models import UserProfile
from ...models.dialogue_model import DialogueManager
import json
from sqlalchemy.exc import SQLAlchemyError
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_seesion_member(session_id):
    with SessionLocal() as session:
        result = session.execute(
            """
            SELECT
                UP.UserId,
                UP.Name AS UserName,
                UP.Interests AS UserInterests,
                UP.Personality AS UserPersonality,
                UP.EmotionalState AS UserEmotionalState,
                UP.physicalState AS UserPhysicalState,
                UP.location AS UserLocation,
                UP.Action AS UserAction,
                CP.CharacterId,
                CP.Name AS CharacterName,
                CP.Interests AS CharacterInterests,
                CP.Personality AS CharacterPersonality,
                CP.EmotionalState AS CharacterEmotionalState,
                CP.physicalState AS CharacterPhysicalState,
                CP.location AS CharacterLocation,
                CP.Action AS CharacterAction
            FROM
                DialogueManagers DM
            INNER JOIN
                UserProfiles UP ON DM.SessionId = UP.SessionId
            INNER JOIN
                CharacterProfiles CP ON DM.SessionId = CP.SessionId
            WHERE
                DM.SessionId = :session_id;
            """,
            {"session_id": session_id}
        ).fetchone()
        return result


def validate_session_id(session_id):
    with SessionLocal() as session:
        result = session.query(DialogueManager).filter(DialogueManager.session_id == session_id).first()
        if result:
            return True
        else:
            return False


def create_session_id(session_id):
    with SessionLocal() as session:
        try:

            # 创建 User 实例
            user_profile  = UserProfile(name="哥哥",interests="阅读",personality="正常",emotional_state="正常",physical_state="正常",location="客厅",action="站立",session_id=session_id)
            session.add(user_profile)
            # 创建 Character 实例
            character_profile = CharacterProfile(name="兔叽",interests="睡觉",personality="正常",emotional_state="正常",physical_state="正常",location="客厅",action="站立",session_id=session_id)
            session.add(character_profile)
            session.flush()  # Flush 确保分配 ID
            situation = prompt.SITUATION.format(user=user_profile.name, char=character_profile.name)
            # 然后创建 DialogueManager 实例，引用新创建的实体的 ID
            dialogue_manager = DialogueManager(session_id=session_id,
                                               user_id=user_profile.id,
                                               character_id=character_profile.id,
                                               situation=situation,

                                               )
            session.add(dialogue_manager)

            # 提交事务以保存所有新实体
            session.commit()
            return "Session and associated entities created successfully."
        except Exception as e:
            # 出错时回滚事务
            session.rollback()
            return f"Failed to create session and entities: {e}"


def update_character_emotion(session_id, new_emotion):
    with SessionLocal() as session:
        # 构造一个update查询
        query = update(CharacterProfile).where(
            CharacterProfile.session_id == session_id
        ).values(emotional_state=new_emotion)
        # 执行查询
        session.execute(query)
        # 提交更改
        session.commit()


def get_dialogue_manager_by_session_id(session_id: str):
    with SessionLocal() as session:
        result = session.query(DialogueManager).filter(DialogueManager.session_id == session_id).first()
        return result


from app.models.message import UserMessage, AiMessage
def get_chat_history_by_session_id(session_id: str):
    with SessionLocal() as session:
        result = session.query(DialogueManager).filter(DialogueManager.session_id == session_id).first()
        if result and result.chat_history:
            chat_history_dicts = result.chat_history
        else:
            chat_history_dicts = []

        messages = []
        for item_dict in chat_history_dicts:
            if item_dict["type"] == "UserMessage":
                message = UserMessage.from_dict(item_dict)
            elif item_dict["type"] == "AiMessage":
                message = AiMessage.from_dict(item_dict)
            messages.append(message)
        return messages

def update_dialogue_chat_history(session_id, chat_history_list):
    with SessionLocal() as session:
        dialogue_manager = session.query(DialogueManager).filter(DialogueManager.session_id == session_id).first()
        if dialogue_manager:
            # 将消息对象列表转换为字典列表
            chat_history_dicts = [message.to_dict() for message in chat_history_list]
            # 直接存储字典列表作为JSON
            dialogue_manager.chat_history = chat_history_dicts
            session.commit()


def get_dialogue_summary(session_id):
    with SessionLocal() as session:
        dialogue_manager = session.query(DialogueManager).filter(DialogueManager.session_id == session_id).first()
        print(dialogue_manager.summary)
        if dialogue_manager and dialogue_manager.summary:
            # 将存储的 JSON 字符串解析为列表
            summary_list = json.loads(dialogue_manager.summary)
            return summary_list
        else:
            return None  # 如果没有数据或者数据为空，返回 None 或者适当的默认值


def update_dialogue_summary(session_id, summary_list):
    with SessionLocal() as session:
        dialogue_manager = session.query(DialogueManager).filter(DialogueManager.session_id == session_id).first()
        # 将列表转换为JSON字符串
        dialogue_manager.summary = json.dumps(summary_list)
        session.commit()


def get_dialogue_situation(session_id):
    with SessionLocal() as session:
        dialogue_manager = session.query(DialogueManager).filter(DialogueManager.session_id == session_id).first()
        if dialogue_manager and dialogue_manager.situation:
            return dialogue_manager.situation
        else:
            return None  # 如果没有数据或者数据为空，返回 None 或者适当的默认值


def update_dialogue_situation(session_id, new_situation):
    with SessionLocal() as session:
        # 构造一个更新查询
        query = update(DialogueManager).where(
            DialogueManager.session_id == session_id
        ).values(situation=new_situation)
        # 执行查询
        session.execute(query)
        # 提交更改
        session.commit()


def update_entity_summary(session_id, entity_summary):
    with SessionLocal() as session:
        # 构造一个更新查询
        query = update(DialogueManager).where(
            DialogueManager.session_id == session_id
        ).values(entity_summary=entity_summary)
        # 执行查询
        session.execute(query)
        # 提交更改
        session.commit()


def get_entity_summary(session_id):
    with SessionLocal() as session:
        dialogue_manager = session.query(DialogueManager).filter(DialogueManager.session_id == session_id).first()
        if dialogue_manager and dialogue_manager.entity_summary:
            return dialogue_manager.entity_summary
        else:
            return None  # 如果没有数据或者数据为空，返回 None 或者适当的默认值
