# Figures and Diagrams

## Contents

1. Establish the figure contract
2. Select the figure type and authoring tool
3. Plan the figure and its style contract
4. Author schematic diagrams as draw.io sources
5. Author LaTeX-native figures
6. Generate data figures from traceable analysis
7. Validate diagram sources before rendering
8. Render, inspect, and iterate
9. Meet publication standards
10. Record provenance and pass the figure gate

## 1. Establish the figure contract

Read the claim map, manuscript draft, venue constraints, and existing figures before drawing anything. Page, size, and package-level constraints belong to the recorded contract in paper-formatting.md. Build or extend the claim map per [paper-writing.md](paper-writing.md), section "Build a claim-led paper plan", so placement follows manuscript claims. A figure is a manuscript deliverable, not decoration: every figure must answer a named question or support a named claim.
For each requested figure, record:

- A stable figure ID such as FIG-001 and the claim IDs it supports.
- The role: method schematic, system architecture, protocol or pipeline flow, data figure, qualitative example, or teaser.
- The content source: method description, code, run artifacts, analysis outputs, or named assumptions. Label schematic or illustrative content as such; a schematic may not present invented measurements, and a data figure may not use values that cannot be traced to an analysis artifact.
- The editable source format and the derived export formats.
- The target placement: column width, page width, appendix, or slides, loading [presentation-slides.md](presentation-slides.md) for deck work.

Treat the editable source (`.drawio`, `.tex`, plotting script) as the primary artifact. Exports (PDF, PNG, SVG) are derived artifacts regenerated from the source. Never hand-edit an export or ship an export whose source is missing or out of date.

Do not infer authorization to publish, upload to web-based drawing services, or embed third-party logos and icons. Verify the license and permission for any reused or adapted external figure, and mark required attribution in the figure plan.

## 2. Select the figure type and authoring tool

Choose the smallest tool that the figure type, venue, and revision workflow support. Do not adopt a toolchain because it is available if the deliverable does not need it.

