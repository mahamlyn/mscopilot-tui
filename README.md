# Copilot TUI Application

A modern Terminal User Interface (TUI) for multi-turn conversations with Microsoft Copilot. Built with Python and Textual, this application provides a seamless way to interact with Copilot directly from your terminal while maintaining full conversation history.

## Features

✨ **Multi-turn Conversations**: Maintain context across multiple message exchanges
🎨 **Rich Terminal UI**: Clean, intuitive interface built with Textual
💾 **Local Persistence**: Save conversations as Markdown and JSON files
🔄 **Async API Integration**: Non-blocking API calls for smooth user experience
📝 **Markdown Export**: Generate shareable conversation markdown files with timestamps
🏗️ **Modular Architecture**: Clean separation of concerns (API, UI, Persistence)
⚡ **Production Ready**: Full error handling, logging, and configuration management

## Project Structure

```
mscopilot-tui/
├── src/copilot_tui/
│   ├── __init__.py           # Package exports
│   ├── models.py             # Data models (Message, Conversation)
│   ├── config.py             # Configuration management
│   ├── api_client.py         # Copilot API client
│   ├── tui_app.py            # TUI application logic
│   └── persistence.py        # File persistence layer
├── docs/
│   ├── DEPLOYMENT.md         # Full deployment guide
│   └── DEPLOYMENT-QUICK-START.md  # Quick-start deployment reference
├── examples/
│   └── examples.py           # Usage examples and demo scripts
├── scripts/
│   └── build.sh              # PyInstaller build script
├── release/                  # Build artifacts (generated, gitignored)
├── conversations/            # Saved conversation files (generated)
├── tests/                    # Unit tests
├── main.py                   # Application entry point
├── Makefile                  # Build and development commands
├── Dockerfile                # Container image definition
├── docker-compose.yml        # Docker Compose configuration
├── pyproject.toml            # Package metadata and tool configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## System Requirements

- **OS**: Ubuntu/WSL (Linux)
- **Python**: 3.10 or higher
- **Terminal**: 24x80 minimum, supports ANSI colors

## Installation

### 1. Clone or Download

```bash
cd /home/localadmin/local-repo/copilot-tui
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Microsoft Entra ID Credentials

This app authenticates against the **Microsoft Graph Copilot API** using
OAuth 2.0 via Microsoft Entra ID (Azure AD). A static API key is **not** used.

**Register an app** at [entra.microsoft.com](https://entra.microsoft.com) →
*App registrations* → *New registration*, then copy the Tenant ID and Client ID.

Create a `.env` file in the project root:

```bash
cat > .env << 'EOF'
TENANT_ID=your-tenant-id-here
CLIENT_ID=your-client-id-here
EOF
```

Or set the environment variables directly:

```bash
export TENANT_ID="your-tenant-id-here"
export CLIENT_ID="your-client-id-here"
```

> **First run**: The app uses the **Device Code Flow** — it will print a URL
> (`https://microsoft.com/devicelogin`) and a one-time code. Sign in once;
> subsequent runs use the cached token automatically.
>
> **Requirements**: A Microsoft 365 Copilot licence and an E3/E5 subscription
> are needed per the [API prerequisites](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/copilot-apis-overview#requirements).

## Running the Application

### Start the TUI Application

```bash
python main.py
```

### Via pip (if installed as package)

```bash
copilot-tui
```

### Run Usage Examples

```bash
python examples/examples.py
```

## Documentation

| Document | Description |
|----------|-------------|
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Full packaging and deployment guide (PyInstaller, wheel, Docker, DEB) |
| [docs/DEPLOYMENT-QUICK-START.md](docs/DEPLOYMENT-QUICK-START.md) | Quick-start reference for built artifacts |
| [examples/examples.py](examples/examples.py) | Runnable usage examples for API, persistence, and models |

## Usage Guide

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+D` / `Enter` | Send message |
| `Ctrl+S` | Save conversation |
| `Ctrl+N` | Start new conversation |
| `Ctrl+C` | Quit |

### Basic Workflow

1. **Start the App**: `python main.py`
2. **Type Your Message**: In the input box at the bottom
3. **Send**: Press Enter or Ctrl+D
4. **View History**: Scroll in the conversation pane
5. **Save**: Press Ctrl+S to export as Markdown/JSON

## API Integration Example

### Using the API Client Directly

```python
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))  # or set PYTHONPATH=src

from copilot_tui.api_client import CopilotAPIClient

async def main():
    client = CopilotAPIClient()
    
    try:
        # Create conversation
        result = await client.create_conversation("My Conversation")
        if result.success:
            print(f"Created: {result.data['id']}")
        
        # Send message
        result = await client.send_message("Hello!")
        if result.success:
            print(f"Response: {result.data['content']}")
    
    finally:
        await client.close()

asyncio.run(main())
```

### Streaming Responses

```python
async def stream_example():
    client = CopilotAPIClient()
    
    try:
        async for chunk in client.stream_message("Explain Python"):
            print(chunk, end="", flush=True)
    finally:
        await client.close()

asyncio.run(stream_example())
```

## Persistence Example

### Save Conversation

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))  # or set PYTHONPATH=src

from copilot_tui.persistence import ConversationPersistence
from copilot_tui.models import Conversation, SpeakerRole

persistence = ConversationPersistence()

# Create and save
conv = Conversation(id="123", title="Example")
conv.add_message(SpeakerRole.USER, "Hi!")
conv.add_message(SpeakerRole.ASSISTANT, "Hello!")

md_path, json_path = persistence.save_conversation_both(conv)
print(f"Saved: {md_path}")
```

### Load Conversation

```python
loaded = persistence.load_conversation_json(json_path)
print(f"Loaded: {loaded.title} ({len(loaded.messages)} messages)")
```

## Configuration

Edit `src/copilot_tui/config.py` or set environment variables:

```python
@dataclass
class Config:
    TENANT_ID: str = os.getenv("TENANT_ID", "common")        # Entra tenant ID
    CLIENT_ID: str = os.getenv("CLIENT_ID", "")              # App registration ID
    GRAPH_BASE_URL: str = "https://graph.microsoft.com/beta/copilot"
    GRAPH_SCOPES: list = ["https://graph.microsoft.com/.default"]
    AUTO_SAVE: bool = False
    MAX_MESSAGE_LENGTH: int = 4096
```

## Saved Conversation Format

### Markdown Output
Conversations are saved with timestamps and speaker labels:

```markdown
# My Conversation

Created: 2024-01-15 10:30:45
Updated: 2024-01-15 10:35:12

---

**User [10:30:45]**

How do I use async/await in Python?

**Assistant [10:30:47]**

Async/await is Python's syntax for asynchronous programming...

```

### JSON Output
Full conversation data is also saved in JSON for programmatic access:

```json
{
  "id": "conv-123",
  "title": "Python Questions",
  "created_at": "2024-01-15T10:30:45.123456",
  "updated_at": "2024-01-15T10:35:12.654321",
  "messages": [
    {
      "role": "User",
      "content": "How do I use async/await?",
      "timestamp": "2024-01-15T10:30:45.123456"
    }
  ]
}
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'textual'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Authentication failed / no token"

**Solution**: Ensure `TENANT_ID` and `CLIENT_ID` are set, then re-run to
trigger the Device Code Flow sign-in prompt:
```bash
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
python main.py
```

### Issue: Terminal display issues

**Solution**: Ensure terminal is at least 24x80 and supports ANSI colors
```bash
echo $TERM
stty size
```

### Issue: Conversations directory permission error

**Solution**: Ensure directory is writable
```bash
chmod 755 conversations/
```

## Testing

Run unit tests:

```bash
python -m pytest tests/ -v
```

Run usage examples:

```bash
python examples/examples.py
```

## API Reference

### CopilotAPIClient

#### Methods

- `create_conversation(title)` - Create new conversation
- `send_message(message)` - Send message and get response
- `stream_message(message)` - Stream response chunks
- `get_conversation_history()` - Fetch all messages
- `close()` - Close HTTP client

### ConversationPersistence

- `save_conversation_markdown()` - Save as .md file
- `save_conversation_json()` - Save as .json file
- `save_conversation_both()` - Save both formats
- `load_conversation_json()` - Load from JSON file
- `list_saved_conversations()` - List all saved files
- `get_conversation_summary()` - Get file metadata

### Models

**Message**
- `role`: SpeakerRole enum (USER or ASSISTANT)
- `content`: str - message text
- `timestamp`: datetime
- `to_markdown()` - format as markdown

**Conversation**
- `id`: str - unique identifier
- `title`: str - conversation title
- `messages`: list[Message]
- `add_message()` - add new message
- `to_markdown()` - export full conversation

## Performance Notes

- Messages are processed asynchronously, preventing UI freeze
- Conversations are stored locally to reduce API calls
- Large conversations (1000+ messages) may have slower rendering
- API rate limits depend on your GitHub Copilot subscription

## Contributing

Contributions are welcome! Areas for improvement:

- Additional UI themes
- Message search functionality
- Conversation categorization/tagging
- Export to additional formats (HTML, PDF)
- Multi-window support
- Plugin architecture

## Future Enhancements

- [ ] Voice input/output support
- [ ] Conversation branching
- [ ] Syntax highlighting for code blocks
- [ ] User authentication UI
- [ ] Integration with version control systems
- [ ] Collaborative conversations

## License

MIT

## Support

For issues, questions, or suggestions:

1. Check existing documentation
2. Review the code structure in `/src/copilot_tui/`
3. Check logs in `copilot_tui.log`
4. Test with simpler examples first

## Architecture Overview

### API Client Layer (`api_client.py`)
- Handles all HTTP communication with Copilot API
- Manages authentication and error handling
- Supports streaming and standard responses
- Async/await throughout

### TUI Layer (`tui_app.py`)
- Textual-based user interface
- Manages keyboard input and display
- Updates conversation view in real-time
- Non-blocking message processing

### Persistence Layer (`persistence.py`)
- Saves conversations to disk
- Supports multiple formats (Markdown, JSON)
- Loads saved conversations
- Provides inquiry and summary functions

### Data Models (`models.py`)
- `Message`: Individual messages with role and timestamp
- `Conversation`: Collection of messages with metadata
- `SpeakerRole`: Enum for sender identification

### Configuration (`config.py`)
- Centralized settings management
- API key management via environment variables
- Directory path configuration
- Feature flags

## Environment-Specific Notes for WSL

### Windows Terminal (Recommended)

```powershell
wsl --install Ubuntu
wsl -d Ubuntu
```

### Terminal Configuration

```bash
# Ensure UTF-8 support
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Run application
python main.py
```

### Performance Optimization

For better WSL performance:
- Use Windows Terminal instead of Command Prompt
- Enable GPU acceleration in terminal settings
- Consider using WSL 2 instead of WSL 1

## Security Considerations

⚠️ **API Key Management**
- Never commit `.env` file to version control
- Never log API keys
- Use environment variables for secrets
- Rotate API keys regularly

⚠️ **Data Privacy**
- Conversations are stored locally in plaintext
- Consider encrypting sensitive conversations
- Implement user authentication for shared systems

## Changelog

### v0.1.0 (Initial Release)
- Basic TUI with Textual
- API client for Copilot integration
- Markdown and JSON persistence
- Multi-turn conversation support

---

**Made with ❤️ for terminal lovers**
