"""Character detail page with full blueprint display."""

import json
import streamlit as st
from config import DEFAULT_CHARACTER_ID, KNOWN_CHARACTERS, DEFAULT_BASE_URL, DEFAULT_API_KEY
from utils.client import get_client, is_connected, handle_api_error, init_client

st.set_page_config(page_title="Character Detail", page_icon="📋", layout="wide")

st.title("📋 Character Detail")

# Get UUID from URL query params (e.g., ?uuid=xxx)
url_uuid = st.query_params.get("uuid", None)

# Auto-connect if not connected but env vars are set
if not is_connected() and DEFAULT_API_KEY:
    with st.spinner("Auto-connecting to API..."):
        init_client(DEFAULT_BASE_URL, DEFAULT_API_KEY)

if not is_connected():
    st.warning("Please connect to API first (go to main page)")
    st.stop()

client = get_client()

# Determine initial character ID (URL param takes priority)
initial_character_id = url_uuid or st.session_state.get("selected_character_id", DEFAULT_CHARACTER_ID)

# Character selection
col1, col2 = st.columns([2, 1])

with col1:
    # Quick select from known characters
    character_options = ["-- Custom ID --"] + [f"{c['name']} ({c['id'][:8]}...)" for c in KNOWN_CHARACTERS]

    # Find if URL uuid matches a known character
    default_index = 0
    if url_uuid:
        for i, c in enumerate(KNOWN_CHARACTERS):
            if c["id"] == url_uuid:
                default_index = i + 1
                break

    selected_option = st.selectbox("Quick Select", character_options, index=default_index)

with col2:
    # Manual input
    if selected_option == "-- Custom ID --":
        character_id = st.text_input(
            "Character ID",
            value=initial_character_id,
            placeholder="Enter character UUID",
        )
    else:
        # Find the selected character
        idx = character_options.index(selected_option) - 1
        character_id = KNOWN_CHARACTERS[idx]["id"]
        st.text_input("Character ID", value=character_id, disabled=True)

if not character_id:
    st.info("Select a character or enter a character ID to view details")
    st.stop()

# Fetch character data
with st.spinner("Loading character..."):
    try:
        character = client.character.get_blueprint(character_id)
    except Exception as e:
        st.error(handle_api_error(e))
        st.stop()


def render_dict_as_table(data: dict, title: str = None):
    """Render a dict as formatted display."""
    if title:
        st.markdown(f"**{title}**")
    for key, value in data.items():
        if isinstance(value, list):
            st.markdown(f"**{key}:** {', '.join(str(v) for v in value)}")
        elif isinstance(value, dict):
            st.markdown(f"**{key}:**")
            for k, v in value.items():
                st.markdown(f"  - {k}: {v}")
        else:
            st.markdown(f"**{key}:** {value}")


def render_json_expander(data: dict, title: str, expanded: bool = False):
    """Render data in an expander with JSON view."""
    if data:
        with st.expander(title, expanded=expanded):
            st.json(data)


def render_list_items(items: list, title: str):
    """Render a list as bullet points."""
    if items:
        st.markdown(f"**{title}:**")
        for item in items:
            if isinstance(item, dict):
                st.json(item)
            else:
                st.markdown(f"- {item}")


# Main tabs for different sections
tabs = st.tabs([
    "👤 Profile",
    "🪪 Identity Card",
    "🧠 Core Personality",
    "💼 Career Engine",
    "💬 Expression Engine",
    "🎨 Aesthetic Engine",
    "🏠 Simulation",
    "📖 Backstory",
    "🎯 Goals",
    "📷 Album",
    "📤 JSON Export"
])

# Tab 1: Profile
with tabs[0]:
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

        # Handles
        if character.profile.handles:
            st.markdown("#### Social Media")
            handles = character.profile.handles
            for platform, handle in handles.items():
                if handle:
                    st.markdown(f"**{platform}:** {handle}")