| Figure type | Recommended source | Use when |
|---|---|---|
| Method schematic, architecture, pipeline, protocol | draw.io (`.drawio` XML) | Editable vector diagram with boxes, arrows, containers, and icons; co-authors without LaTeX need to edit it |
| Tight LaTeX integration, math-heavy notation | TikZ with the `tikz` or `pgfplots` packages | Figures must inherit document fonts or live inside `figure` environments as code |
| Quantitative results | Plotting script (matplotlib, seaborn, ggplot2, R base, or the project's existing stack) | Values derive from analysis outputs; reuse the analysis codebase's conventions |
| Quick draft for discussion only | Mermaid or a whiteboard photo | The figure is provisional and will be redrawn before submission |
| Annotated screenshots or interface examples | Image with overlay annotations in draw.io | The artifact under study is genuinely a screenshot |

Routing rules:

- Load `analysis-and-statistics.md` section "Build honest tables and figures" for any figure that encodes measured values. This reference does not relax those rules.
- Prefer draw.io when the authors must iteratively edit layout and the venue accepts vector export. Prefer TikZ when the venue template or the authors' workflow is LaTeX-first. Keep both sources synchronized if both exist; designate one as canonical.
- Do not replace a required editable source with a raster image. Use raster content only as a reference input or with explicit approval.

## 3. Plan the figure and its style contract

Use `assets/figure-plan.md` as the planning template. Before authoring, decide:

- The single message the figure must convey and what a reader should conclude from the caption alone.
- The information hierarchy: primary flow, secondary annotations, and what to omit.
- Exact terminology from the manuscript for every label. Do not paraphrase method components into generic names while drafting.
- A style contract shared by all figures in the paper: palette with hex codes, font family and minimum size, stroke widths, corner radii, arrow style, and container style. If the paper already has accepted figures, extract the contract from them rather than inventing one.
- What must be exact (labels, topology, numbers) and what may be approximate (decorative icons, spacing).

Keep palettes small: three to five categorical hues plus neutrals. Choose colorblind-safe palettes and never encode the only distinction between conditions in color alone; pair color with shape, dash pattern, or annotation.

Define the meaning of every connector before drawing it: source, target, direction, fan-in or fan-out, and whether it denotes data flow, control flow, gradient flow, or reference. Do not draw arrows whose semantics cannot be explained in the caption or text.

## 4. Author schematic diagrams as draw.io sources

Author `.drawio` XML directly rather than relying on interactive-only editing, so the source is reproducible and reviewable. Keep these conventions:

- One `mxfile` element holds one or more `diagram` pages. Each page contains one `mxGraphModel` whose `root` starts with the reserved cells of id `0` and a default layer of id `1` with `parent="0"`.
- Shapes are `mxCell` elements with `vertex="1"`, a stable id, a `value` label, a semicolon-separated `style`, `parent="1"`, and an explicit `mxGeometry` with absolute `x`, `y`, `width`, and `height`. Do not leave geometry to automatic layout for camera-ready figures.
- Connectors are `mxCell` elements with `edge="1"` plus `source` and `target` attributes referencing existing shape ids. Use `edgeStyle=orthogonalEdgeStyle` for axis-aligned routing, set explicit `exitX`, `exitY`, `entryX`, `entryY` when edges stack on one side of a shape, and place edge labels in a child cell with `edgeLabel` style.
- Group related shapes with containers or swimlanes (`container=1`) and keep child geometry relative to the parent.
- With `html=1` in a style, escape label text; emit markup such as `<b>`, `<i>`, `<sub>`, `<sup>` only deliberately.
- Store the palette and typography only in styles, not in embedded images. Prefer editable primitives over pasted screenshots.
- If a reference figure defines the target style, extract palette hex codes, font sizes, stroke widths, and arrow grammar from it before authoring; do not copy its scientific content.

Keep the source file portable and reviewable:

- Do not embed large base64 raster images in the source when an editable primitive suffices.
- Keep page sizes explicit (`pageWidth`, `pageHeight`) and keep content on the page.
- Use descriptive ids where they help review (`encoder-block`, `loss-arrow`); ids must be unique within a page.

Official documentation for the file format and the desktop app: the draw.io project at https://github.com/jgraph/drawio and the desktop releases at https://github.com/jgraph/drawio-desktop. Diagrams.net documentation lives in the project wiki at https://github.com/jgraph/drawio/wiki. Re-verify command syntax against the installed version rather than assuming flags.

## 5. Author LaTeX-native figures

Use TikZ for node-and-edge schematics and `pgfplots` for plots compiled inside LaTeX.

- Verify that the target template permits the packages you need (`tikz`, `pgfplots`, `subcaption`, and the required TikZ libraries) before writing the figure; some venues restrict packages in submission sources.
- Compile against the actual document class so fonts and sizes match the paper, not against a standalone preview class with different defaults.
- Keep figure code in its own `.tex` file included from the manuscript, with a single compiling command recorded in the figure plan.
- Externalize long compilations only if the venue workflow supports the generated artifacts.
- PGFPlots documentation: https://ctan.org/pkg/pgfplots. TikZ documentation: https://ctan.org/pkg/pgf. Verify library names against official documentation; never invent package or library names.

## 6. Generate data figures from traceable analysis

Data figures are analysis artifacts. Generate them with versioned code from immutable run outputs, following `analysis-and-statistics.md`:

- One plotting function or script per figure, taking explicit input paths and configuration; no manual transcription of values.
- Consistent styling through a shared style file or rc parameters so all figures obey the same style contract.
- Common axis scales and units across comparable panels; disclosed truncation, log scales, smoothing, and aggregation.
- Uncertainty shown where claims depend on it: confidence intervals, bands, per-seed curves, or paired differences, matching the analysis reference.
- Output both the review raster and the camera-ready vector from the same script run.

Record the command, input artifact ids, code version, and output paths in the figure plan. A data figure that cannot be regenerated from recorded inputs fails the figure gate.

## 7. Validate diagram sources before rendering

XML alone cannot reveal visual defects such as overlaps, clipped text, or wrong routing, but it can carry structural defects that render as garbage. Run the structural lint before any render:

```bash
# --strict fails on warnings too; --min-font-size N raises the font threshold;
# --json emits a machine-readable report
python3 scripts/validate_drawio.py figures/fig01-method.drawio
```

The validator parses plain and compressed `.drawio` files and reports errors and warnings: malformed XML, duplicate cell ids, edges with dangling source or target references, broken parent links, vertices missing geometry, empty labels, embedded raster images, sub-minimum font sizes, off-page content, and unresolved markers such as `[RESULT PENDING]`. Fix every error and review every warning before rendering; use `--strict` in a camera-ready pass so warnings also fail. The validator certifies structure only, never that the figure communicates correctly.

## 8. Render, inspect, and iterate

Never declare a figure complete from its source code alone. Produce a render and inspect it.

Preferred path, the draw.io desktop CLI (no network needed):

```bash
# Find the binary once per machine: drawio --version, draw.io --version,
# or on macOS /Applications/draw.io.app/Contents/MacOS/draw.io --version

# Camera-ready vector with the diagram embedded for later editing
drawio -x -f pdf -e -b 0 -o figures/fig01-method.pdf figures/fig01-method.drawio

# Review raster at a readable scale
drawio -x -f png -e -s 3 -o render/fig01-method.png figures/fig01-method.drawio

# Selected pages of a multi-page file
drawio -x -f pdf -p 1,2 -o figures/fig01-method.pdf figures/fig01-method.drawio
```

Verify each exported file after rendering: open or screenshot the PDF or PNG and check it against the figure plan. Inspect text readability at final print size, arrow semantics, alignment, color coherence, and agreement of every label and number with the manuscript.

Fallbacks when the CLI is unavailable, in order: local render through the desktop app GUI, the diagrams.net embed in a locally served preview page, or asking the user to export manually. If the only fallback is a public web editor, confirm that the content is not confidential or under anonymity constraints before using it.

Iterate on evidence: for each defect found in a render, patch the source, regenerate the export, and re-check. Do not re-render after every micro-edit without a named defect list, and do not stop while a known blocker (wrong connector semantics, clipped or overlapping text, missing content, wrong numbers) remains visible. Name the defects fixed in the final summary instead of claiming broad perfection.

For TikZ figures, the render is the compiled document section; inspect the page region of the figure at final size.

## 9. Meet publication standards

Venue requirements are volatile. Retrieve the current official figure rules of the target venue or publisher and record the URL and access date; do not rely on remembered limits. Check at minimum:

- Accepted formats (PDF, EPS, SVG, PNG), minimum resolution for rasters, and font embedding requirements.
- Maximum widths for single-column and full-width figures, and treatment of captions and subfigures.
- Color policy, including print and accessibility requirements.
- Whether source files must accompany the submission.

Export sizes and formats must also survive the submission-level checks in paper-formatting.md without rework.

Apply stable standards regardless of venue:

- Text in the final rendered figure is readable at print size; as a rule of thumb no smaller than 7pt for camera-ready output, larger for dense panels.
- Vector export for all schematic figures; rasters only for genuinely raster content, at sufficient resolution.
- Consistent visual language across all figures in the paper.
- Captions that permit correct interpretation without the main text, and that do not overstate what the figure shows.
- Accessible encoding: colorblind-safe palette, redundant cues beyond color, and alternative text where the format supports it.
- No hidden metadata, unreferenced confidential content, or identifying information in exports when anonymity applies.

## 10. Record provenance and pass the figure gate

Keep a figure ledger, either in the figure plan files or in the dossier, mapping every figure ID to:

- Claim IDs and the manuscript placement.
- Editable source path and code version.
- Input data or run artifact ids and hashes for data figures.
- The exact generation or export command and its output paths.
- Render verification: how the render was inspected, by whom, and when.
- Outstanding defects or an explicit clean status.

In a project dossier, capture figure-generation runs with `scripts/capture_run.py` like any other analysis artifact, so `scripts/audit_research.py` can trace the outputs. When figures enter a manuscript pass, recheck their labels and numbers against the text with the audit in [paper-writing.md](paper-writing.md), section "Revise and audit the manuscript".

Require all of the following for a figure gate PASS:

- Every figure has an ID, a supported claim, and a plan with no unresolved placeholders.
- The editable source exists, passes `scripts/validate_drawio.py` (or an equivalent structural check for TikZ and plot sources), and is the unique origin of the shipped export.
- Exports were regenerated from the current source and visually inspected at target size.
- Labels, numbers, and terminology agree with the manuscript text.
- Style contract, font, color, size, and format rules are satisfied, with the current venue source recorded.
- Third-party content has verified license and attribution.

Return `CONDITIONAL` for bounded cosmetic work with an owner; `FAIL` for untraceable data, invented content, source-export divergence, or license violations; `BLOCKED` when required tools, venue rules, or permissions cannot be verified.
