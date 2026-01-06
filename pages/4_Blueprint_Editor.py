"""Blueprint state editor page."""

import json
import streamlit as st
from utils.client import get_client, is_connected, handle_api_error

st.set_page_config(page_title="Blueprint Editor", page_icon="✏️", layout="wide")

st.title("✏️ Blueprint Editor")

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
    st.info("Enter a character ID above to edit blueprint")
    st.stop()

# Fetch current blueprint
with st.spinner("Loading current blueprint..."):
    try:
        character = client.character.get_blueprint(character_id)
    except Exception as e:
        st.error(handle_api_error(e))
        st.stop()

st.success(f"Editing: {character.profile.profile_name}")

# Blueprint fields
BLUEPRINT_FIELDS = [
    "core_personality",
    "expression_engine",
    "aesthetic_engine",
    "simulation",
    "goal",
    "backstory",
    "onboarding_input",
    "prototype",
]

# Select field to edit
selected_field = st.selectbox(
    "Select field to edit",
    options=BLUEPRINT_FIELDS,
    format_func=lambda x: x.replace("_", " ").title(),
)

# Get current value
current_value = None
if character.blueprint:
    current_value = getattr(character.blueprint, selected_field, None)

# Display current value
st.subheader("Current Value")
if current_value:
    st.json(current_value)
else:
    st.info("This field is currently empty")

# Editor
st.subheader("Edit Value")

st.markdown("""
**Tips:**
- Enter valid JSON object
- Use shallow merge: new keys are added, existing keys are overwritten
- Set a key to `null` to delete it
""")

# JSON editor
default_json = json.dumps(current_value or {}, indent=2, ensure_ascii=False)
new_value_str = st.text_area(
    "JSON Editor",
    value=default_json,
    height=300,
    help="Enter valid JSON",
)

# Validate and submit
col1, col2 = st.columns(2)

with col1:
    if st.button("Validate JSON"):
        try:
            parsed = json.loads(new_value_str)
            st.success("Valid JSON!")
            st.json(parsed)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")

with col2:
    if st.button("Update Blueprint", type="primary"):
        try:
            parsed = json.loads(new_value_str)

            # Build update payload
            update_data = {selected_field: parsed}

            with st.spinner("Updating..."):
                updated = client.character.upsert_blueprint_state(
                    character_id,
                    update_data,
                )

            st.success("Blueprint updated successfully!")

            # Show updated value
            st.subheader("Updated Value")
            new_val = getattr(updated.blueprint, selected_field, None)
            if new_val:
                st.json(new_val)

        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
        except Exception as e:
            st.error(handle_api_error(e))

# History section
st.divider()
st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Clear Field", help="Set field to empty object"):
        try:
            with st.spinner("Clearing..."):
                client.character.upsert_blueprint_state(
                    character_id,
                    {selected_field: {}},
                )
            st.success("Field cleared!")
            st.rerun()
        except Exception as e:
            st.error(handle_api_error(e))

with col2:
    if st.button("Refresh", help="Reload current value"):
        st.rerun()

with col3:
    if st.button("View Full Blueprint"):
        if character.blueprint:
            st.json(character.blueprint.model_dump(mode="json"))
        else:
            st.info("No blueprint data")
