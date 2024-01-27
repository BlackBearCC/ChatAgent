from typing import List, Literal
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, BaseMessageChunk
from langchain_core.pydantic_v1 import BaseModel, Field


class EventMessage(BaseMessage):
    """A Message from a human."""

    example: bool = False
    """Whether this Message is being passed in to the model as part of an example 
        conversation.
    """

    type: Literal["event"] = "event"

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "schema", "messages"]


EventMessage.update_forward_refs()


class EventMessageChunk(EventMessage, BaseMessageChunk):
    """A Human Message chunk."""

    # Ignoring mypy re-assignment here since we're overriding the value
    # to make sure that the chunk variant can be discriminated from the
    # non-chunk variant.
    type: Literal["EventMessageChunk"] = "EventMessageChunk"  # type: ignore[assignment] # noqa: E501

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "schema", "messages"]
