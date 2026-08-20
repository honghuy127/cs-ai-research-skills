# Figure Plan

Playbook: [../references/figures-and-diagrams.md](../references/figures-and-diagrams.md)

Copy one block per figure. Keep plans next to the manuscript or index them from the project dossier.

## Figure identity

- Figure ID: FIG-
- Supported claim IDs:
- Manuscript placement (section, column or page width, appendix, or slides):
- Role (method schematic, system architecture, protocol or pipeline flow, data figure, qualitative example, or teaser):

## Content contract

- What the figure must convey in one sentence:
- Content source (method description, named assumptions, code paths, run or analysis artifact IDs):
- Values shown are (traceable results, illustrative only, not applicable):
- Exact labels and terminology taken from:
- What must be exact vs what may be approximate:
- Third-party content, license, and required attribution:

## Style contract

- Information hierarchy: primary flow, secondary annotations, and what to omit:
- Connector meaning (source, target, direction, fan-in or fan-out; data, control, gradient, or reference flow):
- Palette (hex codes) and colorblind-safe check:
- Font family and minimum size at final width:
- Stroke widths, corner radii, arrow style, and container style:
- Consistency reference (existing figure ID or style file):

## Authoring

- Editable source path and canonical tool (draw.io, TikZ/pgfplots, plotting script):
- Derived export format(s) (PDF, PNG, SVG):
- Generation or export command:
- Output paths:
- Input artifact IDs and hashes (data figures only):
- Code version or commit:

## Verification

- Structural check command and result (for example `python3 scripts/validate_drawio.py figures/fig.drawio`):
- Render inspected at target size (how, by whom, date):
- Defects found and fixed:
- Caption draft:
- Current venue figure rules source and access date:
- Figure gate verdict (PASS, CONDITIONAL, FAIL, BLOCKED, or NOT_ASSESSED):
- Uncertainty, deviations, waivers, and next decisive action:

## Status

- Lifecycle state (NOT_ASSESSED, PROPOSED, PLANNED, IMPLEMENTED, SMOKE_TESTED, PILOT_ONLY, EXECUTED, ANALYZED, VERIFIED, REPORTED, BLOCKED, or DROPPED):
- Explicit clean status or outstanding defects, blockers, and owner:
