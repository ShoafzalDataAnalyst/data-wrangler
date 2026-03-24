import streamlit as st

st.set_page_config(
    page_title="Data Wrangler & Visualizer",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session():
    defaults = {
        "df_original":   None,
        "df_working":    None,
        "transform_log": [],
        "file_name":     None,
        "ai_enabled":    False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

st.sidebar.title("🧹 Data Wrangler")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "📁  Upload & Overview",
        "🧽  Cleaning Studio",
        "📊  Visualization Builder",
        "💾  Export & Report",
        "🤖  AI Assistant",
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.session_state["ai_enabled"] = st.sidebar.toggle(
    "🤖 Enable AI Assistant",
    value=st.session_state["ai_enabled"],
    help="Uses Claude API to suggest cleaning steps and chart ideas."
)
if st.session_state["ai_enabled"]:
    st.sidebar.caption("⚠️ AI outputs may be imperfect — always verify.")

st.sidebar.markdown("---")
st.sidebar.caption("Data Wrangling & Visualization · 5COSC038C")

if page == "📁  Upload & Overview":
    from sections.page_a_upload import show
    show()
elif page == "🧽  Cleaning Studio":
    from sections.page_b_cleaning import show
    show()
elif page == "📊  Visualization Builder":
    from sections.page_c_viz import show
    show()
elif page == "💾  Export & Report":
    from sections.page_d_export import show
    show()
elif page == "🤖  AI Assistant":
    from sections.page_e_ai import show
    show()
