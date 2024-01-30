from typing import Any, Optional

from pydantic import BaseModel, Field


class BaseCharacter(BaseModel):
    """角色基类"""
    name: str = Field(...)
    interests: Optional[str] = None
    personality: Optional[str] = None
    emotional_state: Optional[str] = None
    physical_state: Optional[str] = None
    location: Optional[str] = None
    action: Optional[str] = None

    def update(self):
        pass