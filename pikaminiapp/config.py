"""Configuration for the Pika MiniApp SDK."""

from __future__ import annotations

import os

from pikaminiapp.exceptions import MiniAppError

ENV_BASE_URL = "PIKA_BASE_URL"


def get_base_url(override: str | None = None) -> str:
    """Get the API base URL.

    Priority: override param > environment variable.

    Raises:
        MiniAppError: If neither override nor PIKA_BASE_URL env var is set.
    """
    url = override or os.getenv(ENV_BASE_URL)
    if not url:
        raise MiniAppError(
            "No base URL configured. Either pass base_url to the client "
            "or set the PIKA_BASE_URL environment variable."
        )
    return url