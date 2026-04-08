"""
Data models for conversations and messages.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class SpeakerRole(Enum):
    """Enum for speaker roles in a conversation."""
    USER = "User"
    ASSISTANT = "Assistant"


@dataclass
class Message:
    """Represents a single message in a conversation."""
    
    role: SpeakerRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def speaker_label(self) -> str:
        """Return the speaker label with timestamp."""
        return f"{self.role.value} [{self.timestamp.strftime('%H:%M:%S')}]"
    
    def to_markdown(self) -> str:
        """Convert message to markdown format."""
        return f"**{self.speaker_label}**\n\n{self.content}\n"


@dataclass
class Conversation:
    """Represents a complete conversation thread."""
    
    id: str
    title: str
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: SpeakerRole, content: str) -> Message:
        """Add a message to the conversation."""
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def to_markdown(self) -> str:
        """Convert entire conversation to markdown format."""
        lines = [
            f"# {self.title}",
            f"\nCreated: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "\n---\n",
        ]
        
        for message in self.messages:
            lines.append(message.to_markdown())
        
        return "\n".join(lines)
