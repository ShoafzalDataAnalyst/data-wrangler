import streamlit as st
import pandas as pd
import numpy as np
from utils.helpers import log_transform

def show():
    st.title("🧽 Cleaning Studio")

    if st.session_state.get("df_working") is None:
        st.warning("⚠️ Please upload a dataset first on the **Upload & Overview** page.")
        return

    df = st.session_state["df_working"]

    # ── Transformation log + undo ─────────────────────────────────────────────
    with st.expander("📋 Transformation Log", expanded=False):
        log = st.session_state.get("transform_log", [])
        if not log:
            st.info("No transformations applied yet.")
        else:
            for entry in log:
                st.markdown(
                    f"**{entry['step']}.** `{entry['operation']}` — "
                    f"cols: {entry['columns']} — _{entry['timestamp']}_"
                )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("↩️ Undo Last Step"):
                if st.session_state["transform_log"]:
                    st.session_state["transform_log"].pop()
                    st.session_state["df_working"] = st.session_state["df_original"].copy()
                    st.session_state["transform_log"] = []
                    st.warning("Undo resets to original — please re-apply remaining steps.")
                    st.rerun()
        with col2:
            if st.button("🔄 Reset All Transformations"):
                st.session_state["df_working"] = st.session_state["df_original"].copy()
                st.session_state["transform_log"] = []
                st.success("All transformations reset.")
                st.rerun()

    st.markdown("---")

    (tab_missing, tab_dupes, tab_types,
     tab_cat, tab_num, tab_scale,
     tab_cols, tab_valid) = st.tabs([
        "❓ Missing Values", "👥 Duplicates", "🔄 Data Types",
        "🔤 Categorical", "🔢 Numeric", "📏 Scaling",
        "🗂️ Column Ops", "✅ Validation",
    ])

    # ── 4.1 Missing Values ────────────────────────────────────────────────────
    with tab_missing:
        st.subheader("❓ Missing Values")
        missing = df.isnull().sum()
        missing = missing[missing > 0]

        if missing.empty:
            st.success("✅ No missing values in the dataset!")
        else:
            miss_df = pd.DataFrame({
                "Missing Count": missing,
                "Missing %": (missing / len(df) * 100).round(2)
            })
            st.dataframe(miss_df, use_container_width=True)

            action = st.selectbox("Choose action", [
                "Drop rows with missing values",
                "Drop columns above missing threshold (%)",
                "Fill with constant value",
                "Fill with mean / median / mode",
                "Forward fill",
                "Backward fill",
            ], key="mv_action")

            cols_with_missing = missing.index.tolist()
            selected_cols = st.multiselect("Apply to columns", cols_with_missing,
                                           default=cols_with_missing, key="mv_cols")

            if action == "Drop rows with missing values":
                if selected_cols:
                    preview_count = df[selected_cols].isnull().any(axis=1).sum()
                    st.info(f"Will drop **{preview_count}** rows.")
                if st.button("Apply", key="mv_apply1"):
                    st.session_state["df_working"] = df.dropna(subset=selected_cols).reset_index(drop=True)
                    log_transform("Drop rows (missing)", {}, selected_cols)
                    st.success("Done."); st.rerun()

            elif action == "Drop columns above missing threshold (%)":
                threshold = st.slider("Max allowed missing %", 0, 100, 50, key="mv_thresh")
                cols_to_drop = [c for c in selected_cols
                                if (df[c].isnull().sum() / len(df) * 100) >= threshold]
                st.info(f"Will drop: {cols_to_drop}")
                if st.button("Apply", key="mv_apply2"):
                    st.session_state["df_working"] = df.drop(columns=cols_to_drop)
                    log_transform("Drop columns (threshold)", {"threshold": threshold}, cols_to_drop)
                    st.success("Done."); st.rerun()

            elif action == "Fill with constant value":
                fill_val = st.text_input("Constant value", "0", key="mv_const")
                if st.button("Apply", key="mv_apply3"):
                    new_df = df.copy()
                    for c in selected_cols:
                        try:
                            new_df[c] = new_df[c].fillna(type(new_df[c].dropna().iloc[0])(fill_val))
                        except Exception:
                            new_df[c] = new_df[c].fillna(fill_val)
                    st.session_state["df_working"] = new_df
                    log_transform("Fill constant", {"value": fill_val}, selected_cols)
                    st.success("Done."); st.rerun()

            elif action == "Fill with mean / median / mode":
                strategy = st.radio("Strategy", ["mean", "median", "mode"], horizontal=True, key="mv_strat")
                if st.button("Apply", key="mv_apply4"):
                    new_df = df.copy()
                    for c in selected_cols:
                        if strategy == "mean" and pd.api.types.is_numeric_dtype(new_df[c]):
                            new_df[c] = new_df[c].fillna(new_df[c].mean())
                        elif strategy == "median" and pd.api.types.is_numeric_dtype(new_df[c]):
                            new_df[c] = new_df[c].fillna(new_df[c].median())
                        else:
                            new_df[c] = new_df[c].fillna(new_df[c].mode().iloc[0])
                    st.session_state["df_working"] = new_df
                    log_transform(f"Fill {strategy}", {}, selected_cols)
                    st.success("Done."); st.rerun()

            elif action == "Forward fill":
                if st.button("Apply", key="mv_apply5"):
                    new_df = df.copy()
                    new_df[selected_cols] = new_df[selected_cols].ffill()
                    st.session_state["df_working"] = new_df
                    log_transform("Forward fill", {}, selected_cols)
                    st.success("Done."); st.rerun()

            elif action == "Backward fill":
                if st.button("Apply", key="mv_apply6"):
                    new_df = df.copy()
                    new_df[selected_cols] = new_df[selected_cols].bfill()
                    st.session_state["df_working"] = new_df
                    log_transform("Backward fill", {}, selected_cols)
                    st.success("Done."); st.rerun()

            st.markdown("#### Before / After Preview")
            c1, c2 = st.columns(2)
            c1.metric("Total rows", len(df))
            c2.metric("Missing cells (selected cols)",
                      int(df[selected_cols].isnull().sum().sum()) if selected_cols else 0)

    # ── 4.2 Duplicates ────────────────────────────────────────────────────────
    with tab_dupes:
        st.subheader("👥 Duplicates")
        full_dupes = df.duplicated().sum()
        st.metric("Full-row duplicates", full_dupes)

        subset_cols = st.multiselect("Check duplicates by subset of columns (optional)",
                                     df.columns.tolist(), key="dup_subset")
        subset = subset_cols if subset_cols else None
        subset_dupes = df.duplicated(subset=subset).sum()
        st.metric("Duplicates (selected keys)", subset_dupes)

        if subset_dupes > 0:
            if st.checkbox("Show duplicate rows", key="dup_show"):
                st.dataframe(df[df.duplicated(subset=subset, keep=False)], use_container_width=True)

        keep = st.radio("Keep", ["first", "last"], horizontal=True, key="dup_keep")
        if st.button("Remove Duplicates", key="dup_apply"):
            before = len(df)
            new_df = df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)
            removed = before - len(new_df)
            st.session_state["df_working"] = new_df
            log_transform("Remove duplicates", {"subset": subset, "keep": keep}, subset_cols or ["all"])
            st.success(f"Removed {removed} duplicate rows."); st.rerun()

    # ── 4.3 Data Types ────────────────────────────────────────────────────────
    with tab_types:
        st.subheader("🔄 Data Types & Parsing")
        st.dataframe(
            pd.DataFrame({"Column": df.columns, "Current Type": df.dtypes.values.astype(str)}),
            use_container_width=True, hide_index=True
        )
        col_to_convert = st.selectbox("Column to convert", df.columns, key="dt_col")
        target_type = st.selectbox("Convert to", ["numeric", "categorical", "datetime", "string"], key="dt_type")
        dt_format = None
        if target_type == "datetime":
            dt_format = st.text_input("Datetime format (optional, e.g. %Y-%m-%d)", "", key="dt_fmt")
        if st.button("Convert", key="dt_apply"):
            new_df = df.copy()
            try:
                if target_type == "numeric":
                    new_df[col_to_convert] = pd.to_numeric(
                        new_df[col_to_convert].astype(str).str.replace(r"[,\$£€]", "", regex=True),
                        errors="coerce")
                elif target_type == "categorical":
                    new_df[col_to_convert] = new_df[col_to_convert].astype("category")
                elif target_type == "datetime":
                    new_df[col_to_convert] = pd.to_datetime(
                        new_df[col_to_convert], format=dt_format if dt_format else None, errors="coerce")
                elif target_type == "string":
                    new_df[col_to_convert] = new_df[col_to_convert].astype(str)
                st.session_state["df_working"] = new_df
                log_transform(f"Convert → {target_type}", {}, [col_to_convert])
                st.success(f"Converted '{col_to_convert}' to {target_type}."); st.rerun()
            except Exception as e:
                st.error(f"Conversion failed: {e}")

    # ── 4.4 Categorical ───────────────────────────────────────────────────────
    with tab_cat:
        st.subheader("🔤 Categorical Data Tools")
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        if not cat_cols:
            st.info("No categorical columns found.")
        else:
            cat_col = st.selectbox("Select column", cat_cols, key="cat_col")
            st.dataframe(df[cat_col].value_counts().reset_index(), use_container_width=True)

            cat_action = st.selectbox("Action", [
                "Trim whitespace", "Lowercase", "Title Case",
                "Map / Replace values", "Group rare categories into 'Other'",
                "One-Hot Encode",
            ], key="cat_action")

            if cat_action == "Trim whitespace":
                if st.button("Apply", key="cat_a1"):
                    new_df = df.copy(); new_df[cat_col] = new_df[cat_col].astype(str).str.strip()
                    st.session_state["df_working"] = new_df
                    log_transform("Trim whitespace", {}, [cat_col]); st.success("Done."); st.rerun()

            elif cat_action == "Lowercase":
                if st.button("Apply", key="cat_a2"):
                    new_df = df.copy(); new_df[cat_col] = new_df[cat_col].astype(str).str.lower()
                    st.session_state["df_working"] = new_df
                    log_transform("Lowercase", {}, [cat_col]); st.success("Done."); st.rerun()

            elif cat_action == "Title Case":
                if st.button("Apply", key="cat_a3"):
                    new_df = df.copy(); new_df[cat_col] = new_df[cat_col].astype(str).str.title()
                    st.session_state["df_working"] = new_df
                    log_transform("Title Case", {}, [cat_col]); st.success("Done."); st.rerun()

            elif cat_action == "Map / Replace values":
                st.markdown("Change old values to new ones:")
                unique_vals = df[cat_col].dropna().unique().tolist()
                mapping = {}
                for val in unique_vals[:20]:
                    new_val = st.text_input(f"{val}", str(val), key=f"map_{cat_col}_{val}")
                    if new_val != str(val):
                        mapping[val] = new_val
                if st.button("Apply Mapping", key="cat_a4"):
                    if mapping:
                        new_df = df.copy(); new_df[cat_col] = new_df[cat_col].replace(mapping)
                        st.session_state["df_working"] = new_df
                        log_transform("Map values", {"mapping": str(mapping)}, [cat_col])
                        st.success(f"Applied {len(mapping)} mappings."); st.rerun()
                    else:
                        st.warning("No changes detected.")

            elif cat_action == "Group rare categories into 'Other'":
                threshold = st.slider("Frequency threshold (%)", 1, 20, 5, key="cat_thresh")
                freq = df[cat_col].value_counts(normalize=True) * 100
                rare = freq[freq < threshold].index.tolist()
                st.info(f"Will group {len(rare)} rare categories → 'Other'")
                if st.button("Apply", key="cat_a5"):
                    new_df = df.copy()
                    new_df[cat_col] = new_df[cat_col].where(~new_df[cat_col].isin(rare), other="Other")
                    st.session_state["df_working"] = new_df
                    log_transform("Group rare → Other", {"threshold_%": threshold}, [cat_col])
                    st.success("Done."); st.rerun()

            elif cat_action == "One-Hot Encode":
                unique_count = df[cat_col].nunique()
                st.info(f"Will create **{unique_count}** new binary columns (one per category) and drop the original.")
                drop_first = st.checkbox("Drop first category (avoid multicollinearity)", value=False, key="ohe_drop")
                if st.button("Apply", key="cat_a6"):
                    new_df = df.copy()
                    dummies = pd.get_dummies(new_df[cat_col], prefix=cat_col, drop_first=drop_first)
                    new_df = pd.concat([new_df.drop(columns=[cat_col]), dummies], axis=1)
                    st.session_state["df_working"] = new_df
                    log_transform("One-Hot Encode", {"drop_first": drop_first}, [cat_col])
                    st.success(f"Created {len(dummies.columns)} new columns."); st.rerun()

    # ── 4.5 Numeric Cleaning ──────────────────────────────────────────────────
    with tab_num:
        st.subheader("🔢 Numeric Cleaning & Outliers")
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if not num_cols:
            st.info("No numeric columns found.")
        else:
            num_col = st.selectbox("Select column", num_cols, key="num_col")
            method  = st.radio("Detection method", ["IQR", "Z-score"], horizontal=True, key="num_method")
            col_data = df[num_col].dropna()

            if method == "IQR":
                Q1, Q3 = col_data.quantile(0.25), col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
            else:
                lower = col_data.mean() - 3 * col_data.std()
                upper = col_data.mean() + 3 * col_data.std()

            outliers = df[(df[num_col] < lower) | (df[num_col] > upper)]
            st.info(f"Detected **{len(outliers)}** outliers — range: [{lower:.2f}, {upper:.2f}]")

            action = st.selectbox("Action", [
                "Do nothing", "Remove outlier rows", "Cap (Winsorize) at quantiles"
            ], key="num_action")

            if action == "Remove outlier rows":
                if st.button("Apply", key="num_a1"):
                    new_df = df[(df[num_col] >= lower) & (df[num_col] <= upper)].reset_index(drop=True)
                    st.session_state["df_working"] = new_df
                    log_transform("Remove outliers", {"method": method}, [num_col])
                    st.success(f"Removed {len(outliers)} rows."); st.rerun()

            elif action == "Cap (Winsorize) at quantiles":
                low_q  = st.slider("Lower quantile", 0.0, 0.1, 0.01, 0.01, key="num_lq")
                high_q = st.slider("Upper quantile", 0.9, 1.0, 0.99, 0.01, key="num_hq")
                if st.button("Apply", key="num_a2"):
                    new_df = df.copy()
                    new_df[num_col] = new_df[num_col].clip(
                        lower=new_df[num_col].quantile(low_q),
                        upper=new_df[num_col].quantile(high_q))
                    st.session_state["df_working"] = new_df
                    log_transform("Winsorize", {"low_q": low_q, "high_q": high_q}, [num_col])
                    st.success("Capped outliers."); st.rerun()

    # ── 4.6 Scaling ───────────────────────────────────────────────────────────
    with tab_scale:
        st.subheader("📏 Normalization & Scaling")
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if not num_cols:
            st.info("No numeric columns found.")
        else:
            scale_cols   = st.multiselect("Columns to scale", num_cols, key="sc_cols")
            scale_method = st.radio("Method", ["Min-Max (0–1)", "Z-score standardization"],
                                    horizontal=True, key="sc_method")
            if scale_cols:
                st.markdown("**Before:**")
                st.dataframe(df[scale_cols].describe().T[["mean","std","min","max"]].round(3),
                             use_container_width=True)
            if st.button("Apply Scaling", key="sc_apply") and scale_cols:
                new_df = df.copy()
                for c in scale_cols:
                    if scale_method == "Min-Max (0–1)":
                        mn, mx = new_df[c].min(), new_df[c].max()
                        new_df[c] = (new_df[c] - mn) / (mx - mn) if mx != mn else 0.0
                    else:
                        mu, sigma = new_df[c].mean(), new_df[c].std()
                        new_df[c] = (new_df[c] - mu) / sigma if sigma != 0 else 0.0
                st.session_state["df_working"] = new_df
                log_transform(f"Scale ({scale_method})", {}, scale_cols)
                st.success("Scaling applied!")
                st.markdown("**After:**")
                st.dataframe(new_df[scale_cols].describe().T[["mean","std","min","max"]].round(3),
                             use_container_width=True)
                st.rerun()

    # ── 4.7 Column Ops ────────────────────────────────────────────────────────
    with tab_cols:
        st.subheader("🗂️ Column Operations")
        col_op = st.selectbox("Operation", [
            "Rename column", "Drop columns",
            "Create new column (formula)", "Bin numeric column",
        ], key="co_op")

        if col_op == "Rename column":
            old = st.selectbox("Column to rename", df.columns, key="co_old")
            new = st.text_input("New name", old, key="co_new")
            if st.button("Rename", key="co_a1") and new != old:
                st.session_state["df_working"] = df.rename(columns={old: new})
                log_transform("Rename column", {"from": old, "to": new}, [old])
                st.success(f"'{old}' → '{new}'"); st.rerun()

        elif col_op == "Drop columns":
            to_drop = st.multiselect("Columns to drop", df.columns, key="co_drop")
            if st.button("Drop", key="co_a2") and to_drop:
                st.session_state["df_working"] = df.drop(columns=to_drop)
                log_transform("Drop columns", {}, to_drop)
                st.success(f"Dropped: {to_drop}"); st.rerun()

        elif col_op == "Create new column (formula)":
            new_name = st.text_input("New column name", "new_col", key="co_ncol")
            formula  = st.text_input("Formula (e.g. col_a / col_b  or  log(price))", key="co_form")
            st.caption("Available: log, sqrt, abs, mean, std, np")
            if st.button("Create", key="co_a3") and formula:
                try:
                    new_df = df.copy()
                    env = {c: new_df[c] for c in new_df.columns}
                    env.update({"log": np.log, "sqrt": np.sqrt, "abs": np.abs,
                                "mean": np.mean, "std": np.std, "np": np})
                    new_df[new_name] = eval(formula, {"__builtins__": {}}, env)
                    st.session_state["df_working"] = new_df
                    log_transform("Create column", {"formula": formula}, [new_name])
                    st.success(f"Created '{new_name}'"); st.rerun()
                except Exception as e:
                    st.error(f"Formula error: {e}")

        elif col_op == "Bin numeric column":
            num_cols = df.select_dtypes(include="number").columns.tolist()
            bin_col    = st.selectbox("Column", num_cols, key="co_bcol")
            n_bins     = st.slider("Number of bins", 2, 20, 5, key="co_bins")
            bin_method = st.radio("Method", ["Equal-width", "Quantile"], horizontal=True, key="co_bm")
            bin_name   = st.text_input("New column name", f"{bin_col}_binned", key="co_bn")
            if st.button("Apply Binning", key="co_a4"):
                new_df = df.copy()
                try:
                    if bin_method == "Equal-width":
                        new_df[bin_name] = pd.cut(new_df[bin_col], bins=n_bins, duplicates="drop").astype(str)
                    else:
                        new_df[bin_name] = pd.qcut(new_df[bin_col], q=n_bins, duplicates="drop").astype(str)
                    st.session_state["df_working"] = new_df
                    log_transform("Bin column", {"bins": n_bins, "method": bin_method}, [bin_col])
                    st.success(f"Binned into '{bin_name}'"); st.rerun()
                except Exception as e:
                    st.error(f"Binning error: {e}")

    # ── 4.8 Validation ────────────────────────────────────────────────────────
    with tab_valid:
        st.subheader("✅ Data Validation Rules")
        valid_col = st.selectbox("Column to validate", df.columns, key="vl_col")
        rule = st.selectbox("Rule", [
            "Numeric range check (min / max)",
            "Allowed categories list",
            "Non-null constraint",
        ], key="vl_rule")

        violations = None

        if rule == "Numeric range check (min / max)":
            vmin = st.number_input("Min value", value=0.0, key="vl_min")
            vmax = st.number_input("Max value", value=1000.0, key="vl_max")
            if st.button("Check", key="vl_c1"):
                col_num = pd.to_numeric(df[valid_col], errors="coerce")
                violations = df[(col_num < vmin) | (col_num > vmax)]

        elif rule == "Allowed categories list":
            allowed_raw = st.text_input("Allowed values (comma-separated)", key="vl_allowed")
            if st.button("Check", key="vl_c2") and allowed_raw:
                allowed = [v.strip() for v in allowed_raw.split(",")]
                violations = df[~df[valid_col].isin(allowed)]

        elif rule == "Non-null constraint":
            if st.button("Check", key="vl_c3"):
                violations = df[df[valid_col].isnull()]

        if violations is not None:
            if len(violations) == 0:
                st.success("✅ No violations found!")
            else:
                st.error(f"Found **{len(violations)}** violations:")
                st.dataframe(violations, use_container_width=True)
                st.download_button("⬇️ Export violations CSV",
                                   violations.to_csv(index=False).encode(),
                                   "violations.csv", "text/csv")
