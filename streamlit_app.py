import os
import io
import tempfile
import pandas as pd
import streamlit as st
from convert_ob import convert_single_ob

st.set_page_config(
    page_title="Radnik OB to Stitch MES Converter",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 Radnik OB to Stitch MES Online Converter")
st.markdown("Upload your raw Radnik Operation Bulletin (`.xlsx`, `.xls`, `.csv`) to convert it into the standard 29-column Stitch MES format.")

# Sidebar Settings
st.sidebar.header("⚙️ Configuration & Parser Rules")

smv_col = st.sidebar.selectbox(
    "SMV / SAM Column",
    options=["auto", "Column A", "Column B", "Column C", "Column D", "Column E", "Column F", "Column G", "Column H"],
    index=0,
    help="Select 'auto' to automatically detect M/C.SMV, SAM, SMV, or lock to a specific column."
)

skip_duplicates = st.sidebar.checkbox(
    "Skip duplicate operations (Keep 1st occurrence)",
    value=True,
    help="Skips repeated operations after their first occurrence."
)

st.sidebar.markdown("---")
st.sidebar.subheader("Mandatory Operations")
st.sidebar.caption("Machine: **TABLE** | Section: **QUALITY CHECK**")

op_c = st.sidebar.checkbox("CUTTING DISPATCH (Tag: C)", value=True)
op_l = st.sidebar.checkbox("LINE FEEDING (Tag: L | is_line_feeding=1)", value=True)
op_eol = st.sidebar.checkbox("EOL QC (Tag: A | place_inspection_table=1)", value=True)
op_d = st.sidebar.checkbox("DISPATCH (Tag: D)", value=True)
op_f = st.sidebar.checkbox("FINISHING (Tag: F)", value=True)
op_t = st.sidebar.checkbox("TAGGING (Tag: T | Final op)", value=True)

# Main File Uploader
uploaded_file = st.file_uploader(
    "Choose a Radnik OB file (.xlsx, .xls, .csv)",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is not None:
    style_guess = os.path.splitext(uploaded_file.name)[0]
    if style_guess.startswith("Radnik_OB_"):
        style_guess = style_guess.replace("Radnik_OB_", "")

    style_name = st.text_input("Style Name / Code", value=style_guess)

    if st.button("▶ Convert OB to Stitch MES", type="primary"):
        with st.spinner("Processing operation bulletin..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                # Save uploaded file to temp
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

                        st.success(f"✅ Successfully converted '{style_name}'! Total Sequence Rows: {len(df_res)}")

                        # Download Buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            with open(csv_path, "rb") as f_csv:
                                st.download_button(
                                    label="📥 Download Stitch OB CSV (Ready for Upload)",
                                    data=f_csv.read(),
                                    file_name=f"Stitch_OB_{style_name}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                        with col2:
                            with open(xlsx_path, "rb") as f_xlsx:
                                st.download_button(
                                    label="📥 Download Stitch OB Excel (.xlsx)",
                                    data=f_xlsx.read(),
                                    file_name=f"Stitch_OB_{style_name}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )

                        # Preview Table
                        st.subheader("📋 Converted Operations Preview")
                        st.dataframe(
                            df_res[["sort_order", "operation", "section", "machine_type", "tag", "sam", "is_line_feeding_operation", "place_inspection_table", "next_style_operation_item_operation"]],
                            use_container_width=True
                        )

                        # Conversion Logs
                        with st.expander("🔍 View Conversion Logs"):
                            st.code("\n".join(logs))

                    else:
                        st.error("Failed to generate output files.")

                except Exception as ex:
                    st.error(f"Error during conversion: {ex}")
                    if logs:
                        st.code("\n".join(logs))
