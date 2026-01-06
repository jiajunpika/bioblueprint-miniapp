"""SDK client wrapper with session state management."""

import streamlit as st
from pikaminiapp import (
    MiniAppClient,
    MiniAppError,
    MiniAppAuthError,
    MiniAppNotFoundError,
)


def get_client() -> MiniAppClient | None:
    """Get or create SDK client from session state.

    Returns:
        MiniAppClient if configured, None otherwise.
    """
    if "client" not in st.session_state:
        return None
    return st.session_state.client


def init_client(base_url: str, api_key: str) -> tuple[bool, str]:
    """Initialize SDK client and store in session state.

    Args:
        base_url: API base URL
        api_key: API key starting with 'ma_'

    Returns:
        Tuple of (success, message)
    """
    # Close existing client if any
    if "client" in st.session_state and st.session_state.client:
        try:
            st.session_state.client.close()
        except Exception:
            pass

    try:
        client = MiniAppClient(api_key=api_key, base_url=base_url)
        st.session_state.client = client
        st.session_state.base_url = base_url
        st.session_state.api_key = api_key
        return True, "Connected successfully"
    except MiniAppError as e:
        return False, f"Connection failed: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def is_connected() -> bool:
    """Check if client is initialized."""
    return get_client() is not None


def handle_api_error(e: Exception) -> str:
    """Convert API error to user-friendly message."""
    if isinstance(e, MiniAppAuthError):
        return "Authentication failed. Please check your API key."
    elif isinstance(e, MiniAppNotFoundError):
        return "Resource not found. Please check the ID."
    elif isinstance(e, MiniAppError):
        return f"API Error: {e}"
    else:
        return f"Unexpected error: {e}"
