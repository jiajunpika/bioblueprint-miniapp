"""Synchronous HTTP client for the Pika MiniApp API."""

from __future__ import annotations

from typing import Any

import httpx

from pikaminiapp.exceptions import MiniAppAPIError, MiniAppError


class SyncHTTPClient:
    """Synchronous HTTP client with authentication and response handling."""

    def __init__(self, base_url: str, api_key: str):
        self._client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"ApiKey {api_key}"},
            timeout=30.0,
        )

    def get(self, path: str) -> dict[str, Any]:
        """Make a GET request and return the unwrapped data."""
        try:
            response = self._client.get(path)
            return self._handle_response(response)
        except httpx.HTTPError as e:
            raise MiniAppError(f"HTTP error: {e}") from e

    def post(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        """Make a POST request and return the unwrapped data."""
        try:
            response = self._client.post(path, json=json)
            return self._handle_response(response)
        except httpx.HTTPError as e:
            raise MiniAppError(f"HTTP error: {e}") from e

    def put_file(self, url: str, content: bytes, content_type: str) -> None:
        """Upload file content to a presigned URL."""
        try:
            # Use a separate client for S3 uploads (no auth headers)
            response = httpx.put(
                url,
                content=content,
                headers={"Content-Type": content_type},
                timeout=60.0,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise MiniAppError(f"Upload failed: {e}") from e

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Parse response and raise appropriate exceptions on error."""
        try:
            data = response.json()
        except Exception as e:
            raise MiniAppError(f"Invalid JSON response: {e}") from e

        if not data.get("success"):
            error = data.get("error", {})
            raise MiniAppAPIError.from_error_dict(error)

        return data.get("data", {})

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
