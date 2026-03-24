import streamlit as st
import pandas as pd
import json
import os

def show():
    st.title("🤖 AI Assistant")

    if not st.session_state.get("ai_enabled"):
        st.info("Enable the **AI Assistant** toggle in the sidebar to use this feature.")
        return

    if st.session_state.get("df_working") is None:
        st.warning("⚠️ Upload a dataset first.")
        return

    df = st.session_state["df_working"]

    st.markdown(
        "Ask the AI to suggest cleaning steps, chart ideas, or explain your data. "
        "⚠️ *Outputs may be imperfect — always verify before applying.*"
    )
    st.markdown("---")

    # ── API Key input ─────────────────────────────────────────────────────────
    # Priority: session input > secrets.toml > env var
    if "anthropic_api_key" not in st.session_state:
        st.session_state["anthropic_api_key"] = ""

    # Try to auto-load from secrets or env
    if not st.session_state["anthropic_api_key"]:
        try:
            st.session_state["anthropic_api_key"] = st.secrets["ANTHROPIC_API_KEY"]
        except Exception:
            pass
    if not st.session_state["anthropic_api_key"]:
        st.session_state["anthropic_api_key"] = os.environ.get("ANTHROPIC_API_KEY", "")

    # Show key input only if not loaded automatically
    if not st.session_state["anthropic_api_key"]:
        with st.expander("🔑 Enter Anthropic API Key", expanded=True):
            st.caption(
                "Get your key from [console.anthropic.com](https://console.anthropic.com). "
                "The key is only stored in your browser session — not saved anywhere."
            )
            key_input = st.text_input(
                "API Key", type="password",
                placeholder="sk-ant-...",
                key="api_key_input"
            )
            if st.button("Save Key", key="save_key"):
                if key_input.startswith("sk-"):
                    st.session_state["anthropic_api_key"] = key_input
                    st.success("✅ Key saved for this session!")
                    st.rerun()
                else:
                    st.error("Key should start with 'sk-ant-...'")
        st.stop()
    else:
        with st.expander("🔑 API Key", expanded=False):
            st.success("✅ API key loaded.")
            if st.button("Clear Key", key="clear_key"):
                st.session_state["anthropic_api_key"] = ""
                st.rerun()

    st.markdown("---")

    # ── Mode selector ─────────────────────────────────────────────────────────
    ai_mode = st.selectbox("What would you like help with?", [
        "🧹 Suggest cleaning steps for my data",
        "📊 Suggest visualizations",
        "🐍 Generate pandas code for my transformation log",
        "📖 Generate data dictionary",
        "💬 Custom question",
    ])

    user_prompt = ""

    if ai_mode == "🧹 Suggest cleaning steps for my data":
        user_prompt = (
            f"I have a dataset with {df.shape[0]} rows and {df.shape[1]} columns.\n"
            f"Column types: {df.dtypes.astype(str).to_dict()}\n"
            f"Missing values per column: {df.isnull().sum().to_dict()}\n"
            f"Duplicate rows: {int(df.duplicated().sum())}\n\n"
            "Please suggest specific data cleaning steps I should apply, "
            "with brief reasons for each. Be concise and practical."
        )

    elif ai_mode == "📊 Suggest visualizations":
        user_prompt = (
            f"My dataset has {df.shape[0]} rows and columns: {list(df.columns)}\n"
            f"Column types: {df.dtypes.astype(str).to_dict()}\n\n"
            "Suggest 4-5 useful visualizations. For each: chart type, "
            "which columns to use, and what insight it reveals."
        )

    elif ai_mode == "🐍 Generate pandas code for my transformation log":
        log = st.session_state.get("transform_log", [])
        if not log:
            st.warning("No transformations in the log yet. Apply some cleaning steps first.")
            return
        user_prompt = (
            f"Here is my data transformation log:\n{json.dumps(log, indent=2, default=str)}\n\n"
            "Generate clean, well-commented pandas Python code that reproduces all these steps. "
            "Assume the dataframe is already loaded as `df`."
        )

    elif ai_mode == "📖 Generate data dictionary":
        user_prompt = (
            f"Dataset columns with sample values:\n{df.head(5).to_string()}\n\n"
            f"Column types: {df.dtypes.astype(str).to_dict()}\n\n"
            "Generate a data dictionary table: for each column write its likely meaning, "
            "data type, and any potential data quality issues."
        )

    elif ai_mode == "💬 Custom question":
        user_prompt = st.text_area(
            "Your question",
            placeholder="e.g. Which columns are most useful for predicting revenue?",
            key="ai_custom"
        )

    # ── Send to Claude ────────────────────────────────────────────────────────
    if st.button("✨ Ask AI", type="primary") and user_prompt:
        with st.spinner("AI is thinking..."):
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=st.session_state["anthropic_api_key"])
                message = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    system=(
                        "You are a helpful data science assistant. "
                        "Give concise, practical advice focused on pandas and data wrangling. "
                        "Use markdown formatting."
                    ),
                    messages=[{"role": "user", "content": user_prompt}],
                )
                response = message.content[0].text
                st.markdown("### 🤖 AI Response")
                st.markdown(response)

            except ImportError:
                st.error("Run: `pip install anthropic` in your terminal.")
            except Exception as e:
                st.error(f"AI request failed: {e}")
