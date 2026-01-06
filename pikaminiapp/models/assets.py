"""Creation assets models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pikaminiapp.models.media import MediaAsset


class CreationAsset(BaseModel):
    """A creation asset (outfit, item, location, or style)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    media: MediaAsset
    object_name: str = Field(alias="objectName")
    name: str
    type: str
    username: str | None = None


class CreationAssetPage(BaseModel):
    """A page of creation assets with pagination info."""

    items: list[CreationAsset]
    cursor: str | None
    has_more: bool
    total: int  # Number of items in this page (same as len(items))