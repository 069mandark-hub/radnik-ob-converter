import os
import io
import json
import tempfile
import pandas as pd
import streamlit as st
from convert_ob import convert_single_ob, load_config, save_config

# -------------------------------------------------------------
# PAGE CONFIGURATION (Enterprise Wide Layout)
# -------------------------------------------------------------
st.set_page_config(
    page_title="Stitch Converter — Enterprise Operation Bulletin Standardization",
    page_icon="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# DESIGN SYSTEM: LINEAR / STRIPE / VERCEL ENTERPRISE THEME
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Typography & Colors */
    *, html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #0F172A;
    }
    .stApp {
        background-color: #F8FAFC !important;
    }

    /* Top Navigation Bar */
    .top-navbar {
        height: 60px;
        background: #FFFFFF;
        border-bottom: 1px solid #E2E8F0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 24px;
        margin: -6rem -4rem 2rem -4rem;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .brand-section {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-icon {
        width: 32px;
        height: 32px;
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #2563EB;
        font-weight: 700;
        font-size: 15px;
    }
    .brand-title {
        font-size: 15px;
        font-weight: 600;
        color: #0F172A;
        line-height: 1.2;
    }
    .brand-subtitle {
        font-size: 12px;
        font-weight: 400;
        color: #64748B;
        line-height: 1.2;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 9999px;
        padding: 4px 12px;
        font-size: 12px;
        font-weight: 500;
        color: #334155;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        background: #16A34A;
        border-radius: 50%;
    }

    /* Main Workspace Max Width & Centering */
    .main .block-container {
        max-width: 1040px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        width: 310px !important;
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding: 24px 20px !important;
    }
    .sidebar-header {
        margin-bottom: 20px;
        padding-bottom: 14px;
        border-bottom: 1px solid #E2E8F0;
    }
    .sidebar-title {
        font-size: 16px;
        font-weight: 600;
        color: #0F172A;
        margin: 0 0 4px 0;
    }
    .sidebar-desc {
        font-size: 12px;
        font-weight: 400;
        color: #64748B;
        line-height: 1.4;
        margin: 0;
    }
    .sidebar-section-title {
        font-size: 12px;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 20px 0 10px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .count-pill {
        background: #EFF6FF;
        color: #2563EB;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
    }

    /* Sidebar Form Controls */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p {
        color: #0F172A !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] .stCheckbox {
        margin-bottom: 8px !important;
    }

    /* Main Intro Header */
    .intro-header {
        text-align: center;
        margin-bottom: 28px;
    }
    .intro-title {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.025em;
        margin: 0 0 6px 0;
    }
    .intro-subtitle {
        font-size: 14px;
        font-weight: 400;
        color: #64748B;
        margin: 0;
    }

    /* Premium Upload Card */
    .upload-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.02);
        padding: 32px;
        margin-bottom: 24px;
    }
    .upload-hero {
        text-align: center;
        margin-bottom: 20px;
    }
    .upload-icon-container {
        width: 54px;
        height: 54px;
        background: #EFF6FF;
        border: 1px solid #DBEAFE;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 12px;
    }
    .upload-card-title {
        font-size: 16px;
        font-weight: 600;
        color: #0F172A;
        margin: 0 0 4px 0;
    }
    .upload-card-desc {
        font-size: 13px;
        color: #64748B;
        margin: 0 0 14px 0;
    }
    .format-pills {
        display: flex;
        gap: 6px;
        justify-content: center;
        align-items: center;
    }
    .format-pill {
        background: #F1F5F9;
        color: #475569;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        border: 1px solid #E2E8F0;
    }

    /* Native File Uploader Restyling */
    [data-testid="stFileUploader"] {
        background: #F8FAFC !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 24px 20px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #2563EB !important;
        background: #F0F7FF !important;
    }
    [data-testid="stFileUploader"] button {
        background: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 18px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2) !important;
    }
    [data-testid="stFileUploader"] button * {
        color: #FFFFFF !important;
    }
    [data-testid="stFileUploader"] small {
        color: #64748B !important;
        font-size: 12px !important;
    }

    /* Selected File Info Banner */
    .file-banner {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 16px 0;
    }
    .file-info-group {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .file-text-name {
        font-size: 14px;
        font-weight: 600;
        color: #0F172A;
    }
    .file-text-meta {
        font-size: 12px;
        color: #64748B;
    }
    .ready-tag {
        background: #DCFCE7;
        color: #166534;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
        border: 1px solid #BBF7D0;
    }

    /* Inputs */
    [data-testid="stTextInput"] input {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        color: #0F172A !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
    }

    /* Primary Convert Button */
    .stButton > button {
        width: 100% !important;
        background: #2563EB !important;
        color: #FFFFFF !important;
        border: 1px solid #2563EB !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
    }
    .stButton > button * {
        color: #FFFFFF !important;
    }
    .stButton > button:hover {
        background: #1D4ED8 !important;
        border-color: #1D4ED8 !important;
        box-shadow: 0 3px 8px rgba(37, 99, 235, 0.35) !important;
    }

    /* Metric Status Cards Grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 24px 0 16px 0;
    }
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: left;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 500;
        color: #64748B;
        margin-bottom: 6px;
    }
    .metric-val {
        font-size: 22px;
        font-weight: 700;
        color: #0F172A;
        line-height: 1;
    }

    /* Download Buttons */
    .download-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 14px;
    }
    .stDownloadButton button {
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 10px 18px !important;
        width: 100% !important;
    }

    /* Streamlit Defaults Cleanup */
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Load persistent config
saved_cfg = load_config()

