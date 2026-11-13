import sys
import os
import re
import json
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input_radnik_ob")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_stitch_ob")
CONFIG_PATH = os.path.join(BASE_DIR, "converter_config.json")

# 29 Stitch MES Standard OB Specification Columns
STITCH_OB_COLUMNS = [
    "sort_order", "part", "operation", "section", "rate", "sam", "machine_type",
    "special_guide_attachment", "no_of_machines", "no_of_operators", "grade",
    "place_inspection_table", "critical_operation", "tag", "operation_end_date",
    "notes", "skip_previous_child_order_level_production_tracking",
    "child_order_level_production_tracking", "skip_child_order_level_quantity_validation",
    "auto_transfer_to_next_operation", "allow_multiple_pass_item", "allow_multiple_alter_item",
    "allow_multiple_reject_item", "is_line_feeding_operation",
    "next_style_operation_item_operation", "next_style_operation_item_part",
    "next_style_operation_item_section", "is_qva", "escalation_hours"
]

DEFAULT_CONFIG = {
    "smv_column": "auto",
    "skip_duplicates": True,
    "op_cutting_dispatch": True,
    "op_line_feeding": True,
    "op_eol_qc": True,
    "op_dispatch": True,
    "op_finishing": True,
    "op_tagging": True
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

def parse_raw_dataframe(file_path):
    """
    Reads an Excel or CSV file and detects:
    1. Metadata header (e.g. style name if in row 0..8)
    2. The actual table header row (containing OPERATION, SMV, M/C, etc.)
    3. The data rows.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df_raw = pd.read_csv(file_path, header=None)
    else:
        df_raw = None
        engines = ["calamine", "xlrd", None] if ext == ".xls" else ["openpyxl", "calamine", None]
        last_err = None
        for eng in engines:
            try:
                if eng:
                    df_raw = pd.read_excel(file_path, header=None, engine=eng)
                else:
                    df_raw = pd.read_excel(file_path, header=None)
                break
            except Exception as e:
                last_err = e
        if df_raw is None:
            raise last_err

    extracted_style = ""
    header_idx = None

    # Search top 25 rows for table headers & metadata
    for i in range(min(25, len(df_raw))):
        row_vals = [str(x).strip() for x in df_raw.iloc[i].values if pd.notna(x)]
        row_str_upper = [x.upper() for x in row_vals]

        # Check for style name in metadata rows
        if not extracted_style:
            for j, val in enumerate(row_str_upper):
                if "STYLE" in val and ":" in val:
                    parts = row_vals[j].split(":", 1)
                    if len(parts) > 1 and parts[1].strip():
                        extracted_style = parts[1].strip()
                elif val == "STYLE" and j + 1 < len(row_vals):
                    extracted_style = str(row_vals[j + 1]).strip()

        # Check if this row is the table header
        is_op_hdr = any(re.search(r'\b(OPERATION|OP/CO|OP\s*NAME|DESCRIPTION)\b', s) for s in row_str_upper)
        is_smv_or_mc = any(re.search(r'\b(SMV|SAM|M/C|MACHINE|ATTACHMENT)\b', s) for s in row_str_upper)
        if is_op_hdr and (is_smv_or_mc or len(row_vals) >= 4):
            header_idx = i
            break

    if header_idx is None:
        header_idx = 0

    headers = [str(x).strip() for x in df_raw.iloc[header_idx].values]
    data_df = df_raw.iloc[header_idx + 1:].copy().reset_index(drop=True)
    data_df.columns = headers

    return data_df, headers, extracted_style

def convert_single_ob(file_path, style_name, output_folder, smv_col="auto",
                      skip_duplicates=True,
                      op_cutting_dispatch=True,
                      op_line_feeding=True,
                      op_eol_qc=True,
                      op_dispatch=True,
                      op_finishing=True,
                      op_tagging=True,
                      log_func=print):
    """
    Converts a single raw Radnik OB spreadsheet into Stitch MES format.
    - Section is always 'QUALITY CHECK'.
    - Sewing operations machine type is 'SEWING'.
    - Mandatory operations machine type is 'TABLE'.
    - Skips duplicate operations if enabled.
    - Halts extraction immediately upon encountering 'TOTAL' row.
    - Supports individual checkboxes for each mandatory operation.
    """
    log_func(f"Reading file: {file_path} (Style: '{style_name}')...")

    data_df, headers, detected_style = parse_raw_dataframe(file_path)
    if not style_name and detected_style:
        style_name = detected_style
        log_func(f"  ℹ️ Auto-detected Style Name from sheet: '{style_name}'")

    # Resolve Column Mappings
    # 1. Operation Column (Priority: OPERATION or OP NAME over OP/CO code)
    op_col = None
    for priority_keys in [
        ["OPERATION NAME", "OP NAME", "OPERATION DESCRIPTION", "OPERATION"],
        ["DESCRIPTION", "OP/CO", "OP CO"]
    ]:
        for col in headers:
            c_up = col.upper()
            if any(k == c_up or (k in c_up and "NEEDLE" not in c_up) for k in priority_keys):
                op_col = col
                break
        if op_col:
            break
    if not op_col:
        op_col = headers[2] if len(headers) > 2 else headers[0]

    # 2. SMV Column
    actual_smv_col = None
    if smv_col and smv_col != "auto":
        smv_col_clean = smv_col.strip().upper()
        col_letter_match = re.match(r'^(?:COLUMN\s+)?([A-Z])$', smv_col_clean)
        if col_letter_match:
            col_letter = col_letter_match.group(1)
            col_idx = ord(col_letter) - ord('A')
            if col_idx < len(headers):
                actual_smv_col = headers[col_idx]
        elif smv_col in headers:
            actual_smv_col = smv_col

    if not actual_smv_col:
        for keyword in ["M/C.SMV", "MC.SMV", "MC SMV", "M/C SMV", "MACHINE SMV", "MACHINE SAM", "SAM", "SMV", "M/C SAM", "MC SAM"]:
            for col in headers:
                if keyword in col.upper():
                    actual_smv_col = col
                    break
            if actual_smv_col:
                break

    if not actual_smv_col:
        for col in headers:
            if "SMV" in col.upper() or "SAM" in col.upper():
                actual_smv_col = col
                break

    # 3. Machine Type Column (for informational header check)
    mc_col = None
    for col in headers:
        c_up = col.upper()
        if any(k in c_up for k in ["M/C TYPE", "MC TYPE", "MACHINE TYPE", "MACHINE", "M/C"]):
            mc_col = col
            break

    # 4. Attachment Column
    att_col = None
    for col in headers:
        c_up = col.upper()
        if any(k in c_up for k in ["ATTACHMENT", "SPECIAL GUIDE", "GUIDE", "ATTACH"]):
            att_col = col
            break

    log_func(f"  Columns Mapped -> Operation: '{op_col}', SMV/SAM: '{actual_smv_col}'")

    raw_operations = []
    seen_ops = set()
    skipped_headers = []
    skipped_duplicates = []

    for idx, row in data_df.iterrows():
        # Check if operations have finished (TOTAL / TOTAL SAM row)
        row_vals_upper = [str(x).strip().upper() for x in row.values if pd.notna(x)]
        if any(re.match(r'^TOTAL\b', v) for v in row_vals_upper[:4]):
            log_func(f"  🛑 Reached end of operations at sheet row {idx+1} ('TOTAL' detected). Ignoring footer summary rows.")
            break

        op_val = str(row.get(op_col, "")).strip()
        if not op_val or op_val.lower() == "nan":
            continue

        if re.match(r'^TOTAL\b', op_val.upper()):
            log_func(f"  🛑 Reached end of operations at sheet row {idx+1} ('TOTAL' in operation). Ignoring footer summary rows.")
            break

        # Parse numeric SAM
        sam_val = None
        if actual_smv_col:
            raw_sam = row.get(actual_smv_col)
            try:
                f_val = float(raw_sam)
                if not pd.isna(f_val):
                    sam_val = f_val
            except (ValueError, TypeError):
                sam_val = None

        mc_val = str(row.get(mc_col, "")).strip() if mc_col else ""
        if mc_val.lower() == "nan":
            mc_val = ""

        att_val = str(row.get(att_col, "")).strip() if att_col else ""
        if att_val.lower() == "nan":
            att_val = ""

        # Section is always QUALITY CHECK as specified
        sec_val = "QUALITY CHECK"

        # Section Header Filtering:
        # If SAM is missing/NaN/0 and Machine is empty, it is an informational header
        if (sam_val is None or sam_val == 0.0) and not mc_val:
            skipped_headers.append(op_val)
            continue

        # Duplicate Operation Check:
        norm_op = " ".join(op_val.upper().split())
        if skip_duplicates and (norm_op in seen_ops):
            skipped_duplicates.append(op_val)
            continue
        seen_ops.add(norm_op)

        # Sewing operation machine type is always SEWING as specified
        raw_operations.append({
            "operation": op_val,
            "section": sec_val,
            "sam": sam_val if sam_val is not None else 0.0,
            "machine_type": "SEWING",
            "special_guide_attachment": att_val,
            "tag": "A",
            "is_line_feeding_operation": 0,
            "place_inspection_table": 0
        })

    if skipped_headers:
        log_func(f"  ℹ️ Filtered out {len(skipped_headers)} non-operational section headers (e.g. {skipped_headers[:3]})")
    if skipped_duplicates:
        log_func(f"  ⚠️ Skipped {len(skipped_duplicates)} duplicate operation(s): {skipped_duplicates}")
    log_func(f"  ✅ Extracted {len(raw_operations)} valid sewing operations.")

    chain_items = []

    # 1. Mandatory Start Operations (Machine: TABLE, Section: QUALITY CHECK)
    if op_cutting_dispatch:
        chain_items.append({
            "operation": "CUTTING DISPATCH",
            "part": "WHOLE GARMENT",
            "section": "QUALITY CHECK",
            "rate": 0.0,
            "sam": 0.0,
            "machine_type": "TABLE",
            "special_guide_attachment": "",
            "tag": "C",
            "is_line_feeding_operation": 0,
            "place_inspection_table": 0
        })

    if op_line_feeding:
        chain_items.append({
            "operation": "LINE FEEDING",
            "part": "WHOLE GARMENT",
            "section": "QUALITY CHECK",
            "rate": 0.0,
            "sam": 0.0,
            "machine_type": "TABLE",
            "special_guide_attachment": "",
            "tag": "L",
            "is_line_feeding_operation": 1,
            "place_inspection_table": 0
        })

    # 2. Main Sewing Operations (Machine: SEWING, Section: QUALITY CHECK, Tag: A)
    for item in raw_operations:
        chain_items.append({
            "operation": item["operation"],
            "part": "WHOLE GARMENT",
            "section": "QUALITY CHECK",
            "rate": 0.0,
            "sam": item["sam"],
            "machine_type": "SEWING",
            "special_guide_attachment": item["special_guide_attachment"],
            "tag": "A",
            "is_line_feeding_operation": 0,
            "place_inspection_table": 0
        })

    # 3. Mandatory End Operations (Machine: TABLE, Section: QUALITY CHECK)
    if op_eol_qc:
        chain_items.append({
            "operation": "EOL QC",
            "part": "WHOLE GARMENT",
            "section": "QUALITY CHECK",
            "rate": 0.0,
            "sam": 0.0,
            "machine_type": "TABLE",
            "special_guide_attachment": "",
            "tag": "A",  # EOL QC explicitly gets Tag 'A'
            "is_line_feeding_operation": 0,
            "place_inspection_table": 1
        })

    if op_dispatch:
        chain_items.append({
            "operation": "DISPATCH",
            "part": "WHOLE GARMENT",
            "section": "QUALITY CHECK",
            "rate": 0.0,
            "sam": 0.0,
            "machine_type": "TABLE",
            "special_guide_attachment": "",
            "tag": "D",
            "is_line_feeding_operation": 0,
            "place_inspection_table": 0
        })

    if op_finishing:
        chain_items.append({
            "operation": "FINISHING",
            "part": "WHOLE GARMENT",
            "section": "QUALITY CHECK",
            "rate": 0.0,
            "sam": 0.0,
            "machine_type": "TABLE",
            "special_guide_attachment": "",
            "tag": "F",
            "is_line_feeding_operation": 0,
            "place_inspection_table": 0
        })

    if op_tagging:
        chain_items.append({
            "operation": "TAGGING",
            "part": "WHOLE GARMENT",
            "section": "QUALITY CHECK",
            "rate": 0.0,
            "sam": 0.0,
            "machine_type": "TABLE",
            "special_guide_attachment": "",
            "tag": "T",
            "is_line_feeding_operation": 0,
            "place_inspection_table": 0
        })

    # Build Final Sequential Rows with Linked Chain
    converted_rows = []
    total_chain = len(chain_items)

    for i, item in enumerate(chain_items):
        sort_order = i + 1

        if i < total_chain - 1:
            next_op = chain_items[i + 1]["operation"]
            next_part = chain_items[i + 1]["part"]
            next_sec = "QUALITY CHECK"
        else:
            # Final operation has empty next operation fields
            next_op = ""
            next_part = ""
            next_sec = ""

        c_row = {
            "sort_order": sort_order,
            "part": item["part"],
            "operation": item["operation"],
            "section": "QUALITY CHECK",
            "rate": item.get("rate", 0.0),
            "sam": item.get("sam", 0.0),
            "machine_type": item["machine_type"],
            "special_guide_attachment": item.get("special_guide_attachment", ""),
            "no_of_machines": 1.0,
            "no_of_operators": 1.0,
            "grade": "",
            "place_inspection_table": item["place_inspection_table"],
            "critical_operation": 0,
            "tag": item["tag"],
            "operation_end_date": "",
            "notes": "",
            "skip_previous_child_order_level_production_tracking": 0,
            "child_order_level_production_tracking": "",
            "skip_child_order_level_quantity_validation": 0,
            "auto_transfer_to_next_operation": 0,
            "allow_multiple_pass_item": 0,
            "allow_multiple_alter_item": 0,
            "allow_multiple_reject_item": 0,
            "is_line_feeding_operation": item["is_line_feeding_operation"],
            "next_style_operation_item_operation": next_op,
            "next_style_operation_item_part": next_part,
            "next_style_operation_item_section": next_sec,
            "is_qva": 0,
            "escalation_hours": 0
        }
        converted_rows.append(c_row)

    out_df = pd.DataFrame(converted_rows, columns=STITCH_OB_COLUMNS)

    os.makedirs(output_folder, exist_ok=True)
    out_xlsx_path = os.path.join(output_folder, f"Stitch_OB_{style_name}.xlsx")
    out_csv_path = os.path.join(output_folder, f"Stitch_OB_{style_name}.csv")

    try:
        out_df.to_excel(out_xlsx_path, index=False)
        out_df.to_csv(out_csv_path, index=False)
    except PermissionError:
        out_xlsx_path = os.path.join(output_folder, f"Stitch_OB_{style_name}_latest.xlsx")
        out_csv_path = os.path.join(output_folder, f"Stitch_OB_{style_name}_latest.csv")
        out_df.to_excel(out_xlsx_path, index=False)
        out_df.to_csv(out_csv_path, index=False)

    log_func(f"✅ Successfully Converted OB for Style '{style_name}' ({len(out_df)} sequence rows):")
    log_func(f"   Excel File: {out_xlsx_path}")
    log_func(f"   CSV File:   {out_csv_path}")

    return out_xlsx_path

def convert_all(input_folder=INPUT_DIR, output_folder=OUTPUT_DIR, smv_col="auto",
                skip_duplicates=True,
                op_cutting_dispatch=True,
                op_line_feeding=True,
                op_eol_qc=True,
                op_dispatch=True,
                op_finishing=True,
                op_tagging=True,
                log_func=print):
    log_func("===============================================================")
    log_func(" 🧵 RADNIK OB TO STITCH OB CONVERTER ENGINE ")
    log_func("===============================================================")
    log_func(f"[*] Master Input Folder:  {input_folder}")
    log_func(f"[*] Master Output Folder: {output_folder}")
    log_func("---------------------------------------------------------------\n")

    if not os.path.exists(input_folder):
        log_func("Input directory does not exist.")
        return []

    os.makedirs(output_folder, exist_ok=True)
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.xlsx', '.xls', '.csv'))]
    if not files:
        log_func("No spreadsheet or CSV files found in input directory.")
        return []

    converted = []
    for f in files:
        full_p = os.path.join(input_folder, f)
        style = os.path.splitext(f)[0]
        if style.startswith("Radnik_OB_"):
            style = style.replace("Radnik_OB_", "")
        try:
            res = convert_single_ob(full_p, style, output_folder, smv_col=smv_col,
                                    skip_duplicates=skip_duplicates,
                                    op_cutting_dispatch=op_cutting_dispatch,
                                    op_line_feeding=op_line_feeding,
                                    op_eol_qc=op_eol_qc,
                                    op_dispatch=op_dispatch,
                                    op_finishing=op_finishing,
                                    op_tagging=op_tagging,
                                    log_func=log_func)
            converted.append(res)
        except Exception as e:
            log_func(f"❌ Error converting '{f}': {e}")

    log_func(f"\n🎉 Successfully processed {len(converted)} OB files.")
    return converted

if __name__ == "__main__":
    convert_all()
