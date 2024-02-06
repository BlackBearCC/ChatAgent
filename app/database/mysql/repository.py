from sqlalchemy.orm import sessionmaker
from .db import engine
from sqlalchemy import update
from app.models.character_profile import CharacterProfile
from ...models.dialogue_model import DialogueManager

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