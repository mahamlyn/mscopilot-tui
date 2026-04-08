"""
Persistence layer for saving and loading conversations.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import uuid

from .config import config
from .models import Conversation, Message, SpeakerRole

logger = logging.getLogger(__name__)


class ConversationPersistence:
    """
    Handles saving and loading conversations to/from markdown and JSON files.
    """
    
    def __init__(self, conversations_dir: Optional[Path] = None):
        """
        Initialize persistence layer.
        
        Args:
            conversations_dir: Directory to store conversations. 
                             Defaults to config value.
        """
        self.conversations_dir = conversations_dir or config.CONVERSATIONS_DIR
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
    
    def save_conversation_markdown(
        self,
        conversation: Conversation,
        filename: Optional[str] = None
    ) -> Path:
        """
        Save conversation as markdown file.
        
        Args:
            conversation: Conversation object to save
            filename: Optional custom filename. Auto-generated if not provided.
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{conversation.id}.md"
        
        filepath = self.conversations_dir / filename
        
        try:
            markdown_content = conversation.to_markdown()
            filepath.write_text(markdown_content, encoding="utf-8")
            logger.info(f"Conversation saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save conversation: {str(e)}")
            raise
    
    def save_conversation_json(
        self,
        conversation: Conversation,
        filename: Optional[str] = None
    ) -> Path:
        """
        Save conversation as JSON file for programmatic access.
        
        Args:
            conversation: Conversation object to save
            filename: Optional custom filename. Auto-generated if not provided.
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{conversation.id}.json"
        
        filepath = self.conversations_dir / filename
        
        try:
            data = {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "messages": [
                    {
                        "role": msg.role.value,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                    }
                    for msg in conversation.messages
                ]
            }
            filepath.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8"
            )
            logger.info(f"Conversation JSON saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save conversation JSON: {str(e)}")
            raise
    
    def save_conversation_both(
        self,
        conversation: Conversation
    ) -> tuple[Path, Path]:
        """
        Save conversation in both markdown and JSON formats.
        
        Args:
            conversation: Conversation object to save
            
        Returns:
            Tuple of (markdown_path, json_path)
        """
        md_path = self.save_conversation_markdown(conversation)
        json_path = self.save_conversation_json(conversation)
        return md_path, json_path
    
    def load_conversation_json(self, filepath: Path) -> Optional[Conversation]:
        """
        Load conversation from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Loaded Conversation object or None if loading fails
        """
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            conversation = Conversation(
                id=data["id"],
                title=data["title"],
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            )
            
            for msg_data in data["messages"]:
                role = SpeakerRole(msg_data["role"])
                message = Message(
                    role=role,
                    content=msg_data["content"],
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                )
                conversation.messages.append(message)
            
            logger.info(f"Conversation loaded from: {filepath}")
            return conversation
        except Exception as e:
            logger.error(f"Failed to load conversation: {str(e)}")
            return None
    
    def list_saved_conversations(self) -> List[Path]:
        """
        List all saved conversation files.
        
        Returns:
            List of Path objects for conversation files
        """
        json_files = sorted(self.conversations_dir.glob("*.json"))
        return json_files
    
    def get_conversation_summary(self, filepath: Path) -> dict:
        """
        Get summary information about a saved conversation.
        
        Args:
            filepath: Path to conversation file
            
        Returns:
            Dictionary with summary info
        """
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            return {
                "title": data["title"],
                "created_at": data["created_at"],
                "updated_at": data["updated_at"],
                "message_count": len(data["messages"]),
                "filepath": str(filepath),
            }
        except Exception as e:
            logger.error(f"Failed to read conversation summary: {str(e)}")
            return {}


# Example usage
def example_persistence():
    """Example usage of the persistence layer."""
    persistence = ConversationPersistence()
    
    # Create a sample conversation
    conversation = Conversation(
        id=str(uuid.uuid4()),
        title="Example Conversation"
    )
    
    # Add some messages
    conversation.add_message(
        SpeakerRole.USER,
        "Hello, how are you?"
    )
    conversation.add_message(
        SpeakerRole.ASSISTANT,
        "I'm doing well, thank you for asking! How can I help you today?"
    )
    conversation.add_message(
        SpeakerRole.USER,
        "Can you explain Python decorators?"
    )
    conversation.add_message(
        SpeakerRole.ASSISTANT,
        "Of course! Decorators in Python are functions that modify the behavior of other functions or classes..."
    )
    
    # Save in both formats
    md_path, json_path = persistence.save_conversation_both(conversation)
    print(f"✓ Conversation saved:")
    print(f"  Markdown: {md_path}")
    print(f"  JSON: {json_path}")
    
    # Load it back
    loaded = persistence.load_conversation_json(json_path)
    if loaded:
        print(f"\n✓ Loaded conversation: {loaded.title}")
        print(f"  Messages: {len(loaded.messages)}")
    
    # List all conversations
    print(f"\nSaved conversations:")
    for conv_file in persistence.list_saved_conversations():
        summary = persistence.get_conversation_summary(conv_file)
        print(f"  - {summary['title']} ({summary['message_count']} messages)")


if __name__ == "__main__":
    example_persistence()
