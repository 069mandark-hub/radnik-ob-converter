import os
import io
import json
import tempfile
import pandas as pd
import streamlit as st
from convert_ob import convert_single_ob, load_config, save_config

# Page Configuration: Starts with sidebar collapsed (accessible via 3-bar hamburger menu)
st.set_page_config(
    page_title="Stitch Converter - Operation Bulletin Engine",
    page_icon="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom High-End Styling (Plus Jakarta Sans, Soft Ambient Background, Glass Cards, No Emojis)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Global Typography & Light Gradient Ambient Background */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background: linear-gradient(145deg, #f0f4f8 0%, #e9eef5 50%, #f7fafc 100%) !important;
        color: #0f172a !important;
    }

    /* Style the Sidebar Hamburger Button (3 Bars) */
    button[kind="header"] {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
        color: #0f172a !important;
        transition: all 0.2s ease !important;
    }
    button[kind="header"]:hover {
        background: #f1f5f9 !important;
        border-color: #94a3b8 !important;
    }

    /* Hide standard Streamlit header & footer decorations */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* Elevated White Container Cards */
    .app-card {
        background: #ffffff;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 12px 32px -4px rgba(15, 23, 42, 0.06), 0 4px 12px -2px rgba(15, 23, 42, 0.03);
        padding: 32px;
        margin-bottom: 24px;
    }

    /* Minimalist Header Styling */
    .app-header {
        text-align: center;
        margin-bottom: 32px;
        padding-top: 10px;
    }
    .app-title {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #0f172a;
        margin-bottom: 8px;
    }
    .app-subtitle {
        font-size: 14px;
        font-weight: 400;
        color: #64748b;
        margin-bottom: 0px;
    }

    /* File Dropzone Enhancements */
    [data-testid="stFileUploader"] {
        border-radius: 12px;
        background: #f8fafc;
        border: 2px dashed #cbd5e1;
        padding: 16px;
        transition: all 0.2s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #2563eb;
        background: #f1f5f9;
    }

    /* Primary Convert Button */
    button[kind="primary"] {
        width: 100%;
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        color: #ffffff !important;
        border: 1px solid #0f172a !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.15) !important;
        transition: all 0.2s ease !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.22) !important;
    }

    /* Stat Metric Badges */
    .metrics-container {
        display: flex;
        gap: 12px;
        margin: 20px 0;
        flex-wrap: wrap;
    }
    .stat-badge {
        flex: 1;
        min-width: 130px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
    .stat-number {
        font-size: 22px;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .stat-label {
        font-size: 11px;
        font-weight: 500;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    /* Download Buttons */
    .stDownloadButton button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: 4px 0 24px rgba(15, 23, 42, 0.04) !important;
    }
    .sidebar-title {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .sidebar-note {
        font-size: 12px;
        color: #64748b;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Load persistent config
saved_cfg = load_config()

# -------------------------------------------------------------
# SIDEBAR: ONE-TIME SETUP (HIDDEN BEHIND 3-BAR HAMBURGER MENU)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">Configuration & Rules</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-note">Settings are remembered automatically for this client.</div>', unsafe_allow_html=True)

    smv_col = st.selectbox(
        "SMV / SAM Column Detection",
        options=["auto", "Column A", "Column B", "Column C", "Column D", "Column E", "Column F", "Column G", "Column H"],
        index=0 if saved_cfg.get("smv_column") == "auto" else 4,
        help="Choose 'auto' to detect M/C.SMV, SAM, or lock to a specific column index."
    )

    skip_duplicates = st.checkbox(
        "Skip duplicate operations (Retain 1st occurrence)",
        value=saved_cfg.get("skip_duplicates", True)
    )

    st.markdown("---")
    st.markdown("**Mandatory Operations**")
    st.caption("Standard specifications: Section: QUALITY CHECK | Sewing M/C: SEWING | Mandatory M/C: TABLE")

    op_c = st.checkbox("Cutting Dispatch (Tag C)", value=saved_cfg.get("op_cutting_dispatch", True))
    op_l = st.checkbox("Line Feeding (Tag L | Line Feeding flag)", value=saved_cfg.get("op_line_feeding", True))
    op_eol = st.checkbox("EOL QC (Tag A | Inspection table flag)", value=saved_cfg.get("op_eol_qc", True))
    op_d = st.checkbox("Dispatch (Tag D)", value=saved_cfg.get("op_dispatch", True))
    op_f = st.checkbox("Finishing (Tag F)", value=saved_cfg.get("op_finishing", True))
    op_t = st.checkbox("Tagging (Tag T | Final chain row)", value=saved_cfg.get("op_tagging", True))

    # Auto-save changes
    current_cfg = {
        "smv_column": smv_col,
        "skip_duplicates": skip_duplicates,
        "op_cutting_dispatch": op_c,
        "op_line_feeding": op_l,
        "op_eol_qc": op_eol,
        "op_dispatch": op_d,
        "op_finishing": op_f,
        "op_tagging": op_t
    }
    save_config(current_cfg)

# -------------------------------------------------------------
# MAIN CONTENT: ULTRA-CLEAN, FOCUSED CONVERSION STAGE
# -------------------------------------------------------------
st.markdown("""
<div class="app-header">
    <div class="app-title">Stitch Converter</div>
    <div class="app-subtitle">Standardize factory Operation Bulletins into Stitch MES 29-column format</div>
</div>
""", unsafe_allow_html=True)

# Main Card: Upload & Action
st.markdown('<div class="app-card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Operation Bulletin (.xlsx, .xls, .csv)",
    type=["xlsx", "xls", "csv"],
    help="Supports all Excel workbooks and CSV exports."
)

if uploaded_file is not None:
    style_guess = os.path.splitext(uploaded_file.name)[0]
    if style_guess.startswith("Radnik_OB_"):
        style_guess = style_guess.replace("Radnik_OB_", "")

    style_name = st.text_input("Style Name / Reference", value=style_guess)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    convert_clicked = st.button("Convert to Stitch MES Format", type="primary")

    if convert_clicked:
        with st.spinner("Processing bulletin..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                input_path = os.path.join(tmpdir, uploaded_file.name)
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                logs = []
                def log_func(msg):
                    logs.append(msg)

                try:
                    convert_single_ob(
                        input_path,
                        style_name,
                        tmpdir,
                        smv_col=smv_col,
                        skip_duplicates=skip_duplicates,
                        op_cutting_dispatch=op_c,
                        op_line_feeding=op_l,
                        op_eol_qc=op_eol,
                        op_dispatch=op_d,
                        op_finishing=op_f,
                        op_tagging=op_t,
                        log_func=log_func
                    )

                    csv_path = os.path.join(tmpdir, f"Stitch_OB_{style_name}.csv")
                    xlsx_path = os.path.join(tmpdir, f"Stitch_OB_{style_name}.xlsx")

                    if not os.path.exists(csv_path):
                        csv_path = os.path.join(tmpdir, f"Stitch_OB_{style_name}_latest.csv")
                    if not os.path.exists(xlsx_path):
                        xlsx_path = os.path.join(tmpdir, f"Stitch_OB_{style_name}_latest.xlsx")

                    if os.path.exists(csv_path) and os.path.exists(xlsx_path):
                        df_res = pd.read_csv(csv_path)

                        total_rows = len(df_res)
                        total_sam = round(float(df_res['sam'].sum()), 2)
                        
                        # Calculate skipped duplicates from logs
                        dup_count = 0
                        for l in logs:
                            if "Skipped" in l and "duplicate" in l:
                                try:
                                    dup_count = int(l.split("Skipped")[1].split("duplicate")[0].strip())
                                except Exception:
                                    dup_count = 1

                        # Summary Metric Cards
                        st.markdown(f"""
                        <div class="metrics-container">
                            <div class="stat-badge">
                                <div class="stat-number">{total_rows}</div>
                                <div class="stat-label">Sequence Rows</div>
                            </div>
                            <div class="stat-badge">
                                <div class="stat-number">{total_sam}</div>
                                <div class="stat-label">Total SAM (min)</div>
                            </div>
                            <div class="stat-badge">
                                <div class="stat-number">{dup_count}</div>
                                <div class="stat-label">Duplicates Skipped</div>
                            </div>
                            <div class="stat-badge">
                                <div class="stat-number">QUALITY CHECK</div>
                                <div class="stat-label">Section</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Dual Download Buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            with open(csv_path, "rb") as f_csv:
                                st.download_button(
                                    label="Download Stitch CSV (ERP Ready)",
                                    data=f_csv.read(),
                                    file_name=f"Stitch_OB_{style_name}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                        with col2:
                            with open(xlsx_path, "rb") as f_xlsx:
                                st.download_button(
                                    label="Download Excel (.xlsx)",
                                    data=f_xlsx.read(),
                                    file_name=f"Stitch_OB_{style_name}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )

                        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

                        # Collapsed Preview Table
                        with st.expander(f"Preview Converted Table ({total_rows} operations)"):
                            st.dataframe(
                                df_res[["sort_order", "operation", "section", "machine_type", "tag", "sam", "is_line_feeding_operation", "place_inspection_table", "next_style_operation_item_operation"]],
                                use_container_width=True
                            )

                        with st.expander("Conversion Log Output"):
                            st.code("\n".join(logs))

                    else:
                        st.error("Conversion failed to produce output files.")

                except Exception as ex:
                    st.error(f"Error during conversion: {ex}")
                    if logs:
                        st.code("\n".join(logs))

st.markdown('</div>', unsafe_allow_html=True)
