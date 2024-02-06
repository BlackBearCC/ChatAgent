# service.py

from app.database.mysql.repository import *
from app.models import UserProfile
from app.models import CharacterProfile
from sqlalchemy.exc import SQLAlchemyError
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user_and_character_profiles(session_id):
    user_profile = None
    character_profile = None

    result = init_seesion_member(session_id)

    if result:
        user_profile = UserProfile(
            id=result['UserId'],
            name=result['UserName'],
            interests=result['UserInterests'],
            personality=result['UserPersonality'],
            emotional_state=result['UserEmotionalState'],
            physical_state=result['UserPhysicalState'],
            location=result['UserLocation'],
            action=result['UserAction'],
        )

        character_profile = CharacterProfile(
            id=result['CharacterId'],
            name=result['CharacterName'],
            interests=result['CharacterInterests'],
            personality=result['CharacterPersonality'],
            emotional_state=result['CharacterEmotionalState'],
            physical_state=result['CharacterPhysicalState'],
            location=result['CharacterLocation'],
            action=result['CharacterAction'],
        )

    return user_profile, character_profile


def update_character_emotion_service(session_id, new_emotion):
    try:
        update_character_emotion(session_id, new_emotion)
        return "角色情感状态更新成功。"
    except SQLAlchemyError as e:
        logger.error(f"更新角色情感状态时发生错误: {e}")
        return "更新角色情感状态失败。"


def get_dialogue_manager_service(session_id: str):
    try:
        dialogue_manager = get_dialogue_manager_by_session_id(session_id)
        if dialogue_manager:
            return dialogue_manager
        else:
            return None
    except SQLAlchemyError as e:
        logger.error(f"获取对话管理器时发生错误: {e}")
        return None


def get_dialogue_chat_history_service(session_id: str):
    try:
        dialogue_manager = get_chat_history(session_id)
        if dialogue_manager:
            return dialogue_manager.chat_history
        else:
            return None
    except SQLAlchemyError as e:
        logger.error(f"获取对话聊天记录时发生错误: {e}")
        return None


def update_dialogue_summary_service(session_id, summary_list):
    try:
        # 调用数据访问层的函数进行更新
        update_dialogue_summary(session_id, summary_list)

        return "对话总结更新成功。"
    except SQLAlchemyError as e:
        logger.error(f"更新对话总结时发生错误: {e}")
        return "更新对话总结失败。"


def get_dialogue_summary_service(session_id):
    try:
        summary_list = get_dialogue_summary(session_id)
        return summary_list
    except SQLAlchemyError as e:
        logger.error(f"获取对话总结时发生错误: {e}")
        return None


def get_dialogue_situation_service(session_id):
    try:
        dialogue_situation = get_dialogue_situation(session_id)
        return dialogue_situation
    except SQLAlchemyError as e:
        logger.error(f"获取对话情景时发生错误: {e}")
        return None

def update_dialogue_situation_service(session_id, new_situation):
    try:
        # 调用数据访问层的函数进行更新
        update_dialogue_situation(session_id, new_situation)

        return "对话情景更新成功。"
    except SQLAlchemyError as e:
        logger.error(f"更新对话情景时发生错误: {e}")
        return "更新对话情景失败。"