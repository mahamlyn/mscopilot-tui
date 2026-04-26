"""
Example scripts demonstrating Copilot TUI usage.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from copilot_tui.api_client import CopilotAPIClient
from copilot_tui.persistence import ConversationPersistence
from copilot_tui.models import Conversation, SpeakerRole
import uuid


async def example_api_usage():
    """Example: Using the API client directly."""
    print("=== API Client Example ===\n")
    
    client = CopilotAPIClient()
    
    try:
        # Create a conversation
        print("1. Creating conversation...")
        result = await client.create_conversation("Python Questions")
        if result.success:
            print(f"   ✓ Created: {result.data['id']}\n")
        else:
            print(f"   ✗ Error: {result.error}\n")
            return
        
        # Send a message
        print("2. Sending message...")
        result = await client.send_message("What are decorators in Python?")
        if result.success:
            print(f"   ✓ Response received")
            print(f"   Content: {result.data.get('content', 'N/A')[:100]}...\n")
        else:
            print(f"   ✗ Error: {result.error}\n")
        
        # Get history
        print("3. Fetching conversation history...")
        result = await client.get_conversation_history()
        if result.success:
            messages = result.data.get('messages', [])
            print(f"   ✓ Retrieved {len(messages)} messages\n")
        else:
            print(f"   ✗ Error: {result.error}\n")
    
    finally:
        await client.close()


def example_persistence():
    """Example: Using the persistence layer."""
    print("=== Persistence Example ===\n")
    
    persistence = ConversationPersistence()
    
    # Create a sample conversation
    print("1. Creating sample conversation...")
    conversation = Conversation(
        id=str(uuid.uuid4()),
        title="Python Learning Session"
    )
    
    # Add messages
    conversation.add_message(
        SpeakerRole.USER,
        "What is the difference between list and tuple in Python?"
    )
    conversation.add_message(
        SpeakerRole.ASSISTANT,
        "Lists are mutable (can be changed), while tuples are immutable (cannot be changed)."
    )
    conversation.add_message(
        SpeakerRole.USER,
        "Can you give me an example?"
    )
    conversation.add_message(
        SpeakerRole.ASSISTANT,
        "Sure! List: my_list = [1, 2, 3]; my_list[0] = 5 (works)\n"
        "Tuple: my_tuple = (1, 2, 3); my_tuple[0] = 5 (raises TypeError)"
    )
    print(f"   ✓ Created conversation with {len(conversation.messages)} messages\n")
    
    # Save in both formats
    print("2. Saving conversation...")
    md_path, json_path = persistence.save_conversation_both(conversation)
    print(f"   ✓ Markdown: {md_path.name}")
    print(f"   ✓ JSON: {json_path.name}\n")
    
    # Load from JSON
    print("3. Loading conversation...")
    loaded = persistence.load_conversation_json(json_path)
    if loaded:
        print(f"   ✓ Loaded: {loaded.title}")
        print(f"   ✓ Messages: {len(loaded.messages)}\n")
    
    # List all conversations
    print("4. Listing saved conversations...")
    convs = persistence.list_saved_conversations()
    print(f"   ✓ Found {len(convs)} saved conversation(s)")
    for conv_file in convs[:3]:  # Show first 3
        summary = persistence.get_conversation_summary(conv_file)
        print(f"     - {summary['title']} ({summary['message_count']} msgs)")
    print()


def example_models():
    """Example: Working with data models."""
    print("=== Data Models Example ===\n")
    
    # Create individual messages
    print("1. Creating messages...")
    from copilot_tui.models import Message
    
    msg1 = Message(SpeakerRole.USER, "Hello!")
    msg2 = Message(SpeakerRole.ASSISTANT, "Hi there! How can I help?")
    print(f"   ✓ Created 2 messages\n")
    
    # Create a conversation
    print("2. Creating conversation...")
    conv = Conversation(
        id="example-conv-001",
        title="Greeting Exchange"
    )
    conv.messages.append(msg1)
    conv.messages.append(msg2)
    print(f"   ✓ Conversation has {len(conv.messages)} messages\n")
    
    # Export to markdown
    print("3. Exporting to markdown...")
    print("   Generated markdown:\n")
    markdown = conv.to_markdown()
    # Print first 500 chars
    print("   " + "\n   ".join(markdown[:500].split("\n")))
    print("   ...\n")


async def main():
    """Run all examples."""
    print("\n" + "=" * 50)
    print("COPILOT TUI - USAGE EXAMPLES")
    print("=" * 50 + "\n")
    
    # Run synchronous example
    example_models()
    
    # Run persistence example
    example_persistence()
    
    # Run API example (requires Microsoft Entra ID credentials)
    print("=== API Client Example ===")
    print("Note: This requires TENANT_ID and CLIENT_ID set in .env")
    print("      On first run you will be prompted to sign in via Device Code Flow.\n")

    # Uncomment to run (requires valid Entra credentials):
    # await example_api_usage()


if __name__ == "__main__":
    asyncio.run(main())