# Tab 2: Identity Card
with tabs[1]:
    card = character.profile.identity_card

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📝 Basic Info")
        info_items = [
            ("Gender", card.gender),
            ("Age", card.age),
            ("Occupation", card.occupation),
            ("Location", card.location),
            ("Zodiac", card.zodiac),
            ("Relationship", card.relationship),
            ("Title", card.title),
        ]
        for label, value in info_items:
            if value:
                st.markdown(f"**{label}:** {value}")

    with col2:
        st.markdown("#### 👁️ Appearance")
        appearance_items = [
            ("Phenotype", card.phenotype),
            ("Hair", card.hair),
            ("Hair Style", card.hair_style),
            ("Eyes", card.ocular_scan),
            ("Style", card.style),
            ("Style Image", card.style_image),
        ]
        for label, value in appearance_items:
            if value:
                st.markdown(f"**{label}:** {value}")

    if card.interests:
        st.markdown("#### 🎯 Interests")
        st.markdown(" ".join([f"`{i}`" for i in card.interests]))

    if card.profile_tags:
        st.markdown("#### 🏷️ Tags")
        st.markdown(" ".join([f"`{t}`" for t in card.profile_tags]))

# Tab 3: Core Personality
with tabs[2]:
    if character.blueprint and character.blueprint.core_personality:
        cp = character.blueprint.core_personality

        st.markdown("### 🧠 Core Personality")

        # MBTI & Overview
        if cp.get("mbti"):
            st.markdown(f"**MBTI:** `{cp.get('mbti')}`")
        if cp.get("overview"):
            st.info(cp.get("overview"))

        col1, col2 = st.columns(2)

        with col1:
            render_json_expander(cp.get("attributes"), "🎭 Attributes (性格特征)")
            render_json_expander(cp.get("values"), "💎 Values (价值观)")
            render_json_expander(cp.get("knowledge"), "📚 Knowledge (知识领域)")
            render_json_expander(cp.get("opinions"), "💭 Opinions (观点)")
            render_json_expander(cp.get("petPeeves"), "😤 Pet Peeves (烦恼)")
            render_json_expander(cp.get("humor"), "😄 Humor (幽默风格)")

        with col2:
            render_json_expander(cp.get("attachment"), "💕 Attachment (依恋风格)")
            render_json_expander(cp.get("memories"), "🧠 Memories (记忆)")
            render_json_expander(cp.get("fearsAndDesires"), "😰 Fears & Desires (恐惧与渴望)")
            render_json_expander(cp.get("passionsAndHobbies"), "🎨 Passions & Hobbies (热情与爱好)")
            render_json_expander(cp.get("taste"), "🍽️ Taste (口味偏好)")
            render_json_expander(cp.get("habits"), "📅 Habits (习惯)")
            render_json_expander(cp.get("rituals"), "🌅 Rituals (日常仪式)")

        # Career Engine (embedded in corePersonality)
        if cp.get("careerEngine"):
            st.divider()
            st.markdown("### 💼 Career Engine (嵌入)")
            ce = cp.get("careerEngine")
            col1, col2 = st.columns(2)
            with col1:
                render_json_expander(ce.get("identity"), "🏢 Identity (职业身份)")
                render_json_expander(ce.get("workStyle"), "⚙️ Work Style (工作风格)")
                render_json_expander(ce.get("psychology"), "🧠 Psychology (职业心理)")
                render_json_expander(ce.get("capabilities"), "💪 Capabilities (能力)")
            with col2:
                render_json_expander(ce.get("presentation"), "📊 Presentation (职业展示)")
                render_json_expander(ce.get("professionalOpinions"), "💬 Professional Opinions (职业观点)")
                render_json_expander(ce.get("achievements"), "🏆 Achievements (成就)")
                render_json_expander(ce.get("technicalExpertise"), "🔧 Technical Expertise (技术专长)")
    else:
        st.info("No core personality data available")

