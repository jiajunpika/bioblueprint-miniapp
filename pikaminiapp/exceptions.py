"""Exceptions for the Pika MiniApp SDK."""

from __future__ import annotations


class MiniAppError(Exception):
    """Base exception for all SDK errors."""


class MiniAppAPIError(MiniAppError):
    """API returned an error response."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")

    @classmethod
    def from_error_dict(cls, error: dict) -> MiniAppAPIError:
        """Create the appropriate exception type from an error dict."""
        code = error.get("code", "UNKNOWN")
        message = error.get("message", "Unknown error")

        # Extract HTTP status from error code (e.g., A000404 -> 404)
        status = _extract_status(code)

        if status == 401:
            return MiniAppAuthError(code, message)
        elif status == 403:
            return MiniAppForbiddenError(code, message)
        elif status == 404:
            return MiniAppNotFoundError(code, message)
        elif status == 409:
            return MiniAppConflictError(code, message)
        elif status == 422:
            return MiniAppValidationError(code, message)
        else:
            return cls(code, message)


class MiniAppAuthError(MiniAppAPIError):
    """Authentication failed (401)."""


class MiniAppForbiddenError(MiniAppAPIError):
    """Access denied (403)."""


class MiniAppNotFoundError(MiniAppAPIError):
    """Resource not found (404)."""


class MiniAppConflictError(MiniAppAPIError):
    """Resource conflict (409)."""


class MiniAppValidationError(MiniAppAPIError):
    """Validation failed (422)."""


def _extract_status(code: str) -> int | None:
    """Extract HTTP status from error code like 'A000404'."""
    if len(code) >= 7 and code[0].isalpha():
        try:
            return int(code[-3:])
        except ValueError:
            pass
    return None
