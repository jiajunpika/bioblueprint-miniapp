"""Synchronous MiniApp client."""

from __future__ import annotations

from pikaminiapp.config import get_base_url
from pikaminiapp.sync.http import SyncHTTPClient
from pikaminiapp.sync.resources import AssetsResource, CharacterResource, MediaResource


class MiniAppClient:
    """Synchronous client for the Pika MiniApp API.

    Example:
        >>> client = MiniAppClient(api_key="ma_xxx")
        >>> character = client.character.get_blueprint("char-uuid")
        >>> print(character.profile.profile_name)
        >>> client.close()

        # Or use as context manager:
        >>> with MiniAppClient(api_key="ma_xxx") as client:
        ...     character = client.character.get_blueprint("char-uuid")
    """

    def __init__(self, api_key: str, base_url: str | None = None):
        """Initialize the client.

        Args:
            api_key: MiniApp API key (starts with "ma_").
            base_url: API base URL. Falls back to PIKA_BASE_URL env var.
                      Raises MiniAppError if neither is set.
        """
        url = get_base_url(base_url)
        self._http = SyncHTTPClient(url, api_key)
        self.assets = AssetsResource(self._http)
        self.character = CharacterResource(self._http)
        self.media = MediaResource(self._http)

    def close(self) -> None:
        """Close the client and release resources."""
        self._http.close()

    def __enter__(self) -> MiniAppClient:
        return self

    def __exit__(self, *args) -> None:
        self.close()
