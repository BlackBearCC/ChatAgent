from typing import List, Union

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.pydantic_v1 import BaseModel, Field

from simpleaichat.memory.event_message import EventMessage


class GameMessageHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history2.

    Stores messages in an in memory list.
    """

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_message(self, message: BaseMessage) -> None:
        """Add a self-created message to the store"""
        self.messages.append(message)

    def add_user_message(self, message: Union[EventMessage, str]) -> None:
        """Convenience method for adding a human message string to the store.

        Args:
            message: The human message to add
        """
        if isinstance(message, EventMessage):
            self.add_message(message)
        else:
            self.add_message(EventMessage(content=message))

    def clear(self) -> None:
        self.messages = []
