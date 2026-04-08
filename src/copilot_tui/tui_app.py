"""
Textual-based TUI application for Copilot conversations.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
import uuid

from .api_client import CopilotAPIClient
from .persistence import ConversationPersistence
from .models import Conversation, Message, SpeakerRole
from .config import config

logger = logging.getLogger(__name__)


class CopilotTUIApp:
    """
    Main TUI application for Copilot conversation.
    
    This can be used as a component or extended by a Textual App class.
    """
    
    def __init__(self):
        """Initialize the TUI application."""
        self.api_client = CopilotAPIClient()
        self.persistence = ConversationPersistence()
        self.current_conversation: Optional[Conversation] = None
        self.is_waiting_for_response = False
    
    async def create_new_conversation(self, title: str) -> bool:
        """
        Create a new conversation thread.
        
        Args:
            title: Title for the conversation
            
        Returns:
            True if successful
        """
        try:
            # Local conversation creation
            self.current_conversation = Conversation(
                id=str(uuid.uuid4()),
                title=title
            )
            
            # Try to sync with API (may fail if API key is invalid)
            result = await self.api_client.create_conversation(title)
            if result.success:
                self.api_client.conversation_id = result.data.get("id")
                logger.info(f"Created conversation: {title}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to create conversation: {str(e)}")
            return False
    
    async def send_message(self, content: str) -> Optional[str]:
        """
        Send a message and get response.
        
        Args:
            content: Message content
            
        Returns:
            Assistant's response or None if failed
        """
        if not self.current_conversation:
            return "Error: No active conversation"
        
        if not content.strip():
            return "Error: Empty message"
        
        if len(content) > config.MAX_MESSAGE_LENGTH:
            return f"Error: Message exceeds {config.MAX_MESSAGE_LENGTH} characters"
        
        try:
            self.is_waiting_for_response = True
            
            # Add user message
            self.current_conversation.add_message(
                SpeakerRole.USER,
                content
            )
            
            # Send to API
            result = await self.api_client.send_message(content)
            
            if result.success:
                response_content = result.data.get(
                    "content",
                    "No response content"
                )
                # Add assistant message
                self.current_conversation.add_message(
                    SpeakerRole.ASSISTANT,
                    response_content
                )
                return response_content
            else:
                error_msg = result.error or "Unknown error"
                return f"Error: {error_msg}"
        
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return f"Error: {str(e)}"
        
        finally:
            self.is_waiting_for_response = False
    
    def save_current_conversation(self, filename: Optional[str] = None) -> Optional[tuple]:
        """
        Save the current conversation.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Tuple of (markdown_path, json_path) or None
        """
        if not self.current_conversation:
            return None
        
        try:
            md_path, json_path = self.persistence.save_conversation_both(
                self.current_conversation
            )
            logger.info(f"Conversation saved: {md_path}, {json_path}")
            return md_path, json_path
        except Exception as e:
            logger.error(f"Failed to save conversation: {str(e)}")
            return None
    
    def get_conversation_display(self) -> str:
        """
        Get formatted conversation for display.
        
        Returns:
            Formatted conversation text
        """
        if not self.current_conversation:
            return "No active conversation"
        
        lines = []
        for message in self.current_conversation.messages:
            lines.append(message.speaker_label)
            lines.append(message.content)
            lines.append("")
        
        return "\n".join(lines)
    
    async def close(self):
        """Close the application and clean up resources."""
        await self.api_client.close()


# Textual App Integration (optional)
try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import Header, Footer, Static, Input, Button
    from textual.reactive import reactive
    
    class ConversationHistory(Static):
        """Widget for displaying conversation history."""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.border_title = "Conversation History"

    class MessageInput(Input):
        """Custom input widget for messages."""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class StatusBar(Static):
        """Status bar showing current conversation info."""
        
        message: reactive[str] = reactive("Ready")
        conversation_id: reactive[str] = reactive("")
        
        def render(self) -> str:
            status = f"[{self.conversation_id}] {self.message}" if self.conversation_id else self.message
            return f"Status: {status}"

    class CopilotApp(App):
        """Main Textual application."""
        
        CSS = """
        Screen {
            layout: vertical;
        }
        
        #conversation-container {
            height: 1fr;
            border: solid $primary;
        }
        
        #input-container {
            height: auto;
            border-top: solid $primary;
        }
        
        #message-input {
            width: 1fr;
        }
        
        #send-button {
            margin-left: 1;
        }
        
        #status-bar {
            height: 1;
            border-top: solid $accent;
        }
        """
        
        def __init__(self):
            super().__init__()
            self.tui_app = CopilotTUIApp()
        
        def compose(self) -> ComposeResult:
            """Compose the TUI layout."""
            yield Header()
            
            with Vertical(id="main-container"):
                with Container(id="conversation-container"):
                    self.history = ConversationHistory(id="history")
                    yield self.history
                
                with Horizontal(id="input-container"):
                    self.input = MessageInput(
                        id="message-input",
                        placeholder="Type your message (Enter to send, Ctrl+C to quit)"
                    )
                    yield self.input
                    
                    yield Button("Send", id="send-button", variant="primary")
                
                self.status = StatusBar(id="status-bar")
                yield self.status
            
            yield Footer()
        
        async def on_mount(self) -> None:
            """Called when the app is mounted."""
            self.title = config.TUI_TITLE
            self.sub_title = "v0.1.0"
            
            # Create initial conversation
            await self.tui_app.create_new_conversation(
                f"Conversation {datetime.now().strftime('%H:%M:%S')}"
            )
            self.update_display()
            self.input.focus()
        
        def action_save_conversation(self) -> None:
            """Save current conversation."""
            result = self.tui_app.save_current_conversation()
            if result:
                self.history.write("✓ Conversation saved locally")
                self.status.message = "Conversation saved!"
            else:
                self.history.write("✗ Failed to save conversation")
                self.status.message = "Save failed"
        
        def action_new_conversation(self) -> None:
            """Start a new conversation."""
            async def create_new():
                await self.tui_app.create_new_conversation(
                    f"Conversation {datetime.now().strftime('%H:%M:%S')}"
                )
                self.update_display()
            
            asyncio.create_task(create_new())
        
        def action_quit_app(self) -> None:
            """Quit the application."""
            self.exit()
        
        def update_display(self) -> None:
            """Update the conversation display."""
            self.history.clear()
            content = self.tui_app.get_conversation_display()
            self.history.write(content)
        
        async def refresh_display(self) -> None:
            """Refresh the display asynchronously."""
            await self.call_later(self.update_display)
        
        BINDINGS = [
            ("ctrl+s", "save_conversation", "Save"),
            ("ctrl+n", "new_conversation", "New"),
            ("ctrl+c", "quit_app", "Quit"),
        ]
        
        async def on_unmount(self) -> None:
            """Clean up on exit."""
            await self.tui_app.close()

except ImportError:
    logger.warning("Textual not installed. API client only mode available.")
    CopilotApp = None  # type: ignore
