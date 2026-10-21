# Excel Table Style

Single source of truth for the `.xlsx` house style. `SKILL.md`
(and any other skill producing Excel output) points here instead of restating these rules —
if the style changes, edit only this file.

When generating any Excel/.xlsx table, produce it in the house style — use the
`excel-table` skill/helper (`write_styled_table(...)`), don't hand-roll openpyxl styling.

**The style:**
- Header row: navy `#1F3864` fill, white bold, centred, wrapped, frozen.
- Every cell: text wrap ON, top-aligned, thin grey borders.
- Row heights COMPUTED to fit wrapped content — every cell fully visible, never truncated.
- Colour-coding: one distinct colour per distinct value of the grouping column, plus a Legend sheet.
  Group by the meaningful row entity (e.g. each proposed sub-prompt / item name) so each item's rows
  share a colour band — not a coarse category like bucket/status, unless asked (colour per sub-prompt,
  e.g. `shared/coverage-content-metric` ≠ `shared/coverage-core-rules`). Pass `group_col` alone and a
  per-value palette is auto-assigned.
- First/key column bold; optionally freeze the leftmost N columns so they stay visible scrolling right.
- De-duplicate within row-groups: when rows group by an entity (`merge_by=`), vertically merge any
  column whose value is identical across the group (repeated text → one merged cell); per-row columns
  (e.g. source file, verbatim text) stay separate.
- Explicit per-column widths — and if the user has already tuned widths in an existing file,
  read them back (`load_workbook` → `column_dimensions[L].width`) and reuse them, don't overwrite.
