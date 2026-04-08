"""
Configuration module for the Copilot TUI application.
"""

import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""
    
    # API Configuration
    COPILOT_API_KEY: str = os.getenv("COPILOT_API_KEY", "your-api-key-here")
    COPILOT_API_URL: str = "https://api.github.com/copilot"
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    CONVERSATIONS_DIR: Path = PROJECT_ROOT / "conversations"
    
    # UI Configuration
    TUI_TITLE: str = "Copilot TUI - Multi-turn Conversation"
    TUI_THEME: str = "dark"
    
    # Feature flags
    AUTO_SAVE: bool = False
    MAX_MESSAGE_LENGTH: int = 4096
    
    def __post_init__(self):
        """Ensure conversations directory exists."""
        self.CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()