# -------------------------------------------------------------
# A. TOP NAVIGATION BAR (60px Enterprise Nav)
# -------------------------------------------------------------
st.markdown("""
<div class="top-navbar">
    <div class="brand-section">
        <div class="brand-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
        </div>
        <div>
            <div class="brand-title">Stitch Converter</div>
            <div class="brand-subtitle">Operation Bulletin Standardization</div>
        </div>
    </div>
    <div class="status-badge">
        <span class="status-dot"></span>
        <span>Engine Ready</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# B. LEFT CONFIGURATION SIDEBAR (~300px)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-title">Configuration & Rules</div>
        <div class="sidebar-desc">Customize how your operation bulletin is processed.</div>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 1: COLUMN DETECTION
    st.markdown('<div class="sidebar-section-title">SMV / SAM Column Detection</div>', unsafe_allow_html=True)
    smv_options = ["auto", "Column A", "Column B", "Column C", "Column D", "Column E", "Column F", "Column G", "Column H"]
    smv_col = st.selectbox(
        "Column Target",
        options=smv_options,
        index=0 if saved_cfg.get("smv_column") == "auto" else 4,
        label_visibility="collapsed",
        help="Choose 'auto' to detect M/C.SMV, SAM, or lock to a specific column letter."
    )

    # SECTION 2: DUPLICATE HANDLING
    st.markdown('<div class="sidebar-section-title">Duplicate Handling</div>', unsafe_allow_html=True)
    skip_duplicates = st.toggle(
        "Skip duplicate operations",
        value=saved_cfg.get("skip_duplicates", True),
        help="Retain the first occurrence of duplicate operations."
    )
    st.caption("Retain the first occurrence of duplicate operations.")

    # SECTION 3: MANDATORY OPERATIONS
    # Calculate active count
    active_mand_keys = ["op_cutting_dispatch", "op_line_feeding", "op_eol_qc", "op_dispatch", "op_finishing", "op_tagging"]
    current_enabled = sum(1 for k in active_mand_keys if saved_cfg.get(k, True))

    st.markdown(f"""
    <div class="sidebar-section-title">
        <span>Mandatory Operations</span>
        <span class="count-pill">{current_enabled} of 6 enabled</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Select the operations that must be included in the converted bulletin.")

    op_c = st.checkbox("Cutting Dispatch (Tag C)", value=saved_cfg.get("op_cutting_dispatch", True))
    op_l = st.checkbox("Line Feeding (Tag L | Line Feeding flag)", value=saved_cfg.get("op_line_feeding", True))
    op_eol = st.checkbox("EOL QC (Tag A | Inspection table flag)", value=saved_cfg.get("op_eol_qc", True))
    op_d = st.checkbox("Dispatch (Tag D)", value=saved_cfg.get("op_dispatch", True))
    op_f = st.checkbox("Finishing (Tag F)", value=saved_cfg.get("op_finishing", True))
    op_t = st.checkbox("Tagging (Tag T | Final chain row)", value=saved_cfg.get("op_tagging", True))

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.caption("Default Parameters: Section: QUALITY CHECK | Sewing M/C: SEWING | Mandatory M/C: TABLE")

    # Persist configurations automatically
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
# C. MAIN WORKSPACE (Max Width ~1040px)
# -------------------------------------------------------------
st.markdown("""
<div class="intro-header">
    <div class="intro-title">Stitch Converter</div>
    <div class="intro-subtitle">Standardize factory Operation Bulletins into Stitch MES 29-column format.</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# PRIMARY UPLOAD CARD
# -------------------------------------------------------------
st.markdown("""
<div class="upload-card">
    <div class="upload-hero">
        <div class="upload-icon-container">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
        </div>
        <div class="upload-card-title">Upload Operation Bulletin</div>
        <div class="upload-card-desc">Drag and drop your spreadsheet file here, or click to browse.</div>
        <div class="format-pills">
            <span class="format-pill">XLSX</span>
            <span class="format-pill">XLS</span>
            <span class="format-pill">CSV</span>
            <span style="font-size: 11px; color: #94A3B8; margin-left: 6px;">Max 200 MB</span>
        </div>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose File",
    type=["xlsx", "xls", "csv"],
    label_visibility="collapsed"
)

if uploaded_file is not None:
    # Calculate file size in KB or MB
    file_bytes = len(uploaded_file.getvalue())
    if file_bytes > 1024 * 1024:
        size_str = f"{round(file_bytes / (1024 * 1024), 2)} MB"
    else:
        size_str = f"{round(file_bytes / 1024, 1)} KB"

    file_ext = os.path.splitext(uploaded_file.name)[1].upper().replace(".", "")
    style_guess = os.path.splitext(uploaded_file.name)[0]
    if style_guess.startswith("Radnik_OB_"):
        style_guess = style_guess.replace("Radnik_OB_", "")

    # Clean Horizontal File Selected Card
    st.markdown(f"""
    <div class="file-banner">
        <div class="file-info-group">
            <div style="width: 36px; height: 36px; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #2563EB; font-weight: 700; font-size: 11px;">
                {file_ext}
            </div>
            <div>
                <div class="file-text-name">{uploaded_file.name}</div>
                <div class="file-text-meta">{size_str} &bull; Excel Document</div>
            </div>
        </div>
        <span class="ready-tag">Ready for conversion</span>
    </div>
    """, unsafe_allow_html=True)

    # Style Name Input
    style_name = st.text_input("Style Name / Identifier", value=style_guess)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    convert_clicked = st.button("Convert to Stitch Format")

    if convert_clicked:
        with st.spinner("Standardizing operation bulletin..."):
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

                        # Metric Status Cards (4 Columns)
                        st.markdown(f"""
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-label">Sequence Rows</div>
                                <div class="metric-val">{total_rows}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-label">Total SAM (min)</div>
                                <div class="metric-val">{total_sam}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-label">Duplicates Filtered</div>
                                <div class="metric-val">{dup_count}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-label">Section Name</div>
                                <div class="metric-val" style="font-size: 16px; margin-top: 5px;">QUALITY CHECK</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Dual Download Actions
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
                                    label="Download Excel Workbook (.xlsx)",
                                    data=f_xlsx.read(),
                                    file_name=f"Stitch_OB_{style_name}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )

                        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

                        # Operations Preview Table
                        with st.expander(f"Preview Converted Sequence Table ({total_rows} rows)"):
                            st.dataframe(
                                df_res[["sort_order", "operation", "section", "machine_type", "tag", "sam", "is_line_feeding_operation", "place_inspection_table", "next_style_operation_item_operation"]],
                                use_container_width=True,
                                height=280
                            )

                        with st.expander("Conversion Execution Log"):
                            st.code("\n".join(logs))

                    else:
                        st.error("Conversion failed to produce output files.")

                except Exception as ex:
                    st.error(f"Error during conversion: {ex}")
                    if logs:
                        st.code("\n".join(logs))

st.markdown('</div>', unsafe_allow_html=True)
