"""Media-related models."""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field


class ImagePayload(BaseModel):
    """Payload for image media assets."""

    model_config = ConfigDict(populate_by_name=True)

    image_url: str = Field(alias="imageUrl")
    width: int | None = None
    height: int | None = None


class VideoPayload(BaseModel):
    """Payload for video media assets."""

    model_config = ConfigDict(populate_by_name=True)

    video_url: str = Field(alias="videoUrl")
    image_url: str | None = Field(default=None, alias="imageUrl")  # thumbnail
    width: int | None = None
    height: int | None = None
    duration_ms: int | None = Field(default=None, alias="durationMs")


class AudioPayload(BaseModel):
    """Payload for audio media assets."""

    model_config = ConfigDict(populate_by_name=True)

    audio_url: str = Field(alias="audioUrl")
    duration_ms: int | None = Field(default=None, alias="durationMs")


MediaPayload = Annotated[
    Union[ImagePayload, VideoPayload, AudioPayload],
    Field(discriminator=None),
]


class MediaAsset(BaseModel):
    """A media asset (image, video, or audio)."""

    model_config = ConfigDict(populate_by_name=True)

    media_id: str = Field(alias="mediaId")
    kind: Literal["image", "video", "audio"]
    payload: ImagePayload | VideoPayload | AudioPayload
    prompt: str | None = None
    prompt_mentions: list[str] | None = Field(default=None, alias="promptMentions")
    created_at: int | None = Field(default=None, alias="createdAt")

    def __init__(self, **data):
        # Handle payload type based on kind
        if "payload" in data and isinstance(data["payload"], dict):
            kind = data.get("kind", "image")
            payload_data = data["payload"]
            if kind == "image":
                data["payload"] = ImagePayload.model_validate(payload_data)
            elif kind == "video":
                data["payload"] = VideoPayload.model_validate(payload_data)
            elif kind == "audio":
                data["payload"] = AudioPayload.model_validate(payload_data)
        super().__init__(**data)


class AlbumItem(BaseModel):
    """An item in a character's album."""

    model_config = ConfigDict(populate_by_name=True)

    media: MediaAsset | None = None
    created_at: int = Field(alias="createdAt")


class AlbumPage(BaseModel):
    """A page of album items with pagination info."""

    items: list[AlbumItem]
    cursor: str | None
    has_more: bool


class AlbumEntry(BaseModel):
    """Result of adding media to an album."""

    model_config = ConfigDict(populate_by_name=True)

    album_id: str = Field(alias="albumId")


class PresignedUpload(BaseModel):
    """Presigned URL response for file uploads."""

    model_config = ConfigDict(populate_by_name=True)

    presigned_url: str = Field(alias="presignedUrl")
    file_url: str = Field(alias="fileUrl")


class UploadResult(BaseModel):
    """Result of uploading media.

    When uploaded via `upload()` or `upload_bytes()`, album_id is None.
    When uploaded via `upload_to_album()` or `upload_bytes_to_album()`,
    album_id contains the album entry ID.
    """

    media_id: str
    url: str
    media: MediaAsset
    album_id: str | None = None
