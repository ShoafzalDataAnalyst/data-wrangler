import streamlit as st
import pandas as pd
import json
from datetime import datetime
import io

def show():
    st.title("💾 Export & Report")

    if st.session_state.get("df_working") is None:
        st.warning("⚠️ Please upload a dataset first on the **Upload & Overview** page.")
        return

    df_orig = st.session_state["df_original"]
    df_work = st.session_state["df_working"]
    log     = st.session_state.get("transform_log", [])

    # ── Summary stats ─────────────────────────────────────────────────────────
    st.subheader("📊 Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Original rows",  f"{len(df_orig):,}")
    c2.metric("Cleaned rows",   f"{len(df_work):,}")
    c3.metric("Rows removed",   f"{len(df_orig) - len(df_work):,}")
    c4.metric("Steps applied",  len(log))

    st.markdown("---")

    # ── Transformation log ────────────────────────────────────────────────────
    st.subheader("📋 Transformation Log")
    if not log:
        st.info("No transformations were applied.")
    else:
        log_df = pd.DataFrame(log)
        st.dataframe(log_df, use_container_width=True)

    st.markdown("---")

    # ── Export cleaned dataset ────────────────────────────────────────────────
    st.subheader("⬇️ Export Cleaned Dataset")
    col1, col2 = st.columns(2)

    with col1:
        csv_bytes = df_work.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📄 Download CSV",
            data=csv_bytes,
            file_name="cleaned_dataset.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
            df_work.to_excel(writer, index=False, sheet_name="Cleaned Data")
        st.download_button(
            label="📊 Download Excel",
            data=excel_buf.getvalue(),
            file_name="cleaned_dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.markdown("---")

    # ── Export transformation report ──────────────────────────────────────────
    st.subheader("📝 Transformation Report")

    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_file":  st.session_state.get("file_name", "unknown"),
        "original_shape": {"rows": len(df_orig), "columns": len(df_orig.columns)},
        "cleaned_shape":  {"rows": len(df_work), "columns": len(df_work.columns)},
        "steps": log,
    }

    col3, col4 = st.columns(2)

    with col3:
        report_json = json.dumps(report, indent=2, default=str)
        st.download_button(
            label="🗂️ Download JSON Recipe",
            data=report_json.encode("utf-8"),
            file_name="transformation_report.json",
            mime="application/json",
            use_container_width=True,
        )

    with col4:
        # Python script snippet
        lines = [
            "import pandas as pd",
            "import numpy as np",
            "",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"df = pd.read_csv('your_file.csv')",
            "",
        ]
        for step in log:
            lines.append(f"# Step {step['step']}: {step['operation']}")
            lines.append(f"# Columns: {step['columns']}")
            lines.append(f"# Params: {step['params']}")
            lines.append("")
        py_script = "\n".join(lines)
        st.download_button(
            label="🐍 Download Python Script",
            data=py_script.encode("utf-8"),
            file_name="transformation_recipe.py",
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown("---")

    # ── Preview cleaned data ──────────────────────────────────────────────────
    st.subheader("👀 Preview Cleaned Dataset")
    st.dataframe(df_work.head(50), use_container_width=True)
