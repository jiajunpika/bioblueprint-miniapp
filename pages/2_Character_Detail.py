"""Character detail page with album and JSON export."""

import json
import streamlit as st
from utils.client import get_client, is_connected, handle_api_error

st.set_page_config(page_title="Character Detail", page_icon="📋", layout="wide")

st.title("📋 Character Detail")

if not is_connected():
    st.warning("Please connect to API first (go to main page)")
    st.stop()

client = get_client()

# Character ID input
character_id = st.text_input(
    "Character ID",
    value=st.session_state.get("selected_character_id", ""),
    placeholder="Enter character UUID",
)

if not character_id:
    st.info("Enter a character ID above to view details")
    st.stop()

# Fetch character data
with st.spinner("Loading character..."):
    try:
        character = client.character.get_blueprint(character_id)
    except Exception as e:
        st.error(handle_api_error(e))
        st.stop()

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["Profile", "Identity Card", "Album", "JSON Export"])

# Tab 1: Profile
with tab1:
    col1, col2 = st.columns([1, 2])

    with col1:
        if character.profile.avatar:
            st.image(character.profile.avatar, use_container_width=True)

    with col2:
        st.markdown(f"### {character.profile.profile_name}")
        st.markdown(f"**@{character.profile.username}**")

        if character.profile.identity_card.bio:
            st.markdown(f"_{character.profile.identity_card.bio}_")

        st.divider()

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Followers", character.profile.followers_count)
        with col_b:
            st.metric("Following", character.profile.following_count)
        with col_c:
            st.metric("Posts", character.profile.posts_count)

        if character.profile.voice_url:
            st.audio(character.profile.voice_url)

# Tab 2: Identity Card
with tab2:
    card = character.profile.identity_card

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Basic Info")
        info_items = [
            ("Gender", card.gender),
            ("Age", card.age),
            ("Occupation", card.occupation),
            ("Location", card.location),
            ("Zodiac", card.zodiac),
            ("Relationship", card.relationship),
        ]
        for label, value in info_items:
            if value:
                st.markdown(f"**{label}:** {value}")

    with col2:
        st.markdown("#### Appearance")
        appearance_items = [
            ("Phenotype", card.phenotype),
            ("Hair", card.hair),
            ("Hair Style", card.hair_style),
            ("Eyes", card.ocular_scan),
            ("Style", card.style),
        ]
        for label, value in appearance_items:
            if value:
                st.markdown(f"**{label}:** {value}")

    if card.interests:
        st.markdown("#### Interests")
        st.markdown(" ".join([f"`{i}`" for i in card.interests]))

    if card.profile_tags:
        st.markdown("#### Tags")
        st.markdown(" ".join([f"`{t}`" for t in card.profile_tags]))

# Tab 3: Album
with tab3:
    st.markdown("#### Album Preview")

    with st.spinner("Loading album..."):
        try:
            # Get first page of album items
            album_items = []
            for item in client.media.iter_album(character_id):
                album_items.append(item)
                if len(album_items) >= 20:  # Limit to 20 for preview
                    break

            if not album_items:
                st.info("No items in album")
            else:
                st.markdown(f"Showing {len(album_items)} items")

                # Display in grid
                cols = st.columns(4)
                for i, item in enumerate(album_items):
                    if item.media:
                        with cols[i % 4]:
                            if item.media.kind == "image":
                                st.image(
                                    item.media.payload.image_url,
                                    use_container_width=True,
                                )
                            elif item.media.kind == "video":
                                if hasattr(item.media.payload, "image_url") and item.media.payload.image_url:
                                    st.image(
                                        item.media.payload.image_url,
                                        use_container_width=True,
                                    )
                                    st.caption("📹 Video")
                                else:
                                    st.video(item.media.payload.video_url)

        except Exception as e:
            st.error(handle_api_error(e))

# Tab 4: JSON Export
with tab4:
    st.markdown("#### Export as JSON")

    export_options = st.multiselect(
        "Select data to export",
        ["Profile", "Identity Card", "Blueprint State", "Full Character"],
        default=["Full Character"],
    )

    if st.button("Generate JSON", type="primary"):
        export_data = {}

        if "Full Character" in export_options:
            export_data = character.model_dump(mode="json")
        else:
            if "Profile" in export_options:
                export_data["profile"] = character.profile.model_dump(mode="json")
            if "Identity Card" in export_options:
                export_data["identity_card"] = character.profile.identity_card.model_dump(mode="json")
            if "Blueprint State" in export_options and character.blueprint:
                export_data["blueprint"] = character.blueprint.model_dump(mode="json")

        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)

        st.code(json_str, language="json")

        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"character_{character_id[:8]}.json",
            mime="application/json",
        )
