"""Asynchronous character resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pikaminiapp.models import CharacterBlueprintState, CharacterItem

if TYPE_CHECKING:
    from pikaminiapp.aio.http import AsyncHTTPClient


class AsyncCharacterResource:
    """Async resource for character-related API operations."""

    def __init__(self, http: AsyncHTTPClient):
        self._http = http

    async def get_blueprint(self, character_id: str) -> CharacterItem:
        """Get full character blueprint (profile + state) by ID.

        Args:
            character_id: UUID of the character to fetch.

        Returns:
            CharacterItem with profile and blueprint data.

        Raises:
            MiniAppNotFoundError: Character not found.
            MiniAppAuthError: Invalid/missing authentication.
        """
        data = await self._http.post(
            "/miniapp/character/blueprint",
            {"characterId": character_id},
        )
        return CharacterItem.model_validate(data["character"])

    async def upsert_blueprint_state(
        self,
        character_id: str,
        blueprint: CharacterBlueprintState | dict[str, Any],
    ) -> CharacterItem:
        """Upsert character blueprint state fields (partial update).

        Uses shallow merge semantics: each field is merged at the top level,
        where new keys are added and existing keys are overwritten. To delete
        a key, explicitly set it to None.

        Args:
            character_id: UUID of the character to update.
            blueprint: Blueprint state fields to update. Can be a
                CharacterBlueprintState model or a dict with camelCase keys.
                Only provided fields are updated.

        Returns:
            CharacterItem with the updated profile and blueprint data.

        Raises:
            MiniAppNotFoundError: Character not found.
            MiniAppAuthError: Invalid/missing authentication.
        """
        if isinstance(blueprint, CharacterBlueprintState):
            blueprint_dict = blueprint.model_dump(by_alias=True, exclude_none=True)
        else:
            blueprint_dict = blueprint

        payload = {**blueprint_dict, "characterId": character_id}
        data = await self._http.post("/miniapp/character/blueprint/state", payload)
        return CharacterItem.model_validate(data["character"])
