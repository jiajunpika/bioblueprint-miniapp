"""Asynchronous MiniApp client."""

from __future__ import annotations

from pikaminiapp.aio.http import AsyncHTTPClient
from pikaminiapp.aio.resources import AsyncAssetsResource, AsyncCharacterResource, AsyncMediaResource
from pikaminiapp.config import get_base_url


class AsyncMiniAppClient:
    """Asynchronous client for the Pika MiniApp API.

    Example:
        >>> async with AsyncMiniAppClient(api_key="ma_xxx") as client:
        ...     character = await client.character.get_blueprint("char-uuid")
        ...     print(character.profile.profile_name)

        # Or manually manage lifecycle:
        >>> client = AsyncMiniAppClient(api_key="ma_xxx")
        >>> character = await client.character.get_blueprint("char-uuid")
        >>> await client.close()
    """

    def __init__(self, api_key: str, base_url: str | None = None):
        """Initialize the client.

        Args:
            api_key: MiniApp API key (starts with "ma_").
            base_url: API base URL. Falls back to PIKA_BASE_URL env var.
                      Raises MiniAppError if neither is set.
        """
        url = get_base_url(base_url)
        self._http = AsyncHTTPClient(url, api_key)
        self.assets = AsyncAssetsResource(self._http)
        self.character = AsyncCharacterResource(self._http)
        self.media = AsyncMediaResource(self._http)

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._http.close()

    async def __aenter__(self) -> AsyncMiniAppClient:
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
