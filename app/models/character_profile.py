from typing import Any


from app.models.base_charactor import BaseCharacter


class CharacterProfile(BaseCharacter):
    """角色档案"""

    def __init__(self,name,interests,personality,emotional_state,physical_state,location,action,**data: Any):
        super().__init__(
            name=name,
            interests=interests,
            personality=personality,
            emotional_state=emotional_state,
            physical_state=physical_state,
            location=location,
            action=action,
            **data)
    def update(self):
        pass