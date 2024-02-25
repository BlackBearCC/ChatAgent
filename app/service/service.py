# service.py
import json

from app.database.mysql.repository import (init_seesion_member,
                                           update_character_emotion,
                                           get_dialogue_manager_by_session_id,

                                           get_chat_summary,
                                           get_dialogue_situation,
                                           update_dialogue_situation,
                                           update_entity_summary, get_entity_summary, validate_session_id,
                                           create_session_id, update_chat_history, check_summary,
                                           get_chat_history_by_session_id, save_summary_and_bind_messages, update_diary,
                                           get_diary, get_diaries)
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


def validate_session_id_service(session_id):
    try:
        result = validate_session_id(session_id)
        if result:
            return True
        else:
            return create_session_id_service(session_id)
            # return False
    except SQLAlchemyError as e:
        logger.error(f"验证session_id时发生错误: {e}")
        return False


def create_session_id_service(session_id):
    try:
        result = create_session_id(session_id)
        return result
    except SQLAlchemyError as e:
        logger.error(f"创建session_id时发生错误: {e}")
        return "创建session_id失败。"


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


def update_diary_service(session_id, diary):
    try:


        # 调用数据访问层的函数进行更新
        # 这里假设 update_diary 函数接受 session_id 和 diary_dict
        update_diary(session_id, diary)
        return diary
    except SQLAlchemyError as e:
        logger.error(f"更新日记时发生错误: {e}")
        return "更新日记失败。"

def get_diray_service(session_id):
    try:
        diary = get_diary(session_id)
        return diary
    except SQLAlchemyError as e:
        logger.error(f"获取日记时发生错误: {e}")
        return None

def get_diaries_all_service(session_id):
    try:
        diaries = get_diaries(session_id)
        # all_diaries = []
        # for diary in diaries:
        #     diary_info={"time": diary.created_at,"diary": diary.content}
        #     all_diaries.append(diary_info)
        return diaries
    except SQLAlchemyError as e:
        logger.error(f"获取日记时发生错误: {e}")
        return None

def get_chat_history_service(session_id: str, limit, include_ids=False,time=None):
    try:
        # 现在将include_ids参数传递给下层函数
        messages = get_chat_history_by_session_id(session_id, limit, include_ids,time)
        return messages
    except SQLAlchemyError as e:
        logger.error(f"获取对话聊天记录时发生错误: {e}")
        return []  # 确保在错误情况下也返回空列表



def update_chat_history_service(session_id, chat_history):
    try:
        # 调用数据访问层的函数进行更新
        update_chat_history(session_id, chat_history)
        return check_summary(session_id)
    except SQLAlchemyError as e:
        logger.error(f"更新对话聊天记录时发生错误: {e}")
        return "更新对话聊天记录失败。"


# def update_dialogue_summary_service(session_id, summary_list):
#     try:
#         # 调用数据访问层的函数进行更新
#         update_dialogue_summary(session_id, summary_list)
#
#         return f"{session_id}:对话总结更新成功。"
#     except SQLAlchemyError as e:
#         logger.error(f"更新对话总结时发生错误: {e}")
#         return f"{session_id}:更新对话总结失败。"

# 获取对话总结
def get_summary_service(session_id):
    try:
        summary_list = get_chat_summary(session_id)
        return summary_list
    except SQLAlchemyError as e:
        logger.error(f"获取对话总结时发生错误: {e}")
        return None

# 绑定对话总结与消息id
def bind_summary_service(session_id,summary_text, message_ids):
    try:
        save_summary_and_bind_messages(session_id, summary_text, message_ids)
        return "绑定对话总结成功。"
    except SQLAlchemyError as e:
        logger.error(f"绑定对话总结时发生错误: {e}")
        return "绑定对话总结失败。"


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


def update_entity_summary_service(session_id, entity_summary):
    try:
        # 调用数据访问层的函数进行更新
        update_entity_summary(session_id, entity_summary)

        return "实体摘要更新成功。"
    except SQLAlchemyError as e:
        logger.error(f"更新实体摘要时发生错误: {e}")
        return "更新实体摘要失败。"


def get_entity_summary_service(session_id):
    try:
        entity_summary = get_entity_summary(session_id)
        return entity_summary
    except SQLAlchemyError as e:
        logger.error(f"获取实体摘要时发生错误: {e}")
        return None
