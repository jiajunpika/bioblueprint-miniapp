"""Pika MiniApp SDK Demo - Main Entry."""

import streamlit as st
from config import DEFAULT_BASE_URL, DEFAULT_API_KEY
from utils.client import init_client, is_connected

st.set_page_config(
    page_title="Pika MiniApp SDK Demo",
    page_icon="🎮",
    layout="wide",
)

# Auto-connect on startup if environment variables are set
if not is_connected() and DEFAULT_API_KEY:
    with st.spinner("Auto-connecting to API..."):
        success, message = init_client(DEFAULT_BASE_URL, DEFAULT_API_KEY)
        if success:
            # Redirect to Character Detail page after auto-connect
            st.switch_page("pages/2_Character_Detail.py")

# If connected, redirect to Character Detail
if is_connected():
    st.switch_page("pages/2_Character_Detail.py")

st.title("Pika MiniApp SDK Demo")

# Sidebar - API Configuration
with st.sidebar:
    st.header("API Configuration")

    base_url = st.text_input(
        "Base URL",
        value=st.session_state.get("base_url", DEFAULT_BASE_URL),
        help="Staging: https://mnbvcxzlkjh9o4p.pika.art",
    )

    api_key = st.text_input(
        "API Key",
        value=st.session_state.get("api_key", DEFAULT_API_KEY),
        type="password",
        help="API key starting with 'ma_'",
    )

    if st.button("Connect", type="primary", use_container_width=True):
        if not api_key:
            st.error("Please enter an API key")
        elif not api_key.startswith("ma_"):
            st.warning("API key should start with 'ma_'")
        else:
            with st.spinner("Connecting..."):
                success, message = init_client(base_url, api_key)
                if success:
                    st.success(message)
                    st.switch_page("pages/2_Character_Detail.py")
                else:
                    st.error(message)

    # Connection status
    st.divider()
    if is_connected():
        st.success("Status: Connected")
    else:
        st.warning("Status: Not connected")

    st.divider()
    st.caption("Navigate using the sidebar menu above")

# Main content - only shown if not connected
st.info("Please configure your API credentials in the sidebar and click 'Connect' to get started.")

st.markdown("""
### Quick Start

1. Enter your **Base URL** (staging server is pre-filled)
2. Enter your **API Key** (starts with `ma_`)
3. Click **Connect**
4. Use the sidebar menu to navigate between pages

### Available Pages

- **Characters**: Browse and search characters
- **Character Detail**: View profile, album, and export JSON
- **Assets**: Browse creation assets (outfits, etc.)
- **Blueprint Editor**: Edit character AI personality data

### Environment Variables

Set these environment variables to auto-connect:
- `PIKA_BASE_URL`: API base URL
- `PIKA_API_KEY`: Your API key (starts with `ma_`)
""")
