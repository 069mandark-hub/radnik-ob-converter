# Radnik OB to Stitch MES Online Converter

Converts raw Radnik Operation Bulletins (`.xlsx`, `.xls`, `.csv`) into the official 29-column Stitch MES format.

### Features
- Section set to **QUALITY CHECK**
- Sewing operations machine type set to **SEWING**
- Mandatory operations machine type set to **TABLE**
- Auto-stops extraction at **TOTAL** row (ignoring summary tables)
- Deduplication of repeated operations
- Individual checkboxes for mandatory operations (Cutting Dispatch, Line Feeding, EOL QC, Dispatch, Finishing, Tagging)
