"""Creation assets browsing page."""

import streamlit as st
from utils.client import get_client, is_connected, handle_api_error

st.set_page_config(page_title="Assets", page_icon="🎨", layout="wide")

st.title("🎨 Creation Assets")

if not is_connected():
    st.warning("Please connect to API first (go to main page)")
    st.stop()

client = get_client()

# Get available types
with st.spinner("Loading asset types..."):
    try:
        asset_types = client.assets.types()
    except Exception as e:
        st.error(handle_api_error(e))
        asset_types = []

# Filter controls
col1, col2 = st.columns([2, 1])

with col1:
    selected_type = st.selectbox(
        "Filter by Type",
        options=["All"] + asset_types,
        index=0,
    )

with col2:
    items_per_page = st.selectbox(
        "Items per page",
        options=[12, 24, 48],
        index=0,
    )

# Fetch assets
type_filter = None if selected_type == "All" else selected_type

with st.spinner("Loading assets..."):
    try:
        assets = []
        for asset in client.assets.iter(type=type_filter):
            assets.append(asset)
            if len(assets) >= items_per_page:
                break

        if not assets:
            st.info("No assets found")
            st.stop()

        st.markdown(f"Showing {len(assets)} assets")

        # Display in grid
        cols = st.columns(4)
        for i, asset in enumerate(assets):
            with cols[i % 4]:
                with st.container(border=True):
                    # Asset image
                    if asset.media and asset.media.kind == "image":
                        st.image(
                            asset.media.payload.image_url,
                            use_container_width=True,
                        )

                    # Asset info
                    st.markdown(f"**{asset.name}**")
                    st.caption(f"Type: {asset.type}")
                    if asset.username:
                        st.caption(f"By: @{asset.username}")

    except Exception as e:
        st.error(handle_api_error(e))
