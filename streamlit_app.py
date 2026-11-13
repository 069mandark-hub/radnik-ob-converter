import os
import io
import json
import tempfile
import pandas as pd
import streamlit as st
from convert_ob import convert_single_ob, load_config, save_config

# Page Config: Wide layout
st.set_page_config(
    page_title="Stitch Converter — Enterprise OB Standardization",
    page_icon="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load persistent config
saved_cfg = load_config()

# -------------------------------------------------------------
# HIGH-END UI STYLING: EXACT REPLICA OF THE REFERENCE DASHBOARD
# Royal Blue Backdrop + Elevated Floating White Canvas + Crisp Nav
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Global Typography & Royal Blue Outer Canvas */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: #1d4ed8 !important; /* Royal Blue Background matching reference */
    }

    /* Floating White Dashboard Container */
    .main .block-container {
        max-width: 1240px !important;
        background: #ffffff !important;
        border-radius: 24px !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25) !important;
        margin-top: 24px !important;
        margin-bottom: 24px !important;
        padding: 32px 36px 48px 36px !important;
    }

    /* Sidebar Reset & Styling (Always Visible & Accessible) */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: none !important;
        width: 290px !important;
    }
    section[data-testid="stSidebar"] .block-container {
        background: transparent !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        margin: 0 !important;
        padding: 24px 16px !important;
    }

    /* Typography & Contrast: High-contrast Dark Text on Content Surfaces */
    .main .block-container,
    .main .block-container p,
    .main .block-container label,
    .main .block-container div[data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        color: #0f172a !important;
    }
    .stCaption, .stCaption p {
        color: #64748b !important;
    }

    /* Sidebar Toggle Controls (Ensure hamburger/expand button is ALWAYS visible & clickable when sidebar is collapsed) */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 999999 !important;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 4px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        background: #ffffff !important;
        color: #0f172a !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: #0f172a !important;
        stroke: #0f172a !important;
    }
    button[data-testid="stSidebarCollapseButton"] {
        background: #f1f5f9 !important;
        border-radius: 8px !important;
    }
    button[data-testid="stSidebarCollapseButton"] svg {
        fill: #0f172a !important;
        stroke: #0f172a !important;
    }

    /* Navigation Brand Banner */
    .brand-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 12px 24px 12px;
        border-bottom: 1px solid #f1f5f9;
        margin-bottom: 16px;
    }
    .brand-badge {
        width: 38px;
        height: 38px;
        background: #2563eb;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 16px;
    }
    .brand-name {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a !important;
        line-height: 1.2;
    }

    /* Nav Radio Pill Menu */
    .nav-section {
        margin-bottom: 20px;
    }
    div[data-testid="stRadio"] > div {
        background: transparent !important;
        gap: 4px !important;
    }
    div[data-testid="stRadio"] label {
        background: transparent !important;
        border-radius: 10px !important;
        padding: 8px 14px !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
    }
    div[data-testid="stRadio"] label:hover {
        background: #f1f5f9 !important;
    }
    div[data-testid="stRadio"] label span {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }

    /* Main Area Title */
    .main-title-box {
        margin-bottom: 24px;
    }
    .main-title {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a !important;
        letter-spacing: -0.02em;
        margin: 0 0 4px 0;
    }
    .main-subtitle {
        font-size: 13px;
        color: #64748b !important;
        margin: 0;
    }

    /* High-End Dropzone Container */
    [data-testid="stFileUploader"] {
        background: #f8fafc !important;
        border: 2px dashed #3b82f6 !important;
        border-radius: 16px !important;
        padding: 32px 24px !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        background: #eff6ff !important;
        border-color: #1d4ed8 !important;
    }
    /* Dropzone Upload Button */
    [data-testid="stFileUploader"] button {
        background: #ffffff !important;
        color: #2563eb !important;
        border: 1.5px solid #2563eb !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.12) !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stFileUploader"] button * {
        color: #2563eb !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background: #2563eb !important;
        color: #ffffff !important;
    }
    [data-testid="stFileUploader"] button:hover * {
        color: #ffffff !important;
    }
    /* Dropzone Internal Instruction Text */
    [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        border: none !important;
        padding: 12px !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] div,
    [data-testid="stFileUploader"] section > input + div {
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] small,
    [data-testid="stFileUploader"] small {
        color: #64748b !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }

    /* Converted Item Row (Exact Match with Reference Image) */
    .file-item-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 12px 0;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
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
        color: #2563eb;
        font-weight: 700;
        font-size: 12px;
    }
    .file-meta-group {
        display: flex;
        align-items: center;
        gap: 12px;
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
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .file-size-tag {
        color: #64748b !important;
        font-size: 13px;
        font-weight: 500;
    }

    /* Primary Convert Button */
    .stButton > button {
        width: 100% !important;
        background: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #0f172a !important;
        border-radius: 10px !important;
        padding: 14px 24px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15) !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button * {
        color: #ffffff !important;
    }
    .stButton > button:hover {
        background: #1e293b !important;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.25) !important;
    }

    /* Metric Summary Badges */
    .stats-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 20px 0 14px 0;
    }
    .stat-pill-box {
        background: #f8fafc;
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
    .stDownloadButton button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 12px 20px !important;
        width: 100% !important;
    }

    /* Hide default menu and footer while preserving sidebar collapse button */
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SIDEBAR: ALWAYS VISIBLE NAVIGATION & SETTINGS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="brand-header">
        <div class="brand-badge">SC</div>
        <div>
            <div class="brand-name">Stitch Converter</div>
            <div style="font-size: 11px; color: #64748b;">Enterprise Suite</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    app_mode = st.radio(
        "Navigation",
        options=["Convert Files", "Settings & Rules", "Stitch ERP Specs"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    if app_mode == "Convert Files":
        st.markdown("**Quick Status**")
        st.markdown(f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; font-size: 12px;">
            <div style="margin-bottom: 6px;"><b>SMV Column:</b> {saved_cfg.get("smv_column", "auto")}</div>
            <div style="margin-bottom: 6px;"><b>Section:</b> QUALITY CHECK</div>
            <div style="margin-bottom: 6px;"><b>Duplicates:</b> {'Skipping' if saved_cfg.get("skip_duplicates", True) else 'Keeping'}</div>
            <div><b>Mandatory Ops:</b> Active</div>
        </div>
        """, unsafe_allow_html=True)

    elif app_mode == "Settings & Rules":
        st.markdown("### Configuration")
        st.caption("Settings are remembered automatically for this client.")

        smv_col = st.selectbox(
            "SMV / SAM Column Target",
            options=["auto", "Column A", "Column B", "Column C", "Column D", "Column E", "Column F", "Column G", "Column H"],
            index=0 if saved_cfg.get("smv_column") == "auto" else 4,
            help="Choose 'auto' to detect M/C.SMV, SAM, or lock to a specific column index."
        )

        skip_duplicates = st.checkbox(
            "Skip duplicate operations (Keep 1st occurrence)",
            value=saved_cfg.get("skip_duplicates", True)
        )

        st.markdown("---")
        st.markdown("**Mandatory Operations Checklist**")
        st.caption("Default Parameters: Section: QUALITY CHECK | Sewing M/C: SEWING | Mandatory M/C: TABLE")

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
        saved_cfg = current_cfg
        st.success("Preferences saved automatically!")

    else:
        st.markdown("### ERP Specifications")
        st.markdown("""
        - **Total Columns:** 29 Columns
        - **Section:** Always `QUALITY CHECK`
        - **Sewing Machines:** `SEWING`
        - **Mandatory Machines:** `TABLE`
        - **EOL QC Tag:** Tag `A` (place_inspection_table=1)
        - **Line Feeding:** Tag `L` (is_line_feeding=1)
        - **Tagging:** Tag `T` (final row with blank next_*)
        """)

# Always read current configurations
cfg = load_config()

# -------------------------------------------------------------
# MAIN WORKSPACE: CONVERSION STAGE
# -------------------------------------------------------------
if app_mode == "Convert Files":
    st.markdown("""
    <div class="main-title-box">
        <h1 class="main-title">Convert Operation Bulletin to Stitch MES</h1>
        <p class="main-subtitle">Upload your factory technical breakdown spreadsheet to generate standardized ERP-ready files.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Operation Bulletin",
        type=["xlsx", "xls", "csv"],
        help="Upload .xlsx, .xls, or .csv operation bulletins."
    )

    if uploaded_file is not None:
        file_bytes = len(uploaded_file.getvalue())
        size_str = f"{round(file_bytes / 1024, 1)} KB" if file_bytes < 1024*1024 else f"{round(file_bytes / (1024*1024), 2)} MB"
        file_ext = os.path.splitext(uploaded_file.name)[1].upper().replace(".", "")
        style_guess = os.path.splitext(uploaded_file.name)[0]
        if style_guess.startswith("Radnik_OB_"):
            style_guess = style_guess.replace("Radnik_OB_", "")

        # Display Selected File Item Card (Matching Reference Image)
        st.markdown(f"""
        <div class="file-item-card">
            <div class="file-meta-group">
                <div class="file-badge-icon">{file_ext}</div>
                <div>
                    <div class="file-title-text">{uploaded_file.name}</div>
                    <div class="file-size-tag">{size_str} &bull; Ready for conversion</div>
                </div>
            </div>
            <span style="background: #eff6ff; color: #2563eb; font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 9999px;">Pending Convert</span>
        </div>
        """, unsafe_allow_html=True)

        # Style Name Input
        style_name = st.text_input("Style Name / Identifier", value=style_guess)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        convert_clicked = st.button("Convert to Stitch MES Format")

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
                            smv_col=cfg.get("smv_column", "auto"),
                            skip_duplicates=cfg.get("skip_duplicates", True),
                            op_cutting_dispatch=cfg.get("op_cutting_dispatch", True),
                            op_line_feeding=cfg.get("op_line_feeding", True),
                            op_eol_qc=cfg.get("op_eol_qc", True),
                            op_dispatch=cfg.get("op_dispatch", True),
                            op_finishing=cfg.get("op_finishing", True),
                            op_tagging=cfg.get("op_tagging", True),
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

                            # Converted File Item Card with Green Check (Matching Reference Image)
                            st.markdown(f"""
                            <div class="file-item-card" style="border-color: #86efac; background: #f0fdf4;">
                                <div class="file-meta-group">
                                    <div class="file-badge-icon" style="background: #dcfce7; border-color: #bbf7d0; color: #166534;">{file_ext}</div>
                                    <div>
                                        <div class="file-title-text">Stitch_OB_{style_name}.csv</div>
                                        <div class="file-size-tag">{total_rows} sequence rows &bull; {total_sam} mins SAM</div>
                                    </div>
                                </div>
                                <div class="status-converted">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                        <polyline points="20 6 9 17 4 12"></polyline>
                                    </svg>
                                    <span>Converted</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Metric Summary Cards
                            st.markdown(f"""
                            <div class="stats-row">
                                <div class="stat-pill-box">
                                    <div class="stat-pill-num">{total_rows}</div>
                                    <div class="stat-pill-lbl">Sequence Rows</div>
                                </div>
                                <div class="stat-pill-box">
                                    <div class="stat-pill-num">{total_sam}</div>
                                    <div class="stat-pill-lbl">Total SAM (min)</div>
                                </div>
                                <div class="stat-pill-box">
                                    <div class="stat-pill-num">{dup_count}</div>
                                    <div class="stat-pill-lbl">Duplicates Skipped</div>
                                </div>
                                <div class="stat-pill-box">
                                    <div class="stat-pill-num" style="font-size: 15px; margin-top: 5px;">QUALITY CHECK</div>
                                    <div class="stat-pill-lbl">Section Name</div>
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
                                        label="Download Excel Workbook (.xlsx)",
                                        data=f_xlsx.read(),
                                        file_name=f"Stitch_OB_{style_name}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True
                                    )

                            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

                            # Operations Table Preview
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

elif app_mode == "Settings & Rules":
    st.markdown("""
    <div class="main-title-box">
        <h1 class="main-title">Configuration & Rules</h1>
        <p class="main-subtitle">Use the left sidebar to customize column mapping, duplicates, and mandatory operations.</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("Please adjust your settings in the left navigation sidebar. All preferences are remembered automatically.")

else:
    st.markdown("""
    <div class="main-title-box">
        <h1 class="main-title">Stitch ERP Specifications</h1>
        <p class="main-subtitle">Standard compliance rules for Stitch MES Operation Bulletins.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    - **Total Columns:** Exactly 29 Standard Columns
    - **Section Column:** Always set to `QUALITY CHECK`
    - **Sewing Machine Type:** Set to `SEWING`
    - **Mandatory Machine Type:** Set to `TABLE`
    - **Cutting Dispatch:** Tag `C`
    - **Line Feeding:** Tag `L` (`is_line_feeding_operation = 1`)
    - **EOL QC:** Tag `A` (`place_inspection_table = 1`)
    - **Dispatch:** Tag `D`
    - **Finishing:** Tag `F`
    - **Tagging:** Tag `T` (Final row with blank next_style_operation fields)
    """)
