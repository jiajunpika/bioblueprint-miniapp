"""Character browsing page."""

import streamlit as st
from config import KNOWN_CHARACTERS
from utils.client import get_client, is_connected, handle_api_error

st.set_page_config(page_title="Characters", page_icon="👤", layout="wide")

st.title("👤 Characters")

if not is_connected():
    st.warning("Please connect to API first (go to main page)")
    st.stop()

client = get_client()

# Character ID input
st.subheader("Query Character by ID")

col1, col2 = st.columns([3, 1])
with col1:
    character_id = st.text_input(
        "Character ID",
        placeholder="Enter character UUID",
        help="The UUID of the character to query",
    )

with col2:
    st.write("")  # Spacing
    st.write("")
    query_btn = st.button("Query", type="primary", use_container_width=True)

# Quick access from known characters
if KNOWN_CHARACTERS:
    st.subheader("Known Characters")
    cols = st.columns(min(len(KNOWN_CHARACTERS), 4))
    for i, char in enumerate(KNOWN_CHARACTERS):
        with cols[i % 4]:
            if st.button(char["name"], key=f"char_{i}", use_container_width=True):
                st.session_state.selected_character_id = char["id"]
                st.switch_page("pages/2_Character_Detail.py")

# Query result
if query_btn and character_id:
    with st.spinner("Fetching character..."):
        try:
            character = client.character.get_blueprint(character_id)

            st.success(f"Found: {character.profile.profile_name}")

            # Display basic info
            col1, col2 = st.columns([1, 2])

            with col1:
                if character.profile.avatar:
                    st.image(character.profile.avatar, width=200)

            with col2:
                st.markdown(f"**Name:** {character.profile.profile_name}")
                st.markdown(f"**Username:** @{character.profile.username}")
                if character.profile.identity_card.bio:
                    st.markdown(f"**Bio:** {character.profile.identity_card.bio}")
                st.markdown(f"**Followers:** {character.profile.followers_count}")
                st.markdown(f"**Posts:** {character.profile.posts_count}")

            # Button to view detail
            if st.button("View Full Detail →", type="primary"):
                st.session_state.selected_character_id = character_id
                st.switch_page("pages/2_Character_Detail.py")

        except Exception as e:
            st.error(handle_api_error(e))
elif query_btn:
    st.warning("Please enter a character ID")
