"""Asynchronous media resource."""

from __future__ import annotations

import mimetypes
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, AsyncIterator, Literal

from pikaminiapp.models import AlbumEntry, AlbumItem, AlbumPage, MediaAsset, PresignedUpload, UploadResult


def _make_unique_filename(filename: str) -> str:
    """Add a UUID prefix to ensure filename uniqueness in S3."""
    unique_id = uuid.uuid4().hex[:12]
    return f"{unique_id}_{filename}"

if TYPE_CHECKING:
    from pikaminiapp.aio.http import AsyncHTTPClient


class AsyncMediaResource:
    """Async resource for media-related API operations."""

    def __init__(self, http: AsyncHTTPClient):
        self._http = http

    async def create(
        self,
        url: str,
        kind: Literal["image", "video", "audio"] = "image",
        *,
        source: str | None = None,
        width: int | None = None,
        height: int | None = None,
        duration_ms: int | None = None,
        thumbnail_url: str | None = None,
    ) -> MediaAsset:
        """Create a media asset from an external URL.

        For images: Downloads and re-uploads to S3, auto-extracts dimensions.
        For video/audio: Creates DB record with provided URL and metadata.

        Args:
            url: HTTP/HTTPS URL of media to import.
            kind: Media type - "image", "video", or "audio".
            source: Optional tracking identifier (e.g., "my_tool").
            width: Width in pixels (image/video).
            height: Height in pixels (image/video).
            duration_ms: Duration in milliseconds (video/audio).
            thumbnail_url: Thumbnail URL (video only).

        Returns:
            The created MediaAsset.
        """
        payload: dict = {"url": url, "kind": kind}
        if source is not None:
            payload["source"] = source
        if width is not None:
            payload["width"] = width
        if height is not None:
            payload["height"] = height
        if duration_ms is not None:
            payload["durationMs"] = duration_ms
        if thumbnail_url is not None:
            payload["thumbnailUrl"] = thumbnail_url

        data = await self._http.post("/miniapp/media/create", payload)
        return MediaAsset.model_validate(data["media"])

    async def add_to_album(
        self,
        character_id: str,
        media_id: str,
        *,
        captured: bool = True,
    ) -> AlbumEntry:
        """Add a media asset to a character's album.

        Uses upsert - if entry exists (including soft-deleted), it updates
        and restores it.

        Args:
            character_id: UUID of the character.
            media_id: UUID of the media asset.
            captured: Whether media was "captured" (default: True).

        Returns:
            AlbumEntry with the album entry ID.

        Raises:
            MiniAppNotFoundError: Character not found.
            MiniAppConflictError: Media already in another user's album.
        """
        data = await self._http.post(
            "/miniapp/media/album/add",
            {
                "characterId": character_id,
                "mediaId": media_id,
                "captured": captured,
            },
        )
        return AlbumEntry.model_validate(data)

    async def list_album(
        self,
        character_id: str,
        *,
        limit: int = 20,
        cursor: str | None = None,
    ) -> AlbumPage:
        """List items in a character's album.

        Returns album items in reverse chronological order (newest first).

        Args:
            character_id: UUID of the character.
            limit: Number of items per page (default: 20).
            cursor: Pagination cursor from previous response.

        Returns:
            AlbumPage with items and pagination info.
        """
        seek: dict = {"limit": limit}
        if cursor is not None:
            seek["cursor"] = cursor

        data = await self._http.post(
            "/miniapp/media/album/list",
            {"characterId": character_id, "seek": seek},
        )

        items = [AlbumItem.model_validate(item) for item in data.get("items", [])]
        next_info = data.get("next", {})

        return AlbumPage(
            items=items,
            cursor=next_info.get("cursor"),
            has_more=next_info.get("hasMore", False),
        )

    async def iter_album(
        self,
        character_id: str,
        *,
        page_size: int = 50,
    ) -> AsyncIterator[AlbumItem]:
        """Iterate through all items in a character's album.

        Auto-paginates through all pages, yielding items one by one.

        Args:
            character_id: UUID of the character.
            page_size: Number of items to fetch per page (default: 50).

        Yields:
            AlbumItem objects from the album.
        """
        cursor = None
        while True:
            page = await self.list_album(character_id, limit=page_size, cursor=cursor)
            for item in page.items:
                yield item
            if not page.has_more:
                break
            cursor = page.cursor

    async def get_all_album_items(self, character_id: str) -> list[AlbumItem]:
        """Get all items from a character's album.

        Fetches all pages and returns a complete list.

        Args:
            character_id: UUID of the character.

        Returns:
            List of all AlbumItem objects.
        """
        items = []
        async for item in self.iter_album(character_id):
            items.append(item)
        return items

    async def upload(
        self,
        file_path: str,
        *,
        kind: Literal["image", "video", "audio"] = "image",
        source: str | None = None,
    ) -> UploadResult:
        """Upload a local file to S3 and create a media asset.

        Does NOT add to album. Use `upload_to_album()` to upload and add in one step,
        or call `add_to_album()` separately after uploading.

        Args:
            file_path: Path to the local file.
            kind: Media type - "image", "video", or "audio".
            source: Optional tracking identifier.

        Returns:
            UploadResult with media_id, url, and media asset.

        Example:
            >>> result = await client.media.upload("image.png")
            >>> print(result.url)  # CDN URL
            >>> # Later, add to album if needed:
            >>> await client.media.add_to_album(character_id, result.media_id)
        """
        path = Path(file_path)
        return await self.upload_bytes(
            content=path.read_bytes(),
            filename=path.name,
            content_type=None,  # Will be guessed from filename
            kind=kind,
            source=source,
        )

    async def upload_bytes(
        self,
        content: bytes,
        *,
        filename: str = "upload.png",
        content_type: str | None = None,
        kind: Literal["image", "video", "audio"] = "image",
        source: str | None = None,
    ) -> UploadResult:
        """Upload raw bytes to S3 and create a media asset.

        Does NOT add to album. Use `upload_bytes_to_album()` to upload and add
        in one step, or call `add_to_album()` separately after uploading.

        Args:
            content: Raw bytes of the file to upload.
            filename: Filename for the upload (used for content-type detection).
            content_type: MIME type (e.g., "image/png"). If not provided, guessed from filename.
            kind: Media type - "image", "video", or "audio".
            source: Optional tracking identifier.

        Returns:
            UploadResult with media_id, url, and media asset.

        Example:
            >>> result = await client.media.upload_bytes(png_bytes, filename="gen.png")
            >>> print(result.url)  # CDN URL
            >>> print(result.media_id)  # Use for add_to_album later
        """
        # Determine content type if not provided
        if content_type is None:
            content_type, _ = mimetypes.guess_type(filename)
            if content_type is None:
                content_type = "application/octet-stream"

        # Make filename unique to prevent overwrites
        unique_filename = _make_unique_filename(filename)

        # Get presigned upload URL (fileType is "image"/"video"/"audio", not MIME type)
        presign = await self._get_presigned_upload(kind, unique_filename)

        # Upload to S3
        await self._http.put_file(presign.presigned_url, content, content_type)

        # Create media asset
        media = await self.create(presign.file_url, kind=kind, source=source)

        return UploadResult(
            media_id=media.media_id,
            url=presign.file_url,
            media=media,
        )

    async def upload_to_album(
        self,
        character_id: str,
        file_path: str,
        *,
        kind: Literal["image", "video", "audio"] = "image",
        captured: bool = True,
        source: str | None = None,
    ) -> UploadResult:
        """Upload a local file and add it to a character's album.

        Combines `upload()` + `add_to_album()` in one call.

        Args:
            character_id: UUID of the character.
            file_path: Path to the local file.
            kind: Media type - "image", "video", or "audio".
            captured: Whether media was "captured" (default: True).
            source: Optional tracking identifier.

        Returns:
            UploadResult with media_id, url, media asset, and album_id.
        """
        result = await self.upload(file_path, kind=kind, source=source)
        entry = await self.add_to_album(character_id, result.media_id, captured=captured)
        result.album_id = entry.album_id
        return result

    async def upload_bytes_to_album(
        self,
        character_id: str,
        content: bytes,
        *,
        filename: str = "upload.png",
        content_type: str | None = None,
        kind: Literal["image", "video", "audio"] = "image",
        captured: bool = True,
        source: str | None = None,
    ) -> UploadResult:
        """Upload raw bytes and add to a character's album.

        Combines `upload_bytes()` + `add_to_album()` in one call.

        Args:
            character_id: UUID of the character.
            content: Raw bytes of the file to upload.
            filename: Filename for the upload (used for content-type detection).
            content_type: MIME type (e.g., "image/png"). If not provided, guessed from filename.
            kind: Media type - "image", "video", or "audio".
            captured: Whether media was "captured" (default: True).
            source: Optional tracking identifier.

        Returns:
            UploadResult with media_id, url, media asset, and album_id.

        Example:
            >>> result = await client.media.upload_bytes_to_album(
            ...     character_id="char-uuid",
            ...     content=png_bytes,
            ...     filename="generated.png",
            ... )
            >>> print(result.url)       # CDN URL
            >>> print(result.album_id)  # Album entry ID
        """
        result = await self.upload_bytes(
            content=content,
            filename=filename,
            content_type=content_type,
            kind=kind,
            source=source,
        )
        entry = await self.add_to_album(character_id, result.media_id, captured=captured)
        result.album_id = entry.album_id
        return result

    async def _get_presigned_upload(self, file_type: str, filename: str) -> PresignedUpload:
        """Get a presigned URL for uploading a file."""
        data = await self._http.post(
            "/miniapp/files/presign/upload",
            {"fileType": file_type, "filename": filename},
        )
        return PresignedUpload.model_validate(data)
