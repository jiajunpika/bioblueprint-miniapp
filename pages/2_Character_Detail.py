"""Character detail page with full blueprint display."""

import json
import streamlit as st
from config import DEFAULT_CHARACTER_ID, KNOWN_CHARACTERS, DEFAULT_BASE_URL, DEFAULT_API_KEY
from utils.client import get_client, is_connected, handle_api_error, init_client

st.set_page_config(page_title="Character Detail", page_icon="📋", layout="wide")

# Custom CSS for Profile View style
st.markdown("""
<style>
/* Profile Hero Section */
.profile-hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #333;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
}
.profile-hero-top {
    display: flex;
    gap: 20px;
    align-items: flex-start;
}
.profile-avatar {
    width: 80px;
    height: 80px;
    border-radius: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
}
.profile-name {
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;
    margin-bottom: 4px;
    color: white;
}
.profile-tagline {
    font-size: 14px;
    color: #888;
    margin-bottom: 8px;
}
.profile-meta {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    font-size: 13px;
    color: #888;
}
.profile-meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Quick Stats */
.profile-quick-stats {
    display: flex;
    gap: 12px;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #333;
    flex-wrap: wrap;
}
.quick-stat {
    background: #252540;
    border-radius: 8px;
    padding: 12px 16px;
    min-width: 80px;
    text-align: center;
}
.quick-stat-value {
    font-size: 18px;
    font-weight: 700;
    color: white;
}
.quick-stat-label {
    font-size: 11px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Profile Tags */
.profile-tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 12px;
}
.profile-tag {
    font-size: 11px;
    padding: 4px 10px;
    background: #252540;
    border: 1px solid #333;
    border-radius: 16px;
    color: #888;
}
.profile-tag.highlight {
    background: #667eea;
    border-color: #667eea;
    color: white;
}

/* Profile Card */
.profile-card {
    background: #1a1a2e;
    border: 1px solid #333;
    border-radius: 10px;
    margin-bottom: 16px;
    overflow: hidden;
}
.profile-card-header {
    padding: 14px 18px;
    border-bottom: 1px solid #333;
    background: #252540;
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
    color: white;
}
.profile-card-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}
.profile-card-icon.personality { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.profile-card-icon.career { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.profile-card-icon.expression { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.profile-card-icon.aesthetic { background: rgba(168, 85, 247, 0.2); color: #a855f7; }
.profile-card-icon.simulation { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.profile-card-icon.backstory { background: rgba(236, 72, 153, 0.2); color: #ec4899; }
.profile-card-icon.goal { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.profile-card-body {
    padding: 16px 18px;
}

/* Value Pills */
.value-pills {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
.value-pill {
    font-size: 12px;
    padding: 6px 12px;
    background: #252540;
    border-radius: 16px;
    color: #ccc;
}
.value-pill.highlight {
    background: #667eea;
    color: white;
}
.value-pill.negative {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

/* Attribute List */
.attr-item {
    margin-bottom: 12px;
}
.attr-label {
    font-size: 11px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}
.attr-value {
    font-size: 14px;
    color: #ddd;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

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


def render_pills(items: list, highlight_first: int = 0) -> str:
    """Render items as pill badges."""
    if not items:
        return ""
    pills = []
    for i, item in enumerate(items):
        cls = "value-pill highlight" if i < highlight_first else "value-pill"
        pills.append(f'<span class="{cls}">{item}</span>')
    return f'<div class="value-pills">{"".join(pills)}</div>'


def render_card(title: str, icon: str, color_class: str, content: str) -> str:
    """Render a profile card with header and body."""
    return f'''
    <div class="profile-card">
        <div class="profile-card-header">
            <div class="profile-card-icon {color_class}">{icon}</div>
            {title}
        </div>
        <div class="profile-card-body">
            {content}
        </div>
    </div>
    '''


def render_attr(label: str, value: str) -> str:
    """Render an attribute item."""
    return f'''
    <div class="attr-item">
        <div class="attr-label">{label}</div>
        <div class="attr-value">{value}</div>
    </div>
    '''


def format_value(value) -> str:
    """Format a value for HTML display."""
    if value is None:
        return ""
    if isinstance(value, list):
        if not value:
            return ""
        if isinstance(value[0], dict):
            # List of dicts - format as items
            items = []
            for item in value:
                parts = [f"{k}: {v}" for k, v in item.items() if v]
                items.append(" | ".join(parts))
            return "<br>".join(f"• {item}" for item in items)
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            if v:
                parts.append(f"<strong>{k}:</strong> {format_value(v)}")
        return "<br>".join(parts)
    return str(value)


def render_data_card(title: str, icon: str, color_class: str, data: dict) -> str:
    """Render a card with dict data formatted as attributes."""
    if not data:
        return ""
    attrs = []
    for key, value in data.items():
        if value:
            formatted = format_value(value)
            if formatted:
                attrs.append(render_attr(key, formatted))
    if not attrs:
        return ""
    return render_card(title, icon, color_class, "".join(attrs))


# ==================== HERO SECTION ====================
profile = character.profile
identity = profile.identity_card if profile else None
blueprint = character.blueprint
personality = blueprint.core_personality if blueprint else None

# Build hero data
name = profile.profile_name if profile else "Unknown"
initial = name[0].upper() if name else "?"
bio = identity.bio if identity else ""
location = identity.location if identity else ""
username = profile.username if profile else ""
relationship = identity.relationship if identity else ""

# Profile tags
tags = identity.profile_tags if identity and identity.profile_tags else []

# Quick stats
quick_stats = []
if identity:
    if identity.age:
        quick_stats.append(("Age", identity.age))
    if identity.occupation:
        quick_stats.append(("Role", identity.occupation))
if personality and isinstance(personality, dict):
    if personality.get("mbti"):
        quick_stats.append(("MBTI", personality.get("mbti")))
if identity and identity.zodiac:
    quick_stats.append(("Sign", identity.zodiac))

# Render Hero
hero_meta = ""
if location:
    hero_meta += f'<span class="profile-meta-item">📍 {location}</span>'
if username:
    hero_meta += f'<span class="profile-meta-item">@{username}</span>'
if relationship:
    hero_meta += f'<span class="profile-meta-item">💍 {relationship}</span>'

hero_tags = ""
if tags:
    highlight_tags = "".join([f'<span class="profile-tag highlight">{t}</span>' for t in tags[:3]])
    normal_tags = "".join([f'<span class="profile-tag">{t}</span>' for t in tags[3:8]])
    hero_tags = f'<div class="profile-tags">{highlight_tags}{normal_tags}</div>'

hero_stats = ""
if quick_stats:
    stats_html = "".join([f'<div class="quick-stat"><div class="quick-stat-value">{v}</div><div class="quick-stat-label">{l}</div></div>' for l, v in quick_stats])
    hero_stats = f'<div class="profile-quick-stats">{stats_html}</div>'

st.markdown(f'''
<div class="profile-hero">
    <div class="profile-hero-top">
        <div class="profile-avatar">{initial}</div>
        <div style="flex: 1;">
            <div class="profile-name">{name}</div>
            <div class="profile-tagline">{bio}</div>
            <div class="profile-meta">{hero_meta}</div>
            {hero_tags}
        </div>
    </div>
    {hero_stats}
</div>
''', unsafe_allow_html=True)

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
])

# Tab 1: Profile
with tabs[0]:
    col1, col2 = st.columns([1, 2])

    with col1:
        if character.profile.avatar:
            st.image(character.profile.avatar, use_container_width=True)

        # Social Stats Card
        stats_content = f'''
        <div style="display: flex; gap: 16px; margin-top: 16px;">
            <div class="quick-stat">
                <div class="quick-stat-value">{character.profile.followers_count or 0}</div>
                <div class="quick-stat-label">Followers</div>
            </div>
            <div class="quick-stat">
                <div class="quick-stat-value">{character.profile.following_count or 0}</div>
                <div class="quick-stat-label">Following</div>
            </div>
            <div class="quick-stat">
                <div class="quick-stat-value">{character.profile.posts_count or 0}</div>
                <div class="quick-stat-label">Posts</div>
            </div>
        </div>
        '''
        st.markdown(stats_content, unsafe_allow_html=True)

    with col2:
        # Handles Card
        if character.profile.handles:
            handles = character.profile.handles
            handles_content = ""
            for platform, handle in handles.items():
                if handle:
                    handles_content += render_attr(platform.capitalize(), handle)
            st.markdown(render_card("Social Media", "🔗", "expression", handles_content), unsafe_allow_html=True)

        # Voice
        if character.profile.voice_url:
            st.markdown(render_card("Voice Sample", "🎤", "aesthetic", ""), unsafe_allow_html=True)
            st.audio(character.profile.voice_url)

# Tab 2: Identity Card
with tabs[1]:
    card = character.profile.identity_card
    col1, col2 = st.columns(2)

    with col1:
        # Basic Info Card
        basic_content = ""
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
                basic_content += render_attr(label, str(value))
        st.markdown(render_card("Basic Info", "📝", "personality", basic_content), unsafe_allow_html=True)

    with col2:
        # Appearance Card
        appearance_content = ""
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
                appearance_content += render_attr(label, str(value))
        st.markdown(render_card("Appearance", "👁️", "aesthetic", appearance_content), unsafe_allow_html=True)

    # Interests Card
    if card.interests:
        interests_pills = render_pills(card.interests, highlight_first=3)
        st.markdown(render_card("Interests", "🎯", "simulation", interests_pills), unsafe_allow_html=True)

    # Tags Card
    if card.profile_tags:
        tags_pills = render_pills(card.profile_tags, highlight_first=3)
        st.markdown(render_card("Profile Tags", "🏷️", "career", tags_pills), unsafe_allow_html=True)

# Tab 3: Core Personality
with tabs[2]:
    if character.blueprint and character.blueprint.core_personality:
        cp = character.blueprint.core_personality

        # MBTI & Overview header
        if cp.get("mbti") or cp.get("overview"):
            overview_content = ""
            if cp.get("mbti"):
                overview_content += f'<span class="value-pill highlight">{cp.get("mbti")}</span>'
            if cp.get("overview"):
                overview_content += f'<div style="margin-top: 12px; color: #aaa; line-height: 1.6;">{cp.get("overview")}</div>'
            st.markdown(render_card("Overview", "🧠", "personality", overview_content), unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # Values
            if cp.get("values"):
                values_data = cp.get("values")
                if isinstance(values_data, dict):
                    content = ""
                    for k, v in values_data.items():
                        if v:
                            content += render_attr(k, format_value(v))
                    if content:
                        st.markdown(render_card("Values", "💎", "expression", content), unsafe_allow_html=True)
                elif isinstance(values_data, list):
                    st.markdown(render_card("Values", "💎", "expression", render_pills(values_data, highlight_first=3)), unsafe_allow_html=True)

            # Attributes
            if cp.get("attributes"):
                st.markdown(render_data_card("Attributes", "🎭", "personality", cp.get("attributes")), unsafe_allow_html=True)

            # Knowledge
            if cp.get("knowledge"):
                st.markdown(render_data_card("Knowledge", "📚", "simulation", cp.get("knowledge")), unsafe_allow_html=True)

            # Opinions
            if cp.get("opinions"):
                st.markdown(render_data_card("Opinions", "💭", "aesthetic", cp.get("opinions")), unsafe_allow_html=True)

            # Pet Peeves
            if cp.get("petPeeves"):
                peeves = cp.get("petPeeves")
                if isinstance(peeves, list):
                    st.markdown(render_card("Pet Peeves", "😤", "personality", render_pills(peeves)), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Pet Peeves", "😤", "personality", peeves), unsafe_allow_html=True)

            # Humor
            if cp.get("humor"):
                st.markdown(render_data_card("Humor", "😄", "expression", cp.get("humor")), unsafe_allow_html=True)

        with col2:
            # Attachment
            if cp.get("attachment"):
                st.markdown(render_data_card("Attachment", "💕", "personality", cp.get("attachment")), unsafe_allow_html=True)

            # Memories
            if cp.get("memories"):
                st.markdown(render_data_card("Memories", "🧠", "simulation", cp.get("memories")), unsafe_allow_html=True)

            # Fears & Desires
            if cp.get("fearsAndDesires"):
                st.markdown(render_data_card("Fears & Desires", "😰", "aesthetic", cp.get("fearsAndDesires")), unsafe_allow_html=True)

            # Passions & Hobbies
            if cp.get("passionsAndHobbies"):
                ph = cp.get("passionsAndHobbies")
                if isinstance(ph, dict):
                    hobbies = ph.get("hobbies", [])
                    interests = ph.get("interests", [])
                    content = ""
                    if hobbies:
                        content += f"<div style='margin-bottom: 8px;'><strong>Hobbies:</strong></div>{render_pills(hobbies, highlight_first=2)}"
                    if interests:
                        content += f"<div style='margin: 12px 0 8px;'><strong>Interests:</strong></div>{render_pills(interests)}"
                    if content:
                        st.markdown(render_card("Passions & Hobbies", "🎨", "expression", content), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Passions & Hobbies", "🎨", "expression", ph), unsafe_allow_html=True)

            # Taste
            if cp.get("taste"):
                st.markdown(render_data_card("Taste", "🍽️", "aesthetic", cp.get("taste")), unsafe_allow_html=True)

            # Habits
            if cp.get("habits"):
                habits = cp.get("habits")
                if isinstance(habits, list):
                    st.markdown(render_card("Habits", "📅", "simulation", render_pills(habits)), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Habits", "📅", "simulation", habits), unsafe_allow_html=True)

            # Rituals
            if cp.get("rituals"):
                rituals = cp.get("rituals")
                if isinstance(rituals, list):
                    st.markdown(render_card("Rituals", "🌅", "expression", render_pills(rituals)), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Rituals", "🌅", "expression", rituals), unsafe_allow_html=True)

        # Career Engine (embedded in corePersonality) - show preview
        if cp.get("careerEngine"):
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            ce = cp.get("careerEngine")
            identity = ce.get("identity", {})
            title = identity.get("title", "")
            niche = ", ".join(identity.get("industryNiche", [])[:3]) if identity.get("industryNiche") else ""
            career_preview = f"<strong>{title}</strong>" if title else ""
            if niche:
                career_preview += f"<br><span style='color: #888;'>{niche}</span>"
            career_preview += "<br><span style='color: #666; font-size: 12px;'>See Career Engine tab for details →</span>"
            st.markdown(render_card("Career Engine", "💼", "career", career_preview), unsafe_allow_html=True)
    else:
        st.info("No core personality data available")

# Tab 4: Career Engine (separate view)
with tabs[3]:
    if character.blueprint and character.blueprint.core_personality:
        cp = character.blueprint.core_personality
        ce = cp.get("careerEngine", {})

        if ce:
            # Identity card - hero style
            if ce.get("identity"):
                identity_data = ce.get("identity")
                title = identity_data.get("title", "")
                status = identity_data.get("currentStatus", "")
                dream = identity_data.get("dreamRole", "")
                niche = identity_data.get("industryNiche", [])

                id_content = ""
                if title:
                    id_content += f"<div style='font-size: 18px; font-weight: 600; color: #fff; margin-bottom: 8px;'>{title}</div>"
                if status:
                    id_content += render_attr("Status", status)
                if dream:
                    id_content += render_attr("Dream Role", dream)
                if niche:
                    id_content += f"<div style='margin-top: 12px;'>{render_pills(niche, highlight_first=2)}</div>"
                st.markdown(render_card("Professional Identity", "🏢", "career", id_content), unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                # Work Style
                if ce.get("workStyle"):
                    st.markdown(render_data_card("Work Style", "⚙️", "simulation", ce.get("workStyle")), unsafe_allow_html=True)

                # Capabilities
                if ce.get("capabilities"):
                    caps = ce.get("capabilities")
                    caps_content = ""
                    if caps.get("hardSkills"):
                        caps_content += f"<div style='margin-bottom: 8px;'><strong>Hard Skills</strong></div>{render_pills(caps.get('hardSkills'), highlight_first=3)}"
                    if caps.get("softSkills"):
                        caps_content += f"<div style='margin: 12px 0 8px;'><strong>Soft Skills</strong></div>{render_pills(caps.get('softSkills'))}"
                    if caps_content:
                        st.markdown(render_card("Capabilities", "💪", "expression", caps_content), unsafe_allow_html=True)

                # Technical Expertise
                if ce.get("technicalExpertise"):
                    st.markdown(render_data_card("Technical Expertise", "🔧", "aesthetic", ce.get("technicalExpertise")), unsafe_allow_html=True)

            with col2:
                # Achievements
                if ce.get("achievements"):
                    achievements = ce.get("achievements")
                    if isinstance(achievements, list):
                        ach_content = "<br>".join(f"• {a}" for a in achievements)
                        st.markdown(render_card("Achievements", "🏆", "career", ach_content), unsafe_allow_html=True)
                    else:
                        st.markdown(render_data_card("Achievements", "🏆", "career", achievements), unsafe_allow_html=True)

                # Psychology
                if ce.get("psychology"):
                    st.markdown(render_data_card("Psychology", "🧠", "personality", ce.get("psychology")), unsafe_allow_html=True)

                # Presentation
                if ce.get("presentation"):
                    st.markdown(render_data_card("Presentation", "📊", "simulation", ce.get("presentation")), unsafe_allow_html=True)

                # Professional Opinions
                if ce.get("professionalOpinions"):
                    st.markdown(render_data_card("Professional Opinions", "💬", "aesthetic", ce.get("professionalOpinions")), unsafe_allow_html=True)
        else:
            st.info("No career engine data available")
    else:
        st.info("No blueprint data available")

# Tab 5: Expression Engine
with tabs[4]:
    if character.blueprint and character.blueprint.expression_engine:
        ee = character.blueprint.expression_engine

        col1, col2 = st.columns(2)

        with col1:
            # Conversation Style
            if ee.get("conversationStyle"):
                st.markdown(render_data_card("Conversation Style", "🗣️", "expression", ee.get("conversationStyle")), unsafe_allow_html=True)

            # Voice Attributes
            if ee.get("voiceAttributes"):
                st.markdown(render_data_card("Voice Attributes", "🔊", "aesthetic", ee.get("voiceAttributes")), unsafe_allow_html=True)

            # Voice Style
            if ee.get("voiceStyle"):
                st.markdown(render_data_card("Voice Style", "🎙️", "personality", ee.get("voiceStyle")), unsafe_allow_html=True)

        with col2:
            # Typing Style
            if ee.get("typingStyle"):
                st.markdown(render_data_card("Typing Style", "⌨️", "simulation", ee.get("typingStyle")), unsafe_allow_html=True)

            # Interaction
            if ee.get("interaction"):
                st.markdown(render_data_card("Interaction", "🤝", "career", ee.get("interaction")), unsafe_allow_html=True)

            # Languages (if exists)
            if ee.get("languages"):
                langs = ee.get("languages")
                if isinstance(langs, list):
                    st.markdown(render_card("Languages", "🌐", "expression", render_pills(langs, highlight_first=1)), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Languages", "🌐", "expression", langs), unsafe_allow_html=True)
    else:
        st.info("No expression engine data available")

# Tab 6: Aesthetic Engine
with tabs[5]:
    if character.blueprint and character.blueprint.aesthetic_engine:
        ae = character.blueprint.aesthetic_engine

        col1, col2 = st.columns(2)

        with col1:
            # Essence
            if ae.get("essence"):
                essence = ae.get("essence")
                if isinstance(essence, dict):
                    vibe = essence.get("vibe", "")
                    aesthetic = essence.get("aesthetic", [])
                    content = ""
                    if vibe:
                        content += f"<div style='font-size: 16px; color: #fff; margin-bottom: 12px;'>{vibe}</div>"
                    if aesthetic:
                        content += render_pills(aesthetic if isinstance(aesthetic, list) else [aesthetic], highlight_first=2)
                    for k, v in essence.items():
                        if k not in ["vibe", "aesthetic"] and v:
                            content += render_attr(k, format_value(v))
                    if content:
                        st.markdown(render_card("Essence", "✨", "aesthetic", content), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Essence", "✨", "aesthetic", essence), unsafe_allow_html=True)

            # Appearance
            if ae.get("appearance"):
                st.markdown(render_data_card("Appearance", "👤", "personality", ae.get("appearance")), unsafe_allow_html=True)

            # Fashion DNA
            if ae.get("fashionDNA"):
                st.markdown(render_data_card("Fashion DNA", "👔", "career", ae.get("fashionDNA")), unsafe_allow_html=True)

            # Color Palette
            if ae.get("colorPalette"):
                palette = ae.get("colorPalette")
                if isinstance(palette, list):
                    st.markdown(render_card("Color Palette", "🎨", "expression", render_pills(palette)), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Color Palette", "🎨", "expression", palette), unsafe_allow_html=True)

        with col2:
            # Visual Language
            if ae.get("visualLanguage"):
                st.markdown(render_data_card("Visual Language", "📸", "simulation", ae.get("visualLanguage")), unsafe_allow_html=True)

            # Signature Shots
            if ae.get("signatureShots"):
                shots = ae.get("signatureShots")
                if isinstance(shots, list):
                    shots_content = "<br>".join(f"• {s}" for s in shots)
                    st.markdown(render_card("Signature Shots", "📷", "aesthetic", shots_content), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Signature Shots", "📷", "aesthetic", shots), unsafe_allow_html=True)

            # Energy
            if ae.get("energy"):
                st.markdown(render_data_card("Energy", "⚡", "personality", ae.get("energy")), unsafe_allow_html=True)

            # World
            if ae.get("world"):
                st.markdown(render_data_card("World", "🌍", "career", ae.get("world")), unsafe_allow_html=True)
    else:
        st.info("No aesthetic engine data available")

# Tab 7: Simulation
with tabs[6]:
    if character.blueprint and character.blueprint.simulation:
        sim = character.blueprint.simulation

        # Circadian card - special layout
        if sim.get("circadian"):
            circ = sim.get("circadian")
            circ_content = ""
            if circ.get("chronotype"):
                circ_content += f"<div style='font-size: 18px; font-weight: 600; color: #fff; margin-bottom: 12px;'>{circ.get('chronotype')}</div>"
            times = []
            if circ.get("wakeTime"):
                times.append(f"🌅 Wake: {circ.get('wakeTime')}")
            if circ.get("sleepTime"):
                times.append(f"🌙 Sleep: {circ.get('sleepTime')}")
            if times:
                circ_content += f"<div style='color: #aaa; margin-bottom: 8px;'>{' | '.join(times)}</div>"
            if circ.get("peakHours"):
                circ_content += f"<div style='margin-top: 8px;'>{render_pills(circ.get('peakHours'))}</div>"
            st.markdown(render_card("Circadian Rhythm", "⏰", "simulation", circ_content), unsafe_allow_html=True)

        # Household
        if sim.get("household"):
            st.markdown(render_data_card("Household", "🏠", "career", sim.get("household")), unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # Weekday
            if sim.get("weekday"):
                st.markdown(render_data_card("Weekday", "📅", "personality", sim.get("weekday")), unsafe_allow_html=True)

            # Weekend
            if sim.get("weekend"):
                st.markdown(render_data_card("Weekend", "🌴", "aesthetic", sim.get("weekend")), unsafe_allow_html=True)

            # Lifestyle Rhythm
            if sim.get("lifestyleRhythm"):
                st.markdown(render_data_card("Lifestyle Rhythm", "🎵", "expression", sim.get("lifestyleRhythm")), unsafe_allow_html=True)

            # Consumption
            if sim.get("consumption"):
                st.markdown(render_data_card("Consumption", "🛒", "career", sim.get("consumption")), unsafe_allow_html=True)

            # Food Preferences
            if sim.get("foodPreferences"):
                st.markdown(render_data_card("Food Preferences", "🍽️", "aesthetic", sim.get("foodPreferences")), unsafe_allow_html=True)

            # Video Games
            if sim.get("videoGames"):
                st.markdown(render_data_card("Video Games", "🎮", "expression", sim.get("videoGames")), unsafe_allow_html=True)

        with col2:
            # Activities
            if sim.get("activities"):
                st.markdown(render_data_card("Activities", "🎯", "simulation", sim.get("activities")), unsafe_allow_html=True)

            # Social Scene
            if sim.get("socialScene"):
                st.markdown(render_data_card("Social Scene", "👥", "personality", sim.get("socialScene")), unsafe_allow_html=True)

            # Locations
            if sim.get("locations"):
                locs = sim.get("locations")
                if isinstance(locs, list):
                    locs_content = "<br>".join(f"📍 {loc}" for loc in locs)
                    st.markdown(render_card("Locations", "📍", "career", locs_content), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Locations", "📍", "career", locs), unsafe_allow_html=True)

            # Relationships
            if sim.get("relationships"):
                st.markdown(render_data_card("Relationships", "💑", "personality", sim.get("relationships")), unsafe_allow_html=True)

            # Social Tendencies
            if sim.get("socialTendencies"):
                st.markdown(render_data_card("Social Tendencies", "🤝", "expression", sim.get("socialTendencies")), unsafe_allow_html=True)

            # Current State
            if sim.get("currentState"):
                st.markdown(render_data_card("Current State", "📍", "simulation", sim.get("currentState")), unsafe_allow_html=True)

        # Hobbies - full width
        if sim.get("hobbies"):
            st.markdown(render_card("Hobbies", "🎮", "aesthetic", render_pills(sim.get("hobbies"), highlight_first=3)), unsafe_allow_html=True)

        # Recurring Events
        if sim.get("recurringEvents"):
            events = sim.get("recurringEvents")
            if isinstance(events, list):
                events_content = "<br>".join(f"📆 {e}" for e in events)
                st.markdown(render_card("Recurring Events", "📆", "simulation", events_content), unsafe_allow_html=True)
            else:
                st.markdown(render_data_card("Recurring Events", "📆", "simulation", events), unsafe_allow_html=True)

        # Travel Plans
        if sim.get("travelPlans"):
            st.markdown(render_data_card("Travel Plans", "✈️", "career", sim.get("travelPlans")), unsafe_allow_html=True)
    else:
        st.info("No simulation data available")

# Tab 8: Backstory
with tabs[7]:
    if character.blueprint and character.blueprint.backstory:
        bs = character.blueprint.backstory

        # Origin card - hero style
        if bs.get("origin"):
            origin_content = f"<div style='color: #ddd; line-height: 1.6;'>{bs.get('origin')}</div>"
            st.markdown(render_card("Origin", "🌍", "simulation", origin_content), unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # Family
            if bs.get("family"):
                family_content = f"<div style='color: #ddd; line-height: 1.6;'>{bs.get('family')}</div>"
                st.markdown(render_card("Family", "👨‍👩‍👧", "personality", family_content), unsafe_allow_html=True)

            # Education
            if bs.get("education"):
                edu = bs.get("education")
                if isinstance(edu, dict):
                    st.markdown(render_data_card("Education", "🎓", "career", edu), unsafe_allow_html=True)
                elif isinstance(edu, list):
                    edu_content = "<br>".join(f"🎓 {e}" for e in edu)
                    st.markdown(render_card("Education", "🎓", "career", edu_content), unsafe_allow_html=True)
                else:
                    st.markdown(render_card("Education", "🎓", "career", f"<div style='color: #ddd;'>{edu}</div>"), unsafe_allow_html=True)

            # Life Events
            if bs.get("lifeEvents"):
                events = bs.get("lifeEvents")
                if isinstance(events, list):
                    events_content = "<br>".join(f"📅 {format_value(e)}" for e in events)
                    st.markdown(render_card("Life Events", "📅", "aesthetic", events_content), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Life Events", "📅", "aesthetic", events), unsafe_allow_html=True)

            # Core Wounds
            if bs.get("coreWounds"):
                wounds = bs.get("coreWounds")
                if isinstance(wounds, list):
                    wounds_content = "<br>".join(f"💔 {w}" for w in wounds)
                    st.markdown(render_card("Core Wounds", "💔", "personality", wounds_content), unsafe_allow_html=True)

        with col2:
            # Pets
            if bs.get("pets"):
                pets_content = f"<div style='color: #ddd; line-height: 1.6;'>{bs.get('pets')}</div>"
                st.markdown(render_card("Pets", "🐱", "expression", pets_content), unsafe_allow_html=True)

            # Formative Relationships
            if bs.get("formativeRelationships"):
                rels = bs.get("formativeRelationships")
                if isinstance(rels, list):
                    rels_content = "<br>".join(f"💕 {format_value(r)}" for r in rels)
                    st.markdown(render_card("Formative Relationships", "💕", "simulation", rels_content), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Formative Relationships", "💕", "simulation", rels), unsafe_allow_html=True)

            # Core Joys
            if bs.get("coreJoys"):
                joys = bs.get("coreJoys")
                if isinstance(joys, list):
                    joys_content = "<br>".join(f"💖 {j}" for j in joys)
                    st.markdown(render_card("Core Joys", "💖", "expression", joys_content), unsafe_allow_html=True)
    else:
        st.info("No backstory data available")

# Tab 9: Goals
with tabs[8]:
    if character.blueprint and character.blueprint.goal:
        goal = character.blueprint.goal

        col1, col2 = st.columns(2)

        with col1:
            # Long Term Aspirations
            if goal.get("longTermAspirations"):
                aspirations = goal.get("longTermAspirations")
                if isinstance(aspirations, list):
                    asp_content = "<br>".join(f"🌟 {a}" for a in aspirations)
                    st.markdown(render_card("Long Term Aspirations", "🌟", "career", asp_content), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Long Term Aspirations", "🌟", "career", aspirations), unsafe_allow_html=True)

        with col2:
            # Short Term Queue
            if goal.get("shortTermQueue"):
                queue = goal.get("shortTermQueue")
                if isinstance(queue, list):
                    queue_items = []
                    for item in queue:
                        if isinstance(item, dict):
                            priority = item.get("priority", "")
                            task = item.get("task", "")
                            status = item.get("status", "pending")
                            status_icon = "✅" if status == "completed" else "⏳" if status == "in_progress" else "📝"
                            p_badge = f"<span class='value-pill highlight'>P{priority}</span>" if priority else ""
                            queue_items.append(f"{status_icon} {p_badge} {task}")
                        else:
                            queue_items.append(f"📋 {item}")
                    queue_content = "<br>".join(queue_items)
                    st.markdown(render_card("Short Term Queue", "📋", "simulation", queue_content), unsafe_allow_html=True)
                else:
                    st.markdown(render_data_card("Short Term Queue", "📋", "simulation", queue), unsafe_allow_html=True)
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
