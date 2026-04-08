"""
Microsoft Copilot API client for managing conversations.
"""

import httpx
import asyncio
from typing import Optional, AsyncIterator
from dataclasses import dataclass
import logging

from .config import config
from .models import Message, Conversation, SpeakerRole

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Response from the API."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class CopilotAPIClient:
    """
    Client for interacting with Microsoft Copilot API.
    Handles authentication, message sending, and conversation management.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Copilot API client.
        
        Args:
            api_key: GitHub Copilot API key. Defaults to config value.
        """
        self.api_key = api_key or config.COPILOT_API_KEY
        self.base_url = config.COPILOT_API_URL
        self.client = httpx.AsyncClient(
            headers=self._get_headers(),
            timeout=30.0
        )
        self.conversation_id: Optional[str] = None
    
    def _get_headers(self) -> dict:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Copilot-TUI/0.1.0",
        }
    
    async def create_conversation(self, title: str) -> APIResponse:
        """
        Create a new conversation thread.
        
        Args:
            title: Title for the conversation
            
        Returns:
            APIResponse with conversation ID
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/conversations",
                json={"title": title}
            )
            response.raise_for_status()
            data = response.json()
            self.conversation_id = data.get("id")
            logger.info(f"Created conversation: {self.conversation_id}")
            return APIResponse(success=True, data=data)
        except httpx.RequestError as e:
            error_msg = f"Failed to create conversation: {str(e)}"
            logger.error(error_msg)
            return APIResponse(success=False, error=error_msg)
    
    async def send_message(
        self, 
        message: str,
        conversation_id: Optional[str] = None
    ) -> APIResponse:
        """
        Send a message to an existing conversation.
        
        Args:
            message: The message content
            conversation_id: Optional conversation ID. Uses current if not provided.
            
        Returns:
            APIResponse with assistant's reply
        """
        conv_id = conversation_id or self.conversation_id
        if not conv_id:
            return APIResponse(
                success=False,
                error="No active conversation. Create one first with create_conversation()."
            )
        
        try:
            response = await self.client.post(
                f"{self.base_url}/conversations/{conv_id}/messages",
                json={"content": message}
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Message sent to {conv_id}")
            return APIResponse(success=True, data=data)
        except httpx.RequestError as e:
            error_msg = f"Failed to send message: {str(e)}"
            logger.error(error_msg)
            return APIResponse(success=False, error=error_msg)
    
    async def stream_message(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Send a message and stream the response.
        
        Args:
            message: The message content
            conversation_id: Optional conversation ID
            
        Yields:
            Chunks of the assistant's response
        """
        conv_id = conversation_id or self.conversation_id
        if not conv_id:
            yield "Error: No active conversation. Create one first."
            return
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/conversations/{conv_id}/messages",
                json={"content": message, "stream": True}
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        yield line
        except httpx.RequestError as e:
            logger.error(f"Error streaming message: {str(e)}")
            yield f"Error: {str(e)}"
    
    async def get_conversation_history(
        self,
        conversation_id: Optional[str] = None
    ) -> APIResponse:
        """
        Fetch the complete conversation history.
        
        Args:
            conversation_id: Optional conversation ID. Uses current if not provided.
            
        Returns:
            APIResponse with message history
        """
        conv_id = conversation_id or self.conversation_id
        if not conv_id:
            return APIResponse(
                success=False,
                error="No active conversation."
            )
        
        try:
            response = await self.client.get(
                f"{self.base_url}/conversations/{conv_id}/messages"
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved history for {conv_id}")
            return APIResponse(success=True, data=data)
        except httpx.RequestError as e:
            error_msg = f"Failed to retrieve conversation history: {str(e)}"
            logger.error(error_msg)
            return APIResponse(success=False, error=error_msg)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Example usage and testing
async def test_api_client():
    """Test the API client."""
    client = CopilotAPIClient()
    
    try:
        # Create a conversation
        print("Creating conversation...")
        result = await client.create_conversation("Test Conversation")
        if result.success:
            print(f"✓ Conversation created: {result.data}")
        else:
            print(f"✗ Failed to create conversation: {result.error}")
        
        # Send a message
        print("\nSending message...")
        result = await client.send_message("Hello, Copilot!")
        if result.success:
            print(f"✓ Message sent: {result.data}")
        else:
            print(f"✗ Failed to send message: {result.error}")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_api_client())
