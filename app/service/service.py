# service.py
from app.database.mysql import init_seesion_member, engine, db_config
from app.models import UserProfile
from app.models import CharacterProfile
def get_user_and_character_profiles(session_id):
    user_profile = None
    character_profile = None

    result = init_seesion_member(session_id)

    if result:
        user_profile = UserProfile(
            user_id=result['UserId'],
            name=result['UserName'],
            interests=result['UserInterests'],
            personality=result['UserPersonality'],
            emotional_state=result['UserEmotionalState'],
            physical_state=result['UserPhysicalState'],
            location=result['UserLocation'],
            action=result['UserAction'],
        )

        character_profile = CharacterProfile(
            character_id=result['CharacterId'],
            name=result['CharacterName'],
            interests=result['CharacterInterests'],
            personality=result['CharacterPersonality'],
            emotional_state=result['CharacterEmotionalState'],
            physical_state=result['CharacterPhysicalState'],
            location=result['CharacterLocation'],
            action=result['CharacterAction'],
        )

    return user_profile, character_profile
