"""Synchronous assets resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from pikaminiapp.models.assets import CreationAsset, CreationAssetPage

if TYPE_CHECKING:
    from pikaminiapp.sync.http import SyncHTTPClient


class AssetsResource:
    """Resource for creation assets API operations."""

    def __init__(self, http: SyncHTTPClient):
        self._http = http

    def list(
        self,
        *,
        limit: int = 20,
        cursor: str | None = None,
        type: str | None = None,
    ) -> CreationAssetPage:
        """List creation assets.

        Returns assets in reverse chronological order (newest first).

        Args:
            limit: Number of items per page (1-100, default: 20).
            cursor: Pagination cursor from previous response.
            type: Optional filter for asset type (e.g., "Outfit", "Accessories").
                Use types() to get all available types.

        Returns:
            CreationAssetPage with items and pagination info.
        """
        payload: dict = {"limit": limit}
        if cursor is not None:
            payload["cursor"] = cursor
        if type is not None:
            payload["type"] = type

        data = self._http.post("/miniapp/assets/list", payload)

        items = [CreationAsset.model_validate(item) for item in data.get("items", [])]
        next_info = data.get("next") or {}

        return CreationAssetPage(
            items=items,
            cursor=next_info.get("cursor"),
            has_more=next_info.get("hasMore", False),
            total=data.get("total", 0),
        )

    def iter(
        self,
        *,
        page_size: int = 50,
        type: str | None = None,
    ) -> Iterator[CreationAsset]:
        """Iterate through all creation assets.

        Auto-paginates through all pages, yielding items one by one.

        Args:
            page_size: Number of items to fetch per page (default: 50).
            type: Optional filter for asset type (e.g., "Outfit", "Accessories").
                Use types() to get all available types.

        Yields:
            CreationAsset objects.
        """
        cursor = None
        while True:
            page = self.list(limit=page_size, cursor=cursor, type=type)
            yield from page.items
            if not page.has_more:
                break
            cursor = page.cursor

    def get_all(
        self,
        *,
        type: str | None = None,
    ) -> list[CreationAsset]:
        """Get all creation assets.

        Fetches all pages and returns a complete list.

        Args:
            type: Optional filter for asset type (e.g., "Outfit", "Accessories").
                Use types() to get all available types.

        Returns:
            List of all CreationAsset objects.
        """
        return list(self.iter(type=type))

    def types(self) -> list[str]:
        """Get all distinct asset types.

        Returns:
            List of asset type strings (e.g., ['item', 'location', 'outfit', 'style']).
        """
        data = self._http.get("/miniapp/assets/types")
        return data.get("types", [])