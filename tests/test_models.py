"""
Unit tests for Copilot TUI application.
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from copilot_tui.models import Message, Conversation, SpeakerRole
from copilot_tui.persistence import ConversationPersistence
from copilot_tui.config import Config


class TestModels:
    """Test data models."""
    
    def test_message_creation(self):
        """Test message creation."""
        msg = Message(
            role=SpeakerRole.USER,
            content="Hello!"
        )
        assert msg.role == SpeakerRole.USER
        assert msg.content == "Hello!"
        assert msg.timestamp is not None
    
    def test_message_speaker_label(self):
        """Test message speaker label."""
        msg = Message(role=SpeakerRole.ASSISTANT, content="Hi")
        assert "Assistant" in msg.speaker_label
        assert msg.speaker_label.startswith("Assistant")
    
    def test_message_to_markdown(self):
        """Test message markdown conversion."""
        msg = Message(role=SpeakerRole.USER, content="Test message")
        markdown = msg.to_markdown()
        assert "User" in markdown
        assert "Test message" in markdown
    
    def test_conversation_creation(self):
        """Test conversation creation."""
        conv = Conversation(id="test-1", title="Test")
        assert conv.id == "test-1"
        assert conv.title == "Test"
        assert len(conv.messages) == 0
    
    def test_conversation_add_message(self):
        """Test adding messages to conversation."""
        conv = Conversation(id="test-1", title="Test")
        msg = conv.add_message(SpeakerRole.USER, "Hello!")
        
        assert len(conv.messages) == 1
        assert msg.content == "Hello!"
        assert msg.role == SpeakerRole.USER
    
    def test_conversation_to_markdown(self):
        """Test conversation markdown conversion."""
        conv = Conversation(id="test-1", title="Test Conv")
        conv.add_message(SpeakerRole.USER, "Hello")
        conv.add_message(SpeakerRole.ASSISTANT, "Hi there!")
        
        markdown = conv.to_markdown()
        assert "Test Conv" in markdown
        assert "Hello" in markdown
        assert "Hi there!" in markdown


class TestPersistence:
    """Test persistence layer."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def sample_conversation(self):
        """Create sample conversation."""
        conv = Conversation(id="test-123", title="Test Conversation")
        conv.add_message(SpeakerRole.USER, "What is Python?")
        conv.add_message(SpeakerRole.ASSISTANT, "Python is a programming language.")
        return conv
    
    def test_save_markdown(self, temp_dir, sample_conversation):
        """Test saving conversation as markdown."""
        persistence = ConversationPersistence(temp_dir)
        path = persistence.save_conversation_markdown(sample_conversation)
        
        assert path.exists()
        assert path.suffix == ".md"
        
        content = path.read_text()
        assert sample_conversation.title in content
        assert "What is Python?" in content
    
    def test_save_json(self, temp_dir, sample_conversation):
        """Test saving conversation as JSON."""
        persistence = ConversationPersistence(temp_dir)
        path = persistence.save_conversation_json(sample_conversation)
        
        assert path.exists()
        assert path.suffix == ".json"
        
        data = json.loads(path.read_text())
        assert data["title"] == sample_conversation.title
        assert len(data["messages"]) == 2
    
    def test_load_json(self, temp_dir, sample_conversation):
        """Test loading conversation from JSON."""
        persistence = ConversationPersistence(temp_dir)
        
        # Save and load
        path = persistence.save_conversation_json(sample_conversation)
        loaded = persistence.load_conversation_json(path)
        
        assert loaded is not None
        assert loaded.title == sample_conversation.title
        assert len(loaded.messages) == 2
        assert loaded.messages[0].role == SpeakerRole.USER
    
    def test_list_conversations(self, temp_dir, sample_conversation):
        """Test listing saved conversations."""
        persistence = ConversationPersistence(temp_dir)
        
        # Save multiple
        persistence.save_conversation_json(sample_conversation)
        persistence.save_conversation_json(sample_conversation)
        
        convs = persistence.list_saved_conversations()
        assert len(convs) >= 2
    
    def test_get_summary(self, temp_dir, sample_conversation):
        """Test getting conversation summary."""
        persistence = ConversationPersistence(temp_dir)
        path = persistence.save_conversation_json(sample_conversation)
        
        summary = persistence.get_conversation_summary(path)
        assert summary["title"] == sample_conversation.title
        assert summary["message_count"] == 2


class TestConfig:
    """Test configuration."""
    
    def test_config_creation(self):
        """Test config creation."""
        cfg = Config()
        assert cfg.CONVERSATIONS_DIR.exists()
        assert cfg.MAX_MESSAGE_LENGTH > 0
        assert cfg.TUI_TITLE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
