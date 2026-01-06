"""Character-related models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IdentityCard(BaseModel):
    """Character identity card with appearance and personal info."""

    model_config = ConfigDict(populate_by_name=True)

    # Appearance
    gender: str | None = None
    age: str | None = None
    phenotype: str | None = None
    hair: str | None = None
    hair_style: str | None = Field(default=None, alias="hairStyle")
    ocular_scan: str | None = Field(default=None, alias="ocularScan")  # eye description

    # Identity
    occupation: str | None = None
    location: str | None = None
    interests: list[str] | None = None
    zodiac: str | None = None
    relationship: str | None = None
    bio: str | None = None
    profile_tags: list[str] | None = Field(default=None, alias="profileTags")

    # Style
    style: str | None = None
    style_image: str | None = Field(default=None, alias="styleImage")
    title: str | None = None


class CharacterBlueprintProfile(BaseModel):
    """Character's public profile information."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    profile_name: str = Field(alias="profileName")
    username: str
    avatar: str
    identity_card: IdentityCard = Field(alias="identityCard")
    followers_count: int = Field(default=0, alias="followersCount")
    following_count: int = Field(default=0, alias="followingCount")
    posts_count: int = Field(default=0, alias="postsCount")
    voice_url: str | None = Field(default=None, alias="voiceUrl")
    handles: dict[str, Any] | None = None


class CharacterBlueprintState(BaseModel):
    """Character's internal blueprint state (AI personality data)."""

    model_config = ConfigDict(populate_by_name=True)

    core_personality: dict[str, Any] | None = Field(default=None, alias="corePersonality")
    expression_engine: dict[str, Any] | None = Field(default=None, alias="expressionEngine")
    aesthetic_engine: dict[str, Any] | None = Field(default=None, alias="aestheticEngine")
    simulation: dict[str, Any] | None = None
    goal: dict[str, Any] | None = None
    backstory: dict[str, Any] | None = None
    backstory_updated_at: int | None = Field(default=None, alias="backstoryUpdatedAt")
    onboarding_input: dict[str, Any] | None = Field(default=None, alias="onboardingInput")
    prototype: dict[str, Any] | None = None


class CharacterItem(BaseModel):
    """Full character data including profile and blueprint."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    profile: CharacterBlueprintProfile
    blueprint: CharacterBlueprintState | None = None
