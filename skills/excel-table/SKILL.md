---
name: excel-table
description: Create a styled Excel (.xlsx) table in a consistent house style — wrapped cells with auto-fitted row heights (no truncation), a navy header, category/group colour-coding with a legend, thin borders, bold key column, and frozen header/left columns. Use whenever asked to produce, export, or convert data into an Excel/xlsx table or spreadsheet.
---

# excel-table

Produce `.xlsx` tables in a consistent house style. Use the bundled helper — don't hand-roll openpyxl styling each time.

## Preferred style (always apply)
Full house-style rules (header colour, row heights, colour-coding, merging, column widths, etc.)
live in `excel-table-style.md` (next to this file) — that is the single source of truth. Read it
before styling a table; don't restate the rules here.

## How to use
```python
import os, sys
sys.path.insert(0, os.path.join(os.environ["CLAUDE_PLUGIN_ROOT"], "skills/excel-table/scripts"))
from style_excel import write_styled_table

columns = [
  {"key": "name",   "header": "Name",   "width": 20},
  {"key": "bucket", "header": "Bucket", "width": 6, "center": True},
  {"key": "detail", "header": "Detail", "width": 50},
]
rows = [{"name": "...", "bucket": "A", "detail": "long text..."}, ...]
write_styled_table(
    "/path/out.xlsx", columns, rows,
    group_col="name",        # each distinct name gets its own colour band (palette auto-assigned)
    freeze_cols=2,
)
```
`columns` width is in Excel char units. Omit `group_palette` to auto-colour per distinct `group_col`
value; pass one (`{value: hex_no_hash}`) only to fix specific colours. `legend` is optional
`[(label, desc)]` (label colour pulled from the palette).

## Notes
- Requires `openpyxl` — not preinstalled on a stock `python3`. Install with `pip install -r requirements.txt` from the plugin repo root (pins a verified-working version).
- The sheet may still be wide for content-rich tables — that's expected; the priority is **no truncation** (wrap + fitted heights), with frozen columns for orientation. If the user wants a one-screen view, offer to split heavy text columns onto a second tab and keep tab 1 compact.
