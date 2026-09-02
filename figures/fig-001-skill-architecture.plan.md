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
- Font family and minimum size at final width: Helvetica for prose, Courier New for code terms (file and directory names, gate verdicts, truth states); container titles 13 bold, box labels 12, edge labels 10; minimum 10. Edge labels on long straight runs sit above the line with no background; labels on short or crossing runs keep a white background.
- Stroke widths, corner radii, arrow style, and container style: 1.5px strokes, rounded rect arcSize 8, orthogonal edge routing with block arrows, containers are rounded rectangles with bold header lines
- Consistency reference (existing figure ID or style file): none; this is the first figure in the repository and sets the contract

## Authoring

- Editable source path and canonical tool (draw.io, TikZ/pgfplots, plotting script): figures/fig-001-skill-architecture.drawio, draw.io XML authored by hand
- Derived export format(s) (PDF, PNG, SVG): SVG (README) and PNG (review raster)
- Generation or export command: `/Applications/draw.io.app/Contents/MacOS/draw.io -x -f svg -e --embed-svg-fonts false -o figures/fig-001-skill-architecture.svg figures/fig-001-skill-architecture.drawio` and the same with `-f png -s 2` for the review raster (draw.io desktop 31.3.2 on the authoring machine as of 2026-09-02; `--embed-svg-fonts false` keeps labels as vector text instead of rasterized embedded images). Fallback: `python3 scripts/render_drawio.py figures/fig-001-skill-architecture.drawio --scale 2` (Playwright plus the diagrams.net static viewer as a local page)
- Output paths: figures/fig-001-skill-architecture.svg, figures/fig-001-skill-architecture.png
- Input artifact IDs and hashes (data figures only): not applicable
- Code version or commit: working tree at authoring date 2026-08-27

## Verification

- Structural check command and result (for example `python3 scripts/validate_drawio.py figures/fig.drawio`): `python3 scripts/validate_drawio.py figures/fig-001-skill-architecture.drawio --strict --min-font-size 10` — pass (2026-08-27, rerun after F-1 fix; rerun 2026-09-02 after F-2 fix; rerun 2026-09-02 after alignment pass)
- Render inspected at target size (how, by whom, date): PNG and SVG re-render (.svg.check.png) inspected visually by the authoring agent at full page width, 2026-08-27 (initial) and 2026-08-27 (F-1 re-render); 2026-09-02 (F-2 re-render); 2026-09-02 native draw.io desktop CLI PNG and SVG exports inspected visually (PNG direct, SVG via Quick Look thumbnail); 2026-09-02 alignment-pass PNG inspected visually
- Defects found and fixed: first render showed an edge crossing the scripts/ box text, an audit-label overlapping the scripts/ title, and two colliding route labels near the gate box; fixed by re-routing the audit edge to originate at scripts/ (exit left), entering scripts/ from the top for the run-recording edge, shortening three labels, and removing one redundant label; second render is clean. Full-repo audit finding F-1 (scripts/ box omitted render_drawio.py) fixed by adding the line and extending the box; re-rendered and re-inspected clean. Finding F-2 (scripts/ box omitted research_contract.py while the README layout table documents it) fixed by adding the line, growing the box upward, and widening the page from 1200 to 1260 so the "audits unresolved markers" label no longer overlaps box text in the narrower gutter; re-rendered and re-inspected clean. Alignment pass: nudged step-classify up 11 and step-load down 4 so the routes and read edges are straight; moved the revise-loop label off the dashed gate edge; tightened the truth-states box to 120 high; trimmed the scripts/ box to bottom-align with both containers at y=620; re-rendered and inspected clean. Review pass 2026-09-02: made the audits edge a straight horizontal run (exit/entry both at 0.75), separated the revise loop exit from the dashed gate edge anchor (0.25 vs 0.5), lifted the routes/read/record-runs/audits labels 10 above their arrows with transparent backgrounds, and set code terms in Courier New; re-rendered and inspected clean. Round 2 (2026-09-02): recentered the "revise, pivot, or stop" label on the loop's vertical segment (it had drifted to the execute box edge after the label-offset pass), moved the audits edge and its label to the Deliverables midline (scripts exit at 0.62 to keep the run horizontal), and dropped the "maintain and check" label toward the dossier end so it no longer neighbors the "record runs; audit traceability" label; re-rendered and inspected clean. Round 3 (2026-09-02): wrapped the five line-crossing labels into two lines (task intent; revise, pivot, or stop; copied and adapted; PASS with traced evidence; maintain and check) so they cover less edge length; re-rendered and inspected clean. Round 4 (2026-09-02): author manually refined the layout in drawio desktop (host=Electron): revise-loop label re-wrapped as "revise, / pivot, / or stop" sitting on the loop corner, audits label wrapped as two lines above the arrowhead, record-runs label wrapped as two lines, edge-label offsets normalized with explicit x geometry. Exports regenerated from the desktop-saved source and inspected clean.
- Caption draft: "Skill architecture. SKILL.md routes a task to the smallest complete workflow of phase playbooks; every phase closes at a decisive gate, and provenance lives in the project .research/ dossier maintained with scripts/."
- Current venue figure rules source and access date: not applicable (README on GitHub; no venue constraints). GitHub renders SVG and PNG in Markdown.
- Figure gate verdict (PASS, CONDITIONAL, FAIL, BLOCKED, or NOT_ASSESSED): PASS
- Uncertainty, deviations, waivers, and next decisive action: exports produced by the draw.io desktop CLI 31.3.2 with the diagram embedded (-e); if the source is edited, regenerate both exports with the recorded commands and re-inspect. The headless render_drawio.py path remains as fallback for machines without the desktop app.

## Status

- Lifecycle state (NOT_ASSESSED, PROPOSED, PLANNED, IMPLEMENTED, SMOKE_TESTED, PILOT_ONLY, EXECUTED, ANALYZED, VERIFIED, REPORTED, BLOCKED, or DROPPED): REPORTED (embedded in README.md)
- Explicit clean status or outstanding defects, blockers, and owner: clean; no outstanding defects; owner: user