# Tab 4: Career Engine (separate view)
with tabs[3]:
    if character.blueprint and character.blueprint.core_personality:
        cp = character.blueprint.core_personality
        ce = cp.get("careerEngine", {})

        if ce:
            st.markdown("### 💼 Career Engine")

            # Identity
            if ce.get("identity"):
                st.markdown("#### 🏢 职业身份")
                identity = ce.get("identity")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Title:** {identity.get('title', 'N/A')}")
                    st.markdown(f"**Current Status:** {identity.get('currentStatus', 'N/A')}")
                    st.markdown(f"**Dream Role:** {identity.get('dreamRole', 'N/A')}")
                with col2:
                    if identity.get("industryNiche"):
                        st.markdown("**Industry Niche:**")
                        for niche in identity.get("industryNiche", []):
                            st.markdown(f"- {niche}")

            # Work Style
            render_json_expander(ce.get("workStyle"), "⚙️ Work Style (工作风格)", expanded=True)

            # Capabilities
            if ce.get("capabilities"):
                st.markdown("#### 💪 Capabilities")
                caps = ce.get("capabilities")
                col1, col2 = st.columns(2)
                with col1:
                    if caps.get("hardSkills"):
                        st.markdown("**Hard Skills:**")
                        st.markdown(" ".join([f"`{s}`" for s in caps.get("hardSkills", [])]))
                with col2:
                    if caps.get("softSkills"):
                        st.markdown("**Soft Skills:**")
                        st.markdown(" ".join([f"`{s}`" for s in caps.get("softSkills", [])]))

            # Technical Expertise
            render_json_expander(ce.get("technicalExpertise"), "🔧 Technical Expertise (技术专长)")

            # Achievements
            render_json_expander(ce.get("achievements"), "🏆 Achievements (成就)")

            # Psychology
            render_json_expander(ce.get("psychology"), "🧠 Psychology (职业心理)")
        else:
            st.info("No career engine data available")
    else:
        st.info("No blueprint data available")

# Tab 5: Expression Engine
with tabs[4]:
    if character.blueprint and character.blueprint.expression_engine:
        ee = character.blueprint.expression_engine

        st.markdown("### 💬 Expression Engine")

        col1, col2 = st.columns(2)

        with col1:
            render_json_expander(ee.get("conversationStyle"), "🗣️ Conversation Style (对话风格)", expanded=True)
            render_json_expander(ee.get("voiceAttributes"), "🔊 Voice Attributes (语音特征)")
            render_json_expander(ee.get("voiceStyle"), "🎙️ Voice Style (声音风格)")

        with col2:
            render_json_expander(ee.get("typingStyle"), "⌨️ Typing Style (打字风格)", expanded=True)
            render_json_expander(ee.get("interaction"), "🤝 Interaction (互动方式)")
    else:
        st.info("No expression engine data available")

# Tab 6: Aesthetic Engine
with tabs[5]:
    if character.blueprint and character.blueprint.aesthetic_engine:
        ae = character.blueprint.aesthetic_engine

        st.markdown("### 🎨 Aesthetic Engine")

        col1, col2 = st.columns(2)

        with col1:
            render_json_expander(ae.get("essence"), "✨ Essence (本质)", expanded=True)
            render_json_expander(ae.get("appearance"), "👤 Appearance (外观)")
            render_json_expander(ae.get("fashionDNA"), "👔 Fashion DNA (时尚DNA)")
            render_json_expander(ae.get("colorPalette"), "🎨 Color Palette (配色)")

        with col2:
            render_json_expander(ae.get("visualLanguage"), "📸 Visual Language (视觉语言)")
            render_json_expander(ae.get("signatureShots"), "📷 Signature Shots (标志性照片)")
            render_json_expander(ae.get("energy"), "⚡ Energy (能量表达)")
            render_json_expander(ae.get("world"), "🌍 World (世界设定)", expanded=True)
    else:
        st.info("No aesthetic engine data available")

# Tab 7: Simulation
with tabs[6]:
    if character.blueprint and character.blueprint.simulation:
        sim = character.blueprint.simulation

        st.markdown("### 🏠 Simulation")

        # Circadian
        if sim.get("circadian"):
            st.markdown("#### ⏰ Circadian (生物钟)")
            circ = sim.get("circadian")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Chronotype", circ.get("chronotype", "N/A"))
            with col2:
                st.metric("Wake Time", circ.get("wakeTime", "N/A"))
            with col3:
                st.metric("Sleep Time", circ.get("sleepTime", "N/A"))
            if circ.get("peakHours"):
                st.markdown(f"**Peak Hours:** {', '.join(circ.get('peakHours', []))}")

        # Household
        render_json_expander(sim.get("household"), "🏠 Household (家庭)", expanded=True)

        col1, col2 = st.columns(2)

        with col1:
            render_json_expander(sim.get("weekday"), "📅 Weekday (工作日)")
            render_json_expander(sim.get("weekend"), "🌴 Weekend (周末)")
            render_json_expander(sim.get("lifestyleRhythm"), "🎵 Lifestyle Rhythm (生活节奏)")
            render_json_expander(sim.get("consumption"), "🛒 Consumption (消费习惯)")
            render_json_expander(sim.get("foodPreferences"), "🍽️ Food Preferences (食物偏好)")

        with col2:
            render_json_expander(sim.get("activities"), "🎯 Activities (活动)")
            render_json_expander(sim.get("socialScene"), "👥 Social Scene (社交场景)")
            render_json_expander(sim.get("locations"), "📍 Locations (常去地点)")
            render_json_expander(sim.get("relationships"), "💑 Relationships (人际关系)")
            render_json_expander(sim.get("socialTendencies"), "🤝 Social Tendencies (社交倾向)")

        # Hobbies
        if sim.get("hobbies"):
            st.markdown("#### 🎮 Hobbies")
            st.markdown(" ".join([f"`{h}`" for h in sim.get("hobbies", [])]))

        # Video Games
        render_json_expander(sim.get("videoGames"), "🎮 Video Games (游戏偏好)")

        # Recurring Events
        render_json_expander(sim.get("recurringEvents"), "📆 Recurring Events (定期活动)")

        # Travel Plans
        render_json_expander(sim.get("travelPlans"), "✈️ Travel Plans (旅行计划)")

        # Current State
        render_json_expander(sim.get("currentState"), "📍 Current State (当前状态)")
    else:
        st.info("No simulation data available")

