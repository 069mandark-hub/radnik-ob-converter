import os
import io
import json
import tempfile
import pandas as pd
import streamlit as st
from convert_ob import convert_single_ob, load_config, save_config

# Page Configuration: Starts with sidebar collapsed (accessible via 3-bar hamburger menu in top-left)
st.set_page_config(
    page_title="Stitch Converter - Operation Bulletin Engine",
    page_icon="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom High-End Styling: Clean, High Legibility, No Broken Divs, Polished Palette
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Global Typography & Light Gradient Ambient Background */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background: linear-gradient(145deg, #f1f5f9 0%, #e8edf5 45%, #f8fafc 100%) !important;
        color: #0f172a !important;
    }

    /* Top Padding & Center Container Width */
    .main .block-container {
        max-width: 680px !important;
        padding-top: 48px !important;
        padding-bottom: 60px !important;
    }

    /* Style the Sidebar Hamburger Button (3 Bars) prominently in top-left */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        top: 20px !important;
        left: 20px !important;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
        padding: 6px 12px !important;
        color: #0f172a !important;
        z-index: 999999 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="collapsedControl"]:hover {
        background: #f8fafc !important;
        border-color: #94a3b8 !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12) !important;
    }

    /* Hide standard Streamlit header & footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* Dropzone Styling with crisp contrast */
    [data-testid="stFileUploader"] {
        background: #ffffff !important;
        border: 2px dashed #cbd5e1 !important;
        border-radius: 14px !important;
        padding: 24px 20px !important;
        box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.05) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6 !important;
        box-shadow: 0 12px 28px -4px rgba(59, 130, 246, 0.08) !important;
    }
    [data-testid="stFileUploader"] section {
        background: transparent !important;
        padding: 0 !important;
    }
    [data-testid="stFileUploader"] section > input + div {
        color: #475569 !important;
    }
    [data-testid="stFileUploader"] button {
        background: #f1f5f9 !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 8px 18px !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background: #e2e8f0 !important;
        border-color: #94a3b8 !important;
    }

    /* Style Input Fields */
    [data-testid="stTextInput"] input {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        color: #0f172a !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }

    /* Primary Convert Button */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        color: #ffffff !important;
        border: 1px solid #0f172a !important;
        border-radius: 10px !important;
        padding: 14px 24px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.15) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.25) !important;
    }

    /* Stat Metric Badges */
    .metrics-container {
        display: flex;
        gap: 12px;
        margin: 24px 0 16px 0;
        flex-wrap: wrap;
    }
    .stat-badge {
        flex: 1;
        min-width: 130px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
    }
    .stat-number {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.1;
    }
    .stat-label {
        font-size: 11px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 6px;
    }

    /* Download Buttons */
    .stDownloadButton button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 12px 20px !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
        transition: all 0.2s ease !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: 6px 0 24px rgba(15, 23, 42, 0.04) !important;
    }
    .sidebar-header-box {
        padding-bottom: 12px;
        margin-bottom: 16px;
        border-bottom: 1px solid #e2e8f0;
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
    }
</style>
""", unsafe_allow_html=True)

# Load persistent config
saved_cfg = load_config()

# -------------------------------------------------------------
# SIDEBAR: ONE-TIME SETUP (HIDDEN BEHIND 3-BAR HAMBURGER MENU)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header-box">
        <div class="sidebar-title">Configuration & Rules</div>
        <div class="sidebar-note">Settings are remembered automatically for this client.</div>
    </div>
    """, unsafe_allow_html=True)

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
    st.caption("Standard rules: Section: QUALITY CHECK | Sewing M/C: SEWING | Mandatory M/C: TABLE")

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
# MAIN CONTENT: CLEAN, FOCUSED CONVERSION STAGE
# -------------------------------------------------------------
st.markdown("""
<div style="text-align: center; margin-bottom: 28px;">
    <h1 style="font-size: 32px; font-weight: 700; color: #0f172a; margin: 0 0 6px 0; letter-spacing: -0.02em;">Stitch Converter</h1>
    <p style="font-size: 14px; color: #64748b; margin: 0;">Standardize factory Operation Bulletins into Stitch MES 29-column format</p>
</div>
""", unsafe_allow_html=True)

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

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    convert_clicked = st.button("Convert to Stitch MES Format")

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
                        
                        dup_count = 0
                        for l in logs:
                            if "Skipped" in l and "duplicate" in l:
                                try:
                                    dup_count = int(l.split("Skipped")[1].split("duplicate")[0].strip())
                                except Exception:
                                    dup_count = 1

                        # Stat Badges
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
