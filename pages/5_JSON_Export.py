"""JSON Export page for character data."""

import json
import streamlit as st
from config import DEFAULT_CHARACTER_ID, KNOWN_CHARACTERS, DEFAULT_BASE_URL, DEFAULT_API_KEY
from utils.client import get_client, is_connected, handle_api_error, init_client

st.set_page_config(page_title="JSON Export", page_icon="📤", layout="wide")

st.title("📤 JSON Export")

# Get UUID from URL query params
url_uuid = st.query_params.get("uuid", None)

# Auto-connect if not connected but env vars are set
if not is_connected() and DEFAULT_API_KEY:
    with st.spinner("Auto-connecting to API..."):
        init_client(DEFAULT_BASE_URL, DEFAULT_API_KEY)

if not is_connected():
    st.warning("Please connect to API first (go to main page)")
    st.stop()

client = get_client()

# Determine initial character ID
initial_character_id = url_uuid or st.session_state.get("selected_character_id", DEFAULT_CHARACTER_ID)

# Character selection
col1, col2 = st.columns([2, 1])

with col1:
    character_options = ["-- Custom ID --"] + [f"{c['name']} ({c['id'][:8]}...)" for c in KNOWN_CHARACTERS]

    default_index = 0
    if url_uuid:
        for i, c in enumerate(KNOWN_CHARACTERS):
            if c["id"] == url_uuid:
                default_index = i + 1
                break

    selected_option = st.selectbox("Quick Select", character_options, index=default_index)

with col2:
    if selected_option == "-- Custom ID --":
        character_id = st.text_input(
            "Character ID",
            value=initial_character_id,
            placeholder="Enter character UUID",
        )
    else:
        idx = character_options.index(selected_option) - 1
        character_id = KNOWN_CHARACTERS[idx]["id"]
        st.text_input("Character ID", value=character_id, disabled=True)

if not character_id:
    st.info("Select a character or enter a character ID")
    st.stop()

# Fetch character data
with st.spinner("Loading character..."):
    try:
        character = client.character.get_blueprint(character_id)
    except Exception as e:
        st.error(handle_api_error(e))
        st.stop()

st.divider()

# Export options
all_export_options = [
    "Full Character",
    "Profile Only",
    "Identity Card Only",
    "Core Personality",
    "Expression Engine",
    "Aesthetic Engine",
    "Simulation",
    "Backstory",
    "Goals",
]

export_options = st.multiselect(
    "Select data to export",
    all_export_options,
    default=all_export_options,
)

col1, col2 = st.columns([1, 4])
with col1:
    generate_btn = st.button("Generate JSON", type="primary", use_container_width=True)

if generate_btn:
    export_data = {}

    if "Full Character" in export_options:
        export_data = character.model_dump(mode="json")
    else:
        if "Profile Only" in export_options and character.profile:
            export_data["profile"] = character.profile.model_dump(mode="json")
        if "Identity Card Only" in export_options and character.profile and character.profile.identity_card:
            export_data["identityCard"] = character.profile.identity_card.model_dump(mode="json")
        if character.blueprint:
            if "Core Personality" in export_options and character.blueprint.core_personality:
                export_data["corePersonality"] = character.blueprint.core_personality
            if "Expression Engine" in export_options and character.blueprint.expression_engine:
                export_data["expressionEngine"] = character.blueprint.expression_engine
            if "Aesthetic Engine" in export_options and character.blueprint.aesthetic_engine:
                export_data["aestheticEngine"] = character.blueprint.aesthetic_engine
            if "Simulation" in export_options and character.blueprint.simulation:
                export_data["simulation"] = character.blueprint.simulation
            if "Backstory" in export_options and character.blueprint.backstory:
                export_data["backstory"] = character.blueprint.backstory
            if "Goals" in export_options and character.blueprint.goal:
                export_data["goal"] = character.blueprint.goal

    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)

    st.download_button(
        label="Download JSON",
        data=json_str,
        file_name=f"character_{character_id[:8]}.json",
        mime="application/json",
        use_container_width=False,
    )

    st.code(json_str, language="json")
