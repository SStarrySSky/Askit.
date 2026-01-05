"""Session data structure."""

from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message."""
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class Session(BaseModel):
    """Session data structure."""

    id: str
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: List[Message] = Field(default_factory=list)
    scene_state: Dict[str, Any] = Field(default_factory=dict)

    def add_message(self, role: str, content: str):
        """Add a message to the session."""
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now()

    def clear_messages(self):
        """Clear all messages."""
        self.messages.clear()
        self.updated_at = datetime.now()
