import streamlit as st
import pandas as pd
from utils.helpers import profile_dataframe

@st.cache_data
def load_file(file_bytes, ext):
    import io
    buf = io.BytesIO(file_bytes)
    if ext == "csv":
        return pd.read_csv(buf)
    elif ext == "xlsx":
        return pd.read_excel(buf)
    elif ext == "json":
        return pd.read_json(buf)
    return None

def show():
    st.title("📁 Upload & Overview")
    st.markdown("Upload your dataset to get started. Supported formats: **CSV, Excel (.xlsx), JSON**.")

    # ── Upload widget ─────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "json"],
        help="Max recommended size: 200 MB"
    )

    col_reset, col_space = st.columns([1, 5])
    with col_reset:
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in ["df_original", "df_working", "transform_log", "file_name"]:
                st.session_state[key] = None if key != "transform_log" else []
            st.success("Session reset.")
            st.rerun()

    # ── Load file ─────────────────────────────────────────────────────────────
    if uploaded_file is not None:
        try:
            ext = uploaded_file.name.split(".")[-1].lower()
            df = load_file(uploaded_file.getvalue(), ext)
            if df is None:
                st.error("Unsupported file type.")
                return

            # Store in session only if new file
            if st.session_state["file_name"] != uploaded_file.name:
                st.session_state["df_original"] = df.copy()
                st.session_state["df_working"]  = df.copy()
                st.session_state["transform_log"] = []
                st.session_state["file_name"] = uploaded_file.name
                st.success(f"✅ **{uploaded_file.name}** loaded successfully!")

        except Exception as e:
            st.error(f"Failed to load file: {e}")
            return

    # ── Overview ──────────────────────────────────────────────────────────────
    if st.session_state["df_working"] is not None:
        df = st.session_state["df_working"]
        st.markdown("---")
        st.subheader("📊 Dataset Overview")

        # Key metrics row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rows", f"{df.shape[0]:,}")
        m2.metric("Columns", f"{df.shape[1]}")
        m3.metric("Missing Values", f"{df.isnull().sum().sum():,}")
        m4.metric("Duplicate Rows", f"{df.duplicated().sum():,}")

        st.markdown("---")

        # Column info table
        st.subheader("🗂️ Column Summary")
        profile = profile_dataframe(df)
        st.dataframe(profile, use_container_width=True)

        st.markdown("---")

        # Basic stats
        tab_num, tab_cat = st.tabs(["📈 Numeric Statistics", "🔤 Categorical Statistics"])

        with tab_num:
            num_df = df.select_dtypes(include="number")
            if not num_df.empty:
                st.dataframe(num_df.describe().T.round(3), use_container_width=True)
            else:
                st.info("No numeric columns found.")

        with tab_cat:
            cat_df = df.select_dtypes(include=["object", "category"])
            if not cat_df.empty:
                cat_stats = pd.DataFrame({
                    "Unique Values": cat_df.nunique(),
                    "Most Frequent": cat_df.mode().iloc[0],
                    "Frequency": [cat_df[c].value_counts().iloc[0] for c in cat_df.columns],
                })
                st.dataframe(cat_stats, use_container_width=True)
            else:
                st.info("No categorical columns found.")

        st.markdown("---")

        # Missing values detail
        st.subheader("❓ Missing Values by Column")
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if missing.empty:
            st.success("No missing values found!")
        else:
            miss_df = pd.DataFrame({
                "Missing Count": missing,
                "Missing %": (missing / len(df) * 100).round(2)
            })
            st.dataframe(miss_df, use_container_width=True)

        st.markdown("---")

        # Data preview
        st.subheader("👀 Data Preview (first 50 rows)")
        st.dataframe(df.head(50), use_container_width=True)

    else:
        st.info("👆 Upload a file above to see the overview.")
        st.markdown("**Don't have a dataset?** Use one of the sample datasets from the `sample_data/` folder.")