# Tab 8: Backstory
with tabs[7]:
    if character.blueprint and character.blueprint.backstory:
        bs = character.blueprint.backstory

        st.markdown("### 📖 Backstory")

        # Simple string fields
        if bs.get("origin"):
            st.markdown("#### 🌍 Origin (出身)")
            st.info(bs.get("origin"))

        if bs.get("family"):
            st.markdown("#### 👨‍👩‍👧 Family (家庭)")
            st.info(bs.get("family"))

        if bs.get("pets"):
            st.markdown("#### 🐱 Pets (宠物)")
            st.info(bs.get("pets"))

        # Education
        render_json_expander(bs.get("education"), "🎓 Education (教育经历)", expanded=True)

        # Life Events
        render_json_expander(bs.get("lifeEvents"), "📅 Life Events (人生事件)")

        # Formative Relationships
        render_json_expander(bs.get("formativeRelationships"), "💕 Formative Relationships (重要关系)")

        col1, col2 = st.columns(2)
        with col1:
            # Core Wounds
            if bs.get("coreWounds"):
                st.markdown("#### 💔 Core Wounds (核心创伤)")
                for wound in bs.get("coreWounds", []):
                    st.markdown(f"- {wound}")

        with col2:
            # Core Joys
            if bs.get("coreJoys"):
                st.markdown("#### 💖 Core Joys (核心快乐)")
                for joy in bs.get("coreJoys", []):
                    st.markdown(f"- {joy}")
    else:
        st.info("No backstory data available")

# Tab 9: Goals
with tabs[8]:
    if character.blueprint and character.blueprint.goal:
        goal = character.blueprint.goal

        st.markdown("### 🎯 Goals")

        # Long Term Aspirations
        if goal.get("longTermAspirations"):
            st.markdown("#### 🌟 Long Term Aspirations (长期愿景)")
            for aspiration in goal.get("longTermAspirations", []):
                st.markdown(f"- {aspiration}")

        # Short Term Queue
        if goal.get("shortTermQueue"):
            st.markdown("#### 📋 Short Term Queue (短期目标)")
            for item in goal.get("shortTermQueue", []):
                if isinstance(item, dict):
                    priority = item.get("priority", "N/A")
                    task = item.get("task", "N/A")
                    status = item.get("status", "pending")
                    status_icon = "✅" if status == "completed" else "⏳" if status == "in_progress" else "📝"
                    st.markdown(f"{status_icon} **[P{priority}]** {task}")
                else:
                    st.markdown(f"- {item}")
    else:
        st.info("No goal data available")

# Tab 10: Album
with tabs[9]:
    st.markdown("#### 📷 Album Preview")

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

# Tab 11: JSON Export
with tabs[10]:
    st.markdown("#### 📤 Export as JSON")

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

    if st.button("Generate JSON", type="primary"):
        export_data = {}

        if "Full Character" in export_options:
            export_data = character.model_dump(mode="json")
        else:
            if "Profile Only" in export_options:
                export_data["profile"] = character.profile.model_dump(mode="json")
            if "Identity Card Only" in export_options:
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

        st.code(json_str, language="json")

        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"character_{character_id[:8]}.json",
            mime="application/json",
        )
