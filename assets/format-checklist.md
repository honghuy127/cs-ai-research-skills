# Format Checklist

Playbook: [../references/paper-formatting.md](../references/paper-formatting.md)

Copy per submission. Complete every line before calling the formatting gate PASS.

## Venue contract

- Venue, track, and cycle:
- Official instruction URLs and access date:
- Template or class and exact version:
- Allowed template modifications:
- Page or word limit and counting rules (main text, references, appendix, checklists):
- File formats and engine constraints:
- Anonymity state and what it removes:
- Figure rules affecting layout (widths, caption placement, subfigures):

## Build

- Compile command (recorded verbatim):
- Engine version and source revision:
- Output PDF and log paths:
- Build directory pruned to submission content only:

## Machine checks

- `check_latex_log.py` command and status:
- Hard errors resolved:
- Undefined references and citations resolved:
- Labels-changed and rerun requests cleared by final stable recompile:
- Overfull boxes resolved or explicitly waived with venue permission:
- `--strict` pass completed for camera-ready:

## Rendered page inspection

- Render command and DPI:
- Page images path:
- Pages inspected (all, or list with triage rule):
- Margins and text block:
- Figure and table placement, captions, and legibility:
- Orphans, column balance, footnotes:
- Headers, footers, page numbers per template:
- Hyperlink targets and colors:
- Anonymity visible on every page:

## Files and metadata

- Page count against limit (observed value):
- `pdffonts` embedding check:
- PDF metadata reviewed (title, author, subject):
- File size within portal limit:
- Source package complete (.bbl, styles, figures) and free of forbidden files:
- Hidden content check (reviewer-response comments, tracked changes, PDF scripts):

## Verdict

- Formatting gate status and evidence paths:
- Waivers granted, owner, and expiry:
- Outstanding defects and owner:
