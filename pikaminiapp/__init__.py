"""Pika MiniApp SDK - Python client for the Nova2 MiniApp API.

Example:
    >>> from pikaminiapp import MiniAppClient
    >>>
    >>> client = MiniAppClient(api_key="ma_xxx")
    >>> character = client.character.get_blueprint("char-uuid")
    >>> print(character.profile.profile_name)
    >>>
    >>> # Upload to album
    >>> entry = client.media.upload_to_album(
    ...     character_id="char-uuid",
    ...     file_path="/path/to/image.png"
    ... )
    >>>
    >>> # Iterate album
    >>> for item in client.media.iter_album("char-uuid"):
    ...     print(item.media.payload.image_url)
    >>>
    >>> client.close()

Async example:
    >>> from pikaminiapp import AsyncMiniAppClient
    >>>
    >>> async with AsyncMiniAppClient(api_key="ma_xxx") as client:
    ...     character = await client.character.get_blueprint("char-uuid")
    ...     async for item in client.media.iter_album("char-uuid"):
    ...         print(item.media.payload.image_url)
"""

from pikaminiapp.aio import AsyncMiniAppClient
from pikaminiapp.exceptions import (
    MiniAppAPIError,
    MiniAppAuthError,
    MiniAppConflictError,
    MiniAppError,
    MiniAppForbiddenError,
    MiniAppNotFoundError,
    MiniAppValidationError,
)
from pikaminiapp.models import (
    AlbumEntry,
    AlbumItem,
    AlbumPage,
    AudioPayload,
    CharacterBlueprintProfile,
    CharacterBlueprintState,
    CharacterItem,
    IdentityCard,
    ImagePayload,
    MediaAsset,
    UploadResult,
    VideoPayload,
)
from pikaminiapp.sync import MiniAppClient

__version__ = "0.1.0"

__all__ = [
    # Clients
    "MiniAppClient",
    "AsyncMiniAppClient",
    # Exceptions
    "MiniAppError",
    "MiniAppAPIError",
    "MiniAppAuthError",
    "MiniAppForbiddenError",
    "MiniAppNotFoundError",
    "MiniAppConflictError",
    "MiniAppValidationError",
    # Character models
    "CharacterItem",
    "CharacterBlueprintProfile",
    "CharacterBlueprintState",
    "IdentityCard",
    # Media models
    "MediaAsset",
    "ImagePayload",
    "VideoPayload",
    "AudioPayload",
    "AlbumItem",
    "AlbumPage",
    "AlbumEntry",
    "UploadResult",
]
