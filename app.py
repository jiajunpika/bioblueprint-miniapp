"""Pika MiniApp SDK Demo - Main Entry."""

import streamlit as st
from config import DEFAULT_BASE_URL, DEFAULT_API_KEY
from utils.client import init_client, is_connected

st.set_page_config(
    page_title="Pika MiniApp SDK Demo",
    page_icon="🎮",
    layout="wide",
)

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

# Main content
if not is_connected():
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
    """)
else:
    st.success("Connected! Use the sidebar menu to navigate.")

    st.markdown("""
    ### What you can do:

    - **1_Characters**: Browse character list, enter character ID to query
    - **2_Character_Detail**: View detailed profile, album, and export as JSON
    - **3_Assets**: Browse creation assets with type filters
    - **4_Blueprint_Editor**: Edit blueprint state fields
    """)
