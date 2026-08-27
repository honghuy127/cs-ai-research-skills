# Figure Plan

Playbook: [../references/figures-and-diagrams.md](../references/figures-and-diagrams.md)

## Figure identity

- Figure ID: FIG-001
- Supported claim IDs: README claims "a lean SKILL.md router loads focused reference playbooks on demand", "truth states, not vibes", "decisive gates", and the repository layout table
- Manuscript placement (section, column or page width, appendix, or slides): README.md, full text width, rendered on GitHub
- Role (method schematic, system architecture, protocol or pipeline flow, data figure, qualitative example, or teaser): system architecture and workflow schematic

## Content contract

- What the figure must convey in one sentence: a host agent routes a research-shaped task through SKILL.md to load only the relevant phase playbooks, works under decisive gates and explicit truth states, and records provenance in the project .research/ dossier using scripts/ before shipping traceable deliverables.
- Content source (method description, named assumptions, code paths, run or analysis artifact IDs): SKILL.md routing table and gates list; README.md repository layout and dossier listing; scripts/ directory contents
- Values shown are (traceable results, illustrative only, not applicable): not applicable (schematic; counts such as "19 playbooks", "19 gates" match the current SKILL.md routing table and quality-gates list as of 2026-08-27)
- Exact labels and terminology taken from: SKILL.md section headings and gate verdict vocabulary (PASS, CONDITIONAL, FAIL, BLOCKED, NOT_ASSESSED), dossier file names from README.md
- What must be exact vs what may be approximate: exact: component names, gate verdicts, truth-state sequence, dossier file names; approximate: box spacing, edge routing, grouping decoration
- Third-party content, license, and required attribution: none; all content is original to this repository (MIT)

## Style contract

- Information hierarchy: primary flow runs left to right (task -> router -> agent loop -> deliverables); dossier and scripts sit to the right as the provenance backbone; secondary dashed edges denote read/reference flows
- Connector meaning (source, target, direction, fan-in or fan-out; data, control, gradient, or reference flow): solid arrows are control or artifact flow; dashed arrows are read or reference flow; the curved arrow from the gate back to execution is a revision loop; every edge carries a label stating its semantic
- Palette (hex codes) and colorblind-safe check: task/system #F5F5F5 stroke #666666; skill package #DAE8FC stroke #6C8EBF; agent loop #D5E8D4 stroke #82B366; gates and verdicts #FFE6CC stroke #D79B00; neutrals #FFFFFF. Categories are also distinguished by container titles and edge labels, never by color alone.
- Font family and minimum size at final width: Helvetica; container titles 13 bold, box labels 12, edge labels 10; minimum 10
- Stroke widths, corner radii, arrow style, and container style: 1.5px strokes, rounded rect arcSize 8, orthogonal edge routing with block arrows, containers are rounded rectangles with bold header lines
- Consistency reference (existing figure ID or style file): none; this is the first figure in the repository and sets the contract

## Authoring

- Editable source path and canonical tool (draw.io, TikZ/pgfplots, plotting script): figures/fig-001-skill-architecture.drawio, draw.io XML authored by hand
- Derived export format(s) (PDF, PNG, SVG): SVG (README) and PNG (review raster)
- Generation or export command: `python3 scripts/render_drawio.py figures/fig-001-skill-architecture.drawio --scale 2` (Playwright plus the diagrams.net static viewer as a local page; draw.io desktop CLI is not installed on the authoring machine)
- Output paths: figures/fig-001-skill-architecture.svg, figures/fig-001-skill-architecture.png
- Input artifact IDs and hashes (data figures only): not applicable
- Code version or commit: working tree at authoring date 2026-08-27

## Verification

- Structural check command and result (for example `python3 scripts/validate_drawio.py figures/fig.drawio`): `python3 scripts/validate_drawio.py figures/fig-001-skill-architecture.drawio --strict --min-font-size 10` — pass (2026-08-27, rerun after F-1 fix)
- Render inspected at target size (how, by whom, date): PNG and SVG re-render (.svg.check.png) inspected visually by the authoring agent at full page width, 2026-08-27 (initial) and 2026-08-27 (F-1 re-render)
- Defects found and fixed: first render showed an edge crossing the scripts/ box text, an audit-label overlapping the scripts/ title, and two colliding route labels near the gate box; fixed by re-routing the audit edge to originate at scripts/ (exit left), entering scripts/ from the top for the run-recording edge, shortening three labels, and removing one redundant label; second render is clean. Full-repo audit finding F-1 (scripts/ box omitted render_drawio.py) fixed by adding the line and extending the box; re-rendered and re-inspected clean.
- Caption draft: "Skill architecture. SKILL.md routes a task to the smallest complete workflow of phase playbooks; every phase closes at a decisive gate, and provenance lives in the project .research/ dossier maintained with scripts/."
- Current venue figure rules source and access date: not applicable (README on GitHub; no venue constraints). GitHub renders SVG and PNG in Markdown.
- Figure gate verdict (PASS, CONDITIONAL, FAIL, BLOCKED, or NOT_ASSESSED): PASS
- Uncertainty, deviations, waivers, and next decisive action: rendered with the Playwright local-viewer path (scripts/render_drawio.py) because the draw.io desktop CLI is unavailable; the SVG export is reconstructed from the viewer DOM, so if the source is edited, regenerate both exports with the recorded command and re-inspect.

## Status

- Lifecycle state (NOT_ASSESSED, PROPOSED, PLANNED, IMPLEMENTED, SMOKE_TESTED, PILOT_ONLY, EXECUTED, ANALYZED, VERIFIED, REPORTED, BLOCKED, or DROPPED): REPORTED (embedded in README.md)
- Explicit clean status or outstanding defects, blockers, and owner: clean; no outstanding defects; owner: user
