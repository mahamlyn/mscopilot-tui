"""
Configuration module for the Copilot TUI application.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


@dataclass
class Config:
    """
    Application configuration.

    Authentication uses Microsoft Entra ID (formerly Azure AD) OAuth 2.0.
    This TUI uses the Device Code Flow so users authenticate without a
    browser redirect URI.

    Register your app at: https://entra.microsoft.com → App registrations
    API docs: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/copilot-apis-overview
    Auth docs: https://learn.microsoft.com/en-us/graph/auth/auth-concepts
    """

    # -------------------------------------------------------------------------
    # Microsoft Entra ID (Azure AD) OAuth 2.0 credentials
    # Register app at: https://entra.microsoft.com → App registrations
    # -------------------------------------------------------------------------
    TENANT_ID: str = os.getenv("TENANT_ID", "common")
    CLIENT_ID: str = os.getenv("CLIENT_ID", "")

    # Required only for confidential client (app-only) flows.
    # The Device Code Flow used by this TUI does NOT require a client secret.
    CLIENT_SECRET: str = os.getenv("CLIENT_SECRET", "")

    # -------------------------------------------------------------------------
    # Microsoft Graph — M365 Copilot Chat API (preview)
    # Namespace: graph.microsoft.com/v1.0/copilot  (GA)
    #            graph.microsoft.com/beta/copilot   (preview / Chat API)
    # -------------------------------------------------------------------------
    GRAPH_BASE_URL: str = "https://graph.microsoft.com/beta/copilot"

    # Delegated permission scopes. Adjust based on your app registration.
    GRAPH_SCOPES: list = field(
        default_factory=lambda: ["https://graph.microsoft.com/.default"]
    )

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent

    # UI Configuration
    TUI_TITLE: str = "MS Copilot TUI - Multi-turn Conversation"
    TUI_THEME: str = "dark"

    # Feature flags
    AUTO_SAVE: bool = False
    MAX_MESSAGE_LENGTH: int = 4096

    def __post_init__(self):
        """Compute derived fields and ensure required directories exist."""
        # OAuth 2.0 token authority endpoint
        self.AUTHORITY: str = f"https://login.microsoftonline.com/{self.TENANT_ID}"
        # Conversation storage directory
        self.CONVERSATIONS_DIR: Path = self.PROJECT_ROOT / "conversations"
        self.CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()
