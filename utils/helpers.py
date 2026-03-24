import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data
def profile_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary table with dtype, missing count/%, unique count per column."""
    rows = []
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        missing_pct   = round(missing_count / len(df) * 100, 2) if len(df) > 0 else 0
        rows.append({
            "Column":        col,
            "Dtype":         str(df[col].dtype),
            "Non-Null Count": df[col].notnull().sum(),
            "Missing Count": missing_count,
            "Missing %":     missing_pct,
            "Unique Values": df[col].nunique(),
            "Sample Value":  str(df[col].dropna().iloc[0]) if df[col].notnull().any() else "—",
        })
    return pd.DataFrame(rows).set_index("Column")


def log_transform(operation: str, params: dict, columns: list):
    """Append a step to the session transform log."""
    import streamlit as st
    from datetime import datetime
    entry = {
        "step":      len(st.session_state["transform_log"]) + 1,
        "operation": operation,
        "params":    params,
        "columns":   columns,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    st.session_state["transform_log"].append(entry)


def undo_last_transform():
    """Remove the last entry from the transform log (UI undo - resets df_working from scratch)."""
    import streamlit as st
    if st.session_state["transform_log"]:
        st.session_state["transform_log"].pop()
