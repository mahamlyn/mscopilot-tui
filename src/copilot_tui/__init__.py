"""
Copilot TUI - Terminal User Interface for Microsoft Copilot
A multi-turn conversation interface with local persistence capabilities.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .api_client import CopilotAPIClient
from .tui_app import CopilotTUIApp
from .persistence import ConversationPersistence
from .models import Message, Conversation

__all__ = [
    "CopilotAPIClient",
    "CopilotTUIApp",
    "ConversationPersistence",
    "Message",
    "Conversation",
]
