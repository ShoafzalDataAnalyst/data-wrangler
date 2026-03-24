import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

def show():
    st.title("📊 Visualization Builder")

    if st.session_state.get("df_working") is None:
        st.warning("⚠️ Please upload a dataset first on the **Upload & Overview** page.")
        return

    df = st.session_state["df_working"]
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    all_cols = df.columns.tolist()

    st.markdown("Build charts from your cleaned data. All settings are interactive.")
    st.markdown("---")

    # ── Chart type ────────────────────────────────────────────────────────────
    chart_type = st.selectbox("📈 Chart Type", [
        "Histogram",
        "Box Plot",
        "Scatter Plot",
        "Line Chart (time series)",
        "Bar Chart (grouped)",
        "Heatmap / Correlation Matrix",
    ], key="viz_chart")

    st.markdown("---")

    # ── Filters ───────────────────────────────────────────────────────────────
    with st.expander("🔍 Filters (optional)", expanded=False):
        filtered_df = df.copy()

        if cat_cols:
            filter_cat_col = st.selectbox("Filter by category column", ["(none)"] + cat_cols, key="f_cat_col")
            if filter_cat_col != "(none)":
                unique_vals = df[filter_cat_col].dropna().unique().tolist()
                selected_vals = st.multiselect("Keep values", unique_vals, default=unique_vals, key="f_cat_vals")
                filtered_df = filtered_df[filtered_df[filter_cat_col].isin(selected_vals)]

        if num_cols:
            filter_num_col = st.selectbox("Filter by numeric range", ["(none)"] + num_cols, key="f_num_col")
            if filter_num_col != "(none)":
                col_min = float(df[filter_num_col].min())
                col_max = float(df[filter_num_col].max())
                rng = st.slider("Range", col_min, col_max, (col_min, col_max), key="f_num_range")
                filtered_df = filtered_df[
                    (filtered_df[filter_num_col] >= rng[0]) &
                    (filtered_df[filter_num_col] <= rng[1])
                ]

        st.caption(f"Rows after filtering: **{len(filtered_df):,}** / {len(df):,}")

    st.markdown("---")

    # ── Chart-specific controls & render ─────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#262730")
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444")

    rendered = False

    # ── Histogram ─────────────────────────────────────────────────────────────
    if chart_type == "Histogram":
        if not num_cols:
            st.warning("No numeric columns available."); return
        x_col = st.selectbox("Column", num_cols, key="h_x")
        bins   = st.slider("Bins", 5, 100, 30, key="h_bins")
        color  = st.color_picker("Bar color", "#4C9BE8", key="h_color")
        ax.hist(filtered_df[x_col].dropna(), bins=bins, color=color, edgecolor="#222")
        ax.set_xlabel(x_col); ax.set_ylabel("Frequency"); ax.set_title(f"Histogram — {x_col}")
        rendered = True

    # ── Box Plot ──────────────────────────────────────────────────────────────
    elif chart_type == "Box Plot":
        if not num_cols:
            st.warning("No numeric columns available."); return
        y_col   = st.selectbox("Numeric column (Y)", num_cols, key="bp_y")
        grp_col = st.selectbox("Group by (optional)", ["(none)"] + cat_cols, key="bp_grp")
        if grp_col == "(none)":
            data = [filtered_df[y_col].dropna().values]
            labels = [y_col]
        else:
            groups = filtered_df[grp_col].dropna().unique()[:15]
            data   = [filtered_df[filtered_df[grp_col] == g][y_col].dropna().values for g in groups]
            labels = [str(g) for g in groups]
        bp = ax.boxplot(data, labels=labels, patch_artist=True)
        for patch in bp["boxes"]:
            patch.set_facecolor("#4C9BE8")
        ax.set_ylabel(y_col); ax.set_title(f"Box Plot — {y_col}")
        plt.xticks(rotation=30, ha="right", color="white")
        rendered = True

    # ── Scatter Plot ──────────────────────────────────────────────────────────
    elif chart_type == "Scatter Plot":
        if len(num_cols) < 2:
            st.warning("Need at least 2 numeric columns."); return
        x_col   = st.selectbox("X axis", num_cols, key="sc_x")
        y_col   = st.selectbox("Y axis", [c for c in num_cols if c != x_col], key="sc_y")
        grp_col = st.selectbox("Color by (optional)", ["(none)"] + cat_cols, key="sc_grp")
        if grp_col == "(none)":
            ax.scatter(filtered_df[x_col], filtered_df[y_col],
                       alpha=0.6, color="#4C9BE8", s=20)
        else:
            groups = filtered_df[grp_col].dropna().unique()
            cmap   = plt.cm.get_cmap("tab10", len(groups))
            for i, g in enumerate(groups):
                sub = filtered_df[filtered_df[grp_col] == g]
                ax.scatter(sub[x_col], sub[y_col], alpha=0.6,
                           color=cmap(i), label=str(g), s=20)
            ax.legend(facecolor="#333", labelcolor="white", fontsize=8)
        ax.set_xlabel(x_col); ax.set_ylabel(y_col)
        ax.set_title(f"Scatter — {x_col} vs {y_col}")
        rendered = True

    # ── Line Chart ────────────────────────────────────────────────────────────
    elif chart_type == "Line Chart (time series)":
        x_col = st.selectbox("X axis (datetime or index)", ["(index)"] + all_cols, key="lc_x")
        y_cols = st.multiselect("Y axis columns (numeric)", num_cols, default=num_cols[:1], key="lc_y")
        if not y_cols:
            st.warning("Select at least one Y column."); return
        plot_df = filtered_df.copy()
        if x_col != "(index)":
            try:
                plot_df[x_col] = pd.to_datetime(plot_df[x_col], errors="coerce")
                plot_df = plot_df.sort_values(x_col)
                x_vals = plot_df[x_col]
            except Exception:
                x_vals = plot_df[x_col]
        else:
            x_vals = plot_df.index
        colors = plt.cm.tab10.colors
        for i, yc in enumerate(y_cols):
            ax.plot(x_vals, plot_df[yc], label=yc, color=colors[i % 10], linewidth=1.5)
        ax.legend(facecolor="#333", labelcolor="white")
        ax.set_xlabel(x_col if x_col != "(index)" else "Index")
        ax.set_title("Line Chart")
        plt.xticks(rotation=30, ha="right", color="white")
        rendered = True

    # ── Bar Chart ─────────────────────────────────────────────────────────────
    elif chart_type == "Bar Chart (grouped)":
        if not cat_cols:
            st.warning("No categorical columns available."); return
        x_col  = st.selectbox("Category column (X)", cat_cols, key="bc_x")
        y_col  = st.selectbox("Numeric column (Y)", num_cols, key="bc_y") if num_cols else None
        agg    = st.selectbox("Aggregation", ["count", "sum", "mean", "median"], key="bc_agg")
        top_n  = st.slider("Show top N categories", 5, 50, 15, key="bc_topn")
        grp    = st.selectbox("Group by (optional)", ["(none)"] + [c for c in cat_cols if c != x_col], key="bc_grp")

        if agg == "count":
            plot_data = filtered_df[x_col].value_counts().head(top_n)
            ax.bar(plot_data.index.astype(str), plot_data.values, color="#4C9BE8")
            ax.set_ylabel("Count")
        elif y_col:
            if grp == "(none)":
                if agg == "sum":
                    plot_data = filtered_df.groupby(x_col)[y_col].sum().nlargest(top_n)
                elif agg == "mean":
                    plot_data = filtered_df.groupby(x_col)[y_col].mean().nlargest(top_n)
                else:
                    plot_data = filtered_df.groupby(x_col)[y_col].median().nlargest(top_n)
                ax.bar(plot_data.index.astype(str), plot_data.values, color="#4C9BE8")
                ax.set_ylabel(f"{agg}({y_col})")
            else:
                pivot = filtered_df.groupby([x_col, grp])[y_col].mean().unstack(fill_value=0)
                pivot = pivot.loc[pivot.sum(axis=1).nlargest(top_n).index]
                pivot.plot(kind="bar", ax=ax, colormap="tab10")
                ax.legend(facecolor="#333", labelcolor="white", fontsize=8)
                ax.set_ylabel(f"mean({y_col})")

        ax.set_xlabel(x_col)
        ax.set_title(f"Bar Chart — {x_col}")
        plt.xticks(rotation=40, ha="right", color="white")
        rendered = True

    # ── Heatmap / Correlation ─────────────────────────────────────────────────
    elif chart_type == "Heatmap / Correlation Matrix":
        if len(num_cols) < 2:
            st.warning("Need at least 2 numeric columns."); return
        selected = st.multiselect("Columns (numeric only)", num_cols, default=num_cols[:8], key="hm_cols")
        if len(selected) < 2:
            st.warning("Select at least 2 columns."); return
        corr = filtered_df[selected].corr()
        im   = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        plt.colorbar(im, ax=ax)
        ax.set_xticks(range(len(selected))); ax.set_xticklabels(selected, rotation=45, ha="right", color="white")
        ax.set_yticks(range(len(selected))); ax.set_yticklabels(selected, color="white")
        for i in range(len(selected)):
            for j in range(len(selected)):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                        fontsize=7, color="white")
        ax.set_title("Correlation Matrix")
        rendered = True

    # ── Show chart ────────────────────────────────────────────────────────────
    if rendered:
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
