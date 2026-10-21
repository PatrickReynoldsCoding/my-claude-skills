#!/usr/bin/env python3
"""
Write a styled .xlsx table in the team house style.

Preferred style (the house style):
- Header row: navy (#1F3864) fill, white bold, centred, wrapped, frozen.
- Every cell: text wrap ON, top-aligned, thin grey border.
- Row heights COMPUTED to fit wrapped content (nothing truncated).
- Optional category/group colour-coding (light fills) driven by a column's value, + a Legend sheet.
- First column bold (the row key). Optionally freeze the leftmost N columns too.
- Per-column widths are explicit (caller supplies them — respect any the user has tuned).

Reuse: `from style_excel import write_styled_table`.
"""

import math
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HEADER_FILL = "1F3864"
BORDER = Border(*([Side(style="thin", color="D0D0D0")] * 4))
LINE_PT = 14.5          # approx height per wrapped line
MAX_LINES = 40          # cap row height so a huge cell doesn't dominate

# Distinct light fills cycled to give each group value its own colour band.
DEFAULT_PALETTE = ["C6EFCE", "FFF2CC", "FCE4D6", "D9E1F2", "E2EFDA", "FFE699", "DDEBF7", "F8CBAD",
                   "E4DFEC", "DAE8FC", "D5E8D4", "FFE6CC", "E1D5E7", "FCE4EC", "F5F5DC", "DEEAF6"]


def _wrapped_lines(text, width_chars):
    if not text:
        return 1
    total = 0
    for segment in str(text).split("\n"):
        total += max(1, math.ceil(len(segment) / max(width_chars - 1, 1)))
    return total


def write_styled_table(out_path, columns, rows, *, sheet_title="Sheet1",
                       group_col=None, group_palette=None, legend=None,
                       bold_first_col=True, freeze_cols=0, merge_by=None):
    """
    columns: list of dicts {key, header, width, center?(bool), bold?(bool)}
    rows:    list of dicts keyed by column 'key'
    group_col / group_palette: colour each row by row[group_col] -> palette hex
    legend:  list of (label, description) for a Legend sheet (label colour from palette if present)
    freeze_cols: keep this many leftmost columns visible (header row always frozen)
    merge_by:  column key; within each run of consecutive rows sharing that value, vertically MERGE
               any column whose value is identical across the run (de-duplicates repeated cells).
    """
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_title

    # If grouping but no explicit palette, give each distinct group value its own colour band.
    if group_col and not group_palette:
        group_palette = {}
        for row in rows:
            value = str(row.get(group_col, "")).strip()
            if value not in group_palette:
                group_palette[value] = DEFAULT_PALETTE[len(group_palette) % len(DEFAULT_PALETTE)]

    # header
    for i, col in enumerate(columns, 1):
        c = ws.cell(1, i, col["header"])
        c.fill = PatternFill("solid", fgColor=HEADER_FILL)
        c.font = Font(bold=True, color="FFFFFF", size=11)
        c.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
        c.border = BORDER
        ws.column_dimensions[get_column_letter(i)].width = col["width"]
    ws.row_dimensions[1].height = 28
    ws.freeze_panes = f"{get_column_letter(freeze_cols + 1)}2"

    # data
    for r_i, row in enumerate(rows, 2):
        fill = None
        if group_col and group_palette:
            hexcol = group_palette.get(str(row.get(group_col, "")).strip())
            if hexcol:
                fill = PatternFill("solid", fgColor=hexcol)
        max_lines = 1
        for c_i, col in enumerate(columns, 1):
            val = row.get(col["key"], "")
            c = ws.cell(r_i, c_i, val)
            if fill:
                c.fill = fill
            c.border = BORDER
            c.alignment = Alignment(vertical="top", wrap_text=True,
                                    horizontal="center" if col.get("center") else "left")
            if (c_i == 1 and bold_first_col) or col.get("bold"):
                c.font = Font(bold=True)
            max_lines = max(max_lines, _wrapped_lines(val, col["width"]))
        ws.row_dimensions[r_i].height = min(max_lines, MAX_LINES) * LINE_PT + 4

    # Within each run of consecutive rows sharing merge_by, merge any column that's identical across it.
    if merge_by:
        start = 0
        keyvals = [str(r.get(merge_by, "")) for r in rows]
        while start < len(rows):
            end = start
            while end + 1 < len(rows) and keyvals[end + 1] == keyvals[start]:
                end += 1
            if end > start:
                for c_i, col in enumerate(columns, 1):
                    distinct = {str(rows[r].get(col["key"], "")) for r in range(start, end + 1)}
                    if len(distinct) == 1:
                        ws.merge_cells(start_row=start + 2, start_column=c_i,
                                       end_row=end + 2, end_column=c_i)
                        ws.cell(start + 2, c_i).alignment = Alignment(
                            vertical="center", wrap_text=True,
                            horizontal="center" if col.get("center") else "left")
            start = end + 1

    if legend:
        lg = wb.create_sheet("Legend")
        lg.column_dimensions["A"].width = 16
        lg.column_dimensions["B"].width = 72
        lg.cell(1, 1, "Key").font = Font(bold=True)
        lg.cell(1, 2, "Meaning").font = Font(bold=True)
        for i, (label, desc) in enumerate(legend, 2):
            cell = lg.cell(i, 1, label)
            if group_palette and group_palette.get(label):
                cell.fill = PatternFill("solid", fgColor=group_palette[label])
            cell.alignment = Alignment(horizontal="center")
            lg.cell(i, 2, desc)

    wb.save(out_path)
    return out_path
