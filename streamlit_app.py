# Stitch Converter Enterprise UI v2.2 - Forced Rebuild Trigger
import os
import io
import json
import tempfile
import pandas as pd
import streamlit as st
from convert_ob import convert_single_ob, load_config, save_config

# Page Config: Clean enterprise wide layout
st.set_page_config(
    page_title="Stitch Converter — Enterprise OB Standardization",
    page_icon="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load persistent client configuration
saved_cfg = load_config()

# -------------------------------------------------------------
# HIGH-END ENTERPRISE UI STYLING (INTER / PLUS JAKARTA SANS)
# Palette: #F8FAFC (BG), #FFFFFF (Surface), #0F172A (Text), #2563EB (Primary)
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --primary-color: #2563eb !important;
        --background-color: #f8fafc !important;
        --secondary-background-color: #ffffff !important;
        --text-color: #0f172a !important;
    }

    /* Global Typography & Canvas */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    /* Main Content Container */
    .main {
        background-color: #f8fafc !important;
    }
    .main .block-container {
        max-width: 980px !important;
        margin: 0 auto !important;
        padding: 36px 24px 64px 24px !important;
    }

    /* Top Navigation Bar */
    .top-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0 28px 0;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 28px;
    }
    .top-nav-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-icon-box {
        width: 38px;
        height: 38px;
        background: #2563eb;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 15px;
        letter-spacing: -0.02em;
    }
    .brand-title {
        font-size: 17px;
        font-weight: 700;
        color: #0f172a !important;
        line-height: 1.2;
    }
    .brand-sub {
        font-size: 12px;
        color: #64748b !important;
        font-weight: 400;
    }
    .top-nav-badge {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1d4ed8 !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Sidebar Styling: Clean White Surface with Crisp Dark Typography */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        width: 320px !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding: 24px 18px 48px 18px !important;
        background: #ffffff !important;
    }

    /* Force Dark Text on ALL Typography */
    .stApp,
    section[data-testid="stSidebar"],
    .main,
    p, span, label, h1, h2, h3, h4,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] label p,
    [data-testid="stCheckbox"] label span,
    [data-testid="stSelectbox"] label,
    [data-testid="stSelectbox"] p {
        color: #0f172a !important;
    }

    .stCaption, .stCaption p, small {
        color: #64748b !important;
    }

    /* Sidebar Toggle Controls (3-bars hamburger expand button ALWAYS visible & prominent) */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 48px !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 999999 !important;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 6px 8px !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08) !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        background: #ffffff !important;
        color: #0f172a !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg,
    button[data-testid="stSidebarCollapseButton"] svg {
        fill: #0f172a !important;
        stroke: #0f172a !important;
        color: #0f172a !important;
    }
    button[data-testid="stSidebarCollapseButton"] {
        background: #f1f5f9 !important;
        border-radius: 8px !important;
    }

    /* Sidebar Headings & Sections */
    .sidebar-section-title {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #475569 !important;
        margin: 18px 0 8px 0;
    }
    .sidebar-card-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 12px;
    }

    /* Checkbox Styling inside Sidebar */
    [data-testid="stCheckbox"] {
        padding: 3px 0 !important;
    }
    [data-testid="stCheckbox"] label p {
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #1e293b !important;
    }
    [data-testid="stCheckbox"] input[type="checkbox"] {
        accent-color: #2563eb !important;
    }

    /* Selectbox Styling */
    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
    }
    [data-baseweb="select"] * {
        color: #0f172a !important;
    }
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1) !important;
    }
    [data-baseweb="menu"] {
        background-color: #ffffff !important;
    }
    [data-baseweb="menu"] li {
        color: #0f172a !important;
        background-color: #ffffff !important;
    }
    [data-baseweb="menu"] li:hover {
        background-color: #f1f5f9 !important;
    }

    /* Main Area Header */
    .hero-title-box {
        margin-bottom: 24px;
    }
    .hero-title {
        font-size: 26px;
        font-weight: 700;
        color: #0f172a !important;
        letter-spacing: -0.02em;
        margin: 0 0 6px 0;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #64748b !important;
        margin: 0;
    }

    /* Active Config Summary Pill Bar */
    .config-summary-bar {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 16px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
        font-size: 12px;
        color: #475569 !important;
    }
    .config-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-weight: 500;
    }
    .config-pill-dot {
        width: 7px;
        height: 7px;
        background: #16a34a;
        border-radius: 50%;
    }

    /* Premium Upload Card */
    .upload-card-wrapper {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        margin-bottom: 24px;
    }

    /* Streamlit File Uploader Box */
    [data-testid="stFileUploader"] {
        background-color: #f8fafc !important;
        border: 2px dashed #93c5fd !important;
        border-radius: 12px !important;
        padding: 24px 18px !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        background-color: #eff6ff !important;
        border-color: #2563eb !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background-color: transparent !important;
        border: none !important;
        padding: 8px !important;
    }

    /* Browse Files Button */
    [data-testid="stFileUploader"] button {
        background-color: #ffffff !important;
        color: #2563eb !important;
        border: 1.5px solid #2563eb !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        box-shadow: 0 1px 2px rgba(37, 99, 235, 0.08) !important;
    }
    [data-testid="stFileUploader"] button * {
        color: #2563eb !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background-color: #2563eb !important;
        color: #ffffff !important;
    }
    [data-testid="stFileUploader"] button:hover * {
        color: #ffffff !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] div {
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        color: #64748b !important;
        font-size: 12px !important;
    }

    /* Converted Item Row */
    .file-item-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 16px 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }
    .file-meta-group {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .file-badge-icon {
        width: 36px;
        height: 36px;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #2563eb !important;
        font-weight: 700;
        font-size: 12px;
    }
    .file-title-text {
        font-size: 14px;
        font-weight: 600;
        color: #0f172a !important;
    }
    .status-converted {
        color: #16a34a !important;
        font-weight: 600;
        font-size: 13px;
    }

    /* Primary Convert Button */
    .stButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #1d4ed8 !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        width: 100% !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button * {
        color: #ffffff !important;
    }
    .stButton > button:hover {
        background-color: #1d4ed8 !important;
    }

    /* Metric Summary Badges */
    .stats-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 20px 0 16px 0;
    }
    .stat-pill-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 16px;
        text-align: left;
    }
    .stat-pill-num {
        font-size: 22px;
        font-weight: 700;
        color: #0f172a !important;
        line-height: 1;
    }
    .stat-pill-lbl {
        font-size: 11px;
        font-weight: 600;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 6px;
    }

    /* Download Buttons */
    .stDownloadButton > button {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #0f172a !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        width: 100% !important;
    }
    .stDownloadButton > button * {
        color: #ffffff !important;
    }
    .stDownloadButton > button:hover {
        background-color: #1e293b !important;
    }

    /* Hide standard footer and main menu, keep header for collapse button */
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SIDEBAR: CONFIGURATION & RULES (ONE-TIME SETUP, CAN COLLAPSE)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div style="font-size: 17px; font-weight: 700; color: #0f172a; margin-bottom: 2px;">Configuration & Rules</div>
        <div style="font-size: 12px; color: #64748b;">Customize how your operation bulletin is processed.</div>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 1: COLUMN DETECTION
    st.markdown('<div class="sidebar-section-title">SMV / SAM Column Detection</div>', unsafe_allow_html=True)
    col_options = ["auto", "Column A", "Column B", "Column C", "Column D", "Column E", "Column F", "Column G", "Column H"]
    saved_col = saved_cfg.get("smv_column", "auto")
    col_idx = col_options.index(saved_col) if saved_col in col_options else 0
    smv_col = st.selectbox(
        "SMV Column Selection",
        options=col_options,
        index=col_idx,
        label_visibility="collapsed",
        help="Select 'auto' to automatically detect M/C.SMV, SAM, or choose a specific column."
    )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # SECTION 2: DUPLICATE HANDLING
    st.markdown('<div class="sidebar-section-title">Duplicate Handling</div>', unsafe_allow_html=True)
    skip_duplicates = st.checkbox(
        "Skip duplicate operations",
        value=saved_cfg.get("skip_duplicates", True),
        help="Retain the first occurrence of duplicate operations."
    )
    st.caption("Retain the first occurrence of duplicate operations.")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # SECTION 3: MANDATORY OPERATIONS
    # Calculate active count
    op_c_val = saved_cfg.get("op_cutting_dispatch", True)
    op_l_val = saved_cfg.get("op_line_feeding", True)
    op_eol_val = saved_cfg.get("op_eol_qc", True)
    op_d_val = saved_cfg.get("op_dispatch", True)
    op_f_val = saved_cfg.get("op_finishing", True)
    op_t_val = saved_cfg.get("op_tagging", True)

    active_count = sum([op_c_val, op_l_val, op_eol_val, op_d_val, op_f_val, op_t_val])

    st.markdown(f'<div class="sidebar-section-title">Mandatory Operations ({active_count} of 6 enabled)</div>', unsafe_allow_html=True)
    st.caption("Select the operations that must be included in the converted bulletin.")

    op_c = st.checkbox("Cutting Dispatch (Tag C)", value=op_c_val)
    op_l = st.checkbox("Line Feeding (Tag L | Flag)", value=op_l_val)
    op_eol = st.checkbox("EOL QC (Tag A | Inspection Table)", value=op_eol_val)
    op_d = st.checkbox("Dispatch (Tag D)", value=op_d_val)
    op_f = st.checkbox("Finishing (Tag F)", value=op_f_val)
    op_t = st.checkbox("Tagging (Tag T | Final Row)", value=op_t_val)

    # Auto-save changes immediately to config
    new_cfg = {
        "smv_column": smv_col,
        "skip_duplicates": skip_duplicates,
        "op_cutting_dispatch": op_c,
        "op_line_feeding": op_l,
        "op_eol_qc": op_eol,
        "op_dispatch": op_d,
        "op_finishing": op_f,
        "op_tagging": op_t
    }
    if new_cfg != saved_cfg:
        save_config(new_cfg)
        saved_cfg = new_cfg
        st.rerun()

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # SECTION 4: STITCH ERP SPECIFICATION SUMMARY
    st.markdown('<div class="sidebar-section-title">ERP Format Specification</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-card-box" style="font-size: 11px; color: #475569; line-height: 1.5;">
        <div><b>Format:</b> 29 Standard Columns</div>
        <div><b>Section:</b> QUALITY CHECK</div>
        <div><b>Sewing M/C:</b> SEWING</div>
        <div><b>Mandatory M/C:</b> TABLE</div>
        <div><b>EOL QC:</b> Tag A (place_inspection_table=1)</div>
        <div><b>Cut-off:</b> Stops at TOTAL row</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# MAIN WORKSPACE
# -------------------------------------------------------------

# Top Navigation Bar
st.markdown("""
<div class="top-navbar">
    <div class="top-nav-left">
        <div class="brand-icon-box">SC</div>
        <div>
            <div class="brand-title">Stitch Converter</div>
            <div class="brand-sub">Operation Bulletin Standardization</div>
        </div>
    </div>
    <div>
        <span class="top-nav-badge">Stitch MES Ready</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Heading
st.markdown("""
<div class="hero-title-box">
    <h1 class="hero-title">Stitch Converter</h1>
    <p class="hero-subtitle">Standardize factory Operation Bulletins into Stitch MES 29-column format.</p>
</div>
""", unsafe_allow_html=True)

# Active Configuration Summary Pill Bar
active_ops_num = sum([
    saved_cfg.get("op_cutting_dispatch", True),
    saved_cfg.get("op_line_feeding", True),
    saved_cfg.get("op_eol_qc", True),
    saved_cfg.get("op_dispatch", True),
    saved_cfg.get("op_finishing", True),
    saved_cfg.get("op_tagging", True)
])

st.markdown(f"""
<div class="config-summary-bar">
    <span class="config-pill"><span class="config-pill-dot"></span> <b>SMV Detection:</b> {saved_cfg.get("smv_column", "auto").upper()}</span>
    <span class="config-pill"><span class="config-pill-dot"></span> <b>Duplicates:</b> {'Skipped' if saved_cfg.get("skip_duplicates", True) else 'Kept'}</span>
    <span class="config-pill"><span class="config-pill-dot"></span> <b>Mandatory Ops:</b> {active_ops_num} of 6 Active</span>
    <span class="config-pill"><span class="config-pill-dot"></span> <b>Section:</b> QUALITY CHECK</span>
    <span class="config-pill" style="margin-left: auto; color: #2563eb; font-weight: 600;">(Click ☰ at top-left to adjust rules)</span>
</div>
""", unsafe_allow_html=True)

# Upload Card
st.markdown('<div class="upload-card-wrapper">', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Operation Bulletin",
    type=["xlsx", "xls", "csv"],
    help="Upload your factory Excel or CSV technical bulletin (up to 200MB)."
)

st.markdown('</div>', unsafe_allow_html=True)

# Processing and Conversion
if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name
    file_size_kb = len(file_bytes) / 1024
    size_str = f"{file_size_kb / 1024:.1f} MB" if file_size_kb > 1024 else f"{file_size_kb:.0f} KB"
    file_ext = file_name.split('.')[-1].upper()

    # File Selected State Card
    st.markdown(f"""
    <div class="file-item-card">
        <div class="file-meta-group">
            <div class="file-badge-icon">{file_ext}</div>
            <div>
                <div class="file-title-text">{file_name}</div>
                <div style="font-size: 12px; color: #64748b;">Size: {size_str}</div>
            </div>
        </div>
        <div class="status-converted">Ready to Convert</div>
    </div>
    """, unsafe_allow_html=True)

    convert_clicked = st.button("Convert to Stitch Format", key="btn_convert_main")

    if convert_clicked:
        with st.spinner("Standardizing and generating Stitch MES sequence..."):
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_input = os.path.join(tmp_dir, file_name)
                with open(tmp_input, "wb") as f:
                    f.write(file_bytes)

                logs = []
                def capture_log(msg):
                    logs.append(msg)

                try:
                    out_xlsx = convert_single_ob(
                        file_path=tmp_input,
                        style_name=os.path.splitext(file_name)[0],
                        output_folder=tmp_dir,
                        smv_col=saved_cfg.get("smv_column", "auto"),
                        skip_duplicates=saved_cfg.get("skip_duplicates", True),
                        op_cutting_dispatch=saved_cfg.get("op_cutting_dispatch", True),
                        op_line_feeding=saved_cfg.get("op_line_feeding", True),
                        op_eol_qc=saved_cfg.get("op_eol_qc", True),
                        op_dispatch=saved_cfg.get("op_dispatch", True),
                        op_finishing=saved_cfg.get("op_finishing", True),
                        op_tagging=saved_cfg.get("op_tagging", True),
                        log_func=capture_log
                    )

                    with open(out_xlsx, "rb") as f:
                        xlsx_data = f.read()

                    df_converted = pd.read_excel(out_xlsx)
                    csv_data = df_converted.to_csv(index=False).encode("utf-8")

                    total_rows = len(df_converted)
                    sam_sum = round(df_converted["sam"].sum(), 2)
                    sewing_ops = len(df_converted[df_converted["machine_type"] == "SEWING"])
                    mandatory_ops = len(df_converted[df_converted["machine_type"] == "TABLE"])

                    # Store in session state for instant persistence
                    st.session_state["converted_result"] = {
                        "xlsx_data": xlsx_data,
                        "csv_data": csv_data,
                        "file_name": file_name,
                        "df": df_converted,
                        "total_rows": total_rows,
                        "sam_sum": sam_sum,
                        "sewing_ops": sewing_ops,
                        "mandatory_ops": mandatory_ops
                    }
                    st.success("Successfully converted to 29-column Stitch MES format!")

                except Exception as e:
                    st.error(f"Conversion failed: {str(e)}")

# Display Result if Converted
if "converted_result" in st.session_state:
    res = st.session_state["converted_result"]
    base_name = os.path.splitext(res["file_name"])[0]

    st.markdown("""
    <div class="stats-row">
        <div class="stat-pill-box">
            <div class="stat-pill-num">{}</div>
            <div class="stat-pill-lbl">Total Sequence Rows</div>
        </div>
        <div class="stat-pill-box">
            <div class="stat-pill-num">{}</div>
            <div class="stat-pill-lbl">Sewing Operations</div>
        </div>
        <div class="stat-pill-box">
            <div class="stat-pill-num">{}</div>
            <div class="stat-pill-lbl">Mandatory Ops</div>
        </div>
        <div class="stat-pill-box">
            <div class="stat-pill-num">{}</div>
            <div class="stat-pill-lbl">Total SAM (Mins)</div>
        </div>
    </div>
    """.format(res["total_rows"], res["sewing_ops"], res["mandatory_ops"], res["sam_sum"]), unsafe_allow_html=True)

    # Converted File Status Card with Download Actions
    st.markdown(f"""
    <div class="file-item-card" style="border-color: #86efac; background: #f0fdf4;">
        <div class="file-meta-group">
            <div class="file-badge-icon" style="background: #dcfce7; border-color: #86efac; color: #16a34a;">XLSX</div>
            <div>
                <div class="file-title-text">Stitch_OB_{base_name}.xlsx</div>
                <div style="font-size: 12px; color: #16a34a; font-weight: 500;">✓ Converted • 29 Columns • Linked Flow Chain</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="Download Standardized Excel (.xlsx)",
            data=res["xlsx_data"],
            file_name=f"Stitch_OB_{base_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_xlsx"
        )
    with col_dl2:
        st.download_button(
            label="Download CSV Format (.csv)",
            data=res["csv_data"],
            file_name=f"Stitch_OB_{base_name}.csv",
            mime="text/csv",
            key="dl_csv"
        )

    # Preview Table
    with st.expander("Preview Standardized 29-Column Table", expanded=False):
        st.dataframe(res["df"], use_container_width=True)
