"""
Microsoft 365 Copilot API client.

Authenticates via Microsoft Entra ID (Azure AD) using the OAuth 2.0
Device Code Flow — the correct approach for terminal/TUI applications where
a browser redirect URI is not practical.

REST namespace : https://graph.microsoft.com/beta/copilot  (Chat API - preview)
Auth docs      : https://learn.microsoft.com/en-us/graph/auth/auth-concepts
API overview   : https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/copilot-apis-overview

Prerequisites:
  - Microsoft 365 Copilot licence per user
  - Microsoft 365 E3/E5 subscription (or equivalent)
  - App registered in the Microsoft Entra admin centre with the required
    delegated permissions for the M365 Copilot Chat API
  - TENANT_ID and CLIENT_ID set in .env or environment variables
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, AsyncIterator

import httpx
import msal

from .config import config

logger = logging.getLogger(__name__)

# Path for the persisted MSAL token cache (silences re-auth on subsequent runs)
_TOKEN_CACHE_PATH = config.PROJECT_ROOT / ".token_cache.json"


@dataclass
class APIResponse:
    """Wrapper for Microsoft Graph API call results."""

    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class CopilotAPIClient:
    """
    Client for Microsoft 365 Copilot via Microsoft Graph (Chat API - preview).

    Authentication
    --------------
    Uses the OAuth 2.0 Device Code Flow via MSAL so users can sign in via
    https://microsoft.com/devicelogin without a local redirect URI.
    Tokens are cached to disk and silently refreshed on subsequent runs.

    Token endpoint : https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
    Graph base URL : https://graph.microsoft.com/beta/copilot
    """

    def __init__(self) -> None:
        self.base_url = config.GRAPH_BASE_URL
        self.conversation_id: Optional[str] = None

        # ------------------------------------------------------------------ #
        # MSAL token cache — persists Bearer tokens between application runs  #
        # ------------------------------------------------------------------ #
        self._token_cache = msal.SerializableTokenCache()
        if _TOKEN_CACHE_PATH.exists():
            self._token_cache.deserialize(
                _TOKEN_CACHE_PATH.read_text(encoding="utf-8")
            )

        # PublicClientApplication is correct for delegated / Device Code flows.
        # Switch to ConfidentialClientApplication only for app-only (daemon) flows.
        self._msal_app = msal.PublicClientApplication(
            client_id=config.CLIENT_ID,
            authority=config.AUTHORITY,
            token_cache=self._token_cache,
        )

        # Shared async HTTP client — auth header is injected per-request
        self.client = httpx.AsyncClient(timeout=60.0)

    # ---------------------------------------------------------------------- #
    # Authentication helpers                                                   #
    # ---------------------------------------------------------------------- #

    def _save_token_cache(self) -> None:
        """Persist the MSAL token cache to disk when its state has changed."""
        if self._token_cache.has_state_changed:
            _TOKEN_CACHE_PATH.write_text(
                self._token_cache.serialize(), encoding="utf-8"
            )

    def _acquire_token(self) -> Optional[str]:
        """
        Acquire a valid Microsoft Graph access token.

        1. Attempts a silent cache lookup / token refresh first (no user prompt).
        2. Falls back to the Device Code Flow on first run or after expiry,
           printing a one-time sign-in URL and code for the user.

        Returns:
            A Bearer access-token string, or None on failure.
        """
        accounts = self._msal_app.get_accounts()

        # 1 — Silent acquisition from cache (fast path)
        if accounts:
            result = self._msal_app.acquire_token_silent(
                scopes=config.GRAPH_SCOPES,
                account=accounts[0],
            )
            if result and "access_token" in result:
                self._save_token_cache()
                logger.debug("Token acquired silently from cache")
                return result["access_token"]

        # 2 — Device Code Flow (interactive, one-time sign-in)
        logger.info("No cached token — initiating Device Code Flow")
        flow = self._msal_app.initiate_device_flow(scopes=config.GRAPH_SCOPES)

        if "user_code" not in flow:
            logger.error(
                "Device Code Flow failed to initialise: %s",
                flow.get("error_description", flow.get("error")),
            )
            return None

        # Display sign-in instructions to the terminal user
        print("\n" + flow["message"] + "\n")

        result = self._msal_app.acquire_token_by_device_flow(flow)
        self._save_token_cache()

        if "access_token" in result:
            logger.info("Authentication successful via Device Code Flow")
            return result["access_token"]

        logger.error(
            "Token acquisition failed: %s",
            result.get("error_description", result.get("error", "unknown error")),
        )
        return None

    def _get_headers(self) -> dict:
        """
        Build HTTP request headers containing a valid OAuth 2.0 Bearer token.

        The token is obtained from the Microsoft identity platform endpoint:
        POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token

        Raises:
            RuntimeError: If a token cannot be acquired.
        """
        token = self._acquire_token()
        if not token:
            raise RuntimeError(
                "Unable to acquire a Microsoft Entra access token. "
                "Ensure TENANT_ID and CLIENT_ID are set correctly in .env."
            )
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "CopilotTUI/0.1.0",
        }

    # ---------------------------------------------------------------------- #
    # Microsoft Graph — M365 Copilot Chat API (preview)                       #
    # Base: https://graph.microsoft.com/beta/copilot                          #
    # ---------------------------------------------------------------------- #

    async def create_conversation(self, title: str) -> APIResponse:
        """
        Create a new Copilot conversation thread.

        POST https://graph.microsoft.com/beta/copilot/conversations
        """
        try:
            headers = await asyncio.get_event_loop().run_in_executor(
                None, self._get_headers
            )
            response = await self.client.post(
                f"{self.base_url}/conversations",
                headers=headers,
                json={"title": title},
            )
            response.raise_for_status()
            data = response.json()
            self.conversation_id = data.get("id")
            logger.info("Created conversation: %s", self.conversation_id)
            return APIResponse(success=True, data=data)
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error("Failed to create conversation: %s", error_msg)
            return APIResponse(success=False, error=error_msg)
        except Exception as e:
            logger.error("Failed to create conversation: %s", str(e))
            return APIResponse(success=False, error=str(e))

    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> APIResponse:
        """
        Send a message in a conversation and retrieve the Copilot reply.

        POST https://graph.microsoft.com/beta/copilot/conversations/{id}/messages
        """
        conv_id = conversation_id or self.conversation_id
        if not conv_id:
            return APIResponse(
                success=False,
                error="No active conversation. Call create_conversation() first.",
            )

        try:
            headers = await asyncio.get_event_loop().run_in_executor(
                None, self._get_headers
            )
            response = await self.client.post(
                f"{self.base_url}/conversations/{conv_id}/messages",
                headers=headers,
                json={"content": message},
            )
            response.raise_for_status()
            data = response.json()
            logger.info("Message sent to conversation %s", conv_id)
            return APIResponse(success=True, data=data)
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error("Failed to send message: %s", error_msg)
            return APIResponse(success=False, error=error_msg)
        except Exception as e:
            logger.error("Failed to send message: %s", str(e))
            return APIResponse(success=False, error=str(e))

    async def stream_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Send a message and stream the Copilot response via server-sent events.

        POST https://graph.microsoft.com/beta/copilot/conversations/{id}/messages
        (with stream: true and Accept: text/event-stream)
        """
        conv_id = conversation_id or self.conversation_id
        if not conv_id:
            yield "Error: No active conversation. Call create_conversation() first."
            return

        try:
            headers = await asyncio.get_event_loop().run_in_executor(
                None, self._get_headers
            )
            headers["Accept"] = "text/event-stream"

            async with self.client.stream(
                "POST",
                f"{self.base_url}/conversations/{conv_id}/messages",
                headers=headers,
                json={"content": message, "stream": True},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        yield line[6:]   # strip the "data: " SSE prefix
                    elif line and not line.startswith(":"):
                        yield line
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error("Streaming error: %s", error_msg)
            yield f"Error: {error_msg}"
        except Exception as e:
            logger.error("Streaming error: %s", str(e))
            yield f"Error: {str(e)}"

    async def get_conversation_history(
        self,
        conversation_id: Optional[str] = None,
    ) -> APIResponse:
        """
        Fetch the complete message history for a conversation.

        GET https://graph.microsoft.com/beta/copilot/conversations/{id}/messages
        """
        conv_id = conversation_id or self.conversation_id
        if not conv_id:
            return APIResponse(success=False, error="No active conversation.")

        try:
            headers = await asyncio.get_event_loop().run_in_executor(
                None, self._get_headers
            )
            response = await self.client.get(
                f"{self.base_url}/conversations/{conv_id}/messages",
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            logger.info("Retrieved history for conversation %s", conv_id)
            return APIResponse(success=True, data=data)
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error("Failed to get conversation history: %s", error_msg)
            return APIResponse(success=False, error=error_msg)
        except Exception as e:
            logger.error("Failed to get conversation history: %s", str(e))
            return APIResponse(success=False, error=str(e))

    async def close(self) -> None:
        """Close the shared HTTP client."""
        await self.client.aclose()


# --------------------------------------------------------------------------- #
# Standalone smoke test                                                         #
# --------------------------------------------------------------------------- #

async def test_api_client():
    """Quick smoke test — requires valid TENANT_ID and CLIENT_ID in .env."""
    client = CopilotAPIClient()
    try:
        print("Creating conversation...")
        result = await client.create_conversation("Test Conversation")
        if result.success:
            print(f"✓ Conversation created: {result.data}")
        else:
            print(f"✗ Failed: {result.error}")
            return

        print("\nSending message...")
        result = await client.send_message("Hello, Copilot!")
        if result.success:
            print(f"✓ Response: {result.data}")
        else:
            print(f"✗ Failed: {result.error}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_api_client())


